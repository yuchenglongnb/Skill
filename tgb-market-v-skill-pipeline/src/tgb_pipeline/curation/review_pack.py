"""Build editable review packs from review-ready claims."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import yaml

from tgb_pipeline.curation.review_pack_report import (
    build_review_pack_index,
    build_review_pack_markdown,
)
from tgb_pipeline.curation.review_ready_decisions import load_review_ready_decisions
from tgb_pipeline.models import MethodologyClaim
from tgb_pipeline.storage import JSONLStore

DEFAULT_REVIEW_PACKS = (
    ("quant_impact_top100", "量化影响 Top 100", ["量化影响"], [], [], [], 100),
    ("turnover_top100", "成交额 Top 100", ["成交额"], [], [], [], 100),
    ("short_term_base_top100", "短线基础行情 Top 100", ["短线基础行情"], [], [], [], 100),
    ("index_environment_top100", "指数环境 Top 100", ["指数环境"], [], [], [], 100),
    ("risk_control_top80", "风控 Top 80", ["风控"], [], [], [], 80),
    ("bull_bear_top80", "牛熊切换 Top 80", ["牛熊切换"], [], [], [], 80),
    ("digitization_top80", "数字化/标准化 Top 80", ["数字化/标准化"], [], [], [], 80),
    ("execution_rule_top100", "Execution Rule Top 100", [], [], ["execution_rule"], [], 100),
)


def build_review_pack(
    processed_dir: Path,
    reports_dir: Path,
    *,
    pack_id: str,
    title: str,
    tags: list[str] | None = None,
    article_ids: list[str] | None = None,
    buckets: list[str] | None = None,
    priorities: list[str] | None = None,
    max_items: int = 100,
    exclude_reviewed: bool = True,
    decisions_path: Path | None = None,
) -> tuple[Path, Path]:
    claims = JSONLStore(processed_dir / "review_ready_claims.jsonl", MethodologyClaim, "claim_id").read_all()
    decisions_map = _decision_map(decisions_path) if decisions_path else {}
    selected = _filter_claims(
        claims,
        decisions_map,
        tags=tags or [],
        article_ids=article_ids or [],
        buckets=buckets or [],
        priorities=priorities or [],
        exclude_reviewed=exclude_reviewed,
    )
    selected = _sort_claims(selected)[:max_items]

    packs_dir = processed_dir / "review_packs"
    reports_pack_dir = reports_dir / "review_packs"
    pack_path = packs_dir / f"{pack_id}.yaml"
    report_path = reports_pack_dir / f"{pack_id}.md"
    packs_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "version": 1,
        "pack_id": pack_id,
        "title": title,
        "generated_at": datetime.now(UTC).isoformat(),
        "source_path": _relative(processed_dir / "review_ready_claims.jsonl"),
        "filter_tags": list(tags or []),
        "filter_articles": list(article_ids or []),
        "filter_buckets": list(buckets or []),
        "filter_priorities": list(priorities or []),
        "max_items": max_items,
        "items": [_pack_item_payload(claim) for claim in selected],
    }
    with pack_path.open("w", encoding="utf-8", newline="\n") as handle:
        yaml.safe_dump(payload, handle, allow_unicode=True, sort_keys=False)

    build_review_pack_markdown(
        pack_path,
        report_path,
        title=title,
        tags=list(tags or []),
        article_ids=list(article_ids or []),
        buckets=list(buckets or []),
        items=selected,
    )
    return pack_path, report_path


def build_default_review_packs(
    processed_dir: Path,
    reports_dir: Path,
    *,
    decisions_path: Path | None = None,
) -> list[Path]:
    outputs: list[Path] = []
    for pack_id, title, tags, article_ids, buckets, priorities, max_items in DEFAULT_REVIEW_PACKS:
        pack_path, report_path = build_review_pack(
            processed_dir,
            reports_dir,
            pack_id=pack_id,
            title=title,
            tags=list(tags),
            article_ids=list(article_ids),
            buckets=list(buckets),
            priorities=list(priorities),
            max_items=max_items,
            exclude_reviewed=True,
            decisions_path=decisions_path,
        )
        outputs.extend([pack_path, report_path])
    outputs.append(build_review_pack_index(processed_dir / "review_packs", reports_dir / "review_packs"))
    return outputs


def _filter_claims(
    claims: list[MethodologyClaim],
    decisions_map: dict[str, dict],
    *,
    tags: list[str],
    article_ids: list[str],
    buckets: list[str],
    priorities: list[str],
    exclude_reviewed: bool,
) -> list[MethodologyClaim]:
    selected: list[MethodologyClaim] = []
    for claim in claims:
        if tags and not set(claim.method_tags).intersection(tags):
            continue
        if article_ids and claim.article_id not in article_ids:
            continue
        if buckets and (claim.review_bucket or "") not in buckets:
            continue
        if priorities and claim.review_priority not in priorities:
            continue
        if exclude_reviewed and _is_reviewed(decisions_map.get(claim.claim_id, {})):
            continue
        selected.append(claim)
    return selected


def _sort_claims(claims: list[MethodologyClaim]) -> list[MethodologyClaim]:
    priority_order = {"high": 0, "normal": 1, "low": 2}
    source_order = {"article": 0, "comment": 1, "interaction": 2, "image_ocr": 3}

    def ranking_score(claim: MethodologyClaim) -> int:
        ranking = (claim.raw or {}).get("ranking") or {}
        return int(ranking.get("score", 0))

    return sorted(
        claims,
        key=lambda claim: (
            priority_order.get(claim.review_priority, 9),
            -ranking_score(claim),
            source_order.get(claim.source_type.value, 9),
            claim.claim_id,
        ),
    )


def _pack_item_payload(claim: MethodologyClaim) -> dict[str, object]:
    ranking = (claim.raw or {}).get("ranking") or {}
    return {
        "claim_id": claim.claim_id,
        "decision": "unreviewed",
        "reason": _default_reason(claim),
        "edited_claim_text": None,
        "review_notes": "",
        "method_tags": list(claim.method_tags),
        "article_id": claim.article_id,
        "source_type": claim.source_type.value,
        "review_priority": claim.review_priority,
        "review_bucket": claim.review_bucket,
        "ranking_score": ranking.get("score"),
        "raw_excerpt": claim.raw_excerpt,
        "claim_text": claim.claim_text,
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


def _decision_map(path: Path) -> dict[str, dict]:
    payload = load_review_ready_decisions(path)
    decisions = payload.get("decisions", {}) if isinstance(payload, dict) else {}
    return decisions if isinstance(decisions, dict) else {}


def _is_reviewed(entry: dict) -> bool:
    return str(entry.get("decision", "unreviewed")) in {"accepted", "rejected", "needs_edit"}


def _relative(path: Path) -> str:
    resolved = path.resolve()
    cwd = Path.cwd().resolve()
    try:
        return resolved.relative_to(cwd).as_posix()
    except ValueError:
        return path.as_posix()
