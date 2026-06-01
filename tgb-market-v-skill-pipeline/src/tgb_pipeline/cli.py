"""Command-line entry points for the staged pipeline."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from tgb_pipeline.config import load_crawl_config, load_ocr_config, load_target_config
from tgb_pipeline.curation.tasks import review_claims_bundle
from tgb_pipeline.crawler.comment_tasks import crawl_comments, filter_comments
from tgb_pipeline.crawler.tasks import (
    crawl_articles,
    crawl_index,
    ingest_article_seeds,
    seed_start_article,
)
from tgb_pipeline.extraction.tasks import extract_claims_bundle
from tgb_pipeline.export.tasks import export_corpus_bundle
from tgb_pipeline.images.tasks import download_images_task, ocr_images_task

COMMANDS = (
    "crawl-index",
    "crawl-articles",
    "seed-start-article",
    "ingest-article-seeds",
    "crawl-comments",
    "filter-comments",
    "extract-images",
    "download-images",
    "ocr-images",
    "export-corpus",
    "extract-claims",
    "review-claims",
    "build-skill",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tgb-pipeline",
        description="Build a structured Taoguba methodology evidence corpus.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in COMMANDS:
        command_parser = subparsers.add_parser(command, help=f"Run {command}.")
        if command in {
            "crawl-index",
            "crawl-articles",
            "seed-start-article",
            "ingest-article-seeds",
            "crawl-comments",
            "filter-comments",
            "download-images",
            "ocr-images",
            "export-corpus",
            "extract-claims",
            "review-claims",
        }:
            command_parser.add_argument(
                "--target-config",
                default="configs/target.yaml",
                help="Path to target YAML configuration.",
            )
            command_parser.add_argument(
                "--crawl-config",
                default="configs/crawl.yaml",
                help="Path to crawl YAML configuration.",
            )
        if command in {"download-images", "ocr-images"}:
            command_parser.add_argument(
                "--ocr-config",
                default="configs/ocr.yaml",
                help="Path to OCR and image YAML configuration.",
            )
        if command == "ingest-article-seeds":
            command_parser.add_argument(
                "--article-seeds",
                default="configs/article_seeds.yaml",
                help="Path to manual article seed YAML configuration.",
            )
        if command == "review-claims":
            command_parser.add_argument(
                "--decisions",
                default="data/processed/tgb/claim_review_decisions.yaml",
                help="Path to claim review decision YAML file.",
            )
            command_parser.add_argument(
                "--overwrite-review-template",
                action="store_true",
                help="Overwrite an existing review template.",
            )
            command_parser.add_argument(
                "--include-unreviewed",
                action="store_true",
                help="Include unreviewed claims in the needs-edit output when applying.",
            )
            command_parser.add_argument(
                "--apply",
                action="store_true",
                help="Apply review decisions and emit curated artifacts.",
            )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command in {
        "crawl-index",
        "crawl-articles",
        "seed-start-article",
        "ingest-article-seeds",
        "crawl-comments",
        "filter-comments",
        "download-images",
        "ocr-images",
        "export-corpus",
        "extract-claims",
        "review-claims",
    }:
        target_config = load_target_config(args.target_config)
        crawl_config = load_crawl_config(args.crawl_config)
        ocr_config = (
            load_ocr_config(args.ocr_config)
            if hasattr(args, "ocr_config")
            else None
        )
        try:
            if args.command == "crawl-index":
                result = crawl_index(target_config, crawl_config)
                if result.used_seed_fallback:
                    print(
                        "crawl-index: appended "
                        f"{result.seed_appended_count} seed article index record"
                        f"{'' if result.seed_appended_count == 1 else 's'} because "
                        "start article was not visible in public index."
                    )
                else:
                    print(
                        f"crawl-index: appended {result.appended_count} "
                        "article index records."
                    )
            elif args.command == "seed-start-article":
                count = seed_start_article(target_config, crawl_config)
                print(f"seed-start-article: appended {count} seed article index records.")
            elif args.command == "ingest-article-seeds":
                result = ingest_article_seeds(
                    target_config,
                    crawl_config,
                    args.article_seeds,
                )
                print(
                    "ingest-article-seeds: added "
                    f"{result.added_count}, total {result.total_article_index_count}, "
                    f"skipped_before_start {result.skipped_before_start_count}, "
                    f"duplicates {result.duplicate_count}."
                )
            elif args.command == "crawl-comments":
                comment_count, image_count = crawl_comments(target_config, crawl_config)
                print(
                    "crawl-comments: appended "
                    f"{comment_count} comments and {image_count} image assets."
                )
            elif args.command == "filter-comments":
                kept_count, aoch_count, interaction_count = filter_comments(
                    target_config,
                    crawl_config,
                )
                print(
                    "filter-comments: appended "
                    f"{kept_count} comments, {aoch_count} aoch comments, and "
                    f"{interaction_count} interactions."
                )
            elif args.command == "export-corpus":
                raw_dir = crawl_config.storage.raw_dir / "tgb"
                processed_dir = crawl_config.storage.processed_dir / "tgb"
                outputs = export_corpus_bundle(raw_dir, processed_dir, Path("reports"), target_config)
                print(f"export-corpus: generated {len(outputs)} outputs.")
            elif args.command == "download-images":
                downloaded_count, failed_count = download_images_task(
                    crawl_config,
                    ocr_config,
                )
                print(
                    "download-images: downloaded "
                    f"{downloaded_count} images, failed {failed_count} images."
                )
            elif args.command == "ocr-images":
                ocr_count, skipped_count, failed_count = ocr_images_task(
                    crawl_config,
                    ocr_config,
                )
                print(
                    "ocr-images: created "
                    f"{ocr_count} ocr records, skipped {skipped_count} images, "
                    f"failed {failed_count} images."
                )
            elif args.command == "extract-claims":
                raw_dir = crawl_config.storage.raw_dir / "tgb"
                processed_dir = crawl_config.storage.processed_dir / "tgb"
                outputs = extract_claims_bundle(raw_dir, processed_dir, Path("reports"))
                print(f"extract-claims: generated {len(outputs)} outputs.")
            elif args.command == "review-claims":
                raw_dir = crawl_config.storage.raw_dir / "tgb"
                processed_dir = crawl_config.storage.processed_dir / "tgb"
                outputs = review_claims_bundle(
                    raw_dir,
                    processed_dir,
                    Path("reports"),
                    decisions_path=Path(args.decisions),
                    overwrite_review_template=args.overwrite_review_template,
                    include_unreviewed=args.include_unreviewed,
                    apply=args.apply,
                )
                print(f"review-claims: generated {len(outputs)} outputs.")
            else:
                article_count, image_count = crawl_articles(target_config, crawl_config)
                print(
                    "crawl-articles: appended "
                    f"{article_count} articles and {image_count} image assets."
                )
        except (PermissionError, ValueError) as exc:
            print(f"{args.command}: stopped: {exc}", file=sys.stderr)
            return 2
        return 0
    print(f"{args.command}: scaffold only; implementation is planned for a later milestone.")
    return 0
