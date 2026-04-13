from __future__ import annotations

from pydantic import BaseModel, Field

from opencoach.schemas.camera import MatRegion
from opencoach.schemas.models import DetectionCandidate, PoseEstimate


class SceneSnapshot(BaseModel):
    frame_id: int | None = None
    captured_at_ns: int | None = None
    golfer_visible: bool = False
    golfer_on_mat: bool | None = None
    golfer_phase: str = "no_golfer"
    confidence: float = 0.0
    mat_region: MatRegion | None = None
    detection: DetectionCandidate | None = None
    pose: PoseEstimate | None = None
    cues: list[str] = Field(default_factory=list)
    summary: str = "No golfer visible."
