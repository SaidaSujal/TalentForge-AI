"""
TalentForge AI — Interview Kit Database Model
=============================================
Defines the InterviewKit model, enums, and relationships.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.db.models.employee import ExperienceLevel

if TYPE_CHECKING:
    from app.db.models.company import Company
    from app.db.models.user import User


class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class InterviewKit(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    InterviewKit represents rubrics and question banks for evaluating candidates.
    Supports self-referential versioning and human validation audit fields.
    """

    __tablename__ = "interview_kits"

    __table_args__ = (
        CheckConstraint(
            "duration_minutes > 0",
            name="chk_interview_kits_duration",
        ),
        # Composite B-tree indexes
        Index(
            "ix_interview_kits_company_role_level",
            "company_id",
            "job_role",
            "experience_level",
        ),
        Index("ix_interview_kits_company_department", "company_id", "department"),
        Index("ix_interview_kits_company_created", "company_id", "created_at"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Tenant company identifier",
    )
    job_role: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        comment="Designation job role (e.g. Backend Engineer)",
    )
    department: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Department role belongs to",
    )
    experience_level: Mapped[ExperienceLevel] = mapped_column(
        Enum(ExperienceLevel, name="experience_level_enum"),
        nullable=False,
        index=True,
        comment="Target seniority level classification",
    )
    duration_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Target interview duration minutes",
    )
    key_skills: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        comment="List of skills and competence priorities assessed",
    )
    interview_structure: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Timing structure layouts",
    )
    question_bank: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        comment="Draft list of questions, expected answers, scorecard weights",
    )
    evaluation_rubric: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Structured scoring rubrics parameters",
    )
    panel_guide: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Draft panel instruction guidance notes",
    )
    is_template: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Indicates if reusable template",
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
        ForeignKey("interview_kits.id", ondelete="SET NULL"),
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
        comment="User ID who reviewed the interview kit",
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
    company: Mapped[Company] = relationship("Company", back_populates="interview_kits")
    reviewer: Mapped[Optional[User]] = relationship("User")
    previous_version: Mapped[Optional[InterviewKit]] = relationship(
        "InterviewKit",
        remote_side="InterviewKit.id",
        backref="next_versions",
    )

    def __repr__(self) -> str:
        return f"<InterviewKit id={self.id} role={self.job_role!r} level={self.experience_level} version={self.version_number}>"
