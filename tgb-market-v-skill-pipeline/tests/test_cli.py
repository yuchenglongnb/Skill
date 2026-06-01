from tgb_pipeline.cli import COMMANDS, build_parser, main


def test_cli_exposes_all_milestone_commands(capsys) -> None:
    parser = build_parser()

    for command in COMMANDS:
        assert parser.parse_args([command]).command == command

    assert parser.parse_args(["crawl-index"]).target_config == "configs/target.yaml"
    assert parser.parse_args(["crawl-articles"]).crawl_config == "configs/crawl.yaml"
    assert parser.parse_args(["seed-start-article"]).crawl_config == "configs/crawl.yaml"

    assert main(["crawl-comments"]) == 0
    assert "scaffold only" in capsys.readouterr().out
