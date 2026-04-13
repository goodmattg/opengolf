from __future__ import annotations

from opencoach.schemas.models import PoseEstimate
from opencoach.schemas.scene import SceneSnapshot


def infer_golfer_phase(
    *,
    golfer_visible: bool,
    golfer_on_mat: bool | None,
    pose: PoseEstimate | None,
    previous_snapshot: SceneSnapshot | None,
) -> str:
    if not golfer_visible:
        return "no_golfer"
    if golfer_on_mat is False:
        return "off_mat"
    if pose is None or pose.torso_tilt_deg is None:
        return "visible"

    tilt = abs(pose.torso_tilt_deg)
    previous_tilt = (
        abs(previous_snapshot.pose.torso_tilt_deg)
        if (
            previous_snapshot is not None
            and previous_snapshot.pose is not None
            and previous_snapshot.pose.torso_tilt_deg is not None
        )
        else None
    )

    if tilt >= 28:
        return "follow_through"
    if previous_tilt is not None and abs(tilt - previous_tilt) >= 10:
        return "swing"
    if tilt >= 8:
        return "setup"
    return "address"
