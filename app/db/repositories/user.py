"""
TalentForge AI — UserRepository
===============================
Manages User accounts and deactivations.
"""

from __future__ import annotations

import uuid
from typing import Any, Optional, Sequence

from sqlalchemy import select

from app.core.errors import WriteProtectedError
from app.db.models import User
from app.db.repositories.base import TenantRepository


class UserRepository(TenantRepository[User]):
    """
    Tenant-scoped repository for User model.
    """

    ALLOWED_FILTER_FIELDS = {"role", "is_active", "email"}
    ALLOWED_SORT_FIELDS = {"created_at", "email", "role"}

    def __init__(self, db, company_id: uuid.UUID):
        super().__init__(db, User, company_id)

    async def get(
        self, id: uuid.UUID, include_inactive: bool = False
    ) -> Optional[User]:
        """Get user by ID, filtering out inactive users by default."""
        return await super().get(id, include_deleted=include_inactive)

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        sort_by: Optional[str] = None,
        descending: bool = False,
        include_inactive: bool = False,
        **filters: Any,
    ) -> Sequence[User]:
        """List users, filtering out inactive users by default."""
        return await super().list(
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            descending=descending,
            include_deleted=include_inactive,
            **filters,
        )

    async def count(self, include_inactive: bool = False, **filters: Any) -> int:
        """Count users, filtering out inactive users by default."""
        return await super().count(include_deleted=include_inactive, **filters)

    async def exists(self, id: uuid.UUID, include_inactive: bool = False) -> bool:
        """Check existence, filtering out inactive users by default."""
        return await super().exists(id, include_deleted=include_inactive)

    async def get_by_email(
        self, email: str, include_inactive: bool = False
    ) -> Optional[User]:
        """Retrieve user by email, filtering out inactive users by default."""
        query = select(User).where(
            User.email == email, User.company_id == self.company_id
        )
        if not include_inactive:
            query = query.where(User.is_active)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def deactivate_user(self, user_id: uuid.UUID) -> User:
        """Deactivate a user (logical disable)."""
        return await self.update(user_id, {"is_active": False})

    async def reactivate_user(self, user_id: uuid.UUID) -> User:
        """Reactivate a user profile."""
        return await self.update(user_id, {"is_active": True})

    async def delete(self, id: uuid.UUID) -> bool:
        """Users are write-protected against physical delete operations."""
        raise WriteProtectedError(
            "User profiles cannot be deleted. Deactivate them instead."
        )
