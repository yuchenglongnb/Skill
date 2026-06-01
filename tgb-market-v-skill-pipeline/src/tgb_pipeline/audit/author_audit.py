"""Author inventory and diagnostics."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from tgb_pipeline.config import TargetConfig
from tgb_pipeline.filters.author_filter import classify_author_role, normalize_author_name
from tgb_pipeline.models import Comment
from tgb_pipeline.storage import JSONLStore


def build_author_inventory(raw_dir: Path, report_path: Path, target_config: TargetConfig) -> dict:
    comments = JSONLStore(raw_dir / "comments_all.jsonl", Comment, "comment_id").read_all()
    by_author: Counter[str] = Counter(comment.author_name for comment in comments)
    rows = []
    aoch_contains = []
    mention_aoch = []
    target_count = 0
    aoch_count = 0
    unknown_count = 0

    for author_name, count in by_author.most_common():
        normalized = normalize_author_name(author_name)
        role = classify_author_role(author_name, target_config)
        if role.value == "target":
            target_count += count
        elif role.value == "aoch":
            aoch_count += count
        elif role.value == "unknown":
            unknown_count += count
        if "aoch" in normalized:
            aoch_contains.append(author_name)
        rows.append(
            {
                "author_name": author_name,
                "normalized_name": normalized,
                "comment_count": count,
                "classified_role": role.value,
            }
        )

    for comment in comments:
        text = comment.content_text or comment.raw_content or ""
        if "aoch" in text.casefold():
            mention_aoch.append(comment.comment_id)

    exact_aoch_matches = [
        row["author_name"] for row in rows if row["classified_role"] == "aoch"
    ]
    report = {
        "unique_author_count": len(by_author),
        "target_author_comment_count": target_count,
        "aoch_comment_count": aoch_count,
        "unknown_author_count": unknown_count,
        "top_authors": rows,
        "exact_aoch_matches": exact_aoch_matches,
        "aoch_name_candidates": aoch_contains,
        "aoch_content_mentions": mention_aoch,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_render_report(report), encoding="utf-8")
    return report


def _render_report(report: dict) -> str:
    lines = [
        "# Author Inventory",
        "",
        "## Summary",
        f"- unique_author_count: {report['unique_author_count']}",
        f"- target_author_comment_count: {report['target_author_comment_count']}",
        f"- aoch_comment_count: {report['aoch_comment_count']}",
        f"- unknown_author_count: {report['unknown_author_count']}",
        "",
        "## Top Authors",
        "| author_name | normalized_name | comment_count | classified_role |",
        "| --- | --- | ---: | --- |",
    ]
    for row in report["top_authors"][:30]:
        lines.append(
            f"| {row['author_name']} | {row['normalized_name']} | "
            f"{row['comment_count']} | {row['classified_role']} |"
        )
    lines.extend(
        [
            "",
            "## Aoch Diagnostics",
            f"- exact Aoch matches: {report['exact_aoch_matches'] or 'none'}",
            f"- author names containing \"aoch\": {report['aoch_name_candidates'] or 'none'}",
            f"- comments mentioning \"Aoch\" / \"AOCH\": {report['aoch_content_mentions'] or 'none'}",
        ]
    )
    if report["aoch_comment_count"] == 0:
        lines.append(
            "- current crawled corpus has no exact Aoch alias match; this is diagnostic only, not an error."
        )
    return "\n".join(lines) + "\n"

