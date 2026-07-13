"""
TalentForge AI — Job Description Database Model
===============================================
Defines the JobDescription model, enums, and relationships.
"""

from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import Boolean, Enum, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.db.models.employee import ExperienceLevel

if TYPE_CHECKING:
    from app.db.models.company import Company


class EmploymentType(str, enum.Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"


class JobDescription(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Generated and optimized job descriptions, requirements, and variants.
    Tied to a Company (tenant).
    """

    __tablename__ = "job_descriptions"

    __table_args__ = (
        Index("ix_job_descriptions_company_title", "company_id", "title"),
        Index("ix_job_descriptions_company_department", "company_id", "department"),
        Index("ix_job_descriptions_company_jd_hash", "company_id", "jd_hash"),
        Index("ix_job_descriptions_company_created_at", "company_id", "created_at"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Tenant company identifier",
    )
    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
        comment="Job title",
    )
    department: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Department name",
    )
    experience_level: Mapped[ExperienceLevel] = mapped_column(
        Enum(ExperienceLevel, name="experience_level_enum", inherit_schema=True),
        nullable=False,
        comment="Required experience level (junior, mid, senior, lead, director)",
    )
    location: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Work location (e.g. city, state, or remote location)",
    )
    employment_type: Mapped[Optional[EmploymentType]] = mapped_column(
        Enum(EmploymentType, name="employment_type_enum"),
        nullable=True,
        comment="Employment commitment type (full_time, part_time, contract, internship)",
    )
    salary_range: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="AI-suggested or manual salary range details",
    )
    job_description_text: Mapped[str] = mapped_column(
        String,
        nullable=False,
        comment="Full generated markdown job description text",
    )
    # JSONB columns
    required_skills: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        comment="List of required skills (JSONB)",
    )
    preferred_skills: Mapped[Optional[list[str]]] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="List of preferred skills (JSONB)",
    )
    responsibilities: Mapped[Optional[list[str]]] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="Detailed list of responsibilities (JSONB)",
    )
    requirements: Mapped[Optional[list[str]]] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="Detailed list of hiring requirements (JSONB)",
    )
    benefits: Mapped[Optional[list[str]]] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="Detailed list of employment benefits (JSONB)",
    )
    ats_keywords: Mapped[Optional[list[str]]] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="Extracted ATS keywords for search optimization (JSONB)",
    )
    variants: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        comment="Generated description variants (e.g., linkedin_post, naukri_summary, internal_note) (JSONB)",
    )
    jd_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        comment="SHA-256 hash of normalized parameters for JD caching",
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
        "Company", back_populates="job_descriptions"
    )

    def __repr__(self) -> str:
        return f"<JobDescription id={self.id} title={self.title!r} department={self.department!r}>"
