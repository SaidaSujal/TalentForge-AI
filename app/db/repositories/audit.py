"""
TalentForge AI — AuditRepository
================================
Provides append-only compliance auditing log access.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict

from app.core.errors import WriteProtectedError
from app.db.models import AuditLog
from app.db.repositories.base import TenantRepository


class AuditRepository(TenantRepository[AuditLog]):
    """
    Tenant-scoped repository for AuditLog model. Strictly append-only.
    """

    ALLOWED_FILTER_FIELDS = {"module", "action", "entity_type", "entity_id", "user_id"}
    ALLOWED_SORT_FIELDS = {"created_at"}

    def __init__(self, db, company_id: uuid.UUID):
        super().__init__(db, AuditLog, company_id)

    async def update(self, record_id: uuid.UUID, obj_in: Dict[str, Any]) -> AuditLog:
        """Audit logs are strictly write-protected."""
        raise WriteProtectedError("AuditLog records are write-protected.")

    async def delete(self, id: uuid.UUID) -> bool:
        """Audit logs are strictly write-protected."""
        raise WriteProtectedError("AuditLog records cannot be deleted.")
