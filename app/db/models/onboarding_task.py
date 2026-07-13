"""
TalentForge AI — Onboarding Task Database Model
===============================================
Defines the OnboardingTask model, enums, and relationships.
"""

from __future__ import annotations

import enum
import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.company import Company
    from app.db.models.onboarding_plan import OnboardingPlan


class OnboardingTaskCategory(str, enum.Enum):
    SCHEDULE = "schedule"
    TASK = "task"
    GOAL = "goal"
    DOCUMENT = "document"
    TOOL = "tool"
    MEETING = "meeting"


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class OnboardingTask(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    OnboardingTask represents individual checklist tasks assigned during onboarding.
    Tied to a Company (tenant) and OnboardingPlan.
    """

    __tablename__ = "onboarding_tasks"

    __table_args__ = (
        # Composite B-tree indexes
        Index("ix_onboarding_tasks_company_plan", "company_id", "plan_id"),
        Index("ix_onboarding_tasks_company_status", "company_id", "status"),
        Index("ix_onboarding_tasks_company_created", "company_id", "created_at"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Tenant company identifier",
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("onboarding_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Parent onboarding plan identifier",
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Task title",
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Task description",
    )
    category: Mapped[OnboardingTaskCategory] = mapped_column(
        Enum(OnboardingTaskCategory, name="onboarding_task_category_enum"),
        nullable=False,
        index=True,
        comment="Task category type",
    )
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, name="task_status_enum"),
        nullable=False,
        default=TaskStatus.PENDING,
        index=True,
        comment="Task execution status",
    )
    due_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        comment="Task deadline date",
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when task was marked completed",
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
        "Company", back_populates="onboarding_tasks"
    )
    plan: Mapped[OnboardingPlan] = relationship(
        "OnboardingPlan", back_populates="tasks"
    )

    def __repr__(self) -> str:
        return f"<OnboardingTask id={self.id} plan_id={self.plan_id} title={self.title!r} status={self.status}>"
