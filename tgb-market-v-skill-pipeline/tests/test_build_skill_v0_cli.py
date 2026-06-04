from tgb_pipeline.cli import main
from tests.skill_fixture_data import write_minimal_configs, write_skill_inputs


def test_build_skill_v0_cli_generates_outputs(tmp_path, monkeypatch) -> None:
    raw_dir, processed_dir, reports_dir = write_skill_inputs(tmp_path)
    target_path, crawl_path = write_minimal_configs(tmp_path)
    monkeypatch.chdir(tmp_path)

    assert main(
        [
            "build-skill-v0",
            "--target-config",
            str(target_path),
            "--crawl-config",
            str(crawl_path),
            "--include-needs-edit-index",
        ]
    ) == 0

    output_dir = tmp_path / "skill_output" / "tgb_market_v_skill"
    assert (output_dir / "SKILL.md").is_file()
    assert (output_dir / "methodology_profile.md").is_file()
    assert (output_dir / "evidence_index.jsonl").is_file()
    assert (output_dir / "needs_edit_evidence_index.jsonl").is_file()
    assert (output_dir / "uncertainty_policy.md").is_file()
    assert (output_dir / "review_summary.md").is_file()
