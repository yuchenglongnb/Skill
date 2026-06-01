from datetime import date

from tgb_pipeline.config import TargetConfig
from tgb_pipeline.crawler.seed import (
    build_seed_article_index,
    extract_article_id_from_url,
)


def make_target_config(url: str) -> TargetConfig:
    return TargetConfig.parse_obj(
        {
            "target": {
                "platform": "taoguba",
                "author_name": "等主人的猫",
                "blog_url": "https://www.tgb.cn/blog/123",
                "start_article": {
                    "title": "情绪周期是否可靠的思考",
                    "published_date": date(2023, 1, 15),
                    "url": url,
                },
            }
        }
    )


def test_extract_article_id_from_supported_urls() -> None:
    assert extract_article_id_from_url("https://www.tgb.cn/a/1Vgsye6eK36") == "1Vgsye6eK36"
    assert extract_article_id_from_url("https://m.tgb.cn/a/1Vgsye6eK36") == "1Vgsye6eK36"
    assert extract_article_id_from_url("/Article/4588439/1") == "4588439"
    assert extract_article_id_from_url("https://www.tgb.cn/Article/4588439/1") == "4588439"


def test_build_seed_article_index_uses_mobile_url_and_raw_flags() -> None:
    target = make_target_config("https://www.tgb.cn/a/1Vgsye6eK36")

    seed = build_seed_article_index(target)

    assert seed.article_id == "1Vgsye6eK36"
    assert seed.title == "情绪周期是否可靠的思考"
    assert seed.published_date.isoformat() == "2023-01-15"
    assert seed.url == "https://www.tgb.cn/a/1Vgsye6eK36"
    assert seed.mobile_url == "https://m.tgb.cn/a/1Vgsye6eK36"
    assert seed.tag is None
    assert seed.view_count == 0
    assert seed.reply_count == 0
    assert seed.raw["source"] == "target_config.start_article.url"
    assert seed.raw["seed_fallback"] is True
