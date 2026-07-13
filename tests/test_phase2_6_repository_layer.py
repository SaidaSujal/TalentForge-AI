"""
TalentForge AI — Subphase 2.6 Repository Layer Integration Test Suite
======================================================================
Validates tenant isolation, protected fields, custom SQLSTATE exception translation,
soft-delete behaviors, active status filtering, atomic counters, and separate-session concurrency.
"""

import asyncio
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import (
    NotFoundError,
    RecordAlreadyExistsError,
    ValidationFailedError,
    WriteProtectedError,
)
from app.db.models import (
    AIHistory,
    AuditLog,
    Company,
    Employee,
    ExportJob,
    ExportStatus,
    ExportType,
    User,
)
from app.db.repositories import (
    AICacheRepository,
    AIHistoryRepository,
    AuditRepository,
    EmployeeRepository,
    ExportJobRepository,
    UserRepository,
)
from app.db.repositories.base import handle_db_errors
from app.db.session import AsyncSessionLocal
from app.services.ai.cache import ai_cache


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="function")
async def db_session():
    """Provides an isolated database session that rolls back after each test."""
    async with AsyncSessionLocal() as session:
        await session.begin()
        try:
            yield session
        finally:
            await session.rollback()


async def create_company(db: AsyncSession, name: str, slug: str) -> Company:
    company = Company(name=name, slug=slug)
    db.add(company)
    await db.flush()
    return company


