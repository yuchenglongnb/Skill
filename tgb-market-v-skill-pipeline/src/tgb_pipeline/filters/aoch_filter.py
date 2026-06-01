"""Select comments for the dedicated Aoch corpus."""

from __future__ import annotations

from tgb_pipeline.models import AuthorRole, Comment


def select_aoch_comments(comments: list[Comment]) -> list[Comment]:
    selected: list[Comment] = []
    for comment in comments:
        if comment.author_role == AuthorRole.AOCH:
            selected.append(
                comment.copy(
                    update={
                        "keep_reason": "aoch_focus_member",
                        "raw": {
                            **comment.raw,
                            "filter_reason": "aoch_focus_member",
                            "image_asset_ids": comment.image_asset_ids,
                        },
                    }
                )
            )
    return selected

