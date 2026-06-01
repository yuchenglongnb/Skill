"""Command-line entry points for the staged pipeline."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

COMMANDS = (
    "crawl-index",
    "crawl-articles",
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
        subparsers.add_parser(command, help=f"Placeholder for {command}.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    print(f"{args.command}: scaffold only; implementation is planned for a later milestone.")
    return 0

