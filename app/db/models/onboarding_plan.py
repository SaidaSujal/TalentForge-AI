"""
TalentForge AI — Onboarding Plan Database Model
===============================================
Defines the OnboardingPlan model, enums, and relationships.
"""

from __future__ import annotations

import enum
import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import Boolean, CheckConstraint, Enum, ForeignKey, Index, Numeric, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.company import Company
    from app.db.models.employee import Employee
    from app.db.models.onboarding_task import OnboardingTask


class OnboardingStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    ON_TRACK = "on_track"
    BEHIND = "behind"
    COMPLETE = "complete"


class OnboardingPlan(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    OnboardingPlan represents onboarding roadmaps, welcome templates, and milestones.
    Tied to a Company (tenant) and Employee.
    """

    __tablename__ = "onboarding_plans"

    __table_args__ = (
        CheckConstraint(
            "progress_percent >= 0.00 AND progress_percent <= 100.00",
            name="chk_onboarding_plans_progress",
        ),
        # Unique active onboarding plan per employee
        Index(
            "uq_onboarding_plans_active_employee",
            "company_id",
            "employee_id",
            unique=True,
            postgresql_where="is_deleted = false",
        ),
        # Composite B-tree indexes
        Index("ix_onboarding_plans_company_status", "company_id", "status"),
        Index("ix_onboarding_plans_company_created", "company_id", "created_at"),
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
        comment="Employee being onboarded",
    )
    status: Mapped[OnboardingStatus] = mapped_column(
        Enum(OnboardingStatus, name="onboarding_status_enum"),
        nullable=False,
        default=OnboardingStatus.PENDING,
        index=True,
        comment="Onboarding progress status",
    )
    progress_percent: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Onboarding progress percentage",
    )
    welcome_email_text: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="AI-generated welcome email draft",
    )
    team_announcement_text: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="AI-generated team announcement draft",
    )
    plan_data_json: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        comment="Structured onboarding roadmap goals and milestones",
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
        "Company", back_populates="onboarding_plans"
    )
    employee: Mapped[Employee] = relationship(
        "Employee", back_populates="onboarding_plan"
    )
    tasks: Mapped[list[OnboardingTask]] = relationship(
        "OnboardingTask",
        back_populates="plan",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<OnboardingPlan id={self.id} employee_id={self.employee_id} status={self.status}>"
