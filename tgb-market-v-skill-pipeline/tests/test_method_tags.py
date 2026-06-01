from tgb_pipeline.extraction.tags import detect_method_tags


def test_detect_method_tags_returns_stable_deduped_tags() -> None:
    text = "情绪周期切换要结合成交额和市场结构，量化会强化赚钱效应。"
    tags = detect_method_tags(text)

    assert tags[:4] == ["情绪周期", "成交额", "量化影响", "市场结构"]
    assert "赚钱效应" in tags

