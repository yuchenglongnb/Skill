"""Metadata helpers for downloaded image evidence."""

from __future__ import annotations

import hashlib
import imghdr
import struct
from pathlib import Path

from tgb_pipeline.models import ImageAsset

NOISE_TOKENS = ("avatar", "logo", "icon", "loading", "qrcode", "app", "ad")


def compute_file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def detect_mime_type(path: Path) -> str | None:
    suffix = path.suffix.casefold()
    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if suffix == ".png":
        return "image/png"
    if suffix == ".webp":
        return "image/webp"
    guessed = imghdr.what(path)
    if guessed == "jpeg":
        return "image/jpeg"
    if guessed:
        return f"image/{guessed}"
    return None


def read_image_size(path: Path) -> tuple[int, int] | None:
    try:
        from PIL import Image  # type: ignore

        with Image.open(path) as image:
            return image.size
    except ImportError:
        return _read_image_size_without_pillow(path)
    except Exception:
        return _read_image_size_without_pillow(path)


def is_probably_noise_image(image: ImageAsset) -> bool:
    source_url = image.source_url.casefold()
    if any(token in source_url for token in NOISE_TOKENS):
        return True
    if image.width is not None and image.height is not None:
        if image.width < 80 or image.height < 80:
            return True
    if (
        image.source_type == "comment"
        and not image.before_text
        and not image.after_text
        and not image.keep_reason
    ):
        return True
    suffix = Path(image.local_path or image.source_url).suffix.casefold()
    if suffix and suffix not in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}:
        return True
    return False


def _read_image_size_without_pillow(path: Path) -> tuple[int, int] | None:
    with path.open("rb") as handle:
        header = handle.read(32)
    if header.startswith(b"\x89PNG\r\n\x1a\n") and len(header) >= 24:
        width, height = struct.unpack(">II", header[16:24])
        return width, height
    if header[:6] in {b"GIF87a", b"GIF89a"} and len(header) >= 10:
        width, height = struct.unpack("<HH", header[6:10])
        return width, height
    if header.startswith(b"RIFF") and header[8:12] == b"WEBP":
        return _read_webp_size(path)
    return None


def _read_webp_size(path: Path) -> tuple[int, int] | None:
    with path.open("rb") as handle:
        data = handle.read(64)
    if b"VP8X" in data and len(data) >= 30:
        chunk_start = data.index(b"VP8X") + 8
        width = 1 + int.from_bytes(data[chunk_start : chunk_start + 3], "little")
        height = 1 + int.from_bytes(data[chunk_start + 3 : chunk_start + 6], "little")
        return width, height
    return None

