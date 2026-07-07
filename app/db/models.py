"""
TalentForge AI — SQLAlchemy Models (Phase 1 Foundation)
=========================================================
This file imports the Base so that Alembic's env.py can discover all models
via `Base.metadata` when running migrations.

Phase 1 only includes the Company model as the foundational tenant anchor
and a minimal AppSettings model for system-level configuration.

Full HR feature models (employees, candidates, etc.) will be added in Phase 2.

IMPORTANT: Every tenant-owned model MUST:
  1. Include company_id (UUID, NOT NULL, indexed)
  2. Have a foreign key to the companies table
  3. Use UUID primary keys
  4. Extend TimestampMixin
"""

from __future__ import annotations

# Import Base so Alembic sees the metadata
from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin  # noqa: F401

# Import modular models — Alembic autodiscovery requires these to be imported here
from app.db.models import (  # noqa: F401
    Company,
    User,
    AppSettings,
    Employee,
    Candidate,
    Resume,
    JobDescription,
)

