"""High-level image download and OCR tasks for the CLI."""

from __future__ import annotations

from pathlib import Path

from tgb_pipeline.config import CrawlConfig, OCRConfig
from tgb_pipeline.images.download import download_images
from tgb_pipeline.images.ocr import ocr_images
from tgb_pipeline.images.review_queue import build_image_review_queue


def download_images_task(crawl_config: CrawlConfig, ocr_config: OCRConfig) -> tuple[int, int]:
    raw_dir = crawl_config.storage.raw_dir / "tgb"
    return download_images(raw_dir, ocr_config)


def ocr_images_task(crawl_config: CrawlConfig, ocr_config: OCRConfig) -> tuple[int, int, int]:
    raw_dir = crawl_config.storage.raw_dir / "tgb"
    processed_dir = crawl_config.storage.processed_dir / "tgb"
    reports_dir = Path("reports")
    results = ocr_images(raw_dir, processed_dir, ocr_config)
    build_image_review_queue(raw_dir, processed_dir, reports_dir)
    return results
