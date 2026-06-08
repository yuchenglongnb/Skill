"""Command-line entry points for the staged pipeline."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from tgb_pipeline.audit.article_inventory_audit import build_article_inventory_report
from tgb_pipeline.audit.comment_state_audit import build_comment_state_warning_report
from tgb_pipeline.audit.text_encoding_audit import audit_default_text_outputs
from tgb_pipeline.config import (
    load_article_discovery_config,
    load_crawl_config,
    load_ocr_config,
    load_target_config,
)
from tgb_pipeline.completion.tasks import (
    execute_comment_completion_plan,
    generate_comment_completion_plan_bundle,
)
from tgb_pipeline.curation.tasks import (
    audit_review_encoding_bundle,
    apply_review_pack_bundle,
    build_default_review_packs_bundle,
    build_review_pack_bundle,
    review_claims_bundle,
    review_ready_claims_bundle,
)
from tgb_pipeline.crawler.comment_checkpoint import (
    bootstrap_comment_page_states_from_snapshots,
    reconcile_comment_article_states,
)
from tgb_pipeline.crawler.comment_tasks import crawl_comments, filter_comments
from tgb_pipeline.crawler.tasks import (
    crawl_articles,
    crawl_index,
    ingest_article_seeds,
    seed_start_article,
)
from tgb_pipeline.discovery.tasks import (
    discover_article_seeds_task,
    promote_candidates_to_article_seeds,
)
from tgb_pipeline.extraction.tasks import build_review_ready_claims_bundle, extract_claims_bundle
from tgb_pipeline.export.tasks import export_corpus_bundle
from tgb_pipeline.images.tasks import download_images_task, ocr_images_task
from tgb_pipeline.skill.tasks import build_skill_v0_bundle

COMMANDS = (
    "crawl-index",
    "crawl-articles",
    "seed-start-article",
    "ingest-article-seeds",
    "discover-article-seeds",
    "promote-article-seeds",
    "reconcile-comment-states",
    "plan-comment-completion",
    "run-comment-completion-plan",
    "crawl-comments",
    "filter-comments",
    "extract-images",
    "download-images",
    "ocr-images",
    "export-corpus",
    "extract-claims",
    "build-review-ready-claims",
    "review-claims",
    "review-ready-claims",
    "build-review-pack",
    "apply-review-pack",
    "build-default-review-packs",
    "audit-review-encoding",
    "audit-text-encoding",
    "build-skill",
    "build-skill-v0",
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
            "reconcile-comment-states",
            "download-images",
            "ocr-images",
            "export-corpus",
            "extract-claims",
            "build-review-ready-claims",
            "review-claims",
            "review-ready-claims",
            "build-review-pack",
            "apply-review-pack",
            "build-default-review-packs",
            "audit-review-encoding",
            "audit-text-encoding",
            "build-skill-v0",
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
        if command == "crawl-comments":
            command_parser.add_argument(
                "--article-id",
                help="Only crawl comments for one article ID.",
            )
            command_parser.add_argument(
                "--start-page",
                type=int,
                help="Override the checkpoint and begin at this page.",
            )
            command_parser.add_argument(
                "--max-pages",
                type=int,
                help="Override the maximum page number for this run.",
            )
            command_parser.add_argument(
                "--force-comments",
                action="store_true",
                help="Refetch pages even when checkpoint state already exists.",
            )
        if command == "discover-article-seeds":
            command_parser.add_argument(
                "--target-config",
                default="configs/target.yaml",
                help="Path to target YAML configuration.",
            )
            command_parser.add_argument(
                "--discovery-config",
                default="configs/article_discovery.yaml",
                help="Path to article discovery YAML configuration.",
            )
            command_parser.add_argument(
                "--output",
                default="data/interim/tgb/article_seed_candidates.jsonl",
                help="Path to article seed candidate JSONL output.",
            )
        if command == "promote-article-seeds":
            command_parser.add_argument(
                "--candidates",
                default="data/interim/tgb/article_seed_candidates.jsonl",
                help="Path to article seed candidate JSONL file.",
            )
            command_parser.add_argument(
                "--article-seeds",
                default="configs/article_seeds.yaml",
                help="Path to article seeds YAML file.",
            )
            command_parser.add_argument(
                "--only-selected",
                action="store_true",
                help="Only promote candidates manually marked as selected.",
            )
            command_parser.add_argument(
                "--min-confidence",
                default="medium",
                help="Minimum confidence to promote when --only-selected is not used.",
            )
            command_parser.add_argument(
                "--dry-run",
                action="store_true",
                help="Preview seed promotion without writing the YAML file.",
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
        if command == "review-ready-claims":
            command_parser.add_argument(
                "--decisions",
                default="data/processed/tgb/review_ready_decisions.yaml",
                help="Path to review-ready decision YAML file.",
            )
            command_parser.add_argument(
                "--overwrite-template",
                action="store_true",
                help="Overwrite an existing review-ready template.",
            )
            command_parser.add_argument(
                "--include-unreviewed",
                action="store_true",
                help="Include unreviewed claims in the needs-edit output when applying.",
            )
            command_parser.add_argument(
                "--sync",
                action="store_true",
                help="Sync the current review-ready claim set with an existing decisions file.",
            )
            command_parser.add_argument(
                "--apply",
                action="store_true",
                help="Apply review-ready decisions and emit curated artifacts.",
            )
        if command == "build-review-pack":
            command_parser.add_argument("--pack-id", required=True, help="Stable review pack identifier.")
            command_parser.add_argument("--title", required=True, help="Human-readable review pack title.")
            command_parser.add_argument("--tag", dest="tags", action="append", default=[], help="Method tag filter.")
            command_parser.add_argument("--article-id", dest="article_ids", action="append", default=[], help="Article ID filter.")
            command_parser.add_argument("--bucket", dest="buckets", action="append", default=[], help="Review bucket filter.")
            command_parser.add_argument("--priority", dest="priorities", action="append", default=[], help="Review priority filter.")
            command_parser.add_argument("--max-items", type=int, default=100, help="Maximum number of claims in the pack.")
            command_parser.add_argument(
                "--include-reviewed",
                action="store_true",
                help="Include claims that already have accepted/rejected/needs_edit decisions.",
            )
            command_parser.add_argument(
                "--decisions",
                default="data/processed/tgb/review_ready_decisions.yaml",
                help="Path to review-ready decisions YAML file.",
            )
        if command == "apply-review-pack":
            command_parser.add_argument("--pack", required=True, help="Path to an editable review pack YAML file.")
            command_parser.add_argument(
                "--decisions",
                default="data/processed/tgb/review_ready_decisions.yaml",
                help="Path to review-ready decisions YAML file.",
            )
            command_parser.add_argument(
                "--overwrite-existing",
                action="store_true",
                help="Allow pack decisions to overwrite existing accepted/rejected/needs_edit entries.",
            )
        if command == "build-skill-v0":
            command_parser.add_argument(
                "--output-dir",
                default="skill_output/tgb_market_v_skill",
                help="Directory for the generated Skill v0 artifacts.",
            )
            command_parser.add_argument(
                "--include-needs-edit-index",
                action="store_true",
                help="Also emit a separate needs-edit evidence index.",
            )
            command_parser.add_argument(
                "--max-claims-per-theme",
                type=int,
                default=5,
                help="Maximum number of representative claims and rules per theme.",
            )
            command_parser.add_argument(
                "--max-rules-per-theme",
                type=int,
                default=4,
                help="Maximum number of normalized rules to emit per theme.",
            )
            command_parser.add_argument(
                "--max-evidence-per-rule",
                type=int,
                default=5,
                help="Maximum number of accepted claim IDs to attach to one rule.",
            )
            command_parser.add_argument(
                "--include-needs-edit-worklist",
                action="store_true",
                help="Also emit a needs-edit worklist markdown file.",
            )
            command_parser.add_argument(
                "--rule-mode",
                action="store_true",
                help="Generate the rule-normalized Skill v0.2 artifact set.",
            )
            command_parser.add_argument(
                "--strict-rule-abstraction",
                action="store_true",
                help="Fail if rule texts still contain direct claim excerpts or generic rule titles.",
            )
            command_parser.add_argument(
                "--generate-accepted-recheck-pack",
                action="store_true",
                help="Generate a recheck pack for accepted claims that remain too colloquial or context-dependent.",
            )
        if command in {"extract-claims", "build-review-ready-claims"}:
            command_parser.add_argument(
                "--max-per-tag",
                type=int,
                default=500,
                help="Maximum number of normal-priority claims to keep per method tag.",
            )
            command_parser.add_argument(
                "--sample-per-bucket",
                type=int,
                default=20,
                help="Maximum number of sample claims to show per review bucket.",
            )
        if command == "plan-comment-completion":
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
            command_parser.add_argument("--article-id")
            command_parser.add_argument("--pages-per-article", type=int)
            command_parser.add_argument("--max-total-pages", type=int)
        if command == "run-comment-completion-plan":
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
            command_parser.add_argument(
                "--plan",
                default="data/interim/tgb/comment_completion_plan.json",
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
        "reconcile-comment-states",
        "download-images",
        "ocr-images",
        "export-corpus",
        "extract-claims",
        "build-review-ready-claims",
        "review-claims",
        "review-ready-claims",
        "build-review-pack",
        "apply-review-pack",
        "build-default-review-packs",
        "audit-review-encoding",
        "audit-text-encoding",
        "build-skill-v0",
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
                result = crawl_comments(
                    target_config,
                    crawl_config,
                    article_id=args.article_id,
                    start_page=args.start_page,
                    max_pages=args.max_pages,
                    force_comments=args.force_comments,
                )
                print(
                    "crawl-comments: appended "
                    f"{result.appended_comments} comments and "
                    f"{result.appended_images} image assets; fetched "
                    f"{result.fetched_pages} pages, skipped {result.skipped_pages} "
                    f"pages, failed {result.failed_pages} pages; completed "
                    f"{result.completed_articles} articles, max-limit "
                    f"{result.max_limit_articles} articles."
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
            elif args.command == "reconcile-comment-states":
                raw_dir = crawl_config.storage.raw_dir / "tgb"
                reports_dir = Path("reports")
                bootstrap_comment_page_states_from_snapshots(raw_dir)
                reconciled = reconcile_comment_article_states(
                    raw_dir,
                    max_pages_limit=crawl_config.crawl.max_comment_pages_per_article,
                )
                inventory_path = reports_dir / "article_inventory_report.md"
                build_article_inventory_report(raw_dir, inventory_path)
                warning_path = build_comment_state_warning_report(raw_dir, reports_dir)
                print(
                    "reconcile-comment-states: rebuilt "
                    f"{reconciled} article states, inventory {inventory_path.as_posix()}, "
                    f"warnings {warning_path.as_posix()}."
                )
            elif args.command == "export-corpus":
                raw_dir = crawl_config.storage.raw_dir / "tgb"
                processed_dir = crawl_config.storage.processed_dir / "tgb"
                outputs = export_corpus_bundle(
                    raw_dir,
                    processed_dir,
                    Path("reports"),
                    target_config,
                    max_pages_limit=crawl_config.crawl.max_comment_pages_per_article,
                )
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
                outputs = extract_claims_bundle(
                    raw_dir,
                    processed_dir,
                    Path("reports"),
                    max_per_tag=args.max_per_tag,
                    sample_per_bucket=args.sample_per_bucket,
                )
                print(f"extract-claims: generated {len(outputs)} outputs.")
            elif args.command == "build-review-ready-claims":
                raw_dir = crawl_config.storage.raw_dir / "tgb"
                processed_dir = crawl_config.storage.processed_dir / "tgb"
                outputs = build_review_ready_claims_bundle(
                    raw_dir,
                    processed_dir,
                    Path("reports"),
                    max_per_tag=args.max_per_tag,
                    sample_per_bucket=args.sample_per_bucket,
                )
                print(f"build-review-ready-claims: generated {len(outputs)} outputs.")
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
            elif args.command == "review-ready-claims":
                raw_dir = crawl_config.storage.raw_dir / "tgb"
                processed_dir = crawl_config.storage.processed_dir / "tgb"
                outputs = review_ready_claims_bundle(
                    raw_dir,
                    processed_dir,
                    Path("reports"),
                    decisions_path=Path(args.decisions),
                    overwrite_template=args.overwrite_template,
                    include_unreviewed=args.include_unreviewed,
                    sync=args.sync,
                    apply=args.apply,
                )
                print(f"review-ready-claims: generated {len(outputs)} outputs.")
            elif args.command == "build-review-pack":
                raw_dir = crawl_config.storage.raw_dir / "tgb"
                processed_dir = crawl_config.storage.processed_dir / "tgb"
                item_count, outputs = build_review_pack_bundle(
                    raw_dir,
                    processed_dir,
                    Path("reports"),
                    pack_id=args.pack_id,
                    title=args.title,
                    tags=args.tags,
                    article_ids=args.article_ids,
                    buckets=args.buckets,
                    priorities=args.priorities,
                    max_items=args.max_items,
                    include_reviewed=args.include_reviewed,
                    decisions_path=Path(args.decisions),
                )
                print(
                    "build-review-pack: wrote "
                    f"{item_count} items to {outputs[0].as_posix()}"
                )
            elif args.command == "apply-review-pack":
                raw_dir = crawl_config.storage.raw_dir / "tgb"
                processed_dir = crawl_config.storage.processed_dir / "tgb"
                stats, _outputs = apply_review_pack_bundle(
                    raw_dir,
                    processed_dir,
                    Path("reports"),
                    pack_path=Path(args.pack),
                    decisions_path=Path(args.decisions),
                    overwrite_existing=args.overwrite_existing,
                )
                print(
                    "apply-review-pack: applied "
                    f"{stats['applied']} decisions, skipped {stats['skipped_unreviewed']} unreviewed."
                )
            elif args.command == "build-default-review-packs":
                raw_dir = crawl_config.storage.raw_dir / "tgb"
                processed_dir = crawl_config.storage.processed_dir / "tgb"
                outputs = build_default_review_packs_bundle(
                    raw_dir,
                    processed_dir,
                    Path("reports"),
                    decisions_path=Path("data/processed/tgb/review_ready_decisions.yaml"),
                )
                print(f"build-default-review-packs: generated {len(outputs)} outputs.")
            elif args.command == "audit-review-encoding":
                raw_dir = crawl_config.storage.raw_dir / "tgb"
                processed_dir = crawl_config.storage.processed_dir / "tgb"
                stats, report_path = audit_review_encoding_bundle(
                    raw_dir,
                    processed_dir,
                    Path("reports"),
                )
                print(
                    "audit-review-encoding: checked "
                    f"{stats['total_files']} files, found "
                    f"{stats['corrupted_files']} corrupted files; report "
                    f"{report_path.as_posix()}"
                )
                if stats["corrupted_files"] > 0:
                    print("corrupted review text found", file=sys.stderr)
                    return 1
            elif args.command == "audit-text-encoding":
                summary, report_path = audit_default_text_outputs(Path.cwd(), Path("reports"))
                print(
                    "audit-text-encoding: checked "
                    f"{summary['scanned_files']} files, found "
                    f"{summary['corrupted_files']} corrupted files; report "
                    f"{report_path.as_posix()}"
                )
                if summary["corrupted_files"] > 0:
                    print("corrupted text found", file=sys.stderr)
                    return 1
            elif args.command == "build-skill-v0":
                raw_dir = crawl_config.storage.raw_dir / "tgb"
                processed_dir = crawl_config.storage.processed_dir / "tgb"
                outputs = build_skill_v0_bundle(
                    raw_dir,
                    processed_dir,
                    Path("reports"),
                    output_dir=Path(args.output_dir),
                    include_needs_edit_index=args.include_needs_edit_index,
                    include_needs_edit_worklist=args.include_needs_edit_worklist,
                    max_claims_per_theme=args.max_claims_per_theme,
                    max_rules_per_theme=args.max_rules_per_theme,
                    max_evidence_per_rule=args.max_evidence_per_rule,
                    rule_mode=args.rule_mode,
                    strict_rule_abstraction=args.strict_rule_abstraction,
                    generate_accepted_recheck_pack=args.generate_accepted_recheck_pack,
                )
                print(f"build-skill-v0: generated {len(outputs)} outputs.")
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
    if args.command == "discover-article-seeds":
        target_config = load_target_config(args.target_config)
        discovery_config = load_article_discovery_config(args.discovery_config)
        try:
            count, report_path = discover_article_seeds_task(
                discovery_config,
                target_config,
                output_path=Path(args.output),
                reports_dir=Path("reports"),
            )
            print(
                "discover-article-seeds: discovered "
                f"{count} candidates, report {report_path.as_posix()}"
            )
        except ValueError as exc:
            print(f"{args.command}: stopped: {exc}", file=sys.stderr)
            return 2
        return 0
    if args.command == "promote-article-seeds":
        try:
            added_count, total_seed_count = promote_candidates_to_article_seeds(
                Path(args.candidates),
                Path(args.article_seeds),
                only_selected=args.only_selected,
                min_confidence=args.min_confidence,
                dry_run=args.dry_run,
            )
            print(
                "promote-article-seeds: added "
                f"{added_count} article seeds, total {total_seed_count}."
            )
        except ValueError as exc:
            print(f"{args.command}: stopped: {exc}", file=sys.stderr)
            return 2
        return 0
    if args.command == "plan-comment-completion":
        crawl_config = load_crawl_config(args.crawl_config)
        outputs = generate_comment_completion_plan_bundle(
            crawl_config,
            article_id=args.article_id,
            pages_per_article=args.pages_per_article,
            max_total_pages=args.max_total_pages,
        )
        plan_payload = __import__("json").loads(outputs[0].read_text(encoding="utf-8"))
        print(
            "plan-comment-completion: planned "
            f"{plan_payload['total_items']} articles and "
            f"{plan_payload['total_planned_pages']} pages."
        )
        return 0
    if args.command == "run-comment-completion-plan":
        target_config = load_target_config(args.target_config)
        crawl_config = load_crawl_config(args.crawl_config)
        comments, images, pages = execute_comment_completion_plan(
            target_config,
            crawl_config,
            plan_path=Path(args.plan),
        )
        print(
            "run-comment-completion-plan: appended "
            f"{comments} comments, {images} image assets, fetched {pages} pages."
        )
        return 0
    print(f"{args.command}: scaffold only; implementation is planned for a later milestone.")
    return 0
