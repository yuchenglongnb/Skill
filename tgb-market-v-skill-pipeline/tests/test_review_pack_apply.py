from pathlib import Path

import yaml

from tgb_pipeline.curation.review_pack_apply import apply_review_pack_decisions


def write_pack(path: Path, items: list[dict]) -> None:
    payload = {
        "version": 1,
        "pack_id": "pack-1",
        "title": "Pack 1",
        "source_path": "data/processed/tgb/review_ready_claims.jsonl",
        "items": items,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8")


def write_decisions(path: Path) -> None:
    payload = {
        "version": 1,
        "generated_from": "data/processed/tgb/review_ready_claims.jsonl",
        "defaults": {"decision": "unreviewed"},
        "decisions": {
            "claim-a": {
                "decision": "unreviewed",
                "reason": "trading_mechanism",
                "edited_claim_text": None,
                "review_notes": "",
                "review_priority": "high",
            },
            "claim-b": {
                "decision": "accepted",
                "reason": "trading_mechanism",
                "edited_claim_text": None,
                "review_notes": "old",
                "review_priority": "high",
            },
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8")


def test_apply_review_pack_decisions_updates_non_unreviewed_only(tmp_path: Path) -> None:
    pack_path = tmp_path / "pack.yaml"
    decisions_path = tmp_path / "review_ready_decisions.yaml"
    write_pack(
        pack_path,
        [
            {"claim_id": "claim-a", "decision": "accepted", "reason": "trading_mechanism", "edited_claim_text": None, "review_notes": "keep"},
            {"claim_id": "claim-b", "decision": "unreviewed", "reason": "trading_mechanism", "edited_claim_text": None, "review_notes": ""},
            {"claim_id": "claim-missing", "decision": "rejected", "reason": "too_generic", "edited_claim_text": None, "review_notes": "skip"},
        ],
    )
    write_decisions(decisions_path)

    stats = apply_review_pack_decisions(pack_path, decisions_path)
    payload = yaml.safe_load(decisions_path.read_text(encoding="utf-8"))

    assert stats["applied"] == 1
    assert stats["skipped_unreviewed"] == 1
    assert stats["skipped_missing"] == 1
    assert payload["decisions"]["claim-a"]["decision"] == "accepted"
    assert payload["decisions"]["claim-a"]["review_notes"] == "keep"


def test_apply_review_pack_respects_existing_and_overwrite(tmp_path: Path) -> None:
    pack_path = tmp_path / "pack.yaml"
    decisions_path = tmp_path / "review_ready_decisions.yaml"
    write_pack(
        pack_path,
        [
            {"claim_id": "claim-b", "decision": "rejected", "reason": "too_generic", "edited_claim_text": None, "review_notes": "replace"},
        ],
    )
    write_decisions(decisions_path)

    stats = apply_review_pack_decisions(pack_path, decisions_path)
    payload = yaml.safe_load(decisions_path.read_text(encoding="utf-8"))
    assert stats["skipped_existing"] == 1
    assert payload["decisions"]["claim-b"]["decision"] == "accepted"

    stats = apply_review_pack_decisions(pack_path, decisions_path, overwrite_existing=True)
    payload = yaml.safe_load(decisions_path.read_text(encoding="utf-8"))
    assert stats["applied"] == 1
    assert stats["overwritten"] == 1
    assert payload["decisions"]["claim-b"]["decision"] == "rejected"
