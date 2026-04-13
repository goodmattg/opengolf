import numpy as np

from opencoach.pipelines.snapshot import build_scene_snapshot
from opencoach.schemas.camera import FramePacket, MatRegion
from opencoach.schemas.models import DetectionCandidate, DetectionResult, ModelManifest


def test_snapshot_marks_golfer_on_mat() -> None:
    detection = DetectionCandidate(
        label="person",
        score=0.9,
        bbox_xyxy=(40.0, 50.0, 120.0, 160.0),
    )
    snapshot = build_scene_snapshot(
        frame=FramePacket(
            frame_id=1,
            captured_at_ns=1,
            width=200,
            height=200,
            frame_bgr=np.zeros((200, 200, 3), dtype=np.uint8),
        ),
        mat_region=MatRegion(x=0, y=0, width=200, height=200),
        detection=DetectionResult(
            candidates=[detection],
            selected=detection,
            manifest=ModelManifest(name="rf-detr", configured=True, ready=True),
        ),
        pose=None,
        previous_snapshot=None,
    )
    assert snapshot.golfer_on_mat is True
    assert snapshot.golfer_phase in {"visible", "address", "setup"}
