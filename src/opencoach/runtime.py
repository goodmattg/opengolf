from __future__ import annotations

from opencoach.camera.preview import build_mjpeg_generator
from opencoach.camera.session import CameraSession
from opencoach.pipelines.orchestrator import PipelineOrchestrator
from opencoach.schemas.camera import CameraConnectResult, ConnectRequest
from opencoach.schemas.runtime import AppRuntimeState
from opencoach.settings import AppSettings


class OpenCoachRuntime:
    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings
        self.camera_session = CameraSession()
        self.pipeline = PipelineOrchestrator(camera_session=self.camera_session, settings=settings)

    def connect(self, request: ConnectRequest) -> CameraConnectResult:
        self.camera_session.configure(request.camera)
        self.camera_session.start()
        self.pipeline.configure(request)
        self.pipeline.start()
        return CameraConnectResult(
            ok=True, status=self.camera_session.status(), message="camera_connected"
        )

    def disconnect(self) -> CameraConnectResult:
        self.pipeline.stop()
        self.camera_session.stop()
        return CameraConnectResult(
            ok=True, status=self.camera_session.status(), message="camera_disconnected"
        )

    def set_error(self, message: str) -> None:
        state = self.pipeline.state()
        state.last_error = message
        self.pipeline.set_state(state)

    def state(self) -> AppRuntimeState:
        return self.pipeline.state()

    def shutdown(self) -> None:
        self.pipeline.shutdown()
        self.camera_session.stop()

    def preview_stream(self):
        return build_mjpeg_generator(
            self.camera_session.latest_frame,
            quality=self.settings.preview_quality,
            sleep_s=self.settings.preview_frame_sleep_s,
        )
