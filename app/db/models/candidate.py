"""
TalentForge AI — Candidate Database Model
==========================================
Defines the Candidate model, enums, and relationships.
"""

from __future__ import annotations

import enum
import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.company import Company
    from app.db.models.resume import Resume


class CandidateStatus(str, enum.Enum):
    APPLIED = "applied"
    SCREENED = "screened"
    SHORTLISTED = "shortlisted"
    INTERVIEWING = "interviewing"
    OFFERED = "offered"
    HIRED = "hired"
    REJECTED = "rejected"


class Candidate(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Candidate profiles, matching status, and scoring metrics.
    Tied to a Company (tenant) and a Resume upload.
    """

    __tablename__ = "candidates"

    __table_args__ = (
        CheckConstraint(
            "match_score >= 0.0 AND match_score <= 100.0",
            name="chk_candidates_match_score",
        ),
        Index("ix_candidates_company_status", "company_id", "status"),
        Index("ix_candidates_company_email", "company_id", "email"),
        Index("ix_candidates_company_created_at", "company_id", "created_at"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Tenant company identifier",
    )
    first_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Extracted candidate first name",
    )
    last_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Extracted candidate last name",
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
        comment="Extracted candidate email address",
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Extracted candidate phone number",
    )
    status: Mapped[CandidateStatus] = mapped_column(
        Enum(CandidateStatus, name="candidate_status_enum"),
        nullable=False,
        default=CandidateStatus.APPLIED,
        index=True,
        comment="Application status (applied, screened, shortlisted, interviewing, offered, hired, rejected)",
    )
    experience_years: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 1),
        nullable=True,
        comment="Parsed candidate experience in years",
    )
    education: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
        comment="Parsed academic profile summary",
    )
    current_role: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True,
        comment="Parsed current job title",
    )
    # JSONB columns
    skills: Mapped[Optional[list[str]]] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="List of parsed skills (JSONB)",
    )
    match_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="AI Job Description match score (0.00 - 100.00)",
    )
    scorecard_json: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        comment="Detailed AI assessment metrics (JSONB)",
    )
    suggested_questions: Mapped[Optional[list[str]]] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="AI-suggested candidate interview questions (JSONB)",
    )
    interview_invitation_text: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
        comment="AI-generated interview invitation email draft",
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
    company: Mapped[Company] = relationship("Company", back_populates="candidates")
    resume: Mapped[Optional[Resume]] = relationship(
        "Resume",
        back_populates="candidate",
        cascade="all, delete-orphan",
        uselist=False,
    )

    def __repr__(self) -> str:
        return f"<Candidate id={self.id} email={self.email!r} status={self.status!r}>"
