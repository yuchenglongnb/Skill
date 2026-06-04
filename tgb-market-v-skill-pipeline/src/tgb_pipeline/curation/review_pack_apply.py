"""Apply editable review pack decisions back into review_ready_decisions.yaml."""

from __future__ import annotations

from pathlib import Path

import yaml

from tgb_pipeline.curation.review_ready_decisions import load_review_ready_decisions


def apply_review_pack_decisions(
    pack_path: Path,
    decisions_path: Path,
    *,
    overwrite_existing: bool = False,
) -> dict:
    with pack_path.open("r", encoding="utf-8") as handle:
        pack_payload = yaml.safe_load(handle) or {}
    items = pack_payload.get("items", []) if isinstance(pack_payload, dict) else []
    decisions_payload = load_review_ready_decisions(decisions_path)
    decisions_map = decisions_payload.get("decisions", {}) if isinstance(decisions_payload, dict) else {}

    stats = {
        "applied": 0,
        "skipped_unreviewed": 0,
        "skipped_missing": 0,
        "skipped_existing": 0,
        "overwritten": 0,
        "pack_path": pack_path.as_posix(),
        "decisions_path": decisions_path.as_posix(),
    }

    for item in items:
        if not isinstance(item, dict):
            continue
        claim_id = item.get("claim_id")
        decision = str(item.get("decision", "unreviewed"))
        if decision == "unreviewed":
            stats["skipped_unreviewed"] += 1
            continue
        if claim_id not in decisions_map:
            stats["skipped_missing"] += 1
            continue
        existing = decisions_map[claim_id]
        existing_decision = str(existing.get("decision", "unreviewed"))
        if existing_decision in {"accepted", "rejected", "needs_edit"} and not overwrite_existing:
            stats["skipped_existing"] += 1
            continue
        if existing_decision in {"accepted", "rejected", "needs_edit"} and overwrite_existing:
            stats["overwritten"] += 1

        existing["decision"] = decision
        existing["reason"] = item.get("reason")
        existing["edited_claim_text"] = item.get("edited_claim_text")
        existing["review_notes"] = item.get("review_notes")
        stats["applied"] += 1

    decisions_path.parent.mkdir(parents=True, exist_ok=True)
    with decisions_path.open("w", encoding="utf-8", newline="\n") as handle:
        yaml.safe_dump(decisions_payload, handle, allow_unicode=True, sort_keys=False)
    return stats
