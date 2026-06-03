from tgb_pipeline.extraction.quality import evaluate_claim_candidate


def test_claim_quality_filters_analogy_background() -> None:
    decision = evaluate_claim_candidate(
        text="春夏秋冬本来就是自然规律。",
        source_type="article",
        method_tags=[],
        tickers=[],
        sectors=[],
        concepts=[],
    )

    assert decision.keep is False
    assert decision.reason == "analogy_background"


def test_claim_quality_filters_emotional_noise() -> None:
    decision = evaluate_claim_candidate(
        text="今天太难了，服了。",
        source_type="comment",
        method_tags=[],
        tickers=[],
        sectors=[],
        concepts=[],
    )

    assert decision.keep is False
    assert decision.reason == "emotional_noise"


def test_claim_quality_filters_pure_question() -> None:
    decision = evaluate_claim_candidate(
        text="明天怎么看？",
        source_type="comment",
        method_tags=[],
        tickers=[],
        sectors=[],
        concepts=[],
    )

    assert decision.keep is False
    assert decision.reason == "pure_question"


def test_claim_quality_filters_generic_market_statement() -> None:
    decision = evaluate_claim_candidate(
        text="市场就是这样。",
        source_type="comment",
        method_tags=[],
        tickers=[],
        sectors=[],
        concepts=[],
    )

    assert decision.keep is False
    assert decision.reason == "generic_market_statement"


def test_claim_quality_keeps_strong_methodology_statement() -> None:
    decision = evaluate_claim_candidate(
        text="情绪周期不是失效，而是成交额和量化改变了反馈速度。",
        source_type="comment",
        method_tags=["情绪周期", "成交额", "量化影响"],
        tickers=[],
        sectors=[],
        concepts=["情绪周期"],
    )

    assert decision.keep is True
    assert decision.reason == "strong_methodology_statement"


def test_claim_quality_keeps_conditional_trading_statement() -> None:
    decision = evaluate_claim_candidate(
        text="如果指数环境太差，短线基础行情会压制个股高度。",
        source_type="comment",
        method_tags=["指数环境", "短线基础行情"],
        tickers=[],
        sectors=[],
        concepts=[],
    )

    assert decision.keep is True
    assert decision.reason == "strong_methodology_statement"


def test_claim_quality_keeps_buy_trigger_statement() -> None:
    decision = evaluate_claim_candidate(
        text="买入触发不是看感觉，而是看标准是否满足。",
        source_type="comment",
        method_tags=["买入触发"],
        tickers=[],
        sectors=[],
        concepts=[],
    )

    assert decision.keep is True
    assert decision.reason == "strong_methodology_statement"


def test_claim_quality_keeps_risk_statement() -> None:
    decision = evaluate_claim_candidate(
        text="弱市风控比进攻更重要。",
        source_type="comment",
        method_tags=["风控"],
        tickers=[],
        sectors=[],
        concepts=[],
    )

    assert decision.keep is True
    assert decision.reason == "strong_methodology_statement"


def test_claim_quality_keeps_bull_bear_statement() -> None:
    decision = evaluate_claim_candidate(
        text="牛市和熊市的短线基础行情不同。",
        source_type="comment",
        method_tags=["牛熊切换", "短线基础行情"],
        tickers=[],
        sectors=[],
        concepts=[],
    )

    assert decision.keep is True
    assert decision.reason == "strong_methodology_statement"
