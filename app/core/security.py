"""
TalentForge AI — Security Utilities
=====================================
Contains:
  - Security headers middleware
  - CORS configuration
  - Demo user dependency (V1 placeholder — swappable for JWT later)
  - Password hashing helpers (pre-wired for Phase 10)

Auth is DEFERRED until after all 8 HR modules work.
For V1, get_current_user returns a DemoUser with the default company_id.
All services/repos accept company_id so RBAC can be bolted on without refactor.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from app.core.config import settings

logger = logging.getLogger(__name__)

# ─── Password Hashing (pre-wired for future auth) ────────────────────────────
# bcrypt via passlib — rounds tuned for production safety
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Hash a plain-text password with bcrypt. Never store plain passwords."""
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a bcrypt hash."""
    return _pwd_context.verify(plain_password, hashed_password)


# ─── Demo User (V1 Placeholder) ───────────────────────────────────────────────


@dataclass(frozen=True)
class DemoUser:
    """
    V1 placeholder user injected by the get_current_user dependency.
    Every service receives company_id from this object so that
    JWT/RBAC can be wired in Phase 10 without changing service signatures.
    """

    id: str = settings.demo_user_id
    company_id: str = settings.demo_company_id
    role: str = "admin"
    email: str = "demo@talentforge.ai"
    is_active: bool = True


# Module-level singleton — one demo user for the whole V1 session
_DEMO_USER = DemoUser()


async def get_current_user() -> DemoUser:
    """
    FastAPI dependency that returns the current user.

    V1 behaviour: always returns the DemoUser.
    Phase 10: replace the body of this function with JWT validation;
              the signature stays the same so no callers need updating.
    """
    return _DEMO_USER


# ─── Security Headers Middleware ──────────────────────────────────────────────


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Injects mandatory security headers on every HTTP response.

    Headers applied (per AGENT.md §12.5):
      - X-Frame-Options
      - X-Content-Type-Options
      - Referrer-Policy
      - Permissions-Policy
      - Content-Security-Policy
      - Strict-Transport-Security (production only)
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdn.tailwindcss.com; "
            "style-src 'self' 'unsafe-inline' cdn.tailwindcss.com fonts.googleapis.com; "
            "font-src 'self' fonts.gstatic.com; "
            "img-src 'self' data:; "
            "connect-src 'self';"
        )
        # HSTS only in production — avoids breaking local HTTPS-free dev
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
        return response


def get_cors_kwargs() -> dict:
    """
    Return keyword arguments for FastAPI's CORSMiddleware.
    Origins are read from ALLOWED_ORIGINS env var — never wildcard.
    """
    origins = settings.allowed_origins_list
    if not origins:
        logger.warning(
            "ALLOWED_ORIGINS is empty — CORS will block all cross-origin requests"
        )
    return {
        "allow_origins": origins,
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Request-ID"],
    }
