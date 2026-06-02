from datetime import UTC, datetime, date
from pathlib import Path

from tgb_pipeline.config import load_crawl_config, load_target_config
from tgb_pipeline.crawler.comment_tasks import crawl_comments
from tgb_pipeline.models import ArticleIndex, Comment
from tgb_pipeline.storage import JSONLStore


class FixtureFetcher:
    def __init__(self, html: str = "<html></html>"):
        self.html = html

    def get_text(self, url: str) -> str:
        return self.html


def _write_configs(tmp_path: Path) -> tuple[Path, Path]:
    target_path = tmp_path / "target.yaml"
    target_path.write_text(
        """
target:
  platform: taoguba
  author_name: tester
  start_article:
    title: Start
    published_date: "2023-01-15"
    url: https://www.tgb.cn/a/a1
""",
        encoding="utf-8",
    )
    crawl_path = tmp_path / "crawl.yaml"
    crawl_path.write_text(
        f"""
crawl:
  user_agent: fixture
  request_interval_seconds: 0
  request_timeout_seconds: 10
  respect_robots_txt: false
  max_comment_pages_per_article: 10
storage:
  raw_dir: {tmp_path.as_posix()}/raw
  interim_dir: {tmp_path.as_posix()}/interim
  processed_dir: {tmp_path.as_posix()}/processed
""",
        encoding="utf-8",
    )
    return target_path, crawl_path


def _write_article_index(raw_dir: Path) -> None:
    JSONLStore(raw_dir / "articles_index.jsonl", ArticleIndex, "article_id").append(
        ArticleIndex(
            article_id="a1",
            title="A1",
            published_date=date(2023, 1, 15),
            url="https://www.tgb.cn/a/a1",
            mobile_url="https://m.tgb.cn/a/a1",
        )
    )


def _comment(page_num: int) -> Comment:
    return Comment(
        comment_id=f"c-{page_num}",
        article_id="a1",
        author_name="tester",
        published_at=datetime(2023, 1, 15, 9, page_num, tzinfo=UTC),
        page_num=page_num,
        page_position=1,
        raw_content=f"comment {page_num}",
        content_text=f"comment {page_num}",
    )


def test_crawl_loop_uses_discovered_last_page_when_next_link_missing(tmp_path: Path, monkeypatch) -> None:
    target_path, crawl_path = _write_configs(tmp_path)
    target = load_target_config(target_path)
    crawl = load_crawl_config(crawl_path)
    raw_dir = tmp_path / "raw" / "tgb"
    _write_article_index(raw_dir)

    monkeypatch.setattr(
        "tgb_pipeline.crawler.comment_tasks.parse_comments_page",
        lambda *args, page_num, **kwargs: ([_comment(page_num)], []),
    )
    monkeypatch.setattr(
        "tgb_pipeline.crawler.comment_tasks.find_comment_last_page_num",
        lambda html, page_url: 3,
    )
    monkeypatch.setattr(
        "tgb_pipeline.crawler.comment_tasks.find_comment_next_page_url",
        lambda html, page_url: None,
    )

    result = crawl_comments(target, crawl, fetcher=FixtureFetcher(), max_pages=3)

    assert result.fetched_pages == 3


def test_crawl_loop_breaks_without_known_last_page_when_next_link_missing(
    tmp_path: Path, monkeypatch
) -> None:
    target_path, crawl_path = _write_configs(tmp_path)
    target = load_target_config(target_path)
    crawl = load_crawl_config(crawl_path)
    raw_dir = tmp_path / "raw" / "tgb"
    _write_article_index(raw_dir)

    monkeypatch.setattr(
        "tgb_pipeline.crawler.comment_tasks.parse_comments_page",
        lambda *args, page_num, **kwargs: ([_comment(page_num)], []),
    )
    monkeypatch.setattr(
        "tgb_pipeline.crawler.comment_tasks.find_comment_last_page_num",
        lambda html, page_url: None,
    )
    monkeypatch.setattr(
        "tgb_pipeline.crawler.comment_tasks.find_comment_next_page_url",
        lambda html, page_url: None,
    )

    result = crawl_comments(target, crawl, fetcher=FixtureFetcher(), max_pages=3)

    assert result.fetched_pages == 1
