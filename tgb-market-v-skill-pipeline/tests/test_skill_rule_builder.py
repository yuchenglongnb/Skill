from tgb_pipeline.skill.rule_builder import build_methodology_rules
from tests.skill_fixture_data import make_claim


def test_build_methodology_rules_creates_abstract_rules_with_multi_evidence() -> None:
    accepted = [
        make_claim("claim-1", "量化会改变短线盘中的反馈速度。", tag="量化影响", review_bucket="trading_mechanism"),
        make_claim("claim-2", "量化趋同交易会改变流动性分布。", tag="量化影响", review_bucket="market_environment"),
        make_claim("claim-3", "弱市要先收缩仓位。", tag="风控", review_bucket="risk_control"),
        make_claim("claim-4", "买入前提不成立时先减少交易。", tag="风控", review_bucket="execution_rule"),
    ]

    rules = build_methodology_rules(
        accepted,
        max_rules_per_theme=4,
        max_evidence_per_rule=3,
    )

    assert rules
    assert all(rule.evidence_claim_ids for rule in rules)
    assert any(rule.theme == "量化影响" for rule in rules)
    assert any(rule.theme == "风控" for rule in rules)
    assert all("claim-" in claim_id for rule in rules for claim_id in rule.evidence_claim_ids)
    assert all("规则 1" not in rule.title for rule in rules)
    assert all(rule.rule_text not in {claim.claim_text for claim in accepted} for rule in rules)
