from tgb_pipeline.skill.rule_builder import build_methodology_rules
from tests.skill_fixture_data import make_claim


def test_build_methodology_rules_uses_only_accepted_themes_and_evidence() -> None:
    accepted = [
        make_claim("claim-1", "量化会改变短线反馈速度。", tag="量化影响"),
        make_claim("claim-2", "弱市先收缩仓位。", tag="风控"),
        make_claim("claim-3", "成交额不足时短线高度受限。", tag="成交额"),
    ]

    rules = build_methodology_rules(
        accepted,
        max_rules_per_theme=3,
        max_evidence_per_rule=2,
    )

    assert rules
    assert all(rule.evidence_claim_ids for rule in rules)
    assert any(rule.theme == "量化影响" for rule in rules)
    assert any(rule.theme == "风控" for rule in rules)
    assert any(rule.theme == "成交额 / 量能" for rule in rules)
    assert all(claim_id in {"claim-1", "claim-2", "claim-3"} for rule in rules for claim_id in rule.evidence_claim_ids)
