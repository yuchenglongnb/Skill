import json

from tgb_pipeline.export.manifest import build_corpus_manifest
from tgb_pipeline.export.export_markdown import export_all_corpora
from tgb_pipeline.models import ArticleSeedCandidate
from tgb_pipeline.storage import JSONLStore
from tests.export_fixture_data import build_sample_corpus


def test_build_corpus_manifest_uses_relative_paths_and_counts(tmp_path, monkeypatch) -> None:
    raw_dir, processed_dir, reports_dir = build_sample_corpus(tmp_path)
    export_all_corpora(raw_dir, processed_dir)
    interim_dir = tmp_path / "data" / "interim" / "tgb"
    JSONLStore(
        interim_dir / "article_seed_candidates.jsonl",
        ArticleSeedCandidate,
        "candidate_id",
    ).append(
        ArticleSeedCandidate(
            candidate_id="candidate-a1",
            article_id="a1",
            title="Start article",
            url="https://www.tgb.cn/a/1Vgsye6eK36",
            mobile_url="https://m.tgb.cn/a/1Vgsye6eK36",
            source="seed_yaml",
            selected=True,
        )
    )
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "article_seed_candidates.md").write_text("# candidates\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    manifest_path = build_corpus_manifest(raw_dir, processed_dir, reports_dir)
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert payload["counts"]["article_index"] == 1
    assert payload["counts"]["article_seed_candidates"] == 1
    assert payload["counts"]["article_seed_candidates_report"] == 1
    assert payload["counts"]["article_seeds_config_count"] >= 0
    assert payload["counts"]["comments_all"] == 3
    assert payload["counts"]["images"] == 3
    assert payload["counts"]["article_crawl_errors"] == 0
    assert payload["counts"]["comment_crawl_errors"] == 0
    assert payload["counts"]["comment_state_warnings"] in {0, 1}
    assert payload["counts"]["images_downloaded"] == 0
    assert payload["counts"]["image_ocr"] == 0
    assert payload["counts"]["methodology_claims"] == 0
    assert payload["counts"]["review_ready_claims"] == 0
    assert payload["counts"]["low_priority_methodology_claims"] == 0
    assert payload["counts"]["review_ready_decisions"] == 0
    assert payload["counts"]["accepted_review_ready_claims"] == 0
    assert payload["counts"]["rejected_review_ready_claims"] == 0
    assert payload["counts"]["needs_edit_review_ready_claims"] == 0
    assert payload["counts"]["review_packs_count"] == 0
    assert payload["counts"]["review_pack_reports_count"] == 0
    assert payload["counts"]["review_pack_index"] == 0
    assert payload["counts"]["skill_v0_count"] == 0
    assert payload["counts"]["skill_v0_methodology_rules"] == 0
    assert payload["counts"]["skill_v0_rule_evidence_map"] == 0
    assert payload["counts"]["skill_v0_needs_edit_worklist"] == 0
    assert payload["counts"]["skill_v0_skill_quality_report"] == 0
    assert payload["counts"]["accepted_methodology_claims"] == 0
    assert payload["has_aoch"] is False
    assert payload["skill_v0_dir"] is None
    assert payload["skill_v0_skill_md"] is None
    assert payload["skill_v0_methodology_profile"] is None
    assert payload["skill_v0_evidence_index"] is None
    assert payload["skill_v0_methodology_rules"] is None
    assert payload["skill_v0_rule_evidence_map"] is None
    assert payload["skill_v0_needs_edit_worklist"] is None
    assert payload["skill_v0_skill_quality_report"] is None
    assert payload["skill_v0_uncertainty_policy"] is None
    assert payload["skill_v0_review_summary"] is None
    assert all(not path.startswith("C:/") for path in payload["outputs"])
    assert any(path.endswith("reports/article_inventory_report.md") for path in payload["reports"])
    assert any(path.endswith("reports/comment_state_warnings.md") for path in payload["reports"])
    assert payload["image_ocr_path"].endswith("data/processed/tgb/image_ocr.jsonl")
    assert payload["methodology_claims_path"].endswith("data/processed/tgb/methodology_claims.jsonl")
    assert payload["claim_review_decisions_path"].endswith("data/processed/tgb/claim_review_decisions.yaml")
