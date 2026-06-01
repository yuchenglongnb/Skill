"""Markdown corpus exports for downstream review and skill building."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from textwrap import fill

from tgb_pipeline.models import Article, Comment, ImageAsset, Interaction
from tgb_pipeline.storage import JSONLStore


def export_target_author_corpus(raw_dir: Path, processed_dir: Path) -> Path:
    articles = JSONLStore(raw_dir / "articles.jsonl", Article, "article_id").read_all()
    comments = _read_optional(raw_dir / "comments.jsonl", Comment, "comment_id")
    images = JSONLStore(raw_dir / "images.jsonl", ImageAsset, "image_id").read_all()
    target_author = articles[0].author_name if articles else ""
    target_comments_by_article = defaultdict(list)
    for comment in comments:
        if comment.author_role.value == "target" or comment.author_name == target_author:
            target_comments_by_article[comment.article_id].append(comment)
    images_by_article = defaultdict(list)
    images_by_comment = defaultdict(list)
    for image in images:
        if image.article_id:
            images_by_article[image.article_id].append(image)
        if image.comment_id:
            images_by_comment[image.comment_id].append(image)

    lines = ["# Target Author Corpus", ""]
    for article in articles:
        lines.extend(
            [
                f"## Article: {article.title}",
                "",
                f"- article_id: {article.article_id}",
                f"- published_at: {article.published_at.isoformat()}",
                f"- source_url: {article.url}",
                "",
                "### Body",
                "",
                f"> {_quote(article.raw_content)}",
                "",
                "### Article Images",
                "",
                "| image_id | source_url | before_text | after_text | review_status |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for image in images_by_article.get(article.article_id, []):
            lines.append(
                f"| {image.image_id} | {image.source_url} | {_cell(image.before_text)} | "
                f"{_cell(image.after_text)} | {image.review_status} |"
            )
        lines.extend(["", "### Target Author Comments", ""])
        for comment in target_comments_by_article.get(article.article_id, []):
            lines.extend(
                [
                    f"#### {comment.comment_id} / {comment.published_at.isoformat() if comment.published_at else ''} / "
                    f"{comment.page_num or ''} / {comment.page_position or ''}",
                    "",
                    f"> {_quote(comment.raw_content)}",
                ]
            )
            if images_by_comment.get(comment.comment_id):
                lines.extend(
                    [
                        "",
                        "| image_id | source_url | before_text | after_text | review_status |",
                        "| --- | --- | --- | --- | --- |",
                    ]
                )
                for image in images_by_comment[comment.comment_id]:
                    lines.append(
                        f"| {image.image_id} | {image.source_url} | {_cell(image.before_text)} | "
                        f"{_cell(image.after_text)} | {image.review_status} |"
                    )
            lines.append("")
    output_path = processed_dir / "target_author_corpus.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return output_path


def export_interaction_pairs(raw_dir: Path, processed_dir: Path) -> Path:
    comments_all = JSONLStore(raw_dir / "comments_all.jsonl", Comment, "comment_id").read_all()
    interactions = JSONLStore(raw_dir / "interactions.jsonl", Interaction, "interaction_id").read_all()
    comments_by_id = {comment.comment_id: comment for comment in comments_all}

    lines = ["# Interaction Pairs", ""]
    for interaction in interactions:
        lines.extend(
            [
                f"## {interaction.interaction_id}",
                "",
                f"- article_id: {interaction.article_id}",
                f"- keep_reason: {interaction.keep_reason}",
                f"- members: {interaction.member_names}",
                f"- comment_ids: {interaction.comment_ids}",
                "",
                "### Conversation",
                "",
            ]
        )
        for comment_id in interaction.comment_ids:
            comment = comments_by_id.get(comment_id)
            if not comment:
                continue
            lines.append(f"{comment.author_name}:")
            lines.append(f"> {_quote(comment.raw_content)}")
            lines.append("")
    output_path = processed_dir / "interaction_pairs.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return output_path


def export_aoch_corpus(raw_dir: Path, processed_dir: Path) -> Path:
    comments = _read_optional(raw_dir / "aoch_discussions.jsonl", Comment, "comment_id")
    images = JSONLStore(raw_dir / "images.jsonl", ImageAsset, "image_id").read_all()
    images_by_comment = defaultdict(list)
    for image in images:
        if image.comment_id:
            images_by_comment[image.comment_id].append(image)

    lines = ["# Aoch Corpus", ""]
    if not comments:
        lines.append("No Aoch comments were found in the current crawled corpus.")
    else:
        for comment in comments:
            lines.extend(
                [
                    f"## {comment.comment_id}",
                    "",
                    f"- article_id: {comment.article_id}",
                    f"- published_at: {comment.published_at.isoformat() if comment.published_at else ''}",
                    "",
                    f"> {_quote(comment.raw_content)}",
                    "",
                ]
            )
            if images_by_comment.get(comment.comment_id):
                lines.extend(
                    [
                        "| image_id | source_url | before_text | after_text | review_status |",
                        "| --- | --- | --- | --- | --- |",
                    ]
                )
                for image in images_by_comment[comment.comment_id]:
                    lines.append(
                        f"| {image.image_id} | {image.source_url} | {_cell(image.before_text)} | "
                        f"{_cell(image.after_text)} | {image.review_status} |"
                    )
                lines.append("")
    output_path = processed_dir / "aoch_corpus.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return output_path


def export_all_corpora(raw_dir: Path, processed_dir: Path) -> list[Path]:
    return [
        export_target_author_corpus(raw_dir, processed_dir),
        export_interaction_pairs(raw_dir, processed_dir),
        export_aoch_corpus(raw_dir, processed_dir),
    ]


def _quote(value: str | None) -> str:
    text = (value or "").strip()
    return fill(text, width=100, break_long_words=False, break_on_hyphens=False)


def _cell(value: str | None) -> str:
    if not value:
        return ""
    return fill(value.replace("\n", " "), width=40, break_long_words=False, break_on_hyphens=False)


def _read_optional(path: Path, model_type, key_field: str):
    if not path.exists():
        return []
    return JSONLStore(path, model_type, key_field).read_all()
