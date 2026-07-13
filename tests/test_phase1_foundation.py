"""
TalentForge AI — Test Suite
Phase 1 Foundation Tests

Tests the Phase 1 foundation:
  - Health endpoint returns {"status": "healthy"}
  - Settings load correctly from environment
  - Model router resolves task types to correct models
  - Cache key generation is deterministic
  - Security headers are present in responses
  - No secrets hardcoded

Run with:
    pytest tests/ -v
"""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

# ─── Test Client Setup ────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def client():
    """
    Create a synchronous TestClient for the FastAPI app.
    Database calls are mocked so tests don't require a real Neon connection.
    """
    # Set required env vars before importing the app
    os.environ.setdefault("SECRET_KEY", "test-secret-key-for-phase-1-testing-only")
    os.environ.setdefault(
        "DATABASE_URL",
        "postgresql+psycopg://test:test@localhost/testdb?sslmode=require",
    )

    # Patch the DB health check so tests don't need a real database
    with patch(
        "app.db.session.check_database_connection",
        new_callable=AsyncMock,
        return_value=True,
    ):
        from app.main import app

        with TestClient(app, raise_server_exceptions=True) as c:
            yield c


# ─── Health Endpoint Tests ────────────────────────────────────────────────────


class TestHealthEndpoint:
    """Tests for GET /api/v1/health"""

    def test_health_returns_200(self, client: TestClient):
        """Health endpoint must return HTTP 200."""
        with patch(
            "app.db.session.check_database_connection",
            new_callable=AsyncMock,
            return_value=True,
        ):
            response = client.get("/api/v1/health")
        assert response.status_code == 200

    def test_health_status_healthy(self, client: TestClient):
        """Health endpoint must return {'status': 'healthy'} when DB is up."""
        with patch(
            "app.db.session.check_database_connection",
            new_callable=AsyncMock,
            return_value=True,
        ):
            response = client.get("/api/v1/health")
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_has_required_fields(self, client: TestClient):
        """Health response must include status, version, environment, database."""
        with patch(
            "app.db.session.check_database_connection",
            new_callable=AsyncMock,
            return_value=True,
        ):
            response = client.get("/api/v1/health")
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "environment" in data
        assert "database" in data

    def test_health_db_status_when_connected(self, client: TestClient):
        """When DB is reachable, database field must be 'connected'."""
        with patch(
            "app.db.session.check_database_connection",
            new_callable=AsyncMock,
            return_value=True,
        ):
            response = client.get("/api/v1/health")
        assert response.json()["database"] == "connected"

    def test_health_status_unhealthy_when_db_down(self, client: TestClient):
        """When DB is unreachable, status must be 'unhealthy'."""
        # Patch at the routes module where the name is looked up (where it's used)
        with patch(
            "app.routes.health.check_database_connection",
            new_callable=AsyncMock,
            return_value=False,
        ):
            response = client.get("/api/v1/health")
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["database"] == "unavailable"


# ─── Security Headers Tests ───────────────────────────────────────────────────


class TestSecurityHeaders:
    """Verify mandatory security headers are present on every response."""

    def test_x_frame_options_deny(self, client: TestClient):
        with patch(
            "app.db.session.check_database_connection",
            new_callable=AsyncMock,
            return_value=True,
        ):
            response = client.get("/api/v1/health")
        assert response.headers.get("x-frame-options") == "DENY"

    def test_x_content_type_options_nosniff(self, client: TestClient):
        with patch(
            "app.db.session.check_database_connection",
            new_callable=AsyncMock,
            return_value=True,
        ):
            response = client.get("/api/v1/health")
        assert response.headers.get("x-content-type-options") == "nosniff"

    def test_referrer_policy_present(self, client: TestClient):
        with patch(
            "app.db.session.check_database_connection",
            new_callable=AsyncMock,
            return_value=True,
        ):
            response = client.get("/api/v1/health")
        assert "referrer-policy" in response.headers

    def test_permissions_policy_present(self, client: TestClient):
        with patch(
            "app.db.session.check_database_connection",
            new_callable=AsyncMock,
            return_value=True,
        ):
            response = client.get("/api/v1/health")
        assert "permissions-policy" in response.headers

    def test_content_security_policy_present(self, client: TestClient):
        with patch(
            "app.db.session.check_database_connection",
            new_callable=AsyncMock,
            return_value=True,
        ):
            response = client.get("/api/v1/health")
        assert "content-security-policy" in response.headers


# ─── Settings Tests ───────────────────────────────────────────────────────────


