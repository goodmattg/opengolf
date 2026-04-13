from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from opencoach.schemas.tts import SpeechRequest, SpeechResult, TtsConfig
from opencoach.tts.base import Speaker
from opencoach.tts.player import play_audio_file


class PiperSpeaker(Speaker):
    def __init__(self, config: TtsConfig) -> None:
        self.config = config

    def speak(self, request: SpeechRequest) -> SpeechResult:
        if self.config.voice_model_path is None:
            return SpeechResult(
                spoken=False,
                backend="piper",
                error="voice_model_path_missing",
            )
        generation_command = _resolve_generation_command(self.config.backend)
        if generation_command is None:
            return SpeechResult(
                spoken=False,
                backend="piper",
                error="piper_command_missing",
            )

        with tempfile.NamedTemporaryFile(
            prefix="opencoach-", suffix=".wav", delete=False
        ) as handle:
            audio_path = Path(handle.name)

        command = [
            *generation_command,
            "--model",
            self.config.voice_model_path,
            "--output_file",
            str(audio_path),
        ]
        try:
            subprocess.run(
                command,
                input=request.text,
                check=True,
                capture_output=True,
                text=True,
            )
            play_audio_file(
                audio_path,
                player_command=self.config.player_command,
                volume=self.config.player_volume,
            )
            return SpeechResult(spoken=True, backend="piper", audio_path=str(audio_path))
        except Exception as exc:
            return SpeechResult(
                spoken=False,
                backend="piper",
                audio_path=str(audio_path),
                error=str(exc),
            )


class NoOpSpeaker(Speaker):
    def speak(self, request: SpeechRequest) -> SpeechResult:
        return SpeechResult(spoken=False, backend="noop", error="speech_disabled")


def _resolve_generation_command(backend: str) -> list[str] | None:
    if backend != "piper":
        return None
    binary = shutil.which("piper")
    if binary is not None:
        return [binary]
    try:
        import piper  # noqa: F401

        return [sys.executable, "-m", "piper"]
    except Exception:
        return None
