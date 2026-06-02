from datetime import date
from pathlib import Path

from tgb_pipeline.config import load_crawl_config, load_target_config
from tgb_pipeline.crawler.comment_tasks import crawl_comments
from tgb_pipeline.models import ArticleIndex, CommentArticleState, CommentPageState
from tgb_pipeline.storage import JSONLStore


class TrackingFetcher:
    def __init__(self, pages: dict[str, str]):
        self.pages = pages
        self.requested: list[str] = []

    def get_text(self, url: str) -> str:
        self.requested.append(url)
        return self.pages[url]


def _write_configs(tmp_path: Path) -> tuple[Path, Path]:
    target_path = tmp_path / "target.yaml"
    target_path.write_text(
        """
target:
  platform: taoguba
  author_name: Target Author
  start_article:
    title: Article
    published_date: "2023-01-15"
    url: https://www.tgb.cn/a/a1
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
  max_comment_pages_per_article: 100
storage:
  raw_dir: {tmp_path.as_posix()}/raw
  interim_dir: {tmp_path.as_posix()}/interim
  processed_dir: {tmp_path.as_posix()}/processed
""",
        encoding="utf-8",
    )
    return target_path, crawl_path


def _write_index(raw_dir: Path) -> None:
    JSONLStore(raw_dir / "articles_index.jsonl", ArticleIndex, "article_id").append(
        ArticleIndex(
            article_id="a1",
            title="Article",
            published_date=date(2023, 1, 15),
            url="https://www.tgb.cn/a/a1",
            mobile_url="https://m.tgb.cn/a/a1",
        )
    )


def test_crawl_comments_resumes_after_existing_snapshot(tmp_path: Path) -> None:
    target_path, crawl_path = _write_configs(tmp_path)
    target = load_target_config(target_path)
    crawl = load_crawl_config(crawl_path)
    raw_dir = tmp_path / "raw" / "tgb"
    _write_index(raw_dir)
    html_dir = raw_dir / "html"
    html_dir.mkdir(parents=True)
    (html_dir / "a1_comments_page_1.html").write_text(
        """
        <html><div class='plContent'>
          <div class='plItem'><div class='pl_text'>Page one</div></div>
        </div><a href='/a/a1-2?type='>下一页</a></html>
        """,
        encoding="utf-8",
    )
    fetcher = TrackingFetcher(
        {"https://m.tgb.cn/a/a1-2?type=": "<html><div class='plContent'></div></html>"}
    )

    result = crawl_comments(target, crawl, fetcher=fetcher)

    assert fetcher.requested == ["https://m.tgb.cn/a/a1-2?type="]
    assert result.fetched_pages == 1
    states = JSONLStore(raw_dir / "comment_page_states.jsonl", CommentPageState, "state_id").read_all()
    assert {state.page_num for state in states} == {1, 2}
    article_state = JSONLStore(
        raw_dir / "comment_article_states.jsonl",
        CommentArticleState,
        "article_id",
    ).read_all()[0]
    assert article_state.completed is True


def test_crawl_comments_honors_article_start_page_and_max_pages(tmp_path: Path) -> None:
    target_path, crawl_path = _write_configs(tmp_path)
    target = load_target_config(target_path)
    crawl = load_crawl_config(crawl_path)
    raw_dir = tmp_path / "raw" / "tgb"
    _write_index(raw_dir)
    html = """
    <html><div class='plContent'>
      <div class='plItem'>
        <a class='plName'>Member</a>
        <span class='pl_time'>2023-01-15 10:00</span>
        <div class='pl_text'>Still active</div>
      </div>
    </div>
      <a href='/a/a1-102?type='>下一页</a>
      <a href='/a/a1-749?type='>末页</a>
    </html>
    """
    fetcher = TrackingFetcher({"https://m.tgb.cn/a/a1-101?type=": html})

    result = crawl_comments(
        target,
        crawl,
        fetcher=fetcher,
        article_id="a1",
        start_page=101,
        max_pages=101,
    )

    assert fetcher.requested == ["https://m.tgb.cn/a/a1-101?type="]
    assert result.fetched_pages == 1
    assert result.max_limit_articles == 1
