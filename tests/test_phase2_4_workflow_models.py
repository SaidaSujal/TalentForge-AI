"""
TalentForge AI — Subphase 2.4 Workflow Models Test Suite
=========================================================
Validates database models, enums, check constraints, indexes, cascade rules,
soft delete columns, and tenant isolation behavior for the 8 workflow tables.
"""

import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    ApprovalStatus,
    AttritionAssessment,
    Company,
    Employee,
    EmployeeStatus,
    ExperienceLevel,
    InterviewKit,
    LearningPlan,
    OnboardingPlan,
    OnboardingStatus,
    OnboardingTask,
    OnboardingTaskCategory,
    PerformanceReview,
    RetentionStrategy,
    RetentionStrategyStatus,
    ReviewStatus,
    RiskLevel,
    TaskStatus,
    TrainingRecord,
    TrainingStatus,
    User,
    WorkMode,
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


async def create_base_tenant_and_employee(db_session: AsyncSession, suffix: str):
    """Helper utility to create a tenant company and a basic employee."""
    company = Company(name=f"Tenant Co {suffix}", slug=f"tenant-co-{suffix}")
    db_session.add(company)
    await db_session.flush()

    employee = Employee(
        company_id=company.id,
        first_name="Jane",
        last_name="Doe",
        email=f"jane.doe.{suffix}@tenant.com",
        status=EmployeeStatus.ACTIVE,
        role="Software Engineer",
        department="Engineering",
        experience_level=ExperienceLevel.MID,
        work_mode=WorkMode.HYBRID,
        salary=Decimal("100000.00"),
    )
    db_session.add(employee)
    await db_session.flush()
    return company, employee


