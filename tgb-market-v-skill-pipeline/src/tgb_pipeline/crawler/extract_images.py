"""Extract article image evidence and replace images with stable placeholders."""

from __future__ import annotations

import hashlib
from urllib.parse import urljoin

from bs4 import Tag

from tgb_pipeline.models import ImageAsset


def extract_article_images(
    container: Tag,
    *,
    article_id: str,
    page_url: str,
) -> list[ImageAsset]:
    images: list[ImageAsset] = []
    for position, image in enumerate(container.find_all("img"), start=1):
        source_url = _image_url(image)
        if not source_url:
            image.decompose()
            continue
        absolute_url = urljoin(page_url, source_url)
        digest = hashlib.sha256(f"{article_id}:{position}:{absolute_url}".encode()).hexdigest()
        image_id = f"image-{digest[:20]}"
        images.append(
            ImageAsset(
                image_id=image_id,
                article_id=article_id,
                source_url=absolute_url,
                page_url=page_url,
                raw={
                    "position": position,
                    "html": str(image),
                    "attributes": dict(image.attrs),
                },
            )
        )
        image.replace_with(f"\n[IMAGE: {image_id}]\n")
    return images


def _image_url(image: Tag) -> str | None:
    for name in ("data-original", "data-src", "src"):
        value = image.get(name)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None

