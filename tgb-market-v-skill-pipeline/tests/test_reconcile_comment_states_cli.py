from pathlib import Path

from tgb_pipeline.cli import main
from tgb_pipeline.models import CommentArticleState, CommentPageState
from tgb_pipeline.storage import JSONLStore
from tests.export_fixture_data import build_sample_corpus


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
storage:
  raw_dir: {tmp_path.as_posix()}/data/raw
  interim_dir: {tmp_path.as_posix()}/data/interim
  processed_dir: {tmp_path.as_posix()}/data/processed
""",
        encoding="utf-8",
    )
    return target_path, crawl_path


def test_reconcile_comment_states_cli_regenerates_states_and_warning_report(tmp_path, monkeypatch) -> None:
    raw_dir, _, _ = build_sample_corpus(tmp_path)
    target_path, crawl_path = _write_configs(tmp_path)
    monkeypatch.chdir(tmp_path)

    JSONLStore(raw_dir / "comment_page_states.jsonl", CommentPageState, "state_id").append(
        CommentPageState(
            state_id="comment-page-a1-1",
            article_id="a1",
            page_num=1,
            page_url="https://m.tgb.cn/a/a1",
            status="fetched",
            discovered_last_page=10,
            has_next_page=False,
        )
    )
    JSONLStore(raw_dir / "comment_article_states.jsonl", CommentArticleState, "article_id").append(
        CommentArticleState(
            article_id="a1",
            title="Article 1",
            discovered_last_page=10,
            max_fetched_page=1,
            next_page_to_fetch=1,
            completed=True,
            raw={"state_warnings": ["completed_before_discovered_last_page"]},
        )
    )

    assert main(
        [
            "reconcile-comment-states",
            "--target-config",
            str(target_path),
            "--crawl-config",
            str(crawl_path),
        ]
    ) == 0

    states = JSONLStore(raw_dir / "comment_article_states.jsonl", CommentArticleState, "article_id").read_all()
    assert states[0].completed is False
    assert states[0].next_page_to_fetch == 3
    assert (tmp_path / "reports" / "comment_state_warnings.md").is_file()
    assert (tmp_path / "reports" / "article_inventory_report.md").is_file()
