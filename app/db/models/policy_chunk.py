"""
TalentForge AI — Policy Chunk Database Model
============================================
Defines the PolicyChunk model and relationships, including pgvector storage.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any, Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.company import Company
    from app.db.models.policy_document import PolicyDocument


class PolicyChunk(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    PolicyChunk represents a parsed segment of an HR policy document.
    Stores the semantic content and vector embeddings for RAG chatbot Q&A.
    """

    __tablename__ = "policy_chunks"

    __table_args__ = (
        # Unique chunk index mapping per tenant document
        UniqueConstraint(
            "company_id",
            "document_id",
            "chunk_index",
            name="uq_policy_chunks_index",
        ),
        # Composite B-tree index for tenant document chunks list
        Index(
            "ix_policy_chunks_company_document",
            "company_id",
            "document_id",
        ),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Tenant company identifier",
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("policy_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Parent policy document identifier",
    )
    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="0-indexed position order of the chunk in the document",
    )
    section_title: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True,
        comment="Section header / title where chunk belongs",
    )
    page_number: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Origin page number reference for citations",
    )
    token_count: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Word count/token count approximation of content",
    )
    content: Mapped[str] = mapped_column(
        String,
        nullable=False,
        comment="Clean text contents of this chunk",
    )
    # pgvector embedding representation
    embedding: Mapped[list[float]] = mapped_column(
        Vector(1024),
        nullable=False,
        comment="1024-dimension vector embedding array",
    )
    # Flexible JSONB field for chunk-level metadata
    metadata_json: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        comment="Additional chunk-specific metadata details",
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
    company: Mapped[Company] = relationship("Company")
    document: Mapped[PolicyDocument] = relationship(
        "PolicyDocument", back_populates="chunks"
    )

    def __repr__(self) -> str:
        return f"<PolicyChunk id={self.id} document_id={self.document_id} chunk_index={self.chunk_index}>"
