"""
TalentForge AI — AI Cache Database Model
=========================================
Caches repeatable generative LLM responses based on deterministic key hashing.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.company import Company


class AICache(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    AI response cache table.
    Stores prompt outputs mapped by SHA-256 cache key.
    """

    __tablename__ = "ai_responses_cache"

    __table_args__ = (
        # Tenant-scoped cache key uniqueness
        UniqueConstraint(
            "company_id",
            "cache_key",
            name="uq_ai_responses_cache_key",
        ),
        # Composite B-Tree index for tenant cache expiration evictions
        Index(
            "ix_ai_responses_cache_company_expires",
            "company_id",
            "expires_at",
        ),
        # Positive bounds check constraint
        CheckConstraint(
            "token_count >= 0",
            name="chk_ai_cache_tokens",
        ),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        comment="Tenant company identifier",
    )
    cache_key: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="SHA-256 hash of normalized request variables",
    )
    prompt_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="SHA-256 hash of the system prompt template",
    )
    task_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="AI task type alias name",
    )
    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Model provider key (e.g. nvidia)",
    )
    model_used: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="LLM model string representation",
    )
    response_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Raw generated LLM response",
    )
    token_count: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Output tokens count approximation",
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Cache entry expiration timestamp",
    )

    # Relationships
    company: Mapped[Company] = relationship("Company", back_populates="ai_caches")
