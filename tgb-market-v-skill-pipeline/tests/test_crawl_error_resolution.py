from datetime import UTC, datetime

from tgb_pipeline.audit.crawl_error_audit import (
    build_crawl_error_report,
    mark_resolved_crawl_errors,
)
from tgb_pipeline.models import Article, CommentPageState, CrawlError
from tgb_pipeline.storage import JSONLStore


def test_mark_resolved_crawl_errors_and_build_report(tmp_path) -> None:
    raw_dir = tmp_path / "raw"
    JSONLStore(raw_dir / "articles.jsonl", Article, "article_id").append(
        Article(
            article_id="a1",
            title="Article",
            author_name="Target",
            published_at=datetime(2023, 1, 15, tzinfo=UTC),
            url="https://www.tgb.cn/a/a1",
            raw_content="body",
        )
    )
    JSONLStore(raw_dir / "comment_page_states.jsonl", CommentPageState, "state_id").append(
        CommentPageState(
            state_id="comment-page-a1-2",
            article_id="a1",
            page_num=2,
            page_url="https://m.tgb.cn/a/a1-2?type=",
        )
    )
    article_errors = JSONLStore(raw_dir / "article_crawl_errors.jsonl", CrawlError, "error_id")
    article_errors.append(
        CrawlError(
            error_id="article-error",
            stage="crawl_articles.fetch_article",
            article_id="a1",
            error_type="ConnectionError",
            error_message="failed",
        )
    )
    comment_errors = JSONLStore(raw_dir / "comment_crawl_errors.jsonl", CrawlError, "error_id")
    comment_errors.append_many(
        [
            CrawlError(
                error_id="comment-resolved",
                stage="crawl_comments.page",
                article_id="a1",
                error_type="ConnectionError",
                error_message="failed",
                raw={"page_num": 2},
            ),
            CrawlError(
                error_id="comment-active",
                stage="crawl_comments.page",
                article_id="a1",
                error_type="ConnectionError",
                error_message="still failed",
                raw={"page_num": 3},
            ),
        ]
    )

    assert mark_resolved_crawl_errors(raw_dir) == (1, 1)
    assert article_errors.read_all()[0].resolved is True
    assert [error.resolved for error in comment_errors.read_all()] == [True, False]

    report_path = build_crawl_error_report(raw_dir, tmp_path / "reports")
    content = report_path.read_text(encoding="utf-8")
    assert "article_errors_active: 0" in content
    assert "comment_errors_active: 1" in content
    assert "comment-active" in content
