from pathlib import Path

from tgb_pipeline.crawler.parse_comments import (
    build_comment_page_url,
    find_comment_last_page_num,
    find_comment_next_page_url,
    parse_comments_page,
)

FIXTURES = Path(__file__).parent / "fixtures"


def test_build_comment_page_url_supports_seed_mobile_urls() -> None:
    assert build_comment_page_url("https://m.tgb.cn/a/1Vgsye6eK36", 1) == "https://m.tgb.cn/a/1Vgsye6eK36"
    assert build_comment_page_url("https://m.tgb.cn/a/1Vgsye6eK36", 2) == "https://m.tgb.cn/a/1Vgsye6eK36-2?type="


def test_find_comment_pagination_links() -> None:
    html = (FIXTURES / "comment_page_sample.html").read_text(encoding="utf-8")

    assert find_comment_next_page_url(html, "https://m.tgb.cn/a/1Vgsye6eK36") == "https://m.tgb.cn/a/1Vgsye6eK36-2?type="
    assert find_comment_last_page_num(html, "https://m.tgb.cn/a/1Vgsye6eK36") == 31


def test_parse_comments_page_extracts_comments_and_images() -> None:
    html = (FIXTURES / "comment_page_sample.html").read_text(encoding="utf-8")

    comments, images = parse_comments_page(
        html,
        article_id="1Vgsye6eK36",
        article_title="情绪周期是否可靠的思考",
        page_url="https://m.tgb.cn/a/1Vgsye6eK36",
        page_num=1,
        target_author="等主人的猫",
    )

    assert len(comments) == 5
    assert comments[0].comment_id == "comment-1001"
    assert comments[1].author_name == "普通成员乙"
    assert comments[1].page_num == 1
    assert comments[1].page_position == 2
    assert "[IMAGE: image-" in comments[4].content_text
    assert "图片 alt 文本" not in comments[4].content_text
    assert len(images) == 1
    assert images[0].source_type == "comment"
    assert images[0].comment_id == "comment-1005"
    assert images[0].before_text == "图片前文字"
    assert "图片后文字" in (images[0].after_text or "")

