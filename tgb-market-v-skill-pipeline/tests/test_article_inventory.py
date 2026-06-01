from datetime import date

from tgb_pipeline.crawler.article_inventory import merge_article_indexes
from tgb_pipeline.models import ArticleIndex


def test_merge_article_indexes_deduplicates_and_keeps_more_complete_counts() -> None:
    public_record = ArticleIndex(
        article_id="4588439",
        title="Start article",
        published_date=date(2023, 1, 15),
        view_count=123,
        reply_count=45,
        url="https://www.tgb.cn/Article/4588439/1",
        mobile_url="https://m.tgb.cn/Article/4588439/1",
        raw={"source": "public_index"},
    )
    manual_seed = ArticleIndex(
        article_id="4588439",
        title="Start article",
        published_date=date(2023, 1, 15),
        tag="methodology",
        view_count=0,
        reply_count=0,
        url="https://www.tgb.cn/a/1Vgsye6eK36",
        mobile_url="https://m.tgb.cn/a/1Vgsye6eK36",
        raw={"source": "configs/article_seeds.yaml", "manual_seed": True},
    )
    later_article = ArticleIndex(
        article_id="5000001",
        title="Later article",
        published_date=date(2023, 2, 1),
        view_count=10,
        reply_count=1,
        url="https://www.tgb.cn/Article/5000001/1",
        mobile_url="https://m.tgb.cn/Article/5000001/1",
        raw={"source": "public_index"},
    )

    merged = merge_article_indexes([later_article], [public_record, manual_seed, manual_seed])

    assert [record.article_id for record in merged] == ["4588439", "5000001"]
    assert merged[0].view_count == 123
    assert merged[0].reply_count == 45
    assert merged[0].tag == "methodology"
    assert set(merged[0].raw["sources"]) == {"public_index", "configs/article_seeds.yaml"}
