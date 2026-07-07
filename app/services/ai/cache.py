"""
TalentForge AI — AI Response Cache Skeleton (Phase 1)
======================================================
The cache system is the primary cost-saving mechanism.
Before every LLM call the service must check the cache.
A cache hit avoids the NVIDIA API call entirely.

Cache key: SHA-256 hash of (prompt_text + model_id)
TTL: controlled by CACHE_TTL_HOURS env var (default 24 h)
Storage: ai_cache database table (added in Phase 2)

Phase 1: This file defines the cache interface as a skeleton.
         The actual database-backed implementation is wired in Phase 2.
Phase 3: Full cache read/write is integrated into the AI call pipeline.

Rules (from AGENT.md §11):
  - Check cache BEFORE every LLM call.
  - Cache every repeatable AI output.
  - Cache TTL is configurable via CACHE_TTL_HOURS.
  - Dashboard must show "API calls saved by cache" as a KPI.
"""

from __future__ import annotations

import hashlib
import logging
from datetime import timedelta
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


def build_cache_key(prompt: str, model_id: str) -> str:
    """
    Generate a deterministic SHA-256 cache key from the prompt and model ID.
    The key is safe to store in the database and compare.

    Args:
        prompt: The complete prompt text (after all preprocessing).
        model_id: The resolved NVIDIA model ID string.

    Returns:
        A 64-character hex string (SHA-256 digest).
    """
    raw = f"{model_id}::{prompt}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def get_cache_ttl() -> timedelta:
    """Return the configured cache TTL as a timedelta."""
    return timedelta(hours=settings.cache_ttl_hours)


class AICache:
    """
    Skeleton cache interface.
    Phase 2: Replace stub methods with real database-backed implementations.
    Phase 3: Integrate into the AI call pipeline (check → call → store).
    """

    async def get(self, cache_key: str) -> Optional[str]:
        """
        Look up a cache entry by key.

        Phase 1 stub — always returns None (cache miss).
        Phase 2: Query the ai_cache table WHERE key = cache_key AND expires_at > now().

        Args:
            cache_key: SHA-256 hex digest from build_cache_key().

        Returns:
            The cached response JSON string if found and not expired, else None.
        """
        # TODO (Phase 2): Implement database lookup
        logger.debug("Cache lookup (stub) — cache miss", extra={"extra_fields": {"cache_key": cache_key[:8] + "..."}})
        return None

    async def set(self, cache_key: str, response: str) -> None:
        """
        Store an AI response in the cache.

        Phase 1 stub — no-op.
        Phase 2: INSERT INTO ai_cache (key, response, expires_at) VALUES (...).

        Args:
            cache_key: SHA-256 hex digest from build_cache_key().
            response: The AI response as a JSON string.
        """
        # TODO (Phase 2): Implement database store
        logger.debug("Cache store (stub) — skipped", extra={"extra_fields": {"cache_key": cache_key[:8] + "..."}})

    async def get_hit_count(self, company_id: str) -> int:
        """
        Return the number of cache hits for a company (for dashboard KPI).

        Phase 1 stub — returns 0.
        Phase 2: SELECT COUNT(*) FROM ai_history WHERE company_id=... AND cache_hit=true.

        Args:
            company_id: UUID string of the tenant company.

        Returns:
            Integer count of cache hits.
        """
        # TODO (Phase 2): Implement count query
        return 0


# Module-level singleton used by service layer
ai_cache = AICache()
