from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="OPENCOACH_",
        env_file=".env.local",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: str = "127.0.0.1"
    port: int = 8001
    reload: bool = False

    app_name: str = "OpenCoach"
    data_dir: Path = Path("var")
    external_dir: Path = Path("external")
    model_dir: Path = Path("models")

    preview_quality: int = Field(default=85, ge=30, le=100)
    preview_frame_sleep_s: float = Field(default=0.03, gt=0.0, le=1.0)
    swing_dir: Path = Path("var/swings")

    rfdetr_variant: str = "small"
    rfdetr_threshold: float = Field(default=0.35, ge=0.0, le=1.0)
    rfdetr_interval_s: float = Field(default=0.5, gt=0.0, le=10.0)

    sam3_body_repo_path: Path = Path("external/sam-3d-body")
    sam3_body_checkpoint_path: Path | None = Path("models/sam-3d-body-dinov3/model.ckpt")
    sam3_body_mhr_path: Path | None = Path("models/sam-3d-body-dinov3/assets/mhr_model.pt")
    sam3_body_interval_s: float = Field(default=1.5, gt=0.0, le=30.0)

    gemma_model_id: str = "google/gemma-4-E4B-it"
    gemma_model_path: Path | None = None
    gemma_max_new_tokens: int = Field(default=64, ge=8, le=512)
    gemma_interval_s: float = Field(default=3.0, gt=0.0, le=30.0)

    commentary_cooldown_s: float = Field(default=4.0, ge=0.0, le=60.0)
    commentary_enabled: bool = True

    tts_backend: str = "piper"
    piper_command: str = "piper"
    piper_voice_model_path: Path | None = None
    audio_player_command: str = "ffplay"
    audio_player_volume: int = Field(default=100, ge=0, le=100)

    address_hold_frames: int = Field(default=3, ge=1, le=30)
    finish_hold_frames: int = Field(default=2, ge=1, le=30)
    swing_clip_max_s: float = Field(default=8.0, gt=1.0, le=30.0)
    max_recent_swings: int = Field(default=8, ge=1, le=100)

    @property
    def template_dir(self) -> Path:
        return Path(__file__).parent / "web" / "templates"

    @property
    def static_dir(self) -> Path:
        return Path(__file__).parent / "web" / "static"


def load_settings() -> AppSettings:
    settings = AppSettings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.model_dir.mkdir(parents=True, exist_ok=True)
    settings.swing_dir.mkdir(parents=True, exist_ok=True)
    return settings
