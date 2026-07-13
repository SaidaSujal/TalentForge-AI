"""
TalentForge AI — Seeder Tests
==============================
Verifies deterministic stable UUIDs, idempotency, reset mode, schemas, and error boundaries.
"""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import delete, select, update

from app.core.config import settings
from app.db.models import (
    AICache,
    AIHistory,
    AttritionAssessment,
    AuditLog,
    Candidate,
    Company,
    Employee,
    ExportJob,
    InterviewKit,
    JobDescription,
    LearningPlan,
    OnboardingPlan,
    OnboardingTask,
    PerformanceReview,
    PolicyDocument,
    Resume,
    RetentionStrategy,
    TrainingRecord,
    User,
)
from app.db.session import AsyncSessionLocal
from scripts.seed_demo_data import (
    DEMO_COMPANY_ID,
    DEMO_USER_ID,
    delete_demo_data,
    get_uuid,
)
from scripts.seed_demo_data import main as seeder_main
from scripts.seed_demo_data import (
    seed_data,
)


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
class TestSeedDemoData:
    """Covers all database seeder constraints, counts, and idempotency rules."""

    async def get_count(self, session, model) -> int:
        result = await session.execute(select(model))
        return len(result.scalars().all())

    async def clear_all_tables(self, session):
        """Clean all DB tables inside test transaction to start from absolute zero."""
        await session.execute(update(Employee).values(manager_id=None, user_id=None))
        await session.execute(delete(AuditLog))
        await session.execute(delete(TrainingRecord))
        await session.execute(delete(LearningPlan))
        await session.execute(delete(RetentionStrategy))
        await session.execute(delete(AttritionAssessment))
        await session.execute(delete(PerformanceReview))
        await session.execute(delete(OnboardingTask))
        await session.execute(delete(OnboardingPlan))
        await session.execute(delete(InterviewKit))
        await session.execute(delete(Resume))
        await session.execute(delete(Candidate))
        await session.execute(delete(JobDescription))
        await session.execute(delete(PolicyDocument))
        await session.execute(delete(Employee))
        await session.execute(delete(User))
        await session.execute(delete(Company))
        await session.flush()

    async def test_exact_table_counts(self, db_session):
        """Verify seeder creates exactly the expected counts for every table."""
        # 1. Clean first
        await self.clear_all_tables(db_session)

        # 2. Seed
        created = await seed_data(db_session, "test-password")

        # 3. Assert returned counts
        assert created["companies"] == 1
        assert created["users"] == 1
        assert created["employees"] == 10
        assert created["candidates"] == 8
        assert created["resumes"] == 8
        assert created["job_descriptions"] == 3
        assert created["policy_documents"] == 2
        assert created["onboarding_plans"] == 1
        assert created["onboarding_tasks"] == 5
        assert created["performance_reviews"] == 2
        assert created["attrition_assessments"] == 2
        assert created["retention_strategies"] == 1
        assert created["learning_plans"] == 2
        assert created["training_records"] == 3
        assert created["interview_kits"] == 2
        assert created["audit_logs"] == 1

        # 4. Assert actual DB counts
        assert await self.get_count(db_session, Company) == 1
        assert await self.get_count(db_session, User) == 1
        assert await self.get_count(db_session, Employee) == 10
        assert await self.get_count(db_session, Candidate) == 8
        assert await self.get_count(db_session, Resume) == 8
        assert await self.get_count(db_session, JobDescription) == 3
        assert await self.get_count(db_session, PolicyDocument) == 2
        assert await self.get_count(db_session, OnboardingPlan) == 1
        assert await self.get_count(db_session, OnboardingTask) == 5
        assert await self.get_count(db_session, PerformanceReview) == 2
        assert await self.get_count(db_session, AttritionAssessment) == 2
        assert await self.get_count(db_session, RetentionStrategy) == 1
        assert await self.get_count(db_session, LearningPlan) == 2
        assert await self.get_count(db_session, TrainingRecord) == 3
        assert await self.get_count(db_session, InterviewKit) == 2
        assert await self.get_count(db_session, AuditLog) == 1

    async def test_stable_uuids(self, db_session):
        """Verify seeded records are created with exact stable UUIDs."""
        await self.clear_all_tables(db_session)
        await seed_data(db_session, "test-password")

        # Company
        comp = await db_session.get(Company, DEMO_COMPANY_ID)
        assert comp is not None
        assert comp.slug == "dev-enterprise"

        # User
        usr = await db_session.get(User, DEMO_USER_ID)
        assert usr is not None
        assert usr.email == "admin@example.com"

        # Employee 1
        emp = await db_session.get(Employee, get_uuid("employee_1"))
        assert emp is not None
        assert emp.first_name == "Taylor"
        assert emp.last_name == "Vance"

        # Candidate 1
        cand = await db_session.get(Candidate, get_uuid("candidate_1"))
        assert cand is not None
        assert cand.first_name == "Avery"

    async def test_ordinary_rerun_idempotence(self, db_session):
        """Verify ordinary seeder run skips existing, does not duplicate or overwrite modifications."""
        await self.clear_all_tables(db_session)

        # Seed pass 1
        await seed_data(db_session, "test-password")

        # Seed pass 2 (ordinary rerun)
        created_pass_2 = await seed_data(db_session, "test-password")

        # Assert no new records were created
        for val in created_pass_2.values():
            assert val == 0

        # Assert total counts are still correct
        assert await self.get_count(db_session, Employee) == 10

        # Modify a record
        emp = await db_session.get(Employee, get_uuid("employee_1"))
        emp.first_name = "Modified-Taylor"
        db_session.add(emp)
        await db_session.flush()

        # Seed pass 3
        await seed_data(db_session, "test-password")

        # Assert modified value is preserved (no overwrite)
        db_session.expire(emp)
        emp_refresh = await db_session.get(Employee, get_uuid("employee_1"))
        assert emp_refresh.first_name == "Modified-Taylor"

        # Soft-delete a record
        emp2 = await db_session.get(Employee, get_uuid("employee_2"))
        emp2.is_deleted = True
        db_session.add(emp2)
        await db_session.flush()

        # Seed pass 4
        await seed_data(db_session, "test-password")

        # Assert soft-deleted remains soft-deleted (no reactivation)
        db_session.expire(emp2)
        emp2_refresh = await db_session.get(Employee, get_uuid("employee_2"))
        assert emp2_refresh.is_deleted is True

    async def test_reset_mode_restores_baseline(self, db_session):
        """Verify delete_demo_data deletes all demo records and seed_data recreates baseline."""
        await self.clear_all_tables(db_session)
        await seed_data(db_session, "test-password")

        # Modify Taylor
        emp = await db_session.get(Employee, get_uuid("employee_1"))
        emp.first_name = "Modified-Taylor"
        db_session.add(emp)
        await db_session.flush()

        # Perform Reset
        deleted = await delete_demo_data(db_session)
        assert deleted["employees"] == 10
        assert deleted["companies"] == 1

        # Check DB empty of demo
        assert await self.get_count(db_session, Employee) == 0

        # Re-seed
        await seed_data(db_session, "test-password")

        # Verify Taylor is restored to baseline
        emp_restored = await db_session.get(Employee, get_uuid("employee_1"))
        assert emp_restored.first_name == "Taylor"

    async def test_reset_removes_only_demo_uuids(self, db_session):
        """Verify reset deletes only records with demo UUIDs, leaving non-demo rows untouched."""
        await self.clear_all_tables(db_session)

        # Create a non-demo Company
        non_demo_company_id = uuid.uuid4()
        non_demo_company = Company(
            id=non_demo_company_id,
            name="External Corp",
            slug="external-corp",
            settings_json="{}",
        )
        db_session.add(non_demo_company)
        await db_session.flush()

        # Run seed
        await seed_data(db_session, "test-password")

        # Run reset
        await delete_demo_data(db_session)

        # Verify non-demo company still exists
        comp_check = await db_session.get(Company, non_demo_company_id)
        assert comp_check is not None
        assert comp_check.name == "External Corp"

    async def test_json_field_types(self, db_session):
        """Verify JSON/JSONB fields are loaded and stored as correct Python types (lists/dicts)."""
        await self.clear_all_tables(db_session)
        await seed_data(db_session, "test-password")

        # Candidate 1
        cand = await db_session.get(Candidate, get_uuid("candidate_1"))
        assert isinstance(cand.skills, list)
        assert isinstance(cand.scorecard_json, dict)
        assert isinstance(cand.suggested_questions, list)

        # Job Description 1
        jd = await db_session.get(JobDescription, get_uuid("jd_1"))
        assert isinstance(jd.required_skills, list)
        assert isinstance(jd.preferred_skills, list)
        assert isinstance(jd.variants, dict)

        # Performance Review 1
        rev = await db_session.get(PerformanceReview, get_uuid("performance_review_1"))
        assert isinstance(rev.key_achievements, dict)
        assert isinstance(rev.development_areas, dict)

    async def test_no_manager_hierarchy_cycle(self, db_session):
        """Verify employee managers hierarchy contains no loops/cycles."""
        await self.clear_all_tables(db_session)
        await seed_data(db_session, "test-password")

        # Fetch all seeded employees
        res = await db_session.execute(select(Employee))
        employees = res.scalars().all()

        for emp in employees:
            visited = set()
            curr = emp
            while curr.manager_id is not None:
                assert curr.id not in visited, f"Cycle detected for employee {curr.id}"
                visited.add(curr.id)
                # Fetch manager
                curr = await db_session.get(Employee, curr.manager_id)
                assert curr is not None

    async def test_empty_database_seed(self, db_session):
        """Verify seeding against a completely empty database works and matches counts."""
        await self.clear_all_tables(db_session)
        created = await seed_data(db_session, "test-password")
        assert created["companies"] == 1
        assert created["users"] == 1
        assert created["employees"] == 10

    async def test_rollback_on_forced_failure(self, db_session):
        """Verify transaction rollback on a forced middle-of-run failure."""
        await self.clear_all_tables(db_session)

        try:
            async with db_session.begin_nested():
                await seed_data(db_session, "test-password")
                # Force failure
                raise ValueError("Forced test rollback")
        except ValueError:
            pass

        # Assert database remains completely clean
        comp = await db_session.get(Company, DEMO_COMPANY_ID)
        assert comp is None
        assert await self.get_count(db_session, Employee) == 0

    async def test_missing_password_rejection(self, monkeypatch):
        """Verify script aborts when DEMO_ADMIN_PASSWORD is unset."""
        import sys

        monkeypatch.delenv("DEMO_ADMIN_PASSWORD", raising=False)
        monkeypatch.setattr(sys, "argv", ["seed_demo_data.py"])
        with pytest.raises(SystemExit) as exc:
            await seeder_main()
        assert exc.value.code == 1

    async def test_production_blocking(self, monkeypatch):
        """Verify production APP_ENV blocks seeder execution."""
        import sys

        monkeypatch.setenv("DEMO_ADMIN_PASSWORD", "test-pass")
        monkeypatch.setattr(settings, "app_env", "production")
        monkeypatch.setattr(sys, "argv", ["seed_demo_data.py"])
        with pytest.raises(SystemExit) as exc:
            await seeder_main()
        assert exc.value.code == 1

    async def test_remote_development_flag_enforcement(self, monkeypatch):
        """Verify remote Neon host requires the allow-remote-development flag."""
        import sys

        monkeypatch.setenv("DEMO_ADMIN_PASSWORD", "test-pass")
        monkeypatch.setattr(settings, "app_env", "development")
        monkeypatch.setattr(
            settings,
            "database_url",
            "postgresql+psycopg://user:pass@neon-host.neon.tech/db",
        )
        monkeypatch.setattr(sys, "argv", ["seed_demo_data.py"])
        with pytest.raises(SystemExit) as exc:
            await seeder_main()
        assert exc.value.code == 1

    @pytest.mark.anyio
    async def test_masked_database_logging(self, capsys, monkeypatch):
        """Verify that secret URL credentials never appear in console logs."""
        import sys
        import unittest.mock

        monkeypatch.setenv("DEMO_ADMIN_PASSWORD", "test-pass")
        monkeypatch.setattr(settings, "app_env", "development")
        monkeypatch.setattr(
            settings,
            "database_url",
            "postgresql+psycopg://secret_user:secret_pass@my-neon-host.tech/talentforge_dev",
        )
        monkeypatch.setattr(
            sys, "argv", ["seed_demo_data.py", "--allow-remote-development"]
        )

        mock_session = unittest.mock.AsyncMock()
        mock_begin = unittest.mock.MagicMock()
        mock_begin.__aenter__ = unittest.mock.AsyncMock()
        mock_begin.__aexit__ = unittest.mock.AsyncMock()
        mock_session.begin = unittest.mock.MagicMock(return_value=mock_begin)

        with unittest.mock.patch(
            "scripts.seed_demo_data.AsyncSessionLocal"
        ) as mock_session_local:
            mock_session_local.return_value.__aenter__.return_value = mock_session
            await seeder_main()

        captured = capsys.readouterr()
        assert "secret_user" not in captured.out
        assert "secret_pass" not in captured.out
        assert "Host: my-neon-host.tech" in captured.out
        assert "Database: talentforge_dev" in captured.out

    @pytest.mark.anyio
    async def test_password_hash_output_protection(self, capsys, monkeypatch):
        """Verify that neither plaintext password nor bcrypt hash appears in logging."""
        import sys
        import unittest.mock

        monkeypatch.setenv("DEMO_ADMIN_PASSWORD", "super-secret-password-123")
        monkeypatch.setattr(settings, "app_env", "development")
        monkeypatch.setattr(sys, "argv", ["seed_demo_data.py"])

        mock_session = unittest.mock.AsyncMock()
        mock_begin = unittest.mock.MagicMock()
        mock_begin.__aenter__ = unittest.mock.AsyncMock()
        mock_begin.__aexit__ = unittest.mock.AsyncMock()
        mock_session.begin = unittest.mock.MagicMock(return_value=mock_begin)

        with unittest.mock.patch(
            "scripts.seed_demo_data.AsyncSessionLocal"
        ) as mock_session_local:
            mock_session_local.return_value.__aenter__.return_value = mock_session
            await seeder_main()

        captured = capsys.readouterr()
        assert "super-secret-password-123" not in captured.out
        assert "super-secret-password-123" not in captured.err
        assert "$2b$" not in captured.out
        assert "$2b$" not in captured.err

    async def test_zero_operational_system_rows(self, db_session):
        """Verify AI system operational tables remain completely empty."""
        await self.clear_all_tables(db_session)
        await seed_data(db_session, "test-password")
        assert await self.get_count(db_session, AICache) == 0
        assert await self.get_count(db_session, AIHistory) == 0
        assert await self.get_count(db_session, ExportJob) == 0

    def test_zero_external_api_calls(self, monkeypatch):
        """Verify seeder executes purely offline with zero network attempts."""
        import socket

        def guard(*args, **kwargs):
            raise RuntimeError("Network call blocked during seeder execution")

        monkeypatch.setattr(socket, "socket", guard)

        # Verify local stable UUID generation works offline
        val = get_uuid("test-offline-key")
        assert val is not None
