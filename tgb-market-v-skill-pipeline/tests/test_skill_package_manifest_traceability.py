import json

from tgb_pipeline.skill.package_audit import audit_skill_package
from tgb_pipeline.skill.package_builder import build_skill_package
from tgb_pipeline.skill.tasks import build_skill_v0_bundle
from tests.skill_fixture_data import write_skill_inputs


def test_package_manifest_contains_traceability_fields(tmp_path) -> None:
    raw_dir, processed_dir, reports_dir = write_skill_inputs(tmp_path)
    source_dir = tmp_path / "skill_output" / "tgb_market_v_skill"
    dist_dir = tmp_path / "dist" / "tgb_market_v_skill"

    build_skill_v0_bundle(
        raw_dir,
        processed_dir,
        reports_dir,
        output_dir=source_dir,
        include_needs_edit_index=True,
        include_needs_edit_worklist=True,
        rule_mode=True,
        strict_rule_abstraction=True,
        generate_accepted_recheck_pack=True,
    )
    build_skill_package(source_dir, dist_dir, include_needs_edit=True)

    payload = json.loads((dist_dir / "MANIFEST.json").read_text(encoding="utf-8"))
    assert "source_commit" in payload
    assert "package_build_commit" in payload
    assert "package_commit" in payload
    assert payload["package_commit"] is None
    assert payload["generated_from"]["skill_output_dir"] == "skill_output/tgb_market_v_skill"
    assert payload["generated_from"]["pipeline_repo"] == "tgb-market-v-skill-pipeline"
    review_state = payload["generated_from"]["review_state"]
    assert set(review_state) == {
        "accepted_claims",
        "needs_edit_claims",
        "rejected_claims",
        "unreviewed_claims",
    }


def test_package_audit_warns_when_traceability_fields_missing(tmp_path) -> None:
    dist_dir = tmp_path / "dist" / "tgb_market_v_skill"
    dist_dir.mkdir(parents=True, exist_ok=True)
    (dist_dir / "SKILL.md").write_text("# skill\n", encoding="utf-8")
    (dist_dir / "README.md").write_text("# package\n", encoding="utf-8")
    (dist_dir / "MANIFEST.json").write_text(
        json.dumps(
            {
                "accepted_claims": 1,
                "needs_edit_claims": 0,
                "rejected_claims": 0,
                "unreviewed_claims": 0,
                "rules_count": 1,
                "quality": {
                    "direct_excerpt_in_rule_text": 0,
                    "generic_rule_titles": 0,
                    "raw_excerpt_in_skill_md": 0,
                    "warnings": 0,
                },
            }
        ),
        encoding="utf-8",
    )
    (dist_dir / "methodology_rules.jsonl").write_text('{"rule_id":"r1"}\n', encoding="utf-8")
    (dist_dir / "rule_evidence_map.jsonl").write_text('{"rule_id":"r1","claim_id":"c1"}\n', encoding="utf-8")
    (dist_dir / "uncertainty_policy.md").write_text("# policy\n", encoding="utf-8")
    (dist_dir / "review_summary.md").write_text(
        "# Review Summary\n\n## Counts\n- accepted: 1\n- needs_edit: 0\n- rejected: 0\n- unreviewed: 0\n\n## Accepted By Tag\n- 量化影响: 1\n\n## Rule Count By Theme\n- 量化影响: 1\n",
        encoding="utf-8",
    )
    (dist_dir / "skill_quality_report.md").write_text(
        "# Skill Quality Report\n\n## Summary\n- generated_rules: 1\n\n## Rule Abstraction Checks\n- direct excerpt in rule_text: 0\n- generic rule titles: 0\n- raw excerpt in SKILL.md: 0\n\n## Warnings\n- none\n",
        encoding="utf-8",
    )

    audit = audit_skill_package(dist_dir)

    failed = {check["check"] for check in audit["checks"] if check["status"] != "ok"}
    assert "manifest_has_package_build_commit" in failed
    assert "manifest_has_generated_from" in failed
    assert "manifest_has_review_state" in failed

