"""Runnable crawl stages shared by the command-line interface."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from tgb_pipeline.config import CrawlConfig, TargetConfig
from tgb_pipeline.crawler.article_inventory import merge_article_indexes
from tgb_pipeline.crawler.article_seeds import load_article_seed_indexes
from tgb_pipeline.crawler.fetch import Fetcher
from tgb_pipeline.crawler.parse_article import parse_article_page
from tgb_pipeline.crawler.parse_blog import (
    filter_articles,
    find_next_page_url,
    parse_blog_index,
)
from tgb_pipeline.crawler.seed import build_seed_article_index
from tgb_pipeline.models import Article, ArticleIndex, CrawlError, ImageAsset
from tgb_pipeline.storage import JSONLStore


@dataclass(frozen=True)
class CrawlIndexResult:
    appended_count: int
    used_seed_fallback: bool = False
    seed_appended_count: int = 0


@dataclass(frozen=True)
class IngestArticleSeedsResult:
    added_count: int
    total_article_index_count: int
    skipped_before_start_count: int
    duplicate_count: int


def crawl_index(
    target_config: TargetConfig,
    crawl_config: CrawlConfig,
    *,
    fetcher: Fetcher | None = None,
) -> CrawlIndexResult:
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
        require_start_article=False,
    )
    if _contains_start_article(selected, target_config):
        return CrawlIndexResult(appended_count=store.append_many(selected))

    if not crawl_config.crawl.allow_seed_article_fallback:
        raise ValueError(
            f"start article not found in parsed index pages: "
            f"{target_config.target.start_article.title}"
        )
    if not target_config.target.start_article.url:
        raise ValueError(
            "target.start_article.url must be configured when public index "
            "does not expose the start article"
        )

    seed_record = build_seed_article_index(target_config)
    appended_count = store.append_many(selected)
    should_append_seed = (
        not crawl_config.crawl.seed_only_when_index_missing_start
        or not any(record.article_id == seed_record.article_id for record in selected)
    )
    seed_appended_count = int(should_append_seed and store.append(seed_record))
    return CrawlIndexResult(
        appended_count=appended_count + seed_appended_count,
        used_seed_fallback=True,
        seed_appended_count=seed_appended_count,
    )


def seed_start_article(
    target_config: TargetConfig,
    crawl_config: CrawlConfig,
) -> int:
    raw_root = crawl_config.storage.raw_dir / "tgb"
    store = JSONLStore(raw_root / "articles_index.jsonl", ArticleIndex, "article_id")
    return int(store.append(build_seed_article_index(target_config)))


def ingest_article_seeds(
    target_config: TargetConfig,
    crawl_config: CrawlConfig,
    article_seeds_path: str | Path,
) -> IngestArticleSeedsResult:
    raw_root = crawl_config.storage.raw_dir / "tgb"
    store = JSONLStore(raw_root / "articles_index.jsonl", ArticleIndex, "article_id")
    existing = store.read_all()
    seed_records, skipped_before_start_count = load_article_seed_indexes(
        Path(article_seeds_path),
        target_config,
    )
    merged = merge_article_indexes(existing, seed_records)
    store.rewrite_all(merged)
    existing_ids = {record.article_id for record in existing}
    new_ids = {record.article_id for record in seed_records}
    added_count = len(new_ids - existing_ids)
    duplicate_count = len(seed_records) - len(new_ids) + len(new_ids & existing_ids)
    return IngestArticleSeedsResult(
        added_count=added_count,
        total_article_index_count=len(merged),
        skipped_before_start_count=skipped_before_start_count,
        duplicate_count=duplicate_count,
    )


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
    error_store = JSONLStore(raw_root / "article_crawl_errors.jsonl", CrawlError, "error_id")
    existing_articles = {record.article_id for record in article_store.read_all()}
    client = fetcher or Fetcher(crawl_config.crawl)
    article_count = 0
    image_count = 0

    for index_record in index_store.read_all():
        if crawl_config.crawl.resume and index_record.article_id in existing_articles:
            continue
        try:
            html = client.get_text(index_record.mobile_url)
            _save_snapshot(html_root / f"{index_record.article_id}_page_1.html", html)
            article, images = parse_article_page(
                html,
                index_record=index_record,
                target_author=target_config.target.author_name,
            )
            image_count += image_store.append_many(images)
            article_count += int(article_store.append(article))
        except PermissionError:
            raise
        except ValueError as exc:
            error_store.append(
                _build_crawl_error(
                    stage="crawl_articles.parse_article",
                    article_id=index_record.article_id,
                    url=index_record.mobile_url,
                    error=exc,
                    error_message=(
                        f"failed to parse article {index_record.article_id} "
                        f"from {index_record.mobile_url}: {exc}"
                    ),
                    raw={"mobile_url": index_record.mobile_url},
                )
            )
            continue
        except Exception as exc:
            error_store.append(
                _build_crawl_error(
                    stage="crawl_articles.fetch_article",
                    article_id=index_record.article_id,
                    url=index_record.mobile_url,
                    error=exc,
                    raw={"mobile_url": index_record.mobile_url},
                )
            )
            continue
    return article_count, image_count


def _contains_start_article(records: list[ArticleIndex], target_config: TargetConfig) -> bool:
    title = target_config.target.start_article.title
    return any(_title_matches(record.title, title) for record in records)


def _title_matches(actual: str, expected: str) -> bool:
    return actual == expected or actual.endswith(expected)


def _save_snapshot(path: Path, html: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")


def _build_crawl_error(
    *,
    stage: str,
    article_id: str | None,
    url: str | None,
    error: Exception,
    error_message: str | None = None,
    raw: dict[str, object] | None = None,
) -> CrawlError:
    payload = {
        "stage": stage,
        "article_id": article_id,
        "url": url,
        "error_type": type(error).__name__,
        "error_message": error_message or str(error),
    }
    digest = hashlib.sha1(repr(sorted(payload.items())).encode("utf-8")).hexdigest()[:16]
    return CrawlError(
        error_id=f"{stage}:{digest}",
        raw=raw or {},
        **payload,
    )
