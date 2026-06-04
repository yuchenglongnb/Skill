from datetime import UTC, datetime
from pathlib import Path

import yaml

from tgb_pipeline.curation.review_pack import build_review_pack
from tgb_pipeline.models import ClaimSourceType, MethodologyClaim
from tgb_pipeline.storage import JSONLStore


def make_claim(
    claim_id: str,
    *,
    tags: list[str],
    article_id: str = "a1",
    source_type: ClaimSourceType = ClaimSourceType.COMMENT,
    review_priority: str = "normal",
    review_bucket: str = "needs_human_check",
    ranking_score: int = 5,
) -> MethodologyClaim:
    return MethodologyClaim(
        claim_id=claim_id,
        claim_text=f"{claim_id} claim text",
        raw_excerpt=f"{claim_id} raw excerpt",
        source_type=source_type,
        source_ids=[claim_id],
        article_id=article_id,
        source_time=datetime(2024, 1, 1, tzinfo=UTC),
        source_author="等主人的猫",
        method_tags=tags,
        review_priority=review_priority,
        review_bucket=review_bucket,
        raw={"ranking": {"reason": "fixture", "score": ranking_score}},
    )


def test_build_review_pack_filters_by_tag_and_sorts_priority(tmp_path: Path) -> None:
    processed_dir = tmp_path / "data" / "processed" / "tgb"
    reports_dir = tmp_path / "reports"
    JSONLStore(processed_dir / "review_ready_claims.jsonl", MethodologyClaim, "claim_id").rewrite_all(
        [
            make_claim("claim-low", tags=["量化影响"], ranking_score=3),
            make_claim("claim-high", tags=["量化影响"], review_priority="high", ranking_score=10),
            make_claim("claim-other", tags=["成交额"], ranking_score=99),
        ]
    )

    pack_path, report_path = build_review_pack(
        processed_dir,
        reports_dir,
        pack_id="quant_pack",
        title="量化影响 Top",
        tags=["量化影响"],
        max_items=10,
    )

    payload = yaml.safe_load(pack_path.read_text(encoding="utf-8"))
    claim_ids = [item["claim_id"] for item in payload["items"]]
    assert claim_ids == ["claim-high", "claim-low"]
    assert report_path.is_file()
    assert "量化影响 Top" in report_path.read_text(encoding="utf-8")


def test_build_review_pack_filters_article_bucket_and_excludes_reviewed(tmp_path: Path) -> None:
    processed_dir = tmp_path / "data" / "processed" / "tgb"
    reports_dir = tmp_path / "reports"
    JSONLStore(processed_dir / "review_ready_claims.jsonl", MethodologyClaim, "claim_id").rewrite_all(
        [
            make_claim("keep-1", tags=["风控"], article_id="a1", review_bucket="risk_control"),
            make_claim("skip-reviewed", tags=["风控"], article_id="a1", review_bucket="risk_control"),
            make_claim("skip-bucket", tags=["风控"], article_id="a1", review_bucket="market_environment"),
            make_claim("skip-article", tags=["风控"], article_id="a2", review_bucket="risk_control"),
        ]
    )
    decisions_path = processed_dir / "review_ready_decisions.yaml"
    decisions_path.write_text(
        yaml.safe_dump(
            {
                "version": 1,
                "generated_from": "x",
                "defaults": {"decision": "unreviewed"},
                "decisions": {"skip-reviewed": {"decision": "accepted"}},
            },
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    pack_path, _ = build_review_pack(
        processed_dir,
        reports_dir,
        pack_id="risk_pack",
        title="风控",
        article_ids=["a1"],
        buckets=["risk_control"],
        max_items=10,
        decisions_path=decisions_path,
    )

    payload = yaml.safe_load(pack_path.read_text(encoding="utf-8"))
    assert [item["claim_id"] for item in payload["items"]] == ["keep-1"]


def test_build_review_pack_max_items_and_metadata(tmp_path: Path) -> None:
    processed_dir = tmp_path / "data" / "processed" / "tgb"
    reports_dir = tmp_path / "reports"
    claims = [
        make_claim(f"claim-{index}", tags=["指数环境"], ranking_score=100 - index)
        for index in range(4)
    ]
    JSONLStore(processed_dir / "review_ready_claims.jsonl", MethodologyClaim, "claim_id").rewrite_all(claims)

    pack_path, _ = build_review_pack(
        processed_dir,
        reports_dir,
        pack_id="index_pack",
        title="指数环境",
        tags=["指数环境"],
        max_items=2,
    )
    payload = yaml.safe_load(pack_path.read_text(encoding="utf-8"))

    assert len(payload["items"]) == 2
    first_item = payload["items"][0]
    assert "claim_text" in first_item
    assert "raw_excerpt" in first_item
    assert "review_priority" in first_item
    assert "ranking_score" in first_item
