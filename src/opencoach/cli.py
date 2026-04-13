from __future__ import annotations

import json
from pathlib import Path

import click
import cv2
import uvicorn

from opencoach.models.gemma4 import Gemma4Adapter
from opencoach.models.rfdetr import RfDetrAdapter
from opencoach.models.sam3_body import Sam3BodyAdapter
from opencoach.pipelines.commentary import CommentaryController
from opencoach.pipelines.snapshot import build_scene_snapshot
from opencoach.schemas.camera import FramePacket
from opencoach.schemas.commentary import CommentaryPrompt
from opencoach.schemas.models import DetectionCandidate
from opencoach.schemas.runtime import PipelineSmokeResult
from opencoach.schemas.scene import SceneSnapshot
from opencoach.schemas.tts import SpeechRequest, TtsConfig
from opencoach.settings import load_settings
from opencoach.tts.piper import PiperSpeaker


@click.group()
def main() -> None:
    """OpenCoach CLI."""


@main.command()
def serve() -> None:
    settings = load_settings()
    uvicorn.run(
        "opencoach.app:create_app",
        factory=True,
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )


@main.command("smoke-rfdetr")
@click.option("--image", "image_path", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--variant", default="small", show_default=True)
def smoke_rfdetr(image_path: Path, variant: str) -> None:
    settings = load_settings()
    adapter = RfDetrAdapter(variant=variant, model_dir=settings.model_dir)
    packet = _frame_from_image(image_path)
    result = adapter.detect(packet)
    click.echo(
        json.dumps(
            result.model_dump(mode="json", exclude={"candidates": {"__all__": {"mask"}}}), indent=2
        )
    )


@main.command("smoke-sam3-body")
@click.option("--image", "image_path", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--repo-path", required=True, type=click.Path(path_type=Path))
@click.option("--checkpoint-path", required=True, type=click.Path(path_type=Path))
@click.option("--mhr-path", required=True, type=click.Path(path_type=Path))
@click.option("--bbox", default=None, help="bbox as x1,y1,x2,y2")
def smoke_sam3_body(
    image_path: Path,
    repo_path: Path,
    checkpoint_path: Path,
    mhr_path: Path,
    bbox: str | None,
) -> None:
    adapter = Sam3BodyAdapter(
        repo_path=repo_path,
        checkpoint_path=checkpoint_path,
        mhr_path=mhr_path,
    )
    packet = _frame_from_image(image_path)
    detection = _bbox_candidate(bbox, packet)
    result = adapter.estimate(packet, detection)
    click.echo(json.dumps(result.model_dump(mode="json"), indent=2))


@main.command("smoke-gemma4")
@click.option("--image", "image_path", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--model-id", default="google/gemma-4-E4B-it", show_default=True)
@click.option("--model-path", default=None, type=click.Path(path_type=Path))
def smoke_gemma4(image_path: Path, model_id: str, model_path: Path | None) -> None:
    adapter = Gemma4Adapter(model_id=model_id, model_path=model_path)
    packet = _frame_from_image(image_path)
    prompt = CommentaryPrompt(snapshot=SceneSnapshot(golfer_visible=True, golfer_phase="setup"))
    result = adapter.describe(packet, prompt)
    click.echo(json.dumps(result.model_dump(mode="json"), indent=2))


@main.command("smoke-tts")
@click.option("--text", required=True)
@click.option("--voice-model", required=True, type=click.Path(path_type=Path))
def smoke_tts(text: str, voice_model: Path) -> None:
    settings = load_settings()
    speaker = PiperSpeaker(
        TtsConfig(
            backend="piper",
            voice_model_path=str(voice_model),
            player_command=settings.audio_player_command,
            player_volume=settings.audio_player_volume,
        )
    )
    result = speaker.speak(SpeechRequest(text=text))
    click.echo(json.dumps(result.model_dump(mode="json"), indent=2))


@main.command("smoke-pipeline")
@click.option("--image", "image_path", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--rf-variant", default="small", show_default=True)
@click.option(
    "--sam-repo-path",
    default="external/sam-3d-body",
    show_default=True,
    type=click.Path(path_type=Path),
)
@click.option(
    "--sam-checkpoint-path",
    default="models/sam-3d-body-dinov3/model.ckpt",
    show_default=True,
    type=click.Path(path_type=Path),
)
@click.option(
    "--sam-mhr-path",
    default="models/sam-3d-body-dinov3/assets/mhr_model.pt",
    show_default=True,
    type=click.Path(path_type=Path),
)
@click.option("--gemma-model-id", default="google/gemma-4-E4B-it", show_default=True)
@click.option(
    "--gemma-model-path",
    default="models/gemma-4-E4B-it",
    show_default=True,
    type=click.Path(path_type=Path),
)
@click.option(
    "--voice-model",
    default="models/piper-lessac/en/en_US/lessac/medium/en_US-lessac-medium.onnx",
    show_default=True,
    type=click.Path(path_type=Path),
)
def smoke_pipeline(
    image_path: Path,
    rf_variant: str,
    sam_repo_path: Path,
    sam_checkpoint_path: Path,
    sam_mhr_path: Path,
    gemma_model_id: str,
    gemma_model_path: Path,
    voice_model: Path,
) -> None:
    settings = load_settings()
    frame = _frame_from_image(image_path)

    detection_adapter = RfDetrAdapter(variant=rf_variant, model_dir=settings.model_dir)
    detection_result = detection_adapter.detect(frame)
    if detection_result.error is not None:
        raise click.ClickException(f"RF-DETR failed: {detection_result.error}")
    if detection_result.selected is None:
        raise click.ClickException("RF-DETR did not produce a selected person detection.")

    pose_adapter = Sam3BodyAdapter(
        repo_path=sam_repo_path,
        checkpoint_path=sam_checkpoint_path,
        mhr_path=sam_mhr_path,
    )
    pose_result = pose_adapter.estimate(frame, detection_result.selected)
    if pose_result.error is not None:
        raise click.ClickException(f"SAM 3D Body failed: {pose_result.error}")

    snapshot = build_scene_snapshot(
        frame=frame,
        mat_region=None,
        detection=detection_result,
        pose=pose_result,
        previous_snapshot=None,
    )
    prompt = CommentaryPrompt(snapshot=snapshot)

    gemma_adapter = Gemma4Adapter(model_id=gemma_model_id, model_path=gemma_model_path)
    commentary = gemma_adapter.describe(frame, prompt)
    if commentary.error is not None:
        raise click.ClickException(f"Gemma 4 failed: {commentary.error}")

    decision = CommentaryController(cooldown_s=0.0).decide(
        proposed_text=commentary.text,
        snapshot=snapshot,
    )
    speech = None
    if decision.should_speak and decision.text is not None:
        speech = PiperSpeaker(
            TtsConfig(
                backend="piper",
                voice_model_path=str(voice_model),
                player_command=settings.audio_player_command,
                player_volume=settings.audio_player_volume,
            )
        ).speak(SpeechRequest(text=decision.text))

    result = PipelineSmokeResult(
        detection=detection_result,
        pose=pose_result,
        snapshot=snapshot,
        commentary=commentary,
        speech=speech,
    )
    click.echo(json.dumps(result.model_dump(mode="json"), indent=2))


def _frame_from_image(image_path: Path) -> FramePacket:
    frame = cv2.imread(str(image_path))
    if frame is None:
        raise click.ClickException(f"Failed to load image: {image_path}")
    return FramePacket(
        frame_id=1,
        captured_at_ns=0,
        width=int(frame.shape[1]),
        height=int(frame.shape[0]),
        frame_bgr=frame,
    )


def _bbox_candidate(bbox: str | None, packet: FramePacket) -> DetectionCandidate:
    if bbox is None:
        coords = (0.0, 0.0, float(packet.width), float(packet.height))
    else:
        parts = [float(value) for value in bbox.split(",")]
        if len(parts) != 4:
            raise click.ClickException("bbox must be x1,y1,x2,y2")
        coords = tuple(parts)  # type: ignore[assignment]
    return DetectionCandidate(label="person", score=1.0, bbox_xyxy=coords)
