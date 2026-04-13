from __future__ import annotations

import time
from collections.abc import Iterator

import cv2
import numpy as np

from opencoach.schemas.camera import FramePacket


def _encode_mjpeg(frame: np.ndarray, *, quality: int) -> bytes:
    ok, encoded = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    if not ok:
        raise RuntimeError("Failed to encode preview frame as JPEG.")
    return encoded.tobytes()


def _placeholder_frame(message: str = "Waiting for camera") -> np.ndarray:
    frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    cv2.putText(
        frame,
        message,
        (50, 360),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.2,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )
    return frame


def build_mjpeg_generator(
    latest_frame: callable[[], FramePacket | None],
    *,
    quality: int,
    sleep_s: float,
) -> Iterator[bytes]:
    while True:
        packet = latest_frame()
        frame = packet.frame_bgr if packet is not None else _placeholder_frame()
        payload = _encode_mjpeg(frame, quality=quality)
        yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + payload + b"\r\n"
        time.sleep(sleep_s)
