from pathlib import Path

from tgb_pipeline.cli import main
from tgb_pipeline.models import ArticleSeedCandidate
from tgb_pipeline.storage import JSONLStore


def _write_target_config(tmp_path: Path) -> Path:
    target_path = tmp_path / "target.yaml"
    target_path.write_text(
        """
target:
  platform: taoguba
  author_name: Target Author
  start_article:
    title: Start article
    published_date: "2023-01-15"
    url: https://www.tgb.cn/a/1Vgsye6eK36
""",
        encoding="utf-8",
    )
    return target_path


def test_discovery_and_promote_cli_run(tmp_path: Path, monkeypatch) -> None:
    manual_links = tmp_path / "manual_article_links.txt"
    manual_links.write_text(
        "2023-01-15 情绪周期是否可靠的思考 https://www.tgb.cn/a/1Vgsye6eK36\n"
        "2023-02-01 后续文章 https://www.tgb.cn/Article/5000001/1\n",
        encoding="utf-8",
    )
    discovery_path = tmp_path / "article_discovery.yaml"
    discovery_path.write_text(
        f"""
version: 1
start_date: "2023-01-15"
sources:
  - name: manual_notes
    type: text_file
    path: {manual_links.as_posix()}
""",
        encoding="utf-8",
    )
    target_path = _write_target_config(tmp_path)
    candidates_path = tmp_path / "article_seed_candidates.jsonl"
    seeds_path = tmp_path / "article_seeds.yaml"
    monkeypatch.chdir(tmp_path)

    assert main(
        [
            "discover-article-seeds",
            "--target-config",
            str(target_path),
            "--discovery-config",
            str(discovery_path),
            "--output",
            str(candidates_path),
        ]
    ) == 0
    candidates = JSONLStore(
        candidates_path,
        ArticleSeedCandidate,
        "candidate_id",
    ).read_all()
    assert len(candidates) == 2

    for candidate in candidates:
        if candidate.article_id == "5000001":
            candidate.selected = True
    JSONLStore(candidates_path, ArticleSeedCandidate, "candidate_id").rewrite_all(candidates)

    assert main(
        [
            "promote-article-seeds",
            "--candidates",
            str(candidates_path),
            "--article-seeds",
            str(seeds_path),
            "--only-selected",
        ]
    ) == 0
    assert "5000001" in seeds_path.read_text(encoding="utf-8")
