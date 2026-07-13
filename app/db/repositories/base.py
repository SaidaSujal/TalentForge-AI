"""
TalentForge AI — Base and Tenant Repository Foundations
======================================================
Defines generic CRUD operations and tenant scoping using company_id.
"""

from __future__ import annotations

import contextlib
import uuid
from typing import Any, Dict, Generic, Optional, Sequence, Set, Type, TypeVar

import psycopg.errors
from sqlalchemy import func, inspect, select
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import (
    DatabaseConstraintError,
    DatabaseError,
    ForeignKeyViolationError,
    NotFoundError,
    RecordAlreadyExistsError,
    ValidationFailedError,
)
from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


@contextlib.asynccontextmanager
async def handle_db_errors():
    """
    Catch driver/SQLAlchemy database integrity errors and translate them
    into safe domain-specific exceptions. Preserves the traceback/chaining.
    """
    try:
        yield
    except IntegrityError as exc:
        orig = exc.orig
        sqlstate = getattr(orig, "sqlstate", None)
        if not sqlstate:
            sqlstate = getattr(orig, "pgcode", None)

        orig_class_name = type(orig).__name__

        # Check against psycopg 3 native errors, SQLSTATE codes, or fallback class names
        if (
            sqlstate == "23505"
            or (
                hasattr(psycopg.errors, "UniqueViolation")
                and isinstance(orig, psycopg.errors.UniqueViolation)
            )
            or orig_class_name == "UniqueViolation"
        ):
            raise RecordAlreadyExistsError(
                message="Unique constraint violation in database", orig_exc=exc
            ) from exc
        elif (
            sqlstate == "23503"
            or (
                hasattr(psycopg.errors, "ForeignKeyViolation")
                and isinstance(orig, psycopg.errors.ForeignKeyViolation)
            )
            or orig_class_name == "ForeignKeyViolation"
        ):
            raise ForeignKeyViolationError(
                message="Foreign key constraint violation in database", orig_exc=exc
            ) from exc
        elif (
            sqlstate == "23514"
            or (
                hasattr(psycopg.errors, "CheckViolation")
                and isinstance(orig, psycopg.errors.CheckViolation)
            )
            or orig_class_name == "CheckViolation"
        ):
            raise DatabaseConstraintError(
                message="Check constraint violation in database", orig_exc=exc
            ) from exc
        else:
            raise DatabaseError(
                message=f"Integrity check failed: {orig_class_name}"
            ) from exc
    except DBAPIError as exc:
        raise DatabaseError(
            message=f"Database execution failure: {type(exc).__name__}"
        ) from exc


