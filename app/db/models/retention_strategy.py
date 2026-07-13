"""
TalentForge AI — Retention Strategy Database Model
===================================================
Defines the RetentionStrategy model, enums, and relationships.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.attrition_assessment import AttritionAssessment
    from app.db.models.company import Company
    from app.db.models.employee import Employee
    from app.db.models.user import User


class RetentionStrategyStatus(str, enum.Enum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"


class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class RetentionStrategy(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    RetentionStrategy represents AI recommendations and action plans for high-risk employees.
    Supports self-referential versioning and human audit validation fields.
    """

    __tablename__ = "retention_strategies"

    __table_args__ = (
        # Composite B-tree indexes
        Index("ix_retention_strategies_company_employee", "company_id", "employee_id"),
        Index("ix_retention_strategies_company_status", "company_id", "status"),
        Index("ix_retention_strategies_company_created", "company_id", "created_at"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Tenant company identifier",
    )
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("attrition_assessments.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
        comment="Linked attrition risk assessment identifier",
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Employee target for retention",
    )
    recommendations: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        comment="Structured AI suggested retention actions (benefits, salary, environment)",
    )
    action_plan: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="HR Action plan text draft",
    )
    status: Mapped[RetentionStrategyStatus] = mapped_column(
        Enum(RetentionStrategyStatus, name="retention_strategy_status_enum"),
        nullable=False,
        default=RetentionStrategyStatus.PROPOSED,
        index=True,
        comment="Execution strategy status state",
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Soft-delete logical exclusion flag",
    )

    # Versioning
    version_number: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        default=1,
        comment="Revision version counter",
    )
    previous_version_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("retention_strategies.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Self-reference to the previous revision",
    )

    # Human review fields
    human_review_required: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Flags if human validation is pending",
    )
    reviewed_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="User ID who approved the retention strategies",
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Approval timestamp",
    )
    approval_status: Mapped[ApprovalStatus] = mapped_column(
        Enum(ApprovalStatus, name="approval_status_enum"),
        nullable=False,
        default=ApprovalStatus.PENDING,
        index=True,
        comment="Verification status state",
    )

    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        comment="User ID who created the record",
    )
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        comment="User ID who last updated the record",
    )

    # Relationships
    company: Mapped[Company] = relationship(
        "Company", back_populates="retention_strategies"
    )
    assessment: Mapped[AttritionAssessment] = relationship(
        "AttritionAssessment",
        back_populates="retention_strategy",
    )
    employee: Mapped[Employee] = relationship(
        "Employee", back_populates="retention_strategies"
    )
    reviewer: Mapped[Optional[User]] = relationship("User")
    previous_version: Mapped[Optional[RetentionStrategy]] = relationship(
        "RetentionStrategy",
        remote_side="RetentionStrategy.id",
        backref="next_versions",
    )

    def __repr__(self) -> str:
        return f"<RetentionStrategy id={self.id} employee_id={self.employee_id} status={self.status} version={self.version_number}>"
