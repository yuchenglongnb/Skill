import json

from tgb_pipeline.skill.package_builder import build_skill_package
from tgb_pipeline.skill.tasks import build_skill_v0_bundle
from tests.skill_fixture_data import write_skill_inputs


def test_build_skill_package_copies_release_files_and_manifest(tmp_path) -> None:
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
    outputs = build_skill_package(source_dir, dist_dir, include_needs_edit=True)

    assert (dist_dir / "SKILL.md").is_file()
    assert (dist_dir / "README.md").is_file()
    assert (dist_dir / "MANIFEST.json").is_file()
    assert (dist_dir / "methodology_rules.jsonl").is_file()
    assert (dist_dir / "rule_evidence_map.jsonl").is_file()
    assert (dist_dir / "uncertainty_policy.md").is_file()
    assert (dist_dir / "review_summary.md").is_file()
    assert (dist_dir / "skill_quality_report.md").is_file()
    assert (dist_dir / "evidence_index.jsonl").is_file()
    assert (dist_dir / "needs_edit_evidence_index.jsonl").is_file()
    assert (dist_dir / "needs_edit_worklist.md").is_file()
    assert any(path.name == "MANIFEST.json" for path in outputs)

    payload = json.loads((dist_dir / "MANIFEST.json").read_text(encoding="utf-8"))
    assert payload["package_name"] == "tgb_market_v_skill"
    assert payload["rules_count"] > 0
    assert payload["accepted_claims"] > 0
    assert "review_ready_decisions.yaml" not in payload["files"]
    assert not any("raw" in entry for entry in payload["files"])

