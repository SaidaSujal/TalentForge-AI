"""
TalentForge AI — Database Session & Engine
==========================================
Configures the SQLAlchemy async-compatible engine and session factory
for Neon PostgreSQL.

Design notes:
- Uses psycopg (v3) driver for native async support and Neon compatibility.
- Connection pool is sized conservatively to stay within Neon free-tier limits.
- Sessions are yielded via FastAPI dependencies and automatically closed.
- The engine is created once at module import time using settings from .env.

Usage:
    # In a FastAPI route or dependency:
    from app.db.session import get_db
    async def my_route(db: AsyncSession = Depends(get_db)):
        ...
"""

from __future__ import annotations

import logging
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

logger = logging.getLogger(__name__)

# ─── Engine ───────────────────────────────────────────────────────────────────
# Neon requires SSL by default, but we allow overriding it (e.g. sslmode=disable) for local development
connect_args = {}
if "sslmode=" not in settings.database_url:
    connect_args["sslmode"] = "require"

engine: AsyncEngine = create_async_engine(
    settings.database_url,
    echo=settings.is_development,   # SQL echo only in dev
    pool_size=5,                    # Neon free tier: max ~10 concurrent connections
    max_overflow=10,
    pool_pre_ping=True,             # Detect stale connections before use
    pool_recycle=1800,              # Recycle connections every 30 min (Neon idle timeout)
    connect_args=connect_args,
)

# ─── Session Factory ──────────────────────────────────────────────────────────
AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Avoids lazy-load errors after commit
    autoflush=False,
    autocommit=False,
)


# ─── FastAPI Dependency ───────────────────────────────────────────────────────


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides a database session per request.
    The session is automatically closed (and rolled back on error) after the request.

    Usage:
        async def endpoint(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ─── Health Check Utility ─────────────────────────────────────────────────────


async def check_database_connection() -> bool:
    """
    Execute a lightweight probe query to verify the database is reachable.
    Used by the /api/v1/health endpoint.

    Returns:
        True if the database responds correctly, False otherwise.
    """
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        logger.info("Database connection check passed")
        return True
    except Exception as exc:
        # Log the error server-side but do NOT expose details to the caller
        logger.error(
            "Database connection check failed",
            extra={"extra_fields": {"exception_type": type(exc).__name__}},
        )
        return False
