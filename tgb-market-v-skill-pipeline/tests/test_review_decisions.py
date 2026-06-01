from datetime import UTC, datetime
from pathlib import Path

from tgb_pipeline.curation.decisions import load_review_decisions, write_review_decision_template
from tgb_pipeline.models import ClaimSourceType, MethodologyClaim


def make_claim() -> MethodologyClaim:
    return MethodologyClaim(
        claim_id="claim-1",
        claim_text="情绪周期切换要结合成交额。",
        raw_excerpt="情绪周期切换要结合成交额。",
        source_type=ClaimSourceType.ARTICLE,
        source_ids=["a1"],
        article_id="a1",
        source_time=datetime(2023, 1, 15, tzinfo=UTC),
        source_author="等主人的猫",
        method_tags=["情绪周期", "成交额"],
    )


def test_write_review_decision_template_and_load(tmp_path: Path) -> None:
    path = tmp_path / "claim_review_decisions.yaml"
    write_review_decision_template([make_claim()], path)
    payload = load_review_decisions(path)

    assert path.is_file()
    assert payload["defaults"]["decision"] == "unreviewed"
    assert "claim-1" in payload["decisions"]


def test_existing_review_template_is_not_overwritten_by_default(tmp_path: Path) -> None:
    path = tmp_path / "claim_review_decisions.yaml"
    path.write_text("version: 1\ncustom: true\n", encoding="utf-8")

    write_review_decision_template([make_claim()], path, overwrite=False)

    assert "custom: true" in path.read_text(encoding="utf-8")

