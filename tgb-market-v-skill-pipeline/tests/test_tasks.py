from pathlib import Path

from tgb_pipeline.config import load_crawl_config, load_target_config
from tgb_pipeline.crawler.tasks import crawl_articles, crawl_index

FIXTURES = Path(__file__).parent / "fixtures"


class FixtureFetcher:
    def __init__(self, pages: dict[str, str]):
        self.pages = pages
        self.requested: list[str] = []

    def get_text(self, url: str) -> str:
        self.requested.append(url)
        return self.pages[url]


def write_configs(tmp_path: Path) -> tuple[Path, Path]:
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

    assert crawl_index(target, crawl, fetcher=fetcher) == 2
    assert crawl_index(target, crawl, fetcher=fetcher) == 0
    assert crawl_articles(target, crawl, fetcher=fetcher) == (2, 2)
    assert crawl_articles(target, crawl, fetcher=fetcher) == (0, 0)

    raw_root = tmp_path / "raw" / "tgb"
    assert (raw_root / "articles_index.jsonl").is_file()
    assert (raw_root / "articles.jsonl").is_file()
    assert (raw_root / "images.jsonl").is_file()
    assert (raw_root / "html" / "4588439_page_1.html").is_file()

