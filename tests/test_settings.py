from pathlib import Path

from opencoach.settings import AppSettings


def test_settings_use_python_project_defaults() -> None:
    settings = AppSettings()
    assert settings.port == 8001
    assert settings.rfdetr_variant == "small"
    assert settings.gemma_model_id == "google/gemma-4-E4B-it"
    assert settings.sam3_body_checkpoint_path == Path("models/sam-3d-body-dinov3/model.ckpt")
    assert settings.sam3_body_mhr_path == Path("models/sam-3d-body-dinov3/assets/mhr_model.pt")
