from tgb_pipeline.cli import COMMANDS, build_parser, main


def test_cli_exposes_all_milestone_commands(capsys) -> None:
    parser = build_parser()

    for command in COMMANDS:
        if command == "build-review-pack":
            parsed = parser.parse_args([command, "--pack-id", "pack-1", "--title", "Pack 1"])
        elif command == "apply-review-pack":
            parsed = parser.parse_args([command, "--pack", "data/processed/tgb/review_packs/pack-1.yaml"])
        else:
            parsed = parser.parse_args([command])
        assert parsed.command == command

    assert parser.parse_args(["crawl-index"]).target_config == "configs/target.yaml"
    assert parser.parse_args(["crawl-articles"]).crawl_config == "configs/crawl.yaml"
    assert parser.parse_args(["seed-start-article"]).crawl_config == "configs/crawl.yaml"
    assert parser.parse_args(["ingest-article-seeds"]).article_seeds == "configs/article_seeds.yaml"
    assert parser.parse_args(["discover-article-seeds"]).discovery_config == "configs/article_discovery.yaml"
    assert parser.parse_args(["promote-article-seeds"]).only_selected is False
    assert parser.parse_args(["reconcile-comment-states"]).crawl_config == "configs/crawl.yaml"
    plan_args = parser.parse_args(
        [
            "plan-comment-completion",
            "--pages-per-article",
            "20",
            "--max-total-pages",
            "60",
        ]
    )
    assert plan_args.pages_per_article == 20
    assert plan_args.max_total_pages == 60
    assert parser.parse_args(["run-comment-completion-plan"]).plan.endswith(
        "comment_completion_plan.json"
    )
    assert parser.parse_args(["crawl-comments"]).crawl_config == "configs/crawl.yaml"
    comment_args = parser.parse_args(
        [
            "crawl-comments",
            "--article-id",
            "a1",
            "--start-page",
            "101",
            "--max-pages",
            "120",
            "--force-comments",
        ]
    )
    assert comment_args.article_id == "a1"
    assert comment_args.start_page == 101
    assert comment_args.max_pages == 120
    assert comment_args.force_comments is True
    assert parser.parse_args(["filter-comments"]).target_config == "configs/target.yaml"
    assert parser.parse_args(["download-images"]).ocr_config == "configs/ocr.yaml"
    assert parser.parse_args(["ocr-images"]).crawl_config == "configs/crawl.yaml"
    assert parser.parse_args(["extract-claims"]).target_config == "configs/target.yaml"
    review_ready_args = parser.parse_args(["build-review-ready-claims", "--max-per-tag", "200", "--sample-per-bucket", "10"])
    assert review_ready_args.max_per_tag == 200
    assert review_ready_args.sample_per_bucket == 10
    assert parser.parse_args(["review-claims"]).decisions == "data/processed/tgb/claim_review_decisions.yaml"
    review_ready_claim_args = parser.parse_args(["review-ready-claims", "--sync", "--apply"])
    assert review_ready_claim_args.decisions == "data/processed/tgb/review_ready_decisions.yaml"
    assert review_ready_claim_args.sync is True
    assert review_ready_claim_args.apply is True
    build_pack_args = parser.parse_args(
        ["build-review-pack", "--pack-id", "pack-1", "--title", "Pack 1", "--tag", "量化影响"]
    )
    assert build_pack_args.pack_id == "pack-1"
    assert build_pack_args.tags == ["量化影响"]
    apply_pack_args = parser.parse_args(["apply-review-pack", "--pack", "data/processed/tgb/review_packs/pack-1.yaml"])
    assert apply_pack_args.pack.endswith("pack-1.yaml")
    assert parser.parse_args(["build-default-review-packs"]).crawl_config == "configs/crawl.yaml"
    assert parser.parse_args(["audit-review-encoding"]).crawl_config == "configs/crawl.yaml"
    assert parser.parse_args(["audit-text-encoding"]).crawl_config == "configs/crawl.yaml"

    assert main(["extract-images"]) == 0
    assert "scaffold only" in capsys.readouterr().out
