"""Audit comment article state consistency warnings."""

from __future__ import annotations

from pathlib import Path

from tgb_pipeline.models import CommentArticleState
from tgb_pipeline.storage import JSONLStore


def build_comment_state_warning_report(raw_dir: Path, reports_dir: Path) -> Path:
    states = _read_optional(
        raw_dir / "comment_article_states.jsonl",
        CommentArticleState,
        "article_id",
    )
    warning_rows = []
    for state in states:
        warnings = state.raw.get("state_warnings", [])
        if warnings:
            warning_rows.append(
                {
                    "article_id": state.article_id,
                    "title": state.title or "",
                    "max_fetched_page": state.max_fetched_page,
                    "discovered_last_page": state.discovered_last_page,
                    "completed": state.completed,
                    "next_page_to_fetch": state.next_page_to_fetch,
                    "warnings": ", ".join(warnings),
                }
            )
    report_path = reports_dir / "comment_state_warnings.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_render_report(states, warning_rows), encoding="utf-8")
    return report_path


def _render_report(states: list[CommentArticleState], warning_rows: list[dict[str, object]]) -> str:
    lines = [
        "# Comment State Warnings",
        "",
        "## Summary",
        f"- total_states: {len(states)}",
        f"- warning_states: {len(warning_rows)}",
        "",
        "## Warnings",
        "| article_id | title | max_fetched_page | discovered_last_page | completed | next_page_to_fetch | warnings |",
        "| --- | --- | ---: | ---: | --- | ---: | --- |",
    ]
    for row in warning_rows:
        lines.append(
            f"| {row['article_id']} | {row['title']} | {row['max_fetched_page']} | "
            f"{row['discovered_last_page'] or ''} | {row['completed']} | "
            f"{row['next_page_to_fetch']} | {row['warnings']} |"
        )
    return "\n".join(lines) + "\n"


def _read_optional(path: Path, model_type, key_field: str):
    if not path.exists():
        return []
    return JSONLStore(path, model_type, key_field).read_all()
