from tgb_pipeline.export.export_markdown import (
    export_all_corpora,
    export_aoch_corpus,
    export_interaction_pairs,
    export_target_author_corpus,
)
from tests.export_fixture_data import build_sample_corpus


def test_markdown_exports_separate_target_and_member_content(tmp_path) -> None:
    raw_dir, processed_dir, _ = build_sample_corpus(tmp_path)

    target_path = export_target_author_corpus(raw_dir, processed_dir)
    interaction_path = export_interaction_pairs(raw_dir, processed_dir)
    aoch_path = export_aoch_corpus(raw_dir, processed_dir)

    target_text = target_path.read_text(encoding="utf-8")
    interaction_text = interaction_path.read_text(encoding="utf-8")
    aoch_text = aoch_path.read_text(encoding="utf-8")
    assert "Target Author Corpus" in target_text
    assert "普通成员乙:" not in target_text
    assert "等主人的猫:" in interaction_text
    assert "普通成员乙:" in interaction_text
    assert "No Aoch comments were found" in aoch_text
    assert len(export_all_corpora(raw_dir, processed_dir)) == 3

