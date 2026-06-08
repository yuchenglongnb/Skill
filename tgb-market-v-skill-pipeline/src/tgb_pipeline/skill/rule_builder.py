"""Deterministic rule builder for Skill v0.2."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from tgb_pipeline.models import MethodologyClaim, MethodologyRule

THEME_ORDER = [
    "量化影响",
    "成交额 / 量能",
    "短线基础行情",
    "指数环境",
    "风控",
    "牛熊切换",
]

THEME_TAG_MAP = {
    "量化影响": {"量化影响"},
    "成交额 / 量能": {"成交额"},
    "短线基础行情": {"短线基础行情"},
    "指数环境": {"指数环境"},
    "风控": {"风控"},
    "牛熊切换": {"牛熊切换"},
}


@dataclass(frozen=True)
class RuleBlueprint:
    rule_id: str
    title: str
    rule_text: str
    when_to_use: list[str]
    do_not_use_when: list[str]
    caveats: list[str]
    keywords: tuple[str, ...] = field(default_factory=tuple)
    review_buckets: tuple[str, ...] = field(default_factory=tuple)


THEME_RULE_BLUEPRINTS: dict[str, list[RuleBlueprint]] = {
    "量化影响": [
        RuleBlueprint(
            rule_id="quant-impact-market-structure",
            title="量化影响需要纳入短线市场结构判断",
            rule_text=(
                "量化交易会改变短线生态中的资金反馈速度、流动性分布和追涨/抛压结构；"
                "分析短线机会时，需要把量化带来的趋同交易、规避策略和盘中反馈纳入市场结构判断。"
            ),
            when_to_use=["当作者讨论量化冲击、盘中反馈或短线生态变化时。"],
            do_not_use_when=["只有个股复盘细节、没有市场结构含义时。"],
            caveats=["不要把量化影响简化成单一利多或利空。"],
            keywords=("量化", "生态", "结构", "反馈", "流动性", "追涨", "抛压"),
            review_buckets=("trading_mechanism", "market_environment"),
        ),
        RuleBlueprint(
            rule_id="quant-impact-not-single-direction",
            title="不要把量化影响简化为单一利多或利空",
            rule_text=(
                "量化影响更像市场结构变量，而不是固定方向结论；"
                "同样的量化参与，在不同成交额、指数环境和短线基础行情下会放大不同结果。"
            ),
            when_to_use=["当作者用量化解释市场强弱、承接或异动时。"],
            do_not_use_when=["只有情绪表达、没有环境约束或结构含义时。"],
            caveats=["需要结合指数环境、成交额和短线基础行情共同判断。"],
            keywords=("量化", "单一", "利多", "利空", "环境", "变量"),
            review_buckets=("core_methodology", "market_environment"),
        ),
        RuleBlueprint(
            rule_id="quant-impact-intraday-liquidity",
            title="量化会影响盘中流动性与反馈节奏",
            rule_text=(
                "量化会改变盘中流动性分布和反馈节奏，进而影响追涨、回落、回封和承接的时间结构；"
                "短线分析不能只看结果，还要看盘中反馈如何被量化重塑。"
            ),
            when_to_use=["当作者讨论盘中承接、追涨抛压、回封或反馈速度时。"],
            do_not_use_when=["只有静态行情判断、没有盘中反馈信息时。"],
            caveats=["更适合作为结构判断，不直接导出具体买卖指令。"],
            keywords=("盘中", "反馈", "承接", "回封", "抛压", "追涨", "流动性"),
            review_buckets=("trading_mechanism",),
        ),
    ],
    "成交额 / 量能": [
        RuleBlueprint(
            rule_id="turnover-short-term-height",
            title="成交额约束短线高度与持续性",
            rule_text=(
                "短线高度、接力持续性和赚钱效应受整体成交额与活跃度约束；"
                "当成交额不足时，局部强势未必能外推为更高高度或更长持续性。"
            ),
            when_to_use=["当作者讨论成交额、接力高度、持续性和赚钱效应时。"],
            do_not_use_when=["只有单只个股强弱、没有整体活跃度背景时。"],
            caveats=["成交额是环境变量，不是单独买卖结论。"],
            keywords=("成交额", "量能", "高度", "持续性", "活跃度", "接力"),
            review_buckets=("market_environment", "trading_mechanism"),
        ),
        RuleBlueprint(
            rule_id="turnover-with-index-context",
            title="放量和缩量必须结合指数环境与资金稀缺性判断",
            rule_text=(
                "放量、缩量本身没有固定方向含义，必须结合指数环境、资金稀缺性和短线基础行情一起判断；"
                "同样的量能变化，在不同市场状态下对应的交易难度并不相同。"
            ),
            when_to_use=["当作者讨论放量、缩量、活跃度变化和环境切换时。"],
            do_not_use_when=["只有量能描述、没有指数环境或资金背景时。"],
            caveats=["量能变化需要和市场状态配套解读。"],
            keywords=("放量", "缩量", "资金", "稀缺", "活跃度", "环境"),
            review_buckets=("market_environment",),
        ),
        RuleBlueprint(
            rule_id="turnover-not-standalone-signal",
            title="量能变化是环境变量，不是单独买卖结论",
            rule_text=(
                "成交额和量能更适合作为短线环境约束，而不是直接导出进攻或防守结论；"
                "分析时要把量能放回指数、短线基础行情和风险偏好框架里。"
            ),
            when_to_use=["当作者讨论量能能否支撑交易节奏时。"],
            do_not_use_when=["只有情绪化判断、没有环境变量之间的关系时。"],
            caveats=["不要把放量或缩量机械当作操作信号。"],
            keywords=("量能", "环境变量", "结论", "框架", "支撑"),
            review_buckets=("core_methodology", "execution_rule"),
        ),
    ],
    "短线基础行情": [
        RuleBlueprint(
            rule_id="short-term-base-before-local-opportunity",
            title="先判断短线整体环境，再判断局部机会",
            rule_text=(
                "短线机会不能只看单只个股局部强弱，必须先判断整体赚钱效应、接力环境、轮动速度和容错空间；"
                "局部机会是否成立，取决于短线基础行情是否支持。"
            ),
            when_to_use=["当作者讨论连板、首板、接力和短线容错时。"],
            do_not_use_when=["只有个股点评、没有整体短线生态含义时。"],
            caveats=["局部龙头强势不等于整体短线环境健康。"],
            keywords=("短线", "赚钱效应", "接力", "容错", "轮动", "首板", "连板"),
            review_buckets=("core_methodology", "trading_mechanism"),
        ),
        RuleBlueprint(
            rule_id="short-term-base-not-single-stock",
            title="赚钱效应应看短线整体，而不是单个龙头或局部强势",
            rule_text=(
                "短线赚钱效应应从整体接力质量、承接分布和亏钱效应扩散看，"
                "而不是把单个龙头或局部强势误判为整体环境转好。"
            ),
            when_to_use=["当作者讨论龙头、赚钱效应、亏钱效应或局部强势时。"],
            do_not_use_when=["只有局部情绪评价、没有整体短线生态判断时。"],
            caveats=["龙头表现只能作为局部样本，不能替代整体环境判断。"],
            keywords=("赚钱效应", "亏钱效应", "龙头", "整体", "局部", "接力"),
            review_buckets=("market_environment", "risk_control"),
        ),
        RuleBlueprint(
            rule_id="short-term-base-difficulty",
            title="轮动速度、接力容错和指数成交额背景共同决定短线难度",
            rule_text=(
                "短线难度由轮动速度、接力容错、指数环境和成交额背景共同决定；"
                "环境越差，越不能把局部强势误当成短线全面回暖。"
            ),
            when_to_use=["当作者讨论轮动速度、接力难度、承接或环境压制时。"],
            do_not_use_when=["只有单点行情描述、没有环境变量之间的关系时。"],
            caveats=["要和指数环境、成交额约束一起阅读。"],
            keywords=("轮动", "容错", "难度", "承接", "回暖", "环境"),
            review_buckets=("market_environment", "core_methodology"),
        ),
    ],
    "指数环境": [
        RuleBlueprint(
            rule_id="index-environment-risk-appetite",
            title="指数环境影响短线承接与风险偏好",
            rule_text=(
                "指数环境会改变短线承接、风险偏好和仓位容忍度；"
                "指数震荡、走弱或风险升高时，短线局部强势的可持续性要打折看待。"
            ),
            when_to_use=["当作者讨论指数、风险偏好、承接和短线容错时。"],
            do_not_use_when=["只有单日涨跌陈述、没有承接或风险偏好含义时。"],
            caveats=["指数环境影响的是容错与承接，不应被机械当成唯一方向信号。"],
            keywords=("指数", "承接", "风险偏好", "震荡", "走弱", "容错"),
            review_buckets=("market_environment",),
        ),
        RuleBlueprint(
            rule_id="index-environment-lower-certainty",
            title="指数震荡或下行风险会降低局部题材确定性",
            rule_text=(
                "指数震荡或下行风险抬升时，局部题材和个股的确定性会下降；"
                "即使存在热点，也要降低对持续性和高度的预期。"
            ),
            when_to_use=["当作者讨论热点持续性、局部题材或大盘压制时。"],
            do_not_use_when=["只有个股复盘、没有指数背景约束时。"],
            caveats=["局部题材强势需要放回大盘环境中重新评估。"],
            keywords=("指数", "震荡", "下行", "题材", "确定性", "持续性"),
            review_buckets=("market_environment", "risk_control"),
        ),
        RuleBlueprint(
            rule_id="index-environment-layered-judgment",
            title="指数、板块、个股需要分层判断",
            rule_text=(
                "指数、板块和个股是不同层级的判断对象；"
                "分析时应先分清环境层、板块层和个股层，再决定哪些结论可以外推。"
            ),
            when_to_use=["当作者讨论大盘、板块、个股之间的关系时。"],
            do_not_use_when=["只有情绪化环境判断、没有层级区分时。"],
            caveats=["不要用单层级强弱替代全部层级判断。"],
            keywords=("板块", "个股", "分层", "层级", "环境", "外推"),
            review_buckets=("core_methodology",),
        ),
    ],
    "风控": [
        RuleBlueprint(
            rule_id="risk-control-reduce-exposure",
            title="环境不支持进攻时优先收缩风险暴露",
            rule_text=(
                "当指数、成交额、短线基础行情或亏钱效应不支持进攻时，应优先收缩风险暴露、减少交易频率或降低仓位；"
                "而不是继续套用强环境下的节奏。"
            ),
            when_to_use=["当作者讨论弱市、回撤、亏钱效应、减仓或等待时。"],
            do_not_use_when=["只有口号式风控提醒、没有环境依据时。"],
            caveats=["风控优先于进攻意愿。"],
            keywords=("风控", "仓位", "减仓", "减少交易", "等待", "回撤", "亏钱效应"),
            review_buckets=("risk_control", "execution_rule"),
        ),
        RuleBlueprint(
            rule_id="risk-control-missing-entry-premise",
            title="买入前提不成立时应减少交易或等待",
            rule_text=(
                "当买入前提、承接条件或流动性条件不成立时，应减少交易、延后出手或直接等待；"
                "而不是强行把弱环境里的反弹解释为可持续机会。"
            ),
            when_to_use=["当作者讨论买入前提、承接不足、流动性恶化或等待时。"],
            do_not_use_when=["只有模糊的情绪宣泄、没有可识别前提条件时。"],
            caveats=["这是一条执行约束，不是具体买卖建议。"],
            keywords=("买入前提", "承接", "流动性", "等待", "不做", "少做"),
            review_buckets=("execution_rule", "risk_control"),
        ),
        RuleBlueprint(
            rule_id="risk-control-weak-market-priority",
            title="亏钱效应、流动性不足和弱市环境下风控优先",
            rule_text=(
                "当亏钱效应扩散、流动性不足或弱市环境强化时，风控应优先于进攻；"
                "短线策略要先处理风险预算，再考虑机会筛选。"
            ),
            when_to_use=["当作者讨论弱市、防守、亏钱效应或仓位管理时。"],
            do_not_use_when=["只有个股层面的抱怨、没有环境层的风险判断时。"],
            caveats=["需要结合指数环境和成交额共同确认。"],
            keywords=("弱市", "防守", "亏钱效应", "流动性", "仓位", "风险预算"),
            review_buckets=("risk_control", "market_environment"),
        ),
    ],
    "牛熊切换": [
        RuleBlueprint(
            rule_id="bull-bear-no-single-rhythm",
            title="牛市、熊市和切换期不能沿用同一套短线节奏",
            rule_text=(
                "牛市、熊市和切换期的短线基础行情不同，不能简单沿用同一套短线节奏；"
                "进攻强度、容错预期和风险预算都要随环境调整。"
            ),
            when_to_use=["当作者讨论牛市、熊市、切换期和短线节奏时。"],
            do_not_use_when=["只有泛泛的牛熊评论、没有策略差异判断时。"],
            caveats=["牛熊切换要和成交额、指数环境、赚钱效应一起看。"],
            keywords=("牛市", "熊市", "切换", "节奏", "策略", "容错"),
            review_buckets=("market_environment", "core_methodology"),
        ),
        RuleBlueprint(
            rule_id="bull-bear-combined-signals",
            title="牛熊判断必须结合成交额、指数环境和赚钱/亏钱效应",
            rule_text=(
                "牛熊判断不是单一标签，而是成交额、指数环境、赚钱效应和亏钱效应共同作用的结果；"
                "环境切换时，要重新确认哪些变量在主导市场。"
            ),
            when_to_use=["当作者讨论市场状态识别、牛熊判断或环境变化时。"],
            do_not_use_when=["只有情绪化牛熊表述、没有变量支撑时。"],
            caveats=["不要把牛熊判断当作单一、瞬时信号。"],
            keywords=("牛市", "熊市", "赚钱效应", "亏钱效应", "状态", "环境"),
            review_buckets=("market_environment", "risk_control"),
        ),
        RuleBlueprint(
            rule_id="bull-bear-attack-defense-weight",
            title="市场状态切换会改变进攻与防守权重",
            rule_text=(
                "市场状态切换会改变进攻与防守的权重分配；"
                "环境越偏弱，越应把防守和节奏控制放在进攻冲动之前。"
            ),
            when_to_use=["当作者讨论进攻、防守、仓位节奏和状态切换时。"],
            do_not_use_when=["只有单次交易感受、没有环境权重变化判断时。"],
            caveats=["更适合作为权重调整规则，而非单次操作指令。"],
            keywords=("进攻", "防守", "权重", "切换", "状态", "仓位"),
            review_buckets=("risk_control", "execution_rule"),
        ),
    ],
}


def build_methodology_rules(
    accepted_claims: list[MethodologyClaim],
    *,
    max_rules_per_theme: int = 4,
    min_evidence_per_rule: int = 2,
    max_evidence_per_rule: int = 5,
) -> list[MethodologyRule]:
    grouped = group_claims_by_theme(accepted_claims)
    rules: list[MethodologyRule] = []
    for theme in THEME_ORDER:
        theme_claims = grouped.get(theme, [])
        if not theme_claims:
            continue
        bucketed_claims = _bucket_claims_for_theme(theme_claims, theme)
        theme_rules_before = len(rules)
        for blueprint in THEME_RULE_BLUEPRINTS[theme][:max_rules_per_theme]:
            evidence = select_representative_claims(
                bucketed_claims.get(blueprint.rule_id, []),
                max_evidence_per_rule,
            )
            if len(evidence) < min_evidence_per_rule:
                continue
            rules.append(_build_rule_from_blueprint(theme, blueprint, evidence))
        if len(rules) == theme_rules_before and len(theme_claims) >= min_evidence_per_rule:
            fallback_blueprint = THEME_RULE_BLUEPRINTS[theme][0]
            fallback_evidence = select_representative_claims(theme_claims, max_evidence_per_rule)
            rules.append(_build_rule_from_blueprint(theme, fallback_blueprint, fallback_evidence))
    return rules


def assign_claim_to_rule_bucket(claim: MethodologyClaim, theme: str) -> str:
    text = _claim_search_text(claim)
    review_bucket = (claim.review_bucket or "").lower()

    if theme == "量化影响":
        if _contains_any(text, "盘中", "反馈", "承接", "回封", "抛压", "追涨", "流动性"):
            return "quant-impact-intraday-liquidity"
        if _contains_any(text, "单一", "利多", "利空", "不能简单", "不是固定"):
            return "quant-impact-not-single-direction"
        return "quant-impact-market-structure"

    if theme == "成交额 / 量能":
        if _contains_any(text, "放量", "缩量", "资金", "稀缺", "环境切换"):
            return "turnover-with-index-context"
        if _contains_any(text, "环境变量", "不是单独", "不能直接", "框架"):
            return "turnover-not-standalone-signal"
        return "turnover-short-term-height"

    if theme == "短线基础行情":
        if _contains_any(text, "赚钱效应", "亏钱效应", "龙头", "局部", "整体"):
            return "short-term-base-not-single-stock"
        if _contains_any(text, "轮动", "容错", "难度", "回暖", "节奏"):
            return "short-term-base-difficulty"
        return "short-term-base-before-local-opportunity"

    if theme == "指数环境":
        if _contains_any(text, "板块", "个股", "分层", "层级", "外推"):
            return "index-environment-layered-judgment"
        if _contains_any(text, "题材", "确定性", "持续性", "震荡", "下行"):
            return "index-environment-lower-certainty"
        return "index-environment-risk-appetite"

    if theme == "风控":
        if _contains_any(text, "买入前提", "不做", "少做", "等待", "延后", "前提") or review_bucket == "execution_rule":
            return "risk-control-missing-entry-premise"
        if _contains_any(text, "弱市", "防守", "流动性", "风险预算") or review_bucket == "market_environment":
            return "risk-control-weak-market-priority"
        return "risk-control-reduce-exposure"

    if theme == "牛熊切换":
        if _contains_any(text, "进攻", "防守", "权重", "仓位") or review_bucket == "execution_rule":
            return "bull-bear-attack-defense-weight"
        if _contains_any(text, "赚钱效应", "亏钱效应", "成交额", "指数", "状态识别"):
            return "bull-bear-combined-signals"
        return "bull-bear-no-single-rhythm"

    return THEME_RULE_BLUEPRINTS[theme][0].rule_id


def primary_theme(claim: MethodologyClaim) -> str | None:
    for theme in THEME_ORDER:
        if THEME_TAG_MAP[theme].intersection(claim.method_tags):
            return theme
    return None


def group_claims_by_theme(claims: list[MethodologyClaim]) -> dict[str, list[MethodologyClaim]]:
    grouped: dict[str, list[MethodologyClaim]] = defaultdict(list)
    for claim in claims:
        matched = False
        for theme in THEME_ORDER:
            if THEME_TAG_MAP[theme].intersection(claim.method_tags):
                grouped[theme].append(claim)
                matched = True
        if not matched:
            theme = primary_theme(claim)
            if theme is not None:
                grouped[theme].append(claim)
    return grouped


def select_representative_claims(claims: list[MethodologyClaim], max_items: int) -> list[MethodologyClaim]:
    source_priority = {"article": 0, "comment": 1, "interaction": 2, "image_ocr": 3}

    def ranking_score(claim: MethodologyClaim) -> int:
        ranking = (claim.raw or {}).get("ranking") or {}
        return int(ranking.get("score", 0))

    return sorted(
        claims,
        key=lambda claim: (
            source_priority.get(claim.source_type.value, 9),
            -ranking_score(claim),
            claim.claim_id,
        ),
    )[:max_items]


def theme_key(theme: str) -> str:
    return {
        "量化影响": "quant-impact",
        "成交额 / 量能": "turnover",
        "短线基础行情": "short-term-base",
        "指数环境": "index-environment",
        "风控": "risk-control",
        "牛熊切换": "bull-bear",
    }[theme]


def _bucket_claims_for_theme(claims: list[MethodologyClaim], theme: str) -> dict[str, list[MethodologyClaim]]:
    bucketed: dict[str, list[MethodologyClaim]] = defaultdict(list)
    for claim in select_representative_claims(claims, max(50, len(claims))):
        bucketed[assign_claim_to_rule_bucket(claim, theme)].append(claim)
    return bucketed


def _claim_search_text(claim: MethodologyClaim) -> str:
    parts = [
        claim.claim_text,
        claim.raw_excerpt,
        claim.review_notes or "",
        claim.review_bucket or "",
        " ".join(claim.method_tags),
    ]
    return " ".join(part.strip() for part in parts if part).lower()


def _contains_any(text: str, *keywords: str) -> bool:
    return any(keyword and keyword in text for keyword in keywords)


def _build_rule_from_blueprint(
    theme: str,
    blueprint: RuleBlueprint,
    evidence: list[MethodologyClaim],
) -> MethodologyRule:
    return MethodologyRule(
        rule_id=blueprint.rule_id,
        theme=theme,
        title=blueprint.title,
        rule_text=blueprint.rule_text,
        when_to_use=blueprint.when_to_use,
        do_not_use_when=blueprint.do_not_use_when,
        evidence_claim_ids=[claim.claim_id for claim in evidence],
        evidence_article_ids=_unique_article_ids(evidence),
        confidence="reviewed_v0_2",
        caveats=list(blueprint.caveats),
        source_tags=sorted({tag for claim in evidence for tag in claim.method_tags}),
        raw={
            "rule_kind": "theme_abstract",
            "theme": theme,
            "evidence_count": len(evidence),
            "bucket": blueprint.rule_id,
        },
    )


def _unique_article_ids(claims: list[MethodologyClaim]) -> list[str]:
    seen: set[str] = set()
    article_ids: list[str] = []
    for claim in claims:
        if not claim.article_id or claim.article_id in seen:
            continue
        seen.add(claim.article_id)
        article_ids.append(claim.article_id)
    return article_ids
