from datetime import date
from pathlib import Path

from tgb_pipeline.crawler.parse_article import parse_article_page
from tgb_pipeline.models import ArticleIndex

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_article_extracts_text_and_first_class_images() -> None:
    html = (FIXTURES / "article_page_sample.html").read_text(encoding="utf-8")
    index = ArticleIndex(
        article_id="4588439",
        title="情绪周期是否可靠的思考",
        tag="原",
        published_date=date(2023, 1, 15),
        view_count=8961,
        reply_count=301,
        url="https://www.tgb.cn/Article/4588439/1",
        mobile_url="https://m.tgb.cn/Article/4588439/1",
    )

    article, images = parse_article_page(
        html,
        index_record=index,
        target_author="等主人的猫",
    )

    assert article.title == "情绪周期是否可靠的思考"
    assert article.author_name == "等主人的猫"
    assert "这是正文第一段。" in article.content_text
    assert "[IMAGE: image-" in article.content_text
    assert article.mobile_url == "https://m.tgb.cn/Article/4588439/1"
    assert article.tag == "原"
    assert article.view_count == 8961
    assert article.reply_count == 301
    assert article.image_asset_ids == [images[0].image_id]
    assert images[0].source_url == "https://m.tgb.cn/images/chart-cycle.png"
    assert images[0].article_id == "4588439"
    assert images[0].evidence_source is True
    assert images[0].source_type == "article_body"
    assert images[0].keep_reason == "target_author_article_image"
    assert images[0].review_status == "unreviewed"
    assert images[0].position_index == 1
    assert images[0].before_text == "这是正文第一段。"
    assert images[0].after_text == "图片之后仍然是普通正文。"


def test_article_text_does_not_include_image_ocr_or_alt_text() -> None:
    html = (FIXTURES / "article_page_sample.html").read_text(encoding="utf-8")
    index = ArticleIndex(
        article_id="4588439",
        title="情绪周期是否可靠的思考",
        published_date=date(2023, 1, 15),
        url="https://www.tgb.cn/Article/4588439/1",
        mobile_url="https://m.tgb.cn/Article/4588439/1",
    )

    article, images = parse_article_page(
        html,
        index_record=index,
        target_author="等主人的猫",
    )

    assert "OCR 不应进入正文" not in article.content_text
    assert "OCR 不应进入正文" in images[0].raw["attributes"]["alt"]
    assert "content_html" in article.raw