class BaseRepository(Generic[ModelType]):
    """
    Generic asynchronous SQLAlchemy repository implementing base CRUD.
    """

    PROTECTED_FIELDS: Set[str] = {"id", "company_id", "created_at", "updated_at"}
    ALLOWED_FILTER_FIELDS: Set[str] = set()
    ALLOWED_SORT_FIELDS: Set[str] = set()

    def __init__(self, db: AsyncSession, model: Type[ModelType]):
        self.db = db
        self.model = model

    def _validate_payload(self, obj_in: Dict[str, Any]) -> None:
        """Validate payload keys to prevent mass assignment of protected or unknown fields."""
        # 1. Block protected fields
        for field in self.PROTECTED_FIELDS:
            if field in obj_in:
                raise ValidationFailedError(
                    f"Field '{field}' is protected and cannot be assigned."
                )

        # 2. Block unknown fields
        model_columns = {c.key for c in inspect(self.model).mapper.column_attrs}
        for key in obj_in.keys():
            if key not in model_columns:
                raise ValidationFailedError(
                    f"Field '{key}' is not a valid attribute for model '{self.model.__name__}'."
                )

    def _validate_query_params(
        self, skip: int, limit: int, sort_by: Optional[str], filters: Dict[str, Any]
    ) -> None:
        """Enforce query bounds, sorting, and filtering safety."""
        if skip < 0:
            raise ValidationFailedError(
                "Pagination parameter 'skip' must be greater than or equal to 0."
            )
        if limit < 1 or limit > 100:
            raise ValidationFailedError(
                "Pagination parameter 'limit' must be between 1 and 100."
            )

        if sort_by and sort_by not in self.ALLOWED_SORT_FIELDS:
            raise ValidationFailedError(
                f"Sorting by field '{sort_by}' is not allowed or supported."
            )

        for key in filters.keys():
            if key not in self.ALLOWED_FILTER_FIELDS:
                raise ValidationFailedError(
                    f"Filtering by field '{key}' is not allowed or supported."
                )

    async def get(self, id: uuid.UUID) -> Optional[ModelType]:
        """Retrieve a record by ID."""
        query = select(self.model).where(self.model.id == id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        sort_by: Optional[str] = None,
        descending: bool = False,
        **filters: Any,
    ) -> Sequence[ModelType]:
        """List multiple records with validation, sorting, pagination, and deterministic secondary sorting."""
        self._validate_query_params(skip, limit, sort_by, filters)

        query = select(self.model)
        for key, value in filters.items():
            query = query.where(getattr(self.model, key) == value)

        if sort_by:
            sort_attr = getattr(self.model, sort_by)
            query = query.order_by(sort_attr.desc() if descending else sort_attr.asc())
        elif hasattr(self.model, "created_at"):
            query = query.order_by(self.model.created_at.asc())

        query = query.order_by(self.model.id.asc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """Insert a record and flush it."""
        self._validate_payload(obj_in)
        async with handle_db_errors():
            db_obj = self.model(**obj_in)
            self.db.add(db_obj)
            await self.db.flush()
            return db_obj

    async def update(self, db_obj: ModelType, obj_in: Dict[str, Any]) -> ModelType:
        """Update a record and flush it."""
        self._validate_payload(obj_in)
        async with handle_db_errors():
            for field, value in obj_in.items():
                setattr(db_obj, field, value)
            self.db.add(db_obj)
            await self.db.flush()
            return db_obj

    async def delete(self, id: uuid.UUID) -> bool:
        """Physically delete a record and flush it."""
        db_obj = await self.get(id)
        if not db_obj:
            return False
        async with handle_db_errors():
            await self.db.delete(db_obj)
            await self.db.flush()
            return True

    async def exists(self, id: uuid.UUID) -> bool:
        """Check record existence."""
        query = select(func.count()).select_from(self.model).where(self.model.id == id)
        result = await self.db.execute(query)
        return (result.scalar() or 0) > 0

    async def count(self, **filters: Any) -> int:
        """Count records matching safe filters."""
        self._validate_query_params(0, 10, None, filters)
        query = select(func.count()).select_from(self.model)
        for key, value in filters.items():
            query = query.where(getattr(self.model, key) == value)
        result = await self.db.execute(query)
        return result.scalar() or 0


class TenantRepository(BaseRepository[ModelType]):
    """
    Subclass of BaseRepository enforcing strict company_id tenant boundaries.
    """

    def __init__(self, db: AsyncSession, model: Type[ModelType], company_id: uuid.UUID):
        super().__init__(db, model)
        self.company_id = company_id

    async def get(
        self, id: uuid.UUID, include_deleted: bool = False
    ) -> Optional[ModelType]:
        """Get record scoped by tenant company_id."""
        query = select(self.model).where(
            self.model.id == id, self.model.company_id == self.company_id
        )
        query = self._apply_soft_delete_filter(query, include_deleted)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        sort_by: Optional[str] = None,
        descending: bool = False,
        include_deleted: bool = False,
        **filters: Any,
    ) -> Sequence[ModelType]:
        """List records scoped by tenant company_id."""
        self._validate_query_params(skip, limit, sort_by, filters)

        query = select(self.model).where(self.model.company_id == self.company_id)
        for key, value in filters.items():
            query = query.where(getattr(self.model, key) == value)

        query = self._apply_soft_delete_filter(query, include_deleted)

        if sort_by:
            sort_attr = getattr(self.model, sort_by)
            query = query.order_by(sort_attr.desc() if descending else sort_attr.asc())
        elif hasattr(self.model, "created_at"):
            query = query.order_by(self.model.created_at.asc())

        query = query.order_by(self.model.id.asc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """Create a record forcing the repository's authoritative company_id internally after validation."""
        self._validate_payload(obj_in)
        async with handle_db_errors():
            db_obj = self.model(**obj_in, company_id=self.company_id)
            self.db.add(db_obj)
            await self.db.flush()
            return db_obj

    async def update(self, record_id: uuid.UUID, obj_in: Dict[str, Any]) -> ModelType:
        """Update a tenant record fetched by record_id and company_id, rejecting company_id edits."""
        # Fetch using direct select to bypass soft-delete/inactive filters (e.g. for reactivation/restoration)
        query = select(self.model).where(
            self.model.id == record_id, self.model.company_id == self.company_id
        )
        result = await self.db.execute(query)
        db_obj = result.scalar_one_or_none()
        if not db_obj:
            raise NotFoundError(self.model.__name__, record_id)

        self._validate_payload(obj_in)
        async with handle_db_errors():
            for field, value in obj_in.items():
                setattr(db_obj, field, value)
            self.db.add(db_obj)
            await self.db.flush()
            return db_obj

    async def delete(self, id: uuid.UUID) -> bool:
        raise NotImplementedError(
            "Deletion rules must be explicitly defined in subclass repositories."
        )

    async def exists(self, id: uuid.UUID, include_deleted: bool = False) -> bool:
        """Check record existence scoped to tenant."""
        query = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.id == id, self.model.company_id == self.company_id)
        )
        query = self._apply_soft_delete_filter(query, include_deleted)
        result = await self.db.execute(query)
        return (result.scalar() or 0) > 0

    async def count(self, include_deleted: bool = False, **filters: Any) -> int:
        """Count records scoped to tenant."""
        self._validate_query_params(0, 10, None, filters)
        query = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.company_id == self.company_id)
        )
        for key, value in filters.items():
            query = query.where(getattr(self.model, key) == value)
        query = self._apply_soft_delete_filter(query, include_deleted)
        result = await self.db.execute(query)
        return result.scalar() or 0

    def _apply_soft_delete_filter(self, query, include_deleted: bool):
        if not include_deleted:
            if hasattr(self.model, "is_deleted"):
                query = query.where(self.model.is_deleted.is_(False))
            elif hasattr(self.model, "is_active"):
                query = query.where(self.model.is_active.is_(True))
        return query
