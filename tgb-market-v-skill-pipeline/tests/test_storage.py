from datetime import UTC, datetime

from tgb_pipeline.models import Article
from tgb_pipeline.storage import JSONLStore


def make_article(article_id: str, title: str = "标题") -> Article:
    return Article(
        article_id=article_id,
        title=title,
        author_name="等主人的猫",
        published_at=datetime(2023, 1, 15, tzinfo=UTC),
        url=f"https://example.test/{article_id}",
        raw_content="原始正文",
    )


def test_store_writes_utf8_and_deduplicates(tmp_path) -> None:
    store = JSONLStore(tmp_path / "articles.jsonl", Article, "article_id")

    assert store.append_many([make_article("a-1"), make_article("a-1")]) == 1
    assert store.append(make_article("a-2")) is True
    assert store.append(make_article("a-2")) is False

    records = store.read_all()
    assert [record.article_id for record in records] == ["a-1", "a-2"]
    assert "等主人的猫" in (tmp_path / "articles.jsonl").read_text(encoding="utf-8")


def test_store_indexes_records_by_field(tmp_path) -> None:
    store = JSONLStore(tmp_path / "articles.jsonl", Article, "article_id")
    store.append_many([make_article("a-1", "同题"), make_article("a-2", "同题")])

    index = store.index_by("title")
    assert [record.article_id for record in index["同题"]] == ["a-1", "a-2"]

