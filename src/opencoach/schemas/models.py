from __future__ import annotations

from typing import Any

import numpy as np
from pydantic import BaseModel, ConfigDict, Field


class ModelManifest(BaseModel):
    name: str
    configured: bool
    ready: bool
    detail: str | None = None
    device: str | None = None
    model_id: str | None = None
    model_path: str | None = None


class DetectionCandidate(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    label: str
    score: float
    class_id: int | None = None
    bbox_xyxy: tuple[float, float, float, float]
    mask: np.ndarray | None = Field(default=None, exclude=True)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DetectionResult(BaseModel):
    candidates: list[DetectionCandidate] = Field(default_factory=list)
    selected: DetectionCandidate | None = None
    latency_ms: float | None = None
    manifest: ModelManifest
    error: str | None = None


class PoseEstimate(BaseModel):
    bbox_xyxy: tuple[float, float, float, float]
    focal_length: float | None = None
    torso_tilt_deg: float | None = None
    hip_center_xy: tuple[float, float] | None = None
    shoulder_center_xy: tuple[float, float] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class PoseResult(BaseModel):
    poses: list[PoseEstimate] = Field(default_factory=list)
    selected: PoseEstimate | None = None
    latency_ms: float | None = None
    manifest: ModelManifest
    error: str | None = None


class ModelCommentary(BaseModel):
    text: str
    raw_text: str | None = None
    latency_ms: float | None = None
    manifest: ModelManifest
    error: str | None = None
