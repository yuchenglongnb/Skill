from datetime import date
from pathlib import Path

from tgb_pipeline.config import load_article_discovery_config, load_target_config
from tgb_pipeline.discovery.discover_articles import discover_article_candidates
from tgb_pipeline.models import ArticleIndex
from tgb_pipeline.storage import JSONLStore


def _write_target_config(tmp_path: Path) -> Path:
    path = tmp_path / "target.yaml"
    path.write_text(
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
    return path


def test_discover_article_candidates_merges_sources_and_filters_noise(tmp_path: Path, monkeypatch) -> None:
    manual_links = tmp_path / "manual_article_links.txt"
    manual_links.write_text(
        """
        2023-01-10 https://www.tgb.cn/a/tooEarly
        2023-01-15 https://www.tgb.cn/a/1Vgsye6eK36
        2023/02/01 https://www.tgb.cn/a/1Vgsye6eK36-2?type=
        2023年2月5日 https://www.tgb.cn/Article/5000001/1
        """,
        encoding="utf-8",
    )
    html_dir = tmp_path / "html"
    html_dir.mkdir()
    (html_dir / "blog_index_page_1.html").write_text(
        """
        <html><body>
          <tr><td><a href="/a/1Vgsye6eK36">情绪周期是否可靠的思考</a></td><td>2023-01-15</td></tr>
          <tr><td><a href="/a/5000001">下一页</a></td><td>2023-02-02</td></tr>
          <tr><td><a href="/Article/5000001/1">后续文章</a></td><td>2023-02-05</td></tr>
        </body></html>
        """,
        encoding="utf-8",
    )
    raw_index_path = tmp_path / "articles_index.jsonl"
    JSONLStore(raw_index_path, ArticleIndex, "article_id").append(
        ArticleIndex(
            article_id="5000001",
            title="后续文章",
            published_date=date(2023, 2, 5),
            url="https://www.tgb.cn/Article/5000001/1",
            mobile_url="https://m.tgb.cn/Article/5000001/1",
        )
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
  - name: saved_blog_html
    type: html_glob
    path: {html_dir.as_posix()}/blog_index_page_*.html
  - name: raw_index
    type: raw_jsonl_index
    path: {raw_index_path.as_posix()}
""",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    candidates = discover_article_candidates(
        load_article_discovery_config(discovery_path),
        load_target_config(_write_target_config(tmp_path)),
    )

    assert [candidate.article_id for candidate in candidates] == ["1Vgsye6eK36", "5000001"]
    assert candidates[0].confidence == "high"
    assert "saved_blog_html" in candidates[0].raw["sources"]
    assert candidates[1].title == "后续文章"
