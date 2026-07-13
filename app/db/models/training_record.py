"""
TalentForge AI — Training Record Database Model
===============================================
Defines the TrainingRecord model, enums, and relationships.
"""

from __future__ import annotations

import enum
import uuid
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.company import Company
    from app.db.models.employee import Employee
    from app.db.models.learning_plan import LearningPlan


class TrainingStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXPIRED = "expired"


class TrainingRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    TrainingRecord tracks certification progress, costs, and completed skills.
    Tied to a Company (tenant), Employee, and optionally a LearningPlan.
    """

    __tablename__ = "training_records"

    __table_args__ = (
        CheckConstraint(
            "progress_percent >= 0.00 AND progress_percent <= 100.00",
            name="chk_training_records_progress",
        ),
        CheckConstraint(
            "cost >= 0.00",
            name="chk_training_records_cost",
        ),
        # Composite B-tree indexes
        Index("ix_training_records_company_employee", "company_id", "employee_id"),
        Index("ix_training_records_company_plan", "company_id", "plan_id"),
        Index("ix_training_records_company_status", "company_id", "status"),
        Index("ix_training_records_company_created", "company_id", "created_at"),
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
        comment="Employee enrolled in training",
    )
    plan_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("learning_plans.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Parent learning plan recommended pathway",
    )
    course_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Course display name",
    )
    provider: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Platform course host provider (e.g. Coursera)",
    )
    skill_targeted: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Competence targeted by training",
    )
    status: Mapped[TrainingStatus] = mapped_column(
        Enum(TrainingStatus, name="training_status_enum"),
        nullable=False,
        default=TrainingStatus.NOT_STARTED,
        index=True,
        comment="Current training record state",
    )
    progress_percent: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="In-progress percent computed locally",
    )
    cost: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Cost of enrolled training program",
    )
    started_at: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        comment="Start date of training course",
    )
    completed_at: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        comment="Completion date of training course",
    )
    certificate_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Link to course completion certification asset",
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Soft-delete logical exclusion flag",
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
        "Company", back_populates="training_records"
    )
    employee: Mapped[Employee] = relationship(
        "Employee", back_populates="training_records"
    )
    plan: Mapped[Optional[LearningPlan]] = relationship(
        "LearningPlan", back_populates="training_records"
    )

    def __repr__(self) -> str:
        return f"<TrainingRecord id={self.id} course_name={self.course_name!r} status={self.status}>"
