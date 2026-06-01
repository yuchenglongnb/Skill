import json

from tgb_pipeline.export.manifest import build_corpus_manifest
from tgb_pipeline.export.export_markdown import export_all_corpora
from tests.export_fixture_data import build_sample_corpus


def test_build_corpus_manifest_uses_relative_paths_and_counts(tmp_path, monkeypatch) -> None:
    raw_dir, processed_dir, reports_dir = build_sample_corpus(tmp_path)
    export_all_corpora(raw_dir, processed_dir)
    monkeypatch.chdir(tmp_path)

    manifest_path = build_corpus_manifest(raw_dir, processed_dir, reports_dir)
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert payload["counts"]["comments_all"] == 3
    assert payload["counts"]["images"] == 3
    assert payload["counts"]["images_downloaded"] == 0
    assert payload["counts"]["image_ocr"] == 0
    assert payload["has_aoch"] is False
    assert all(not path.startswith("C:/") for path in payload["outputs"])
    assert payload["image_ocr_path"].endswith("data/processed/tgb/image_ocr.jsonl")
