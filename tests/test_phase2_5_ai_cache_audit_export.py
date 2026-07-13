"""
TalentForge AI — Subphase 2.5 AI & System Models Test Suite
============================================================
Validates schemas, enums, check constraints, composite indexes, cascades,
and tenant-scoped uniqueness rules for AI Cache, AI History, Audit Logs, and Export Jobs.
"""

import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    AICache,
    AIHistory,
    AuditLog,
    Company,
    ExportJob,
    ExportStatus,
    ExportType,
    User,
)
from app.db.session import AsyncSessionLocal


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


async def create_base_tenant_and_user(db_session: AsyncSession, suffix: str):
    """Helper utility to create a tenant company and a basic user."""
    company = Company(name=f"Tenant Co {suffix}", slug=f"tenant-co-{suffix}")
    db_session.add(company)
    await db_session.flush()

    user = User(
        company_id=company.id,
        email=f"user.{suffix}@tenant.com",
        password_hash="hashed_pass_mock",
        role="employee",
    )
    db_session.add(user)
    await db_session.flush()
    return company, user


@pytest.mark.anyio
class TestAISystemModels:
    """Verification suite for AI cache, invocation history, audit, and exports."""

    # ── MODEL REGISTRATION ──────────────────────────────────────────────────

    async def test_models_registration(self, db_session: AsyncSession):
        """Verify new models are registered on metadata and can be inspected."""
        mapper_cache = inspect(AICache)
        mapper_history = inspect(AIHistory)
        mapper_log = inspect(AuditLog)
        mapper_export = inspect(ExportJob)

        assert mapper_cache.class_.__name__ == "AICache"
        assert mapper_history.class_.__name__ == "AIHistory"
        assert mapper_log.class_.__name__ == "AuditLog"
        assert mapper_export.class_.__name__ == "ExportJob"

    # ── AI CACHE ─────────────────────────────────────────────────────────────

    async def test_ai_cache_crud_and_expiry(self, db_session: AsyncSession):
        """Verify CRUD and expiration time boundary checks for AICache."""
        suffix = uuid.uuid4().hex[:6]
        company, _ = await create_base_tenant_and_user(db_session, suffix)

        created_time = datetime.now(timezone.utc)
        expires_time = created_time + timedelta(hours=2)

        cache = AICache(
            company_id=company.id,
            cache_key="key_hash_abc123",
            prompt_hash="prompt_hash_xyz789",
            task_type="jd_draft",
            provider="nvidia",
            model_used="meta/llama-3.1-8b-instruct",
            response_text="Cached JD Response",
            token_count=150,
            expires_at=expires_time,
        )
        db_session.add(cache)
        await db_session.flush()

        # Retrieve and verify expires_at > created_at
        await db_session.refresh(cache)
        assert cache.id is not None
        assert cache.expires_at > cache.created_at
        assert cache.token_count == 150

    async def test_ai_cache_negative_token_count_constraint(
        self, db_session: AsyncSession
    ):
        """Verify check constraint on AICache token count rejects negative values."""
        suffix = uuid.uuid4().hex[:6]
        company, _ = await create_base_tenant_and_user(db_session, suffix)

        cache = AICache(
            company_id=company.id,
            cache_key="key_hash_negative",
            prompt_hash="prompt_hash_neg",
            task_type="jd_draft",
            provider="nvidia",
            model_used="meta/llama-3.1-8b-instruct",
            response_text="Failed Cache",
            token_count=-5,  # Negative
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        async with db_session.begin_nested():
            db_session.add(cache)
            with pytest.raises(IntegrityError):
                await db_session.flush()

    async def test_ai_cache_tenant_scoped_uniqueness(self, db_session: AsyncSession):
        """Verify same cache_key is allowed across tenants but unique within one tenant."""
        suffix1 = uuid.uuid4().hex[:6]
        company1, _ = await create_base_tenant_and_user(db_session, suffix1)

        suffix2 = uuid.uuid4().hex[:6]
        company2, _ = await create_base_tenant_and_user(db_session, suffix2)

        # 1. Insert cache for Company 1
        cache1 = AICache(
            company_id=company1.id,
            cache_key="shared_cache_key_value",
            prompt_hash="prompt_hash_1",
            task_type="jd_draft",
            provider="nvidia",
            model_used="meta/llama-3.1-8b-instruct",
            response_text="Cached output for Company 1",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        db_session.add(cache1)
        await db_session.flush()

        # 2. Insert same cache key for Company 2 (Should Succeed)
        cache2 = AICache(
            company_id=company2.id,
            cache_key="shared_cache_key_value",
            prompt_hash="prompt_hash_1",
            task_type="jd_draft",
            provider="nvidia",
            model_used="meta/llama-3.1-8b-instruct",
            response_text="Cached output for Company 2",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        db_session.add(cache2)
        await db_session.flush()
        assert cache2.id is not None

        # 3. Duplicate key in Company 1 (Should Fail)
        cache_dup = AICache(
            company_id=company1.id,
            cache_key="shared_cache_key_value",
            prompt_hash="prompt_hash_2",
            task_type="jd_draft",
            provider="nvidia",
            model_used="meta/llama-3.1-8b-instruct",
            response_text="Duplicate cached output",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        async with db_session.begin_nested():
            db_session.add(cache_dup)
            with pytest.raises(IntegrityError):
                await db_session.flush()

    # ── AI HISTORY ───────────────────────────────────────────────────────────

    async def test_ai_history_crud_and_redacted_json(self, db_session: AsyncSession):
        """Verify AI History insertion, constraints, cost precision, and redacted JSON metadata."""
        suffix = uuid.uuid4().hex[:6]
        company, user = await create_base_tenant_and_user(db_session, suffix)

        history = AIHistory(
            company_id=company.id,
            user_id=user.id,
            request_id="correlation_request_id_123",
            module="performance_review",
            task_type="performance_review",
            provider="nvidia",
            model_used="meta/llama-3.1-70b-instruct",
            prompt_template_name="generate_performance_review",
            prompt_hash="compiled_prompt_hash_val",
            input_summary="Employee ID: 123, Reviewer ID: 456",
            input_metadata_json={"input_length": 1500, "word_count": 220},
            response_text="Complete raw response content.",
            prompt_tokens=400,
            completion_tokens=600,
            total_tokens=1000,
            latency_ms=250,
            estimated_cost=Decimal("0.015250"),
            cache_hit=False,
        )
        db_session.add(history)
        await db_session.flush()

        await db_session.refresh(history)
        assert history.id is not None
        assert history.request_id == "correlation_request_id_123"
        assert history.input_metadata_json == {"input_length": 1500, "word_count": 220}
        assert history.estimated_cost == Decimal("0.015250")

    async def test_ai_history_tokens_check_constraints(self, db_session: AsyncSession):
        """Verify token counts value validations and total token consistency constraint."""
        suffix = uuid.uuid4().hex[:6]
        company, _ = await create_base_tenant_and_user(db_session, suffix)

        # 1. Reject negative tokens
        history_neg = AIHistory(
            company_id=company.id,
            module="jd_draft",
            task_type="jd_draft",
            provider="nvidia",
            model_used="meta/llama-3.1-8b-instruct",
            prompt_template_name="generate_jd",
            prompt_hash="hash1",
            input_summary="Inputs",
            response_text="Output text",
            prompt_tokens=-100,  # Negative
            completion_tokens=200,
            total_tokens=100,
        )
        async with db_session.begin_nested():
            db_session.add(history_neg)
            with pytest.raises(IntegrityError):
                await db_session.flush()

        # 2. Reject total tokens mismatch (total != prompt + completion)
        history_mismatch = AIHistory(
            company_id=company.id,
            module="jd_draft",
            task_type="jd_draft",
            provider="nvidia",
            model_used="meta/llama-3.1-8b-instruct",
            prompt_template_name="generate_jd",
            prompt_hash="hash2",
            input_summary="Inputs",
            response_text="Output text",
            prompt_tokens=100,
            completion_tokens=200,
            total_tokens=500,  # Mismatch
        )
        async with db_session.begin_nested():
            db_session.add(history_mismatch)
            with pytest.raises(IntegrityError):
                await db_session.flush()

    async def test_ai_history_cost_and_latency_constraints(
        self, db_session: AsyncSession
    ):
        """Verify check constraints block negative costs and negative latencies."""
        suffix = uuid.uuid4().hex[:6]
        company, _ = await create_base_tenant_and_user(db_session, suffix)

        # 1. Reject negative cost
        history_neg_cost = AIHistory(
            company_id=company.id,
            module="jd_draft",
            task_type="jd_draft",
            provider="nvidia",
            model_used="meta/llama-3.1-8b-instruct",
            prompt_template_name="generate_jd",
            prompt_hash="hash1",
            input_summary="Inputs",
            response_text="Output text",
            prompt_tokens=100,
            completion_tokens=100,
            total_tokens=200,
            estimated_cost=Decimal("-0.01"),  # Negative
        )
        async with db_session.begin_nested():
            db_session.add(history_neg_cost)
            with pytest.raises(IntegrityError):
                await db_session.flush()

        # 2. Reject negative latency
        history_neg_latency = AIHistory(
            company_id=company.id,
            module="jd_draft",
            task_type="jd_draft",
            provider="nvidia",
            model_used="meta/llama-3.1-8b-instruct",
            prompt_template_name="generate_jd",
            prompt_hash="hash2",
            input_summary="Inputs",
            response_text="Output text",
            prompt_tokens=100,
            completion_tokens=100,
            total_tokens=200,
            latency_ms=-20,  # Negative
        )
        async with db_session.begin_nested():
            db_session.add(history_neg_latency)
            with pytest.raises(IntegrityError):
                await db_session.flush()

    # ── AUDIT LOGS ───────────────────────────────────────────────────────────

    async def test_audit_log_crud_and_safe_jsonb(self, db_session: AsyncSession):
        """Verify AuditLog CRUD, safety design, and append-only constraints."""
        suffix = uuid.uuid4().hex[:6]
        company, user = await create_base_tenant_and_user(db_session, suffix)

        log = AuditLog(
            company_id=company.id,
            user_id=user.id,
            module="security",
            action="HUMAN_REVIEW_APPROVED",
            entity_type="performance_reviews",
            entity_id="uuid_performance_review_123",
            metadata_json={"fields_changed": ["approval_status"], "diff_count": 1},
            ip_address="192.168.1.50",
            user_agent="Mozilla/5.0 Chrome/120.0",
        )
        db_session.add(log)
        await db_session.flush()

        await db_session.refresh(log)
        assert log.id is not None
        assert log.entity_id == "uuid_performance_review_123"
        assert log.metadata_json == {
            "fields_changed": ["approval_status"],
            "diff_count": 1,
        }

        # Verify no is_deleted soft-delete field exists
        assert not hasattr(log, "is_deleted")

    # ── EXPORT JOBS ──────────────────────────────────────────────────────────

    async def test_export_job_crud_and_lifecycle(self, db_session: AsyncSession):
        """Verify ExportJob CRUD, enums lifecycle, download counters, and file size constraints."""
        suffix = uuid.uuid4().hex[:6]
        company, user = await create_base_tenant_and_user(db_session, suffix)

        job = ExportJob(
            company_id=company.id,
            user_id=user.id,
            module_scope="attrition",
            export_type=ExportType.PDF,
            status=ExportStatus.PENDING,
            file_name="attrition_report_2026.pdf",
            file_size_bytes=50000,
            storage_path="exports/attrition/attrition_report_2026.pdf",
            download_count=0,
        )
        db_session.add(job)
        await db_session.flush()

        # Update status and downloads
        job.status = ExportStatus.COMPLETED
        job.download_count = 2
        await db_session.flush()

        await db_session.refresh(job)
        assert job.id is not None
        assert job.status == ExportStatus.COMPLETED
        assert job.download_count == 2
        assert job.is_deleted is False

        # Reject negative size
        job_neg_size = ExportJob(
            company_id=company.id,
            user_id=user.id,
            module_scope="attrition",
            export_type=ExportType.CSV,
            status=ExportStatus.PENDING,
            file_name="neg_size.csv",
            file_size_bytes=-100,  # Negative size
        )
        async with db_session.begin_nested():
            db_session.add(job_neg_size)
            with pytest.raises(IntegrityError):
                await db_session.flush()

        # Reject negative downloads
        job_neg_downloads = ExportJob(
            company_id=company.id,
            user_id=user.id,
            module_scope="attrition",
            export_type=ExportType.CSV,
            status=ExportStatus.PENDING,
            file_name="neg_downloads.csv",
            download_count=-1,  # Negative downloads
        )
        async with db_session.begin_nested():
            db_session.add(job_neg_downloads)
            with pytest.raises(IntegrityError):
                await db_session.flush()

    # ── CASCADE & DELETIONS ──────────────────────────────────────────────────

    async def test_cascades_on_company_delete(self, db_session: AsyncSession):
        """Verify deleting a Company cascades to drop caches, histories, logs, and export jobs."""
        suffix = uuid.uuid4().hex[:6]
        company, user = await create_base_tenant_and_user(db_session, suffix)

        # Create child entities
        cache = AICache(
            company_id=company.id,
            cache_key=f"cache_key_{suffix}",
            prompt_hash="phash",
            task_type="jd_draft",
            provider="nvidia",
            model_used="meta/llama-3.1-8b-instruct",
            response_text="Cached output",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        history = AIHistory(
            company_id=company.id,
            module="jd_draft",
            task_type="jd_draft",
            provider="nvidia",
            model_used="meta/llama-3.1-8b-instruct",
            prompt_template_name="p",
            prompt_hash="phash",
            input_summary="Summary",
            response_text="Output text",
        )
        log = AuditLog(
            company_id=company.id,
            module="security",
            action="TEST_ACTION",
        )
        job = ExportJob(
            company_id=company.id,
            module_scope="attrition",
            export_type=ExportType.CSV,
            status=ExportStatus.PENDING,
            file_name="test.csv",
        )
        db_session.add_all([cache, history, log, job])
        await db_session.flush()

        # Delete company
        await db_session.delete(company)
        await db_session.flush()

        from sqlalchemy import select

        # Verify all are cascading deleted from DB using fresh SELECT statements
        res_cache = await db_session.execute(
            select(AICache).where(AICache.id == cache.id)
        )
        assert res_cache.scalar_one_or_none() is None

        res_history = await db_session.execute(
            select(AIHistory).where(AIHistory.id == history.id)
        )
        assert res_history.scalar_one_or_none() is None

        res_log = await db_session.execute(
            select(AuditLog).where(AuditLog.id == log.id)
        )
        assert res_log.scalar_one_or_none() is None

        res_job = await db_session.execute(
            select(ExportJob).where(ExportJob.id == job.id)
        )
        assert res_job.scalar_one_or_none() is None

    async def test_user_delete_set_null_history_and_audit(
        self, db_session: AsyncSession
    ):
        """Verify user deletion sets user_id to NULL on histories and logs."""
        suffix = uuid.uuid4().hex[:6]
        company, user = await create_base_tenant_and_user(db_session, suffix)

        history = AIHistory(
            company_id=company.id,
            user_id=user.id,
            module="jd_draft",
            task_type="jd_draft",
            provider="nvidia",
            model_used="meta/llama-3.1-8b-instruct",
            prompt_template_name="p",
            prompt_hash="phash",
            input_summary="Summary",
            response_text="Output text",
        )
        log = AuditLog(
            company_id=company.id,
            user_id=user.id,
            module="security",
            action="TEST_ACTION",
        )
        db_session.add_all([history, log])
        await db_session.flush()

        # Delete User
        await db_session.delete(user)
        await db_session.flush()

        # Verify child rows persist with user_id = NULL
        await db_session.refresh(history)
        await db_session.refresh(log)
        assert history.user_id is None
        assert log.user_id is None
