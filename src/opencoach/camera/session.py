from __future__ import annotations

import re
import threading
import time

import cv2

from opencoach.camera.v4l2 import list_camera_descriptors
from opencoach.schemas.camera import CameraConfig, CameraStatus, FramePacket


class CameraSession:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._capture: cv2.VideoCapture | None = None
        self._frame: FramePacket | None = None
        self._frame_counter = 0
        self._config: CameraConfig | None = None
        self._last_error: str | None = None
        self._warmup_frames_remaining = 0

    def configure(self, config: CameraConfig) -> None:
        with self._lock:
            self._config = config
            self._last_error = None

    def start(self) -> None:
        config = self._config
        if config is None:
            raise ValueError("Camera configuration is required before starting the session.")
        self.stop()
        capture = _open_capture(config.device_path)
        if not capture.isOpened():
            capture.release()
            raise RuntimeError(f"Failed to open camera device {config.device_path}.")

        capture.set(cv2.CAP_PROP_FRAME_WIDTH, config.width)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, config.height)
        capture.set(cv2.CAP_PROP_FPS, config.fps)
        if len(config.pixel_format) == 4:
            capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*config.pixel_format))

        self._capture = capture
        self._frame_counter = 0
        self._warmup_frames_remaining = 5
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._capture_loop, name="camera-capture", daemon=True
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None
        if self._capture is not None:
            self._capture.release()
            self._capture = None
        with self._lock:
            self._frame = None
        self._warmup_frames_remaining = 0

    def latest_frame(self) -> FramePacket | None:
        with self._lock:
            if self._frame is None:
                return None
            return self._frame.model_copy(deep=False)

    def status(self) -> CameraStatus:
        with self._lock:
            frame = self._frame
            return CameraStatus(
                configured=self._config is not None,
                connected=self._capture is not None and self._capture.isOpened(),
                preview_active=frame is not None,
                config=self._config,
                available_devices=list_camera_descriptors(),
                last_frame_id=frame.frame_id if frame is not None else None,
                last_frame_shape=(frame.height, frame.width) if frame is not None else None,
                last_error=self._last_error,
            )

    def _capture_loop(self) -> None:
        assert self._capture is not None
        while not self._stop_event.is_set():
            ok, frame = self._capture.read()
            if not ok or frame is None:
                with self._lock:
                    self._last_error = "Camera read failed."
                time.sleep(0.05)
                continue
            if self._warmup_frames_remaining > 0:
                self._warmup_frames_remaining -= 1
                continue
            self._frame_counter += 1
            packet = FramePacket(
                frame_id=self._frame_counter,
                captured_at_ns=time.time_ns(),
                width=int(frame.shape[1]),
                height=int(frame.shape[0]),
                frame_bgr=frame.copy(),
            )
            with self._lock:
                self._frame = packet
                self._last_error = None


def _open_capture(device_path: str) -> cv2.VideoCapture:
    fallback_index = _fallback_device_index(device_path)
    attempts: list[tuple[object, int | None]] = [
        (device_path, cv2.CAP_V4L2),
    ]
    if fallback_index is not None:
        attempts.append((fallback_index, cv2.CAP_V4L2))
    attempts.append((device_path, None))
    if fallback_index is not None:
        attempts.append((fallback_index, None))

    last_capture: cv2.VideoCapture | None = None
    for source, backend in attempts:
        capture = (
            cv2.VideoCapture(source, backend) if backend is not None else cv2.VideoCapture(source)
        )
        if capture.isOpened():
            return capture
        capture.release()
        last_capture = capture
    return cv2.VideoCapture() if last_capture is None else last_capture


def _fallback_device_index(device_path: str) -> int | None:
    match = re.fullmatch(r"/dev/video(\d+)", device_path)
    if match is None:
        return None
    return int(match.group(1))
