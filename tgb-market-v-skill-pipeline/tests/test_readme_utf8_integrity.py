from pathlib import Path


def test_readme_has_no_mojibake() -> None:
    text = Path("README.md").read_text(encoding="utf-8")
    forbidden_snippets = [
        "\ufffd",
        "蜷譁縲",
        "髱螳",
        "蟆荳",
        "繝",
    ]
    for snippet in forbidden_snippets:
        assert snippet not in text


def test_skill_outputs_have_no_mojibake() -> None:
    skill_dir = Path("skill_output") / "tgb_market_v_skill"
    for path in skill_dir.glob("*"):
        if path.suffix.lower() not in {".md", ".jsonl"}:
            continue
        text = path.read_text(encoding="utf-8")
        assert "\ufffd" not in text
        assert "蜷譁縲" not in text
