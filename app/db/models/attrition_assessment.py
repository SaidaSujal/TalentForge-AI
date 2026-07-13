"""
TalentForge AI — Attrition Assessment Database Model
=====================================================
Defines the AttritionAssessment model, enums, and relationships.
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
    Numeric,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.company import Company
    from app.db.models.employee import Employee
    from app.db.models.retention_strategy import RetentionStrategy
    from app.db.models.user import User


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class AttritionAssessment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    AttritionAssessment represents attrition risk analysis for employees.
    Supports explainable local model scores, features, and human-in-the-loop audit fields.
    """

    __tablename__ = "attrition_assessments"

    __table_args__ = (
        CheckConstraint(
            "risk_score >= 0.00 AND risk_score <= 100.00",
            name="chk_attrition_assessments_risk",
        ),
        CheckConstraint(
            "manager_satisfaction_score >= 0.0 AND manager_satisfaction_score <= 5.0",
            name="chk_attrition_assessments_satisfaction",
        ),
        # Composite B-tree indexes
        Index("ix_attrition_assessments_company_employee", "company_id", "employee_id"),
        Index("ix_attrition_assessments_company_risk", "company_id", "risk_level"),
        Index("ix_attrition_assessments_company_created", "company_id", "created_at"),
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
        comment="Employee under assessment",
    )
    risk_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        comment="Locally computed/model risk percentage",
    )
    risk_level: Mapped[RiskLevel] = mapped_column(
        Enum(RiskLevel, name="risk_level_enum"),
        nullable=False,
        default=RiskLevel.LOW,
        index=True,
        comment="Risk categorization level",
    )
    risk_factors: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Explainable feature importances (e.g. SHAP values / local metrics)",
    )
    stay_interview_questions: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="AI-generated stay interview questions list draft",
    )
    replacement_cost: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
        comment="Estimated replacement cost value",
    )
    manager_satisfaction_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(3, 1),
        nullable=True,
        comment="Manager satisfaction rating on 1-5 scale",
    )
    overtime_hours: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 1),
        nullable=True,
        comment="Average monthly overtime hours",
    )
    is_active_assessment: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Indicates if this is the active assessment cycle",
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Soft-delete logical exclusion flag",
    )

    # Human-in-the-Loop Audit Fields
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
        comment="User ID who reviewed the risk score",
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Verification timestamp",
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
        "Company", back_populates="attrition_assessments"
    )
    employee: Mapped[Employee] = relationship(
        "Employee", back_populates="attrition_assessments"
    )
    reviewer: Mapped[Optional[User]] = relationship("User")
    retention_strategy: Mapped[Optional[RetentionStrategy]] = relationship(
        "RetentionStrategy",
        back_populates="assessment",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<AttritionAssessment id={self.id} employee_id={self.employee_id} risk_level={self.risk_level} score={self.risk_score}>"
