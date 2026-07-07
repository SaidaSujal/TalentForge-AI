"""
TalentForge AI — FastAPI Application Entry Point
=================================================
This is the main module imported by uvicorn:
    uvicorn app.main:app --host 0.0.0.0 --port $PORT

Startup sequence (from AGENT.md Build Order):
  1. Configure structured JSON logging
  2. Validate required environment variables
  3. Create FastAPI app with metadata
  4. Register exception handlers
  5. Add security headers middleware
  6. Add CORS middleware (allowlist from env)
  7. Add SlowAPI rate limiter middleware
  8. Mount API routers under /api/v1
  9. Log successful startup

Phase 1 note:
  - No HR feature routers are mounted yet.
  - Only /api/v1/health is live.
  - Database connection is tested on the health endpoint only, not at startup,
    to avoid slow boot times on Render's free tier.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.core.logging_config import configure_logging
from app.core.rate_limiter import limiter
from app.core.security import SecurityHeadersMiddleware, get_cors_kwargs
from app.routes import health as health_router


# ─── Lifespan ─────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.
    Runs startup logic before yielding and teardown after.
    """
    # ── Startup ──────────────────────────────────────────────────────────────
    configure_logging(settings.log_level)
    logger = logging.getLogger(__name__)

    logger.info(
        "TalentForge AI starting",
        extra={
            "extra_fields": {
                "app_name": settings.app_name,
                "environment": settings.app_env,
                "version": "1.0",
            }
        },
    )

    # Warn if SECRET_KEY looks like a placeholder (development safety check)
    if settings.secret_key in ("change-me-to-a-random-64-char-string", "changeme", ""):
        logger.warning(
            "SECRET_KEY appears to be a placeholder. "
            "Generate a strong key before deployment."
        )

    yield

    # ── Shutdown ──────────────────────────────────────────────────────────────
    logger.info("TalentForge AI shutting down")


# ─── Application Factory ──────────────────────────────────────────────────────


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    Called once at module import time — result stored in `app`.
    """
    app = FastAPI(
        title=settings.app_name,
        description=(
            "AI-Powered HR Intelligence Platform — "
            "Resume screening, policy chatbot, JD generation, "
            "onboarding, performance reviews, attrition prediction, "
            "learning recommendations, and interview kit generation."
        ),
        version="1.0.0",
        docs_url="/api/docs" if not settings.is_production else None,
        redoc_url="/api/redoc" if not settings.is_production else None,
        openapi_url="/api/openapi.json" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # ── Rate Limiter State ────────────────────────────────────────────────────
    # SlowAPI requires the limiter to be attached to app.state
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # ── Exception Handlers ────────────────────────────────────────────────────
    register_exception_handlers(app)

    # ── Middleware (applied last-to-first) ────────────────────────────────────
    # 1. Security headers — outermost wrapper, applied to every response
    app.add_middleware(SecurityHeadersMiddleware)

    # 2. CORS — must come after security headers
    app.add_middleware(CORSMiddleware, **get_cors_kwargs())

    # 3. SlowAPI rate limiter middleware
    app.add_middleware(SlowAPIMiddleware)

    # ── Routers ───────────────────────────────────────────────────────────────
    # Health endpoint — Phase 1
    app.include_router(health_router.router, prefix="/api/v1")

    # Phase 2+ routers will be mounted here:
    # app.include_router(employees_router, prefix="/api/v1/employees", tags=["Employees"])
    # app.include_router(candidates_router, prefix="/api/v1/candidates", tags=["Candidates"])
    # app.include_router(policies_router, prefix="/api/v1/policies", tags=["Policies"])
    # app.include_router(chatbot_router, prefix="/api/v1/chatbot", tags=["Chatbot"])
    # app.include_router(jobs_router, prefix="/api/v1/jobs", tags=["Jobs"])
    # app.include_router(onboarding_router, prefix="/api/v1/onboarding", tags=["Onboarding"])
    # app.include_router(performance_router, prefix="/api/v1/performance", tags=["Performance"])
    # app.include_router(attrition_router, prefix="/api/v1/attrition", tags=["Attrition"])
    # app.include_router(training_router, prefix="/api/v1/training", tags=["Training"])
    # app.include_router(interviews_router, prefix="/api/v1/interviews", tags=["Interviews"])
    # app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["Analytics"])
    # app.include_router(exports_router, prefix="/api/v1/exports", tags=["Exports"])

    return app


# ─── App Instance ─────────────────────────────────────────────────────────────
# This is the object uvicorn imports: `uvicorn app.main:app`
app: FastAPI = create_app()
