from __future__ import annotations

from opencoach.pipelines.state_machine import infer_golfer_phase
from opencoach.schemas.camera import FramePacket, MatRegion
from opencoach.schemas.models import DetectionResult, PoseResult
from opencoach.schemas.scene import SceneSnapshot


def build_scene_snapshot(
    *,
    frame: FramePacket | None,
    mat_region: MatRegion | None,
    detection: DetectionResult | None,
    pose: PoseResult | None,
    previous_snapshot: SceneSnapshot | None,
) -> SceneSnapshot:
    selected_detection = detection.selected if detection is not None else None
    selected_pose = pose.selected if pose is not None else None
    golfer_visible = selected_detection is not None
    golfer_on_mat = _is_on_mat(selected_detection, mat_region) if golfer_visible else None
    phase = infer_golfer_phase(
        golfer_visible=golfer_visible,
        golfer_on_mat=golfer_on_mat,
        pose=selected_pose,
        previous_snapshot=previous_snapshot,
    )

    cues: list[str] = []
    if golfer_visible:
        cues.append(f"detection_score={selected_detection.score:.2f}")
    if golfer_on_mat is True:
        cues.append("golfer_center_inside_mat")
    elif golfer_on_mat is False:
        cues.append("golfer_center_outside_mat")
    if selected_pose is not None and selected_pose.torso_tilt_deg is not None:
        cues.append(f"torso_tilt_deg={selected_pose.torso_tilt_deg:.1f}")

    summary = "No golfer visible."
    if golfer_visible:
        location = (
            "on the mat"
            if golfer_on_mat
            else "near the mat"
            if golfer_on_mat is False
            else "in frame"
        )
        summary = f"Golfer visible {location} in {phase.replace('_', ' ')}."

    return SceneSnapshot(
        frame_id=frame.frame_id if frame is not None else None,
        captured_at_ns=frame.captured_at_ns if frame is not None else None,
        golfer_visible=golfer_visible,
        golfer_on_mat=golfer_on_mat,
        golfer_phase=phase,
        confidence=selected_detection.score if selected_detection is not None else 0.0,
        mat_region=mat_region,
        detection=selected_detection,
        pose=selected_pose,
        cues=cues,
        summary=summary,
    )


def _is_on_mat(detection: object, mat_region: MatRegion | None) -> bool | None:
    if detection is None or mat_region is None:
        return None
    bbox = detection.bbox_xyxy
    center_x = (bbox[0] + bbox[2]) / 2.0
    center_y = (bbox[1] + bbox[3]) / 2.0
    x1, y1, x2, y2 = mat_region.xyxy
    return x1 <= center_x <= x2 and y1 <= center_y <= y2
