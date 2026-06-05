from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from tgb_pipeline.models import ClaimSourceType, MethodologyClaim
from tgb_pipeline.storage import JSONLStore


def make_claim(
    claim_id: str,
    claim_text: str,
    *,
    tag: str,
    article_id: str = "a1",
    source_type: ClaimSourceType = ClaimSourceType.COMMENT,
    review_status: str = "accepted",
    review_notes: str | None = None,
) -> MethodologyClaim:
    return MethodologyClaim(
        claim_id=claim_id,
        claim_text=claim_text,
        raw_excerpt=claim_text,
        source_type=source_type,
        source_ids=[f"src-{claim_id}"],
        article_id=article_id,
        source_time=datetime(2024, 1, 1, tzinfo=UTC),
        source_author="等主人的猫",
        method_tags=[tag],
        review_status=review_status,
        review_notes=review_notes,
        review_priority="high",
        review_bucket="core_methodology",
        raw={"ranking": {"score": 10}, "review_reason": review_status},
    )


def write_skill_inputs(tmp_path: Path) -> tuple[Path, Path, Path]:
    raw_dir = tmp_path / "data" / "raw" / "tgb"
    processed_dir = tmp_path / "data" / "processed" / "tgb"
    reports_dir = tmp_path / "reports"
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    accepted = [
        make_claim("claim-quant", "量化资金会改变短线反馈速度。", tag="量化影响", article_id="2jbi0efIsof"),
        make_claim("claim-turnover", "成交额不足时短线高度会受限。", tag="成交额", article_id="2ohHCnLXtP8"),
        make_claim("claim-short", "短线基础行情差时接力容错会下降。", tag="短线基础行情", article_id="2bWeZGDSi07"),
        make_claim("claim-index", "指数环境转弱会压制短线承接。", tag="指数环境", article_id="2bWeZGDSi07"),
        make_claim("claim-risk", "弱市要先收缩仓位。", tag="风控", article_id="2bWeZGDSi07"),
        make_claim("claim-bullbear", "牛熊切换时不能套用同一套短线节奏。", tag="牛熊切换", article_id="2bWeZGDSi07"),
    ]
    needs_edit = [
        make_claim(
            "claim-needs",
            "像牛市又不像牛市，先别激动。",
            tag="牛熊切换",
            review_status="needs_edit",
            review_notes="待确认：疑似反讽、打趣或上下文不足，需要人工结合原文确认。",
        )
    ]
    rejected = [
        make_claim(
            "claim-rejected",
            "今天市场又不太行。",
            tag="指数环境",
            review_status="rejected",
            review_notes="拒绝：表述偏泛，不能独立构成方法论。",
        )
    ]
    review_ready = [*accepted, *needs_edit, *rejected]

    JSONLStore(processed_dir / "accepted_review_ready_claims.jsonl", MethodologyClaim, "claim_id").rewrite_all(accepted)
    JSONLStore(processed_dir / "needs_edit_review_ready_claims.jsonl", MethodologyClaim, "claim_id").rewrite_all(needs_edit)
    JSONLStore(processed_dir / "rejected_review_ready_claims.jsonl", MethodologyClaim, "claim_id").rewrite_all(rejected)
    JSONLStore(processed_dir / "review_ready_claims.jsonl", MethodologyClaim, "claim_id").rewrite_all(review_ready)

    for name in [
        "review_ready_curated_profile.md",
        "review_ready_curation_report.md",
    ]:
        (reports_dir / name).write_text(f"# {name}\n", encoding="utf-8")
    review_packs_dir = reports_dir / "review_packs"
    review_packs_dir.mkdir(parents=True, exist_ok=True)
    for name in [
        "quant_impact_top100_apply_report.md",
        "turnover_top100_apply_report.md",
        "short_term_base_top100_apply_report.md",
        "risk_control_top80_apply_report.md",
        "bull_bear_top80_apply_report.md",
    ]:
        (review_packs_dir / name).write_text(f"# {name}\n", encoding="utf-8")

    return raw_dir, processed_dir, reports_dir


def write_minimal_configs(tmp_path: Path) -> tuple[Path, Path]:
    target_path = tmp_path / "target.yaml"
    target_path.write_text(
        """
target:
  platform: taoguba
  author_name: 等主人的猫
  start_article:
    title: 情绪周期是否可靠的思考
    published_date: "2023-01-15"
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
