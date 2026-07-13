"""
TalentForge AI — AI Invocation History Database Model
======================================================
Stores audit trails of generative LLM calls, costs, and token usages.
"""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.company import Company
    from app.db.models.user import User


class AIHistory(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    AI invocation history table.
    Records every LLM request and output details.
    """

    __tablename__ = "ai_invocation_histories"

    __table_args__ = (
        # Positive bounds check constraints
        CheckConstraint(
            "prompt_tokens >= 0 AND completion_tokens >= 0 AND total_tokens >= 0",
            name="chk_ai_invocation_tokens_positive",
        ),
        CheckConstraint(
            "estimated_cost >= 0.00",
            name="chk_ai_invocation_cost_positive",
        ),
        CheckConstraint(
            "latency_ms >= 0",
            name="chk_ai_invocation_latency",
        ),
        # Consistency checking check constraints
        CheckConstraint(
            "total_tokens = prompt_tokens + completion_tokens",
            name="chk_ai_invocation_tokens_total",
        ),
        # Composite B-Tree indexes (ensuring no duplicate indexes on primary fields)
        Index(
            "ix_ai_invocation_company_task_created",
            "company_id",
            "task_type",
            "created_at",
        ),
        Index(
            "ix_ai_invocation_company_user",
            "company_id",
            "user_id",
        ),
        Index(
            "ix_ai_invocation_company_cache_hit",
            "company_id",
            "cache_hit",
        ),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        comment="Tenant company identifier",
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User identifier who ran the AI request",
    )
    request_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Correlation ID mapping the FastAPI/request lifecycle",
    )
    module: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Target feature module name",
    )
    task_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="AI routing task name (e.g. jd_draft)",
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
    prompt_template_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Prompt template function name used",
    )
    prompt_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="SHA-256 hash of the compiled prompt text",
    )
    input_summary: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Redacted summary of parameters for privacy",
    )
    input_metadata_json: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        comment="Redacted operational metadata mapping details",
    )
    response_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Raw generated LLM response",
    )
    prompt_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Input prompt tokens count",
    )
    completion_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Output completion tokens count",
    )
    total_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Total tokens sum count",
    )
    latency_ms: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Execution duration in milliseconds",
    )
    estimated_cost: Mapped[Decimal] = mapped_column(
        Numeric(10, 6),
        nullable=False,
        default=Decimal("0.00"),
        comment="Calculated API call financial cost",
    )
    cache_hit: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="True if resolved from cache",
    )

    # Relationships
    company: Mapped[Company] = relationship("Company", back_populates="ai_histories")
    user: Mapped[Optional[User]] = relationship("User")
