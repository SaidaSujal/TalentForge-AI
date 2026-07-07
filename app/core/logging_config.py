"""
TalentForge AI — Structured Logging Configuration
===================================================
Configures the Python standard logging module with JSON-structured output
suitable for Render's stdout capture and future log aggregation.

Rules (from AGENT.md §16):
- Log: startup/shutdown, AI requests (metadata only), DB errors, rate-limit violations.
- NEVER log: passwords, JWT tokens, API keys, resume content, employee PII.
- Log level controlled by LOG_LEVEL env var.

Usage:
    from app.core.logging_config import get_logger
    logger = get_logger(__name__)
    logger.info("Application started")
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """
    Emits log records as a single-line JSON object.
    This format is trivially parseable by log aggregation systems.
    """

    # Fields that must NEVER appear in log output — security requirement
    _SENSITIVE_KEYS: frozenset[str] = frozenset(
        {
            "password",
            "password_hash",
            "api_key",
            "nvidia_api_key",
            "secret_key",
            "jwt",
            "token",
            "authorization",
            "cookie",
            "resume_text",
            "full_text",
            "salary",
            "ssn",
            "medical",
        }
    )

    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Attach exception info without exposing raw stack traces in structured fields
        if record.exc_info:
            log_entry["exception_type"] = (
                record.exc_info[0].__name__ if record.exc_info[0] else "Unknown"
            )
            # The formatted traceback is included only for server-side logs (never returned to clients)
            log_entry["traceback"] = self.formatException(record.exc_info)

        # Attach any extra fields, redacting sensitive keys
        if hasattr(record, "extra_fields"):
            safe_extras = {
                k: "[REDACTED]" if k.lower() in self._SENSITIVE_KEYS else v
                for k, v in record.extra_fields.items()  # type: ignore[attr-defined]
            }
            log_entry.update(safe_extras)

        return json.dumps(log_entry, default=str, ensure_ascii=False)


def configure_logging(log_level: str = "INFO") -> None:
    """
    Initialize the root logger with JSON formatting.
    Should be called once during application startup (inside lifespan).

    Args:
        log_level: One of DEBUG, INFO, WARNING, ERROR, CRITICAL.
    """
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Remove all existing handlers to avoid duplicate output
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    handler.setLevel(numeric_level)

    root_logger.setLevel(numeric_level)
    root_logger.addHandler(handler)

    # Suppress noisy third-party loggers in production
    for noisy_logger in ("uvicorn.access", "sqlalchemy.engine"):
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)

    # Always keep uvicorn error logs visible
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger.

    Args:
        name: Typically __name__ of the calling module.

    Returns:
        A standard Python Logger configured with the global handler.
    """
    return logging.getLogger(name)
