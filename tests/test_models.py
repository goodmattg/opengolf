import numpy as np

from opencoach.schemas.models import DetectionCandidate, DetectionResult, ModelManifest


def test_detection_result_json_dump_excludes_numpy_mask() -> None:
    detection = DetectionCandidate(
        label="person",
        score=0.9,
        bbox_xyxy=(1.0, 2.0, 3.0, 4.0),
        mask=np.ones((2, 2), dtype=np.uint8),
    )
    result = DetectionResult(
        candidates=[detection],
        selected=detection,
        manifest=ModelManifest(name="rf-detr", configured=True, ready=True),
    )

    payload = result.model_dump(mode="json")

    assert "mask" not in payload["candidates"][0]
    assert "mask" not in payload["selected"]
