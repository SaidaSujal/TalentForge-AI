"""create policy tables

Revision ID: 0005_create_policy_tables
Revises: 0004_create_hr_foundation_tables
Create Date: 2026-07-08 12:00:00.000000+00:00
"""

from __future__ import annotations

import re
from typing import Sequence, Union

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

import alembic.op as op

# revision identifiers, used by Alembic.
revision: str = "0005_create_policy_tables"
down_revision: Union[str, None] = "0004_create_hr_foundation_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Explicit ENUM declaration with create_type=False
policy_document_status_enum = postgresql.ENUM(
    "UPLOADED",
    "INDEXED",
    "FAILED",
    "ARCHIVED",
    name="policy_document_status_enum",
    create_type=False,
)


def upgrade() -> None:
    # ── Custom Postgres Enum Type ─────────────────────────────────────────────
    policy_document_status_enum.create(op.get_bind(), checkfirst=True)

    # ── policy_documents ──────────────────────────────────────────────────────
    op.create_table(
        "policy_documents",
        sa.Column(
            "company_id", sa.UUID(), nullable=False, comment="Tenant company identifier"
        ),
        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False,
            comment="Display name of the document",
        ),
        sa.Column(
            "description",
            sa.String(length=500),
            nullable=True,
            comment="Document summary / description",
        ),
        sa.Column(
            "category",
            sa.String(length=100),
            nullable=False,
            comment="Document category classification (e.g., Compliance, Benefits, Security)",
        ),
        sa.Column(
            "status",
            policy_document_status_enum,
            nullable=False,
            comment="Processing status of the document",
        ),
        sa.Column(
            "file_name",
            sa.String(length=255),
            nullable=False,
            comment="Original uploaded filename",
        ),
        sa.Column(
            "file_path",
            sa.String(length=500),
            nullable=True,
            comment="Temporary file path reference, cleared post-parsing",
        ),
        sa.Column(
            "file_size", sa.Integer(), nullable=False, comment="File size in bytes"
        ),
        sa.Column(
            "mime_type",
            sa.String(length=100),
            nullable=False,
            comment="MIME type classification",
        ),
        sa.Column(
            "document_hash",
            sa.String(length=64),
            nullable=False,
            comment="SHA-256 hash of document binary content",
        ),
        sa.Column(
            "chunk_count",
            sa.Integer(),
            nullable=False,
            comment="Total number of chunks generated",
        ),
        sa.Column(
            "indexed_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Timestamp when document chunks were successfully embedded",
        ),
        sa.Column(
            "error_message",
            sa.String(),
            nullable=True,
            comment="Error message detailing parsing/indexing failure description",
        ),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            nullable=False,
            comment="Soft-delete logical exclusion flag",
        ),
        sa.Column(
            "created_by",
            sa.UUID(),
            nullable=True,
            comment="User ID who created the record",
        ),
        sa.Column(
            "updated_by",
            sa.UUID(),
            nullable=True,
            comment="User ID who last updated the record",
        ),
        sa.Column(
            "id",
            sa.UUID(),
            nullable=False,
            comment="Universally unique record identifier",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Record creation timestamp (UTC)",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Record last-update timestamp (UTC)",
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_policy_documents_company_hash",
        "policy_documents",
        ["company_id", "document_hash"],
        unique=False,
    )
    op.create_index(
        "ix_policy_documents_document_hash",
        "policy_documents",
        ["document_hash"],
        unique=False,
    )

    # Partial unique index for active document name per tenant
    op.create_index(
        "uq_policy_documents_active_name",
        "policy_documents",
        ["company_id", "name"],
        unique=True,
        postgresql_where=sa.text("is_deleted = false"),
    )

    # Partial unique index for active document hash per tenant
    op.create_index(
        "uq_policy_documents_active_hash",
        "policy_documents",
        ["company_id", "document_hash"],
        unique=True,
        postgresql_where=sa.text("is_deleted = false"),
    )

    # ── policy_chunks ─────────────────────────────────────────────────────────
    op.create_table(
        "policy_chunks",
        sa.Column(
            "company_id", sa.UUID(), nullable=False, comment="Tenant company identifier"
        ),
        sa.Column(
            "document_id",
            sa.UUID(),
            nullable=False,
            comment="Parent policy document identifier",
        ),
        sa.Column(
            "chunk_index",
            sa.Integer(),
            nullable=False,
            comment="0-indexed position order of the chunk in the document",
        ),
        sa.Column(
            "section_title",
            sa.String(length=150),
            nullable=True,
            comment="Section header / title where chunk belongs",
        ),
        sa.Column(
            "page_number",
            sa.Integer(),
            nullable=True,
            comment="Origin page number reference for citations",
        ),
        sa.Column(
            "token_count",
            sa.Integer(),
            nullable=True,
            comment="Word count/token count approximation of content",
        ),
        sa.Column(
            "content",
            sa.String(),
            nullable=False,
            comment="Clean text contents of this chunk",
        ),
        sa.Column(
            "embedding",
            Vector(1024),
            nullable=False,
            comment="1024-dimension vector embedding array",
        ),
        sa.Column(
            "metadata_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Additional chunk-specific metadata details",
        ),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            nullable=False,
            comment="Soft-delete logical exclusion flag",
        ),
        sa.Column(
            "created_by",
            sa.UUID(),
            nullable=True,
            comment="User ID who created the record",
        ),
        sa.Column(
            "updated_by",
            sa.UUID(),
            nullable=True,
            comment="User ID who last updated the record",
        ),
        sa.Column(
            "id",
            sa.UUID(),
            nullable=False,
            comment="Universally unique record identifier",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Record creation timestamp (UTC)",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Record last-update timestamp (UTC)",
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["document_id"], ["policy_documents.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "company_id", "document_id", "chunk_index", name="uq_policy_chunks_index"
        ),
    )
    op.create_index(
        "ix_policy_chunks_company_document",
        "policy_chunks",
        ["company_id", "document_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_policy_chunks_company_id"),
        "policy_chunks",
        ["company_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_policy_chunks_document_id"),
        "policy_chunks",
        ["document_id"],
        unique=False,
    )

    # ── Dynamic pgvector Index Fallback Strategy ──────────────────────────────
    # HNSW index is supported on pgvector >= 0.5.0. IVFFlat on pgvector >= 0.2.0.
    # Fallback to IVFFlat or skip if unsupported.
    conn = op.get_bind()
    res = conn.execute(
        sa.text("SELECT extversion FROM pg_extension WHERE extname = 'vector';")
    )
    row = res.fetchone()
    if row:
        version_str = row[0]
        version_digits = [int(x) for x in re.findall(r"\d+", version_str)]
        if version_digits >= [0, 5, 0]:
            # Use HNSW
            conn.execute(
                sa.text(
                    "CREATE INDEX ix_policy_chunks_embedding_hnsw ON policy_chunks "
                    "USING hnsw (embedding vector_cosine_ops);"
                )
            )
        elif version_digits >= [0, 2, 0]:
            # Use IVFFlat
            conn.execute(
                sa.text(
                    "CREATE INDEX ix_policy_chunks_embedding_ivfflat ON policy_chunks "
                    "USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);"
                )
            )
        else:
            # Skip similarity index on vector versions < 0.2.0
            pass


def downgrade() -> None:
    # Drop vector indexes first
    op.execute("DROP INDEX IF EXISTS ix_policy_chunks_embedding_hnsw;")
    op.execute("DROP INDEX IF EXISTS ix_policy_chunks_embedding_ivfflat;")

    op.drop_index(op.f("ix_policy_chunks_document_id"), table_name="policy_chunks")
    op.drop_index(op.f("ix_policy_chunks_company_id"), table_name="policy_chunks")
    op.drop_index("ix_policy_chunks_company_document", table_name="policy_chunks")
    op.drop_table("policy_chunks")

    op.drop_index("uq_policy_documents_active_hash", table_name="policy_documents")
    op.drop_index("uq_policy_documents_active_name", table_name="policy_documents")
    op.drop_index("ix_policy_documents_document_hash", table_name="policy_documents")
    op.drop_index("ix_policy_documents_company_hash", table_name="policy_documents")
    op.drop_table("policy_documents")

    policy_document_status_enum.drop(op.get_bind(), checkfirst=True)
