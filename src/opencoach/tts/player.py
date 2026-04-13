from __future__ import annotations

import subprocess
from pathlib import Path


def play_audio_file(audio_path: Path, *, player_command: str, volume: int) -> None:
    if player_command.endswith("ffplay"):
        command = [
            player_command,
            "-nodisp",
            "-autoexit",
            "-loglevel",
            "error",
            "-volume",
            str(volume),
            str(audio_path),
        ]
    elif player_command.endswith("aplay"):
        command = [player_command, "-q", str(audio_path)]
    else:
        command = [player_command, str(audio_path)]
    subprocess.run(command, check=True, capture_output=True, text=True)
