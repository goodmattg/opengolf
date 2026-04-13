import time

from opencoach.pipelines.orchestrator import _finish_decision, _is_address_candidate
from opencoach.schemas.models import PoseEstimate
from opencoach.schemas.scene import SceneSnapshot


def test_address_candidate_requires_pose_and_stability() -> None:
    previous = SceneSnapshot(
        golfer_visible=True,
        golfer_on_mat=True,
        golfer_phase="setup",
        pose=PoseEstimate(bbox_xyxy=(0.0, 0.0, 1.0, 1.0), torso_tilt_deg=12.0),
    )
    current = SceneSnapshot(
        golfer_visible=True,
        golfer_on_mat=True,
        golfer_phase="setup",
        pose=PoseEstimate(bbox_xyxy=(0.0, 0.0, 1.0, 1.0), torso_tilt_deg=14.0),
    )
    assert (
        _is_address_candidate(
            snapshot=current,
            previous_snapshot=previous,
            require_mat=True,
        )
        is True
    )


def test_finish_decision_abandons_stalled_address_clip() -> None:
    snapshot = SceneSnapshot(golfer_visible=True, golfer_phase="setup")
    decision = _finish_decision(
        snapshot=snapshot,
        swing_started=False,
        started_at_ns=1,
        max_duration_s=0.0,
        finish_hold=0,
        required_finish_hold=2,
    )
    assert decision.should_stop is True
    assert decision.stop_state == "abandoned"


def test_finish_decision_queues_after_follow_through() -> None:
    snapshot = SceneSnapshot(golfer_visible=True, golfer_phase="follow_through")
    decision = _finish_decision(
        snapshot=snapshot,
        swing_started=True,
        started_at_ns=time.time_ns(),
        max_duration_s=10.0,
        finish_hold=0,
        required_finish_hold=1,
    )
    assert decision.should_stop is True
    assert decision.stop_state == "queued"
    assert decision.updated_finish_hold == 1
