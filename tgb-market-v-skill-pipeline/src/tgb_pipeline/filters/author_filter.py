"""Author normalization and role classification."""

from __future__ import annotations

from tgb_pipeline.config import TargetConfig
from tgb_pipeline.models import AuthorRole, Comment


def normalize_author_name(name: str) -> str:
    return "".join(str(name).split()).casefold()


def classify_author_role(author_name: str, target_config: TargetConfig) -> AuthorRole:
    normalized = normalize_author_name(author_name)
    if not normalized:
        return AuthorRole.UNKNOWN
    if normalized == normalize_author_name(target_config.target.author_name):
        return AuthorRole.TARGET

    aoch = target_config.aoch
    if aoch is not None:
        aliases = [aoch.name, *aoch.aliases]
        if normalized in {normalize_author_name(alias) for alias in aliases}:
            return AuthorRole.AOCH
    return AuthorRole.MEMBER


def annotate_comment_author_role(comment: Comment, target_config: TargetConfig) -> Comment:
    return comment.copy(update={"author_role": classify_author_role(comment.author_name, target_config)})

