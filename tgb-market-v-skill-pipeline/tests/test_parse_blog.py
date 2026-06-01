from datetime import date
from pathlib import Path

from tgb_pipeline.crawler.parse_blog import (
    filter_articles,
    find_next_page_url,
    parse_blog_index,
)

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_blog_index_extracts_article_metadata() -> None:
    html = (FIXTURES / "blog_index_sample.html").read_text(encoding="utf-8")
    records = parse_blog_index(html, "https://www.tgb.cn/blog/123")

    start = next(record for record in records if record.article_id == "4588439")
    assert start.title == "情绪周期是否可靠的思考"
    assert start.tag == "原"
    assert start.published_date == date(2023, 1, 15)
    assert start.view_count == 8961
    assert start.reply_count == 301
    assert start.url == "https://www.tgb.cn/Article/4588439/1"
    assert start.mobile_url == "https://m.tgb.cn/Article/4588439/1"
    assert records[0].view_count == 12000
    assert find_next_page_url(html, "https://www.tgb.cn/blog/123") == (
        "https://www.tgb.cn/blog/123?page=2"
    )


def test_filter_articles_keeps_start_and_removes_older_records() -> None:
    html = (FIXTURES / "blog_index_sample.html").read_text(encoding="utf-8")
    records = parse_blog_index(html, "https://www.tgb.cn/blog/123")

    filtered = filter_articles(
        records,
        start_date=date(2023, 1, 15),
        start_title="情绪周期是否可靠的思考",
    )

    assert [record.article_id for record in filtered] == ["5000001", "4588439"]

