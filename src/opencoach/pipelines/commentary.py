from __future__ import annotations

import time

from opencoach.schemas.commentary import CommentaryDecision
from opencoach.schemas.scene import SceneSnapshot


class CommentaryController:
    def __init__(self, *, cooldown_s: float) -> None:
        self.cooldown_ns = int(cooldown_s * 1_000_000_000)
        self._last_spoken_text: str | None = None
        self._last_spoken_phase: str | None = None
        self._last_spoken_at_ns: int = 0

    def decide(self, *, proposed_text: str, snapshot: SceneSnapshot) -> CommentaryDecision:
        text = proposed_text.strip()
        now_ns = time.time_ns()
        if not text:
            return CommentaryDecision(should_speak=False, text=None, reason="empty")
        if text.lower() == "silent":
            return CommentaryDecision(should_speak=False, text=None, reason="silent")
        if text == self._last_spoken_text:
            return CommentaryDecision(should_speak=False, text=None, reason="duplicate")
        if (
            now_ns - self._last_spoken_at_ns < self.cooldown_ns
            and snapshot.golfer_phase == self._last_spoken_phase
        ):
            return CommentaryDecision(should_speak=False, text=None, reason="cooldown")

        self._last_spoken_text = text
        self._last_spoken_phase = snapshot.golfer_phase
        self._last_spoken_at_ns = now_ns
        return CommentaryDecision(should_speak=True, text=text, reason="speak")