class TestSettings:
    """Verify settings load correctly and have sane defaults."""

    def test_settings_load_without_error(self):
        """Settings module must import and instantiate without errors."""
        from app.core.config import settings

        assert settings is not None

    def test_app_name_default(self):
        from app.core.config import settings

        assert settings.app_name == "TalentForge AI"

    def test_allowed_origins_list_returns_list(self):
        from app.core.config import settings

        origins = settings.allowed_origins_list
        assert isinstance(origins, list)
        assert len(origins) >= 1

    def test_max_upload_size_bytes_correct(self):
        from app.core.config import settings

        assert (
            settings.max_upload_size_bytes == settings.max_upload_size_mb * 1024 * 1024
        )

    def test_is_development_flag(self):
        from app.core.config import settings

        # Test env sets APP_ENV=development (default)
        assert isinstance(settings.is_development, bool)

    def test_is_production_flag(self):
        from app.core.config import settings

        assert isinstance(settings.is_production, bool)


# ─── Model Router Tests ───────────────────────────────────────────────────────


class TestModelRouter:
    """Verify the model router selects correct models for each task type."""

    def test_jd_draft_routes_to_small(self):
        from app.services.ai.model_router import ModelAlias, get_model_alias

        assert get_model_alias("jd_draft") == ModelAlias.SMALL

    def test_resume_scoring_routes_to_large(self):
        from app.services.ai.model_router import ModelAlias, get_model_alias

        assert get_model_alias("resume_scoring") == ModelAlias.LARGE

    def test_admin_insight_routes_to_advanced(self):
        from app.services.ai.model_router import ModelAlias, get_model_alias

        assert get_model_alias("admin_insight") == ModelAlias.ADVANCED

    def test_embedding_routes_to_embedding(self):
        from app.services.ai.model_router import ModelAlias, get_model_alias

        assert get_model_alias("embedding") == ModelAlias.EMBEDDING

    def test_unknown_task_defaults_to_small(self):
        from app.services.ai.model_router import ModelAlias, get_model_alias

        assert get_model_alias("nonexistent_task_xyz") == ModelAlias.SMALL

    def test_get_model_id_returns_string(self):
        from app.services.ai.model_router import get_model_id

        model_id = get_model_id("jd_draft")
        assert isinstance(model_id, str)
        assert len(model_id) > 0

    def test_model_ids_not_empty(self):
        from app.core.config import settings

        assert settings.nvidia_small_model
        assert settings.nvidia_large_model
        assert settings.nvidia_advanced_model
        assert settings.nvidia_embedding_model


# ─── Cache Tests ─────────────────────────────────────────────────────────────


class TestAICache:
    """Verify the AI cache skeleton behaves correctly in Phase 1."""

    def test_cache_key_is_deterministic(self):
        from app.services.ai.cache import build_cache_key

        key1 = build_cache_key("test prompt", "model-id")
        key2 = build_cache_key("test prompt", "model-id")
        assert key1 == key2

    def test_different_inputs_produce_different_keys(self):
        from app.services.ai.cache import build_cache_key

        key1 = build_cache_key("prompt A", "model-id")
        key2 = build_cache_key("prompt B", "model-id")
        assert key1 != key2

    def test_cache_key_is_64_chars(self):
        """SHA-256 hex digest is always 64 characters."""
        from app.services.ai.cache import build_cache_key

        key = build_cache_key("any prompt", "any-model")
        assert len(key) == 64

    @pytest.mark.asyncio
    async def test_cache_get_returns_none_in_phase1(self):
        """Phase 1 cache always returns None (stub)."""
        from app.services.ai.cache import AICache

        cache = AICache()
        result = await cache.get("any_key")
        assert result is None


# ─── No Secrets Hardcoded Test ────────────────────────────────────────────────


class TestNoHardcodedSecrets:
    """Verify no secrets are hardcoded in critical files."""

    SUSPICIOUS_PATTERNS = [
        "nvapi-",
        "postgresql+psycopg://",  # real connection strings should never be in source
        "sk-",
    ]

    def _file_content(self, path: str) -> str:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def test_no_nvidia_key_in_config(self):
        content = self._file_content("app/core/config.py")
        assert "nvapi-" not in content

    def test_no_nvidia_key_in_main(self):
        content = self._file_content("app/main.py")
        assert "nvapi-" not in content

    def test_no_hardcoded_db_url_in_session(self):
        content = self._file_content("app/db/session.py")
        # Must not contain a real DB URL pattern
        assert "postgresql+psycopg://USER:PASSWORD" not in content
