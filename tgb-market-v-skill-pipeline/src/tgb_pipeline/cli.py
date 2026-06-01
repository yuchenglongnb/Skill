"""Command-line entry points for the staged pipeline."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from tgb_pipeline.config import load_crawl_config, load_target_config
from tgb_pipeline.crawler.comment_tasks import crawl_comments, filter_comments
from tgb_pipeline.crawler.tasks import crawl_articles, crawl_index, seed_start_article

COMMANDS = (
    "crawl-index",
    "crawl-articles",
    "seed-start-article",
    "crawl-comments",
    "filter-comments",
    "extract-images",
    "download-images",
    "ocr-images",
    "export-corpus",
    "extract-claims",
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
            "crawl-comments",
            "filter-comments",
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
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command in {
        "crawl-index",
        "crawl-articles",
        "seed-start-article",
        "crawl-comments",
        "filter-comments",
    }:
        target_config = load_target_config(args.target_config)
        crawl_config = load_crawl_config(args.crawl_config)
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
