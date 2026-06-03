from datetime import UTC, datetime

from tgb_pipeline.extraction.ranking import rank_claim_for_review
from tgb_pipeline.models import ClaimSourceType, MethodologyClaim


def test_digitization_standardization_tag_is_high_value() -> None:
    claim = MethodologyClaim(
        claim_id="claim-digitization",
        claim_text="数字化/标准化的核心是把竞价活跃度转成可比较的统一指标。",
        raw_excerpt="数字化/标准化的核心是把竞价活跃度转成可比较的统一指标。",
        source_type=ClaimSourceType.ARTICLE,
        source_ids=["a1"],
        article_id="a1",
        source_time=datetime(2024, 1, 1, tzinfo=UTC),
        source_author="等主人的猫",
        method_tags=["数字化/标准化"],
        raw={"quality": {"reason": "strong_methodology_statement", "score": 5, "flags": []}},
    )

    ranked = rank_claim_for_review(claim)

    assert ranked.review_priority == "high"
    assert ranked.review_bucket == "trading_mechanism"
    assert "high_value_tags" in ranked.raw["ranking"]["reason"]
