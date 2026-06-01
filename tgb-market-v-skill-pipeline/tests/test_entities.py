from tgb_pipeline.extraction.entities import (
    extract_sectors_or_concepts,
    extract_tickers,
    infer_direction,
    infer_horizon,
)


def test_extract_entities_and_infer_intent() -> None:
    text = "300750 和 600000 今天更强，机器人、AI、指数共振，短线偏看多。"

    tickers = extract_tickers(text)
    sectors, concepts = extract_sectors_or_concepts(text)

    assert tickers == ["300750", "600000"]
    assert "机器人" in sectors
    assert "AI" in sectors
    assert "指数" in sectors
    assert infer_direction(text) == "bullish"
    assert infer_horizon(text) == "short_term"

