"""
TalentForge AI — Policy Document Database Model
===============================================
Defines the PolicyDocument model, enums, and relationships.
"""

from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.company import Company
    from app.db.models.policy_chunk import PolicyChunk


class PolicyDocumentStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    INDEXED = "indexed"
    FAILED = "failed"
    ARCHIVED = "archived"


class PolicyDocument(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    PolicyDocument represents metadata and processing status of uploaded HR policy files.
    Tied to a Company (tenant). Binaries are only temporary and are parsed and deleted.
    """

    __tablename__ = "policy_documents"

    __table_args__ = (
        Index(
            "ix_policy_documents_company_hash",
            "company_id",
            "document_hash",
        ),
        # Unique active document name per tenant
        Index(
            "uq_policy_documents_active_name",
            "company_id",
            "name",
            unique=True,
            postgresql_where="is_deleted = false",
        ),
        # Unique active document hash per tenant
        Index(
            "uq_policy_documents_active_hash",
            "company_id",
            "document_hash",
            unique=True,
            postgresql_where="is_deleted = false",
        ),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Tenant company identifier",
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Display name of the document",
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Document summary / description",
    )
    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Document category classification (e.g., Compliance, Benefits, Security)",
    )
    status: Mapped[PolicyDocumentStatus] = mapped_column(
        Enum(PolicyDocumentStatus, name="policy_document_status_enum"),
        nullable=False,
        default=PolicyDocumentStatus.UPLOADED,
        index=True,
        comment="Processing status of the document",
    )
    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Original uploaded filename",
    )
    file_path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Temporary file path reference, cleared post-parsing",
    )
    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="File size in bytes",
    )
    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="MIME type classification",
    )
    document_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        comment="SHA-256 hash of document binary content",
    )
    chunk_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Total number of chunks generated",
    )
    indexed_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when document chunks were successfully embedded",
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
        comment="Error message detailing parsing/indexing failure description",
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
        "Company", back_populates="policy_documents"
    )
    chunks: Mapped[list[PolicyChunk]] = relationship(
        "PolicyChunk",
        back_populates="document",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<PolicyDocument id={self.id} name={self.name!r} status={self.status!r}>"
        )
