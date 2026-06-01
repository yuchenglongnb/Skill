from pathlib import Path

import pytest

from tgb_pipeline.config import OCRConfig
from tgb_pipeline.images.tasks import download_images_task, ocr_images_task
from tgb_pipeline.models import ImageAsset
from tgb_pipeline.storage import JSONLStore

PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR"
    b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00"
    b"\x90wS\xde"
    b"\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\xff\xff?\x00\x05\xfe\x02\xfeA\xe2$\xb5"
    b"\x00\x00\x00\x00IEND\xaeB`\x82"
)


class MockCrawlConfig:
    class Storage:
        def __init__(self, root: Path) -> None:
            self.raw_dir = root / "data" / "raw"
            self.processed_dir = root / "data" / "processed"

    def __init__(self, root: Path) -> None:
        self.storage = self.Storage(root)


def test_download_and_ocr_tasks(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    raw_dir = tmp_path / "data" / "raw" / "tgb"
    JSONLStore(raw_dir / "images.jsonl", ImageAsset, "image_id").append(
        ImageAsset(
            image_id="img-1",
            article_id="a1",
            source_url="https://example.test/image.png",
            page_url="https://example.test/a1",
            source_type="article_body",
        )
    )

    def fake_download_images(raw_dir_arg, config_arg):
        local_path = tmp_path / "downloaded.png"
        local_path.write_bytes(PNG_BYTES)
        JSONLStore(raw_dir_arg / "images_downloaded.jsonl", ImageAsset, "image_id").rewrite_all(
            [
                ImageAsset(
                    image_id="img-1",
                    article_id="a1",
                    source_url="https://example.test/image.png",
                    page_url="https://example.test/a1",
                    source_type="article_body",
                    local_path=local_path.as_posix(),
                )
            ]
        )
        return 1, 0

    def fake_ocr_images(raw_dir_arg, processed_dir_arg, config_arg):
        return 1, 0, 0

    def fake_review_queue(raw_dir_arg, processed_dir_arg, reports_dir_arg):
        reports_dir_arg.mkdir(parents=True, exist_ok=True)
        path = reports_dir_arg / "image_ocr_review_queue.md"
        path.write_text("# queue\n", encoding="utf-8")
        return path

    monkeypatch.setattr("tgb_pipeline.images.tasks.download_images", fake_download_images)
    monkeypatch.setattr("tgb_pipeline.images.tasks.ocr_images", fake_ocr_images)
    monkeypatch.setattr("tgb_pipeline.images.tasks.build_image_review_queue", fake_review_queue)

    crawl_config = MockCrawlConfig(tmp_path)
    ocr_config = OCRConfig()

    assert download_images_task(crawl_config, ocr_config) == (1, 0)
    assert ocr_images_task(crawl_config, ocr_config) == (1, 0, 0)
    assert (tmp_path / "reports" / "image_ocr_review_queue.md").is_file()
