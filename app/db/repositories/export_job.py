"""
TalentForge AI — ExportJobRepository
====================================
Manages file download trackers, atomic download counters, and job soft-deletes.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import select, update

from app.core.errors import NotFoundError
from app.db.models import ExportJob
from app.db.repositories.base import TenantRepository, handle_db_errors


class ExportJobRepository(TenantRepository[ExportJob]):
    """
    Tenant-scoped repository for ExportJob model.
    """

    ALLOWED_FILTER_FIELDS = {"module_scope", "export_type", "status"}
    ALLOWED_SORT_FIELDS = {"created_at", "expires_at"}

    def __init__(self, db, company_id: uuid.UUID):
        super().__init__(db, ExportJob, company_id)

    async def get_expired_jobs(self) -> Sequence[ExportJob]:
        """Find non-deleted jobs whose storage TTL has expired."""
        now = datetime.now(timezone.utc)
        query = select(ExportJob).where(
            ExportJob.company_id == self.company_id,
            ExportJob.expires_at <= now,
            ExportJob.is_deleted.is_(False),
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def increment_download_count(self, id: uuid.UUID) -> int:
        """Atomically increment the download count and return the updated value."""
        # Enforces isolation and soft-delete check inside one single statement
        stmt = (
            update(ExportJob)
            .where(
                ExportJob.id == id,
                ExportJob.company_id == self.company_id,
                ExportJob.is_deleted.is_(False),
            )
            .values(download_count=ExportJob.download_count + 1)
            .returning(ExportJob.download_count)
        )

        async with handle_db_errors():
            result = await self.db.execute(stmt)
            await self.db.flush()

        download_count = result.scalar()
        if download_count is None:
            raise NotFoundError("ExportJob", id)

        return download_count

    async def delete(self, id: uuid.UUID) -> bool:
        """Logical soft-deletion of export job tracker."""
        db_obj = await self.get(id)
        if not db_obj:
            return False

        async with handle_db_errors():
            db_obj.is_deleted = True
            self.db.add(db_obj)
            await self.db.flush()
            return True
