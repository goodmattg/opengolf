from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

SwingArtifactState = Literal[
    "recording",
    "queued",
    "processing",
    "completed",
    "failed",
    "abandoned",
]
SwingStopState = Literal["queued", "abandoned"]


class LiveSwingState(BaseModel):
    address_on: bool = False
    recording: bool = False
    swing_started: bool = False
    active_swing_id: str | None = None
    buffered_frames: int = Field(default=0, ge=0)
    processor_busy: bool = False


class SwingArtifact(BaseModel):
    swing_id: str
    state: SwingArtifactState
    started_at_ns: int | None = None
    ended_at_ns: int | None = None
    frame_count: int = Field(default=0, ge=0)
    fps: int = Field(default=0, ge=0)
    input_video_path: str | None = None
    overlay_video_path: str | None = None
    phrase: str | None = None
    error: str | None = None


class FinishDecision(BaseModel):
    should_stop: bool = False
    stop_state: SwingStopState | None = None
    updated_finish_hold: int = Field(default=0, ge=0)
