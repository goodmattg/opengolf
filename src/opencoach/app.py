from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from opencoach.logging_config import configure_logging
from opencoach.runtime import OpenCoachRuntime
from opencoach.settings import AppSettings, load_settings
from opencoach.web.routes import build_router


def create_app(settings: AppSettings | None = None) -> FastAPI:
    configure_logging()
    resolved_settings = settings or load_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.runtime = OpenCoachRuntime(resolved_settings)
        yield
        app.state.runtime.shutdown()

    app = FastAPI(title=resolved_settings.app_name, lifespan=lifespan)
    app.mount("/static", StaticFiles(directory=resolved_settings.static_dir), name="static")
    templates = Jinja2Templates(directory=str(resolved_settings.template_dir))
    app.include_router(build_router(templates=templates))
    return app
