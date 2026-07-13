"""
TalentForge AI — AI Response Cache System (Phase 2.6)
======================================================
The cache system is the primary cost-saving mechanism.
Before every LLM call, the service must check the cache.
A cache hit avoids the NVIDIA API call entirely.
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.repositories.ai_cache import AICacheRepository
from app.db.repositories.ai_history import AIHistoryRepository

logger = logging.getLogger(__name__)


def build_cache_key(prompt: str, model_id: str) -> str:
    """
    Generate a deterministic SHA-256 cache key from the prompt and model ID.
    The key is safe to store in the database and compare.
    """
    raw = f"{model_id}::{prompt}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def get_cache_ttl() -> timedelta:
    """Return the configured cache TTL as a timedelta."""
    return timedelta(hours=settings.cache_ttl_hours)


class AICache:
    """
    Database-backed cache utilities using repository injection.
    Phase 2.6: Replace stub methods with real database-backed implementations.
    Phase 3: Integrate into the AI call pipeline (check → call → store).
    """

    async def get(
        self,
        cache_key: str,
        db: Optional[AsyncSession] = None,
        company_id: Optional[uuid.UUID] = None,
    ) -> Optional[str]:
        """
        Look up a cache entry by key.
        If db or company_id are omitted, returns None (acting as skeleton stub).
        """
        if db is None or company_id is None:
            logger.debug(
                "Cache lookup (stub) — cache miss (missing db or company_id)",
                extra={"extra_fields": {"cache_key": cache_key[:8] + "..."}},
            )
            return None

        repo = AICacheRepository(db, company_id)
        cache_entry = await repo.get_active_cache(cache_key)
        if cache_entry:
            logger.debug(
                "Cache lookup — hit",
                extra={"extra_fields": {"cache_key": cache_key[:8] + "..."}},
            )
            return cache_entry.response_text

        logger.debug(
            "Cache lookup — miss",
            extra={"extra_fields": {"cache_key": cache_key[:8] + "..."}},
        )
        return None

    async def set(
        self,
        cache_key: str,
        response: str,
        db: Optional[AsyncSession] = None,
        company_id: Optional[uuid.UUID] = None,
        prompt_hash: Optional[str] = None,
        task_type: Optional[str] = None,
        provider: Optional[str] = None,
        model_used: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        token_count: Optional[int] = None,
    ) -> None:
        """
        Store an AI response in the cache.
        If db or company_id are omitted, acts as a no-op skeleton.
        """
        if db is None or company_id is None:
            logger.debug(
                "Cache store (stub) — skipped (missing db or company_id)",
                extra={"extra_fields": {"cache_key": cache_key[:8] + "..."}},
            )
            return

        if not expires_at:
            expires_at = datetime.now(timezone.utc) + get_cache_ttl()

        repo = AICacheRepository(db, company_id)
        await repo.upsert_cache(
            cache_key=cache_key,
            prompt_hash=prompt_hash or "default_prompt_hash",
            task_type=task_type or "default_task",
            provider=provider or "nvidia",
            model_used=model_used or "meta/llama-3.1-8b-instruct",
            response_text=response,
            expires_at=expires_at,
            token_count=token_count,
        )
        logger.debug(
            "Cache store — saved",
            extra={"extra_fields": {"cache_key": cache_key[:8] + "..."}},
        )

    async def get_hit_count(
        self, company_id: str, db: Optional[AsyncSession] = None
    ) -> int:
        """
        Return the number of cache hits for a company (for dashboard KPI).
        If db is omitted, returns 0.
        """
        if db is None:
            return 0

        repo = AIHistoryRepository(db, uuid.UUID(company_id))
        return await repo.count_cache_hits()


# Module-level singleton used by service layer
ai_cache = AICache()
