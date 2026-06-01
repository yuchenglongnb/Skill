"""Rule-based methodology tag detection."""

from __future__ import annotations

from collections import OrderedDict

TAG_KEYWORDS: list[tuple[str, tuple[str, ...]]] = [
    ("情绪周期", ("情绪周期", "情绪", "周期")),
    ("成交额", ("成交额", "成交量", "量能", "缩量", "放量")),
    ("指数环境", ("指数", "沪指", "创业板", "北交所")),
    ("短线基础行情", ("短线", "连板", "首板", "接力")),
    ("量化影响", ("量化", "机器单", "程序化")),
    ("市场结构", ("市场结构", "结构", "高低切", "风格切换")),
    ("赚钱效应", ("赚钱效应", "赚钱", "溢价")),
    ("亏钱效应", ("亏钱效应", "亏钱", "核按钮")),
    ("龙头", ("龙头", "总龙", "核心标的")),
    ("反核", ("反核", "翘板", "核按钮")),
    ("题材持续性", ("题材持续性", "持续性", "主线")),
    ("仓位管理", ("仓位", "满仓", "轻仓", "半仓")),
    ("风控", ("风控", "止损", "回撤", "风险控制")),
    ("买入触发", ("买入", "上车", "低吸", "半路")),
    ("卖出条件", ("卖出", "止盈", "兑现", "离场")),
    ("牛熊切换", ("牛熊", "牛市", "熊市")),
    ("政策催化", ("政策", "催化", "监管")),
    ("AI工具", ("AI工具", "ai", "人工智能工具")),
    ("机器人", ("机器人", "机械臂", "自动化设备")),
    ("数字化/标准化", ("数字化", "标准化", "流程化")),
]


def detect_method_tags(text: str) -> list[str]:
    lowered = text.casefold()
    matches: OrderedDict[str, None] = OrderedDict()
    for tag, keywords in TAG_KEYWORDS:
        if any(keyword.casefold() in lowered for keyword in keywords):
            matches[tag] = None
    return list(matches.keys())

