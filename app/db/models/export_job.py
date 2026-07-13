"""
TalentForge AI — Export Job Database Model
===========================================
Tracks server-side report generation (PDF, CSV) jobs and user downloads.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.company import Company
    from app.db.models.user import User


class ExportType(str, enum.Enum):
    """Supported export formats for reports."""

    PDF = "pdf"
    CSV = "csv"
    EXCEL = "excel"
    DOCX = "docx"
    TXT = "txt"


class ExportStatus(str, enum.Enum):
    """States of a background export generation job."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ExportJob(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Export job table.
    Tracks document generation requests and secure path references.
    """

    __tablename__ = "export_jobs"

    __table_args__ = (
        # Positive bounds check constraints
        CheckConstraint(
            "file_size_bytes >= 0",
            name="chk_export_jobs_size",
        ),
        CheckConstraint(
            "download_count >= 0",
            name="chk_export_jobs_downloads",
        ),
        # Composite B-Tree indexes for status and creator filtering
        Index(
            "ix_export_jobs_company_status",
            "company_id",
            "status",
        ),
        Index(
            "ix_export_jobs_company_created",
            "company_id",
            "created_at",
        ),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        comment="Tenant company identifier",
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User identifier who generated the export job",
    )
    module_scope: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Target feature module scope (e.g. attrition)",
    )
    export_type: Mapped[ExportType] = mapped_column(
        Enum(ExportType, name="export_type_enum"),
        nullable=False,
        comment="Generated report format",
    )
    status: Mapped[ExportStatus] = mapped_column(
        Enum(ExportStatus, name="export_status_enum"),
        nullable=False,
        default=ExportStatus.PENDING,
        comment="Job processing state",
    )
    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Sanitized file name generated server-side",
    )
    file_size_bytes: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Calculated report size in bytes",
    )
    storage_path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Secure internal storage path reference",
    )
    download_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="File download counter",
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Sanitized error description with no stack details",
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Deletion timestamp limit for file retention TTL",
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Soft-delete logical exclusion flag",
    )

    # Relationships
    company: Mapped[Company] = relationship("Company", back_populates="export_jobs")
    user: Mapped[Optional[User]] = relationship("User")
