"""Normalize discovered article URLs into stable seed candidates."""

from __future__ import annotations

from datetime import date
from urllib.parse import urljoin, urlsplit

from tgb_pipeline.crawler.parse_blog import to_mobile_url
from tgb_pipeline.crawler.seed import extract_article_id_from_url
from tgb_pipeline.models import ArticleSeedCandidate


def normalize_article_url(url: str) -> tuple[str, str, str]:
    absolute_url = _absolute_url(url)
    if "/a/" in absolute_url and "-" in absolute_url.rsplit("/", 1)[-1]:
        absolute_url, _normalized_from_comment_page = _strip_comment_page_suffix(absolute_url)
    article_id = extract_article_id_from_url(absolute_url)
    canonical_url = _canonical_url(article_id, absolute_url)
    mobile_url = to_mobile_url(canonical_url)
    return article_id, canonical_url, mobile_url


def build_article_seed_candidate(raw: dict, source_name: str) -> ArticleSeedCandidate:
    article_id, url, mobile_url = normalize_article_url(str(raw["url"]))
    extracted_date = raw.get("published_date")
    if extracted_date is not None and not isinstance(extracted_date, date):
        raise TypeError("published_date must be a date when provided")
    title = _none_if_blank(raw.get("title"))
    confidence = _confidence_for(title=title, published_date=extracted_date)
    normalized_from_comment_page = _is_comment_page_url(str(raw["url"]))
    candidate_sources = list(dict.fromkeys([source_name, *raw.get("sources", [])]))
    return ArticleSeedCandidate(
        candidate_id=f"candidate-{article_id}",
        article_id=article_id,
        title=title,
        published_date=extracted_date,
        url=url,
        mobile_url=mobile_url,
        tag=_none_if_blank(raw.get("tag")),
        source=source_name,
        confidence=confidence,
        selected=bool(raw.get("selected", False)),
        note=_none_if_blank(raw.get("note")),
        raw={
            "original_url": raw.get("url"),
            "source_name": source_name,
            "sources": candidate_sources,
            "extracted_title": title,
            "extracted_date": extracted_date.isoformat() if extracted_date else None,
            "normalized_from_comment_page": normalized_from_comment_page,
            **{key: value for key, value in raw.items() if key not in {"url", "title", "published_date", "tag", "note", "selected", "sources"}},
        },
    )


def _confidence_for(*, title: str | None, published_date: date | None) -> str:
    if title and published_date:
        return "high"
    if title or published_date:
        return "medium"
    return "candidate"


def _absolute_url(url: str) -> str:
    if urlsplit(url).scheme:
        return url
    return urljoin("https://www.tgb.cn", url)


def _strip_comment_page_suffix(url: str) -> tuple[str, bool]:
    split = urlsplit(url)
    if "/a/" not in split.path:
        return url, False
    prefix, suffix = split.path.rsplit("/", 1)
    if "-" not in suffix:
        return url, False
    article_hash = suffix.split("-", 1)[0]
    if article_hash == suffix:
        return url, False
    normalized = split._replace(path=f"{prefix}/{article_hash}", query="", fragment="")
    return normalized.geturl(), True


def _canonical_url(article_id: str, original_url: str) -> str:
    split = urlsplit(original_url)
    if "/Article/" in split.path:
        return f"https://www.tgb.cn/Article/{article_id}/1"
    return f"https://www.tgb.cn/a/{article_id}"


def _none_if_blank(value: object) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def _is_comment_page_url(url: str) -> bool:
    split = urlsplit(_absolute_url(url))
    return "/a/" in split.path and "-" in split.path.rsplit("/", 1)[-1]
