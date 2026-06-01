"""Parse mobile comment pages and related pagination links."""

from __future__ import annotations

import hashlib
import re
from urllib.parse import urljoin, urlsplit, urlunsplit

from bs4 import BeautifulSoup, Tag

from tgb_pipeline.crawler.extract_images import extract_comment_images
from tgb_pipeline.models import Comment, ImageAsset
from tgb_pipeline.utils.dates import parse_datetime
from tgb_pipeline.utils.text_cleaning import clean_text

SHORT_ARTICLE_PATH = re.compile(r"^/a/(?P<id>[A-Za-z0-9]+)(?:-(?P<page>\d+))?$")
NUMERIC_ARTICLE_PATH = re.compile(r"^/(?:Article|article)/(?P<id>\d+)(?:/(?P<page>\d+))?$")
COMMENT_PAGE_HREF = re.compile(r"/a/(?P<id>[A-Za-z0-9]+)-(?P<page>\d+)\?type=")


def build_comment_page_url(article_mobile_url: str, page_num: int) -> str:
    parts = urlsplit(article_mobile_url)
    if not parts.scheme:
        parts = urlsplit(urljoin("https://m.tgb.cn", article_mobile_url))
    scheme = parts.scheme or "https"
    host = parts.netloc or "m.tgb.cn"
    path = parts.path.rstrip("/")

    short_match = SHORT_ARTICLE_PATH.match(path)
    if short_match:
        article_id = short_match.group("id")
        if page_num == 1:
            return urlunsplit((scheme, host, f"/a/{article_id}", "", ""))
        return urlunsplit((scheme, host, f"/a/{article_id}-{page_num}", "type=", ""))

    numeric_match = NUMERIC_ARTICLE_PATH.match(path)
    if numeric_match:
        article_id = numeric_match.group("id")
        if page_num == 1:
            return urlunsplit((scheme, host, f"/Article/{article_id}/1", "", ""))
        return urlunsplit((scheme, host, f"/Article/{article_id}/{page_num}", "type=", ""))

    raise ValueError(f"unsupported article mobile url for comments: {article_mobile_url}")


def find_comment_next_page_url(html: str, page_url: str) -> str | None:
    soup = BeautifulSoup(html, "lxml")
    for anchor in soup.find_all("a", href=True):
        text = anchor.get_text(" ", strip=True)
        if text in {"下一页", "下页", "Next", "next", ">"}:
            return urljoin(page_url, anchor["href"])
    return None


def find_comment_last_page_num(html: str, page_url: str) -> int | None:
    soup = BeautifulSoup(html, "lxml")
    for anchor in soup.find_all("a", href=True):
        text = anchor.get_text(" ", strip=True)
        href = str(anchor["href"])
        if text in {"末页", "尾页", "最后一页"}:
            match = COMMENT_PAGE_HREF.search(href)
            if match:
                return int(match.group("page"))
    return None


def parse_comments_page(
    html: str,
    *,
    article_id: str,
    article_title: str,
    page_url: str,
    page_num: int,
    target_author: str,
) -> tuple[list[Comment], list[ImageAsset]]:
    soup = BeautifulSoup(html, "lxml")
    items = soup.select(".plContent .plItem")
    comments: list[Comment] = []
    images: list[ImageAsset] = []

    for floor_index, item in enumerate(items, start=1):
        metadata = item.find(id=re.compile(r"^gtgioMsg"))
        author_name = _author_name(item, metadata)
        published_at = _published_at(item)
        text_container = item.select_one(".pl_text")
        if not isinstance(text_container, Tag):
            continue
        content = _clone_tag(text_container)
        comment_id = _comment_id(
            article_id=article_id,
            page_num=page_num,
            floor_index=floor_index,
            author_name=author_name,
            metadata=metadata,
        )
        comment_images = extract_comment_images(
            content,
            article_id=article_id,
            comment_id=comment_id,
            page_url=page_url,
        )
        comment_text = clean_text(content.get_text("\n", strip=True))
        comment = Comment(
            comment_id=comment_id,
            article_id=article_id,
            author_name=author_name,
            published_at=published_at,
            page_num=page_num,
            page_position=floor_index,
            raw_content=comment_text,
            content_text=comment_text,
            image_asset_ids=[image.image_id for image in comment_images],
            raw={
                "article_title": article_title,
                "html": str(item),
                "page_url": page_url,
                "metadata_attributes": dict(metadata.attrs) if isinstance(metadata, Tag) else {},
            },
        )
        comments.append(comment)
        images.extend(comment_images)

    return comments, images


def _author_name(item: Tag, metadata: Tag | None) -> str:
    author_link = item.select_one(".plName")
    if isinstance(author_link, Tag):
        return author_link.get_text(" ", strip=True)
    if isinstance(metadata, Tag):
        username = metadata.get("username")
        if isinstance(username, str):
            return username.strip()
    return ""


def _published_at(item: Tag):
    time_node = item.select_one(".pl_time")
    if not isinstance(time_node, Tag):
        return None
    value = time_node.get_text(" ", strip=True)
    try:
        if re.match(r"^\d{2}-\d{2}-\d{2}", value):
            value = f"20{value}"
        return parse_datetime(value)
    except ValueError:
        return None


def _comment_id(
    *,
    article_id: str,
    page_num: int,
    floor_index: int,
    author_name: str,
    metadata: Tag | None,
) -> str:
    if isinstance(metadata, Tag):
        content_id = metadata.get("contentid")
        if isinstance(content_id, str) and content_id.strip():
            return f"comment-{content_id.strip()}"
    digest = hashlib.sha256(
        f"{article_id}:{page_num}:{floor_index}:{author_name.casefold()}".encode("utf-8")
    ).hexdigest()
    return f"comment-{article_id}-{page_num}-{floor_index}-{digest[:10]}"


def _clone_tag(tag: Tag) -> Tag:
    return BeautifulSoup(str(tag), "lxml").select_one(tag.name) or tag
