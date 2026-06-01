"""Extract article image evidence and replace images with stable placeholders."""

from __future__ import annotations

from copy import copy
import hashlib
from urllib.parse import urljoin

from bs4 import NavigableString, Tag

from tgb_pipeline.models import ImageAsset
from tgb_pipeline.utils.text_cleaning import clean_text


def extract_article_images(
    container: Tag,
    *,
    article_id: str,
    page_url: str,
) -> list[ImageAsset]:
    return extract_inline_images(
        container,
        article_id=article_id,
        page_url=page_url,
        source_type="article_body",
        article_owner_id=article_id,
        keep_reason="target_author_article_image",
    )


def extract_comment_images(
    container: Tag,
    *,
    article_id: str,
    comment_id: str,
    page_url: str,
) -> list[ImageAsset]:
    return extract_inline_images(
        container,
        article_id=article_id,
        page_url=page_url,
        source_type="comment",
        article_owner_id=article_id,
        comment_owner_id=comment_id,
        keep_reason=None,
    )


def extract_inline_images(
    container: Tag,
    *,
    article_id: str,
    page_url: str,
    source_type: str,
    article_owner_id: str | None = None,
    comment_owner_id: str | None = None,
    keep_reason: str | None = None,
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
                article_id=article_owner_id,
                comment_id=comment_owner_id,
                source_url=absolute_url,
                page_url=page_url,
                source_type=source_type,
                position_index=position,
                before_text=_adjacent_text(image, reverse=True),
                after_text=_adjacent_text(image, reverse=False),
                keep_reason=keep_reason,
                image_type=_image_type(image),
                review_status="unreviewed",
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


def _image_type(image: Tag) -> str | None:
    data_type = image.get("data-type")
    if isinstance(data_type, str) and data_type.strip():
        return data_type.strip()
    classes = image.get("class", [])
    if isinstance(classes, list) and classes:
        return " ".join(str(cls) for cls in classes if str(cls).strip()) or None
    return None


def _adjacent_text(image: Tag, *, reverse: bool) -> str | None:
    sibling = image.previous_sibling if reverse else image.next_sibling
    while sibling is not None:
        text = _text_from_node(sibling)
        if text:
            return clean_text(text)
        sibling = sibling.previous_sibling if reverse else sibling.next_sibling

    parent = image.parent
    if not isinstance(parent, Tag):
        return None
    sibling = parent.previous_sibling if reverse else parent.next_sibling
    while sibling is not None:
        text = _text_from_node(sibling)
        if text:
            return clean_text(text)
        sibling = sibling.previous_sibling if reverse else sibling.next_sibling
    return None


def _text_from_node(node: object) -> str:
    if isinstance(node, NavigableString):
        return str(node).strip()
    if isinstance(node, Tag):
        clone = copy(node)
        for nested_image in clone.find_all("img"):
            nested_image.decompose()
        return clone.get_text(" ", strip=True)
    return ""
