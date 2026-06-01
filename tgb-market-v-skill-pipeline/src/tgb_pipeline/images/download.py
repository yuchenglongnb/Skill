"""Download original image assets and fill local metadata."""

from __future__ import annotations

import mimetypes
import time
from copy import deepcopy
from pathlib import Path
from urllib.parse import urlparse

import requests

from tgb_pipeline.config import OCRConfig
from tgb_pipeline.images.metadata import (
    compute_file_sha256,
    detect_mime_type,
    is_probably_noise_image,
    read_image_size,
)
from tgb_pipeline.models import ImageAsset
from tgb_pipeline.storage import JSONLStore


def download_image_asset(
    image: ImageAsset,
    *,
    image_root: Path,
    session: requests.Session | None = None,
    timeout: float = 20,
    max_retries: int = 3,
    skip_existing: bool = True,
) -> ImageAsset:
    if not image.source_url:
        return _with_error(image, "missing source_url")

    client = session or requests.Session()
    target_path = _build_local_path(image, image_root)
    updated = image.copy(deep=True)

    if skip_existing and target_path.exists():
        _populate_local_metadata(updated, target_path)
        return _mark_noise(updated)

    target_path.parent.mkdir(parents=True, exist_ok=True)
    last_error: str | None = None
    for attempt in range(max_retries + 1):
        try:
            response = client.get(image.source_url, timeout=timeout)
            response.raise_for_status()
            extension = _choose_extension(image.source_url, response.headers.get("Content-Type"))
            if target_path.suffix != extension:
                target_path = target_path.with_suffix(extension)
            target_path.write_bytes(response.content)
            _populate_local_metadata(updated, target_path, response.headers.get("Content-Type"))
            return _mark_noise(updated)
        except Exception as exc:  # pragma: no cover - exercised via tests with specific branches
            last_error = str(exc)
            if attempt < max_retries:
                time.sleep(0)
    return _with_error(updated, last_error or "download failed")


def download_images(raw_dir: Path, ocr_config: OCRConfig) -> tuple[int, int]:
    source_path = raw_dir / "images.jsonl"
    if not source_path.exists():
        raise ValueError("images.jsonl not found; run crawl-articles or crawl-comments first.")

    image_root = Path(ocr_config.images.download_dir)
    store = JSONLStore(source_path, ImageAsset, "image_id")
    output_store = JSONLStore(raw_dir / "images_downloaded.jsonl", ImageAsset, "image_id")
    existing_downloaded = {
        image.image_id: image for image in output_store.read_all()
    }

    session = requests.Session()
    updated_records: list[ImageAsset] = []
    downloaded_count = 0
    failed_count = 0
    for image in store.read_all():
        current = existing_downloaded.get(image.image_id, image)
        updated = download_image_asset(
            current,
            image_root=image_root,
            session=session,
            timeout=ocr_config.images.request_timeout_seconds,
            max_retries=ocr_config.images.max_retries,
            skip_existing=ocr_config.images.skip_existing,
        )
        if updated.local_path and not current.local_path:
            downloaded_count += 1
        elif updated.local_path and current.local_path:
            if not Path(updated.local_path).is_absolute():
                downloaded_count += 0
        if updated.raw.get("download_error"):
            failed_count += 1
        updated_records.append(updated)
        time.sleep(ocr_config.images.request_interval_seconds)
    output_store.rewrite_all(updated_records)
    return downloaded_count, failed_count


def _build_local_path(image: ImageAsset, image_root: Path) -> Path:
    suffix = _choose_extension(image.source_url, None)
    if image.comment_id:
        return image_root / str(image.article_id) / "comments" / image.comment_id / f"{image.image_id}_original{suffix}"
    return image_root / str(image.article_id) / f"{image.image_id}_original{suffix}"


def _choose_extension(source_url: str, content_type: str | None) -> str:
    parsed = urlparse(source_url)
    suffix = Path(parsed.path).suffix.casefold()
    if suffix in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}:
        return suffix
    if content_type:
        guessed = mimetypes.guess_extension(content_type.split(";")[0].strip(), strict=False)
        if guessed:
            return ".jpg" if guessed == ".jpe" else guessed
    return ".bin"


def _populate_local_metadata(
    image: ImageAsset,
    path: Path,
    content_type: str | None = None,
) -> None:
    image.local_path = path.as_posix()
    image.raw = deepcopy(image.raw)
    image.raw.pop("download_error", None)
    image.sha256 = compute_file_sha256(path)
    image.mime_type = (content_type.split(";")[0].strip() if content_type else None) or detect_mime_type(path)
    try:
        size = read_image_size(path)
        if size:
            image.width, image.height = size
    except Exception as exc:
        image.raw["image_open_error"] = str(exc)


def _with_error(image: ImageAsset, error: str) -> ImageAsset:
    updated = image.copy(deep=True)
    updated.raw = deepcopy(updated.raw)
    updated.raw["download_error"] = error
    return updated


def _mark_noise(image: ImageAsset) -> ImageAsset:
    updated = image.copy(deep=True)
    updated.raw = deepcopy(updated.raw)
    if is_probably_noise_image(updated):
        updated.raw["probably_noise_image"] = True
    return updated