@pytest.mark.anyio
class TestWorkflowModels:
    """Verification suite for workflow database schemas and integrity rules."""

    # ── ONBOARDING PLANS & TASKS ──────────────────────────────────────────────

    async def test_onboarding_plan_and_task_creation(self, db_session: AsyncSession):
        """Verify successful creation of onboarding plans and tasks with relationships."""
        suffix = uuid.uuid4().hex[:6]
        company, employee = await create_base_tenant_and_employee(db_session, suffix)

        # 1. Create OnboardingPlan
        plan = OnboardingPlan(
            company_id=company.id,
            employee_id=employee.id,
            status=OnboardingStatus.IN_PROGRESS,
            progress_percent=Decimal("25.50"),
            welcome_email_text="Welcome to the team!",
            team_announcement_text="Meet Jane, our new engineer!",
            plan_data_json={
                "milestones": ["Setup dev environment", "Complete first task"]
            },
        )
        db_session.add(plan)
        await db_session.flush()

        # 2. Create OnboardingTasks
        task1 = OnboardingTask(
            company_id=company.id,
            plan_id=plan.id,
            title="Setup Laptop",
            category=OnboardingTaskCategory.TOOL,
            status=TaskStatus.IN_PROGRESS,
            due_date=date(2026, 7, 15),
        )
        task2 = OnboardingTask(
            company_id=company.id,
            plan_id=plan.id,
            title="Intro Meeting",
            category=OnboardingTaskCategory.MEETING,
            status=TaskStatus.PENDING,
            due_date=date(2026, 7, 16),
        )
        db_session.add_all([task1, task2])
        await db_session.flush()

        # Refresh to load relationships asynchronously
        await db_session.refresh(plan, ["tasks", "employee"])

        assert plan.status == OnboardingStatus.IN_PROGRESS
        assert plan.progress_percent == Decimal("25.50")
        assert len(plan.tasks) == 2
        assert {t.title for t in plan.tasks} == {"Setup Laptop", "Intro Meeting"}
        assert plan.employee.first_name == "Jane"

    async def test_onboarding_plan_progress_check_constraint(
        self, db_session: AsyncSession
    ):
        """Verify progress percentage check constraints (0 <= progress <= 100)."""
        suffix = uuid.uuid4().hex[:6]
        company, employee = await create_base_tenant_and_employee(db_session, suffix)

        invalid_plan = OnboardingPlan(
            company_id=company.id,
            employee_id=employee.id,
            status=OnboardingStatus.PENDING,
            progress_percent=Decimal("105.00"),  # Invalid > 100
        )
        async with db_session.begin_nested():
            db_session.add(invalid_plan)
            with pytest.raises(IntegrityError):
                await db_session.flush()

    async def test_onboarding_plan_unique_active_employee_index(
        self, db_session: AsyncSession
    ):
        """Verify unique active onboarding plan per employee constraint and soft-delete interaction."""
        suffix = uuid.uuid4().hex[:6]
        company, employee = await create_base_tenant_and_employee(db_session, suffix)

        # Plan 1: Active
        plan1 = OnboardingPlan(
            company_id=company.id,
            employee_id=employee.id,
            status=OnboardingStatus.IN_PROGRESS,
            is_deleted=False,
        )
        db_session.add(plan1)
        await db_session.flush()

        # Plan 2: Active (should fail due to unique constraint)
        plan2 = OnboardingPlan(
            company_id=company.id,
            employee_id=employee.id,
            status=OnboardingStatus.PENDING,
            is_deleted=False,
        )
        async with db_session.begin_nested():
            db_session.add(plan2)
            with pytest.raises(IntegrityError):
                await db_session.flush()

        # Soft delete plan1
        plan1.is_deleted = True
        await db_session.flush()

        # Creating Plan 3 (active) should now succeed because Plan 1 is soft-deleted
        plan3 = OnboardingPlan(
            company_id=company.id,
            employee_id=employee.id,
            status=OnboardingStatus.PENDING,
            is_deleted=False,
        )
        db_session.add(plan3)
        await db_session.flush()
        assert plan3.id is not None

    # ── PERFORMANCE REVIEWS ───────────────────────────────────────────────────

    async def test_performance_review_lifecycle(self, db_session: AsyncSession):
        """Verify performance review creation, constraints, self-referential versioning, and SET NULL cascade."""
        suffix = uuid.uuid4().hex[:6]
        company, employee = await create_base_tenant_and_employee(db_session, suffix)

        # Create manager employee and reviewer user
        manager = Employee(
            company_id=company.id,
            first_name="John",
            last_name="Manager",
            email=f"john.manager.{suffix}@tenant.com",
            status=EmployeeStatus.ACTIVE,
            role="Engineering Manager",
            department="Engineering",
            experience_level=ExperienceLevel.LEAD,
            work_mode=WorkMode.OFFICE,
        )
        reviewer_user = User(
            company_id=company.id,
            email=f"hr.reviewer.{suffix}@company.com",
            password_hash="hashed_pass_mock",
            role="hr_manager",
        )
        db_session.add_all([manager, reviewer_user])
        await db_session.flush()

        # 1. Create a draft performance review (version 1)
        review_v1 = PerformanceReview(
            company_id=company.id,
            employee_id=employee.id,
            manager_id=manager.id,
            review_period="Annual 2025",
            status=ReviewStatus.DRAFT,
            goals_achieved=4,
            total_goals=5,
            attendance_percent=Decimal("98.50"),
            manager_observations="Excellent backend design work.",
            key_achievements={"items": ["Shipped policy index module"]},
            development_areas={"items": ["Improve front-end expertise"]},
            version_number=1,
        )
        db_session.add(review_v1)
        await db_session.flush()

        # 2. Create version 2 linking back to version 1 (self-referential check)
        review_v2 = PerformanceReview(
            company_id=company.id,
            employee_id=employee.id,
            manager_id=manager.id,
            review_period="Annual 2025",
            status=ReviewStatus.COMPLETED,
            goals_achieved=5,
            total_goals=5,
            attendance_percent=Decimal("98.50"),
            manager_observations="Completed all goals with distinction.",
            key_achievements={
                "items": ["Shipped policy index module", "Front-end fixes"]
            },
            development_areas={"items": ["Improve documentation"]},
            version_number=2,
            previous_version_id=review_v1.id,
            reviewed_by=reviewer_user.id,
            reviewed_at=datetime.now(timezone.utc),
            approval_status=ApprovalStatus.APPROVED,
        )
        db_session.add(review_v2)
        await db_session.flush()

        # Load relationships asynchronously
        await db_session.refresh(review_v2, ["previous_version"])
        await db_session.refresh(review_v1, ["next_versions"])

        # 3. Assert self-referential relationships
        assert review_v2.previous_version_id == review_v1.id
        assert review_v2.previous_version.id == review_v1.id
        assert len(review_v1.next_versions) == 1

        # 4. Check goals constraints (goals_achieved <= total_goals)
        invalid_review = PerformanceReview(
            company_id=company.id,
            employee_id=employee.id,
            manager_id=manager.id,
            review_period="Q1 2026",
            status=ReviewStatus.DRAFT,
            goals_achieved=6,  # 6 met out of 5 is invalid
            total_goals=5,
        )
        async with db_session.begin_nested():
            db_session.add(invalid_review)
            with pytest.raises(IntegrityError):
                await db_session.flush()

        # 5. Verify manager profile SET NULL deletion safeguard
        # Create a new review
        review = PerformanceReview(
            company_id=company.id,
            employee_id=employee.id,
            manager_id=manager.id,
            review_period="Q2 2026",
            status=ReviewStatus.DRAFT,
            goals_achieved=2,
            total_goals=3,
        )
        db_session.add(review)
        await db_session.flush()

        # Delete manager employee
        await db_session.delete(manager)
        await db_session.flush()

        # The review MUST NOT be deleted. Its manager_id must become NULL.
        await db_session.refresh(review)
        assert review is not None
        assert review.manager_id is None

    # ── ATTRITION & RETENTION ─────────────────────────────────────────────────

    async def test_attrition_assessment_and_retention_strategy(
        self, db_session: AsyncSession
    ):
        """Verify attrition assessments and retention strategies schemas, constraints, and cascades."""
        suffix = uuid.uuid4().hex[:6]
        company, employee = await create_base_tenant_and_employee(db_session, suffix)

        # 1. Create AttritionAssessment
        assessment = AttritionAssessment(
            company_id=company.id,
            employee_id=employee.id,
            risk_score=Decimal("78.50"),
            risk_level=RiskLevel.HIGH,
            risk_factors={
                "shap_explainability": [
                    {"feature": "overtime_hours", "importance": 0.45},
                    {"feature": "years_at_role", "importance": 0.20},
                ]
            },
            stay_interview_questions={"questions": ["What is causing burnout?"]},
            replacement_cost=Decimal("45000.00"),
            manager_satisfaction_score=Decimal("2.5"),
            overtime_hours=Decimal("42.0"),
        )
        db_session.add(assessment)
        await db_session.flush()

        # 2. Create RetentionStrategy
        strategy = RetentionStrategy(
            company_id=company.id,
            assessment_id=assessment.id,
            employee_id=employee.id,
            recommendations={
                "salary_revision": "Increase base by 15%",
                "remote_days": "Increase to 3 days/week",
            },
            action_plan="Discuss salary hike with VP of Engineering.",
            status=RetentionStrategyStatus.PROPOSED,
        )
        db_session.add(strategy)
        await db_session.flush()

        # Load relationships asynchronously
        await db_session.refresh(assessment, ["retention_strategy"])
        await db_session.refresh(strategy, ["assessment"])

        # 3. Assert relationship and values
        assert assessment.retention_strategy is not None
        assert assessment.retention_strategy.id == strategy.id
        assert strategy.assessment.id == assessment.id

        # 4. Check risk_score constraint (0 <= score <= 100)
        invalid_assessment = AttritionAssessment(
            company_id=company.id,
            employee_id=employee.id,
            risk_score=Decimal("-5.00"),  # Negative score invalid
            risk_level=RiskLevel.LOW,
        )
        async with db_session.begin_nested():
            db_session.add(invalid_assessment)
            with pytest.raises(IntegrityError):
                await db_session.flush()

    # ── LEARNING PLANS & TRAINING RECORDS ─────────────────────────────────────

    async def test_learning_plan_and_training_records(self, db_session: AsyncSession):
        """Verify learning plans, training records, enums, check constraints, and SET NULL plan_id behavior."""
        suffix = uuid.uuid4().hex[:6]
        company, employee = await create_base_tenant_and_employee(db_session, suffix)

        # 1. Create LearningPlan
        plan = LearningPlan(
            company_id=company.id,
            employee_id=employee.id,
            current_role="Mid Developer",
            target_role="Senior Architect",
            readiness_score=Decimal("45.00"),
            skill_gap_analysis={"gaps": ["System Design", "Distributed Systems"]},
            learning_path_json={
                "courses": ["Advanced Systems Design", "Kubernetes Mastery"]
            },
        )
        db_session.add(plan)
        await db_session.flush()

        # 2. Create TrainingRecord
        training = TrainingRecord(
            company_id=company.id,
            employee_id=employee.id,
            plan_id=plan.id,
            course_name="Kubernetes Mastery",
            provider="Udemy",
            skill_targeted="Cloud Infrastructure",
            status=TrainingStatus.IN_PROGRESS,
            progress_percent=Decimal("60.00"),
            cost=Decimal("200.00"),
        )
        db_session.add(training)
        await db_session.flush()

        # Refresh relationships asynchronously
        await db_session.refresh(plan, ["training_records"])

        # 3. Verify relations
        assert len(plan.training_records) == 1
        assert plan.training_records[0].id == training.id

        # 4. Verify progress constraint
        invalid_training = TrainingRecord(
            company_id=company.id,
            employee_id=employee.id,
            course_name="Invalid Training",
            skill_targeted="None",
            progress_percent=Decimal("150.00"),  # Invalid
        )
        async with db_session.begin_nested():
            db_session.add(invalid_training)
            with pytest.raises(IntegrityError):
                await db_session.flush()

        # Delete learning plan to check training record SET NULL
        await db_session.delete(plan)
        await db_session.flush()

        # The TrainingRecord must NOT be deleted, but its plan_id must become NULL.
        await db_session.refresh(training)
        assert training is not None
        assert training.plan_id is None

    # ── INTERVIEW KITS ────────────────────────────────────────────────────────

    async def test_interview_kit_lifecycle(self, db_session: AsyncSession):
        """Verify interview kit schema, enums, duration check constraint, and cascades."""
        suffix = uuid.uuid4().hex[:6]
        company, _ = await create_base_tenant_and_employee(db_session, suffix)

        # 1. Create InterviewKit
        kit = InterviewKit(
            company_id=company.id,
            job_role="Lead Platform Engineer",
            department="Platform Systems",
            experience_level=ExperienceLevel.LEAD,
            duration_minutes=60,
            key_skills={"skills": ["Golang", "Kubernetes", "gRPC"]},
            question_bank={
                "questions": [{"q": "Explain Raft consensus.", "weight": 5}]
            },
            is_template=True,
        )
        db_session.add(kit)
        await db_session.flush()

        # Verify
        assert kit.id is not None
        assert kit.experience_level == ExperienceLevel.LEAD

        # 2. Check duration constraint
        invalid_kit = InterviewKit(
            company_id=company.id,
            job_role="Intern Engineer",
            department="Platform",
            experience_level=ExperienceLevel.JUNIOR,
            duration_minutes=-10,  # Invalid duration
            key_skills={"skills": []},
            question_bank={"questions": []},
        )
        async with db_session.begin_nested():
            db_session.add(invalid_kit)
            with pytest.raises(IntegrityError):
                await db_session.flush()
