"""create workflow tables

Revision ID: e61edd53de79
Revises: 0005_create_policy_tables
Create Date: 2026-07-09 08:06:46.884430+00:00
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

import alembic.op as op

# revision identifiers, used by Alembic.
revision: str = "e61edd53de79"
down_revision: Union[str, None] = "0005_create_policy_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Explicit ENUM declarations with create_type=False
onboarding_status_enum = postgresql.ENUM(
    "PENDING",
    "IN_PROGRESS",
    "ON_TRACK",
    "BEHIND",
    "COMPLETE",
    name="onboarding_status_enum",
    create_type=False,
)
onboarding_task_category_enum = postgresql.ENUM(
    "SCHEDULE",
    "TASK",
    "GOAL",
    "DOCUMENT",
    "TOOL",
    "MEETING",
    name="onboarding_task_category_enum",
    create_type=False,
)
task_status_enum = postgresql.ENUM(
    "PENDING",
    "IN_PROGRESS",
    "COMPLETED",
    name="task_status_enum",
    create_type=False,
)
review_status_enum = postgresql.ENUM(
    "DRAFT",
    "UNDER_REVIEW",
    "COMPLETED",
    "ARCHIVED",
    name="review_status_enum",
    create_type=False,
)
risk_level_enum = postgresql.ENUM(
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
    name="risk_level_enum",
    create_type=False,
)
retention_strategy_status_enum = postgresql.ENUM(
    "PROPOSED",
    "APPROVED",
    "REJECTED",
    "IMPLEMENTED",
    name="retention_strategy_status_enum",
    create_type=False,
)
training_status_enum = postgresql.ENUM(
    "NOT_STARTED",
    "IN_PROGRESS",
    "COMPLETED",
    "EXPIRED",
    name="training_status_enum",
    create_type=False,
)
approval_status_enum = postgresql.ENUM(
    "PENDING",
    "APPROVED",
    "REJECTED",
    name="approval_status_enum",
    create_type=False,
)
experience_level_enum = postgresql.ENUM(
    "JUNIOR",
    "MID",
    "SENIOR",
    "LEAD",
    "DIRECTOR",
    name="experience_level_enum",
    create_type=False,
)


def upgrade() -> None:
    # Create the custom PostgreSQL enum types
    onboarding_status_enum.create(op.get_bind(), checkfirst=True)
    onboarding_task_category_enum.create(op.get_bind(), checkfirst=True)
    task_status_enum.create(op.get_bind(), checkfirst=True)
    review_status_enum.create(op.get_bind(), checkfirst=True)
    risk_level_enum.create(op.get_bind(), checkfirst=True)
    retention_strategy_status_enum.create(op.get_bind(), checkfirst=True)
    training_status_enum.create(op.get_bind(), checkfirst=True)
    approval_status_enum.create(op.get_bind(), checkfirst=True)

    # ── interview_kits ────────────────────────────────────────────────────────
    op.create_table(
        "interview_kits",
        sa.Column(
            "company_id", sa.UUID(), nullable=False, comment="Tenant company identifier"
        ),
        sa.Column(
            "job_role",
            sa.String(length=150),
            nullable=False,
            comment="Designation job role (e.g. Backend Engineer)",
        ),
        sa.Column(
            "department",
            sa.String(length=100),
            nullable=False,
            comment="Department role belongs to",
        ),
        sa.Column(
            "experience_level",
            experience_level_enum,
            nullable=False,
            comment="Target seniority level classification",
        ),
        sa.Column(
            "duration_minutes",
            sa.Integer(),
            nullable=False,
            comment="Target interview duration minutes",
        ),
        sa.Column(
            "key_skills",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            comment="List of skills and competence priorities assessed",
        ),
        sa.Column(
            "interview_structure",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Timing structure layouts",
        ),
        sa.Column(
            "question_bank",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            comment="Draft list of questions, expected answers, scorecard weights",
        ),
        sa.Column(
            "evaluation_rubric",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Structured scoring rubrics parameters",
        ),
        sa.Column(
            "panel_guide",
            sa.Text(),
            nullable=True,
            comment="Draft panel instruction guidance notes",
        ),
        sa.Column(
            "is_template",
            sa.Boolean(),
            nullable=False,
            comment="Indicates if reusable template",
        ),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            nullable=False,
            comment="Soft-delete logical exclusion flag",
        ),
        sa.Column(
            "version_number",
            sa.Integer(),
            nullable=True,
            comment="Revision version counter",
        ),
        sa.Column(
            "previous_version_id",
            sa.UUID(),
            nullable=True,
            comment="Self-reference to the previous revision",
        ),
        sa.Column(
            "human_review_required",
            sa.Boolean(),
            nullable=False,
            comment="Flags if human validation is pending",
        ),
        sa.Column(
            "reviewed_by",
            sa.UUID(),
            nullable=True,
            comment="User ID who reviewed the interview kit",
        ),
        sa.Column(
            "reviewed_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Approval timestamp",
        ),
        sa.Column(
            "approval_status",
            approval_status_enum,
            nullable=False,
            comment="Verification status state",
        ),
        sa.Column(
            "created_by",
            sa.UUID(),
            nullable=True,
            comment="User ID who created the record",
        ),
        sa.Column(
            "updated_by",
            sa.UUID(),
            nullable=True,
            comment="User ID who last updated the record",
        ),
        sa.Column(
            "id",
            sa.UUID(),
            nullable=False,
            comment="Universally unique record identifier",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Record creation timestamp (UTC)",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Record last-update timestamp (UTC)",
        ),
        sa.CheckConstraint("duration_minutes > 0", name="chk_interview_kits_duration"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["previous_version_id"], ["interview_kits.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["reviewed_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_interview_kits_approval_status"),
        "interview_kits",
        ["approval_status"],
        unique=False,
    )
    op.create_index(
        "ix_interview_kits_company_created",
        "interview_kits",
        ["company_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_interview_kits_company_department",
        "interview_kits",
        ["company_id", "department"],
        unique=False,
    )
    op.create_index(
        op.f("ix_interview_kits_company_id"),
        "interview_kits",
        ["company_id"],
        unique=False,
    )
    op.create_index(
        "ix_interview_kits_company_role_level",
        "interview_kits",
        ["company_id", "job_role", "experience_level"],
        unique=False,
    )
    op.create_index(
        op.f("ix_interview_kits_experience_level"),
        "interview_kits",
        ["experience_level"],
        unique=False,
    )
    op.create_index(
        op.f("ix_interview_kits_previous_version_id"),
        "interview_kits",
        ["previous_version_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_interview_kits_reviewed_by"),
        "interview_kits",
        ["reviewed_by"],
        unique=False,
    )

    # ── attrition_assessments ──────────────────────────────────────────────────
    op.create_table(
        "attrition_assessments",
        sa.Column(
            "company_id", sa.UUID(), nullable=False, comment="Tenant company identifier"
        ),
        sa.Column(
            "employee_id",
            sa.UUID(),
            nullable=False,
            comment="Employee under assessment",
        ),
        sa.Column(
            "risk_score",
            sa.Numeric(precision=5, scale=2),
            nullable=False,
            comment="Locally computed/model risk percentage",
        ),
        sa.Column(
            "risk_level",
            risk_level_enum,
            nullable=False,
            comment="Risk categorization level",
        ),
        sa.Column(
            "risk_factors",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Explainable feature importances (e.g. SHAP values / local metrics)",
        ),
        sa.Column(
            "stay_interview_questions",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="AI-generated stay interview questions list draft",
        ),
        sa.Column(
            "replacement_cost",
            sa.Numeric(precision=12, scale=2),
            nullable=True,
            comment="Estimated replacement cost value",
        ),
        sa.Column(
            "manager_satisfaction_score",
            sa.Numeric(precision=3, scale=1),
            nullable=True,
            comment="Manager satisfaction rating on 1-5 scale",
        ),
        sa.Column(
            "overtime_hours",
            sa.Numeric(precision=5, scale=1),
            nullable=True,
            comment="Average monthly overtime hours",
        ),
        sa.Column(
            "is_active_assessment",
            sa.Boolean(),
            nullable=False,
            comment="Indicates if this is the active assessment cycle",
        ),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            nullable=False,
            comment="Soft-delete logical exclusion flag",
        ),
        sa.Column(
            "human_review_required",
            sa.Boolean(),
            nullable=False,
            comment="Flags if human validation is pending",
        ),
        sa.Column(
            "reviewed_by",
            sa.UUID(),
            nullable=True,
            comment="User ID who reviewed the risk score",
        ),
        sa.Column(
            "reviewed_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Verification timestamp",
        ),
        sa.Column(
            "approval_status",
            approval_status_enum,
            nullable=False,
            comment="Verification status state",
        ),
        sa.Column(
            "created_by",
            sa.UUID(),
            nullable=True,
            comment="User ID who created the record",
        ),
        sa.Column(
            "updated_by",
            sa.UUID(),
            nullable=True,
            comment="User ID who last updated the record",
        ),
        sa.Column(
            "id",
            sa.UUID(),
            nullable=False,
            comment="Universally unique record identifier",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Record creation timestamp (UTC)",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Record last-update timestamp (UTC)",
        ),
        sa.CheckConstraint(
            "manager_satisfaction_score >= 0.0 AND manager_satisfaction_score <= 5.0",
            name="chk_attrition_assessments_satisfaction",
        ),
        sa.CheckConstraint(
            "risk_score >= 0.00 AND risk_score <= 100.00",
            name="chk_attrition_assessments_risk",
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reviewed_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_attrition_assessments_approval_status"),
        "attrition_assessments",
        ["approval_status"],
        unique=False,
    )
    op.create_index(
        "ix_attrition_assessments_company_created",
        "attrition_assessments",
        ["company_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_attrition_assessments_company_employee",
        "attrition_assessments",
        ["company_id", "employee_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_attrition_assessments_company_id"),
        "attrition_assessments",
        ["company_id"],
        unique=False,
    )
    op.create_index(
        "ix_attrition_assessments_company_risk",
        "attrition_assessments",
        ["company_id", "risk_level"],
        unique=False,
    )
    op.create_index(
        op.f("ix_attrition_assessments_employee_id"),
        "attrition_assessments",
        ["employee_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_attrition_assessments_reviewed_by"),
        "attrition_assessments",
        ["reviewed_by"],
        unique=False,
    )
    op.create_index(
        op.f("ix_attrition_assessments_risk_level"),
        "attrition_assessments",
        ["risk_level"],
        unique=False,
    )

    # ── learning_plans ────────────────────────────────────────────────────────
    op.create_table(
        "learning_plans",
        sa.Column(
            "company_id", sa.UUID(), nullable=False, comment="Tenant company identifier"
        ),
        sa.Column(
            "employee_id",
            sa.UUID(),
            nullable=False,
            comment="Employee target for skill path recommendations",
        ),
        sa.Column(
            "current_role",
            sa.String(length=150),
            nullable=False,
            comment="Employee's current designation",
        ),
        sa.Column(
            "target_role",
            sa.String(length=150),
            nullable=False,
            comment="Designation being recommended for learning path",
        ),
        sa.Column(
            "readiness_score",
            sa.Numeric(precision=5, scale=2),
            nullable=False,
            comment="Readiness score locally/analytically generated",
        ),
        sa.Column(
            "skill_gap_analysis",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            comment="List of missing competencies and priorities",
        ),
        sa.Column(
            "learning_path_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            comment="Detailed timeline, certification guides, and materials",
        ),
        sa.Column(
            "estimated_roi",
            sa.String(length=255),
            nullable=True,
            comment="Estimated training business ROI details",
        ),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            nullable=False,
            comment="Soft-delete logical exclusion flag",
        ),
        sa.Column(
            "version_number",
            sa.Integer(),
            nullable=True,
            comment="Revision version counter",
        ),
        sa.Column(
            "previous_version_id",
            sa.UUID(),
            nullable=True,
            comment="Self-reference to the previous revision",
        ),
        sa.Column(
            "human_review_required",
            sa.Boolean(),
            nullable=False,
            comment="Flags if human validation is pending",
        ),
        sa.Column(
            "reviewed_by",
            sa.UUID(),
            nullable=True,
            comment="User ID who reviewed the learning plan",
        ),
        sa.Column(
            "reviewed_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Approval timestamp",
        ),
        sa.Column(
            "approval_status",
            approval_status_enum,
            nullable=False,
            comment="Verification status state",
        ),
        sa.Column(
            "created_by",
            sa.UUID(),
            nullable=True,
            comment="User ID who created the record",
        ),
        sa.Column(
            "updated_by",
            sa.UUID(),
            nullable=True,
            comment="User ID who last updated the record",
        ),
        sa.Column(
            "id",
            sa.UUID(),
            nullable=False,
            comment="Universally unique record identifier",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Record creation timestamp (UTC)",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Record last-update timestamp (UTC)",
        ),
        sa.CheckConstraint(
            "readiness_score >= 0.00 AND readiness_score <= 100.00",
            name="chk_learning_plans_readiness",
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["previous_version_id"], ["learning_plans.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["reviewed_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_learning_plans_approval_status"),
        "learning_plans",
        ["approval_status"],
        unique=False,
    )
    op.create_index(
        "ix_learning_plans_company_created",
        "learning_plans",
        ["company_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_learning_plans_company_employee",
        "learning_plans",
        ["company_id", "employee_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_learning_plans_company_id"),
        "learning_plans",
        ["company_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_learning_plans_employee_id"),
        "learning_plans",
        ["employee_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_learning_plans_previous_version_id"),
        "learning_plans",
        ["previous_version_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_learning_plans_reviewed_by"),
        "learning_plans",
        ["reviewed_by"],
        unique=False,
    )

    # ── onboarding_plans ──────────────────────────────────────────────────────
    op.create_table(
        "onboarding_plans",
        sa.Column(
            "company_id", sa.UUID(), nullable=False, comment="Tenant company identifier"
        ),
        sa.Column(
            "employee_id", sa.UUID(), nullable=False, comment="Employee being onboarded"
        ),
        sa.Column(
            "status",
            onboarding_status_enum,
            nullable=False,
            comment="Onboarding progress status",
        ),
        sa.Column(
            "progress_percent",
            sa.Numeric(precision=5, scale=2),
            nullable=False,
            comment="Onboarding progress percentage",
        ),
        sa.Column(
            "welcome_email_text",
            sa.Text(),
            nullable=True,
            comment="AI-generated welcome email draft",
        ),
        sa.Column(
            "team_announcement_text",
            sa.Text(),
            nullable=True,
            comment="AI-generated team announcement draft",
        ),
        sa.Column(
            "plan_data_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Structured onboarding roadmap goals and milestones",
        ),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            nullable=False,
            comment="Soft-delete logical exclusion flag",
        ),
        sa.Column(
            "created_by",
            sa.UUID(),
            nullable=True,
            comment="User ID who created the record",
        ),
        sa.Column(
            "updated_by",
            sa.UUID(),
            nullable=True,
            comment="User ID who last updated the record",
        ),
        sa.Column(
            "id",
            sa.UUID(),
            nullable=False,
            comment="Universally unique record identifier",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Record creation timestamp (UTC)",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Record last-update timestamp (UTC)",
        ),
        sa.CheckConstraint(
            "progress_percent >= 0.00 AND progress_percent <= 100.00",
            name="chk_onboarding_plans_progress",
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_onboarding_plans_company_created",
        "onboarding_plans",
        ["company_id", "created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_onboarding_plans_company_id"),
        "onboarding_plans",
        ["company_id"],
        unique=False,
    )
    op.create_index(
        "ix_onboarding_plans_company_status",
        "onboarding_plans",
        ["company_id", "status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_onboarding_plans_employee_id"),
        "onboarding_plans",
        ["employee_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_onboarding_plans_status"), "onboarding_plans", ["status"], unique=False
    )
    op.create_index(
        "uq_onboarding_plans_active_employee",
        "onboarding_plans",
        ["company_id", "employee_id"],
        unique=True,
        postgresql_where="is_deleted = false",
    )

    # ── performance_reviews ───────────────────────────────────────────────────
    op.create_table(
        "performance_reviews",
        sa.Column(
            "company_id", sa.UUID(), nullable=False, comment="Tenant company identifier"
        ),
        sa.Column(
            "employee_id", sa.UUID(), nullable=False, comment="Employee being reviewed"
        ),
        sa.Column(
            "manager_id",
            sa.UUID(),
            nullable=True,
            comment="Manager reviewing the employee",
        ),
        sa.Column(
            "review_period",
            sa.String(length=100),
            nullable=False,
            comment="Review cycle identifier (e.g. Q1 2026, Annual 2025)",
        ),
        sa.Column(
            "status", review_status_enum, nullable=False, comment="Review state status"
        ),
        sa.Column(
            "goals_achieved",
            sa.Integer(),
            nullable=False,
            comment="Number of goals met in review period",
        ),
        sa.Column(
            "total_goals",
            sa.Integer(),
            nullable=False,
            comment="Total goals set in review period",
        ),
        sa.Column(
            "attendance_percent",
            sa.Numeric(precision=5, scale=2),
            nullable=True,
            comment="Attendance rating percentage",
        ),
        sa.Column(
            "manager_observations",
            sa.Text(),
            nullable=True,
            comment="Observations entered by evaluating manager",
        ),
        sa.Column(
            "peer_feedback",
            sa.Text(),
            nullable=True,
            comment="Collated peer reviews and notes",
        ),
        sa.Column(
            "review_summary",
            sa.Text(),
            nullable=True,
            comment="AI-generated review summary draft",
        ),
        sa.Column(
            "rating_suggestion",
            sa.String(length=100),
            nullable=True,
            comment="AI rating suggestion label",
        ),
        sa.Column(
            "key_achievements",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="List of highlighted accomplishments",
        ),
        sa.Column(
            "development_areas",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Improvement priorities list",
        ),
        sa.Column(
            "bias_check_notes",
            sa.Text(),
            nullable=True,
            comment="AI-generated language bias evaluation notes",
        ),
        sa.Column(
            "promotion_readiness",
            sa.Boolean(),
            nullable=False,
            comment="Indicates if candidate is fit for promotion",
        ),
        sa.Column(
            "salary_revision_label",
            sa.String(length=100),
            nullable=True,
            comment="Compensation revision draft recommendations",
        ),
        sa.Column(
            "smart_goals",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Draft list of SMART goals for next cycle",
        ),
        sa.Column(
            "development_plan",
            sa.Text(),
            nullable=True,
            comment="Detailed employee career development path",
        ),
        sa.Column(
            "pip_details",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Performance Improvement Plan details if applicable",
        ),
        sa.Column(
            "signed_off_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Timestamp when final sign-off completed",
        ),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            nullable=False,
            comment="Soft-delete logical exclusion flag",
        ),
        sa.Column(
            "version_number",
            sa.Integer(),
            nullable=True,
            comment="Revision version counter",
        ),
        sa.Column(
            "previous_version_id",
            sa.UUID(),
            nullable=True,
            comment="Self-reference to the previous revision",
        ),
        sa.Column(
            "human_review_required",
            sa.Boolean(),
            nullable=False,
            comment="Flags if human approval is pending",
        ),
        sa.Column(
            "reviewed_by",
            sa.UUID(),
            nullable=True,
            comment="User ID who approved the review",
        ),
        sa.Column(
            "reviewed_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Approval timestamp",
        ),
        sa.Column(
            "approval_status",
            approval_status_enum,
            nullable=False,
            comment="Human approval status state",
        ),
        sa.Column(
            "created_by",
            sa.UUID(),
            nullable=True,
            comment="User ID who created the record",
        ),
        sa.Column(
            "updated_by",
            sa.UUID(),
            nullable=True,
            comment="User ID who last updated the record",
        ),
        sa.Column(
            "id",
            sa.UUID(),
            nullable=False,
            comment="Universally unique record identifier",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Record creation timestamp (UTC)",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Record last-update timestamp (UTC)",
        ),
        sa.CheckConstraint(
            "attendance_percent >= 0.00 AND attendance_percent <= 100.00",
            name="chk_performance_reviews_attendance",
        ),
        sa.CheckConstraint(
            "goals_achieved >= 0 AND total_goals >= 0 AND goals_achieved <= total_goals",
            name="chk_performance_reviews_goals",
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["manager_id"], ["employees.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(
            ["previous_version_id"], ["performance_reviews.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["reviewed_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_performance_reviews_approval_status"),
        "performance_reviews",
        ["approval_status"],
        unique=False,
    )
    op.create_index(
        "ix_performance_reviews_company_created",
        "performance_reviews",
        ["company_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_performance_reviews_company_employee",
        "performance_reviews",
        ["company_id", "employee_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_performance_reviews_company_id"),
        "performance_reviews",
        ["company_id"],
        unique=False,
    )
    op.create_index(
        "ix_performance_reviews_company_manager",
        "performance_reviews",
        ["company_id", "manager_id"],
        unique=False,
    )
    op.create_index(
        "ix_performance_reviews_company_status",
        "performance_reviews",
        ["company_id", "status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_performance_reviews_employee_id"),
        "performance_reviews",
        ["employee_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_performance_reviews_manager_id"),
        "performance_reviews",
        ["manager_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_performance_reviews_previous_version_id"),
        "performance_reviews",
        ["previous_version_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_performance_reviews_reviewed_by"),
        "performance_reviews",
        ["reviewed_by"],
        unique=False,
    )
    op.create_index(
        op.f("ix_performance_reviews_status"),
        "performance_reviews",
        ["status"],
        unique=False,
    )

    # ── onboarding_tasks ──────────────────────────────────────────────────────
    op.create_table(
        "onboarding_tasks",
        sa.Column(
            "company_id", sa.UUID(), nullable=False, comment="Tenant company identifier"
        ),
        sa.Column(
            "plan_id",
            sa.UUID(),
            nullable=False,
            comment="Parent onboarding plan identifier",
        ),
        sa.Column("title", sa.String(length=255), nullable=False, comment="Task title"),
        sa.Column(
            "description",
            sa.String(length=500),
            nullable=True,
            comment="Task description",
        ),
        sa.Column(
            "category",
            onboarding_task_category_enum,
            nullable=False,
            comment="Task category type",
        ),
        sa.Column(
            "status", task_status_enum, nullable=False, comment="Task execution status"
        ),
        sa.Column("due_date", sa.Date(), nullable=True, comment="Task deadline date"),
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Timestamp when task was marked completed",
        ),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            nullable=False,
            comment="Soft-delete logical exclusion flag",
        ),
        sa.Column(
            "created_by",
            sa.UUID(),
            nullable=True,
            comment="User ID who created the record",
        ),
        sa.Column(
            "updated_by",
            sa.UUID(),
            nullable=True,
            comment="User ID who last updated the record",
        ),
        sa.Column(
            "id",
            sa.UUID(),
            nullable=False,
            comment="Universally unique record identifier",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Record creation timestamp (UTC)",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Record last-update timestamp (UTC)",
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["plan_id"], ["onboarding_plans.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_onboarding_tasks_category"),
        "onboarding_tasks",
        ["category"],
        unique=False,
    )
    op.create_index(
        "ix_onboarding_tasks_company_created",
        "onboarding_tasks",
        ["company_id", "created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_onboarding_tasks_company_id"),
        "onboarding_tasks",
        ["company_id"],
        unique=False,
    )
    op.create_index(
        "ix_onboarding_tasks_company_plan",
        "onboarding_tasks",
        ["company_id", "plan_id"],
        unique=False,
    )
    op.create_index(
        "ix_onboarding_tasks_company_status",
        "onboarding_tasks",
        ["company_id", "status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_onboarding_tasks_plan_id"),
        "onboarding_tasks",
        ["plan_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_onboarding_tasks_status"), "onboarding_tasks", ["status"], unique=False
    )

    # ── retention_strategies ──────────────────────────────────────────────────
    op.create_table(
        "retention_strategies",
        sa.Column(
            "company_id", sa.UUID(), nullable=False, comment="Tenant company identifier"
        ),
        sa.Column(
            "assessment_id",
            sa.UUID(),
            nullable=False,
            comment="Linked attrition risk assessment identifier",
        ),
        sa.Column(
            "employee_id",
            sa.UUID(),
            nullable=False,
            comment="Employee target for retention",
        ),
        sa.Column(
            "recommendations",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            comment="Structured AI suggested retention actions (benefits, salary, environment)",
        ),
        sa.Column(
            "action_plan", sa.Text(), nullable=True, comment="HR Action plan text draft"
        ),
        sa.Column(
            "status",
            retention_strategy_status_enum,
            nullable=False,
            comment="Execution strategy status state",
        ),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            nullable=False,
            comment="Soft-delete logical exclusion flag",
        ),
        sa.Column(
            "version_number",
            sa.Integer(),
            nullable=True,
            comment="Revision version counter",
        ),
        sa.Column(
            "previous_version_id",
            sa.UUID(),
            nullable=True,
            comment="Self-reference to the previous revision",
        ),
        sa.Column(
            "human_review_required",
            sa.Boolean(),
            nullable=False,
            comment="Flags if human validation is pending",
        ),
        sa.Column(
            "reviewed_by",
            sa.UUID(),
            nullable=True,
            comment="User ID who approved the retention strategies",
        ),
        sa.Column(
            "reviewed_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Approval timestamp",
        ),
        sa.Column(
            "approval_status",
            approval_status_enum,
            nullable=False,
            comment="Verification status state",
        ),
        sa.Column(
            "created_by",
            sa.UUID(),
            nullable=True,
            comment="User ID who created the record",
        ),
        sa.Column(
            "updated_by",
            sa.UUID(),
            nullable=True,
            comment="User ID who last updated the record",
        ),
        sa.Column(
            "id",
            sa.UUID(),
            nullable=False,
            comment="Universally unique record identifier",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Record creation timestamp (UTC)",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Record last-update timestamp (UTC)",
        ),
        sa.ForeignKeyConstraint(
            ["assessment_id"], ["attrition_assessments.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["previous_version_id"], ["retention_strategies.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["reviewed_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_retention_strategies_approval_status"),
        "retention_strategies",
        ["approval_status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_retention_strategies_assessment_id"),
        "retention_strategies",
        ["assessment_id"],
        unique=True,
    )
    op.create_index(
        "ix_retention_strategies_company_created",
        "retention_strategies",
        ["company_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_retention_strategies_company_employee",
        "retention_strategies",
        ["company_id", "employee_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_retention_strategies_company_id"),
        "retention_strategies",
        ["company_id"],
        unique=False,
    )
    op.create_index(
        "ix_retention_strategies_company_status",
        "retention_strategies",
        ["company_id", "status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_retention_strategies_employee_id"),
        "retention_strategies",
        ["employee_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_retention_strategies_previous_version_id"),
        "retention_strategies",
        ["previous_version_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_retention_strategies_reviewed_by"),
        "retention_strategies",
        ["reviewed_by"],
        unique=False,
    )
    op.create_index(
        op.f("ix_retention_strategies_status"),
        "retention_strategies",
        ["status"],
        unique=False,
    )

    # ── training_records ──────────────────────────────────────────────────────
    op.create_table(
        "training_records",
        sa.Column(
            "company_id", sa.UUID(), nullable=False, comment="Tenant company identifier"
        ),
        sa.Column(
            "employee_id",
            sa.UUID(),
            nullable=False,
            comment="Employee enrolled in training",
        ),
        sa.Column(
            "plan_id",
            sa.UUID(),
            nullable=True,
            comment="Parent learning plan recommended pathway",
        ),
        sa.Column(
            "course_name",
            sa.String(length=255),
            nullable=False,
            comment="Course display name",
        ),
        sa.Column(
            "provider",
            sa.String(length=255),
            nullable=True,
            comment="Platform course host provider (e.g. Coursera)",
        ),
        sa.Column(
            "skill_targeted",
            sa.String(length=100),
            nullable=False,
            comment="Competence targeted by training",
        ),
        sa.Column(
            "status",
            training_status_enum,
            nullable=False,
            comment="Current training record state",
        ),
        sa.Column(
            "progress_percent",
            sa.Numeric(precision=5, scale=2),
            nullable=False,
            comment="In-progress percent computed locally",
        ),
        sa.Column(
            "cost",
            sa.Numeric(precision=10, scale=2),
            nullable=False,
            comment="Cost of enrolled training program",
        ),
        sa.Column(
            "started_at",
            sa.Date(),
            nullable=True,
            comment="Start date of training course",
        ),
        sa.Column(
            "completed_at",
            sa.Date(),
            nullable=True,
            comment="Completion date of training course",
        ),
        sa.Column(
            "certificate_url",
            sa.String(length=500),
            nullable=True,
            comment="Link to course completion certification asset",
        ),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            nullable=False,
            comment="Soft-delete logical exclusion flag",
        ),
        sa.Column(
            "created_by",
            sa.UUID(),
            nullable=True,
            comment="User ID who created the record",
        ),
        sa.Column(
            "updated_by",
            sa.UUID(),
            nullable=True,
            comment="User ID who last updated the record",
        ),
        sa.Column(
            "id",
            sa.UUID(),
            nullable=False,
            comment="Universally unique record identifier",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Record creation timestamp (UTC)",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Record last-update timestamp (UTC)",
        ),
        sa.CheckConstraint("cost >= 0.00", name="chk_training_records_cost"),
        sa.CheckConstraint(
            "progress_percent >= 0.00 AND progress_percent <= 100.00",
            name="chk_training_records_progress",
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["plan_id"], ["learning_plans.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_training_records_company_created",
        "training_records",
        ["company_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_training_records_company_employee",
        "training_records",
        ["company_id", "employee_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_training_records_company_id"),
        "training_records",
        ["company_id"],
        unique=False,
    )
    op.create_index(
        "ix_training_records_company_plan",
        "training_records",
        ["company_id", "plan_id"],
        unique=False,
    )
    op.create_index(
        "ix_training_records_company_status",
        "training_records",
        ["company_id", "status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_training_records_employee_id"),
        "training_records",
        ["employee_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_training_records_plan_id"),
        "training_records",
        ["plan_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_training_records_status"), "training_records", ["status"], unique=False
    )

    # Existing tables sync omitted to avoid unrelated migration side effects


def downgrade() -> None:
    # Drop all workflow tables
    # Drop all workflow tables in correct dependency order (children first)
    # 1. onboarding_tasks (depends on onboarding_plans)
    op.drop_index(op.f("ix_onboarding_tasks_status"), table_name="onboarding_tasks")
    op.drop_index(op.f("ix_onboarding_tasks_plan_id"), table_name="onboarding_tasks")
    op.drop_index("ix_onboarding_tasks_company_status", table_name="onboarding_tasks")
    op.drop_index("ix_onboarding_tasks_company_plan", table_name="onboarding_tasks")
    op.drop_index(op.f("ix_onboarding_tasks_company_id"), table_name="onboarding_tasks")
    op.drop_index("ix_onboarding_tasks_company_created", table_name="onboarding_tasks")
    op.drop_index(op.f("ix_onboarding_tasks_category"), table_name="onboarding_tasks")
    op.drop_table("onboarding_tasks")

    # 2. onboarding_plans
    op.drop_index(
        "uq_onboarding_plans_active_employee",
        table_name="onboarding_plans",
        postgresql_where="is_deleted = false",
    )
    op.drop_index(op.f("ix_onboarding_plans_status"), table_name="onboarding_plans")
    op.drop_index(
        op.f("ix_onboarding_plans_employee_id"), table_name="onboarding_plans"
    )
    op.drop_index("ix_onboarding_plans_company_status", table_name="onboarding_plans")
    op.drop_index(op.f("ix_onboarding_plans_company_id"), table_name="onboarding_plans")
    op.drop_index("ix_onboarding_plans_company_created", table_name="onboarding_plans")
    op.drop_table("onboarding_plans")

    # 3. training_records (depends on learning_plans)
    op.drop_index(op.f("ix_training_records_status"), table_name="training_records")
    op.drop_index(op.f("ix_training_records_plan_id"), table_name="training_records")
    op.drop_index(
        op.f("ix_training_records_employee_id"), table_name="training_records"
    )
    op.drop_index("ix_training_records_company_status", table_name="training_records")
    op.drop_index("ix_training_records_company_plan", table_name="training_records")
    op.drop_index(op.f("ix_training_records_company_id"), table_name="training_records")
    op.drop_index("ix_training_records_company_employee", table_name="training_records")
    op.drop_index("ix_training_records_company_created", table_name="training_records")
    op.drop_table("training_records")

    # 4. learning_plans
    op.drop_index(op.f("ix_learning_plans_reviewed_by"), table_name="learning_plans")
    op.drop_index(
        op.f("ix_learning_plans_previous_version_id"), table_name="learning_plans"
    )
    op.drop_index(op.f("ix_learning_plans_employee_id"), table_name="learning_plans")
    op.drop_index(op.f("ix_learning_plans_company_id"), table_name="learning_plans")
    op.drop_index("ix_learning_plans_company_employee", table_name="learning_plans")
    op.drop_index("ix_learning_plans_company_created", table_name="learning_plans")
    op.drop_index(
        op.f("ix_learning_plans_approval_status"), table_name="learning_plans"
    )
    op.drop_table("learning_plans")

    # 5. retention_strategies (depends on attrition_assessments)
    op.drop_index(
        op.f("ix_retention_strategies_status"), table_name="retention_strategies"
    )
    op.drop_index(
        op.f("ix_retention_strategies_reviewed_by"), table_name="retention_strategies"
    )
    op.drop_index(
        op.f("ix_retention_strategies_previous_version_id"),
        table_name="retention_strategies",
    )
    op.drop_index(
        op.f("ix_retention_strategies_employee_id"), table_name="retention_strategies"
    )
    op.drop_index(
        "ix_retention_strategies_company_status", table_name="retention_strategies"
    )
    op.drop_index(
        op.f("ix_retention_strategies_company_id"), table_name="retention_strategies"
    )
    op.drop_index(
        "ix_retention_strategies_company_employee", table_name="retention_strategies"
    )
    op.drop_index(
        "ix_retention_strategies_company_created", table_name="retention_strategies"
    )
    op.drop_index(
        op.f("ix_retention_strategies_assessment_id"), table_name="retention_strategies"
    )
    op.drop_index(
        op.f("ix_retention_strategies_approval_status"),
        table_name="retention_strategies",
    )
    op.drop_table("retention_strategies")

    # 6. attrition_assessments
    op.drop_index(
        op.f("ix_attrition_assessments_risk_level"), table_name="attrition_assessments"
    )
    op.drop_index(
        op.f("ix_attrition_assessments_reviewed_by"), table_name="attrition_assessments"
    )
    op.drop_index(
        op.f("ix_attrition_assessments_employee_id"), table_name="attrition_assessments"
    )
    op.drop_index(
        "ix_attrition_assessments_company_risk", table_name="attrition_assessments"
    )
    op.drop_index(
        op.f("ix_attrition_assessments_company_id"), table_name="attrition_assessments"
    )
    op.drop_index(
        "ix_attrition_assessments_company_employee", table_name="attrition_assessments"
    )
    op.drop_index(
        "ix_attrition_assessments_company_created", table_name="attrition_assessments"
    )
    op.drop_index(
        op.f("ix_attrition_assessments_approval_status"),
        table_name="attrition_assessments",
    )
    op.drop_table("attrition_assessments")

    # 7. performance_reviews
    op.drop_index(
        op.f("ix_performance_reviews_status"), table_name="performance_reviews"
    )
    op.drop_index(
        op.f("ix_performance_reviews_reviewed_by"), table_name="performance_reviews"
    )
    op.drop_index(
        op.f("ix_performance_reviews_previous_version_id"),
        table_name="performance_reviews",
    )
    op.drop_index(
        op.f("ix_performance_reviews_manager_id"), table_name="performance_reviews"
    )
    op.drop_index(
        op.f("ix_performance_reviews_employee_id"), table_name="performance_reviews"
    )
    op.drop_index(
        "ix_performance_reviews_company_status", table_name="performance_reviews"
    )
    op.drop_index(
        "ix_performance_reviews_company_manager", table_name="performance_reviews"
    )
    op.drop_index(
        op.f("ix_performance_reviews_company_id"), table_name="performance_reviews"
    )
    op.drop_index(
        "ix_performance_reviews_company_employee", table_name="performance_reviews"
    )
    op.drop_index(
        "ix_performance_reviews_company_created", table_name="performance_reviews"
    )
    op.drop_index(
        op.f("ix_performance_reviews_approval_status"), table_name="performance_reviews"
    )
    op.drop_table("performance_reviews")

    # 8. interview_kits
    op.drop_index(op.f("ix_interview_kits_reviewed_by"), table_name="interview_kits")
    op.drop_index(
        op.f("ix_interview_kits_previous_version_id"), table_name="interview_kits"
    )
    op.drop_index(
        op.f("ix_interview_kits_experience_level"), table_name="interview_kits"
    )
    op.drop_index("ix_interview_kits_company_role_level", table_name="interview_kits")
    op.drop_index(op.f("ix_interview_kits_company_id"), table_name="interview_kits")
    op.drop_index("ix_interview_kits_company_department", table_name="interview_kits")
    op.drop_index("ix_interview_kits_company_created", table_name="interview_kits")
    op.drop_index(
        op.f("ix_interview_kits_approval_status"), table_name="interview_kits"
    )
    op.drop_table("interview_kits")

    # Revert existing tables sync omitted

    # Drop custom PostgreSQL enum types
    onboarding_status_enum.drop(op.get_bind(), checkfirst=True)
    onboarding_task_category_enum.drop(op.get_bind(), checkfirst=True)
    task_status_enum.drop(op.get_bind(), checkfirst=True)
    review_status_enum.drop(op.get_bind(), checkfirst=True)
    risk_level_enum.drop(op.get_bind(), checkfirst=True)
    retention_strategy_status_enum.drop(op.get_bind(), checkfirst=True)
    training_status_enum.drop(op.get_bind(), checkfirst=True)
    approval_status_enum.drop(op.get_bind(), checkfirst=True)
