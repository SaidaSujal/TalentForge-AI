"""create_ai_and_system_tables

Revision ID: 0007
Revises: e61edd53de79
Create Date: 2026-07-10 08:53:20.391761+00:00
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

import alembic.op as op

# revision identifiers, used by Alembic.
revision: str = "0007"
down_revision: Union[str, None] = "e61edd53de79"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Explicit ENUM declarations with create_type=False
export_type_enum = postgresql.ENUM(
    "PDF",
    "CSV",
    "EXCEL",
    "DOCX",
    "TXT",
    name="export_type_enum",
    create_type=False,
)

export_status_enum = postgresql.ENUM(
    "PENDING",
    "PROCESSING",
    "COMPLETED",
    "FAILED",
    name="export_status_enum",
    create_type=False,
)


def upgrade() -> None:
    # 1. Create custom enum types in database
    export_type_enum.create(op.get_bind(), checkfirst=True)
    export_status_enum.create(op.get_bind(), checkfirst=True)

    # 2. Create ai_responses_cache table
    op.create_table(
        "ai_responses_cache",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("cache_key", sa.String(length=64), nullable=False),
        sa.Column("prompt_hash", sa.String(length=64), nullable=False),
        sa.Column("task_type", sa.String(length=50), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("model_used", sa.String(length=100), nullable=False),
        sa.Column("response_text", sa.Text(), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "company_id", "cache_key", name="uq_ai_responses_cache_key"
        ),
        sa.CheckConstraint("token_count >= 0", name="chk_ai_cache_tokens"),
    )
    # Composite index for cache expiry
    op.create_index(
        "ix_ai_responses_cache_company_expires",
        "ai_responses_cache",
        ["company_id", "expires_at"],
    )

    # 3. Create ai_invocation_histories table
    op.create_table(
        "ai_invocation_histories",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=True),
        sa.Column("request_id", sa.String(length=100), nullable=True),
        sa.Column("module", sa.String(length=50), nullable=False),
        sa.Column("task_type", sa.String(length=50), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("model_used", sa.String(length=100), nullable=False),
        sa.Column("prompt_template_name", sa.String(length=100), nullable=False),
        sa.Column("prompt_hash", sa.String(length=64), nullable=False),
        sa.Column("input_summary", sa.String(length=255), nullable=False),
        sa.Column(
            "input_metadata_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("response_text", sa.Text(), nullable=False),
        sa.Column("prompt_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "completion_tokens", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("total_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column(
            "estimated_cost",
            sa.Numeric(precision=10, scale=6),
            nullable=False,
            server_default="0.00",
        ),
        sa.Column("cache_hit", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "prompt_tokens >= 0 AND completion_tokens >= 0 AND total_tokens >= 0",
            name="chk_ai_invocation_tokens_positive",
        ),
        sa.CheckConstraint(
            "estimated_cost >= 0.00", name="chk_ai_invocation_cost_positive"
        ),
        sa.CheckConstraint("latency_ms >= 0", name="chk_ai_invocation_latency"),
        sa.CheckConstraint(
            "total_tokens = prompt_tokens + completion_tokens",
            name="chk_ai_invocation_tokens_total",
        ),
    )
    # Composite indexes
    op.create_index(
        "ix_ai_invocation_company_task_created",
        "ai_invocation_histories",
        ["company_id", "task_type", "created_at"],
    )
    op.create_index(
        "ix_ai_invocation_company_user",
        "ai_invocation_histories",
        ["company_id", "user_id"],
    )
    op.create_index(
        "ix_ai_invocation_company_cache_hit",
        "ai_invocation_histories",
        ["company_id", "cache_hit"],
    )

    # 4. Create audit_logs table
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=True),
        sa.Column("module", sa.String(length=50), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=True),
        sa.Column("entity_id", sa.String(length=100), nullable=True),
        sa.Column(
            "metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_audit_logs_company_action_created",
        "audit_logs",
        ["company_id", "action", "created_at"],
    )
    op.create_index(
        "ix_audit_logs_company_entity",
        "audit_logs",
        ["company_id", "entity_type", "entity_id"],
    )

    # 5. Create export_jobs table
    op.create_table(
        "export_jobs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=True),
        sa.Column("module_scope", sa.String(length=50), nullable=False),
        sa.Column("export_type", export_type_enum, nullable=False),
        sa.Column(
            "status", export_status_enum, nullable=False, server_default="PENDING"
        ),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column("storage_path", sa.String(length=500), nullable=True),
        sa.Column("download_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.String(length=500), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("file_size_bytes >= 0", name="chk_export_jobs_size"),
        sa.CheckConstraint("download_count >= 0", name="chk_export_jobs_downloads"),
    )
    op.create_index(
        "ix_export_jobs_company_status",
        "export_jobs",
        ["company_id", "status"],
    )
    op.create_index(
        "ix_export_jobs_company_created",
        "export_jobs",
        ["company_id", "created_at"],
    )


def downgrade() -> None:
    # 1. Drop tables in reverse dependency order
    op.drop_table("export_jobs")
    op.drop_table("audit_logs")
    op.drop_table("ai_invocation_histories")
    op.drop_table("ai_responses_cache")

    # 2. Drop custom enum types from database
    export_status_enum.drop(op.get_bind(), checkfirst=True)
    export_type_enum.drop(op.get_bind(), checkfirst=True)
