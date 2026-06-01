from datetime import UTC, datetime

from tgb_pipeline.curation.apply_review import apply_review_decisions
from tgb_pipeline.models import ClaimSourceType, MethodologyClaim


def make_claim(claim_id: str) -> MethodologyClaim:
    return MethodologyClaim(
        claim_id=claim_id,
        claim_text="情绪周期切换要结合成交额。",
        raw_excerpt="情绪周期切换要结合成交额。",
        source_type=ClaimSourceType.ARTICLE,
        source_ids=["a1"],
        article_id="a1",
        source_time=datetime(2023, 1, 15, tzinfo=UTC),
        source_author="等主人的猫",
        method_tags=["情绪周期", "成交额"],
    )


def test_apply_review_splits_claims_and_preserves_edit_history() -> None:
    claims = [make_claim("claim-a"), make_claim("claim-b"), make_claim("claim-c")]
    decisions = {
        "decisions": {
            "claim-a": {"decision": "accepted", "reason": "core_methodology"},
            "claim-b": {
                "decision": "needs_edit",
                "reason": "useful_context",
                "edited_claim_text": "压缩后的表述",
                "review_notes": "保留逻辑，缩短文本",
            },
            "claim-c": {"decision": "rejected", "reason": "too_generic"},
        }
    }

    accepted, rejected, needs_edit = apply_review_decisions(claims, decisions)

    assert [claim.claim_id for claim in accepted] == ["claim-a"]
    assert [claim.claim_id for claim in rejected] == ["claim-c"]
    assert [claim.claim_id for claim in needs_edit] == ["claim-b"]
    assert needs_edit[0].claim_text == "压缩后的表述"
    assert needs_edit[0].raw["edited_from_claim_text"] == "情绪周期切换要结合成交额。"


def test_unreviewed_is_excluded_by_default_and_can_be_included() -> None:
    claims = [make_claim("claim-a")]

    accepted, rejected, needs_edit = apply_review_decisions(claims, {"decisions": {}})
    assert accepted == []
    assert rejected == []
    assert needs_edit == []

    accepted, rejected, needs_edit = apply_review_decisions(
        claims,
        {"decisions": {}},
        include_unreviewed=True,
    )
    assert accepted == []
    assert rejected == []
    assert [claim.claim_id for claim in needs_edit] == ["claim-a"]

