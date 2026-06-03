from datetime import UTC, datetime

from tgb_pipeline.curation.review_ready_apply import apply_review_ready_decisions
from tgb_pipeline.models import ClaimSourceType, MethodologyClaim


def make_claim(claim_id: str) -> MethodologyClaim:
    return MethodologyClaim(
        claim_id=claim_id,
        claim_text="成交额和量化共振会改变短线反馈节奏。",
        raw_excerpt="成交额和量化共振会改变短线反馈节奏。",
        source_type=ClaimSourceType.COMMENT,
        source_ids=[claim_id],
        article_id="2jbi0efIsof",
        source_time=datetime(2024, 1, 1, tzinfo=UTC),
        source_author="等主人的猫",
        method_tags=["成交额", "量化影响"],
        review_priority="high",
        review_bucket="trading_mechanism",
        raw={},
    )


def test_apply_review_ready_decisions_splits_outputs_and_preserves_edit_origin() -> None:
    claims = [make_claim("accepted"), make_claim("rejected"), make_claim("edited"), make_claim("unreviewed")]
    decisions = {
        "decisions": {
            "accepted": {
                "decision": "accepted",
                "reason": "trading_mechanism",
                "review_notes": "keep",
                "edited_claim_text": None,
            },
            "rejected": {
                "decision": "rejected",
                "reason": "too_generic",
                "review_notes": "drop",
                "edited_claim_text": None,
            },
            "edited": {
                "decision": "needs_edit",
                "reason": "needs_human_check",
                "review_notes": "shorten",
                "edited_claim_text": "量化和成交额共同改变短线反馈速度。",
            },
        }
    }

    accepted, rejected, needs_edit = apply_review_ready_decisions(claims, decisions)

    assert [claim.claim_id for claim in accepted] == ["accepted"]
    assert [claim.claim_id for claim in rejected] == ["rejected"]
    assert [claim.claim_id for claim in needs_edit] == ["edited"]
    assert needs_edit[0].claim_text == "量化和成交额共同改变短线反馈速度。"
    assert needs_edit[0].raw["edited_from_claim_text"] == "成交额和量化共振会改变短线反馈节奏。"
    assert accepted[0].raw["review_source"] == "review_ready_decisions.yaml"


def test_apply_review_ready_decisions_can_include_unreviewed() -> None:
    claims = [make_claim("claim-1")]
    accepted, rejected, needs_edit = apply_review_ready_decisions(claims, {"decisions": {}}, include_unreviewed=True)

    assert accepted == []
    assert rejected == []
    assert [claim.claim_id for claim in needs_edit] == ["claim-1"]
    assert needs_edit[0].raw["review_decision"] == "unreviewed"
