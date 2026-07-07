"""
TalentForge AI — Common Pydantic Schemas
=========================================
Shared request/response envelopes used across all modules.
These match the standard response format from AGENT.md §15:
  Success: {"success": true, "data": {}, "message": "OK"}
  Error:   {"success": false, "error": "Safe user message"}
"""

from __future__ import annotations

from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict

DataT = TypeVar("DataT")


class SuccessResponse(BaseModel, Generic[DataT]):
    """Standard success response envelope."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    success: bool = True
    data: Optional[DataT] = None
    message: str = "OK"


class ErrorResponse(BaseModel):
    """Standard error response envelope. Never include internal details."""

    success: bool = False
    error: str = "An error occurred. Please try again."


class HealthResponse(BaseModel):
    """Response schema for the /api/v1/health endpoint."""

    status: str
    version: str = "1.0"
    environment: str
    database: str  # "connected" | "unavailable"
