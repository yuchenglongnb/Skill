from pathlib import Path

import pytest

from tgb_pipeline.config import load_crawl_config, load_target_config
from tgb_pipeline.crawler.tasks import crawl_articles, crawl_index, seed_start_article

FIXTURES = Path(__file__).parent / "fixtures"


class FixtureFetcher:
    def __init__(self, pages: dict[str, str]):
        self.pages = pages
        self.requested: list[str] = []

    def get_text(self, url: str) -> str:
        self.requested.append(url)
        return self.pages[url]


def write_configs(
    tmp_path: Path,
    *,
    allow_seed_article_fallback: bool = True,
    seed_only_when_index_missing_start: bool = True,
) -> tuple[Path, Path]:
    target_path = tmp_path / "target.yaml"
    target_path.write_text(
        """
target:
  platform: taoguba
  author_name: 等主人的猫
  blog_url: https://www.tgb.cn/blog/123
  start_article:
    title: 情绪周期是否可靠的思考
    published_date: "2023-01-15"
    url: https://www.tgb.cn/a/1Vgsye6eK36
priority_members:
  - name: Aoch
    dedicated_index: true
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
  allow_seed_article_fallback: {str(allow_seed_article_fallback).lower()}
  seed_only_when_index_missing_start: {str(seed_only_when_index_missing_start).lower()}
storage:
  raw_dir: {tmp_path.as_posix()}/raw
  interim_dir: {tmp_path.as_posix()}/interim
  processed_dir: {tmp_path.as_posix()}/processed
""",
        encoding="utf-8",
    )
    return target_path, crawl_path


def test_tasks_write_snapshots_and_resume_without_duplicates(tmp_path: Path) -> None:
    target_path, crawl_path = write_configs(tmp_path)
    target = load_target_config(target_path)
    crawl = load_crawl_config(crawl_path)
    index_html = (FIXTURES / "blog_index_sample.html").read_text(encoding="utf-8")
    article_html = (FIXTURES / "article_page_sample.html").read_text(encoding="utf-8")
    pages = {
        "https://www.tgb.cn/blog/123": index_html,
        "https://m.tgb.cn/Article/5000001/1": article_html,
        "https://m.tgb.cn/Article/4588439/1": article_html,
    }
    fetcher = FixtureFetcher(pages)

    result = crawl_index(target, crawl, fetcher=fetcher)
    assert result.appended_count == 2
    assert result.used_seed_fallback is False
    assert crawl_index(target, crawl, fetcher=fetcher).appended_count == 0
    assert crawl_articles(target, crawl, fetcher=fetcher) == (2, 2)
    assert crawl_articles(target, crawl, fetcher=fetcher) == (0, 0)

    raw_root = tmp_path / "raw" / "tgb"
    assert (raw_root / "articles_index.jsonl").is_file()
    assert (raw_root / "articles.jsonl").is_file()
    assert (raw_root / "images.jsonl").is_file()
    assert (raw_root / "html" / "4588439_page_1.html").is_file()


def test_crawl_index_uses_seed_when_start_article_missing(tmp_path: Path) -> None:
    target_path, crawl_path = write_configs(tmp_path)
    target = load_target_config(target_path)
    crawl = load_crawl_config(crawl_path)
    index_html = """
    <html><body>
      <table>
        <tr><td><a href="/Article/5000001/1">[原] 新阶段复盘</a></td><td>120/3</td><td>2023-02-01</td></tr>
      </table>
    </body></html>
    """
    article_html = (FIXTURES / "article_page_sample.html").read_text(encoding="utf-8")
    fetcher = FixtureFetcher(
        {
            "https://www.tgb.cn/blog/123": index_html,
        }
    )

    result = crawl_index(target, crawl, fetcher=fetcher)
    assert result.used_seed_fallback is True
    assert result.seed_appended_count == 1
    assert result.appended_count == 2


def test_crawl_articles_can_read_seed_record(tmp_path: Path) -> None:
    target_path, crawl_path = write_configs(tmp_path)
    target = load_target_config(target_path)
    crawl = load_crawl_config(crawl_path)
    article_html = (FIXTURES / "article_page_sample.html").read_text(encoding="utf-8")
    fetcher = FixtureFetcher({"https://m.tgb.cn/a/1Vgsye6eK36": article_html})

    assert seed_start_article(target, crawl) == 1
    assert crawl_articles(target, crawl, fetcher=fetcher) == (1, 1)


def test_crawl_index_raises_when_seed_fallback_disabled(tmp_path: Path) -> None:
    target_path, crawl_path = write_configs(tmp_path, allow_seed_article_fallback=False)
    target = load_target_config(target_path)
    crawl = load_crawl_config(crawl_path)
    fetcher = FixtureFetcher({"https://www.tgb.cn/blog/123": "<html><body></body></html>"})

    with pytest.raises(ValueError, match="start article not found"):
        crawl_index(target, crawl, fetcher=fetcher)


def test_seed_start_article_is_deduplicated(tmp_path: Path) -> None:
    target_path, crawl_path = write_configs(tmp_path)
    target = load_target_config(target_path)
    crawl = load_crawl_config(crawl_path)

    assert seed_start_article(target, crawl) == 1
    assert seed_start_article(target, crawl) == 0
