"""
TalentForge AI — AI Model Router (Phase 1 Skeleton)
=====================================================
The model router is the ONLY entry point for selecting AI models.
No service, repository, or route may call NVIDIA directly — they must
go through this router.

Model Registry (locked — do not change without approval):
  small    → meta/llama-3.1-8b-instruct       (fast, low-cost tasks)
  large    → meta/llama-3.1-70b-instruct       (complex HR reasoning)
  advanced → nvidia/llama-3.3-nemotron-super-49b-v1.5  (admin insights)
  embedding→ nvidia/nv-embed-v1                (vector embeddings)

Routing Table (from AGENT.md §10):
  Task type string → model alias → resolved model ID

Phase 1: This file defines the routing logic as a skeleton.
         Actual NVIDIA API calls are NOT made in Phase 1.
Phase 3: The nvidia_client and execute_prompt methods are wired up.

Usage (Phase 3+):
    from app.services.ai.model_router import get_model_id, ModelRouter

    model_id = get_model_id("jd_draft")        # → small model ID
    model_id = get_model_id("resume_scoring")   # → large model ID
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Dict, Final

from app.core.config import settings

logger = logging.getLogger(__name__)


# ─── Model Aliases ────────────────────────────────────────────────────────────


class ModelAlias(str, Enum):
    """Logical model tiers. Use these instead of raw model IDs."""

    SMALL = "small"
    LARGE = "large"
    ADVANCED = "advanced"
    EMBEDDING = "embedding"


# ─── Task → Model Alias Routing Table ────────────────────────────────────────


ROUTING_TABLE: Final[Dict[str, ModelAlias]] = {
    # Small model tasks — fast, low-cost
    "jd_draft": ModelAlias.SMALL,
    "email_text": ModelAlias.SMALL,
    "interview_questions": ModelAlias.SMALL,
    "welcome_message": ModelAlias.SMALL,
    "simple_summary": ModelAlias.SMALL,
    "onboarding_plan": ModelAlias.SMALL,
    "interview_kit": ModelAlias.SMALL,
    # Large model tasks — complex HR reasoning
    "resume_scoring": ModelAlias.LARGE,
    "policy_reasoning": ModelAlias.LARGE,
    "performance_review": ModelAlias.LARGE,
    "learning_plan": ModelAlias.LARGE,
    "retention_strategy": ModelAlias.LARGE,
    "attrition_analysis": ModelAlias.LARGE,
    # Advanced model tasks — multi-document / admin insights
    "admin_insight": ModelAlias.ADVANCED,
    "workforce_analysis": ModelAlias.ADVANCED,
    # Embedding model
    "embedding": ModelAlias.EMBEDDING,
}

# ─── Alias → Model ID Resolution ─────────────────────────────────────────────

_ALIAS_TO_MODEL_ID: Final[Dict[ModelAlias, str]] = {
    ModelAlias.SMALL: settings.nvidia_small_model,
    ModelAlias.LARGE: settings.nvidia_large_model,
    ModelAlias.ADVANCED: settings.nvidia_advanced_model,
    ModelAlias.EMBEDDING: settings.nvidia_embedding_model,
}


def get_model_alias(task_type: str) -> ModelAlias:
    """
    Resolve a task type string to the appropriate model alias.
    Unknown task types default to the small model (safest, cheapest).

    Args:
        task_type: One of the keys in ROUTING_TABLE.

    Returns:
        ModelAlias enum value.
    """
    alias = ROUTING_TABLE.get(task_type)
    if alias is None:
        logger.warning(
            "Unknown task_type '%s' — defaulting to small model",
            task_type,
        )
        return ModelAlias.SMALL
    return alias


def get_model_id(task_type: str) -> str:
    """
    Resolve a task type string to a concrete NVIDIA NIM model ID.

    Args:
        task_type: One of the keys in ROUTING_TABLE.

    Returns:
        The model ID string (e.g. "meta/llama-3.1-8b-instruct").
    """
    alias = get_model_alias(task_type)
    model_id = _ALIAS_TO_MODEL_ID[alias]
    logger.debug(
        "Model routed",
        extra={
            "extra_fields": {
                "task_type": task_type,
                "alias": alias.value,
                "model_id": model_id,
            }
        },
    )
    return model_id


class ModelRouter:
    """
    Stateless helper class wrapping the routing functions.
    Phase 3 will add the nvidia_client, execute_prompt, and cache_lookup methods here.
    """

    def get_model_for_task(self, task_type: str) -> str:
        """Return the resolved model ID for a given task type."""
        return get_model_id(task_type)

    def list_tasks(self) -> Dict[str, str]:
        """
        Return a human-readable map of task → model ID.
        Useful for the admin /api/v1/ai-usage endpoint.
        """
        return {
            task: _ALIAS_TO_MODEL_ID[alias].value
            for task, alias in ROUTING_TABLE.items()
        }


# Module-level singleton
model_router = ModelRouter()
