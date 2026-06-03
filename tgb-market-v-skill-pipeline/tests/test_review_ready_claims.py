from datetime import UTC, datetime

from tgb_pipeline.extraction.review_ready import build_review_ready_claims
from tgb_pipeline.models import ClaimSourceType, MethodologyClaim
from tgb_pipeline.storage import JSONLStore


def _claim(claim_id: str, text: str, tag: str, priority_reason: str, score: int, **overrides) -> MethodologyClaim:
    payload = {
        "claim_id": claim_id,
        "claim_text": text,
        "raw_excerpt": text,
        "source_type": ClaimSourceType.COMMENT,
        "source_ids": [claim_id],
        "article_id": "2jbi0efIsof",
        "source_time": datetime(2024, 1, 1, tzinfo=UTC),
        "source_author": "等主人的猫",
        "method_tags": [tag] if tag else [],
        "raw": {"quality": {"reason": priority_reason, "score": score, "flags": []}},
    }
    payload.update(overrides)
    return MethodologyClaim(**payload)


def test_build_review_ready_claims_splits_low_priority_and_caps_normal(tmp_path) -> None:
    processed_dir = tmp_path / "data" / "processed" / "tgb"
    reports_dir = tmp_path / "reports"
    store = JSONLStore(processed_dir / "methodology_claims.jsonl", MethodologyClaim, "claim_id")
    store.append_many(
        [
            _claim(
                "claim-high",
                "情绪周期不是失效，而是成交额和量化改变了反馈速度。",
                "量化影响",
                "strong_methodology_statement",
                9,
            ),
            _claim(
                "claim-normal-1",
                "赚钱效应走弱后，接力意愿也会同步下降。",
                "赚钱效应",
                "tag_supported_statement",
                4,
                article_id="a1",
            ),
            _claim(
                "claim-normal-2",
                "赚钱效应回落时，追高意愿通常也会回落。",
                "赚钱效应",
                "tag_supported_statement",
                3,
                article_id="a1",
            ),
            _claim(
                "claim-low",
                "市场就是这样。",
                "",
                "generic_market_statement",
                -1,
            ),
        ]
    )

    review_ready_path, low_priority_path = build_review_ready_claims(
        processed_dir,
        reports_dir,
        max_per_tag=1,
    )

    review_ready = JSONLStore(review_ready_path, MethodologyClaim, "claim_id").read_all()
    low_priority = JSONLStore(low_priority_path, MethodologyClaim, "claim_id").read_all()

    assert {claim.claim_id for claim in review_ready} == {"claim-high", "claim-normal-1"}
    assert {claim.claim_id for claim in low_priority} == {"claim-normal-2", "claim-low"}
    assert all(claim.review_priority != "low" for claim in review_ready)
    assert all(claim.review_priority == "low" for claim in low_priority)
