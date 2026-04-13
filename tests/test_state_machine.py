from opencoach.pipelines.state_machine import infer_golfer_phase
from opencoach.schemas.models import PoseEstimate
from opencoach.schemas.scene import SceneSnapshot


def test_state_machine_reports_no_golfer_when_hidden() -> None:
    phase = infer_golfer_phase(
        golfer_visible=False,
        golfer_on_mat=None,
        pose=None,
        previous_snapshot=None,
    )
    assert phase == "no_golfer"


def test_state_machine_reports_off_mat() -> None:
    phase = infer_golfer_phase(
        golfer_visible=True,
        golfer_on_mat=False,
        pose=None,
        previous_snapshot=None,
    )
    assert phase == "off_mat"


def test_state_machine_reports_swing_when_tilt_changes() -> None:
    previous = SceneSnapshot(
        golfer_visible=True,
        golfer_on_mat=True,
        golfer_phase="setup",
        pose=PoseEstimate(bbox_xyxy=(0, 0, 1, 1), torso_tilt_deg=2.0),
    )
    phase = infer_golfer_phase(
        golfer_visible=True,
        golfer_on_mat=True,
        pose=PoseEstimate(bbox_xyxy=(0, 0, 1, 1), torso_tilt_deg=18.0),
        previous_snapshot=previous,
    )
    assert phase == "swing"
