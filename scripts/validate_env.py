"""
TalentForge AI — Environment Validator Script
=============================================
Run this script before starting the application to verify all required
environment variables are set and have non-placeholder values.

Usage:
    python scripts/validate_env.py

Exit codes:
    0 — all checks passed
    1 — one or more checks failed
"""

from __future__ import annotations

import os
import sys
from typing import List, Tuple

# Load .env file if it exists
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    print("[WARN] python-dotenv not installed — reading from system environment only")


# ─── Required Variables ───────────────────────────────────────────────────────

REQUIRED_VARS: List[Tuple[str, str]] = [
    ("APP_NAME", "Application name"),
    ("APP_ENV", "Application environment (development/staging/production)"),
    ("SECRET_KEY", "Secret key for cryptographic operations"),
    ("DATABASE_URL", "Neon PostgreSQL connection URL"),
    ("NVIDIA_API_KEY", "NVIDIA NIM API key"),
    ("ALLOWED_ORIGINS", "Comma-separated CORS allowed origins"),
]

# Values that indicate the variable is still a placeholder
PLACEHOLDER_VALUES: frozenset[str] = frozenset(
    {
        "change-me-to-a-random-64-char-string",
        "changeme",
        "your-secret-key",
        "nvapi-your-key-here",
        "postgresql+psycopg://USER:PASSWORD@HOST/DBNAME?sslmode=require",
        "",
    }
)


def check_env() -> bool:
    """
    Check all required environment variables.
    Returns True if all checks pass, False if any fail.
    """
    errors: List[str] = []
    warnings: List[str] = []

    print("=" * 60)
    print("TalentForge AI — Environment Validation")
    print("=" * 60)

    for var_name, description in REQUIRED_VARS:
        value = os.environ.get(var_name, "")
        if not value:
            errors.append(f"  ✗ {var_name} — MISSING ({description})")
        elif value in PLACEHOLDER_VALUES:
            errors.append(
                f"  ✗ {var_name} — PLACEHOLDER VALUE (replace with real value)"
            )
        else:
            # Mask sensitive values in output
            if any(
                secret in var_name.lower()
                for secret in ("key", "password", "secret", "url")
            ):
                display = value[:6] + "..." + value[-4:] if len(value) > 12 else "***"
            else:
                display = value
            print(f"  ✓ {var_name} = {display}")

    # Warn about development-only settings
    app_env = os.environ.get("APP_ENV", "development")
    if app_env == "production":
        secret_key = os.environ.get("SECRET_KEY", "")
        if len(secret_key) < 32:
            warnings.append(
                "  ⚠ SECRET_KEY should be at least 64 characters in production"
            )

    db_url = os.environ.get("DATABASE_URL", "")
    if db_url and "sslmode=require" not in db_url:
        warnings.append(
            "  ⚠ DATABASE_URL should include ?sslmode=require for Neon PostgreSQL"
        )

    # Print results
    print()
    if warnings:
        print("Warnings:")
        for w in warnings:
            print(w)
        print()

    if errors:
        print("Errors:")
        for e in errors:
            print(e)
        print()
        print(
            f"✗ {len(errors)} check(s) failed. Fix the above errors before starting the application."
        )
        return False

    print(f"✓ All {len(REQUIRED_VARS)} environment variable checks passed.")
    return True


if __name__ == "__main__":
    success = check_env()
    sys.exit(0 if success else 1)
