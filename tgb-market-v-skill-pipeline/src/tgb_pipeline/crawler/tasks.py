"""Runnable crawl stages shared by the command-line interface."""

from __future__ import annotations

from pathlib import Path

from tgb_pipeline.config import CrawlConfig, TargetConfig
from tgb_pipeline.crawler.fetch import Fetcher
from tgb_pipeline.crawler.parse_article import parse_article_page
from tgb_pipeline.crawler.parse_blog import (
    filter_articles,
    find_next_page_url,
    parse_blog_index,
)
from tgb_pipeline.models import Article, ArticleIndex, ImageAsset
from tgb_pipeline.storage import JSONLStore


def crawl_index(
    target_config: TargetConfig,
    crawl_config: CrawlConfig,
    *,
    fetcher: Fetcher | None = None,
) -> int:
    blog_url = target_config.target.blog_url
    if not blog_url:
        raise ValueError("target.blog_url must be configured before running crawl-index")

    raw_root = crawl_config.storage.raw_dir / "tgb"
    html_root = raw_root / "html"
    store = JSONLStore(raw_root / "articles_index.jsonl", ArticleIndex, "article_id")
    client = fetcher or Fetcher(crawl_config.crawl)
    records: list[ArticleIndex] = []
    visited: set[str] = set()
    next_url: str | None = blog_url

    for page_number in range(1, crawl_config.crawl.max_index_pages + 1):
        if not next_url or next_url in visited:
            break
        visited.add(next_url)
        html = client.get_text(next_url)
        _save_snapshot(html_root / f"blog_index_page_{page_number}.html", html)
        page_records = parse_blog_index(html, next_url)
        records.extend(page_records)
        if _contains_start_article(records, target_config):
            oldest = min((record.published_date for record in records), default=None)
            if oldest and oldest <= target_config.target.start_article.published_date:
                break
        next_url = find_next_page_url(html, next_url)

    selected = filter_articles(
        records,
        start_date=target_config.target.start_article.published_date,
        start_title=target_config.target.start_article.title,
    )
    return store.append_many(selected)


def crawl_articles(
    target_config: TargetConfig,
    crawl_config: CrawlConfig,
    *,
    fetcher: Fetcher | None = None,
) -> tuple[int, int]:
    raw_root = crawl_config.storage.raw_dir / "tgb"
    html_root = raw_root / "html"
    index_store = JSONLStore(raw_root / "articles_index.jsonl", ArticleIndex, "article_id")
    article_store = JSONLStore(raw_root / "articles.jsonl", Article, "article_id")
    image_store = JSONLStore(raw_root / "images.jsonl", ImageAsset, "image_id")
    existing_articles = {record.article_id for record in article_store.read_all()}
    client = fetcher or Fetcher(crawl_config.crawl)
    article_count = 0
    image_count = 0

    for index_record in index_store.read_all():
        if crawl_config.crawl.resume and index_record.article_id in existing_articles:
            continue
        html = client.get_text(index_record.mobile_url)
        _save_snapshot(html_root / f"{index_record.article_id}_page_1.html", html)
        article, images = parse_article_page(
            html,
            index_record=index_record,
            target_author=target_config.target.author_name,
        )
        image_count += image_store.append_many(images)
        article_count += int(article_store.append(article))
    return article_count, image_count


def _contains_start_article(records: list[ArticleIndex], target_config: TargetConfig) -> bool:
    title = target_config.target.start_article.title
    return any(_title_matches(record.title, title) for record in records)


def _title_matches(actual: str, expected: str) -> bool:
    return actual == expected or actual.endswith(expected)


def _save_snapshot(path: Path, html: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")

