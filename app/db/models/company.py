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
    from app.db.models.user import User
    from app.db.models.employee import Employee
    from app.db.models.candidate import Candidate
    from app.db.models.resume import Resume
    from app.db.models.job_description import JobDescription


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

    def __repr__(self) -> str:
        return f"<Company id={self.id} name={self.name!r}>"
