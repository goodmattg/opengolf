from __future__ import annotations

from pydantic import BaseModel


class TtsConfig(BaseModel):
    backend: str = "piper"
    voice_model_path: str | None = None
    player_command: str = "ffplay"
    player_volume: int = 100


class SpeechRequest(BaseModel):
    text: str


class SpeechResult(BaseModel):
    spoken: bool
    backend: str
    audio_path: str | None = None
    error: str | None = None
