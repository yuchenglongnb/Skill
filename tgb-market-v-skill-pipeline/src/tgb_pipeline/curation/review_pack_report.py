"""Reporting helpers for review pack workflows."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from tgb_pipeline.models import MethodologyClaim


def build_review_pack_markdown(
    pack_path: Path,
    report_path: Path,
    *,
    title: str,
    tags: list[str],
    article_ids: list[str],
    buckets: list[str],
    items: list[MethodologyClaim],
) -> Path:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Review Pack: {title}",
        "",
        "## Summary",
        f"- pack_id: {pack_path.stem}",
        f"- total_items: {len(items)}",
        f"- tags: {tags}",
        f"- articles: {article_ids}",
        f"- buckets: {buckets}",
        "",
        "## Items",
        "",
    ]
    for index, claim in enumerate(items, start=1):
        ranking = (claim.raw or {}).get("ranking") or {}
        lines.extend(
            [
                f"### {index}. {claim.claim_id}",
                "",
                "- decision: unreviewed",
                f"- reason: {_default_reason(claim)}",
                f"- tags: {claim.method_tags}",
                f"- article_id: {claim.article_id}",
                f"- source_type: {claim.source_type.value}",
                f"- priority: {claim.review_priority}",
                f"- bucket: {claim.review_bucket}",
                f"- ranking_score: {ranking.get('score')}",
                "",
                "Raw excerpt:",
                f"> {(claim.raw_excerpt or '').replace(chr(10), ' ')}",
                "",
                "Candidate claim:",
                f"> {(claim.claim_text or '').replace(chr(10), ' ')}",
                "",
            ]
        )
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def build_review_pack_index(
    packs_dir: Path,
    reports_dir: Path,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    pack_files = sorted(packs_dir.glob("*.yaml"))
    report_files = sorted((reports_dir).glob("*.md"))
    lines = [
        "# Review Pack Index",
        "",
        f"- total_packs: {len(pack_files)}",
        f"- total_reports: {len(report_files)}",
        "",
        "## Packs",
        "",
    ]
    if not pack_files:
        lines.append("- none")
    else:
        for path in pack_files:
            lines.append(f"- {path.stem}: {path.as_posix()}")
    lines.append("")
    index_path = reports_dir / "index.md"
    index_path.write_text("\n".join(lines), encoding="utf-8")
    return index_path


def build_review_pack_apply_report(
    stats: dict,
    pack_path: Path,
    reports_dir: Path,
) -> Path:
    report_dir = reports_dir / "review_packs"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"{pack_path.stem}_apply_report.md"
    lines = [
        f"# Review Pack Apply Report: {pack_path.stem}",
        "",
        f"- pack_path: {pack_path.as_posix()}",
        f"- decisions_path: {stats.get('decisions_path')}",
        f"- applied: {stats.get('applied', 0)}",
        f"- skipped_unreviewed: {stats.get('skipped_unreviewed', 0)}",
        f"- skipped_missing: {stats.get('skipped_missing', 0)}",
        f"- skipped_existing: {stats.get('skipped_existing', 0)}",
        f"- overwritten: {stats.get('overwritten', 0)}",
        "",
    ]
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def summarize_pack_items(claims: list[MethodologyClaim]) -> dict[str, object]:
    return {
        "total_items": len(claims),
        "by_tag": dict(Counter(tag for claim in claims for tag in claim.method_tags)),
        "by_bucket": dict(Counter((claim.review_bucket or "unknown") for claim in claims)),
        "by_priority": dict(Counter(claim.review_priority for claim in claims)),
    }


def _default_reason(claim: MethodologyClaim) -> str:
    bucket_to_reason = {
        "core_methodology": "core_methodology",
        "trading_mechanism": "trading_mechanism",
        "risk_control": "risk_control",
        "market_environment": "market_environment",
        "execution_rule": "execution_rule",
        "background_context": "background_context",
        "generic_market": "too_generic",
        "short_reply": "too_fragmented",
        "analogy_background": "background_context",
        "needs_human_check": "needs_human_check",
    }
    return bucket_to_reason.get(claim.review_bucket or "", "needs_human_check")
