from opencoach.models.gemma4 import _build_prompt_text
from opencoach.schemas.commentary import CommentaryPrompt
from opencoach.schemas.scene import SceneSnapshot


def test_prompt_builder_includes_snapshot_fields() -> None:
    prompt = CommentaryPrompt(
        snapshot=SceneSnapshot(
            golfer_visible=True,
            golfer_on_mat=True,
            golfer_phase="setup",
            confidence=0.91,
            cues=["detection_score=0.91", "golfer_center_inside_mat"],
        ),
        previous_commentary="Golfer is getting set.",
    )
    text = _build_prompt_text(prompt)
    assert "golfer_visible: True" in text
    assert "golfer_on_mat: True" in text
    assert "golfer_phase: setup" in text
    assert "previous_commentary: Golfer is getting set." in text
