from tgb_pipeline.audit.article_inventory_audit import build_article_inventory_report
from tgb_pipeline.models import CommentArticleState, CrawlError
from tgb_pipeline.storage import JSONLStore
from tests.export_fixture_data import build_sample_corpus


def test_build_article_inventory_report_counts_coverage_and_errors(tmp_path) -> None:
    raw_dir, _processed_dir, reports_dir = build_sample_corpus(tmp_path)
    JSONLStore(raw_dir / "article_crawl_errors.jsonl", CrawlError, "error_id").append(
        CrawlError(
            error_id="article-error-1",
            stage="crawl_articles.fetch_article",
            article_id="a1",
            url="https://m.tgb.cn/a/1Vgsye6eK36",
            error_type="RuntimeError",
            error_message="boom",
        )
    )
    JSONLStore(raw_dir / "comment_crawl_errors.jsonl", CrawlError, "error_id").append(
        CrawlError(
            error_id="comment-error-1",
            stage="crawl_comments.page",
            article_id="a1",
            url="https://m.tgb.cn/a/1Vgsye6eK36-2?type=",
            error_type="RuntimeError",
            error_message="boom",
            raw={"page_num": 2},
        )
    )
    JSONLStore(
        raw_dir / "comment_article_states.jsonl",
        CommentArticleState,
        "article_id",
    ).append(
        CommentArticleState(
            article_id="a1",
            max_fetched_page=100,
            next_page_to_fetch=101,
            discovered_last_page=749,
            max_limit_reached=True,
        )
    )

    report = build_article_inventory_report(raw_dir, reports_dir / "article_inventory_report.md")

    assert report["indexed_articles"] == 1
    assert report["crawled_articles"] == 1
    assert report["articles_with_comments"] == 1
    assert report["article_crawl_errors"] == 1
    assert report["comment_crawl_errors"] == 1
    assert report["per_article"][0]["next_page_to_fetch"] == 101
    assert report["per_article"][0]["max_limit_reached"] is True
    content = (reports_dir / "article_inventory_report.md").read_text(encoding="utf-8")
    assert "# Article Inventory Report" in content
    assert "| a1 |" in content
