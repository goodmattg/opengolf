from __future__ import annotations

from pathlib import Path

from opencoach.schemas.camera import CameraDescriptor


def list_camera_descriptors() -> list[CameraDescriptor]:
    descriptors: list[CameraDescriptor] = []
    for path in sorted(Path("/dev").glob("video*")):
        descriptors.append(
            CameraDescriptor(
                device_path=str(path),
                name=path.name,
                path_exists=path.exists(),
            )
        )
    return descriptors
