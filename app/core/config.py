"""
TalentForge AI — Settings Management
=====================================
Reads all configuration from environment variables via Pydantic Settings.
Never hardcode secrets — every value must come from .env or the environment.

Usage:
    from app.core.config import settings
    db_url = settings.database_url
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    All fields are read-only after construction.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────────
    app_name: str = "TalentForge AI"
    app_env: str = "development"  # development | staging | production
    secret_key: str  # Required — no default — must be in .env

    # ── Database ──────────────────────────────────────────────────────────────
    database_url: str  # Required — must be postgresql+psycopg://...

    # ── NVIDIA NIM ────────────────────────────────────────────────────────────
    nvidia_api_key: str = ""  # Can be empty during Phase 1 (no AI calls yet)
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    nvidia_small_model: str = "meta/llama-3.1-8b-instruct"
    nvidia_large_model: str = "meta/llama-3.1-70b-instruct"
    nvidia_advanced_model: str = "nvidia/llama-3.3-nemotron-super-49b-v1.5"
    nvidia_embedding_model: str = "nvidia/nv-embed-v1"

    # ── CORS ──────────────────────────────────────────────────────────────────
    # Comma-separated list parsed into a Python list
    allowed_origins: str = "http://localhost:8000,http://127.0.0.1:8000"

    # ── File Upload ───────────────────────────────────────────────────────────
    max_upload_size_mb: int = 10

    # ── AI Response Cache ─────────────────────────────────────────────────────
    cache_ttl_hours: int = 24

    # ── Rate Limiting ─────────────────────────────────────────────────────────
    rate_limit_public: str = "20/minute"
    rate_limit_ai: str = "10/minute"
    rate_limit_auth: str = "5/minute"

    # ── Logging ───────────────────────────────────────────────────────────────
    log_level: str = "INFO"

    # ── Demo / Multi-Tenant Placeholder ──────────────────────────────────────
    demo_company_id: str = "00000000-0000-0000-0000-000000000001"
    demo_user_id: str = "00000000-0000-0000-0000-000000000001"

    # ── Computed Properties ───────────────────────────────────────────────────

    @property
    def is_production(self) -> bool:
        """True when running in a production environment."""
        return self.app_env.lower() == "production"

    @property
    def is_development(self) -> bool:
        """True when running in a development environment."""
        return self.app_env.lower() == "development"

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse the comma-separated ALLOWED_ORIGINS string into a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def max_upload_size_bytes(self) -> int:
        """Convert the max upload size from MB to bytes."""
        return self.max_upload_size_mb * 1024 * 1024


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return the cached Settings singleton.
    Using lru_cache ensures .env is read once at startup, not on every import.
    """
    return Settings()


# Module-level singleton — import this throughout the application
settings: Settings = get_settings()
