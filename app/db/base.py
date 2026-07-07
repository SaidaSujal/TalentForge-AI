"""
TalentForge AI — SQLAlchemy Declarative Base
=============================================
All ORM models must inherit from Base defined here.
The Base also provides default columns (id, created_at, updated_at)
through a TimestampMixin to ensure consistency across all tables.

Rules (from AGENT.md §8):
- UUIDs for primary keys.
- created_at and updated_at on every table.
- company_id on every tenant-owned table.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Shared declarative base for all SQLAlchemy models.
    All models must inherit from this class (not DeclarativeBase directly).
    """

    pass


class TimestampMixin:
    """
    Mixin that adds created_at and updated_at columns to any model.
    Both columns use UTC timestamps managed by the database server.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Record creation timestamp (UTC)",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Record last-update timestamp (UTC)",
    )


class UUIDPrimaryKeyMixin:
    """
    Mixin that adds a UUID primary key column.
    Using UUIDs instead of serial integers prevents internal ID exposure.
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Universally unique record identifier",
    )
