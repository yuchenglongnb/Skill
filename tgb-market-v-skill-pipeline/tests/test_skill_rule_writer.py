import json

from tgb_pipeline.skill.rule_builder import build_methodology_rules
from tgb_pipeline.skill.rule_writer import write_methodology_rules, write_needs_edit_worklist
from tests.skill_fixture_data import make_claim


def test_rule_writer_outputs_rules_and_needs_edit_worklist(tmp_path) -> None:
    accepted = [
        make_claim("claim-1", "量化会改变短线反馈速度。", tag="量化影响"),
        make_claim("claim-2", "弱市先收缩仓位。", tag="风控"),
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
    rules = build_methodology_rules(accepted, max_rules_per_theme=2)

    rules_path = write_methodology_rules(rules, tmp_path)
    worklist_path = write_needs_edit_worklist(needs_edit, tmp_path)

    rows = [json.loads(line) for line in rules_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    worklist_text = worklist_path.read_text(encoding="utf-8")

    assert rows
    assert rows[0]["rule_id"]
    assert rows[0]["evidence_claim_ids"]
    assert "Needs-edit Worklist" in worklist_text
    assert "suggested_action" in worklist_text
