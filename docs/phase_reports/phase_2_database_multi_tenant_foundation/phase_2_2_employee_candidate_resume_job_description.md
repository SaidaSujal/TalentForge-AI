# Project
TalentForge AI

# Phase
2 — Database & Multi-Tenant Foundation

# Subphase
2.2 — Employee, Candidate, Resume, Job Description

# Status
✅ COMPLETED

# Date
2026-07-07

# Objective
Implement the modular package architecture for DB models and establish database models/migrations for the core HR assets (Employee, Candidate, Resume, JobDescription).

# Overview
This subphase refactors foundation models into individual modules and introduces the core HR entities with proper relationships, check constraints, composite indexes, and deferred loading mechanisms.

# Architecture Decisions
- Package-based model organization under `app/db/models/` for code hygiene.
- Sensitive employee `salary` uses deferred loading to avoid accidental exposures in basic queries.
- Candidates `match_score` enforcements using database-level `CheckConstraint` between 0.00 and 100.00.
- Unique email constraint on `Employee` is tenant-scoped (`company_id, email`).
- Candidates to Resumes are linked in a strict 1-to-1 relationship.
- Composite indexes are defined on all query pathways filtering on `company_id`.

# Files Created
### `app/db/models/employee.py`
- **path:** [employee.py](file:///Users/sujal/TalentForge%20AI/app/db/models/employee.py)
- **purpose:** Defines Employee model, enums (EmployeeStatus, WorkMode, ExperienceLevel), and self-referential supervisor relations.
- **classes:** `Employee`, `EmployeeStatus`, `WorkMode`, `ExperienceLevel`
- **methods:** None

### `app/db/models/candidate.py`
- **path:** [candidate.py](file:///Users/sujal/TalentForge%20AI/app/db/models/candidate.py)
- **purpose:** Defines Candidate model, status enum (CandidateStatus), and score check constraints.
- **classes:** `Candidate`, `CandidateStatus`
- **methods:** None

### `app/db/models/resume.py`
- **path:** [resume.py](file:///Users/sujal/TalentForge%20AI/app/db/models/resume.py)
- **purpose:** Defines Resume metadata model and text contents.
- **classes:** `Resume`
- **methods:** None

### `app/db/models/job_description.py`
- **path:** [job_description.py](file:///Users/sujal/TalentForge%20AI/app/db/models/job_description.py)
- **purpose:** Defines JobDescription model, employment type enum (EmploymentType), and social post variants.
- **classes:** `JobDescription`, `EmploymentType`
- **methods:** None

### `tests/test_phase2_2_hr_models.py`
- **path:** [test_phase2_2_hr_models.py](file:///Users/sujal/TalentForge%20AI/tests/test_phase2_2_hr_models.py)
- **purpose:** Verifies constraints, relationships, enums, soft delete, and query behavior for HR models.
- **classes:** `TestHRModels`
- **methods:** `test_create_employee_success`, `test_employee_manager_hierarchy`, `test_employee_user_relationship`, `test_employee_email_uniqueness_per_tenant`, `test_candidate_resume_one_to_one`, `test_candidate_match_score_check_constraint`, `test_job_description_jsonb_and_enums`, `test_employee_salary_deferred_loading`, `test_employee_soft_delete_lifecycle`, `test_tenant_isolation_employees`, `test_migration_lifecycle`

### `alembic/versions/0004_create_hr_foundation_tables.py`
- **path:** [0004_create_hr_foundation_tables.py](file:///Users/sujal/TalentForge%20AI/alembic/versions/0004_create_hr_foundation_tables.py)
- **purpose:** Database schema migration script for Employee, Candidate, Resume, and JD tables.
- **classes:** None
- **methods:** `upgrade`, `downgrade`

# Files Modified
### `app/db/models/company.py`
- **path:** [company.py](file:///Users/sujal/TalentForge%20AI/app/db/models/company.py)
- **exact changes:** Moved from monolithic models file. Added relationships mapping to Employee, Candidate, Resume, and JobDescription models.
- **why changes were required:** Modularize company definition and hook bidirectional relationship collections.

### `app/db/models/user.py`
- **path:** [user.py](file:///Users/sujal/TalentForge%20AI/app/db/models/user.py)
- **exact changes:** Moved from monolithic models file. Added relationship to Employee.
- **why changes were required:** Modularize user definition.

### `app/db/models/__init__.py`
- **path:** [__init__.py](file:///Users/sujal/TalentForge%20AI/app/db/models/__init__.py)
- **exact changes:** Created package imports to export all models.
- **why changes were required:** Maintain Alembic declarative meta autodiscovery.

# Database Changes
- Tables created: `employees`, `candidates`, `resumes`, `job_descriptions`
- Custom Postgres ENUM types: `employee_status_enum`, `work_mode_enum`, `experience_level_enum`, `candidate_status_enum`, `employment_type_enum`
- Check constraint: `chk_candidates_match_score` (`match_score >= 0.0 AND match_score <= 100.0`)
- Unique indices on tenant isolation scopes.

# Repository Changes
None.

# Seeder Changes
None.

# Testing
- new tests: 11 tests in `test_phase2_2_hr_models.py`
- previous tests: 7 tests (Phase 1 + Phase 2.1)
- total tests: 18 tests (cumulative)
- validation commands:
  ```bash
  PYTHONPATH=. .venv/bin/pytest tests/test_phase2_2_hr_models.py -v
  ```

# Validation Results
All tests passed:
- `TestHRModels.test_create_employee_success` PASSED
- `TestHRModels.test_employee_manager_hierarchy` PASSED
- `TestHRModels.test_employee_user_relationship` PASSED
- `TestHRModels.test_employee_email_uniqueness_per_tenant` PASSED
- `TestHRModels.test_candidate_resume_one_to_one` PASSED
- `TestHRModels.test_candidate_match_score_check_constraint` PASSED
- `TestHRModels.test_job_description_jsonb_and_enums` PASSED
- `TestHRModels.test_employee_salary_deferred_loading` PASSED
- `TestHRModels.test_employee_soft_delete_lifecycle` PASSED
- `TestHRModels.test_tenant_isolation_employees` PASSED
- `test_migration_lifecycle` PASSED

# Security Validation
- Verified that sensitive salary column uses `deferred` loading.
- Soft-delete flag validates record preservation without physical row deletion.

# Tenant Isolation Validation
- Composite indexes verified to partition employees, candidates, and job descriptions safely on `company_id`.
- Verified that employee email uniqueness is scoped per tenant.

# Performance Notes
- Composite indexes established on `(company_id, status)`, `(company_id, department)`, and `(company_id, role)` to speed up tenant-scoped queries.

# Remaining Limitations
- None.

# Deliverables
- Modular files for Employee, Candidate, Resume, and JobDescription models.
- Database migration script `0004_create_hr_foundation_tables.py`
- Unit tests in `test_phase2_2_hr_models.py`
