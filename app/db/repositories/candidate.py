"""
TalentForge AI — CandidateRepository
====================================
Manages Candidate records, resumes, and soft deletions.
"""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.models import Candidate
from app.db.repositories.base import TenantRepository, handle_db_errors


class CandidateRepository(TenantRepository[Candidate]):
    """
    Tenant-scoped repository for Candidate model.
    """

    ALLOWED_FILTER_FIELDS = {"status", "email"}
    ALLOWED_SORT_FIELDS = {"created_at", "match_score", "experience_years"}

    def __init__(self, db, company_id: uuid.UUID):
        super().__init__(db, Candidate, company_id)

    async def get_with_resume(self, candidate_id: uuid.UUID) -> Optional[Candidate]:
        """Eagerly load candidate along with their 1-to-1 resume model."""
        query = (
            select(Candidate)
            .options(selectinload(Candidate.resume))
            .where(
                Candidate.id == candidate_id,
                Candidate.company_id == self.company_id,
                Candidate.is_deleted.is_(False),
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def delete(self, id: uuid.UUID) -> bool:
        """Logical soft-deletion of candidate profile."""
        db_obj = await self.get(id)
        if not db_obj:
            return False

        async with handle_db_errors():
            db_obj.is_deleted = True
            self.db.add(db_obj)
            await self.db.flush()
            return True
