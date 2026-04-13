from __future__ import annotations

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from opencoach.schemas.camera import CameraConfig, ConnectRequest, MatRegion
from opencoach.schemas.runtime import AppRuntimeState


def build_router(*, templates: Jinja2Templates) -> APIRouter:
    router = APIRouter()

    @router.get("/", response_class=HTMLResponse)
    async def index(request: Request) -> HTMLResponse:
        runtime = request.app.state.runtime
        state = runtime.state()
        current_config = state.camera.config or CameraConfig()
        return templates.TemplateResponse(
            request,
            "index.html",
            {
                "state": state,
                "current_config": current_config,
            },
        )

    @router.post("/camera/connect")
    async def connect_camera(
        request: Request,
        device_path: str = Form("/dev/video0"),
        width: int = Form(1280),
        height: int = Form(720),
        fps: int = Form(30),
        pixel_format: str = Form("MJPG"),
        commentary_enabled: str | None = Form(None),
        mat_x: int | None = Form(None),
        mat_y: int | None = Form(None),
        mat_width: int | None = Form(None),
        mat_height: int | None = Form(None),
        rf_detr_variant: str = Form("small"),
        sam3_body_repo_path: str | None = Form(None),
        sam3_body_checkpoint_path: str | None = Form(None),
        sam3_body_mhr_path: str | None = Form(None),
        gemma_model_id: str | None = Form(None),
        gemma_model_path: str | None = Form(None),
        piper_voice_model_path: str | None = Form(None),
    ) -> RedirectResponse:
        runtime = request.app.state.runtime
        connect_request = _build_connect_request(
            device_path=device_path,
            width=width,
            height=height,
            fps=fps,
            pixel_format=pixel_format,
            commentary_enabled=commentary_enabled is not None,
            mat_x=mat_x,
            mat_y=mat_y,
            mat_width=mat_width,
            mat_height=mat_height,
            rf_detr_variant=rf_detr_variant,
            sam3_body_repo_path=sam3_body_repo_path,
            sam3_body_checkpoint_path=sam3_body_checkpoint_path,
            sam3_body_mhr_path=sam3_body_mhr_path,
            gemma_model_id=gemma_model_id,
            gemma_model_path=gemma_model_path,
            piper_voice_model_path=piper_voice_model_path,
        )
        try:
            runtime.connect(connect_request)
        except Exception as exc:
            runtime.set_error(str(exc))
        return RedirectResponse(url="/", status_code=303)

    @router.post("/camera/disconnect")
    async def disconnect_camera(request: Request) -> RedirectResponse:
        request.app.state.runtime.disconnect()
        return RedirectResponse(url="/", status_code=303)

    @router.get("/camera/stream.mjpeg")
    async def camera_stream(request: Request) -> StreamingResponse:
        return StreamingResponse(
            request.app.state.runtime.preview_stream(),
            media_type="multipart/x-mixed-replace; boundary=frame",
        )

    @router.get("/api/state")
    async def api_state(request: Request) -> JSONResponse:
        state: AppRuntimeState = request.app.state.runtime.state()
        return JSONResponse(state.model_dump(mode="json"))

    @router.get("/healthz")
    async def health() -> JSONResponse:
        return JSONResponse({"ok": True})

    return router


def _build_mat_region(
    x: int | None,
    y: int | None,
    width: int | None,
    height: int | None,
) -> MatRegion | None:
    values = (x, y, width, height)
    if any(value is None for value in values):
        return None
    assert x is not None
    assert y is not None
    assert width is not None
    assert height is not None
    return MatRegion(x=x, y=y, width=width, height=height)


def _build_connect_request(
    *,
    device_path: str,
    width: int,
    height: int,
    fps: int,
    pixel_format: str,
    commentary_enabled: bool,
    mat_x: int | None,
    mat_y: int | None,
    mat_width: int | None,
    mat_height: int | None,
    rf_detr_variant: str,
    sam3_body_repo_path: str | None,
    sam3_body_checkpoint_path: str | None,
    sam3_body_mhr_path: str | None,
    gemma_model_id: str | None,
    gemma_model_path: str | None,
    piper_voice_model_path: str | None,
) -> ConnectRequest:
    return ConnectRequest(
        camera=CameraConfig(
            device_path=device_path,
            width=width,
            height=height,
            fps=fps,
            pixel_format=pixel_format,
        ),
        commentary_enabled=commentary_enabled,
        mat_region=_build_mat_region(mat_x, mat_y, mat_width, mat_height),
        rf_detr_variant=rf_detr_variant,
        sam3_body_repo_path=sam3_body_repo_path,
        sam3_body_checkpoint_path=sam3_body_checkpoint_path,
        sam3_body_mhr_path=sam3_body_mhr_path,
        gemma_model_id=gemma_model_id,
        gemma_model_path=gemma_model_path,
        piper_voice_model_path=piper_voice_model_path,
    )
