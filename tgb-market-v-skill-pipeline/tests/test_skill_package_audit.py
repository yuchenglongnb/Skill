import json

from tgb_pipeline.skill.package_audit import audit_skill_package, build_skill_package_audit_report
from tgb_pipeline.skill.package_builder import build_skill_package
from tgb_pipeline.skill.tasks import build_skill_v0_bundle
from tests.skill_fixture_data import write_skill_inputs


def test_audit_skill_package_passes_for_valid_dist(tmp_path) -> None:
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

    audit = audit_skill_package(dist_dir)
    report_path = build_skill_package_audit_report(audit, dist_dir / "PACKAGE_AUDIT.md")

    assert audit["warnings"] == 0
    assert report_path.is_file()
    checks = {check["check"]: check["status"] for check in audit["checks"]}
    assert checks["manifest_has_source_commit"] == "ok"
    assert checks["manifest_has_package_build_commit"] == "ok"
    assert checks["manifest_counts_match_current_package"] == "ok"
    assert checks["manifest_quality_matches_quality_report"] == "ok"


def test_audit_skill_package_detects_missing_skill_and_advice_language(tmp_path) -> None:
    dist_dir = tmp_path / "dist" / "tgb_market_v_skill"
    dist_dir.mkdir(parents=True, exist_ok=True)
    (dist_dir / "README.md").write_text("# package\n", encoding="utf-8")
    (dist_dir / "MANIFEST.json").write_text(json.dumps({"quality": {}}), encoding="utf-8")
    (dist_dir / "methodology_rules.jsonl").write_text("", encoding="utf-8")
    (dist_dir / "rule_evidence_map.jsonl").write_text("", encoding="utf-8")
    (dist_dir / "uncertainty_policy.md").write_text("# policy\n", encoding="utf-8")
    (dist_dir / "review_summary.md").write_text("# Review Summary\n", encoding="utf-8")
    (dist_dir / "skill_quality_report.md").write_text("# Skill Quality Report\n", encoding="utf-8")
    (dist_dir / "SKILL.md").write_text("推荐买入\n", encoding="utf-8")

    audit = audit_skill_package(dist_dir)

    failed = {check["check"] for check in audit["checks"] if check["status"] != "ok"}
    assert "investment_advice_language" in failed
    assert audit["warnings"] > 0


def test_audit_skill_package_detects_mojibake(tmp_path) -> None:
    dist_dir = tmp_path / "dist" / "tgb_market_v_skill"
    dist_dir.mkdir(parents=True, exist_ok=True)
    (dist_dir / "SKILL.md").write_text("蜷蜷乱码\n", encoding="utf-8")
    (dist_dir / "README.md").write_text("# package\n", encoding="utf-8")
    (dist_dir / "MANIFEST.json").write_text(json.dumps({"quality": {}}), encoding="utf-8")
    (dist_dir / "methodology_rules.jsonl").write_text("", encoding="utf-8")
    (dist_dir / "rule_evidence_map.jsonl").write_text("", encoding="utf-8")
    (dist_dir / "uncertainty_policy.md").write_text("# policy\n", encoding="utf-8")
    (dist_dir / "review_summary.md").write_text("# Review Summary\n", encoding="utf-8")
    (dist_dir / "skill_quality_report.md").write_text("# Skill Quality Report\n", encoding="utf-8")

    audit = audit_skill_package(dist_dir)

    failed = {check["check"] for check in audit["checks"] if check["status"] != "ok"}
    assert "encoding" in failed
