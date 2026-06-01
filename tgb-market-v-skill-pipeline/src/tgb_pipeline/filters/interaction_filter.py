"""Heuristics for retaining target-author interactions from raw comments."""

from __future__ import annotations

import hashlib
import re

from tgb_pipeline.models import AuthorRole, Comment, Interaction, InteractionType

LOW_VALUE_TOKENS = {
    "谢谢",
    "感谢",
    "点赞",
    "666",
    "哈哈",
    "新年快乐",
    "表情",
}


def filter_comments_for_corpus(
    comments: list[Comment],
    *,
    target_author: str,
    focus_member_aliases: list[str],
) -> tuple[list[Comment], list[Interaction]]:
    kept_comments: list[Comment] = []
    interactions: list[Interaction] = []
    normalized_target = _normalize(target_author)
    focus_aliases = {_normalize(alias) for alias in focus_member_aliases if alias}

    for index, comment in enumerate(comments):
        normalized_text = _normalize(comment.content_text or comment.raw_content)
        if comment.author_role == AuthorRole.TARGET:
            kept_comments.append(_mark_comment(comment, "target_author_comment", False))
            continue
        if comment.author_role == AuthorRole.AOCH:
            continue
        if comment.author_role == AuthorRole.UNKNOWN:
            continue

        if _is_low_value(normalized_text) and _normalize(comment.author_name) not in focus_aliases:
            comment = comment.copy(
                update={"raw": {**comment.raw, "low_value": True, "filter_reason": "low_value"}}
            )
            continue

        keep_reason = _member_keep_reason(comments, index, normalized_target)
        if not keep_reason:
            continue
        kept_comments.append(_mark_comment(comment, keep_reason, True))

    target_comments = [comment for comment in kept_comments if comment.author_role == AuthorRole.TARGET]
    for target_comment in target_comments:
        related = [target_comment]
        for candidate in kept_comments:
            if candidate.author_role != AuthorRole.MEMBER:
                continue
            if candidate.page_num == target_comment.page_num and abs((candidate.page_position or 0) - (target_comment.page_position or 0)) <= 1:
                related.append(candidate)
        if len(related) < 2:
            continue
        interaction = _build_interaction(target_comment.article_id, related)
        interactions.append(interaction)
    return kept_comments, interactions


def _member_keep_reason(comments: list[Comment], index: int, normalized_target: str) -> str | None:
    comment = comments[index]
    text = _normalize(comment.content_text or comment.raw_content)
    if normalized_target and normalized_target in text:
        return "mentions_target_author"

    previous_comment = comments[index - 1] if index > 0 else None
    next_comment = comments[index + 1] if index + 1 < len(comments) else None
    if previous_comment and previous_comment.author_role == AuthorRole.TARGET:
        return "adjacent_to_target_author_reply"
    if next_comment and next_comment.author_role == AuthorRole.TARGET:
        if "?" in (comment.content_text or comment.raw_content) or "吗" in (comment.content_text or comment.raw_content):
            return "question_answer_window"
        return "adjacent_to_target_author_reply"
    return None


def _build_interaction(article_id: str, comments: list[Comment]) -> Interaction:
    member_names = sorted({comment.author_name for comment in comments})
    comment_ids = [comment.comment_id for comment in comments]
    digest = hashlib.sha256(f"{article_id}:{'|'.join(comment_ids)}".encode("utf-8")).hexdigest()
    return Interaction(
        interaction_id=f"interaction-{digest[:16]}",
        article_id=article_id,
        interaction_type=InteractionType.REPLY,
        actor_name=comments[0].author_name,
        target_name=comments[-1].author_name,
        comment_id=comments[0].comment_id,
        related_comment_id=comments[-1].comment_id,
        member_names=member_names,
        comment_ids=comment_ids,
        keep_reason="target_author_interaction_window",
        occurred_at=comments[0].published_at,
        raw_content="\n".join(filter(None, (comment.content_text for comment in comments))),
        raw={"filter_reason": "target_author_interaction_window"},
    )


def _mark_comment(comment: Comment, keep_reason: str, target_author_interacted: bool) -> Comment:
    return comment.copy(
        update={
            "keep_reason": keep_reason,
            "target_author_interacted": target_author_interacted,
            "raw": {**comment.raw, "filter_reason": keep_reason},
        }
    )


def _is_low_value(text: str) -> bool:
    stripped = re.sub(r"[^\w\u4e00-\u9fff]+", "", text)
    return not stripped or stripped in {_normalize(token) for token in LOW_VALUE_TOKENS}


def _normalize(value: str | None) -> str:
    return "".join((value or "").split()).casefold()
