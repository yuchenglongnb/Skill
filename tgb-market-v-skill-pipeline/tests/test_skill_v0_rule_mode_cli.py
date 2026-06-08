from tgb_pipeline.cli import main
from tests.skill_fixture_data import write_minimal_configs, write_skill_inputs


def test_build_skill_v0_rule_mode_cli_generates_rule_outputs(tmp_path, monkeypatch) -> None:
    write_skill_inputs(tmp_path)
    target_path, crawl_path = write_minimal_configs(tmp_path)
    monkeypatch.chdir(tmp_path)

    assert main(
        [
            "build-skill-v0",
            "--target-config",
            str(target_path),
            "--crawl-config",
            str(crawl_path),
            "--rule-mode",
            "--include-needs-edit-index",
            "--include-needs-edit-worklist",
            "--strict-rule-abstraction",
            "--generate-accepted-recheck-pack",
            "--max-rules-per-theme",
            "4",
            "--max-evidence-per-rule",
            "3",
        ]
    ) == 0

    output_dir = tmp_path / "skill_output" / "tgb_market_v_skill"
    assert (output_dir / "methodology_rules.jsonl").is_file()
    assert (output_dir / "rule_evidence_map.jsonl").is_file()
    assert (output_dir / "skill_quality_report.md").is_file()
    assert (output_dir / "needs_edit_worklist.md").is_file()
    assert (tmp_path / "data" / "processed" / "tgb" / "review_packs" / "accepted_recheck_v0_2.yaml").is_file()
