from datetime import UTC, datetime

from tgb_pipeline.extraction.ranking import rank_claim_for_review
from tgb_pipeline.models import ClaimSourceType, MethodologyClaim


def _claim(**overrides) -> MethodologyClaim:
    payload = {
        "claim_id": "claim-1",
        "claim_text": "情绪周期不是失效，而是成交额和量化改变了反馈速度。",
        "raw_excerpt": "情绪周期不是失效，而是成交额和量化改变了反馈速度。",
        "source_type": ClaimSourceType.COMMENT,
        "source_ids": ["c1"],
        "article_id": "2jbi0efIsof",
        "source_time": datetime(2024, 1, 1, tzinfo=UTC),
        "source_author": "等主人的猫",
        "method_tags": ["情绪周期", "成交额", "量化影响"],
        "raw": {"quality": {"reason": "strong_methodology_statement", "score": 5, "flags": []}},
    }
    payload.update(overrides)
    return MethodologyClaim(**payload)


def test_rank_claim_for_review_marks_strong_structure_high() -> None:
    ranked = rank_claim_for_review(_claim())

    assert ranked.review_priority == "high"
    assert ranked.review_bucket == "trading_mechanism"
    assert ranked.raw["ranking"]["score"] >= 5


def test_rank_claim_for_review_keeps_article_out_of_low_by_default() -> None:
    ranked = rank_claim_for_review(
        _claim(
            source_type=ClaimSourceType.ARTICLE,
            source_ids=["a1"],
            claim_text="短线基础行情会压制个股高度。",
            raw_excerpt="短线基础行情会压制个股高度。",
            method_tags=["短线基础行情"],
            article_id="a1",
            raw={"quality": {"reason": "tag_supported_statement", "score": 2, "flags": []}},
        )
    )

    assert ranked.review_priority in {"high", "normal"}


def test_rank_claim_for_review_marks_short_generic_low() -> None:
    ranked = rank_claim_for_review(
        _claim(
            claim_text="市场就是这样。",
            raw_excerpt="市场就是这样。",
            method_tags=[],
            article_id="a1",
            raw={
                "quality": {
                    "reason": "generic_market_statement",
                    "score": -1,
                    "flags": ["has_generic_market_terms", "short_text"],
                }
            },
        )
    )

    assert ranked.review_priority == "low"
    assert ranked.review_bucket == "generic_market"
