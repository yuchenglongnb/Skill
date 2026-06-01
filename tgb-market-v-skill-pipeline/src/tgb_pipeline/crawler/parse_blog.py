"""Parse article metadata from a Taoguba blog index page."""

from __future__ import annotations

import re
from datetime import date
from urllib.parse import urljoin, urlsplit, urlunsplit

from bs4 import BeautifulSoup, Tag

from tgb_pipeline.models import ArticleIndex
from tgb_pipeline.utils.dates import parse_date

ARTICLE_PATH = re.compile(r"/(?:Article|article)/(?P<id>\d+)(?:/|$)")
SHORT_PATH = re.compile(r"/a/(?P<id>[A-Za-z0-9]+)(?:/|$)")
COUNTS = re.compile(r"(?P<views>[\d,.万]+)\s*/\s*(?P<replies>[\d,.万]+)")
TAG = re.compile(r"^\s*\[(?P<tag>[^\]]+)\]\s*")


def parse_blog_index(html: str, page_url: str) -> list[ArticleIndex]:
    soup = BeautifulSoup(html, "lxml")
    records: list[ArticleIndex] = []
    seen: set[str] = set()
    for anchor in soup.find_all("a", href=True):
        article_id = _article_id(anchor)
        if not article_id or article_id in seen:
            continue
        row = _metadata_container(anchor)
        row_text = row.get_text(" ", strip=True)
        try:
            published_date = parse_date(row_text)
        except ValueError:
            continue
        url = urljoin(page_url, anchor["href"])
        views, replies = _counts(row)
        raw_title = anchor.get_text(" ", strip=True)
        tag, title = _split_tag(raw_title)
        records.append(
            ArticleIndex(
                article_id=article_id,
                title=title,
                tag=tag,
                published_date=published_date,
                view_count=views,
                reply_count=replies,
                url=url,
                mobile_url=to_mobile_url(url),
                raw={"html": str(row), "source_page_url": page_url},
            )
        )
        seen.add(article_id)
    return records


def filter_articles(
    records: list[ArticleIndex],
    *,
    start_date: date,
    start_title: str,
    require_start_article: bool = True,
) -> list[ArticleIndex]:
    filtered = [record for record in records if record.published_date >= start_date]
    if require_start_article and not any(
        record.title == start_title or record.title.endswith(start_title)
        for record in filtered
    ):
        raise ValueError(f"start article not found in parsed index pages: {start_title}")
    return filtered


def find_next_page_url(html: str, page_url: str) -> str | None:
    soup = BeautifulSoup(html, "lxml")
    for anchor in soup.find_all("a", href=True):
        text = anchor.get_text(" ", strip=True)
        rel = anchor.get("rel", [])
        classes = anchor.get("class", [])
        if text in {"下一页", "下页", "Next", "next", ">"} or "next" in rel or "next" in classes:
            return urljoin(page_url, anchor["href"])
    return None


def to_mobile_url(url: str) -> str:
    parts = urlsplit(url)
    host = parts.netloc
    if host in {"www.tgb.cn", "tgb.cn", "www.taoguba.com.cn", "taoguba.com.cn"}:
        host = "m.tgb.cn"
    return urlunsplit((parts.scheme or "https", host, parts.path, parts.query, parts.fragment))


def _article_id(anchor: Tag) -> str | None:
    explicit = anchor.get("data-article-id")
    if explicit:
        return str(explicit)
    href = str(anchor.get("href", ""))
    match = ARTICLE_PATH.search(href) or SHORT_PATH.search(href)
    return match.group("id") if match else None


def _metadata_container(anchor: Tag) -> Tag:
    return anchor.find_parent("tr") or anchor.find_parent("li") or anchor.parent


def _counts(row: Tag) -> tuple[int, int]:
    match = COUNTS.search(row.get_text(" ", strip=True))
    if not match:
        return 0, 0
    return _parse_count(match.group("views")), _parse_count(match.group("replies"))


def _parse_count(value: str) -> int:
    normalized = value.replace(",", "")
    if normalized.endswith("万"):
        return int(float(normalized[:-1]) * 10_000)
    return int(float(normalized))


def _split_tag(value: str) -> tuple[str | None, str]:
    match = TAG.match(value)
    if not match:
        return None, value.strip()
    return match.group("tag"), value[match.end():].strip()
