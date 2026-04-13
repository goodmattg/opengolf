from __future__ import annotations

import queue
import threading
import time
from pathlib import Path
from uuid import uuid4

import cv2

from opencoach.camera.session import CameraSession
from opencoach.models.rfdetr import RfDetrAdapter
from opencoach.models.sam3_body import Sam3BodyAdapter
from opencoach.pipelines.snapshot import build_scene_snapshot
from opencoach.schemas.camera import ConnectRequest, FramePacket
from opencoach.schemas.commentary import CommentaryRecord
from opencoach.schemas.models import DetectionResult, ModelManifest, PoseResult
from opencoach.schemas.runtime import AppRuntimeState
from opencoach.schemas.scene import SceneSnapshot
from opencoach.schemas.swing import FinishDecision, LiveSwingState, SwingArtifact
from opencoach.schemas.tts import SpeechRequest, TtsConfig
from opencoach.settings import AppSettings
from opencoach.tts.piper import NoOpSpeaker, PiperSpeaker

ADDRESS_PHASES = frozenset({"address", "setup"})
SWING_STARTED_PHASES = frozenset({"swing", "follow_through"})
SWING_PHRASES = (
    "Nice swing.",
    "That's a beauty.",
    "Pure rope.",
)


class PipelineOrchestrator:
    def __init__(self, *, camera_session: CameraSession, settings: AppSettings) -> None:
        self.camera_session = camera_session
        self.settings = settings
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._worker_stop_event = threading.Event()

        self._state = AppRuntimeState(commentary_enabled=settings.commentary_enabled)

        self._rf_detr: RfDetrAdapter | None = None
        self._sam3_body: Sam3BodyAdapter | None = None
        self._speaker = NoOpSpeaker()
        self._request: ConnectRequest | None = None

        self._recent_swings: list[SwingArtifact] = []
        self._live_swing = LiveSwingState()
        self._address_hold = 0
        self._finish_hold = 0
        self._recording_started_ns = 0
        self._recording_frames: list[FramePacket] = []
        self._recording_last_frame_id: int | None = None
        self._active_swing_id: str | None = None
        self._processing_swing_id: str | None = None
        self._phrase_index = 0
        self._sam_job_queue: queue.Queue[SwingArtifact] = queue.Queue()
        self._worker_rf_detr: RfDetrAdapter | None = None
        self._worker_sam3_body: Sam3BodyAdapter | None = None
        self._worker_thread = threading.Thread(
            target=self._run_sam_worker,
            name="sam3-worker",
            daemon=True,
        )
        self._worker_thread.start()

    def configure(self, request: ConnectRequest) -> None:
        self.stop()
        self._request = request
        self._rf_detr = RfDetrAdapter(
            variant=request.rf_detr_variant or self.settings.rfdetr_variant,
            threshold=self.settings.rfdetr_threshold,
            model_dir=self.settings.model_dir,
        )
        self._sam3_body = Sam3BodyAdapter(
            repo_path=Path(request.sam3_body_repo_path or self.settings.sam3_body_repo_path),
            checkpoint_path=_path_or_none(
                request.sam3_body_checkpoint_path, self.settings.sam3_body_checkpoint_path
            ),
            mhr_path=_path_or_none(request.sam3_body_mhr_path, self.settings.sam3_body_mhr_path),
        )
        self._worker_rf_detr = None
        self._worker_sam3_body = None
        voice_model_path = _resolve_voice_model_path(
            request.piper_voice_model_path,
            self.settings.piper_voice_model_path,
        )
        self._speaker = (
            PiperSpeaker(
                TtsConfig(
                    backend=self.settings.tts_backend,
                    voice_model_path=voice_model_path,
                    player_command=self.settings.audio_player_command,
                    player_volume=self.settings.audio_player_volume,
                )
            )
            if request.commentary_enabled
            else NoOpSpeaker()
        )
        self._reset_live_state()
        with self._lock:
            self._state = AppRuntimeState(
                camera=self.camera_session.status(),
                models=self._manifests(),
                commentary_enabled=request.commentary_enabled,
                live_swing=self._live_swing,
                recent_swings=list(self._recent_swings),
            )

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, name="pipeline", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None
        self._discard_active_recording()

    def shutdown(self) -> None:
        self.stop()
        self._worker_stop_event.set()
        self._worker_thread.join(timeout=2.0)

    def state(self) -> AppRuntimeState:
        with self._lock:
            state = self._state.model_copy(deep=False)
            state.camera = self.camera_session.status()
            state.models = self._manifests()
            state.live_swing = self._build_live_swing_state()
            state.recent_swings = list(self._recent_swings)
            return state

    def set_state(self, state: AppRuntimeState) -> None:
        with self._lock:
            self._state = state

    def _run_loop(self) -> None:
        previous_snapshot: SceneSnapshot | None = None
        last_rfdetr_at = 0.0
        last_sam_at = 0.0
        detection_result: DetectionResult | None = None
        pose_result: PoseResult | None = None

        while not self._stop_event.is_set():
            frame = self.camera_session.latest_frame()
            if frame is None or self._request is None:
                time.sleep(0.05)
                continue

            now = time.monotonic()
            if (
                self._rf_detr is not None
                and now - last_rfdetr_at >= self.settings.rfdetr_interval_s
            ):
                detection_result = self._rf_detr.detect(frame)
                last_rfdetr_at = now
                if detection_result.selected is None:
                    pose_result = None
                    self._address_hold = 0

            if (
                self._sam3_body is not None
                and detection_result is not None
                and detection_result.selected is not None
                and now - last_sam_at >= self.settings.sam3_body_interval_s
            ):
                pose_result = self._sam3_body.estimate(frame, detection_result.selected)
                last_sam_at = now

            snapshot = build_scene_snapshot(
                frame=frame,
                mat_region=self._request.mat_region,
                detection=detection_result,
                pose=pose_result,
                previous_snapshot=previous_snapshot,
            )

            commentary_record = self._state.last_commentary
            commentary_record = self._advance_swing_workflow(
                frame=frame,
                snapshot=snapshot,
                previous_snapshot=previous_snapshot,
                commentary_record=commentary_record,
            )

            with self._lock:
                self._state = AppRuntimeState(
                    camera=self.camera_session.status(),
                    models=self._manifests(),
                    snapshot=snapshot,
                    last_commentary=commentary_record,
                    commentary_enabled=self._request.commentary_enabled,
                    live_swing=self._build_live_swing_state(),
                    recent_swings=list(self._recent_swings),
                    last_error=_first_error(detection_result, pose_result),
                )
            previous_snapshot = snapshot
            time.sleep(0.05)

    def _advance_swing_workflow(
        self,
        *,
        frame: FramePacket,
        snapshot: SceneSnapshot,
        previous_snapshot: SceneSnapshot | None,
        commentary_record: CommentaryRecord | None,
    ) -> CommentaryRecord | None:
        address_candidate = _is_address_candidate(
            snapshot=snapshot,
            previous_snapshot=previous_snapshot,
            require_mat=self._request is not None and self._request.mat_region is not None,
        )
        if address_candidate:
            self._address_hold += 1
        elif not self._live_swing.recording:
            self._address_hold = 0

        address_on = self._address_hold >= self.settings.address_hold_frames
        if not self._live_swing.recording and address_on:
            self._start_recording(frame)

        if self._live_swing.recording:
            self._append_recording_frame(frame)
            if snapshot.golfer_phase in SWING_STARTED_PHASES:
                self._live_swing.swing_started = True

            decision = _finish_decision(
                snapshot=snapshot,
                swing_started=self._live_swing.swing_started,
                started_at_ns=self._recording_started_ns,
                max_duration_s=self.settings.swing_clip_max_s,
                finish_hold=self._finish_hold,
                required_finish_hold=self.settings.finish_hold_frames,
            )
            self._finish_hold = decision.updated_finish_hold

            if decision.should_stop:
                artifact = self._stop_recording(state=decision.stop_state or "abandoned")
                if artifact is not None and decision.stop_state == "queued":
                    commentary_record = self._queue_swing_artifact(artifact)
                return commentary_record

        self._live_swing.address_on = address_on
        return commentary_record

    def _start_recording(self, frame: FramePacket) -> None:
        self._active_swing_id = _build_swing_id()
        self._recording_started_ns = time.time_ns()
        self._recording_frames = []
        self._recording_last_frame_id = None
        self._finish_hold = 0
        self._live_swing = LiveSwingState(
            address_on=True,
            recording=True,
            swing_started=False,
            active_swing_id=self._active_swing_id,
            buffered_frames=0,
            processor_busy=self._processor_busy(),
        )
        self._append_recording_frame(frame)
        artifact = SwingArtifact(
            swing_id=self._active_swing_id,
            state="recording",
            started_at_ns=self._recording_started_ns,
            fps=self._recording_fps(),
        )
        self._upsert_swing_artifact(artifact)

    def _append_recording_frame(self, frame: FramePacket) -> None:
        if self._recording_last_frame_id == frame.frame_id:
            return
        self._recording_frames.append(frame.model_copy(deep=False))
        self._recording_last_frame_id = frame.frame_id
        self._live_swing.buffered_frames = len(self._recording_frames)

    def _stop_recording(self, *, state: str) -> SwingArtifact | None:
        if self._active_swing_id is None or not self._recording_frames:
            self._discard_active_recording()
            return None

        artifact = SwingArtifact(
            swing_id=self._active_swing_id,
            state=state,
            started_at_ns=self._recording_started_ns,
            ended_at_ns=time.time_ns(),
            frame_count=len(self._recording_frames),
            fps=self._recording_fps(),
        )
        if state != "abandoned":
            swing_dir = self.settings.swing_dir / artifact.swing_id
            swing_dir.mkdir(parents=True, exist_ok=True)
            input_path = swing_dir / "input.mp4"
            _write_video(input_path, self._recording_frames, artifact.fps)
            artifact = artifact.model_copy(
                update={
                    "state": "queued",
                    "input_video_path": str(input_path),
                }
            )
        self._upsert_swing_artifact(artifact)
        self._discard_active_recording()
        return artifact

    def _discard_active_recording(self) -> None:
        self._address_hold = 0
        self._finish_hold = 0
        self._recording_started_ns = 0
        self._recording_frames = []
        self._recording_last_frame_id = None
        self._active_swing_id = None
        self._live_swing = LiveSwingState(processor_busy=self._processor_busy())

    def _run_sam_worker(self) -> None:
        while not self._worker_stop_event.is_set():
            try:
                artifact = self._sam_job_queue.get(timeout=0.2)
            except queue.Empty:
                continue
            self._processing_swing_id = artifact.swing_id
            self._upsert_swing_artifact(artifact.model_copy(update={"state": "processing"}))
            try:
                overlay_path = self._process_swing_artifact(artifact)
                self._upsert_swing_artifact(
                    artifact.model_copy(
                        update={
                            "state": "completed",
                            "overlay_video_path": str(overlay_path),
                        }
                    )
                )
            except Exception as exc:
                self._upsert_swing_artifact(
                    artifact.model_copy(update={"state": "failed", "error": str(exc)})
                )
            finally:
                self._processing_swing_id = None
                self._sam_job_queue.task_done()

    def _process_swing_artifact(self, artifact: SwingArtifact) -> Path:
        input_path = Path(artifact.input_video_path or "")
        if not input_path.exists():
            raise FileNotFoundError(f"Swing clip missing: {input_path}")
        cap = cv2.VideoCapture(str(input_path))
        if not cap.isOpened():
            raise RuntimeError(f"Failed to open swing clip: {input_path}")
        fps = float(cap.get(cv2.CAP_PROP_FPS) or artifact.fps or 30)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        overlay_path = input_path.parent / "sam3-overlay.mp4"
        writer = cv2.VideoWriter(
            str(overlay_path),
            cv2.VideoWriter_fourcc(*"mp4v"),
            fps,
            (width, height),
        )
        if not writer.isOpened():
            cap.release()
            raise RuntimeError(f"Failed to open overlay writer: {overlay_path}")
        worker_rf_detr, worker_sam3 = self._ensure_worker_models()
        frame_id = 0
        try:
            while True:
                ok, frame_bgr = cap.read()
                if not ok or frame_bgr is None:
                    break
                frame_id += 1
                packet = FramePacket(
                    frame_id=frame_id,
                    captured_at_ns=time.time_ns(),
                    width=width,
                    height=height,
                    frame_bgr=frame_bgr,
                )
                detection_result = worker_rf_detr.detect(packet)
                rendered = frame_bgr
                if detection_result.selected is not None:
                    _pose_result, overlay = worker_sam3.estimate_with_overlay(
                        packet, detection_result.selected
                    )
                    if overlay is not None:
                        rendered = overlay
                writer.write(rendered)
        finally:
            cap.release()
            writer.release()
        return overlay_path

    def _ensure_worker_models(self) -> tuple[RfDetrAdapter, Sam3BodyAdapter]:
        if self._worker_rf_detr is None:
            self._worker_rf_detr = RfDetrAdapter(
                variant=_resolve_rf_variant(self._request, self.settings),
                threshold=self.settings.rfdetr_threshold,
                model_dir=self.settings.model_dir,
            )
        if self._worker_sam3_body is None:
            self._worker_sam3_body = Sam3BodyAdapter(
                repo_path=_resolve_sam_repo_path(self._request, self.settings),
                checkpoint_path=_path_or_none(
                    self._request.sam3_body_checkpoint_path if self._request is not None else None,
                    self.settings.sam3_body_checkpoint_path,
                ),
                mhr_path=_path_or_none(
                    self._request.sam3_body_mhr_path if self._request is not None else None,
                    self.settings.sam3_body_mhr_path,
                ),
            )
        return self._worker_rf_detr, self._worker_sam3_body

    def _build_live_swing_state(self) -> LiveSwingState:
        return LiveSwingState(
            address_on=self._live_swing.address_on,
            recording=self._active_swing_id is not None and bool(self._recording_frames),
            swing_started=self._live_swing.swing_started,
            active_swing_id=self._active_swing_id,
            buffered_frames=len(self._recording_frames),
            processor_busy=self._processor_busy(),
        )

    def _reset_live_state(self) -> None:
        self._recent_swings = []
        self._live_swing = LiveSwingState()
        self._address_hold = 0
        self._finish_hold = 0
        self._recording_started_ns = 0
        self._recording_frames = []
        self._recording_last_frame_id = None
        self._active_swing_id = None
        self._processing_swing_id = None

    def _upsert_swing_artifact(self, artifact: SwingArtifact) -> None:
        with self._lock:
            for index, existing in enumerate(self._recent_swings):
                if existing.swing_id == artifact.swing_id:
                    self._recent_swings[index] = artifact
                    break
            else:
                self._recent_swings.insert(0, artifact)
            self._recent_swings = self._recent_swings[: self.settings.max_recent_swings]

    def _queue_swing_artifact(self, artifact: SwingArtifact) -> CommentaryRecord:
        phrase = _next_phrase(self)
        speech = self._speaker.speak(SpeechRequest(text=phrase))
        queued_artifact = artifact.model_copy(update={"phrase": phrase})
        self._upsert_swing_artifact(queued_artifact)
        self._sam_job_queue.put(queued_artifact)
        return CommentaryRecord(
            text=phrase,
            spoken=speech.spoken,
            generated_at_ns=time.time_ns(),
            reason="swing_complete" if speech.error is None else speech.error,
        )

    def _manifests(self) -> list[ModelManifest]:
        manifests: list[ModelManifest] = []
        for adapter in (self._rf_detr, self._sam3_body):
            if adapter is not None:
                manifests.append(adapter.manifest())
        return manifests

    def _processor_busy(self) -> bool:
        return self._processing_swing_id is not None or not self._sam_job_queue.empty()

    def _recording_fps(self) -> int:
        if self._request is None:
            return 0
        return self._request.camera.fps


