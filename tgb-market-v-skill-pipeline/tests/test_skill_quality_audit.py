from tgb_pipeline.skill.rule_builder import build_methodology_rules
from tgb_pipeline.skill.skill_audit import audit_skill_outputs
from tgb_pipeline.skill.skill_writer import write_review_summary, write_skill_markdown, write_uncertainty_policy
from tests.skill_fixture_data import make_claim


def test_skill_quality_audit_checks_boundaries_and_outputs(tmp_path) -> None:
    accepted = [
        make_claim("claim-1", "量化会改变短线盘中的反馈速度。", tag="量化影响", review_bucket="trading_mechanism"),
        make_claim("claim-2", "量化趋同交易会改变流动性分布。", tag="量化影响", review_bucket="market_environment"),
    ]
    needs_edit = [
        make_claim("claim-3", "像牛市又不像牛市。", tag="牛熊切换", review_status="needs_edit")
    ]
    rejected = [
        make_claim("claim-4", "今天市场一般。", tag="指数环境", review_status="rejected")
    ]
    rules = build_methodology_rules(accepted, max_rules_per_theme=4)
    write_skill_markdown(rules, tmp_path)
    write_uncertainty_policy(tmp_path)
    write_review_summary(accepted, needs_edit, rejected, rules, tmp_path, reviewed_packs=["quant_impact_top100"], unreviewed_count=3)
    (tmp_path / "methodology_profile.md").write_text("# profile\n", encoding="utf-8")
    (tmp_path / "methodology_rules.jsonl").write_text('{"rule_id":"r1"}\n', encoding="utf-8")
    (tmp_path / "rule_evidence_map.jsonl").write_text('{"claim_id":"claim-1"}\n', encoding="utf-8")

    summary = audit_skill_outputs(
        tmp_path,
        rules=rules,
        accepted_claims=accepted,
        accepted_claim_ids={"claim-1", "claim-2"},
        needs_edit_claim_ids={"claim-3"},
        rejected_claim_ids={"claim-4"},
        unreviewed_claim_ids={"claim-5"},
        accepted_claims_count=2,
        needs_edit_claims_count=1,
        rejected_claims_count=1,
        unreviewed_claims_count=1,
        accepted_recheck_candidates_count=1,
    )

    assert summary["generated_rules"] == len(rules)
    assert "量化影响" in summary["rule_coverage_by_theme"]
    assert summary["text_audit"]["corrupted_files"] == 0
    assert summary["rule_abstraction_checks"]["accepted_recheck_candidates"] == 1


def test_skill_quality_audit_allows_descriptive_buy_sell_context(tmp_path) -> None:
    accepted = [
        make_claim("claim-1", "买入前提不成立时先减少交易。", tag="风控", review_bucket="execution_rule"),
        make_claim("claim-2", "弱市要先收缩仓位。", tag="风控", review_bucket="risk_control"),
    ]
    rules = build_methodology_rules(accepted, max_rules_per_theme=4)
    write_skill_markdown(rules, tmp_path)
    write_uncertainty_policy(tmp_path)
    write_review_summary(accepted, [], [], rules, tmp_path, reviewed_packs=["risk_control_top80"], unreviewed_count=0)
    (tmp_path / "methodology_profile.md").write_text("# profile\n", encoding="utf-8")
    (tmp_path / "methodology_rules.jsonl").write_text('{"rule_id":"r1"}\n', encoding="utf-8")
    (tmp_path / "rule_evidence_map.jsonl").write_text('{"claim_id":"claim-1"}\n', encoding="utf-8")

    summary = audit_skill_outputs(
        tmp_path,
        rules=rules,
        accepted_claims=accepted,
        accepted_claim_ids={"claim-1", "claim-2"},
        needs_edit_claim_ids=set(),
        rejected_claim_ids=set(),
        unreviewed_claim_ids=set(),
        accepted_claims_count=2,
        needs_edit_claims_count=0,
        rejected_claims_count=0,
        unreviewed_claims_count=0,
    )

    assert not any("possible investment-advice wording" in warning for warning in summary["warnings"])
    assert not any("buy/sell wording needs manual review" in warning for warning in summary["warnings"])
