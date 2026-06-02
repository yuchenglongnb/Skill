from pathlib import Path

from tgb_pipeline.audit.comment_state_audit import build_comment_state_warning_report
from tgb_pipeline.models import CommentArticleState
from tgb_pipeline.storage import JSONLStore


def test_comment_state_warning_report_is_generated(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw" / "tgb"
    reports_dir = tmp_path / "reports"
    JSONLStore(raw_dir / "comment_article_states.jsonl", CommentArticleState, "article_id").append_many(
        [
            CommentArticleState(
                article_id="a1",
                title="Article 1",
                max_fetched_page=500,
                discovered_last_page=749,
                next_page_to_fetch=500,
                completed=True,
                raw={"state_warnings": ["completed_before_discovered_last_page"]},
            ),
            CommentArticleState(
                article_id="a2",
                title="Article 2",
                max_fetched_page=10,
                discovered_last_page=10,
                next_page_to_fetch=10,
                completed=True,
                raw={"state_warnings": []},
            ),
        ]
    )

    report_path = build_comment_state_warning_report(raw_dir, reports_dir)
    text = report_path.read_text(encoding="utf-8")

    assert report_path == reports_dir / "comment_state_warnings.md"
    assert "warning_states: 1" in text
    assert "completed_before_discovered_last_page" in text
    assert "a1" in text
