"""Build recheck packs for accepted claims that remain too colloquial or context-heavy."""

from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

import yaml

from tgb_pipeline.models import MethodologyClaim
from tgb_pipeline.skill.rule_builder import THEME_ORDER, primary_theme, select_representative_claims

COLLOQUIAL_TOKENS = (
    "傻问",
    "虫子",
    "大婶",
    "砸成狗",
    "拼裸泳",
    "低纬战高维",
    "癌股",
    "笑死",
    "哈哈",
    "服了",
)

STRONG_CONTEXT_TOKENS = (
    "今天",
    "这里",
    "那个",
    "这次",
    "昨天",
    "午后",
    "竞价",
)


def build_accepted_recheck_pack(
    accepted_claims: list[MethodologyClaim],
    processed_dir: Path,
    reports_dir: Path,
) -> tuple[Path, Path, int]:
    candidates = []
    for claim in accepted_claims:
        flags = detect_accepted_recheck_flags(claim)
        if flags:
            candidates.append((claim, flags))

    sorted_claims = select_representative_claims([claim for claim, _ in candidates], len(candidates))
    flag_map = {claim.claim_id: flags for claim, flags in candidates}

    pack_path = processed_dir / "review_packs" / "accepted_recheck_v0_2.yaml"
    report_path = reports_dir / "review_packs" / "accepted_recheck_v0_2.md"
    pack_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "version": 1,
        "pack_id": "accepted_recheck_v0_2",
        "title": "Accepted Recheck v0.2",
        "generated_at": datetime.now(UTC).isoformat(),
        "source_path": _relative(processed_dir / "accepted_review_ready_claims.jsonl"),
        "items": [_pack_item_payload(claim, flag_map[claim.claim_id]) for claim in sorted_claims],
    }
    with pack_path.open("w", encoding="utf-8", newline="\n") as handle:
        yaml.safe_dump(payload, handle, allow_unicode=True, sort_keys=False)

    _write_recheck_markdown(sorted_claims, flag_map, report_path)
    return pack_path, report_path, len(sorted_claims)


def detect_accepted_recheck_flags(claim: MethodologyClaim) -> list[str]:
    flags: list[str] = []
    text = (claim.claim_text or "").strip()
    notes = (claim.review_notes or "") + " " + str((claim.raw or {}).get("review_notes", ""))
    haystack = " ".join([text, claim.raw_excerpt or "", notes])

    if any(token in haystack for token in COLLOQUIAL_TOKENS):
        flags.append("colloquial_or_exaggerated")
    if len(text) < 18:
        flags.append("too_short")
    if "？" in text or "?" in text:
        flags.append("rhetorical_or_question")
    if any(token in haystack for token in STRONG_CONTEXT_TOKENS):
        flags.append("strong_context_dependency")
    if any(token in haystack for token in ("needs_human_check", "反讽", "打趣", "上下文")):
        flags.append("review_note_uncertainty")
    return flags


def _pack_item_payload(claim: MethodologyClaim, flags: list[str]) -> dict[str, object]:
    ranking = (claim.raw or {}).get("ranking") or {}
    return {
        "claim_id": claim.claim_id,
        "decision": "accepted",
        "reason": claim.review_bucket or claim.review_status,
        "edited_claim_text": None,
        "review_notes": claim.review_notes or "",
        "recheck_reason": flags,
        "method_tags": list(claim.method_tags),
        "article_id": claim.article_id,
        "source_type": claim.source_type.value,
        "review_priority": claim.review_priority,
        "review_bucket": claim.review_bucket,
        "ranking_score": ranking.get("score"),
        "raw_excerpt": claim.raw_excerpt,
        "claim_text": claim.claim_text,
    }


def _write_recheck_markdown(
    claims: list[MethodologyClaim],
    flag_map: dict[str, list[str]],
    report_path: Path,
) -> None:
    grouped: dict[str, list[MethodologyClaim]] = defaultdict(list)
    for claim in claims:
        grouped[primary_theme(claim) or "未分类"].append(claim)

    lines = [
        "# Review Pack: Accepted Recheck v0.2",
        "",
        "## Summary",
        f"- pack_id: accepted_recheck_v0_2",
        f"- total_items: {len(claims)}",
        "",
        "## Items",
        "",
    ]
    for theme in [*THEME_ORDER, "未分类"]:
        theme_claims = grouped.get(theme, [])
        if not theme_claims:
            continue
        lines.append(f"### {theme}")
        lines.append("")
        for index, claim in enumerate(theme_claims, start=1):
            lines.extend(
                [
                    f"#### {index}. {claim.claim_id}",
                    f"- recheck_reason: {flag_map[claim.claim_id]}",
                    f"- article_id: {claim.article_id}",
                    f"- source_type: {claim.source_type.value}",
                    f"- review_notes: {claim.review_notes or ''}",
                    "",
                    "Raw excerpt:",
                    f"> {(claim.raw_excerpt or '').replace(chr(10), ' ')}",
                    "",
                    "Accepted claim:",
                    f"> {(claim.claim_text or '').replace(chr(10), ' ')}",
                    "",
                ]
            )
    report_path.write_text("\n".join(lines), encoding="utf-8")


def _relative(path: Path) -> str:
    resolved = path.resolve()
    cwd = Path.cwd().resolve()
    try:
        return resolved.relative_to(cwd).as_posix()
    except ValueError:
        return path.as_posix()
