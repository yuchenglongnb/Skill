"""Audit review files for suspiciously corrupted UTF-8 review text."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

CORRUPTED_REVIEW_TEXT_RE = re.compile(r"\?{3,}")


def has_corrupted_review_text(text: str | None) -> bool:
    if not text:
        return False
    return bool(CORRUPTED_REVIEW_TEXT_RE.search(str(text)))


def audit_review_file_encoding(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "path": path.as_posix(),
            "exists": False,
            "total_items": 0,
            "reviewed_items": 0,
            "corrupted_review_notes_count": 0,
            "corrupted_edited_claim_text_count": 0,
            "sample_claim_ids": [],
            "corrupted": False,
        }

    suffix = path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        items = _load_yaml_items(path)
    elif suffix == ".jsonl":
        items = _load_jsonl_items(path)
    else:
        raise ValueError(f"unsupported review audit file type: {path}")

    reviewed_items = 0
    corrupted_review_notes_count = 0
    corrupted_edited_claim_text_count = 0
    sample_claim_ids: list[str] = []

    for item in items:
        decision = str(item.get("decision", "unreviewed"))
        review_notes = _normalize_optional_text(item.get("review_notes"))
        edited_claim_text = _normalize_optional_text(item.get("edited_claim_text"))
        is_reviewed = decision != "unreviewed" or bool(review_notes) or bool(edited_claim_text)
        if is_reviewed:
            reviewed_items += 1

        corrupted = False
        if has_corrupted_review_text(review_notes):
            corrupted_review_notes_count += 1
            corrupted = True
        if has_corrupted_review_text(edited_claim_text):
            corrupted_edited_claim_text_count += 1
            corrupted = True

        if corrupted and len(sample_claim_ids) < 5:
            sample_claim_ids.append(str(item.get("claim_id", "<unknown>")))

    return {
        "path": path.as_posix(),
        "exists": True,
        "total_items": len(items),
        "reviewed_items": reviewed_items,
        "corrupted_review_notes_count": corrupted_review_notes_count,
        "corrupted_edited_claim_text_count": corrupted_edited_claim_text_count,
        "sample_claim_ids": sample_claim_ids,
        "corrupted": (corrupted_review_notes_count + corrupted_edited_claim_text_count) > 0,
    }


def audit_review_encoding_outputs(
    processed_dir: Path,
    reports_dir: Path,
) -> tuple[dict[str, Any], Path]:
    paths = _default_review_paths(processed_dir)
    results = [audit_review_file_encoding(path) for path in paths]
    report_path = build_review_encoding_report(results, reports_dir / "review_encoding_audit.md")
    summary = {
        "total_files": len(results),
        "corrupted_files": sum(1 for result in results if result["corrupted"]),
        "total_reviewed_items": sum(int(result["reviewed_items"]) for result in results),
        "corrupted_review_notes_count": sum(
            int(result["corrupted_review_notes_count"]) for result in results
        ),
        "corrupted_edited_claim_text_count": sum(
            int(result["corrupted_edited_claim_text_count"]) for result in results
        ),
        "results": results,
        "report_path": report_path.as_posix(),
    }
    return summary, report_path


def build_review_encoding_report(results: list[dict[str, Any]], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    total_reviewed = sum(int(result["reviewed_items"]) for result in results)
    total_corrupted_notes = sum(int(result["corrupted_review_notes_count"]) for result in results)
    total_corrupted_edited = sum(
        int(result["corrupted_edited_claim_text_count"]) for result in results
    )
    corrupted_files = [result for result in results if result["corrupted"]]

    lines = [
        "# Review Encoding Audit",
        "",
        "## Summary",
        f"- total_files: {len(results)}",
        f"- corrupted_files: {len(corrupted_files)}",
        f"- total_reviewed_items: {total_reviewed}",
        f"- corrupted_review_notes_count: {total_corrupted_notes}",
        f"- corrupted_edited_claim_text_count: {total_corrupted_edited}",
        "",
        "## Files",
        "",
    ]

    if not results:
        lines.append("- none")
    for result in results:
        lines.extend(
            [
                f"### {result['path']}",
                "",
                f"- exists: {result['exists']}",
                f"- total_items: {result['total_items']}",
                f"- reviewed_items: {result['reviewed_items']}",
                f"- corrupted_review_notes_count: {result['corrupted_review_notes_count']}",
                f"- corrupted_edited_claim_text_count: {result['corrupted_edited_claim_text_count']}",
                f"- sample_claim_ids: {result['sample_claim_ids']}",
                "",
            ]
        )

    lines.extend(
        [
            "## Repair Guidance",
            "",
            "- Ensure YAML writes use UTF-8 with `allow_unicode=True`.",
            "- Ensure JSONL writes use UTF-8 with `ensure_ascii=False`.",
            "- If corruption is found, rebuild `review_notes` or `edited_claim_text` from a trusted source before applying review outputs.",
            "",
        ]
    )

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def _default_review_paths(processed_dir: Path) -> list[Path]:
    review_packs_dir = processed_dir / "review_packs"
    paths = sorted(review_packs_dir.glob("*.yaml")) if review_packs_dir.exists() else []
    paths.extend(
        [
            processed_dir / "review_ready_decisions.yaml",
            processed_dir / "accepted_review_ready_claims.jsonl",
            processed_dir / "rejected_review_ready_claims.jsonl",
            processed_dir / "needs_edit_review_ready_claims.jsonl",
        ]
    )
    return paths


def _load_yaml_items(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    if not isinstance(payload, dict):
        return []

    if isinstance(payload.get("items"), list):
        items: list[dict[str, Any]] = []
        for item in payload["items"]:
            if isinstance(item, dict):
                items.append(dict(item))
        return items

    if isinstance(payload.get("decisions"), dict):
        items = []
        for claim_id, entry in payload["decisions"].items():
            if isinstance(entry, dict):
                item = dict(entry)
                item.setdefault("claim_id", claim_id)
                items.append(item)
        return items

    return []


def _load_jsonl_items(path: Path) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            payload = json.loads(line)
            if isinstance(payload, dict):
                items.append(payload)
    return items


def _normalize_optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text if text else None
