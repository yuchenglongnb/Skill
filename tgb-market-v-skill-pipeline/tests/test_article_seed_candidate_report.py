from datetime import date

from tgb_pipeline.discovery.report import build_article_seed_candidate_report
from tgb_pipeline.models import ArticleSeedCandidate


def test_article_seed_candidate_report_includes_single_candidate_hint(tmp_path) -> None:
    candidate = ArticleSeedCandidate(
        candidate_id="candidate-1Vgsye6eK36",
        article_id="1Vgsye6eK36",
        title="情绪周期是否可靠的思考",
        published_date=date(2023, 1, 15),
        url="https://www.tgb.cn/a/1Vgsye6eK36",
        mobile_url="https://m.tgb.cn/a/1Vgsye6eK36",
        confidence="high",
        source="seed_yaml",
        selected=True,
    )

    report_path = build_article_seed_candidate_report([candidate], tmp_path)
    content = report_path.read_text(encoding="utf-8")

    assert "Only one article candidate found" in content
    assert "| True | high | 1Vgsye6eK36 | 2023-01-15 |" in content
