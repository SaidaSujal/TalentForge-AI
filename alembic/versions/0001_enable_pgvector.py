"""
TalentForge AI — Phase 1: Enable pgvector Extension
=====================================================
Revision ID: 0001_enable_pgvector
Create Date: 2026-07-04

This is the first migration in the project.
It enables the pgvector PostgreSQL extension required for:
  - Policy chunk embeddings (Module 2 — HR Policy Chatbot)
  - Resume similarity search (Module 1)
  - Any future vector-based feature

Rule (from AGENT.md §9):
  Enable pgvector through Alembic migration:
  CREATE EXTENSION IF NOT EXISTS vector;

Note: pgvector must be installed on the PostgreSQL server.
Neon PostgreSQL includes pgvector by default.
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

# revision identifiers
revision: str = "0001_enable_pgvector"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Enable the pgvector extension on the PostgreSQL database."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")


def downgrade() -> None:
    """
    Drop the pgvector extension.
    WARNING: This will also drop all vector columns — use with caution.
    """
    op.execute("DROP EXTENSION IF EXISTS vector;")
