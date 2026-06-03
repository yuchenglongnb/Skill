"""Human-review decision templates for review-ready claims."""

from __future__ import annotations

from pathlib import Path

import yaml

from tgb_pipeline.models import MethodologyClaim
from tgb_pipeline.storage import JSONLStore

VALID_DECISIONS = {"accepted", "rejected", "needs_edit", "unreviewed"}
VALID_REASONS = {
    "core_methodology",
    "trading_mechanism",
    "risk_control",
    "market_environment",
    "execution_rule",
    "too_generic",
    "background_context",
    "duplicate",
    "too_fragmented",
    "needs_human_check",
}


def load_review_ready_decisions(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"review-ready decisions must be a YAML mapping: {path}")
    return payload


def write_review_ready_decision_template(
    claims: list[MethodologyClaim],
    path: Path,
    *,
    overwrite: bool = False,
    generated_from: str = "data/processed/tgb/review_ready_claims.jsonl",
) -> Path:
    if path.exists() and not overwrite:
        return path

    payload = {
        "version": 1,
        "generated_from": generated_from,
        "defaults": {"decision": "unreviewed"},
        "decisions": {claim.claim_id: _build_decision_entry(claim) for claim in claims},
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        yaml.safe_dump(payload, handle, allow_unicode=True, sort_keys=False)
    return path


def sync_review_ready_decisions(claims_path: Path, decisions_path: Path) -> dict:
    claims = JSONLStore(claims_path, MethodologyClaim, "claim_id").read_all()
    current_claim_ids = {claim.claim_id for claim in claims}
    existing = load_review_ready_decisions(decisions_path)
    existing_decisions = existing.get("decisions", {}) if isinstance(existing, dict) else {}
    archived = existing.get("archived_decisions", {}) if isinstance(existing, dict) else {}

    decisions: dict[str, dict] = {}
    preserved = 0
    new_added = 0
    archived_count = 0

    for claim in claims:
        if claim.claim_id in existing_decisions:
            entry = dict(existing_decisions[claim.claim_id])
            entry.update(_build_metadata_fields(claim))
            decisions[claim.claim_id] = entry
            preserved += 1
        else:
            decisions[claim.claim_id] = _build_decision_entry(claim)
            new_added += 1

    archived_decisions = dict(archived) if isinstance(archived, dict) else {}
    for claim_id, entry in existing_decisions.items():
        if claim_id not in current_claim_ids:
            archived_decisions[claim_id] = entry
            archived_count += 1

    payload = {
        "version": 1,
        "generated_from": _relative(claims_path),
        "defaults": {"decision": "unreviewed"},
        "decisions": decisions,
        "archived_decisions": archived_decisions,
    }
    decisions_path.parent.mkdir(parents=True, exist_ok=True)
    with decisions_path.open("w", encoding="utf-8", newline="\n") as handle:
        yaml.safe_dump(payload, handle, allow_unicode=True, sort_keys=False)
    return {
        "preserved": preserved,
        "new_added": new_added,
        "archived": archived_count,
        "total_current_claims": len(claims),
    }


def _build_decision_entry(claim: MethodologyClaim) -> dict[str, object]:
    return {
        "decision": "unreviewed",
        "reason": _default_reason(claim),
        "edited_claim_text": None,
        "review_notes": "",
        **_build_metadata_fields(claim),
    }


def _build_metadata_fields(claim: MethodologyClaim) -> dict[str, object]:
    ranking = (claim.raw or {}).get("ranking") or {}
    return {
        "review_priority": claim.review_priority,
        "review_bucket": claim.review_bucket,
        "method_tags": list(claim.method_tags),
        "article_id": claim.article_id,
        "source_type": claim.source_type.value,
        "raw_excerpt_short": (claim.raw_excerpt or "")[:160],
        "ranking_reason": ranking.get("reason"),
        "ranking_score": ranking.get("score"),
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


def _relative(path: Path) -> str:
    resolved = path.resolve()
    cwd = Path.cwd().resolve()
    try:
        return resolved.relative_to(cwd).as_posix()
    except ValueError:
        return path.as_posix()