def _path_or_none(primary: str | None, fallback: Path | None) -> Path | None:
    if primary:
        return Path(primary)
    return fallback


def _resolve_voice_model_path(primary: str | None, fallback: Path | None) -> str | None:
    if primary:
        return primary
    if fallback is not None:
        return str(fallback)
    return None


def _resolve_rf_variant(request: ConnectRequest | None, settings: AppSettings) -> str:
    if request is not None and request.rf_detr_variant:
        return request.rf_detr_variant
    return settings.rfdetr_variant


def _resolve_sam_repo_path(request: ConnectRequest | None, settings: AppSettings) -> Path:
    if request is not None and request.sam3_body_repo_path:
        return Path(request.sam3_body_repo_path)
    return settings.sam3_body_repo_path


def _first_error(
    detection_result: DetectionResult | None, pose_result: PoseResult | None
) -> str | None:
    if detection_result is not None and detection_result.error is not None:
        return detection_result.error
    if pose_result is not None and pose_result.error is not None:
        return pose_result.error
    return None


def _is_address_candidate(
    *,
    snapshot: SceneSnapshot,
    previous_snapshot: SceneSnapshot | None,
    require_mat: bool,
) -> bool:
    if not snapshot.golfer_visible or snapshot.pose is None or snapshot.pose.torso_tilt_deg is None:
        return False
    if require_mat and snapshot.golfer_on_mat is not True:
        return False
    if snapshot.golfer_phase not in ADDRESS_PHASES:
        return False
    if previous_snapshot is None or previous_snapshot.pose is None:
        return True
    if previous_snapshot.pose.torso_tilt_deg is None:
        return True
    return abs(snapshot.pose.torso_tilt_deg - previous_snapshot.pose.torso_tilt_deg) <= 6.0


