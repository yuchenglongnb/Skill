from datetime import UTC, datetime

import yaml

from tgb_pipeline.curation.review_pack import build_default_review_packs
from tgb_pipeline.models import ClaimSourceType, MethodologyClaim
from tgb_pipeline.storage import JSONLStore


def make_claim(claim_id: str, tag: str, bucket: str = "trading_mechanism") -> MethodologyClaim:
    return MethodologyClaim(
        claim_id=claim_id,
        claim_text=f"{claim_id} claim text",
        raw_excerpt=f"{claim_id} raw excerpt",
        source_type=ClaimSourceType.ARTICLE,
        source_ids=[claim_id],
        article_id="a1",
        source_time=datetime(2024, 1, 1, tzinfo=UTC),
        source_author="等主人的猫",
        method_tags=[tag],
        review_priority="high",
        review_bucket=bucket,
        raw={"ranking": {"reason": "fixture", "score": 10}},
    )


def test_build_default_review_packs_generates_index_and_files(tmp_path) -> None:
    processed_dir = tmp_path / "data" / "processed" / "tgb"
    reports_dir = tmp_path / "reports"
    JSONLStore(processed_dir / "review_ready_claims.jsonl", MethodologyClaim, "claim_id").rewrite_all(
        [
            make_claim("claim-1", "量化影响"),
            make_claim("claim-2", "成交额"),
            make_claim("claim-3", "短线基础行情"),
            make_claim("claim-4", "指数环境", bucket="market_environment"),
            make_claim("claim-5", "风控", bucket="risk_control"),
            make_claim("claim-6", "牛熊切换"),
            make_claim("claim-7", "数字化/标准化"),
            make_claim("claim-8", "买入触发", bucket="execution_rule"),
        ]
    )

    outputs = build_default_review_packs(processed_dir, reports_dir)

    assert outputs
    assert (processed_dir / "review_packs" / "quant_impact_top100.yaml").is_file()
    assert (processed_dir / "review_packs" / "digitization_top80.yaml").is_file()
    assert (reports_dir / "review_packs" / "index.md").is_file()

    payload = yaml.safe_load((processed_dir / "review_packs" / "digitization_top80.yaml").read_text(encoding="utf-8"))
    assert payload["pack_id"] == "digitization_top80"
