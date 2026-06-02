from datetime import date
from pathlib import Path

from tgb_pipeline.discovery.tasks import promote_candidates_to_article_seeds
from tgb_pipeline.models import ArticleSeedCandidate
from tgb_pipeline.storage import JSONLStore


def test_promote_candidates_only_promotes_selected_without_duplicates(tmp_path: Path) -> None:
    candidates_path = tmp_path / "article_seed_candidates.jsonl"
    JSONLStore(candidates_path, ArticleSeedCandidate, "candidate_id").append_many(
        [
            ArticleSeedCandidate(
                candidate_id="candidate-a1",
                article_id="a1",
                title="Start article",
                published_date=date(2023, 1, 15),
                url="https://www.tgb.cn/a/a1",
                mobile_url="https://m.tgb.cn/a/a1",
                confidence="high",
                selected=True,
            ),
            ArticleSeedCandidate(
                candidate_id="candidate-a2",
                article_id="a2",
                title="Later article",
                published_date=date(2023, 1, 20),
                url="https://www.tgb.cn/a/a2",
                mobile_url="https://m.tgb.cn/a/a2",
                confidence="medium",
                selected=False,
            ),
        ]
    )
    seeds_path = tmp_path / "article_seeds.yaml"
    seeds_path.write_text(
        """
version: 1
source: manual_article_seed_list
description: existing
articles:
  - title: Start article
    published_date: "2023-01-15"
    url: https://www.tgb.cn/a/a1
    tag: null
    note: keep
""",
        encoding="utf-8",
    )

    added_count, total_count = promote_candidates_to_article_seeds(
        candidates_path,
        seeds_path,
        only_selected=True,
        dry_run=False,
    )

    assert added_count == 0
    assert total_count == 1
    assert "keep" in seeds_path.read_text(encoding="utf-8")


def test_promote_candidates_respects_min_confidence_in_dry_run(tmp_path: Path) -> None:
    candidates_path = tmp_path / "article_seed_candidates.jsonl"
    JSONLStore(candidates_path, ArticleSeedCandidate, "candidate_id").append(
        ArticleSeedCandidate(
            candidate_id="candidate-a2",
            article_id="a2",
            title="Later article",
            published_date=date(2023, 1, 20),
            url="https://www.tgb.cn/a/a2",
            mobile_url="https://m.tgb.cn/a/a2",
            confidence="medium",
            selected=False,
        )
    )
    seeds_path = tmp_path / "article_seeds.yaml"

    added_count, total_count = promote_candidates_to_article_seeds(
        candidates_path,
        seeds_path,
        only_selected=False,
        min_confidence="medium",
        dry_run=True,
    )

    assert added_count == 1
    assert total_count == 1
    assert not seeds_path.exists()
