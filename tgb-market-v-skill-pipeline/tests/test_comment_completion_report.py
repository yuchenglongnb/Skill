from datetime import UTC, datetime

from tgb_pipeline.completion.report import build_comment_completion_plan_report
from tgb_pipeline.models import CommentCompletionPlan, CommentCompletionPlanItem


def test_comment_completion_report_contains_copyable_command(tmp_path) -> None:
    plan = CommentCompletionPlan(
        plan_id="plan-1",
        generated_at=datetime.now(UTC),
        total_items=1,
        total_planned_pages=100,
        items=[
            CommentCompletionPlanItem(
                article_id="a1",
                title="Article",
                next_page_to_fetch=101,
                target_max_page=200,
                discovered_last_page=749,
                remaining_known_pages=649,
                planned_pages=100,
            )
        ],
    )

    report = build_comment_completion_plan_report(plan, tmp_path)
    content = report.read_text(encoding="utf-8")

    assert "# Comment Completion Plan" in content
    assert "--article-id a1 --start-page 101 --max-pages 200" in content
