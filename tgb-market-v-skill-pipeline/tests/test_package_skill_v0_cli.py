from tgb_pipeline.cli import main
from tests.skill_fixture_data import write_minimal_configs, write_skill_inputs


def test_package_skill_v0_cli_generates_dist_outputs(tmp_path, monkeypatch) -> None:
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
            "--include-needs-edit-worklist",
            "--rule-mode",
            "--strict-rule-abstraction",
            "--generate-accepted-recheck-pack",
        ]
    ) == 0

    assert main(
        [
            "package-skill-v0",
            "--target-config",
            str(target_path),
            "--crawl-config",
            str(crawl_path),
        ]
    ) == 0

    dist_dir = tmp_path / "dist" / "tgb_market_v_skill"
    assert (dist_dir / "SKILL.md").is_file()
    assert (dist_dir / "README.md").is_file()
    assert (dist_dir / "MANIFEST.json").is_file()
    assert (dist_dir / "PACKAGE_AUDIT.md").is_file()
    assert (dist_dir / "methodology_rules.jsonl").is_file()
    assert (dist_dir / "rule_evidence_map.jsonl").is_file()