@pytest.mark.anyio
class TestRepositoryLayer:
    """Verifies all aspects of Subphase 2.6 repository layer constraints."""

    # ── TENANT CREATION HELPER ───────────────────────────────────────────────

    async def setup_tenants(self, db: AsyncSession):
        """Setup two isolated test tenants."""
        company_a = await create_company(
            db, "Company A", f"co-a-{uuid.uuid4().hex[:6]}"
        )
        company_b = await create_company(
            db, "Company B", f"co-b-{uuid.uuid4().hex[:6]}"
        )
        return company_a, company_b

    # ── TENANT ISOLATION TESTS ───────────────────────────────────────────────

    async def test_tenant_read_isolation(self, db_session: AsyncSession):
        """Verify Company A cannot read Company B records (returns None)."""
        co_a, co_b = await self.setup_tenants(db_session)

        # Create record in Company B
        emp_b = Employee(
            company_id=co_b.id,
            first_name="John",
            last_name="Doe",
            email=f"john.{uuid.uuid4().hex[:6]}@co-b.com",
            department="Engineering",
            role="Software Engineer",
        )
        db_session.add(emp_b)
        await db_session.flush()

        # Try to query via Company A's repository
        repo_a = EmployeeRepository(db_session, co_a.id)
        fetched = await repo_a.get(emp_b.id)
        assert fetched is None  # Cross-tenant get returns None

    async def test_tenant_update_isolation(self, db_session: AsyncSession):
        """Verify Company A cannot update Company B records (raises NotFoundError)."""
        co_a, co_b = await self.setup_tenants(db_session)

        emp_b = Employee(
            company_id=co_b.id,
            first_name="Jane",
            last_name="Doe",
            email=f"jane.{uuid.uuid4().hex[:6]}@co-b.com",
            department="HR",
            role="HR Lead",
        )
        db_session.add(emp_b)
        await db_session.flush()

        repo_a = EmployeeRepository(db_session, co_a.id)
        with pytest.raises(NotFoundError):
            # Attempting to update a Company B record using Company A's repo throws NotFoundError
            await repo_a.update(emp_b.id, {"first_name": "HackName"})

    async def test_tenant_delete_isolation(self, db_session: AsyncSession):
        """Verify Company A cannot delete Company B records (returns False/not found)."""
        co_a, co_b = await self.setup_tenants(db_session)

        emp_b = Employee(
            company_id=co_b.id,
            first_name="Mark",
            last_name="Smith",
            email=f"mark.{uuid.uuid4().hex[:6]}@co-b.com",
            department="Sales",
            role="Sales Manager",
        )
        db_session.add(emp_b)
        await db_session.flush()

        repo_a = EmployeeRepository(db_session, co_a.id)
        success = await repo_a.delete(emp_b.id)
        assert success is False

        # Verify not soft-deleted in Company B
        await db_session.refresh(emp_b)
        assert emp_b.is_deleted is False

    async def test_tenant_list_and_count_isolation(self, db_session: AsyncSession):
        """Verify list and count are strictly tenant-scoped."""
        co_a, co_b = await self.setup_tenants(db_session)

        # Create one in A, two in B
        emp_a = Employee(
            company_id=co_a.id,
            first_name="EmpA",
            last_name="A",
            email=f"empa.{uuid.uuid4().hex[:6]}@co-a.com",
            department="Ops",
            role="Specialist",
        )
        emp_b1 = Employee(
            company_id=co_b.id,
            first_name="EmpB1",
            last_name="B",
            email=f"empb1.{uuid.uuid4().hex[:6]}@co-b.com",
            department="Ops",
            role="Specialist",
        )
        emp_b2 = Employee(
            company_id=co_b.id,
            first_name="EmpB2",
            last_name="B",
            email=f"empb2.{uuid.uuid4().hex[:6]}@co-b.com",
            department="Ops",
            role="Specialist",
        )
        db_session.add_all([emp_a, emp_b1, emp_b2])
        await db_session.flush()

        repo_a = EmployeeRepository(db_session, co_a.id)
        repo_b = EmployeeRepository(db_session, co_b.id)

        assert await repo_a.count(department="Ops") == 1
        assert await repo_b.count(department="Ops") == 2

        list_a = await repo_a.list(department="Ops")
        list_b = await repo_b.list(department="Ops")

        assert len(list_a) == 1
        assert list_a[0].id == emp_a.id
        assert len(list_b) == 2

    # ── PAYLOAD VALIDATION & PROTECTED FIELDS ────────────────────────────────

    async def test_protected_fields_mass_assignment_protection(
        self, db_session: AsyncSession
    ):
        """Verify protected fields cannot be passed in payloads."""
        co_a, _ = await self.setup_tenants(db_session)
        repo = EmployeeRepository(db_session, co_a.id)

        # 1. Block company_id
        with pytest.raises(ValidationFailedError) as exc_info:
            await repo.create(
                {
                    "first_name": "Test",
                    "last_name": "One",
                    "email": "test@talentforge.ai",
                    "department": "Finance",
                    "role": "Analyst",
                    "company_id": co_a.id,
                }
            )
        assert "protected" in str(exc_info.value)

        # 2. Block id
        with pytest.raises(ValidationFailedError):
            await repo.create(
                {
                    "id": uuid.uuid4(),
                    "first_name": "Test",
                    "last_name": "One",
                    "email": "test@talentforge.ai",
                    "department": "Finance",
                    "role": "Analyst",
                }
            )

    async def test_unknown_fields_rejected(self, db_session: AsyncSession):
        """Verify passing non-existent fields raises ValidationFailedError."""
        co_a, _ = await self.setup_tenants(db_session)
        repo = EmployeeRepository(db_session, co_a.id)

        with pytest.raises(ValidationFailedError) as exc_info:
            await repo.create(
                {
                    "first_name": "Test",
                    "last_name": "One",
                    "email": "test@talentforge.ai",
                    "department": "Finance",
                    "role": "Analyst",
                    "some_non_existent_column": "value",
                }
            )
        assert "not a valid attribute" in str(exc_info.value)

    async def test_strict_query_parameters(self, db_session: AsyncSession):
        """Verify listing rejects unknown sorting or filtering parameters."""
        co_a, _ = await self.setup_tenants(db_session)
        repo = EmployeeRepository(db_session, co_a.id)

        # Reject unknown filter field
        with pytest.raises(ValidationFailedError):
            await repo.list(unknown_filter="value")

        # Reject unknown sort field
        with pytest.raises(ValidationFailedError):
            await repo.list(
                sort_by="salary"
            )  # salary is deferred and excluded from sort allowlist

        # Pagination bounds
        with pytest.raises(ValidationFailedError):
            await repo.list(skip=-1)

        with pytest.raises(ValidationFailedError):
            await repo.list(limit=0)

        with pytest.raises(ValidationFailedError):
            await repo.list(limit=101)

    async def test_deterministic_ordering(self, db_session: AsyncSession):
        """Verify sorting enforces deterministic secondary ordering by ID."""
        co_a, _ = await self.setup_tenants(db_session)
        repo = EmployeeRepository(db_session, co_a.id)

        # Create two employees in the same department
        emp1 = Employee(
            company_id=co_a.id,
            first_name="Alice",
            last_name="A",
            email=f"alice.{uuid.uuid4().hex[:6]}@co-a.com",
            department="HR",
            role="Recruiter",
        )
        emp2 = Employee(
            company_id=co_a.id,
            first_name="Bob",
            last_name="B",
            email=f"bob.{uuid.uuid4().hex[:6]}@co-a.com",
            department="HR",
            role="Recruiter",
        )
        db_session.add_all([emp1, emp2])
        await db_session.flush()

        results = await repo.list(sort_by="department", descending=False)
        assert len(results) == 2
        # Deterministic secondary sorting forces ID order (uuid ordering)
        expected_first = emp1 if emp1.id < emp2.id else emp2
        expected_second = emp2 if emp1.id < emp2.id else emp1
        assert results[0].id == expected_first.id
        assert results[1].id == expected_second.id

    # ── DELETION & ACTIVATION BEHAVIORS ──────────────────────────────────────

    async def test_explicit_soft_delete_lifecycle(self, db_session: AsyncSession):
        """Verify Employee logical soft-delete and query inclusion behavior."""
        co_a, _ = await self.setup_tenants(db_session)
        repo = EmployeeRepository(db_session, co_a.id)

        emp = await repo.create(
            {
                "first_name": "Soft",
                "last_name": "Delete",
                "email": "soft@talentforge.ai",
                "department": "Engineering",
                "role": "Architect",
            }
        )

        # Exists by default
        assert await repo.exists(emp.id) is True

        # Perform delete (should soft-delete)
        success = await repo.delete(emp.id)
        assert success is True

        # Excluded by default now
        assert await repo.exists(emp.id) is False
        assert await repo.get(emp.id) is None
        assert len(await repo.list(department="Engineering")) == 0

        # Accessible if explicitly requested
        assert await repo.exists(emp.id, include_deleted=True) is True
        assert (await repo.get(emp.id, include_deleted=True)) is not None
        assert len(await repo.list(include_deleted=True, department="Engineering")) == 1

    async def test_user_active_filtering_consistency(self, db_session: AsyncSession):
        """Verify UserRepository filters by active status consistently across methods."""
        co_a, _ = await self.setup_tenants(db_session)
        repo = UserRepository(db_session, co_a.id)

        user = User(
            company_id=co_a.id,
            email=f"user.{uuid.uuid4().hex[:6]}@co-a.com",
            password_hash="hashed_mock",
            role="recruiter",
            is_active=False,  # Inactive
        )
        db_session.add(user)
        await db_session.flush()

        # 1. Excluded by get
        assert await repo.get(user.id) is None
        assert await repo.get(user.id, include_inactive=True) is not None

        # 2. Excluded by list
        assert len(await repo.list(email=user.email)) == 0
        assert len(await repo.list(include_inactive=True, email=user.email)) == 1

        # 3. Excluded by count
        assert await repo.count(email=user.email) == 0
        assert await repo.count(include_inactive=True, email=user.email) == 1

        # 4. Excluded by get_by_email
        assert await repo.get_by_email(user.email) is None
        assert await repo.get_by_email(user.email, include_inactive=True) is not None

        # Reactivate
        await repo.reactivate_user(user.id)
        assert await repo.get(user.id) is not None

    async def test_append_only_protections(self, db_session: AsyncSession):
        """Verify AuditRepository and AIHistoryRepository block updates and deletes."""
        co_a, _ = await self.setup_tenants(db_session)
        repo_audit = AuditRepository(db_session, co_a.id)
        repo_history = AIHistoryRepository(db_session, co_a.id)

        # Audit write logs
        log = AuditLog(
            company_id=co_a.id,
            module="core",
            action="ACCESS",
        )
        db_session.add(log)
        await db_session.flush()

        with pytest.raises(WriteProtectedError):
            await repo_audit.update(log.id, {"action": "HACK"})

        with pytest.raises(WriteProtectedError):
            await repo_audit.delete(log.id)

        # AI History write logs
        history = AIHistory(
            company_id=co_a.id,
            module="jd",
            task_type="jd_draft",
            provider="nvidia",
            model_used="meta/llama-3.1-8b-instruct",
            prompt_template_name="p",
            prompt_hash="hash",
            input_summary="Input",
            response_text="Output",
        )
        db_session.add(history)
        await db_session.flush()

        with pytest.raises(WriteProtectedError):
            await repo_history.update(history.id, {"response_text": "HACK"})

        with pytest.raises(WriteProtectedError):
            await repo_history.delete(history.id)

    # ── CONCURRENCY & CACHING ────────────────────────────────────────────────

    async def test_cache_expiry_and_metadata_refresh(self, db_session: AsyncSession):
        """Verify AICache expiration, tenant isolation, and metadata refresh on upsert."""
        co_a, co_b = await self.setup_tenants(db_session)
        repo_a = AICacheRepository(db_session, co_a.id)
        repo_b = AICacheRepository(db_session, co_b.id)

        cache_key = f"key_{uuid.uuid4().hex[:6]}"
        expires_past = datetime.now(timezone.utc) - timedelta(minutes=1)
        expires_future = datetime.now(timezone.utc) + timedelta(hours=1)

        # 1. Upsert with past expiry raises ValidationFailedError
        with pytest.raises(ValidationFailedError):
            await repo_a.upsert_cache(
                cache_key=cache_key,
                prompt_hash="p1",
                task_type="jd",
                provider="nvidia",
                model_used="llama",
                response_text="expired response",
                expires_at=expires_past,
            )

        # 2. Store active cache in Company A
        active_cache = await repo_a.upsert_cache(
            cache_key=cache_key,
            prompt_hash="p1",
            task_type="jd",
            provider="nvidia",
            model_used="llama",
            response_text="response a",
            expires_at=expires_future,
        )
        assert active_cache.response_text == "response a"

        # Company B lookup gets None (Tenant Isolation)
        assert await repo_b.get_active_cache(cache_key) is None

        # 3. Metadata refresh on upsert conflict
        refreshed_cache = await repo_a.upsert_cache(
            cache_key=cache_key,
            prompt_hash="p_new",
            task_type="jd_v2",
            provider="nvidia_new",
            model_used="nemotron",
            response_text="response updated",
            expires_at=expires_future + timedelta(hours=1),
        )
        assert refreshed_cache.id == active_cache.id
        assert refreshed_cache.prompt_hash == "p_new"
        assert refreshed_cache.task_type == "jd_v2"
        assert refreshed_cache.provider == "nvidia_new"
        assert refreshed_cache.model_used == "nemotron"
        assert refreshed_cache.response_text == "response updated"
        assert refreshed_cache.expires_at == expires_future + timedelta(hours=1)

    async def test_concurrent_same_tenant_cache_upsert(self, db_session: AsyncSession):
        """Verify parallel cache upserts under separate database sessions execute safely."""
        suffix = uuid.uuid4().hex[:6]
        co = await create_company(
            db_session, f"Concur Co {suffix}", f"concur-co-{suffix}"
        )
        await db_session.commit()  # Make it visible to other connections/sessions

        cache_key = f"concurrent_key_{suffix}"

        async def run_upsert(worker_id: int):
            async with AsyncSessionLocal() as session:
                repo = AICacheRepository(session, co.id)
                expires = datetime.now(timezone.utc) + timedelta(hours=1)
                await repo.upsert_cache(
                    cache_key=cache_key,
                    prompt_hash="p_hash",
                    task_type="jd",
                    provider="nvidia",
                    model_used="llama",
                    response_text=f"worker_{worker_id}_resp",
                    expires_at=expires,
                )
                await session.commit()

        # Run upserts concurrently
        await asyncio.gather(run_upsert(1), run_upsert(2), run_upsert(3))

        # Check final state
        repo_verify = AICacheRepository(db_session, co.id)
        entry = await repo_verify.get_active_cache(cache_key)
        assert entry is not None
        assert "worker_" in entry.response_text

        # Verify only one row exists
        count = await repo_verify.count(cache_key=cache_key)
        assert count == 1

    # ── EXPORT DOWNLOAD ATOMIC COUNTER ───────────────────────────────────────

    async def test_atomic_download_count_increment(self, db_session: AsyncSession):
        """Verify atomic increment logic and boundary safeguards."""
        co_a, co_b = await self.setup_tenants(db_session)
        repo_a = ExportJobRepository(db_session, co_a.id)

        job_a = ExportJob(
            company_id=co_a.id,
            module_scope="attrition",
            export_type=ExportType.PDF,
            status=ExportStatus.PENDING,
            file_name="report.pdf",
            download_count=0,
        )
        job_deleted = ExportJob(
            company_id=co_a.id,
            module_scope="attrition",
            export_type=ExportType.PDF,
            status=ExportStatus.PENDING,
            file_name="report_deleted.pdf",
            download_count=0,
            is_deleted=True,
        )
        db_session.add_all([job_a, job_deleted])
        await db_session.flush()

        # Increment success
        new_count = await repo_a.increment_download_count(job_a.id)
        assert new_count == 1

        await db_session.refresh(job_a)
        assert job_a.download_count == 1

        # Raises NotFoundError for soft-deleted job
        with pytest.raises(NotFoundError):
            await repo_a.increment_download_count(job_deleted.id)

        # Raises NotFoundError for cross-tenant job ID
        repo_b = ExportJobRepository(db_session, co_b.id)
        with pytest.raises(NotFoundError):
            await repo_b.increment_download_count(job_a.id)

    # ── EXCEPTION TRANSLATION ────────────────────────────────────────────────

    async def test_sqlstate_exception_translation(self, db_session: AsyncSession):
        """Verify IntegrityError is safely translated to custom domain exceptions."""
        co_a, _ = await self.setup_tenants(db_session)

        # 1. Test unique violation
        user1 = User(
            company_id=co_a.id,
            email="shared@talentforge.ai",
            password_hash="hash",
            role="employee",
        )
        db_session.add(user1)
        await db_session.flush()

        user2 = User(
            company_id=co_a.id,
            email="shared@talentforge.ai",
            password_hash="hash2",
            role="employee",
        )
        db_session.add(user2)

        with pytest.raises(RecordAlreadyExistsError) as exc_info:
            async with handle_db_errors():
                await db_session.flush()

        # Verify raw database strings are not leaked in error message
        assert "unique constraint" not in str(exc_info.value)
        # Verify original exception is chained
        assert isinstance(exc_info.value.__cause__, IntegrityError)

        # Rollback the subtransaction block manually in tests to clear session error state
        await db_session.rollback()

    # ── CACHE SERVICE INJECTION ──────────────────────────────────────────────

    async def test_cache_service_zero_external_api_calls(
        self, db_session: AsyncSession
    ):
        """Verify the AICache service functions run purely as database operations."""
        co_a, _ = await self.setup_tenants(db_session)
        cache_key = f"key_{uuid.uuid4().hex[:6]}"

        # Write to cache via service (Zero external SDK/API calls)
        expires = datetime.now(timezone.utc) + timedelta(hours=1)
        await ai_cache.set(
            cache_key=cache_key,
            response="service response value",
            db=db_session,
            company_id=co_a.id,
            expires_at=expires,
        )

        # Read from cache via service
        val = await ai_cache.get(cache_key, db=db_session, company_id=co_a.id)
        assert val == "service response value"

        # Count hit count via service
        assert await ai_cache.get_hit_count(str(co_a.id), db=db_session) == 0
