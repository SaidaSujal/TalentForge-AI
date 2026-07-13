"""
TalentForge AI — Alembic Environment Script
============================================
This file is run by Alembic for every migration command.

Key behaviours:
1. DATABASE_URL is read from the environment (.env or system env).
   Never hardcoded here.
2. All SQLAlchemy models are imported so Alembic sees the full metadata.
3. Async engine is used (psycopg v3 + asyncio).
4. run_migrations_online uses asyncio.run() for async compatibility.
"""

from __future__ import annotations

import asyncio
import os
from logging.config import fileConfig

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# ─── Alembic Config Object ────────────────────────────────────────────────────
config = context.config

# ─── Logging ─────────────────────────────────────────────────────────────────
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

import app.db.models  # noqa: E402, F401 — side-effect import to register all models

# ─── Import Models ────────────────────────────────────────────────────────────
# IMPORTANT: importing app.db.models triggers all model imports,
# making Base.metadata aware of every table for auto-generation.
from app.db.base import Base  # noqa: E402

target_metadata = Base.metadata


# ─── Database URL ─────────────────────────────────────────────────────────────
# Read from environment — NEVER hardcode credentials here.
def get_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise ValueError(
            "DATABASE_URL environment variable is not set. "
            "Copy .env.example to .env and fill in your Neon connection string."
        )
    return url


# ─── Offline Migrations ───────────────────────────────────────────────────────


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode — generates SQL without connecting.
    Useful for reviewing migration SQL before applying it.
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# ─── Online Migrations (Async) ────────────────────────────────────────────────


def do_run_migrations(connection: Connection) -> None:
    """Run the actual migrations on a synchronous connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async engine and run migrations inside it."""
    url = get_url()
    connectable = create_async_engine(
        url,
        poolclass=pool.NullPool,  # No pooling for migration runs
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    """Entry point for online migrations — uses asyncio.run()."""
    asyncio.run(run_async_migrations())


# ─── Entry Point ─────────────────────────────────────────────────────────────
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
