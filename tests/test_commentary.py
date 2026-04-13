from opencoach.pipelines.commentary import CommentaryController
from opencoach.schemas.scene import SceneSnapshot


def test_commentary_skips_duplicate_text() -> None:
    controller = CommentaryController(cooldown_s=0.0)
    snapshot = SceneSnapshot(golfer_visible=True, golfer_phase="setup")
    first = controller.decide(proposed_text="Golfer is setting up.", snapshot=snapshot)
    second = controller.decide(proposed_text="Golfer is setting up.", snapshot=snapshot)
    assert first.should_speak is True
    assert second.should_speak is False
    assert second.reason == "duplicate"


def test_commentary_skips_silent() -> None:
    controller = CommentaryController(cooldown_s=0.0)
    decision = controller.decide(
        proposed_text="silent",
        snapshot=SceneSnapshot(golfer_visible=True, golfer_phase="setup"),
    )
    assert decision.should_speak is False
    assert decision.reason == "silent"
