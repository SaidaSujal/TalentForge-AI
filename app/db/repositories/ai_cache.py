"""
TalentForge AI — AICacheRepository
==================================
Manages generative response caching, upserts, and physical eviction of expired cache keys.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert

from app.core.errors import ValidationFailedError, WriteProtectedError
from app.db.models import AICache
from app.db.repositories.base import TenantRepository, handle_db_errors


class AICacheRepository(TenantRepository[AICache]):
    """
    Tenant-scoped repository for AICache model.
    """

    ALLOWED_FILTER_FIELDS = {"cache_key", "task_type", "provider", "model_used"}
    ALLOWED_SORT_FIELDS = {"created_at", "expires_at"}

    def __init__(self, db, company_id: uuid.UUID):
        super().__init__(db, AICache, company_id)

    async def get_active_cache(self, cache_key: str) -> Optional[AICache]:
        """Retrieve cache record if present and not expired."""
        now = datetime.now(timezone.utc)
        query = select(AICache).where(
            AICache.cache_key == cache_key,
            AICache.company_id == self.company_id,
            AICache.expires_at > now,
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def upsert_cache(
        self,
        cache_key: str,
        prompt_hash: str,
        task_type: str,
        provider: str,
        model_used: str,
        response_text: str,
        expires_at: datetime,
        token_count: Optional[int] = None,
    ) -> AICache:
        """Insert or refresh cache entry using PostgreSQL native ON CONFLICT DO UPDATE clause."""
        # Validate expires_at is in the future
        if expires_at <= datetime.now(timezone.utc):
            raise ValidationFailedError("Cache expiration time must be in the future.")

        async with handle_db_errors():
            stmt = insert(AICache).values(
                company_id=self.company_id,
                cache_key=cache_key,
                prompt_hash=prompt_hash,
                task_type=task_type,
                provider=provider,
                model_used=model_used,
                response_text=response_text,
                expires_at=expires_at,
                token_count=token_count,
            )
            stmt = stmt.on_conflict_do_update(
                constraint="uq_ai_responses_cache_key",
                set_={
                    "prompt_hash": stmt.excluded.prompt_hash,
                    "task_type": stmt.excluded.task_type,
                    "provider": stmt.excluded.provider,
                    "model_used": stmt.excluded.model_used,
                    "response_text": stmt.excluded.response_text,
                    "token_count": stmt.excluded.token_count,
                    "expires_at": stmt.excluded.expires_at,
                    "updated_at": func.now(),
                },
            )
            await self.db.execute(stmt)
            await self.db.flush()
            # Expire only the specific stale AICache objects in the session to prevent stale read
            for obj in list(self.db.identity_map.values()):
                if (
                    isinstance(obj, AICache)
                    and obj.cache_key == cache_key
                    and obj.company_id == self.company_id
                ):
                    self.db.expire(obj)

        # Retrieve fresh active record
        active = await self.get_active_cache(cache_key)
        if not active:
            # Fallback retrieve if clock skew or small TTL instantly expired
            query = select(AICache).where(
                AICache.cache_key == cache_key, AICache.company_id == self.company_id
            )
            result = await self.db.execute(query)
            active = result.scalar_one()
        return active

    async def delete_expired(self) -> int:
        """Physically remove all expired cache keys for the company."""
        now = datetime.now(timezone.utc)
        stmt = delete(AICache).where(
            AICache.company_id == self.company_id, AICache.expires_at <= now
        )
        async with handle_db_errors():
            result = await self.db.execute(stmt)
            await self.db.flush()
            return result.rowcount

    async def update(self, record_id: uuid.UUID, obj_in: Dict[str, Any]) -> AICache:
        raise WriteProtectedError(
            "AICache records cannot be modified via update payload."
        )

    async def delete(self, id: uuid.UUID) -> bool:
        raise WriteProtectedError(
            "AICache records cannot be physically deleted individually via delete(). Use evictions."
        )
