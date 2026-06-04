from datetime import UTC, datetime
from pathlib import Path

import yaml

from tgb_pipeline.cli import main
from tgb_pipeline.models import ClaimSourceType, MethodologyClaim
from tgb_pipeline.storage import JSONLStore


def write_configs(tmp_path: Path) -> tuple[Path, Path]:
    target_path = tmp_path / "target.yaml"
    target_path.write_text(
        """
target:
  platform: taoguba
  author_name: 等主人的猫
  start_article:
    title: 情绪周期是否可靠的思考
    published_date: "2023-01-15"
priority_members:
  - name: Aoch
    aliases: [aoch]
""",
        encoding="utf-8",
    )
    crawl_path = tmp_path / "crawl.yaml"
    crawl_path.write_text(
        f"""
crawl:
  user_agent: fixture-agent
  request_interval_seconds: 0
  request_timeout_seconds: 10
storage:
  raw_dir: {tmp_path.as_posix()}/data/raw
  interim_dir: {tmp_path.as_posix()}/data/interim
  processed_dir: {tmp_path.as_posix()}/data/processed
""",
        encoding="utf-8",
    )
    return target_path, crawl_path


def make_claim(claim_id: str, *, tag: str = "量化影响") -> MethodologyClaim:
    return MethodologyClaim(
        claim_id=claim_id,
        claim_text=f"{claim_id} claim text",
        raw_excerpt=f"{claim_id} raw excerpt",
        source_type=ClaimSourceType.ARTICLE,
        source_ids=[claim_id],
        article_id="2jbi0efIsof",
        source_time=datetime(2024, 1, 1, tzinfo=UTC),
        source_author="等主人的猫",
        method_tags=[tag],
        review_priority="high",
        review_bucket="trading_mechanism",
        raw={"ranking": {"reason": "high_value_tags", "score": 9}},
    )


def test_build_and_apply_review_pack_cli(tmp_path, monkeypatch) -> None:
    processed_dir = tmp_path / "data" / "processed" / "tgb"
    JSONLStore(processed_dir / "review_ready_claims.jsonl", MethodologyClaim, "claim_id").rewrite_all(
        [make_claim("claim-a"), make_claim("claim-b")]
    )
    decisions_path = processed_dir / "review_ready_decisions.yaml"
    decisions_path.parent.mkdir(parents=True, exist_ok=True)
    decisions_path.write_text(
        yaml.safe_dump(
            {
                "version": 1,
                "generated_from": "data/processed/tgb/review_ready_claims.jsonl",
                "defaults": {"decision": "unreviewed"},
                "decisions": {
                    "claim-a": {"decision": "unreviewed", "reason": "trading_mechanism", "edited_claim_text": None, "review_notes": ""},
                    "claim-b": {"decision": "unreviewed", "reason": "trading_mechanism", "edited_claim_text": None, "review_notes": ""},
                },
            },
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    target_path, crawl_path = write_configs(tmp_path)
    monkeypatch.chdir(tmp_path)

    assert main(
        [
            "build-review-pack",
            "--target-config",
            str(target_path),
            "--crawl-config",
            str(crawl_path),
            "--pack-id",
            "quant_impact_top100",
            "--title",
            "量化影响 Top 100",
            "--tag",
            "量化影响",
            "--max-items",
            "100",
        ]
    ) == 0
    pack_path = processed_dir / "review_packs" / "quant_impact_top100.yaml"
    assert pack_path.is_file()

    payload = yaml.safe_load(pack_path.read_text(encoding="utf-8"))
    payload["items"][0]["decision"] = "accepted"
    payload["items"][0]["review_notes"] = "keep"
    pack_path.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8")

    assert main(
        [
            "apply-review-pack",
            "--target-config",
            str(target_path),
            "--crawl-config",
            str(crawl_path),
            "--pack",
            str(pack_path),
        ]
    ) == 0
    updated = yaml.safe_load(decisions_path.read_text(encoding="utf-8"))
    assert updated["decisions"]["claim-a"]["decision"] == "accepted"
    assert (tmp_path / "reports" / "review_packs" / "quant_impact_top100_apply_report.md").is_file()
