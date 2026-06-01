"""Manifest for derived corpus exports and reports."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from tgb_pipeline.models import Article, Comment, ImageAsset, ImageOCR, Interaction
from tgb_pipeline.storage import JSONLStore


def build_corpus_manifest(raw_dir: Path, processed_dir: Path, reports_dir: Path) -> Path:
    downloaded_images = _read_optional(raw_dir / "images_downloaded.jsonl", ImageAsset, "image_id")
    counts = {
        "articles": len(_read_optional(raw_dir / "articles.jsonl", Article, "article_id")),
        "comments_all": len(_read_optional(raw_dir / "comments_all.jsonl", Comment, "comment_id")),
        "comments": len(_read_optional(raw_dir / "comments.jsonl", Comment, "comment_id")),
        "interactions": len(_read_optional(raw_dir / "interactions.jsonl", Interaction, "interaction_id")),
        "images": len(_read_optional(raw_dir / "images.jsonl", ImageAsset, "image_id")),
        "aoch_discussions": len(_read_optional(raw_dir / "aoch_discussions.jsonl", Comment, "comment_id")),
        "images_downloaded": len(downloaded_images),
        "image_ocr": len(_read_optional(processed_dir / "image_ocr.jsonl", ImageOCR, "ocr_id")),
        "image_ocr_review_queue": 1 if (reports_dir / "image_ocr_review_queue.md").exists() else 0,
    }
    manifest = {
        "generated_at": datetime.now(UTC).isoformat(),
        "inputs": [
            _relative(raw_dir / "articles_index.jsonl"),
            _relative(raw_dir / "articles.jsonl"),
            _relative(raw_dir / "comments_all.jsonl"),
            _relative(raw_dir / "comments.jsonl"),
            _relative(raw_dir / "interactions.jsonl"),
            _relative(raw_dir / "images.jsonl"),
        ],
        "outputs": [
            _relative(processed_dir / "target_author_corpus.md"),
            _relative(processed_dir / "interaction_pairs.md"),
            _relative(processed_dir / "aoch_corpus.md"),
            _relative(processed_dir / "image_ocr.jsonl"),
        ],
        "reports": [
            _relative(reports_dir / "comment_coverage_report.md"),
            _relative(reports_dir / "author_inventory.md"),
            _relative(reports_dir / "image_inventory_report.md"),
            _relative(reports_dir / "image_review_candidates.md"),
            _relative(reports_dir / "filter_quality_report.md"),
            _relative(reports_dir / "image_ocr_review_queue.md"),
        ],
        "counts": counts,
        "has_aoch": counts["aoch_discussions"] > 0,
        "downloaded_images_path": _relative(raw_dir / "images_downloaded.jsonl"),
        "image_ocr_path": _relative(processed_dir / "image_ocr.jsonl"),
    }
    output_path = processed_dir / "corpus_manifest.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output_path


def _relative(path: Path) -> str:
    resolved = path.resolve()
    cwd = Path.cwd().resolve()
    try:
        return resolved.relative_to(cwd).as_posix()
    except ValueError:
        return path.as_posix()


def _read_optional(path: Path, model_type, key_field: str):
    if not path.exists():
        return []
    return JSONLStore(path, model_type, key_field).read_all()