def _finish_decision(
    *,
    snapshot: SceneSnapshot,
    swing_started: bool,
    started_at_ns: int,
    max_duration_s: float,
    finish_hold: int,
    required_finish_hold: int,
) -> FinishDecision:
    elapsed_s = 0.0 if started_at_ns == 0 else (time.time_ns() - started_at_ns) / 1_000_000_000.0
    if not swing_started and elapsed_s >= max_duration_s:
        return FinishDecision(should_stop=True, stop_state="abandoned")

    updated_finish_hold = finish_hold
    if swing_started:
        if snapshot.golfer_phase == "follow_through" or not snapshot.golfer_visible:
            updated_finish_hold += 1
        else:
            updated_finish_hold = 0
        if updated_finish_hold >= required_finish_hold or elapsed_s >= max_duration_s:
            return FinishDecision(
                should_stop=True,
                stop_state="queued",
                updated_finish_hold=updated_finish_hold,
            )
    return FinishDecision(updated_finish_hold=updated_finish_hold)


def _write_video(path: Path, frames: list[FramePacket], fps: int) -> None:
    if not frames:
        raise RuntimeError("No frames were captured for the swing clip.")
    height = frames[0].height
    width = frames[0].width
    writer = cv2.VideoWriter(
        str(path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        float(fps or 30),
        (width, height),
    )
    try:
        for frame in frames:
            writer.write(frame.frame_bgr)
    finally:
        writer.release()


def _build_swing_id() -> str:
    return f"{time.strftime('%Y%m%d-%H%M%S')}-{uuid4().hex[:8]}"


def _next_phrase(orchestrator: PipelineOrchestrator) -> str:
    phrase = SWING_PHRASES[orchestrator._phrase_index % len(SWING_PHRASES)]
    orchestrator._phrase_index += 1
    return phrase
