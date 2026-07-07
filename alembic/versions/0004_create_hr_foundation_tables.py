"""create hr foundation tables

Revision ID: 0004_create_hr_foundation_tables
Revises: 0003_create_users_table
Create Date: 2026-07-07 08:04:14.503465+00:00
"""

from __future__ import annotations

from typing import Sequence, Union

import alembic.op as op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0004_create_hr_foundation_tables'
down_revision: Union[str, None] = '0003_create_users_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Explicit ENUM declarations for PostgreSQL schema management with create_type=False
candidate_status_enum = postgresql.ENUM(
    'APPLIED', 'SCREENED', 'SHORTLISTED', 'INTERVIEWING', 'OFFERED', 'HIRED', 'REJECTED',
    name='candidate_status_enum',
    create_type=False
)
employee_status_enum = postgresql.ENUM(
    'ACTIVE', 'SUSPENDED', 'TERMINATED', 'ONBOARDING',
    name='employee_status_enum',
    create_type=False
)
work_mode_enum = postgresql.ENUM(
    'REMOTE', 'HYBRID', 'OFFICE',
    name='work_mode_enum',
    create_type=False
)
experience_level_enum = postgresql.ENUM(
    'JUNIOR', 'MID', 'SENIOR', 'LEAD', 'DIRECTOR',
    name='experience_level_enum',
    create_type=False
)
employment_type_enum = postgresql.ENUM(
    'FULL_TIME', 'PART_TIME', 'CONTRACT', 'INTERNSHIP',
    name='employment_type_enum',
    create_type=False
)


