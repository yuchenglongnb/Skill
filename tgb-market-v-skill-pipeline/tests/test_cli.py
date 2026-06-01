from tgb_pipeline.cli import COMMANDS, build_parser, main


def test_cli_exposes_all_milestone_commands(capsys) -> None:
    parser = build_parser()

    for command in COMMANDS:
        assert parser.parse_args([command]).command == command

    assert main(["crawl-index"]) == 0
    assert "scaffold only" in capsys.readouterr().out

