from pathlib import Path

import yaml

from tgb_pipeline.models import ClaimSourceType, MethodologyClaim
from tgb_pipeline.storage import JSONLStore


def test_yaml_roundtrip_preserves_chinese_review_notes(tmp_path: Path) -> None:
    payload = {
        "version": 1,
        "pack_id": "quant_impact_top100",
        "title": "量化影响 Top 100",
        "source_path": "data/processed/tgb/review_ready_claims.jsonl",
        "items": [
            {
                "claim_id": "claim-a",
                "decision": "accepted",
                "reason": "trading_mechanism",
                "edited_claim_text": None,
                "review_notes": "保留：属于量化影响下的交易机制或市场结构判断。",
            }
        ],
    }
    path = tmp_path / "pack.yaml"
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        yaml.safe_dump(payload, handle, allow_unicode=True, sort_keys=False)

    roundtrip = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert roundtrip["items"][0]["review_notes"] == "保留：属于量化影响下的交易机制或市场结构判断。"


def test_jsonl_roundtrip_preserves_chinese_review_notes(tmp_path: Path) -> None:
    claim = MethodologyClaim(
        claim_id="claim-a",
        claim_text="量化影响改变了短线反馈速度。",
        raw_excerpt="量化影响改变了短线反馈速度。",
        source_type=ClaimSourceType.COMMENT,
        source_ids=["claim-a"],
        article_id="2jbi0efIsof",
        source_author="等主人的猫",
        method_tags=["量化影响"],
        review_notes="待确认：疑似反讽、打趣或上下文不足，需要人工结合原文确认。",
        raw={"review_notes": "待确认：疑似反讽、打趣或上下文不足，需要人工结合原文确认。"},
    )
    path = tmp_path / "accepted_review_ready_claims.jsonl"
    JSONLStore(path, MethodologyClaim, "claim_id").rewrite_all([claim])

    reloaded = JSONLStore(path, MethodologyClaim, "claim_id").read_all()
    assert reloaded[0].review_notes == "待确认：疑似反讽、打趣或上下文不足，需要人工结合原文确认。"