def upgrade() -> None:
    # Create the ENUM types in the database explicitly first
    candidate_status_enum.create(op.get_bind(), checkfirst=True)
    employee_status_enum.create(op.get_bind(), checkfirst=True)
    work_mode_enum.create(op.get_bind(), checkfirst=True)
    experience_level_enum.create(op.get_bind(), checkfirst=True)
    employment_type_enum.create(op.get_bind(), checkfirst=True)

    # ── candidates ────────────────────────────────────────────────────────────
    op.create_table(
        'candidates',
        sa.Column('company_id', sa.UUID(), nullable=False, comment='Tenant company identifier'),
        sa.Column('first_name', sa.String(length=100), nullable=True, comment='Extracted candidate first name'),
        sa.Column('last_name', sa.String(length=100), nullable=True, comment='Extracted candidate last name'),
        sa.Column('email', sa.String(length=255), nullable=True, comment='Extracted candidate email address'),
        sa.Column('phone', sa.String(length=50), nullable=True, comment='Extracted candidate phone number'),
        sa.Column('status', candidate_status_enum, nullable=False, comment='Application status (applied, screened, shortlisted, interviewing, offered, hired, rejected)'),
        sa.Column('experience_years', sa.Numeric(precision=4, scale=1), nullable=True, comment='Parsed candidate experience in years'),
        sa.Column('education', sa.String(), nullable=True, comment='Parsed academic profile summary'),
        sa.Column('current_role', sa.String(length=150), nullable=True, comment='Parsed current job title'),
        sa.Column('skills', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='List of parsed skills (JSONB)'),
        sa.Column('match_score', sa.Numeric(precision=5, scale=2), nullable=True, comment='AI Job Description match score (0.00 - 100.00)'),
        sa.Column('scorecard_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Detailed AI assessment metrics (JSONB)'),
        sa.Column('suggested_questions', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='AI-suggested candidate interview questions (JSONB)'),
        sa.Column('interview_invitation_text', sa.String(), nullable=True, comment='AI-generated interview invitation email draft'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, comment='Soft-delete logical exclusion flag'),
        sa.Column('created_by', sa.UUID(), nullable=True, comment='User ID who created the record'),
        sa.Column('updated_by', sa.UUID(), nullable=True, comment='User ID who last updated the record'),
        sa.Column('id', sa.UUID(), nullable=False, comment='Universally unique record identifier'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Record creation timestamp (UTC)'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Record last-update timestamp (UTC)'),
        sa.CheckConstraint('match_score >= 0.0 AND match_score <= 100.0', name='chk_candidates_match_score'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_candidates_company_created_at', 'candidates', ['company_id', 'created_at'], unique=False)
    op.create_index('ix_candidates_company_email', 'candidates', ['company_id', 'email'], unique=False)
    op.create_index(op.f('ix_candidates_company_id'), 'candidates', ['company_id'], unique=False)
    op.create_index('ix_candidates_company_status', 'candidates', ['company_id', 'status'], unique=False)
    op.create_index(op.f('ix_candidates_email'), 'candidates', ['email'], unique=False)
    op.create_index(op.f('ix_candidates_status'), 'candidates', ['status'], unique=False)

    # ── job_descriptions ──────────────────────────────────────────────────────
    op.create_table(
        'job_descriptions',
        sa.Column('company_id', sa.UUID(), nullable=False, comment='Tenant company identifier'),
        sa.Column('title', sa.String(length=150), nullable=False, comment='Job title'),
        sa.Column('department', sa.String(length=100), nullable=False, comment='Department name'),
        sa.Column('experience_level', experience_level_enum, nullable=False, comment='Required experience level (junior, mid, senior, lead, director)'),
        sa.Column('location', sa.String(length=100), nullable=True, comment='Work location (e.g. city, state, or remote location)'),
        sa.Column('employment_type', employment_type_enum, nullable=True, comment='Employment commitment type (full_time, part_time, contract, internship)'),
        sa.Column('salary_range', sa.String(length=100), nullable=True, comment='AI-suggested or manual salary range details'),
        sa.Column('job_description_text', sa.String(), nullable=False, comment='Full generated markdown job description text'),
        sa.Column('required_skills', postgresql.JSONB(astext_type=sa.Text()), nullable=False, comment='List of required skills (JSONB)'),
        sa.Column('preferred_skills', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='List of preferred skills (JSONB)'),
        sa.Column('responsibilities', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Detailed list of responsibilities (JSONB)'),
        sa.Column('requirements', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Detailed list of hiring requirements (JSONB)'),
        sa.Column('benefits', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Detailed list of employment benefits (JSONB)'),
        sa.Column('ats_keywords', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Extracted ATS keywords for search optimization (JSONB)'),
        sa.Column('variants', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Generated description variants (e.g., linkedin_post, naukri_summary, internal_note) (JSONB)'),
        sa.Column('jd_hash', sa.String(length=64), nullable=False, comment='SHA-256 hash of normalized parameters for JD caching'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, comment='Soft-delete logical exclusion flag'),
        sa.Column('created_by', sa.UUID(), nullable=True, comment='User ID who created the record'),
        sa.Column('updated_by', sa.UUID(), nullable=True, comment='User ID who last updated the record'),
        sa.Column('id', sa.UUID(), nullable=False, comment='Universally unique record identifier'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Record creation timestamp (UTC)'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Record last-update timestamp (UTC)'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_job_descriptions_company_created_at', 'job_descriptions', ['company_id', 'created_at'], unique=False)
    op.create_index('ix_job_descriptions_company_department', 'job_descriptions', ['company_id', 'department'], unique=False)
    op.create_index(op.f('ix_job_descriptions_company_id'), 'job_descriptions', ['company_id'], unique=False)
    op.create_index('ix_job_descriptions_company_jd_hash', 'job_descriptions', ['company_id', 'jd_hash'], unique=False)
    op.create_index('ix_job_descriptions_company_title', 'job_descriptions', ['company_id', 'title'], unique=False)
    op.create_index(op.f('ix_job_descriptions_department'), 'job_descriptions', ['department'], unique=False)
    op.create_index(op.f('ix_job_descriptions_jd_hash'), 'job_descriptions', ['jd_hash'], unique=False)
    op.create_index(op.f('ix_job_descriptions_title'), 'job_descriptions', ['title'], unique=False)

    # ── employees ─────────────────────────────────────────────────────────────
    op.create_table(
        'employees',
        sa.Column('company_id', sa.UUID(), nullable=False, comment='Tenant company identifier'),
        sa.Column('user_id', sa.UUID(), nullable=True, comment='Linked application User account'),
        sa.Column('first_name', sa.String(length=100), nullable=False, comment='First name'),
        sa.Column('last_name', sa.String(length=100), nullable=False, comment='Last name'),
        sa.Column('email', sa.String(length=255), nullable=False, comment='Corporate email address'),
        sa.Column('phone', sa.String(length=50), nullable=True, comment='Contact phone number'),
        sa.Column('department', sa.String(length=100), nullable=False, comment='Department name'),
        sa.Column('role', sa.String(length=100), nullable=False, comment='Job title / role description'),
        sa.Column('salary', sa.Numeric(precision=12, scale=2), nullable=True, comment='Confidential salary (deferred loading)'),
        sa.Column('manager_id', sa.UUID(), nullable=True, comment='Manager employee identifier'),
        sa.Column('status', employee_status_enum, nullable=False, comment='Employment status (active, suspended, terminated, onboarding)'),
        sa.Column('role_enum', sa.String(length=50), nullable=True, comment='Role enum representation if needed'),
        sa.Column('hire_date', sa.Date(), nullable=True, comment='Date of hire'),
        sa.Column('work_mode', work_mode_enum, nullable=True, comment='Work environment mode (remote, hybrid, office)'),
        sa.Column('experience_level', experience_level_enum, nullable=True, comment='Employee seniority level'),
        sa.Column('current_skills', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='List of current skills (JSONB)'),
        sa.Column('target_role', sa.String(length=100), nullable=True, comment='Target career progression role'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, comment='Soft-delete logical exclusion flag'),
        sa.Column('created_by', sa.UUID(), nullable=True, comment='User ID who created the record'),
        sa.Column('updated_by', sa.UUID(), nullable=True, comment='User ID who last updated the record'),
        sa.Column('id', sa.UUID(), nullable=False, comment='Universally unique record identifier'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Record creation timestamp (UTC)'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Record last-update timestamp (UTC)'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['manager_id'], ['employees.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email', 'company_id', name='uq_employees_email_company')
    )
    op.create_index('ix_employees_company_created_at', 'employees', ['company_id', 'created_at'], unique=False)
    op.create_index('ix_employees_company_department', 'employees', ['company_id', 'department'], unique=False)
    op.create_index(op.f('ix_employees_company_id'), 'employees', ['company_id'], unique=False)
    op.create_index('ix_employees_company_role', 'employees', ['company_id', 'role'], unique=False)
    op.create_index('ix_employees_company_status', 'employees', ['company_id', 'status'], unique=False)
    op.create_index(op.f('ix_employees_department'), 'employees', ['department'], unique=False)
    op.create_index(op.f('ix_employees_email'), 'employees', ['email'], unique=False)
    op.create_index(op.f('ix_employees_manager_id'), 'employees', ['manager_id'], unique=False)
    op.create_index(op.f('ix_employees_role'), 'employees', ['role'], unique=False)
    op.create_index(op.f('ix_employees_status'), 'employees', ['status'], unique=False)
    op.create_index(op.f('ix_employees_user_id'), 'employees', ['user_id'], unique=True)

    # ── resumes ───────────────────────────────────────────────────────────────
    op.create_table(
        'resumes',
        sa.Column('company_id', sa.UUID(), nullable=False, comment='Tenant company identifier'),
        sa.Column('candidate_id', sa.UUID(), nullable=False, comment='Associated candidate profile identifier'),
        sa.Column('file_name', sa.String(length=255), nullable=False, comment='Original uploaded file name'),
        sa.Column('file_path', sa.String(length=500), nullable=True, comment='Temporary file storage path reference (if retained)'),
        sa.Column('file_size', sa.Integer(), nullable=False, comment='File size in bytes'),
        sa.Column('mime_type', sa.String(length=100), nullable=False, comment='MIME type check value (PDF or DOCX)'),
        sa.Column('raw_text', sa.String(), nullable=False, comment='Extracted raw text parsed from document content'),
        sa.Column('resume_hash', sa.String(length=64), nullable=False, comment='SHA-256 hash of extracted text for screening cache checks'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, comment='Soft-delete logical exclusion flag'),
        sa.Column('created_by', sa.UUID(), nullable=True, comment='User ID who created the record'),
        sa.Column('updated_by', sa.UUID(), nullable=True, comment='User ID who last updated the record'),
        sa.Column('id', sa.UUID(), nullable=False, comment='Universally unique record identifier'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Record creation timestamp (UTC)'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Record last-update timestamp (UTC)'),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('candidate_id', name='uq_resumes_candidate')
    )
    op.create_index(op.f('ix_resumes_candidate_id'), 'resumes', ['candidate_id'], unique=False)
    op.create_index('ix_resumes_company_candidate', 'resumes', ['company_id', 'candidate_id'], unique=True)
    op.create_index('ix_resumes_company_hash', 'resumes', ['company_id', 'resume_hash'], unique=False)
    op.create_index(op.f('ix_resumes_company_id'), 'resumes', ['company_id'], unique=False)
    op.create_index(op.f('ix_resumes_resume_hash'), 'resumes', ['resume_hash'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse dependency order
    op.drop_index('ix_resumes_resume_hash', table_name='resumes')
    op.drop_index('ix_resumes_company_id', table_name='resumes')
    op.drop_index('ix_resumes_company_hash', table_name='resumes')
    op.drop_index('ix_resumes_company_candidate', table_name='resumes')
    op.drop_index('ix_resumes_candidate_id', table_name='resumes')
    op.drop_table('resumes')

    op.drop_index('ix_employees_user_id', table_name='employees')
    op.drop_index('ix_employees_status', table_name='employees')
    op.drop_index('ix_employees_role', table_name='employees')
    op.drop_index('ix_employees_manager_id', table_name='employees')
    op.drop_index('ix_employees_email', table_name='employees')
    op.drop_index('ix_employees_department', table_name='employees')
    op.drop_index('ix_employees_company_status', table_name='employees')
    op.drop_index('ix_employees_company_role', table_name='employees')
    op.drop_index('ix_employees_company_id', table_name='employees')
    op.drop_index('ix_employees_company_department', table_name='employees')
    op.drop_index('ix_employees_company_created_at', table_name='employees')
    op.drop_table('employees')

    op.drop_index('ix_job_descriptions_title', table_name='job_descriptions')
    op.drop_index('ix_job_descriptions_jd_hash', table_name='job_descriptions')
    op.drop_index('ix_job_descriptions_department', table_name='job_descriptions')
    op.drop_index('ix_job_descriptions_company_title', table_name='job_descriptions')
    op.drop_index('ix_job_descriptions_company_jd_hash', table_name='job_descriptions')
    op.drop_index('ix_job_descriptions_company_id', table_name='job_descriptions')
    op.drop_index('ix_job_descriptions_company_department', table_name='job_descriptions')
    op.drop_index('ix_job_descriptions_company_created_at', table_name='job_descriptions')
    op.drop_table('job_descriptions')

    op.drop_index('ix_candidates_status', table_name='candidates')
    op.drop_index('ix_candidates_email', table_name='candidates')
    op.drop_index('ix_candidates_company_status', table_name='candidates')
    op.drop_index('ix_candidates_company_id', table_name='candidates')
    op.drop_index('ix_candidates_company_email', table_name='candidates')
    op.drop_index('ix_candidates_company_created_at', table_name='candidates')
    op.drop_table('candidates')

    # Drop custom Enums from Postgres
    candidate_status_enum.drop(op.get_bind(), checkfirst=True)
    employee_status_enum.drop(op.get_bind(), checkfirst=True)
    work_mode_enum.drop(op.get_bind(), checkfirst=True)
    experience_level_enum.drop(op.get_bind(), checkfirst=True)
    employment_type_enum.drop(op.get_bind(), checkfirst=True)
