"""Lightweight entity and intent extraction for methodology claims."""

from __future__ import annotations

import re
from collections import OrderedDict

TICKER_RE = re.compile(r"(?<!\d)((?:6\d{5}|0\d{5}|3\d{5}|688\d{3})(?:\.(?:SH|SZ))?)(?!\d)", re.IGNORECASE)
IMAGE_PLACEHOLDER_RE = re.compile(r"\[IMAGE:\s*[^\]]+\]", re.IGNORECASE)
SECTOR_KEYWORDS = (
    "券商",
    "机器人",
    "AI",
    "人工智能",
    "半导体",
    "新能源",
    "光伏",
    "军工",
    "地产",
    "中特估",
    "医药",
    "消费",
    "算力",
    "传媒",
    "汽车",
    "量化",
    "小票",
    "大票",
    "指数",
    "沪指",
    "创业板",
    "北交所",
)
CONCEPT_KEYWORDS = (
    "情绪周期",
    "成交额",
    "风控",
    "仓位",
    "主线",
    "赚钱效应",
    "亏钱效应",
    "反核",
    "龙头",
    "量化",
    "AI",
    "机器人",
)


def extract_tickers(text: str) -> list[str]:
    sanitized = IMAGE_PLACEHOLDER_RE.sub(" ", text)
    seen: OrderedDict[str, None] = OrderedDict()
    for match in TICKER_RE.findall(sanitized):
        seen[match.upper()] = None
    return list(seen.keys())


def extract_sectors_or_concepts(text: str) -> tuple[list[str], list[str]]:
    sectors = _ordered_keyword_matches(text, SECTOR_KEYWORDS)
    concepts = _ordered_keyword_matches(text, CONCEPT_KEYWORDS)
    return sectors, concepts


def infer_direction(text: str) -> str | None:
    lowered = text.casefold()
    bullish = ("看多", "走强", "向上", "乐观", "修复", "反弹", "做多")
    bearish = ("看空", "走弱", "向下", "悲观", "退潮", "下跌", "风险")
    if any(token in lowered for token in bullish) and not any(token in lowered for token in bearish):
        return "bullish"
    if any(token in lowered for token in bearish) and not any(token in lowered for token in bullish):
        return "bearish"
    if "震荡" in text or "中性" in text:
        return "neutral"
    return None


def infer_horizon(text: str) -> str | None:
    lowered = text.casefold()
    if any(token in lowered for token in ("日内", "分时", "盘中", "当日")):
        return "intraday"
    if any(token in lowered for token in ("短线", "明天", "明日", "次日", "这两天")):
        return "short_term"
    if any(token in lowered for token in ("波段", "一周", "几天", "中期")):
        return "medium_term"
    if any(token in lowered for token in ("长线", "季度", "半年", "长期")):
        return "long_term"
    return None


def _ordered_keyword_matches(text: str, keywords: tuple[str, ...]) -> list[str]:
    matches: OrderedDict[str, None] = OrderedDict()
    lowered = text.casefold()
    for keyword in keywords:
        if keyword.casefold() in lowered:
            matches[keyword] = None
    return list(matches.keys())
