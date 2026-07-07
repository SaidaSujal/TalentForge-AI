"""
TalentForge AI — AppSettings Database Model
===========================================
Defines the AppSettings model for global system settings.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class AppSettings(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    System-level application settings stored in the database.
    These are shared across all tenants and do NOT require company_id.

    Examples: feature flags, maintenance mode, global rate-limit overrides.
    """

    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Setting key (unique)",
    )
    value: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Setting value (stored as text)",
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Human-readable description of this setting",
    )

    def __repr__(self) -> str:
        return f"<AppSettings key={self.key!r}>"
