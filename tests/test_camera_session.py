from opencoach.camera.session import _fallback_device_index


def test_fallback_device_index_parses_v4l2_nodes() -> None:
    assert _fallback_device_index("/dev/video0") == 0
    assert _fallback_device_index("/dev/video12") == 12


def test_fallback_device_index_rejects_non_v4l2_paths() -> None:
    assert _fallback_device_index("0") is None
    assert _fallback_device_index("/tmp/video0") is None
