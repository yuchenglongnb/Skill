from bs4 import BeautifulSoup

from tgb_pipeline.crawler.extract_images import extract_article_images


def test_extract_article_images_captures_context_and_replaces_placeholder() -> None:
    soup = BeautifulSoup(
        """
        <div class="article-content">
          <p>图片前的一段话。</p>
          <p><img src="/images/context.png" alt="图片说明"></p>
          <p>图片后的一段话。</p>
        </div>
        """,
        "lxml",
    )
    container = soup.select_one(".article-content")
    assert container is not None

    images = extract_article_images(
        container,
        article_id="article-1",
        page_url="https://m.tgb.cn/Article/1/1",
    )

    assert len(images) == 1
    image = images[0]
    assert image.source_type == "article_body"
    assert image.position_index == 1
    assert image.before_text == "图片前的一段话。"
    assert image.after_text == "图片后的一段话。"
    assert image.keep_reason == "target_author_article_image"
    assert image.review_status == "unreviewed"
    assert image.raw["attributes"]["alt"] == "图片说明"
    assert "[IMAGE: image-" in container.get_text("\n", strip=True)

