"""Markdown reports for article seed discovery."""

from __future__ import annotations

from pathlib import Path

from tgb_pipeline.models import ArticleSeedCandidate


def build_article_seed_candidate_report(
    candidates: list[ArticleSeedCandidate],
    reports_dir: Path,
) -> Path:
    report_path = reports_dir / "article_seed_candidates.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_render_report(candidates), encoding="utf-8")
    return report_path


def _render_report(candidates: list[ArticleSeedCandidate]) -> str:
    sorted_candidates = sorted(
        candidates,
        key=lambda item: (item.published_date is None, item.published_date or item.article_id, item.article_id),
    )
    lines = [
        "# Article Seed Candidates",
        "",
        "## Summary",
        f"- total_candidates: {len(sorted_candidates)}",
        f"- high_confidence: {sum(1 for item in sorted_candidates if item.confidence == 'high')}",
        f"- medium_confidence: {sum(1 for item in sorted_candidates if item.confidence == 'medium')}",
        f"- candidate_only: {sum(1 for item in sorted_candidates if item.confidence == 'candidate')}",
        f"- selected: {sum(1 for item in sorted_candidates if item.selected)}",
        f"- missing_date: {sum(1 for item in sorted_candidates if item.published_date is None)}",
        f"- missing_title: {sum(1 for item in sorted_candidates if not item.title)}",
        "",
    ]
    if len(sorted_candidates) == 1:
        lines.extend(
            [
                "Only one article candidate found; add more source files or links to reach full corpus coverage.",
                "",
            ]
        )
    lines.extend(
        [
            "## Candidates",
            "| selected | confidence | article_id | published_date | title | url | mobile_url | source |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for item in sorted_candidates:
        lines.append(
            f"| {item.selected} | {item.confidence} | {item.article_id} | "
            f"{item.published_date.isoformat() if item.published_date else ''} | "
            f"{item.title or ''} | {item.url} | {item.mobile_url} | {item.source or ''} |"
        )
    return "\n".join(lines) + "\n"
