from __future__ import annotations

from pydantic import BaseModel, Field

from opencoach.schemas.camera import CameraStatus
from opencoach.schemas.commentary import CommentaryRecord
from opencoach.schemas.models import DetectionResult, ModelCommentary, ModelManifest, PoseResult
from opencoach.schemas.scene import SceneSnapshot
from opencoach.schemas.swing import LiveSwingState, SwingArtifact
from opencoach.schemas.tts import SpeechResult


class AppRuntimeState(BaseModel):
    camera: CameraStatus = Field(default_factory=CameraStatus)
    models: list[ModelManifest] = Field(default_factory=list)
    snapshot: SceneSnapshot = Field(default_factory=SceneSnapshot)
    last_commentary: CommentaryRecord | None = None
    commentary_enabled: bool = True
    live_swing: LiveSwingState = Field(default_factory=LiveSwingState)
    recent_swings: list[SwingArtifact] = Field(default_factory=list)
    last_error: str | None = None


class PipelineSmokeResult(BaseModel):
    detection: DetectionResult
    pose: PoseResult
    snapshot: SceneSnapshot
    commentary: ModelCommentary
    speech: SpeechResult | None = None
