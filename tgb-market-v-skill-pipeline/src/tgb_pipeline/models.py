"""Core data contracts for the evidence pipeline."""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, root_validator


class AuthorRole(StrEnum):
    TARGET = "target"
    AOCH = "aoch"
    MEMBER = "member"
    UNKNOWN = "unknown"


class InteractionType(StrEnum):
    REPLY = "reply"
    MENTION = "mention"
    LIKE = "like"
    FOLLOW_UP = "follow_up"
    OTHER = "other"


class ClaimSourceType(StrEnum):
    ARTICLE = "article"
    COMMENT = "comment"
    INTERACTION = "interaction"
    IMAGE_OCR = "image_ocr"
    MIXED = "mixed"


class ClaimStatus(StrEnum):
    CANDIDATE = "candidate"
    REVIEWED = "reviewed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class PipelineModel(BaseModel):
    """Base model that rejects accidental schema drift."""

    class Config:
        extra = "forbid"
        validate_assignment = True


class ArticleIndex(PipelineModel):
    article_id: str
    title: str
    tag: str | None = None
    published_date: date
    view_count: int = 0
    reply_count: int = 0
    url: str
    mobile_url: str
    raw: dict[str, Any] = Field(default_factory=dict)


class Article(PipelineModel):
    article_id: str
    title: str
    author_name: str
    published_at: datetime
    url: str
    mobile_url: str | None = None
    tag: str | None = None
    view_count: int | None = None
    reply_count: int | None = None
    raw_content: str
    content_text: str | None = None
    image_asset_ids: list[str] = Field(default_factory=list)
    raw: dict[str, Any] = Field(default_factory=dict)


class Comment(PipelineModel):
    comment_id: str
    article_id: str
    author_name: str
    author_role: AuthorRole = AuthorRole.UNKNOWN
    published_at: datetime | None = None
    page_num: int | None = None
    page_position: int | None = None
    parent_comment_id: str | None = None
    replied_to_author_name: str | None = None
    target_author_interacted: bool = False
    keep_reason: str | None = None
    raw_content: str
    content_text: str | None = None
    image_asset_ids: list[str] = Field(default_factory=list)
    raw: dict[str, Any] = Field(default_factory=dict)

    @property
    def eligible_for_corpus(self) -> bool:
        """Keep members in the final corpus only when the target author interacted."""

        return self.author_role == AuthorRole.TARGET or self.target_author_interacted

    @property
    def is_aoch(self) -> bool:
        return self.author_role == AuthorRole.AOCH

    @property
    def eligible_for_aoch_corpus(self) -> bool:
        return self.author_role == AuthorRole.AOCH


class Interaction(PipelineModel):
    interaction_id: str
    article_id: str
    interaction_type: InteractionType
    actor_name: str
    target_name: str | None = None
    comment_id: str | None = None
    related_comment_id: str | None = None
    member_names: list[str] = Field(default_factory=list)
    comment_ids: list[str] = Field(default_factory=list)
    keep_reason: str | None = None
    occurred_at: datetime | None = None
    raw_content: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class ImageAsset(PipelineModel):
    image_id: str
    source_url: str
    page_url: str
    article_id: str | None = None
    comment_id: str | None = None
    local_path: str | None = None
    sha256: str | None = None
    mime_type: str | None = None
    width: int | None = None
    height: int | None = None
    source_type: str | None = None
    position_index: int | None = None
    before_text: str | None = None
    after_text: str | None = None
    keep_reason: str | None = None
    image_type: str | None = None
    review_status: str = "unreviewed"
    raw: dict[str, Any] = Field(default_factory=dict)

    @property
    def evidence_source(self) -> bool:
        return True

    @root_validator
    def validate_parent(cls, values: dict[str, Any]) -> dict[str, Any]:
        if not values.get("article_id") and not values.get("comment_id"):
            raise ValueError("image must belong to an article or comment")
        return values


