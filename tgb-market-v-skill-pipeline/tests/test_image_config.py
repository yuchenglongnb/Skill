from pathlib import Path

from tgb_pipeline.config import load_ocr_config


def test_load_ocr_config_defaults_backward_compatible(tmp_path: Path) -> None:
    config_path = tmp_path / "ocr.yaml"
    config_path.write_text(
        """
ocr:
  enabled: true
images:
  download_dir: data/raw/tgb/images
""",
        encoding="utf-8",
    )

    config = load_ocr_config(config_path)

    assert config.ocr.engine == "rapidocr"
    assert config.ocr.skip_if_engine_missing is True
    assert config.images.max_retries == 3
    assert config.images.skip_existing is True
    assert config.images.download_dir == Path("data/raw/tgb/images")
