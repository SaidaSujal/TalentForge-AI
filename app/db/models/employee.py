"""
TalentForge AI — Employee Database Model
=========================================
Defines the Employee model, enums, and relationships.
"""

from __future__ import annotations

import enum
import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Date, Enum, ForeignKey, Index, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, deferred, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.company import Company
    from app.db.models.user import User


class EmployeeStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    ONBOARDING = "onboarding"


class WorkMode(str, enum.Enum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    OFFICE = "office"


class ExperienceLevel(str, enum.Enum):
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    DIRECTOR = "director"


class Employee(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Employee record representing active, suspended, or terminated employees.
    Tied to a Company (tenant) and optionally a User account.
    """

    __tablename__ = "employees"

    __table_args__ = (
        UniqueConstraint("email", "company_id", name="uq_employees_email_company"),
        Index("ix_employees_company_status", "company_id", "status"),
        Index("ix_employees_company_department", "company_id", "department"),
        Index("ix_employees_company_role", "company_id", "role"),
        Index("ix_employees_company_created_at", "company_id", "created_at"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Tenant company identifier",
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        unique=True,
        nullable=True,
        index=True,
        comment="Linked application User account",
    )
    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="First name",
    )
    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Last name",
    )
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Corporate email address",
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Contact phone number",
    )
    department: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Department name",
    )
    role: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Job title / role description",
    )
    # Sensitive salary field — deferred loading by default
    salary: Mapped[Optional[Decimal]] = deferred(
        mapped_column(
            Numeric(12, 2),
            nullable=True,
            comment="Confidential salary (deferred loading)",
        )
    )
    manager_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Manager employee identifier",
    )
    status: Mapped[EmployeeStatus] = mapped_column(
        Enum(EmployeeStatus, name="employee_status_enum"),
        nullable=False,
        default=EmployeeStatus.ACTIVE,
        index=True,
        comment="Employment status (active, suspended, terminated, onboarding)",
    )
    role_enum: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Role enum representation if needed",
    )
    hire_date: Mapped[Optional[Date]] = mapped_column(
        Date,
        nullable=True,
        comment="Date of hire",
    )
    work_mode: Mapped[Optional[WorkMode]] = mapped_column(
        Enum(WorkMode, name="work_mode_enum"),
        nullable=True,
        comment="Work environment mode (remote, hybrid, office)",
    )
    experience_level: Mapped[Optional[ExperienceLevel]] = mapped_column(
        Enum(ExperienceLevel, name="experience_level_enum"),
        nullable=True,
        comment="Employee seniority level",
    )
    # JSONB field for list of skills
    current_skills: Mapped[Optional[list[str]]] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="List of current skills (JSONB)",
    )
    target_role: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Target career progression role",
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Soft-delete logical exclusion flag",
    )
    # Audit compatibility columns
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
    company: Mapped[Company] = relationship("Company", back_populates="employees")
    user: Mapped[Optional[User]] = relationship("User", back_populates="employee")
    manager: Mapped[Optional[Employee]] = relationship(
        "Employee",
        remote_side="Employee.id",
        back_populates="subordinates",
    )
    subordinates: Mapped[list[Employee]] = relationship(
        "Employee",
        back_populates="manager",
    )

    def __repr__(self) -> str:
        return f"<Employee id={self.id} email={self.email!r} role={self.role!r}>"
