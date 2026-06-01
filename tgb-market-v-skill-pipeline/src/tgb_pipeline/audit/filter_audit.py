"""Audit report for filtering outputs and interaction density."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from tgb_pipeline.models import Comment, Interaction
from tgb_pipeline.storage import JSONLStore


def build_filter_quality_report(raw_dir: Path, report_path: Path) -> dict:
    comments_all = JSONLStore(raw_dir / "comments_all.jsonl", Comment, "comment_id").read_all()
    kept_comments = JSONLStore(raw_dir / "comments.jsonl", Comment, "comment_id").read_all()
    interactions = JSONLStore(raw_dir / "interactions.jsonl", Interaction, "interaction_id").read_all()
    aoch_comments = _read_optional(raw_dir / "aoch_discussions.jsonl", Comment, "comment_id")

    keep_reasons = Counter(comment.keep_reason or "unknown" for comment in kept_comments)
    raw_filter_reasons = Counter(
        (comment.raw.get("filter_reason") or "unlabeled") for comment in comments_all
    )
    target_author_comment_count = sum(1 for comment in kept_comments if comment.author_role.value == "target")
    needs_sampling = bool(target_author_comment_count and len(interactions) / target_author_comment_count > 5)
    samples = interactions[:20]

    report = {
        "raw_comment_count": len(comments_all),
        "kept_comment_count": len(kept_comments),
        "kept_ratio": round(len(kept_comments) / len(comments_all), 4) if comments_all else 0.0,
        "aoch_comment_count": len(aoch_comments),
        "interaction_count": len(interactions),
        "keep_reasons": dict(keep_reasons),
        "filter_reasons": dict(raw_filter_reasons),
        "interaction_samples": samples,
        "needs_sampling": needs_sampling,
        "target_author_comment_count": target_author_comment_count,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_render_report(report), encoding="utf-8")
    return report


def _render_report(report: dict) -> str:
    lines = [
        "# Filter Quality Report",
        "",
        "## Summary",
        f"- raw_comment_count: {report['raw_comment_count']}",
        f"- kept_comment_count: {report['kept_comment_count']}",
        f"- kept_ratio: {report['kept_ratio']}",
        f"- aoch_comment_count: {report['aoch_comment_count']}",
        f"- interaction_count: {report['interaction_count']}",
        "",
        "## Keep Reasons",
        "| keep_reason | count |",
        "| --- | ---: |",
    ]
    for key, count in report["keep_reasons"].items():
        lines.append(f"| {key} | {count} |")
    lines.extend(["", "## Filter Reasons", "| filter_reason | count |", "| --- | ---: |"])
    for key, count in report["filter_reasons"].items():
        lines.append(f"| {key} | {count} |")
    lines.extend(["", "## Interaction Samples"])
    for interaction in report["interaction_samples"]:
        excerpt = _excerpt(interaction.raw_content)
        lines.extend(
            [
                f"- interaction_id: {interaction.interaction_id}",
                f"  article_id: {interaction.article_id}",
                f"  member_names: {interaction.member_names}",
                f"  comment_ids: {interaction.comment_ids}",
                f"  keep_reason: {interaction.keep_reason}",
                f"  raw_content_excerpt: {excerpt}",
            ]
        )
    if report["needs_sampling"]:
        lines.append(
            "- interaction density looks high relative to target author comments; manual sampling is recommended."
        )
    return "\n".join(lines) + "\n"


def _excerpt(value: str | None, limit: int = 120) -> str:
    text = (value or "").replace("\n", " ").strip()
    return text if len(text) <= limit else text[: limit - 3] + "..."


def _read_optional(path: Path, model_type, key_field: str):
    if not path.exists():
        return []
    return JSONLStore(path, model_type, key_field).read_all()