class ImageOCR(PipelineModel):
    ocr_id: str
    image_id: str
    engine: str
    languages: list[str] = Field(default_factory=list)
    raw_text: str
    normalized_text: str | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    raw: dict[str, Any] = Field(default_factory=dict)


class CrawlError(PipelineModel):
    error_id: str
    stage: str
    article_id: str | None = None
    url: str | None = None
    error_type: str
    error_message: str
    resolved: bool = False
    resolved_at: datetime | None = None
    resolved_by: str | None = None
    resolution_note: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class CommentPageState(PipelineModel):
    state_id: str
    article_id: str
    page_num: int
    page_url: str
    status: str = "fetched"
    comments_count: int = 0
    images_count: int = 0
    discovered_last_page: int | None = None
    has_next_page: bool | None = None
    fetched_at: datetime | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class CommentArticleState(PipelineModel):
    article_id: str
    title: str | None = None
    indexed_reply_count: int = 0
    discovered_last_page: int | None = None
    fetched_pages: int = 0
    max_fetched_page: int = 0
    next_page_to_fetch: int = 1
    completed: bool = False
    max_limit_reached: bool = False
    comments_count: int = 0
    images_count: int = 0
    updated_at: datetime | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class CommentCompletionPlanItem(PipelineModel):
    article_id: str
    title: str | None = None
    next_page_to_fetch: int
    target_max_page: int
    discovered_last_page: int | None = None
    remaining_known_pages: int | None = None
    planned_pages: int
    priority: int = 0
    reason: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class CommentCompletionPlan(PipelineModel):
    plan_id: str
    generated_at: datetime
    total_items: int
    total_planned_pages: int
    items: list[CommentCompletionPlanItem] = Field(default_factory=list)
    raw: dict[str, Any] = Field(default_factory=dict)


class ArticleSeedCandidate(PipelineModel):
    candidate_id: str
    article_id: str
    title: str | None = None
    published_date: date | None = None
    url: str
    mobile_url: str
    tag: str | None = None
    source: str | None = None
    confidence: str = "candidate"
    selected: bool = False
    note: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class MethodologyClaim(PipelineModel):
    claim_id: str
    claim_text: str
    raw_excerpt: str
    source_type: ClaimSourceType
    source_ids: list[str] = Field(min_items=1)
    article_id: str | None = None
    source_title: str | None = None
    source_time: datetime | None = None
    source_author: str | None = None
    method_tags: list[str] = Field(default_factory=list)
    mentioned_tickers: list[str] = Field(default_factory=list)
    mentioned_sectors: list[str] = Field(default_factory=list)
    mentioned_concepts: list[str] = Field(default_factory=list)
    direction: str | None = None
    horizon: str | None = None
    confidence_level: str = "candidate"
    evidence_text: str | None = None
    evidence_level: str = "text_raw"
    review_status: str = "unreviewed"
    review_notes: str | None = None
    review_priority: str = "normal"
    review_bucket: str | None = None
    evidence_image_ids: list[str] = Field(default_factory=list)
    evidence_ocr_ids: list[str] = Field(default_factory=list)
    author_name: str | None = None
    status: ClaimStatus = ClaimStatus.CANDIDATE
    tags: list[str] = Field(default_factory=list)
    raw: dict[str, Any] = Field(default_factory=dict)


class ReviewPackItem(PipelineModel):
    claim_id: str
    decision: str = "unreviewed"
    reason: str | None = None
    edited_claim_text: str | None = None
    review_notes: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class ReviewPack(PipelineModel):
    pack_id: str
    title: str
    generated_at: datetime
    source_path: str
    filter_tags: list[str] = Field(default_factory=list)
    filter_articles: list[str] = Field(default_factory=list)
    filter_buckets: list[str] = Field(default_factory=list)
    max_items: int = 100
    items: list[ReviewPackItem] = Field(default_factory=list)
    raw: dict[str, Any] = Field(default_factory=dict)
