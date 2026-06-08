import json

from tgb_pipeline.skill.rule_builder import build_methodology_rules
from tgb_pipeline.skill.rule_writer import write_methodology_rules, write_needs_edit_worklist, write_skill_quality_report
from tests.skill_fixture_data import make_claim


def test_rule_writer_outputs_rules_quality_report_and_needs_edit_worklist(tmp_path) -> None:
    accepted = [
        make_claim("claim-1", "量化会改变短线盘中的反馈速度。", tag="量化影响", review_bucket="trading_mechanism"),
        make_claim("claim-2", "量化趋同交易会改变流动性分布。", tag="量化影响", review_bucket="market_environment"),
    ]
    needs_edit = [
        make_claim(
            "claim-3",
            "像牛市又不像牛市。",
            tag="牛熊切换",
            review_status="needs_edit",
            review_notes="待确认：需要上下文。",
        )
    ]
    rules = build_methodology_rules(accepted, max_rules_per_theme=4)

    rules_path = write_methodology_rules(rules, tmp_path)
    worklist_path = write_needs_edit_worklist(needs_edit, tmp_path)
    quality_path = write_skill_quality_report(
        {
            "accepted_claims": 2,
            "generated_rules": len(rules),
            "needs_edit_claims": 1,
            "rejected_claims": 0,
            "unreviewed_claims": 0,
            "rule_coverage_by_theme": {"量化影响": {"rules": 1, "evidence_claims": 2}},
            "evidence_density": {rules[0].rule_id: 2},
            "rule_abstraction_checks": {
                "direct_excerpt_in_rule_text": 0,
                "generic_rule_titles": 0,
                "raw_excerpt_in_skill_md": 0,
                "accepted_recheck_candidates": 1,
            },
            "warnings": [],
        },
        tmp_path,
    )

    rows = [json.loads(line) for line in rules_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    worklist_text = worklist_path.read_text(encoding="utf-8")
    quality_text = quality_path.read_text(encoding="utf-8")

    assert rows
    assert rows[0]["rule_id"]
    assert rows[0]["evidence_claim_ids"]
    assert "Needs-edit Worklist" in worklist_text
    assert "suggested_action" in worklist_text
    assert "Rule Abstraction Checks" in quality_text
    assert "accepted recheck candidates: 1" in quality_text
