from __future__ import annotations

from typing import Any

import numpy as np
from pydantic import BaseModel, ConfigDict, Field


class CameraDescriptor(BaseModel):
    device_path: str
    name: str
    path_exists: bool = True


class CameraConfig(BaseModel):
    device_path: str = "/dev/video0"
    width: int = Field(default=1280, ge=64, le=8192)
    height: int = Field(default=720, ge=64, le=8192)
    fps: int = Field(default=30, ge=1, le=240)
    pixel_format: str = "MJPG"


class MatRegion(BaseModel):
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    width: int = Field(ge=1)
    height: int = Field(ge=1)

    @property
    def xyxy(self) -> tuple[int, int, int, int]:
        return (self.x, self.y, self.x + self.width, self.y + self.height)


class FramePacket(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    frame_id: int
    captured_at_ns: int
    width: int
    height: int
    frame_bgr: np.ndarray

    def to_rgb(self) -> np.ndarray:
        return self.frame_bgr[:, :, ::-1]


class CameraStatus(BaseModel):
    configured: bool = False
    connected: bool = False
    preview_active: bool = False
    config: CameraConfig | None = None
    available_devices: list[CameraDescriptor] = Field(default_factory=list)
    last_frame_id: int | None = None
    last_frame_shape: tuple[int, int] | None = None
    last_error: str | None = None


class ConnectRequest(BaseModel):
    camera: CameraConfig
    commentary_enabled: bool = True
    mat_region: MatRegion | None = None
    rf_detr_variant: str = "small"
    sam3_body_repo_path: str | None = None
    sam3_body_checkpoint_path: str | None = None
    sam3_body_mhr_path: str | None = None
    gemma_model_id: str | None = None
    gemma_model_path: str | None = None
    piper_voice_model_path: str | None = None


class CameraConnectResult(BaseModel):
    ok: bool
    status: CameraStatus
    message: str


class FrameDebugSnapshot(BaseModel):
    frame_id: int
    mean_bgr: tuple[float, float, float]
    metadata: dict[str, Any] = Field(default_factory=dict)
