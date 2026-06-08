import json

from tgb_pipeline.skill.rule_builder import build_methodology_rules
from tgb_pipeline.skill.skill_writer import write_skill_markdown
from tests.skill_fixture_data import make_claim


def test_rule_text_is_not_direct_claim_text_and_skill_md_has_no_long_raw_excerpt(tmp_path) -> None:
    accepted = [
        make_claim("claim-a", "量化会改变短线盘中的反馈速度，并重塑追涨和抛压的时间结构。", tag="量化影响", review_bucket="trading_mechanism"),
        make_claim("claim-b", "量化趋同交易会改变流动性分布，并影响盘中承接和回封节奏。", tag="量化影响", review_bucket="market_environment"),
    ]
    rules = build_methodology_rules(accepted, max_rules_per_theme=4)
    for rule in rules:
        assert rule.rule_text not in {claim.claim_text for claim in accepted}
        assert "规则 1" not in rule.title

    skill_path = write_skill_markdown(rules, tmp_path)
    skill_text = skill_path.read_text(encoding="utf-8")
    assert "量化会改变短线盘中的反馈速度，并重塑追涨和抛压的时间结构。" not in skill_text
    assert "量化趋同交易会改变流动性分布，并影响盘中承接和回封节奏。" not in skill_text
