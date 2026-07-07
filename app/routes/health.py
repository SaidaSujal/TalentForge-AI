"""
TalentForge AI — Health Check Route
=====================================
Provides the GET /api/v1/health endpoint required by:
  - Render deployment health check (AGENT.md §18)
  - Phase 1 verification criteria
  - CI/CD pre-flight checks

Expected response:
    {"status": "healthy"}

Extended response (for monitoring):
    {
        "status": "healthy",
        "version": "1.0",
        "environment": "development",
        "database": "connected"
    }

Route rules (from AGENT.md §6):
  - Routes must stay thin — no business logic here.
  - Call services (check_database_connection) not DB directly.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Request, Response

from app.core.config import settings
from app.core.rate_limiter import limiter, public_limit
from app.db.session import check_database_connection
from app.schemas.common import HealthResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Application health check",
    description=(
        "Returns the current health status of the application. "
        "Used by Render for deployment health checks and by monitoring systems."
    ),
    responses={
        200: {"description": "Application is healthy"},
        503: {"description": "Application is unhealthy — database unreachable"},
    },
)
@limiter.limit(public_limit)
async def health_check(request: Request, response: Response) -> HealthResponse:
    """
    Health check endpoint.

    Performs:
      1. Basic liveness check (always succeeds if the app is running).
      2. Database connectivity probe.

    Args:
        request: FastAPI request object (required by SlowAPI rate limiter).
        response: FastAPI response object (required by SlowAPI header injection).

    Returns:
      HealthResponse with status "healthy" or "unhealthy".
    """
    db_ok = await check_database_connection()

    status_str = "healthy" if db_ok else "unhealthy"
    db_status = "connected" if db_ok else "unavailable"

    if not db_ok:
        logger.warning("Health check: database unavailable")
    else:
        logger.info("Health check: OK")

    return HealthResponse(
        status=status_str,
        version="1.0",
        environment=settings.app_env,
        database=db_status,
    )
