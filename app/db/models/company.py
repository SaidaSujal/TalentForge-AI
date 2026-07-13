"""
TalentForge AI — Company Database Model
========================================
Defines the Company model which acts as the foundational multi-tenant anchor.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.ai_cache import AICache
    from app.db.models.ai_history import AIHistory
    from app.db.models.attrition_assessment import AttritionAssessment
    from app.db.models.audit_log import AuditLog
    from app.db.models.candidate import Candidate
    from app.db.models.employee import Employee
    from app.db.models.export_job import ExportJob
    from app.db.models.interview_kit import InterviewKit
    from app.db.models.job_description import JobDescription
    from app.db.models.learning_plan import LearningPlan
    from app.db.models.onboarding_plan import OnboardingPlan
    from app.db.models.onboarding_task import OnboardingTask
    from app.db.models.performance_review import PerformanceReview
    from app.db.models.policy_document import PolicyDocument
    from app.db.models.resume import Resume
    from app.db.models.retention_strategy import RetentionStrategy
    from app.db.models.training_record import TrainingRecord
    from app.db.models.user import User


class Company(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Tenant/company record.
    Every tenant-owned table has a foreign key pointing here.

    V1: one demo company is seeded at startup.
    Phase 10+: HR admins can create additional company records.
    """

    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Company display name",
    )
    slug: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="URL-safe company identifier",
    )
    # Flexible JSON blob for per-company feature toggles / configuration
    settings_json: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        default="{}",
        comment="JSON-encoded company-level settings",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Soft-delete flag — inactive companies are not served",
    )

    # Relationships
    users: Mapped[list[User]] = relationship(
        "User",
        back_populates="company",
        cascade="all, delete-orphan",
    )
    employees: Mapped[list[Employee]] = relationship(
        "Employee",
        back_populates="company",
        cascade="all, delete-orphan",
    )
    candidates: Mapped[list[Candidate]] = relationship(
        "Candidate",
        back_populates="company",
        cascade="all, delete-orphan",
    )
    resumes: Mapped[list[Resume]] = relationship(
        "Resume",
        back_populates="company",
        cascade="all, delete-orphan",
    )
    job_descriptions: Mapped[list[JobDescription]] = relationship(
        "JobDescription",
        back_populates="company",
        cascade="all, delete-orphan",
    )
    policy_documents: Mapped[list[PolicyDocument]] = relationship(
        "PolicyDocument",
        back_populates="company",
        cascade="all, delete-orphan",
    )
    onboarding_plans: Mapped[list[OnboardingPlan]] = relationship(
        "OnboardingPlan", back_populates="company", cascade="all, delete-orphan"
    )
    onboarding_tasks: Mapped[list[OnboardingTask]] = relationship(
        "OnboardingTask", back_populates="company", cascade="all, delete-orphan"
    )
    performance_reviews: Mapped[list[PerformanceReview]] = relationship(
        "PerformanceReview", back_populates="company", cascade="all, delete-orphan"
    )
    attrition_assessments: Mapped[list[AttritionAssessment]] = relationship(
        "AttritionAssessment", back_populates="company", cascade="all, delete-orphan"
    )
    retention_strategies: Mapped[list[RetentionStrategy]] = relationship(
        "RetentionStrategy", back_populates="company", cascade="all, delete-orphan"
    )
    learning_plans: Mapped[list[LearningPlan]] = relationship(
        "LearningPlan", back_populates="company", cascade="all, delete-orphan"
    )
    training_records: Mapped[list[TrainingRecord]] = relationship(
        "TrainingRecord", back_populates="company", cascade="all, delete-orphan"
    )
    interview_kits: Mapped[list[InterviewKit]] = relationship(
        "InterviewKit", back_populates="company", cascade="all, delete-orphan"
    )
    ai_caches: Mapped[list[AICache]] = relationship(
        "AICache", back_populates="company", passive_deletes=True
    )
    ai_histories: Mapped[list[AIHistory]] = relationship(
        "AIHistory", back_populates="company", passive_deletes=True
    )
    audit_logs: Mapped[list[AuditLog]] = relationship(
        "AuditLog", back_populates="company", passive_deletes=True
    )
    export_jobs: Mapped[list[ExportJob]] = relationship(
        "ExportJob", back_populates="company", passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<Company id={self.id} name={self.name!r}>"
