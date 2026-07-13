"""
TalentForge AI — Audit Log Database Model
==========================================
Enforces append-only compliance logs for sensitive security mutations and exports.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models.company import Company
    from app.db.models.user import User


class AuditLog(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Audit log table.
    Ensures append-only activity records mapping system changes.
    """

    __tablename__ = "audit_logs"

    __table_args__ = (
        # Composite B-Tree indexes for compliance audits
        Index(
            "ix_audit_logs_company_action_created",
            "company_id",
            "action",
            "created_at",
        ),
        Index(
            "ix_audit_logs_company_entity",
            "company_id",
            "entity_type",
            "entity_id",
        ),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        comment="Tenant company identifier",
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User identifier who executed the audited action",
    )
    module: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Triggering module name (e.g. security, policy_rag)",
    )
    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Action key (e.g. HUMAN_REVIEW_APPROVED)",
    )
    entity_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Audited record database table name reference",
    )
    entity_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Audited record primary identifier reference (generic string)",
    )
    metadata_json: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        comment="Redacted audit metadata containing diff parameters",
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
        comment="IPv4/IPv6 client address metadata details",
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Client browser user agent details",
    )

    # Relationships
    company: Mapped[Company] = relationship("Company", back_populates="audit_logs")
    user: Mapped[Optional[User]] = relationship("User")
