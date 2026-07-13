"""
TalentForge AI — AIHistoryRepository
====================================
Tracks and reads generative AI invocation transactions and logs. strictly append-only.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict

from sqlalchemy import func, select

from app.core.errors import WriteProtectedError
from app.db.models import AIHistory
from app.db.repositories.base import TenantRepository


class AIHistoryRepository(TenantRepository[AIHistory]):
    """
    Tenant-scoped repository for AIHistory model. Strictly append-only.
    """

    ALLOWED_FILTER_FIELDS = {
        "module",
        "task_type",
        "provider",
        "model_used",
        "cache_hit",
        "user_id",
    }
    ALLOWED_SORT_FIELDS = {"created_at", "latency_ms", "estimated_cost"}

    def __init__(self, db, company_id: uuid.UUID):
        super().__init__(db, AIHistory, company_id)

    async def count_cache_hits(self) -> int:
        """Count cumulative cache hits for the company."""
        query = (
            select(func.count())
            .select_from(AIHistory)
            .where(AIHistory.company_id == self.company_id, AIHistory.cache_hit)
        )
        result = await self.db.execute(query)
        return result.scalar() or 0

    async def update(self, record_id: uuid.UUID, obj_in: Dict[str, Any]) -> AIHistory:
        """AI History logs are strictly write-protected."""
        raise WriteProtectedError("AIHistory records are write-protected.")

    async def delete(self, id: uuid.UUID) -> bool:
        """AI History logs are strictly write-protected."""
        raise WriteProtectedError("AIHistory records cannot be deleted.")
