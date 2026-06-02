from tgb_pipeline.discovery.extract_links import (
    extract_article_links_from_html,
    extract_article_links_from_text,
)


def test_extract_article_links_from_text_supports_multiple_patterns() -> None:
    text = """
    2023-01-15 https://www.tgb.cn/a/1Vgsye6eK36
    20230124 https://m.tgb.cn/a/1Vgsye6eK36-31?type=
    2023/02/01 /Article/4588439/1
    2023年2月5日 /a/ABCD123
    """

    records = extract_article_links_from_text(text)

    assert len(records) == 4
    assert records[0]["published_date"].isoformat() == "2023-01-15"
    assert records[1]["published_date"].isoformat() == "2023-01-24"
    assert records[2]["published_date"].isoformat() == "2023-02-01"
    assert records[3]["published_date"].isoformat() == "2023-02-05"


def test_extract_article_links_from_html_uses_anchor_text_as_title() -> None:
    html = """
    <html><body>
      <tr>
        <td><a href="/a/1Vgsye6eK36">情绪周期是否可靠的思考</a></td>
        <td>2023-01-15</td>
      </tr>
      <tr>
        <td><a href="/next">下一页</a></td>
      </tr>
    </body></html>
    """

    records = extract_article_links_from_html(html, page_url="https://www.tgb.cn/blog/123")

    assert len(records) == 1
    assert records[0]["title"] == "情绪周期是否可靠的思考"
    assert records[0]["url"] == "https://www.tgb.cn/a/1Vgsye6eK36"
    assert records[0]["published_date"].isoformat() == "2023-01-15"
