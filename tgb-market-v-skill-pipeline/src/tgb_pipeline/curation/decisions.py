"""Load and scaffold human-editable review decision files."""

from __future__ import annotations

from pathlib import Path

import yaml

from tgb_pipeline.curation.report import suggest_review_reason
from tgb_pipeline.models import MethodologyClaim


def load_review_decisions(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"review decisions must be a YAML mapping: {path}")
    return payload


def write_review_decision_template(
    claims: list[MethodologyClaim],
    path: Path,
    *,
    overwrite: bool = False,
    generated_from: str = "data/processed/tgb/methodology_claims.jsonl",
) -> Path:
    if path.exists() and not overwrite:
        return path

    decisions: dict[str, dict[str, object]] = {}
    for claim in claims:
        suggested_decision, suggested_reason = suggest_review_reason(claim)
        decisions[claim.claim_id] = {
            "decision": "unreviewed",
            "reason": suggested_reason,
            "edited_claim_text": None,
            "review_notes": "",
            "suggested_decision": suggested_decision,
            "suggested_reason": suggested_reason,
            "source_type": claim.source_type.value,
            "method_tags": list(claim.method_tags),
            "raw_excerpt_short": (claim.raw_excerpt or "")[:120],
        }

    payload = {
        "version": 1,
        "generated_from": generated_from,
        "defaults": {"decision": "unreviewed"},
        "decisions": decisions,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        yaml.safe_dump(payload, handle, allow_unicode=True, sort_keys=False)
    return path

