"""
TalentForge AI — Rate Limiting Configuration
=============================================
Uses SlowAPI (a Starlette-compatible rate limiter backed by memory or Redis).

Limits (from AGENT.md §12.4):
  - Public APIs:          20 req/min/IP
  - AI/LLM endpoints:    10 req/min/IP
  - Auth endpoints:       5 req/min/IP
  - Authenticated APIs:  60 req/min/user (applied in Phase 10 with JWT)

Usage in route files:
    from app.core.rate_limiter import limiter, public_limit, ai_limit

    @router.get("/endpoint")
    @limiter.limit(public_limit)
    async def my_endpoint(request: Request):
        ...
"""

from __future__ import annotations

import logging

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

logger = logging.getLogger(__name__)

# ─── Limiter Instance ─────────────────────────────────────────────────────────
# key_func determines what uniquely identifies a "user" for rate limiting.
# In V1 we key by IP address. Phase 10 can switch to JWT subject.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.rate_limit_public],
    headers_enabled=True,  # Adds X-RateLimit-* headers to responses
)

# ─── Convenience Limit Strings ────────────────────────────────────────────────
# Use these in @limiter.limit() decorators to avoid magic strings.
public_limit: str = settings.rate_limit_public  # e.g. "20/minute"
ai_limit: str = settings.rate_limit_ai  # e.g. "10/minute"
auth_limit: str = settings.rate_limit_auth  # e.g. "5/minute"
