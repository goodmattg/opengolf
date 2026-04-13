from __future__ import annotations

from pydantic import BaseModel

from opencoach.schemas.scene import SceneSnapshot


class CommentaryPrompt(BaseModel):
    snapshot: SceneSnapshot
    previous_commentary: str | None = None


class CommentaryDecision(BaseModel):
    should_speak: bool
    text: str | None = None
    reason: str


class CommentaryRecord(BaseModel):
    text: str
    spoken: bool
    generated_at_ns: int
    reason: str
