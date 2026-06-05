from pathlib import Path

from tgb_pipeline.audit.text_encoding_audit import (
    audit_default_text_outputs,
    audit_text_encoding_paths,
)
from tgb_pipeline.cli import main


def write_configs(tmp_path: Path) -> tuple[Path, Path]:
    target_path = tmp_path / "target.yaml"
    target_path.write_text(
        """
target:
  platform: taoguba
  author_name: 等主人的猫
  start_article:
    title: 情绪周期是否可靠的思考
    published_date: "2023-01-15"
""",
        encoding="utf-8",
    )
    crawl_path = tmp_path / "crawl.yaml"
    crawl_path.write_text(
        f"""
crawl:
  user_agent: fixture-agent
  request_interval_seconds: 0
  request_timeout_seconds: 10
storage:
  raw_dir: {tmp_path.as_posix()}/data/raw
  interim_dir: {tmp_path.as_posix()}/data/interim
  processed_dir: {tmp_path.as_posix()}/data/processed
""",
        encoding="utf-8",
    )
    return target_path, crawl_path


def test_audit_text_encoding_detects_question_marks_replacement_and_mojibake(tmp_path: Path) -> None:
    good_path = tmp_path / "good.md"
    qmark_path = tmp_path / "qmark.md"
    replacement_path = tmp_path / "replacement.md"
    mojibake_path = tmp_path / "mojibake.md"

    good_path.write_text("正常中文说明。", encoding="utf-8")
    qmark_path.write_text("这是一段" + ("?" * 6), encoding="utf-8")
    replacement_path.write_text("这里有替换字符\ufffd。", encoding="utf-8")
    mojibake_path.write_text("蜷譁縲逧髱螳蟆荳蝙繝", encoding="utf-8")

    summary = audit_text_encoding_paths([good_path, qmark_path, replacement_path, mojibake_path])

    assert summary["scanned_files"] == 4
    assert summary["corrupted_files"] == 3
    assert summary["corrupted_patterns"]["question_marks"] >= 1
    assert summary["corrupted_patterns"]["replacement_char"] >= 1
    assert summary["corrupted_patterns"]["mojibake_cluster"] >= 1


def test_audit_text_encoding_cli_returns_nonzero_when_corrupted(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "README.md").write_text("坏掉了" + ("?" * 5), encoding="utf-8")
    (tmp_path / "configs").mkdir(parents=True, exist_ok=True)
    (tmp_path / "src").mkdir(parents=True, exist_ok=True)
    (tmp_path / "reports").mkdir(parents=True, exist_ok=True)
    target_path, crawl_path = write_configs(tmp_path)
    monkeypatch.chdir(tmp_path)

    assert (
        main(
            [
                "audit-text-encoding",
                "--target-config",
                str(target_path),
                "--crawl-config",
                str(crawl_path),
            ]
        )
        == 1
    )
    assert (tmp_path / "reports" / "text_encoding_audit.md").is_file()


def test_audit_text_encoding_default_outputs_pass_on_clean_subset(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Clean\n\n正常中文。\n", encoding="utf-8")
    (tmp_path / "data").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data" / "README.md").write_text("# Data\n\n正常中文。\n", encoding="utf-8")
    (tmp_path / "configs").mkdir(parents=True, exist_ok=True)
    (tmp_path / "configs" / "target.yaml").write_text("target:\n  platform: taoguba\n", encoding="utf-8")
    (tmp_path / "src").mkdir(parents=True, exist_ok=True)
    (tmp_path / "src" / "sample.py").write_text("VALUE = '正常中文'\n", encoding="utf-8")
    (tmp_path / "reports").mkdir(parents=True, exist_ok=True)
    (tmp_path / "skill_output" / "tgb_market_v_skill").mkdir(parents=True, exist_ok=True)
    (tmp_path / "skill_output" / "tgb_market_v_skill" / "SKILL.md").write_text("# Skill\n\n正常中文。\n", encoding="utf-8")

    summary, report_path = audit_default_text_outputs(tmp_path, tmp_path / "reports")
    assert summary["corrupted_files"] == 0
    assert report_path.is_file()
