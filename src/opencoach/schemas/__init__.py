from opencoach.schemas.camera import (
    CameraConfig,
    CameraConnectResult,
    CameraDescriptor,
    CameraStatus,
    ConnectRequest,
    FrameDebugSnapshot,
    FramePacket,
    MatRegion,
)
from opencoach.schemas.commentary import CommentaryDecision, CommentaryPrompt, CommentaryRecord
from opencoach.schemas.models import (
    DetectionCandidate,
    DetectionResult,
    ModelCommentary,
    ModelManifest,
    PoseEstimate,
    PoseResult,
)
from opencoach.schemas.runtime import AppRuntimeState
from opencoach.schemas.scene import SceneSnapshot
from opencoach.schemas.swing import FinishDecision, LiveSwingState, SwingArtifact
from opencoach.schemas.tts import SpeechRequest, SpeechResult, TtsConfig

__all__ = [
    "AppRuntimeState",
    "CameraConfig",
    "CameraConnectResult",
    "CameraDescriptor",
    "CameraStatus",
    "CommentaryDecision",
    "CommentaryPrompt",
    "CommentaryRecord",
    "ConnectRequest",
    "DetectionCandidate",
    "DetectionResult",
    "FrameDebugSnapshot",
    "FramePacket",
    "FinishDecision",
    "MatRegion",
    "ModelCommentary",
    "ModelManifest",
    "PoseEstimate",
    "PoseResult",
    "SceneSnapshot",
    "LiveSwingState",
    "SpeechRequest",
    "SpeechResult",
    "SwingArtifact",
    "TtsConfig",
]
