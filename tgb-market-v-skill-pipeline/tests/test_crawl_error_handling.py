from datetime import date
from pathlib import Path

import pytest

from tgb_pipeline.config import load_crawl_config, load_target_config
from tgb_pipeline.crawler.comment_tasks import crawl_comments
from tgb_pipeline.crawler.tasks import crawl_articles
from tgb_pipeline.models import Article, ArticleIndex, Comment, CrawlError
from tgb_pipeline.storage import JSONLStore

FIXTURES = Path(__file__).parent / "fixtures"


class ArticleFetcher:
    def __init__(self, pages: dict[str, str], failures: set[str] | None = None):
        self.pages = pages
        self.failures = failures or set()

    def get_text(self, url: str) -> str:
        if url in self.failures:
            raise RuntimeError(f"boom: {url}")
        return self.pages[url]


def _write_configs(tmp_path: Path) -> tuple[Path, Path]:
    target_path = tmp_path / "target.yaml"
    target_path.write_text(
        """
target:
  platform: taoguba
  author_name: Target Author
  start_article:
    title: Start article
    published_date: "2023-01-15"
    url: https://www.tgb.cn/a/1Vgsye6eK36
""",
        encoding="utf-8",
    )
    crawl_path = tmp_path / "crawl.yaml"
    crawl_path.write_text(
        f"""
crawl:
  user_agent: fixture-agent
  request_interval_seconds: 0
  request_timeout_seconds: 10
  respect_robots_txt: false
  max_comment_pages_per_article: 2
storage:
  raw_dir: {tmp_path.as_posix()}/data/raw
  interim_dir: {tmp_path.as_posix()}/data/interim
  processed_dir: {tmp_path.as_posix()}/data/processed
""",
        encoding="utf-8",
    )
    return target_path, crawl_path


def _write_article_index(tmp_path: Path) -> Path:
    raw_dir = tmp_path / "data" / "raw" / "tgb"
    store = JSONLStore(raw_dir / "articles_index.jsonl", ArticleIndex, "article_id")
    store.append_many(
        [
            ArticleIndex(
                article_id="ok",
                title="Start article",
                published_date=date(2023, 1, 15),
                url="https://www.tgb.cn/a/ok",
                mobile_url="https://m.tgb.cn/a/ok",
            ),
            ArticleIndex(
                article_id="bad",
                title="Bad article",
                published_date=date(2023, 1, 16),
                url="https://www.tgb.cn/a/bad",
                mobile_url="https://m.tgb.cn/a/bad",
            ),
        ]
    )
    return raw_dir


def test_crawl_articles_records_error_and_continues(tmp_path: Path) -> None:
    target_path, crawl_path = _write_configs(tmp_path)
    target = load_target_config(target_path)
    crawl = load_crawl_config(crawl_path)
    raw_dir = _write_article_index(tmp_path)
    article_html = (FIXTURES / "article_page_sample.html").read_text(encoding="utf-8")
    fetcher = ArticleFetcher(
        {
            "https://m.tgb.cn/a/ok": article_html,
        },
        failures={"https://m.tgb.cn/a/bad"},
    )

    article_count, image_count = crawl_articles(target, crawl, fetcher=fetcher)

    assert article_count == 1
    assert image_count >= 1
    assert len(JSONLStore(raw_dir / "articles.jsonl", Article, "article_id").read_all()) == 1
    errors = JSONLStore(raw_dir / "article_crawl_errors.jsonl", CrawlError, "error_id").read_all()
    assert len(errors) == 1
    assert errors[0].article_id == "bad"
    assert errors[0].url == "https://m.tgb.cn/a/bad"


def test_crawl_comments_records_page_error_and_continues_other_articles(tmp_path: Path) -> None:
    target_path, crawl_path = _write_configs(tmp_path)
    target = load_target_config(target_path)
    crawl = load_crawl_config(crawl_path)
    raw_dir = _write_article_index(tmp_path)
    comment_html = (FIXTURES / "comment_page_sample.html").read_text(encoding="utf-8")
    fetcher = ArticleFetcher(
        {
            "https://m.tgb.cn/a/ok": comment_html,
            "https://m.tgb.cn/a/bad": comment_html,
            "https://m.tgb.cn/a/bad-2?type=": comment_html,
        },
        failures={"https://m.tgb.cn/a/ok-2?type="},
    )

    comment_count, image_count = crawl_comments(target, crawl, fetcher=fetcher)

    assert comment_count >= 5
    assert image_count >= 1
    errors = JSONLStore(raw_dir / "comment_crawl_errors.jsonl", CrawlError, "error_id").read_all()
    assert len(errors) == 1
    assert errors[0].article_id == "ok"
    assert errors[0].raw["page_num"] == 2
    assert len(JSONLStore(raw_dir / "comments_all.jsonl", Comment, "comment_id").read_all()) >= 5


def test_crawl_comments_re_raises_permission_error(tmp_path: Path) -> None:
    target_path, crawl_path = _write_configs(tmp_path)
    target = load_target_config(target_path)
    crawl = load_crawl_config(crawl_path)
    _write_article_index(tmp_path)

    class PermissionFetcher:
        def get_text(self, url: str) -> str:
            raise PermissionError("blocked by robots")

    with pytest.raises(PermissionError, match="blocked by robots"):
        crawl_comments(target, crawl, fetcher=PermissionFetcher())
