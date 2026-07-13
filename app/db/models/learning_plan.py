"""
TalentForge AI — Learning Plan Database Model
=============================================
Defines the LearningPlan model, enums, and relationships.
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
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.company import Company
    from app.db.models.employee import Employee
    from app.db.models.training_record import TrainingRecord
    from app.db.models.user import User


class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class LearningPlan(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    LearningPlan maps career path readiness, missing skills, and AI learning plans.
    Supports self-referential versioning and human validation audit fields.
    """

    __tablename__ = "learning_plans"

    __table_args__ = (
        CheckConstraint(
            "readiness_score >= 0.00 AND readiness_score <= 100.00",
            name="chk_learning_plans_readiness",
        ),
        # Composite B-tree indexes
        Index("ix_learning_plans_company_employee", "company_id", "employee_id"),
        Index("ix_learning_plans_company_created", "company_id", "created_at"),
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
        comment="Employee target for skill path recommendations",
    )
    current_role: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        comment="Employee's current designation",
    )
    target_role: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        comment="Designation being recommended for learning path",
    )
    readiness_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        comment="Readiness score locally/analytically generated",
    )
    skill_gap_analysis: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        comment="List of missing competencies and priorities",
    )
    learning_path_json: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        comment="Detailed timeline, certification guides, and materials",
    )
    estimated_roi: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Estimated training business ROI details",
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
        ForeignKey("learning_plans.id", ondelete="SET NULL"),
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
        comment="User ID who reviewed the learning plan",
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
    company: Mapped[Company] = relationship("Company", back_populates="learning_plans")
    employee: Mapped[Employee] = relationship(
        "Employee", back_populates="learning_plans"
    )
    reviewer: Mapped[Optional[User]] = relationship("User")
    previous_version: Mapped[Optional[LearningPlan]] = relationship(
        "LearningPlan",
        remote_side="LearningPlan.id",
        backref="next_versions",
    )
    training_records: Mapped[list[TrainingRecord]] = relationship(
        "TrainingRecord",
        back_populates="plan",
    )

    def __repr__(self) -> str:
        return f"<LearningPlan id={self.id} employee_id={self.employee_id} target={self.target_role!r} version={self.version_number}>"
