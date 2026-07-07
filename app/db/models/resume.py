"""
TalentForge AI — Resume Database Model
======================================
Defines the Resume model and relationships.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.candidate import Candidate
    from app.db.models.company import Company


class Resume(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Metadata and raw text content extracted from uploaded candidate resume files.
    Tied to a Company (tenant) and a specific Candidate profile.
    """

    __tablename__ = "resumes"

    __table_args__ = (
        UniqueConstraint("candidate_id", name="uq_resumes_candidate"),
        Index("ix_resumes_company_candidate", "company_id", "candidate_id", unique=True),
        Index("ix_resumes_company_hash", "company_id", "resume_hash"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Tenant company identifier",
    )
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Associated candidate profile identifier",
    )
    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Original uploaded file name",
    )
    file_path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Temporary file storage path reference (if retained)",
    )
    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="File size in bytes",
    )
    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="MIME type check value (PDF or DOCX)",
    )
    raw_text: Mapped[str] = mapped_column(
        String,
        nullable=False,
        comment="Extracted raw text parsed from document content",
    )
    resume_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        comment="SHA-256 hash of extracted text for screening cache checks",
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
    company: Mapped[Company] = relationship("Company", back_populates="resumes")
    candidate: Mapped[Candidate] = relationship("Candidate", back_populates="resume")

    def __repr__(self) -> str:
        return f"<Resume id={self.id} file_name={self.file_name!r}>"
