"""Extract candidate article links from offline text and HTML sources."""

from __future__ import annotations

import re
from datetime import date
from urllib.parse import urljoin

from bs4 import BeautifulSoup

DATE_PATTERNS = (
    re.compile(r"(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})"),
    re.compile(r"(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})"),
    re.compile(r"(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})"),
    re.compile(r"(?P<year>\d{4})年(?P<month>\d{1,2})月(?P<day>\d{1,2})日"),
)
ARTICLE_URL_PATTERN = re.compile(
    r"(?P<url>"
    r"https?://(?:www|m)\.tgb\.cn/(?:a/[A-Za-z0-9]+(?:-\d+\?type=)?|Article/\d+/1)"
    r"|/(?:a/[A-Za-z0-9]+(?:-\d+\?type=)?|Article/\d+/1)"
    r")"
)


def extract_article_links_from_text(
    text: str,
    *,
    base_url: str = "https://www.tgb.cn",
) -> list[dict]:
    candidates: list[dict] = []
    seen: set[str] = set()
    lines = text.splitlines()
    for match in ARTICLE_URL_PATTERN.finditer(text):
        url = urljoin(base_url, match.group("url"))
        if url in seen:
            continue
        seen.add(url)
        context = _line_context(text, lines, match.start())
        title = _extract_title_from_text_line(context, match.group("url"))
        candidates.append(
            {
                "url": url,
                "title": title,
                "published_date": _extract_date(context),
                "raw_context": context,
            }
        )
    return candidates


def extract_article_links_from_html(
    html: str,
    *,
    page_url: str | None = None,
) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    candidates: list[dict] = []
    seen: set[str] = set()
    base_url = page_url or "https://www.tgb.cn"
    for anchor in soup.find_all("a", href=True):
        href = str(anchor.get("href", ""))
        match = ARTICLE_URL_PATTERN.search(href)
        if not match:
            continue
        url = urljoin(base_url, match.group("url"))
        if url in seen:
            continue
        seen.add(url)
        container = anchor.find_parent(["tr", "li", "div", "p"]) or anchor.parent
        context = container.get_text(" ", strip=True) if container else anchor.get_text(" ", strip=True)
        candidates.append(
            {
                "url": url,
                "title": _clean_title(anchor.get_text(" ", strip=True)) or _extract_title_from_context(context),
                "published_date": _extract_date(context),
                "raw_context": context,
                "anchor_html": str(anchor),
            }
        )
    return candidates


def _extract_date(value: str) -> date | None:
    for pattern in DATE_PATTERNS:
        match = pattern.search(value)
        if match:
            return date(
                int(match.group("year")),
                int(match.group("month")),
                int(match.group("day")),
            )
    return None


def _extract_title_from_context(context: str) -> str | None:
    cleaned = _clean_title(context)
    if not cleaned:
        return None
    first_line = cleaned.splitlines()[0].strip()
    return first_line[:120] if first_line else None


def _extract_title_from_text_line(context: str, matched_url: str) -> str | None:
    cleaned = context.replace(matched_url, " ")
    for pattern in DATE_PATTERNS:
        cleaned = pattern.sub(" ", cleaned)
    title = _clean_title(cleaned)
    return title if title and len(title) > 3 else None


def _clean_title(value: str) -> str | None:
    stripped = " ".join(value.split())
    return stripped or None


def _line_context(text: str, lines: list[str], start: int) -> str:
    line_start = 0
    for line in lines:
        line_end = line_start + len(line) + 1
        if line_start <= start <= line_end:
            return line.strip()
        line_start = line_end
    return text[max(0, start - 80): start + 80]
