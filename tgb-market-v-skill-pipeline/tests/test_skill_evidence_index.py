import json

from tgb_pipeline.skill.evidence_index import (
    build_needs_edit_evidence_index,
    build_rule_evidence_map,
    build_skill_evidence_index,
)
from tgb_pipeline.skill.rule_builder import build_methodology_rules
from tests.skill_fixture_data import make_claim


def test_skill_evidence_index_uses_only_accepted_and_separates_needs_edit(tmp_path) -> None:
    accepted = [
        make_claim("claim-a", "量化会改变短线盘中的反馈速度。", tag="量化影响", review_bucket="trading_mechanism"),
        make_claim("claim-b", "量化趋同交易会改变流动性分布。", tag="量化影响", review_bucket="market_environment"),
    ]
    needs_edit = [
        make_claim(
            "claim-c",
            "像牛市又不像牛市。",
            tag="牛熊切换",
            review_status="needs_edit",
        )
    ]

    accepted_path = build_skill_evidence_index(accepted, tmp_path)
    needs_edit_path = build_needs_edit_evidence_index(needs_edit, tmp_path)
    rules = build_methodology_rules(accepted, max_rules_per_theme=4)
    rule_map_path = build_rule_evidence_map(
        rules,
        accepted,
        tmp_path,
        recheck_flags_by_claim={"claim-a": ["strong_context_dependency"]},
    )

    accepted_rows = [json.loads(line) for line in accepted_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    needs_edit_rows = [json.loads(line) for line in needs_edit_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    rule_map_rows = [json.loads(line) for line in rule_map_path.read_text(encoding="utf-8").splitlines() if line.strip()]

    assert [row["claim_id"] for row in accepted_rows] == ["claim-a", "claim-b"]
    assert accepted_rows[0]["article_id"] == "a1"
    assert accepted_rows[0]["raw_excerpt"] == "量化会改变短线盘中的反馈速度。"
    assert [row["claim_id"] for row in needs_edit_rows] == ["claim-c"]
    assert all(row["claim_id"] in {"claim-a", "claim-b"} for row in rule_map_rows)
    assert "claim_text" in rule_map_rows[0]
    assert "recheck_flags" in rule_map_rows[0]
