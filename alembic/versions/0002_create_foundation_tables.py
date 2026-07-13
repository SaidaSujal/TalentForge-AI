"""
TalentForge AI — Phase 1: Create Foundation Tables
===================================================
Revision ID: 0002_create_foundation_tables
Revises: 0001_enable_pgvector
Create Date: 2026-07-04

Creates the foundational tables required in Phase 1:
  - companies: multi-tenant anchor table
  - app_settings: system-level configuration

These tables have no tenant data and are safe to create before
the full HR schema is built in Phase 2.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

# revision identifiers
revision: str = "0002_create_foundation_tables"
down_revision: Union[str, None] = "0001_enable_pgvector"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create companies and app_settings tables."""

    # ── companies ─────────────────────────────────────────────────────────────
    op.create_table(
        "companies",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
            comment="Universally unique record identifier",
        ),
        sa.Column(
            "name", sa.String(255), nullable=False, comment="Company display name"
        ),
        sa.Column(
            "slug",
            sa.String(100),
            nullable=False,
            comment="URL-safe company identifier",
        ),
        sa.Column(
            "settings_json",
            sa.Text,
            nullable=True,
            server_default="{}",
            comment="JSON-encoded company-level settings",
        ),
        sa.Column(
            "is_active",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("true"),
            comment="Soft-delete flag",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            comment="Record creation timestamp (UTC)",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            comment="Record last-update timestamp (UTC)",
        ),
    )
    op.create_unique_constraint("uq_companies_slug", "companies", ["slug"])
    op.create_index("ix_companies_slug", "companies", ["slug"])
    op.create_index("ix_companies_is_active", "companies", ["is_active"])

    # ── app_settings ──────────────────────────────────────────────────────────
    op.create_table(
        "app_settings",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
            comment="Universally unique record identifier",
        ),
        sa.Column(
            "key", sa.String(255), nullable=False, comment="Setting key (unique)"
        ),
        sa.Column(
            "value", sa.Text, nullable=True, comment="Setting value (stored as text)"
        ),
        sa.Column(
            "description",
            sa.String(500),
            nullable=True,
            comment="Human-readable description of this setting",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            comment="Record creation timestamp (UTC)",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            comment="Record last-update timestamp (UTC)",
        ),
    )
    op.create_unique_constraint("uq_app_settings_key", "app_settings", ["key"])
    op.create_index("ix_app_settings_key", "app_settings", ["key"])


def downgrade() -> None:
    """Drop foundation tables in reverse order."""
    op.drop_table("app_settings")
    op.drop_table("companies")
