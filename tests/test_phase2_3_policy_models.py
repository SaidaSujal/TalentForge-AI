import subprocess
import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, StatementError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import Company, PolicyChunk, PolicyDocument, PolicyDocumentStatus
from app.db.session import AsyncSessionLocal


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="function")
async def db_session():
    """Provides a database session that rolls back changes after each test."""
    async with AsyncSessionLocal() as session:
        await session.begin()
        try:
            yield session
        finally:
            await session.rollback()


@pytest.mark.anyio
class TestPolicyModels:
    """Verify constraints, relationships, pgvector, and behavior of Policy models."""

    async def test_policy_document_creation_success(self, db_session: AsyncSession):
        """Verify PolicyDocument creation, defaults, category, and timestamps."""
        company = Company(name="Policy Co", slug=f"policy-co-{uuid.uuid4().hex[:6]}")
        db_session.add(company)
        await db_session.flush()

        doc = PolicyDocument(
            company_id=company.id,
            name="Employee Handbook 2026",
            description="Official corporate guidelines and employee handbooks.",
            category="Compliance",
            status=PolicyDocumentStatus.UPLOADED,
            file_name="handbook_2026.pdf",
            file_path="/tmp/handbook_2026.pdf",
            file_size=2048576,
            mime_type="application/pdf",
            document_hash="doc_hash_abc123xyz789",
            chunk_count=0,
            indexed_at=None,
        )
        db_session.add(doc)
        await db_session.flush()

        # Retrieve and assert
        q = select(PolicyDocument).where(PolicyDocument.id == doc.id)
        res = await db_session.execute(q)
        db_doc = res.scalar_one_or_none()

        assert db_doc is not None
        assert db_doc.name == "Employee Handbook 2026"
        assert db_doc.category == "Compliance"
        assert db_doc.status == PolicyDocumentStatus.UPLOADED
        assert db_doc.document_hash == "doc_hash_abc123xyz789"
        assert db_doc.chunk_count == 0
        assert db_doc.indexed_at is None
        assert db_doc.is_deleted is False
        assert db_doc.created_at is not None

    async def test_policy_chunk_creation_and_vector(self, db_session: AsyncSession):
        """Verify PolicyChunk creation, fields, JSONB metadata, and pgvector storage."""
        company = Company(name="Vector Co", slug=f"vector-co-{uuid.uuid4().hex[:6]}")
        db_session.add(company)
        await db_session.flush()

        doc = PolicyDocument(
            company_id=company.id,
            name="Travel Policy",
            category="Finance",
            file_name="travel.docx",
            file_size=10240,
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            document_hash="hash_travel_policy",
        )
        db_session.add(doc)
        await db_session.flush()

        mock_embedding = [0.1] * 1024  # 1024-dimension float array
        chunk = PolicyChunk(
            company_id=company.id,
            document_id=doc.id,
            chunk_index=0,
            section_title="2.1 Air Travel Rules",
            page_number=4,
            token_count=150,
            content="Employees must book economy flights for journeys under 6 hours.",
            embedding=mock_embedding,
            metadata_json={"parent_section": "Travel Expenses", "word_count": 12},
        )
        db_session.add(chunk)
        await db_session.flush()

        # Query and assert
        q = select(PolicyChunk).where(PolicyChunk.id == chunk.id)
        res = await db_session.execute(q)
        db_chunk = res.scalar_one_or_none()

        assert db_chunk is not None
        assert db_chunk.chunk_index == 0
        assert db_chunk.section_title == "2.1 Air Travel Rules"
        assert db_chunk.page_number == 4
        assert db_chunk.token_count == 150
        assert (
            db_chunk.content
            == "Employees must book economy flights for journeys under 6 hours."
        )
        assert db_chunk.metadata_json == {
            "parent_section": "Travel Expenses",
            "word_count": 12,
        }
        assert len(db_chunk.embedding) == 1024
        assert abs(db_chunk.embedding[0] - 0.1) < 1e-6

    async def test_wrong_vector_dimension_rejection(self, db_session: AsyncSession):
        """Verify pgvector type verification rejects invalid dimensions (e.g. 512)."""
        company = Company(name="Dimension Co", slug=f"dim-co-{uuid.uuid4().hex[:6]}")
        db_session.add(company)
        await db_session.flush()

        doc = PolicyDocument(
            company_id=company.id,
            name="Dimension Policy",
            category="Security",
            file_name="dim.pdf",
            file_size=5000,
            mime_type="application/pdf",
            document_hash="hash_dim_policy",
        )
        db_session.add(doc)
        await db_session.flush()

        invalid_embedding = [0.5] * 512  # Invalid dimension (should be 1024)
        chunk = PolicyChunk(
            company_id=company.id,
            document_id=doc.id,
            chunk_index=0,
            content="Test content",
            embedding=invalid_embedding,
        )

        # StatementError is thrown during binding because pgvector checks vector size
        async with db_session.begin_nested():
            db_session.add(chunk)
            with pytest.raises((StatementError, IntegrityError)):
                await db_session.flush()

    async def test_document_active_uniqueness_constraints(
        self, db_session: AsyncSession
    ):
        """Verify active document name and hash uniqueness constraints per tenant."""
        company = Company(name="Unique Policy Co", slug=f"unq-p-{uuid.uuid4().hex[:6]}")
        db_session.add(company)
        await db_session.flush()

        doc1 = PolicyDocument(
            company_id=company.id,
            name="IT Policy",
            category="IT",
            file_name="it_policy.pdf",
            file_size=2000,
            mime_type="application/pdf",
            document_hash="hash_unique_it",
            is_deleted=False,
        )
        db_session.add(doc1)
        await db_session.flush()

        # Duplicate Name - Should Fail
        doc_dup_name = PolicyDocument(
            company_id=company.id,
            name="IT Policy",
            category="Security",
            file_name="another_it.pdf",
            file_size=2000,
            mime_type="application/pdf",
            document_hash="different_hash_value",
            is_deleted=False,
        )
        async with db_session.begin_nested():
            db_session.add(doc_dup_name)
            with pytest.raises(IntegrityError):
                await db_session.flush()

        # Duplicate Hash - Should Fail
        doc_dup_hash = PolicyDocument(
            company_id=company.id,
            name="Different Policy Name",
            category="Security",
            file_name="another_it.pdf",
            file_size=2000,
            mime_type="application/pdf",
            document_hash="hash_unique_it",
            is_deleted=False,
        )
        async with db_session.begin_nested():
            db_session.add(doc_dup_hash)
            with pytest.raises(IntegrityError):
                await db_session.flush()

    async def test_duplicate_allowed_after_soft_delete(self, db_session: AsyncSession):
        """Verify unique active constraints allow re-upload if existing doc is soft-deleted."""
        company = Company(name="Soft Del Co", slug=f"sd-c-{uuid.uuid4().hex[:6]}")
        db_session.add(company)
        await db_session.flush()

        doc1 = PolicyDocument(
            company_id=company.id,
            name="Holiday Calendar",
            category="Compliance",
            file_name="holidays_2026.pdf",
            file_size=50000,
            mime_type="application/pdf",
            document_hash="hash_holidays",
            is_deleted=True,  # Soft-deleted
        )
        db_session.add(doc1)
        await db_session.flush()

        # Insert active document with same name and same hash -> Should Succeed!
        doc2 = PolicyDocument(
            company_id=company.id,
            name="Holiday Calendar",
            category="Compliance",
            file_name="holidays_2026_v2.pdf",
            file_size=50000,
            mime_type="application/pdf",
            document_hash="hash_holidays",
            is_deleted=False,  # Active
        )
        db_session.add(doc2)
        await db_session.flush()

        # Verify both exist in DB
        q = select(PolicyDocument).where(PolicyDocument.company_id == company.id)
        res = await db_session.execute(q)
        docs = res.scalars().all()
        assert len(docs) == 2

    async def test_chunk_unique_index_constraint(self, db_session: AsyncSession):
        """Verify unique chunk index constraint (company_id, document_id, chunk_index)."""
        company = Company(name="Chunk Co", slug=f"chunk-c-{uuid.uuid4().hex[:6]}")
        db_session.add(company)
        await db_session.flush()

        doc = PolicyDocument(
            company_id=company.id,
            name="Leave Policy",
            category="Benefits",
            file_name="leave.pdf",
            file_size=15000,
            mime_type="application/pdf",
            document_hash="hash_leave_policy",
        )
        db_session.add(doc)
        await db_session.flush()

        chunk1 = PolicyChunk(
            company_id=company.id,
            document_id=doc.id,
            chunk_index=0,
            content="First segment content",
            embedding=[0.05] * 1024,
        )
        db_session.add(chunk1)
        await db_session.flush()

        # Duplicate chunk_index 0 -> Should Fail
        chunk2 = PolicyChunk(
            company_id=company.id,
            document_id=doc.id,
            chunk_index=0,
            content="Duplicate index segment content",
            embedding=[0.05] * 1024,
        )
        async with db_session.begin_nested():
            db_session.add(chunk2)
            with pytest.raises(IntegrityError):
                await db_session.flush()

    async def test_relationships_and_cascade(self, db_session: AsyncSession):
        """Verify bidirectional relationships and cascade deletes."""
        company = Company(name="Rel Co", slug=f"rel-c-{uuid.uuid4().hex[:6]}")
        db_session.add(company)
        await db_session.flush()

        doc = PolicyDocument(
            company_id=company.id,
            name="Benefits Handbook",
            category="Benefits",
            file_name="benefits.pdf",
            file_size=12000,
            mime_type="application/pdf",
            document_hash="hash_benefits",
        )
        db_session.add(doc)
        await db_session.flush()

        chunk = PolicyChunk(
            company_id=company.id,
            document_id=doc.id,
            chunk_index=0,
            content="Dental plans overview...",
            embedding=[0.2] * 1024,
        )
        db_session.add(chunk)
        await db_session.flush()

        # Check bidirectional relationships
        await db_session.refresh(company, ["policy_documents"])
        await db_session.refresh(doc, ["company", "chunks"])
        await db_session.refresh(chunk, ["document"])

        assert doc.company == company
        assert doc in company.policy_documents
        assert chunk in doc.chunks
        assert chunk.document == doc

        # Verify cascade deletion doc -> chunks
        await db_session.delete(doc)
        await db_session.flush()

        q = select(PolicyChunk).where(PolicyChunk.id == chunk.id)
        res = await db_session.execute(q)
        assert res.scalar_one_or_none() is None

    async def test_tenant_isolation(self, db_session: AsyncSession):
        """Verify tenant separation isolates policy documents and chunks."""
        company_a = Company(name="Tenant A", slug=f"ta-{uuid.uuid4().hex[:6]}")
        company_b = Company(name="Tenant B", slug=f"tb-{uuid.uuid4().hex[:6]}")
        db_session.add_all([company_a, company_b])
        await db_session.flush()

        doc_a = PolicyDocument(
            company_id=company_a.id,
            name="Policy",
            category="Compliance",
            file_name="f.pdf",
            file_size=10,
            mime_type="application/pdf",
            document_hash="hash_a",
        )
        doc_b = PolicyDocument(
            company_id=company_b.id,
            name="Policy",
            category="Compliance",
            file_name="f.pdf",
            file_size=10,
            mime_type="application/pdf",
            document_hash="hash_b",
        )
        db_session.add_all([doc_a, doc_b])
        await db_session.flush()

        # Query A
        q_a = select(PolicyDocument).where(PolicyDocument.company_id == company_a.id)
        res_a = await db_session.execute(q_a)
        docs_a = res_a.scalars().all()
        assert doc_a in docs_a
        assert doc_b not in docs_a

    async def test_indexed_at_and_chunk_count_fields(self, db_session: AsyncSession):
        """Verify indexed_at and chunk_count store values correctly."""
        company = Company(name="Field Co", slug=f"f-co-{uuid.uuid4().hex[:6]}")
        db_session.add(company)
        await db_session.flush()

        now_utc = datetime.now(timezone.utc)
        doc = PolicyDocument(
            company_id=company.id,
            name="Indexed Policy",
            category="Operations",
            file_name="ops.pdf",
            file_size=50000,
            mime_type="application/pdf",
            document_hash="hash_indexed",
            status=PolicyDocumentStatus.INDEXED,
            chunk_count=15,
            indexed_at=now_utc,
        )
        db_session.add(doc)
        await db_session.flush()

        q = select(PolicyDocument).where(PolicyDocument.id == doc.id)
        res = await db_session.execute(q)
        db_doc = res.scalar_one_or_none()

        assert db_doc is not None
        assert db_doc.status == PolicyDocumentStatus.INDEXED
        assert db_doc.chunk_count == 15
        assert db_doc.indexed_at is not None
        assert abs((db_doc.indexed_at - now_utc).total_seconds()) < 1.0


def test_migration_lifecycle():
    """Verify Alembic migration upgrade -> downgrade -> upgrade works."""
    import sys

    # 1. Downgrade to 0004_create_hr_foundation_tables
    downgrade_cmd = [
        sys.executable,
        "-m",
        "alembic",
        "downgrade",
        "0004_create_hr_foundation_tables",
    ]
    env = {
        **os_env_override(),
        "PYTHONPATH": ".",
        "DATABASE_URL": settings.database_url,
    }
    res_down = subprocess.run(downgrade_cmd, capture_output=True, text=True, env=env)
    assert res_down.returncode == 0, f"Downgrade failed: {res_down.stderr}"

    # 2. Upgrade back to head (0005)
    upgrade_cmd = [sys.executable, "-m", "alembic", "upgrade", "head"]
    res_up = subprocess.run(upgrade_cmd, capture_output=True, text=True, env=env)
    assert res_up.returncode == 0, f"Upgrade failed: {res_up.stderr}"


def os_env_override():
    import os

    env = os.environ.copy()
    return env
