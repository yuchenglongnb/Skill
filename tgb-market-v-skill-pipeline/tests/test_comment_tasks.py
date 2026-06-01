from pathlib import Path

from tgb_pipeline.config import load_crawl_config, load_target_config
from tgb_pipeline.crawler.comment_tasks import crawl_comments, filter_comments
from tgb_pipeline.crawler.tasks import seed_start_article
from tgb_pipeline.models import Comment, Interaction
from tgb_pipeline.storage import JSONLStore

FIXTURES = Path(__file__).parent / "fixtures"


class FixtureFetcher:
    def __init__(self, pages: dict[str, str]):
        self.pages = pages

    def get_text(self, url: str) -> str:
        return self.pages[url]


def write_configs(tmp_path: Path) -> tuple[Path, Path]:
    target_path = tmp_path / "target.yaml"
    target_path.write_text(
        """
target:
  platform: taoguba
  author_name: 等主人的猫
  start_article:
    title: 情绪周期是否可靠的思考
    published_date: "2023-01-15"
    url: https://www.tgb.cn/a/1Vgsye6eK36
priority_members:
  - name: Aoch
    aliases: [aoch]
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
  raw_dir: {tmp_path.as_posix()}/raw
  interim_dir: {tmp_path.as_posix()}/interim
  processed_dir: {tmp_path.as_posix()}/processed
""",
        encoding="utf-8",
    )
    return target_path, crawl_path


def test_crawl_comments_and_filter_comments_work_from_seed(tmp_path: Path) -> None:
    target_path, crawl_path = write_configs(tmp_path)
    target = load_target_config(target_path)
    crawl = load_crawl_config(crawl_path)
    html = (FIXTURES / "comment_page_sample.html").read_text(encoding="utf-8")
    fetcher = FixtureFetcher(
        {
            "https://m.tgb.cn/a/1Vgsye6eK36": html,
            "https://m.tgb.cn/a/1Vgsye6eK36-2?type=": "<html><body><div class='plContent'></div></body></html>",
        }
    )

    assert seed_start_article(target, crawl) == 1
    comment_count, image_count = crawl_comments(target, crawl, fetcher=fetcher)
    assert comment_count == 5
    assert image_count == 1

    filtered_count, aoch_count, interaction_count = filter_comments(target, crawl)
    assert filtered_count >= 3
    assert aoch_count == 1
    assert interaction_count >= 1

    raw_root = tmp_path / "raw" / "tgb"
    comments_all_store = JSONLStore(raw_root / "comments_all.jsonl", Comment, "comment_id")
    filtered_store = JSONLStore(raw_root / "comments.jsonl", Comment, "comment_id")
    interactions_store = JSONLStore(raw_root / "interactions.jsonl", Interaction, "interaction_id")
    assert len(comments_all_store.read_all()) == 5
    assert filtered_store.read_all()
    assert interactions_store.read_all()
    assert (raw_root / "html" / "1Vgsye6eK36_comments_page_1.html").is_file()
