"""
TalentForge AI — Phase 2: Create Users Table
=============================================
Revision ID: 0003_create_users_table
Revises: 0002_create_foundation_tables
Create Date: 2026-07-05

Creates the users table for account administration and multi-tenant access.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers
revision: str = "0003_create_users_table"
down_revision: Union[str, None] = "0002_create_foundation_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create users table."""
    op.create_table(
        "users",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
            comment="Universally unique record identifier",
        ),
        sa.Column(
            "email",
            sa.String(255),
            nullable=False,
            comment="User email address (unique, indexed)",
        ),
        sa.Column(
            "password_hash",
            sa.String(255),
            nullable=False,
            comment="Bcrypt-hashed password",
        ),
        sa.Column(
            "role",
            sa.String(50),
            nullable=False,
            server_default="employee",
            comment="User role (e.g. admin, hr_manager, recruiter, employee, manager)",
        ),
        sa.Column(
            "company_id",
            UUID(as_uuid=True),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
            comment="Foreign key linking to the company tenant",
        ),
        sa.Column(
            "is_active",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("true"),
            comment="Soft-delete / active status flag",
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
    op.create_unique_constraint("uq_users_email", "users", ["email"])
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_company_id", "users", ["company_id"])


def downgrade() -> None:
    """Drop users table."""
    op.drop_table("users")
