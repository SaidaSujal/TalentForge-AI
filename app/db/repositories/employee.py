"""
TalentForge AI — EmployeeRepository
===================================
Manages Employee records, manager hierarchies, and soft deletions.
"""

from __future__ import annotations

import uuid
from typing import Optional, Sequence

from sqlalchemy import select

from app.db.models import Employee
from app.db.repositories.base import TenantRepository, handle_db_errors


class EmployeeRepository(TenantRepository[Employee]):
    """
    Tenant-scoped repository for Employee model.
    """

    ALLOWED_FILTER_FIELDS = {
        "status",
        "department",
        "role",
        "manager_id",
        "user_id",
        "work_mode",
        "experience_level",
    }
    ALLOWED_SORT_FIELDS = {
        "created_at",
        "last_name",
        "first_name",
        "department",
        "role",
        "hire_date",
    }

    def __init__(self, db, company_id: uuid.UUID):
        super().__init__(db, Employee, company_id)

    async def get_by_user_id(self, user_id: uuid.UUID) -> Optional[Employee]:
        """Fetch the employee record associated with a user ID."""
        query = select(Employee).where(
            Employee.user_id == user_id,
            Employee.company_id == self.company_id,
            Employee.is_deleted.is_(False),
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_subordinates(self, manager_id: uuid.UUID) -> Sequence[Employee]:
        """Retrieve all subordinates reporting to the specified manager."""
        query = select(Employee).where(
            Employee.manager_id == manager_id,
            Employee.company_id == self.company_id,
            Employee.is_deleted.is_(False),
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def delete(self, id: uuid.UUID) -> bool:
        """Logical soft-deletion of an employee record."""
        db_obj = await self.get(id)
        if not db_obj:
            return False

        async with handle_db_errors():
            db_obj.is_deleted = True
            self.db.add(db_obj)
            await self.db.flush()
            return True
