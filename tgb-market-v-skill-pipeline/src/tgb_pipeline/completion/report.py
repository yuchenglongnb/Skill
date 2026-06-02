"""Render comment completion plans as copyable commands."""

from __future__ import annotations

from pathlib import Path

from tgb_pipeline.models import CommentCompletionPlan


def build_comment_completion_plan_report(
    plan: CommentCompletionPlan,
    reports_dir: Path,
) -> Path:
    report_path = reports_dir / "comment_completion_plan.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_render_report(plan), encoding="utf-8")
    return report_path


def _render_report(plan: CommentCompletionPlan) -> str:
    lines = [
        "# Comment Completion Plan",
        "",
        "## Summary",
        f"- total_items: {plan.total_items}",
        f"- total_planned_pages: {plan.total_planned_pages}",
        "",
        "## Plan Items",
        "| article_id | title | next_page | target_max_page | last_page | planned_pages | reason |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in plan.items:
        lines.append(
            f"| {item.article_id} | {item.title or ''} | {item.next_page_to_fetch} | "
            f"{item.target_max_page} | {item.discovered_last_page or ''} | "
            f"{item.planned_pages} | {item.reason or ''} |"
        )
    lines.extend(["", "## Suggested Commands", ""])
    if not plan.items:
        lines.append("All comment articles are complete or no plannable items remain.")
    for item in plan.items:
        lines.extend(
            [
                "```powershell",
                "python -m tgb_pipeline crawl-comments "
                "--target-config configs/target.yaml "
                "--crawl-config configs/crawl.yaml "
                f"--article-id {item.article_id} "
                f"--start-page {item.next_page_to_fetch} "
                f"--max-pages {item.target_max_page}",
                "```",
                "",
            ]
        )
    return "\n".join(lines) + "\n"
