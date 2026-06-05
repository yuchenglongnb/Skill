"""Repo-wide text encoding audit for docs, config, source, and skill outputs."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

SUSPICIOUS_QUESTION_RE = re.compile(r"\?{3,}")
SUSPICIOUS_MOJIBAKE_CHARS = "".join(
    [
        "\u8737",
        "\u8b41",
        "\u7e32",
        "\u9027",
        "\u9af1",
        "\u87b3",
        "\u87c6",
        "\u8373",
        "\u8759",
        "\u7e5d",
    ]
)
SUSPICIOUS_MOJIBAKE_RE = re.compile("[" + re.escape(SUSPICIOUS_MOJIBAKE_CHARS) + "]{2,}")
SUSPICIOUS_LATIN_RE = re.compile(
    "(?:"
    + re.escape("\u00e3")
    + "|"
    + re.escape("\u00e2")
    + "){2,}|"
    + re.escape("\u00e3\u20ac")
    + "|"
    + re.escape("\u00e2\u20ac\u201d")
    + "|"
    + re.escape("\u00e2\u20ac\u0153")
    + "|"
    + re.escape("\u00e2\u20ac")
)
REPLACEMENT_CHAR = "\ufffd"

TEXT_EXTENSIONS = {".md", ".yaml", ".yml", ".json", ".jsonl", ".py", ".toml", ".txt"}
DEFAULT_EXCLUDED_PARTS = {
    ".git",
    "__pycache__",
    ".venv",
    "html",
}


def audit_text_encoding_paths(paths: list[Path]) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    for path in paths:
        if not path.exists() or not path.is_file():
            continue
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        if any(part in DEFAULT_EXCLUDED_PARTS for part in path.parts):
            continue
        results.append(audit_text_file(path))

    corrupted = [result for result in results if result["corrupted"]]
    summary = {
        "scanned_files": len(results),
        "corrupted_files": len(corrupted),
        "corrupted_patterns": _aggregate_patterns(corrupted),
        "examples": [result["path"] for result in corrupted[:10]],
        "results": results,
        "recommended_action": (
            "Rewrite corrupted docs/config text in UTF-8 and avoid shell/editor paths that replace characters with question marks or replacement chars."
            if corrupted
            else "No action required."
        ),
    }
    return summary


def audit_text_file(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    detected_patterns: list[str] = []
    if SUSPICIOUS_QUESTION_RE.search(text):
        detected_patterns.append("question_marks")
    if REPLACEMENT_CHAR in text:
        detected_patterns.append("replacement_char")
    if SUSPICIOUS_MOJIBAKE_RE.search(text):
        detected_patterns.append("mojibake_cluster")
    if SUSPICIOUS_LATIN_RE.search(text):
        detected_patterns.append("latin_mojibake")

    examples = _extract_examples(text)
    return {
        "path": path.as_posix(),
        "detected_patterns": detected_patterns,
        "corrupted": bool(detected_patterns),
        "examples": examples,
    }


def collect_default_text_audit_paths(root: Path) -> list[Path]:
    candidates: list[Path] = []
    excluded_paths = {
        (root / "reports" / "text_encoding_audit.md").resolve(),
    }
    explicit_files = [
        root / "README.md",
        root / "data" / "README.md",
        root / "pyproject.toml",
    ]
    for file_path in explicit_files:
        if file_path.exists():
            candidates.append(file_path)

    glob_specs = [
        root / "configs",
        root / "src",
        root / "reports",
        root / "skill_output",
        root / "data" / "processed" / "tgb" / "review_packs",
    ]
    explicit_review_files = [
        root / "data" / "processed" / "tgb" / "review_ready_decisions.yaml",
        root / "data" / "processed" / "tgb" / "corpus_manifest.json",
    ]

    for base in glob_specs:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix.lower() in TEXT_EXTENSIONS and not any(
                part in DEFAULT_EXCLUDED_PARTS for part in path.parts
            ):
                candidates.append(path)

    for file_path in explicit_review_files:
        if file_path.exists():
            candidates.append(file_path)

    seen: set[str] = set()
    deduped: list[Path] = []
    for path in candidates:
        key = str(path.resolve())
        if Path(key) in excluded_paths:
            continue
        if key in seen:
            continue
        seen.add(key)
        deduped.append(path)
    return deduped


def build_text_encoding_report(summary: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Text Encoding Audit",
        "",
        "## Summary",
        f"- scanned_files: {summary['scanned_files']}",
        f"- corrupted_files: {summary['corrupted_files']}",
        f"- corrupted_patterns: {summary['corrupted_patterns']}",
        f"- recommended_action: {summary['recommended_action']}",
        "",
        "## Files",
        "",
    ]
    if not summary["results"]:
        lines.append("- none")
    for result in summary["results"]:
        lines.extend(
            [
                f"### {result['path']}",
                "",
                f"- corrupted: {result['corrupted']}",
                f"- detected_patterns: {result['detected_patterns']}",
                f"- examples: {result['examples']}",
                "",
            ]
        )
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def audit_default_text_outputs(root: Path, reports_dir: Path) -> tuple[dict[str, Any], Path]:
    summary = audit_text_encoding_paths(collect_default_text_audit_paths(root))
    report_path = build_text_encoding_report(summary, reports_dir / "text_encoding_audit.md")
    summary = dict(summary)
    summary["report_path"] = report_path.as_posix()
    return summary, report_path


def _aggregate_patterns(corrupted_results: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for result in corrupted_results:
        for pattern in result["detected_patterns"]:
            counts[pattern] = counts.get(pattern, 0) + 1
    return counts


def _extract_examples(text: str) -> list[str]:
    examples: list[str] = []
    regexes = [
        SUSPICIOUS_QUESTION_RE,
        re.compile(REPLACEMENT_CHAR),
        SUSPICIOUS_MOJIBAKE_RE,
        SUSPICIOUS_LATIN_RE,
    ]
    for regex in regexes:
        for match in regex.finditer(text):
            snippet = text[max(0, match.start() - 20): min(len(text), match.end() + 20)]
            snippet = " ".join(snippet.split())
            if snippet and snippet not in examples:
                examples.append(snippet[:120])
            if len(examples) >= 5:
                return examples
    return examples
