from pathlib import Path

import pytest

from tgb_pipeline.config import OCRConfig
from tgb_pipeline.images.ocr import ocr_images, run_ocr_for_image
from tgb_pipeline.models import ImageAsset, ImageOCR
from tgb_pipeline.storage import JSONLStore

PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR"
    b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00"
    b"\x90wS\xde"
    b"\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\xff\xff?\x00\x05\xfe\x02\xfeA\xe2$\xb5"
    b"\x00\x00\x00\x00IEND\xaeB`\x82"
)


def test_run_ocr_for_image_skips_missing_engine(tmp_path: Path) -> None:
    image_path = tmp_path / "image.png"
    image_path.write_bytes(PNG_BYTES)
    image = ImageAsset(
        image_id="img-1",
        article_id="a1",
        source_url="https://example.test/image.png",
        page_url="https://example.test/page",
        local_path=image_path.as_posix(),
    )

    assert run_ocr_for_image(
        image,
        engine="rapidocr",
        languages=["chi_sim"],
        min_confidence=0.85,
        skip_if_engine_missing=True,
    ) is None


def test_run_ocr_for_image_builds_record_with_fake_backend(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    image_path = tmp_path / "image.png"
    image_path.write_bytes(PNG_BYTES)
    image = ImageAsset(
        image_id="img-1",
        article_id="a1",
        source_url="https://example.test/image.png",
        page_url="https://example.test/page",
        local_path=image_path.as_posix(),
    )

    def fake_backend(path: Path, *, languages: list[str]):
        return [[[[0, 0], [1, 0], [1, 1], [0, 1]], ("测试 文本", 0.6)]]

    monkeypatch.setattr("tgb_pipeline.images.ocr._load_backend", lambda engine, skip: fake_backend)

    record = run_ocr_for_image(
        image,
        engine="rapidocr",
        languages=["chi_sim"],
        min_confidence=0.85,
    )

    assert record is not None
    assert record.ocr_id == "ocr-img-1-rapidocr"
    assert record.normalized_text == "测试 文本"
    assert record.raw["need_manual_review"] is True


def test_ocr_images_writes_records(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    image_path = tmp_path / "image.png"
    image_path.write_bytes(PNG_BYTES)
    JSONLStore(raw_dir / "images_downloaded.jsonl", ImageAsset, "image_id").append(
        ImageAsset(
            image_id="img-1",
            article_id="a1",
            source_url="https://example.test/image.png",
            page_url="https://example.test/page",
            local_path=image_path.as_posix(),
        )
    )

    monkeypatch.setattr(
        "tgb_pipeline.images.ocr._load_backend",
        lambda engine, skip: (lambda path, languages: [[[[0, 0], [1, 0], [1, 1], [0, 1]], ("hello", 0.95)]]),
    )

    ocr_count, skipped_count, failed_count = ocr_images(raw_dir, processed_dir, OCRConfig())
    records = JSONLStore(processed_dir / "image_ocr.jsonl", ImageOCR, "ocr_id").read_all()

    assert (ocr_count, skipped_count, failed_count) == (1, 0, 0)
    assert len(records) == 1
    assert records[0].raw_text == "hello"
