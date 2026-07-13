"""
TalentForge AI — Custom Exception Classes & FastAPI Exception Handlers
======================================================================
All custom exceptions are defined here. FastAPI exception handlers are also
registered here and imported in app/main.py.

Rules (from AGENT.md §15):
- Return generic, user-safe messages to clients.
- Log detailed error info server-side only.
- Never return stack traces, SQL errors, file paths, or secrets.
- Use standard success/error JSON envelope:
    Success: {"success": true, "data": {}, "message": "OK"}
    Error:   {"success": false, "error": "Safe user message"}
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


# ─── Base Exception ───────────────────────────────────────────────────────────


class TalentForgeError(Exception):
    """
    Base exception for all TalentForge-specific errors.
    Subclass this to create domain-specific errors.
    """

    def __init__(
        self,
        message: str,
        user_message: str = "An unexpected error occurred. Please try again.",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message  # Server-side detail (logged only)
        self.user_message = user_message  # Safe message returned to client
        self.status_code = status_code
        self.details = details or {}


# ─── Domain Exceptions ────────────────────────────────────────────────────────


class NotFoundError(TalentForgeError):
    """Resource was not found."""

    def __init__(self, resource: str, identifier: Any = None) -> None:
        detail = f"{resource} not found"
        if identifier:
            detail += f" (id={identifier})"
        super().__init__(
            message=detail,
            user_message=f"{resource} not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ValidationFailedError(TalentForgeError):
    """Input validation failed at the business logic layer."""

    def __init__(
        self, message: str, user_message: str = "Invalid input. Please check your data."
    ) -> None:
        super().__init__(
            message=message,
            user_message=user_message,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class DatabaseError(TalentForgeError):
    """Database operation failed."""

    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            user_message="A database error occurred. Please try again.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class RecordAlreadyExistsError(DatabaseError):
    """Raised when a unique constraint or primary key conflict occurs."""

    def __init__(
        self,
        message: str = "Record already exists.",
        orig_exc: Optional[Exception] = None,
    ) -> None:
        super().__init__(message)
        self.user_message = "A record with these details already exists."
        self.status_code = 409  # HTTP Conflict
        self.orig_exc = orig_exc


class ForeignKeyViolationError(DatabaseError):
    """Raised when a foreign key relation check fails."""

    def __init__(
        self,
        message: str = "Invalid reference key.",
        orig_exc: Optional[Exception] = None,
    ) -> None:
        super().__init__(message)
        self.user_message = "The referenced resource is invalid."
        self.status_code = 400  # HTTP Bad Request
        self.orig_exc = orig_exc


class DatabaseConstraintError(DatabaseError):
    """Raised when a check constraint fails in the database."""

    def __init__(
        self,
        message: str = "Database constraint violation.",
        orig_exc: Optional[Exception] = None,
    ) -> None:
        super().__init__(message)
        self.user_message = "Provided values violate database constraint policies."
        self.status_code = 400  # HTTP Bad Request
        self.orig_exc = orig_exc


class WriteProtectedError(DatabaseError):
    """Raised when attempting to edit or delete append-only compliance logs."""

    def __init__(self, message: str = "This resource is write-protected.") -> None:
        super().__init__(message)
        self.user_message = (
            "This operation is not permitted. The record is write-protected."
        )
        self.status_code = 403  # HTTP Forbidden


class ConcurrencyError(DatabaseError):
    """Raised when a concurrent update conflict occurs."""

    def __init__(self, message: str = "Resource modified by another request.") -> None:
        super().__init__(message)
        self.user_message = (
            "The record was updated by another user. Please reload and try again."
        )
        self.status_code = 409  # HTTP Conflict


class AIServiceError(TalentForgeError):
    """AI model call failed or returned an invalid response."""

    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            user_message="The AI service is temporarily unavailable. Please try again later.",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class FileValidationError(TalentForgeError):
    """Uploaded file failed validation checks."""

    def __init__(
        self, message: str, user_message: str = "File validation failed."
    ) -> None:
        super().__init__(
            message=message,
            user_message=user_message,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class RateLimitError(TalentForgeError):
    """Rate limit exceeded."""

    def __init__(self, message: str = "Rate limit exceeded") -> None:
        super().__init__(
            message=message,
            user_message="Too many requests. Please wait a moment and try again.",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )


class PermissionDeniedError(TalentForgeError):
    """Action not permitted for this user/company."""

    def __init__(self, message: str = "Permission denied") -> None:
        super().__init__(
            message=message,
            user_message="You do not have permission to perform this action.",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class PromptInjectionError(TalentForgeError):
    """Potential prompt injection detected in user input."""

    def __init__(self, message: str = "Prompt injection attempt detected") -> None:
        super().__init__(
            message=message,
            user_message="Your input contains disallowed content. Please rephrase your request.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


# ─── Response Helpers ─────────────────────────────────────────────────────────


def success_response(data: Any = None, message: str = "OK") -> Dict[str, Any]:
    """Build a standard success envelope."""
    return {"success": True, "data": data or {}, "message": message}


def error_response(error: str = "An error occurred.") -> Dict[str, Any]:
    """Build a standard error envelope. Never include internal details."""
    return {"success": False, "error": error}


# ─── FastAPI Exception Handlers ───────────────────────────────────────────────


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register all custom exception handlers on the FastAPI app.
    Call this inside create_app() in app/main.py.
    """

    @app.exception_handler(TalentForgeError)
    async def talentforge_error_handler(
        request: Request, exc: TalentForgeError
    ) -> JSONResponse:
        """Handle all TalentForge domain exceptions."""
        logger.error(
            "TalentForge domain error",
            extra={
                "extra_fields": {
                    "error_type": type(exc).__name__,
                    "detail": exc.message,
                    "path": str(request.url.path),
                    "method": request.method,
                }
            },
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(exc.user_message),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        """Handle standard HTTP exceptions (404, 405, etc.)."""
        # Map status codes to safe user messages
        _safe_messages: Dict[int, str] = {
            404: "The requested resource was not found.",
            405: "Method not allowed.",
            401: "Authentication required.",
            403: "You do not have permission to access this resource.",
        }
        user_msg = _safe_messages.get(
            exc.status_code, "An error occurred. Please try again."
        )
        logger.warning(
            "HTTP exception",
            extra={
                "extra_fields": {
                    "status_code": exc.status_code,
                    "path": str(request.url.path),
                    "method": request.method,
                }
            },
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(user_msg),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle Pydantic v2 request validation errors (HTTP 422)."""
        logger.warning(
            "Request validation error",
            extra={
                "extra_fields": {
                    "path": str(request.url.path),
                    "error_count": len(exc.errors()),
                }
            },
        )
        # Return a generic message — never expose field names or values to clients
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response(
                "Request validation failed. Please check your input and try again."
            ),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Catch-all handler — ensures no raw exceptions reach the client."""
        logger.exception(
            "Unhandled exception",
            extra={
                "extra_fields": {
                    "path": str(request.url.path),
                    "method": request.method,
                    "exception_type": type(exc).__name__,
                }
            },
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response("Something went wrong. Please try again."),
        )
