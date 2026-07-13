"""
TalentForge AI — Performance Review Database Model
==================================================
Defines the PerformanceReview model, enums, and relationships.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
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
    from app.db.models.employee import Employee
    from app.db.models.user import User


class ReviewStatus(str, enum.Enum):
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class PerformanceReview(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    PerformanceReview represents evaluations written by managers.
    Includes AI draft features, human audit fields, and self-referential versioning.
    """

    __tablename__ = "performance_reviews"

    __table_args__ = (
        CheckConstraint(
            "goals_achieved >= 0 AND total_goals >= 0 AND goals_achieved <= total_goals",
            name="chk_performance_reviews_goals",
        ),
        CheckConstraint(
            "attendance_percent >= 0.00 AND attendance_percent <= 100.00",
            name="chk_performance_reviews_attendance",
        ),
        # Composite B-tree indexes
        Index("ix_performance_reviews_company_employee", "company_id", "employee_id"),
        Index("ix_performance_reviews_company_manager", "company_id", "manager_id"),
        Index("ix_performance_reviews_company_status", "company_id", "status"),
        Index("ix_performance_reviews_company_created", "company_id", "created_at"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Tenant company identifier",
    )
    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Employee being reviewed",
    )
    manager_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Manager reviewing the employee",
    )
    review_period: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Review cycle identifier (e.g. Q1 2026, Annual 2025)",
    )
    status: Mapped[ReviewStatus] = mapped_column(
        Enum(ReviewStatus, name="review_status_enum"),
        nullable=False,
        default=ReviewStatus.DRAFT,
        index=True,
        comment="Review state status",
    )
    goals_achieved: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Number of goals met in review period",
    )
    total_goals: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Total goals set in review period",
    )
    attendance_percent: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Attendance rating percentage",
    )
    manager_observations: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Observations entered by evaluating manager",
    )
    peer_feedback: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Collated peer reviews and notes",
    )
    review_summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="AI-generated review summary draft",
    )
    rating_suggestion: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="AI rating suggestion label",
    )
    key_achievements: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="List of highlighted accomplishments",
    )
    development_areas: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Improvement priorities list",
    )
    bias_check_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="AI-generated language bias evaluation notes",
    )
    promotion_readiness: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Indicates if candidate is fit for promotion",
    )
    salary_revision_label: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Compensation revision draft recommendations",
    )
    smart_goals: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Draft list of SMART goals for next cycle",
    )
    development_plan: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Detailed employee career development path",
    )
    pip_details: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Performance Improvement Plan details if applicable",
    )
    signed_off_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when final sign-off completed",
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
        ForeignKey("performance_reviews.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Self-reference to the previous revision",
    )

    # Human-in-the-Loop Audit Fields
    human_review_required: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Flags if human approval is pending",
    )
    reviewed_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="User ID who approved the review",
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
        comment="Human approval status state",
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
        "Company", back_populates="performance_reviews"
    )
    employee: Mapped[Employee] = relationship(
        "Employee",
        foreign_keys=[employee_id],
        back_populates="performance_reviews",
    )
    manager: Mapped[Optional[Employee]] = relationship(
        "Employee",
        foreign_keys=[manager_id],
        back_populates="conducted_reviews",
    )
    reviewer: Mapped[Optional[User]] = relationship(
        "User",
        foreign_keys=[reviewed_by],
    )
    previous_version: Mapped[Optional[PerformanceReview]] = relationship(
        "PerformanceReview",
        remote_side="PerformanceReview.id",
        backref="next_versions",
    )

    def __repr__(self) -> str:
        return f"<PerformanceReview id={self.id} employee_id={self.employee_id} status={self.status} version={self.version_number}>"
