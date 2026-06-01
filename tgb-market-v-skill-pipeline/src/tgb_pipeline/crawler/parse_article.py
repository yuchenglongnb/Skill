"""Parse a Taoguba article page into text and first-class image evidence."""

from __future__ import annotations

from copy import copy

from bs4 import BeautifulSoup, Tag

from tgb_pipeline.crawler.extract_images import extract_article_images
from tgb_pipeline.models import Article, ArticleIndex, ImageAsset
from tgb_pipeline.utils.dates import parse_datetime
from tgb_pipeline.utils.text_cleaning import clean_text

CONTENT_SELECTORS = (
    "[data-role='article-content']",
    "#article-content",
    ".article-content",
    ".p_coten",
    ".topic-content",
    ".article-body",
    ".main-content",
)
TITLE_SELECTORS = ("h1", ".article-title", ".title")
AUTHOR_SELECTORS = (".author-name", ".article-author", "[data-role='author']")
TIME_SELECTORS = ("time", ".publish-time", ".article-time", "[data-role='published-at']")


def parse_article_page(
    html: str,
    *,
    index_record: ArticleIndex,
    target_author: str,
) -> tuple[Article, list[ImageAsset]]:
    soup = BeautifulSoup(html, "lxml")
    container = _first(soup, CONTENT_SELECTORS)
    if container is None:
        raise ValueError(f"article content container not found: {index_record.article_id}")

    content_html = str(container)
    content = copy(container)
    for unwanted in content.select("script, style, noscript"):
        unwanted.decompose()
    images = extract_article_images(
        content,
        article_id=index_record.article_id,
        page_url=index_record.mobile_url,
    )
    text = clean_text(content.get_text("\n", strip=True))
    title = _text_or_default(soup, TITLE_SELECTORS, index_record.title)
    author_name = _text_or_default(soup, AUTHOR_SELECTORS, target_author)
    published_at = _published_at(soup, index_record)
    article = Article(
        article_id=index_record.article_id,
        title=title,
        author_name=author_name,
        published_at=published_at,
        url=index_record.url,
        raw_content=text,
        content_text=text,
        image_asset_ids=[image.image_id for image in images],
        raw={
            "content_html": content_html,
            "source_page_url": index_record.mobile_url,
            "index_raw": index_record.raw,
        },
    )
    return article, images


def _first(soup: BeautifulSoup, selectors: tuple[str, ...]) -> Tag | None:
    for selector in selectors:
        match = soup.select_one(selector)
        if isinstance(match, Tag):
            return match
    return None


def _text_or_default(soup: BeautifulSoup, selectors: tuple[str, ...], default: str) -> str:
    match = _first(soup, selectors)
    return match.get_text(" ", strip=True) if match else default


def _published_at(soup: BeautifulSoup, index_record: ArticleIndex):
    match = _first(soup, TIME_SELECTORS)
    if match:
        value = match.get("datetime") or match.get_text(" ", strip=True)
        try:
            return parse_datetime(str(value))
        except ValueError:
            pass
    return parse_datetime(index_record.published_date.isoformat())

