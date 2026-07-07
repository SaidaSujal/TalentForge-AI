import pytest
import uuid
import subprocess
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.db.models import Company, User, Employee, Candidate, Resume, JobDescription
from app.db.models.employee import EmployeeStatus, WorkMode, ExperienceLevel
from app.db.models.candidate import CandidateStatus
from app.db.models.job_description import EmploymentType


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
class TestHRModels:
    """Verify constraints, relationships, and behavior of Subphase 2.2 models."""

    async def test_create_employee_success(self, db_session: AsyncSession):
        """Verify Employee creation, enum defaults, and timestamps."""
        company = Company(name="Emp Tenant", slug=f"emp-tenant-{uuid.uuid4().hex[:6]}")
        db_session.add(company)
        await db_session.flush()

        employee = Employee(
            company_id=company.id,
            first_name="Jane",
            last_name="Doe",
            email=f"jane.doe-{uuid.uuid4().hex[:6]}@tenant.com",
            department="Engineering",
            role="Software Engineer",
            salary=Decimal("120000.00"),
            status=EmployeeStatus.ACTIVE,
            work_mode=WorkMode.REMOTE,
            experience_level=ExperienceLevel.SENIOR,
            current_skills=["Python", "PostgreSQL", "FastAPI"],
            target_role="Lead Engineer",
        )
        db_session.add(employee)
        await db_session.flush()

        # Retrieve and assert
        query = select(Employee).where(Employee.id == employee.id)
        result = await db_session.execute(query)
        db_emp = result.scalar_one_or_none()

        assert db_emp is not None
        assert db_emp.first_name == "Jane"
        assert db_emp.last_name == "Doe"
        assert db_emp.email == employee.email
        assert db_emp.department == "Engineering"
        assert db_emp.role == "Software Engineer"
        assert db_emp.status == EmployeeStatus.ACTIVE
        assert db_emp.work_mode == WorkMode.REMOTE
        assert db_emp.experience_level == ExperienceLevel.SENIOR
        assert db_emp.current_skills == ["Python", "PostgreSQL", "FastAPI"]
        assert db_emp.target_role == "Lead Engineer"
        assert db_emp.is_deleted is False
        assert db_emp.created_at is not None

    async def test_employee_manager_hierarchy(self, db_session: AsyncSession):
        """Verify self-referential manager-subordinate relationship."""
        company = Company(name="Hierarchy Tenant", slug=f"hier-{uuid.uuid4().hex[:6]}")
        db_session.add(company)
        await db_session.flush()

        manager = Employee(
            company_id=company.id,
            first_name="Alice",
            last_name="Manager",
            email=f"alice-{uuid.uuid4().hex[:6]}@corp.com",
            department="HR",
            role="HR Director",
            status=EmployeeStatus.ACTIVE,
        )
        db_session.add(manager)
        await db_session.flush()

        subordinate = Employee(
            company_id=company.id,
            first_name="Bob",
            last_name="Staff",
            email=f"bob-{uuid.uuid4().hex[:6]}@corp.com",
            department="HR",
            role="HR Analyst",
            manager_id=manager.id,
            status=EmployeeStatus.ACTIVE,
        )
        db_session.add(subordinate)
        await db_session.flush()

        await db_session.refresh(manager, ["subordinates"])
        await db_session.refresh(subordinate, ["manager"])

        assert subordinate.manager == manager
        assert subordinate in manager.subordinates

    async def test_employee_user_relationship(self, db_session: AsyncSession):
        """Verify 1-to-1 relationship between User and Employee."""
        company = Company(name="Rel Tenant", slug=f"rel-{uuid.uuid4().hex[:6]}")
        db_session.add(company)
        await db_session.flush()

        user = User(
            email=f"account-{uuid.uuid4().hex[:6]}@tenant.com",
            password_hash="hash",
            role="employee",
            company_id=company.id,
        )
        db_session.add(user)
        await db_session.flush()

        employee = Employee(
            company_id=company.id,
            user_id=user.id,
            first_name="John",
            last_name="User",
            email=user.email,
            department="Sales",
            role="Sales Lead",
        )
        db_session.add(employee)
        await db_session.flush()

        await db_session.refresh(user, ["employee"])
        await db_session.refresh(employee, ["user"])

        assert user.employee == employee
        assert employee.user == user

    async def test_employee_email_uniqueness_per_tenant(self, db_session: AsyncSession):
        """Verify unique constraint on email per company_id."""
        company1 = Company(name="Company 1", slug=f"c1-{uuid.uuid4().hex[:6]}")
        company2 = Company(name="Company 2", slug=f"c2-{uuid.uuid4().hex[:6]}")
        db_session.add_all([company1, company2])
        await db_session.flush()

        shared_email = f"shared-{uuid.uuid4().hex[:6]}@domain.com"

        # Create employee in company1
        emp1 = Employee(
            company_id=company1.id,
            first_name="Jane",
            last_name="One",
            email=shared_email,
            department="Sales",
            role="Rep",
        )
        db_session.add(emp1)
        await db_session.flush()

        # Create employee with same email in company2 -> Should Succeed
        emp2 = Employee(
            company_id=company2.id,
            first_name="Jane",
            last_name="Two",
            email=shared_email,
            department="Sales",
            role="Rep",
        )
        db_session.add(emp2)
        await db_session.flush()

        # Create duplicate employee in company1 -> Should Fail
        emp3 = Employee(
            company_id=company1.id,
            first_name="Jane",
            last_name="Three",
            email=shared_email,
            department="Sales",
            role="Rep",
        )
        db_session.add(emp3)
        with pytest.raises(IntegrityError):
            await db_session.flush()

    async def test_candidate_resume_one_to_one(self, db_session: AsyncSession):
        """Verify candidate-resume relationship and cascade deletion."""
        company = Company(name="Cand Tenant", slug=f"cand-{uuid.uuid4().hex[:6]}")
        db_session.add(company)
        await db_session.flush()

        candidate = Candidate(
            company_id=company.id,
            first_name="John",
            last_name="Applicant",
            email=f"john-{uuid.uuid4().hex[:6]}@gmail.com",
            status=CandidateStatus.APPLIED,
            skills=["Python", "SQL"],
        )
        db_session.add(candidate)
        await db_session.flush()

        resume = Resume(
            company_id=company.id,
            candidate_id=candidate.id,
            file_name="resume.pdf",
            file_size=102400,
            mime_type="application/pdf",
            raw_text="Extracted resume text content",
            resume_hash="hash123",
        )
        db_session.add(resume)
        await db_session.flush()

        await db_session.refresh(candidate, ["resume"])
        await db_session.refresh(resume, ["candidate"])

        assert candidate.resume == resume
        assert resume.candidate == candidate

        # Verify cascade delete candidate -> deletes resume
        await db_session.delete(candidate)
        await db_session.flush()

        q = select(Resume).where(Resume.id == resume.id)
        res = await db_session.execute(q)
        assert res.scalar_one_or_none() is None

    async def test_candidate_match_score_check_constraint(self, db_session: AsyncSession):
        """Verify database check constraint on match_score bounds."""
        company = Company(name="Score Tenant", slug=f"score-{uuid.uuid4().hex[:6]}")
        db_session.add(company)
        await db_session.flush()

        # Fails with match_score > 100
        candidate_high = Candidate(
            company_id=company.id,
            first_name="High",
            last_name="Score",
            match_score=Decimal("101.50"),
        )
        db_session.add(candidate_high)
        with pytest.raises(IntegrityError):
            await db_session.flush()

        # rollback failed flush transaction before trying again
        await db_session.rollback()
        await db_session.begin()

        # Fails with match_score < 0
        candidate_low = Candidate(
            company_id=company.id,
            first_name="Low",
            last_name="Score",
            match_score=Decimal("-5.00"),
        )
        db_session.add(candidate_low)
        with pytest.raises(IntegrityError):
            await db_session.flush()

    async def test_job_description_jsonb_and_enums(self, db_session: AsyncSession):
        """Verify JSONB column mapping and ExperienceLevel/EmploymentType enums."""
        company = Company(name="JD Tenant", slug=f"jd-{uuid.uuid4().hex[:6]}")
        db_session.add(company)
        await db_session.flush()

        jd = JobDescription(
            company_id=company.id,
            title="Senior Python Architect",
            department="Engineering",
            experience_level=ExperienceLevel.SENIOR,
            employment_type=EmploymentType.FULL_TIME,
            required_skills=["Python", "System Design", "PostgreSQL"],
            preferred_skills=["Docker", "FastAPI"],
            job_description_text="# Senior Python Architect Job Description...",
            responsibilities=["Lead team of 5", "Design scalable multi-tenant DB schemas"],
            requirements=["5+ years experience", "Strong communication skills"],
            benefits=["Full remote work", "Competitive stock options"],
            ats_keywords=["Python", "Architect", "Multi-tenant"],
            variants={
                "linkedin_post": "Looking for a Python Architect!",
                "internal_note": "Fulfill ASAP",
            },
            jd_hash="jdhash123",
        )
        db_session.add(jd)
        await db_session.flush()

        q = select(JobDescription).where(JobDescription.id == jd.id)
        res = await db_session.execute(q)
        db_jd = res.scalar_one_or_none()

        assert db_jd is not None
        assert db_jd.experience_level == ExperienceLevel.SENIOR
        assert db_jd.employment_type == EmploymentType.FULL_TIME
        assert db_jd.required_skills == ["Python", "System Design", "PostgreSQL"]
        assert db_jd.variants == {
            "linkedin_post": "Looking for a Python Architect!",
            "internal_note": "Fulfill ASAP",
        }

    async def test_employee_salary_deferred_loading(self, db_session: AsyncSession):
        """Verify sensitive salary field uses deferred loading strategy."""
        company = Company(name="Salary Tenant", slug=f"sal-{uuid.uuid4().hex[:6]}")
        db_session.add(company)
        await db_session.flush()

        employee = Employee(
            company_id=company.id,
            first_name="Salaried",
            last_name="Worker",
            email=f"salaried-{uuid.uuid4().hex[:6]}@tenant.com",
            department="Operations",
            role="Operations Manager",
            salary=Decimal("95000.00"),
        )
        db_session.add(employee)
        await db_session.flush()

        # Clear session to force select queries
        db_session.expunge_all()

        # Query Employee
        q = select(Employee).where(Employee.id == employee.id)
        res = await db_session.execute(q)
        db_emp = res.scalar_one_or_none()

        assert db_emp is not None
        # In SQLAlchemy, we inspect the loaded state to verify salary is deferred
        state = db_emp._sa_instance_state
        assert "salary" in state.unloaded  # salary should be in the unloaded/deferred set

        # Trigger lazy load asynchronously via refresh
        await db_session.refresh(db_emp, ["salary"])
        sal_value = db_emp.salary
        assert sal_value == Decimal("95000.00")
        assert "salary" not in state.unloaded


    async def test_employee_soft_delete_lifecycle(self, db_session: AsyncSession):
        """Verify soft-delete logical lifecycle exclusion."""
        company = Company(name="Soft Delete Tenant", slug=f"sd-{uuid.uuid4().hex[:6]}")
        db_session.add(company)
        await db_session.flush()

        employee = Employee(
            company_id=company.id,
            first_name="Terminated",
            last_name="Worker",
            email=f"terminated-{uuid.uuid4().hex[:6]}@tenant.com",
            department="Operations",
            role="Operations Coordinator",
            is_deleted=False,
        )
        db_session.add(employee)
        await db_session.flush()

        # Initially not deleted
        assert employee.is_deleted is False

        # Soft delete
        employee.is_deleted = True
        await db_session.flush()

        # Verify still physically exists
        q = select(Employee).where(Employee.id == employee.id)
        res = await db_session.execute(q)
        db_emp = res.scalar_one_or_none()
        assert db_emp is not None
        assert db_emp.is_deleted is True

    async def test_tenant_isolation_employees(self, db_session: AsyncSession):
        """Verify that queries filter by company_id correctly."""
        company_a = Company(name="Tenant A", slug=f"ta-{uuid.uuid4().hex[:6]}")
        company_b = Company(name="Tenant B", slug=f"tb-{uuid.uuid4().hex[:6]}")
        db_session.add_all([company_a, company_b])
        await db_session.flush()

        emp_a = Employee(
            company_id=company_a.id,
            first_name="TenantA",
            last_name="Emp",
            email=f"empa-{uuid.uuid4().hex[:6]}@domain.com",
            department="HR",
            role="Partner",
        )
        emp_b = Employee(
            company_id=company_b.id,
            first_name="TenantB",
            last_name="Emp",
            email=f"empb-{uuid.uuid4().hex[:6]}@domain.com",
            department="HR",
            role="Partner",
        )
        db_session.add_all([emp_a, emp_b])
        await db_session.flush()

        # Query company_a
        q_a = select(Employee).where(Employee.company_id == company_a.id)
        res_a = await db_session.execute(q_a)
        emps_a = res_a.scalars().all()
        assert emp_a in emps_a
        assert emp_b not in emps_a

        # Query company_b
        q_b = select(Employee).where(Employee.company_id == company_b.id)
        res_b = await db_session.execute(q_b)
        emps_b = res_b.scalars().all()
        assert emp_b in emps_b
        assert emp_a not in emps_b


def test_migration_lifecycle():
    """Verify Alembic migration upgrade -> downgrade -> upgrade works."""
    import sys
    from app.core.config import settings
    # 1. Downgrade to 0003_create_users_table
    downgrade_cmd = [sys.executable, "-m", "alembic", "downgrade", "0003_create_users_table"]
    env = {
        **os_env_override(),
        "PYTHONPATH": ".",
        "DATABASE_URL": settings.database_url,
    }

    res_down = subprocess.run(downgrade_cmd, capture_output=True, text=True, env=env)
    assert res_down.returncode == 0, f"Downgrade failed: {res_down.stderr}"

    # 2. Upgrade back to head (0004)
    upgrade_cmd = [sys.executable, "-m", "alembic", "upgrade", "head"]
    res_up = subprocess.run(upgrade_cmd, capture_output=True, text=True, env=env)
    assert res_up.returncode == 0, f"Upgrade failed: {res_up.stderr}"




def os_env_override():
    import os
    env = os.environ.copy()
    return env
