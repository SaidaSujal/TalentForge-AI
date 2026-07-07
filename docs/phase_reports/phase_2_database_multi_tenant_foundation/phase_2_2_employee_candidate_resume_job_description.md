# Phase 2.2 Employee, Candidate, Resume, Job Description — Subphase Report

**Status:** ✅ COMPLETED

---

## 1. Subphase Objectives
The goal of Subphase 2.2 was to establish the database models and migrations for the core HR assets of the TalentForge AI application, ensuring strong multi-tenant isolation, data integrity, and strict separation of concerns.

Key requirements included:
- **Refactoring Foundation Models**: Moving existing models (`Company`, `User`, `AppSettings`) from a monolithic file (`models_foundation.py`) into a modular package structure under `app/db/models/`.
- **Implementing Core HR Models**:
  - **Employee**: Supports active/onboarding staff, self-referential managers, and sensitive salary deferred loading.
  - **Candidate**: Manages applicant metadata, JSONB skills, check constraints, and AI scorecards.
  - **Resume**: Holds uploaded file metadata and raw extracted text. Linked 1-to-1 with a candidate.
  - **Job Description**: Manages generated JDs, skills, and social media/post variants.
- **Alembic Migration**: Generating migration `0004_create_hr_foundation_tables.py` and verifying its full rollback and upgrade lifecycle.
- **Validation**: Creating a robust pytest suite verifying relationships, constraints, enums, soft delete, and query behavior.

---

## 2. Technical Implementation Details

### A. Modular Package Architecture (`app/db/models/`)
The database models have been modularized under `app/db/models/` for scalability:
- `__init__.py`: Exports all models to maintain Alembic autodiscovery.
- `company.py`: `Company` model and its relationships to employees, candidates, resumes, and job descriptions.
- `user.py`: `User` model, linking 1-to-1 with `Employee`.
- `app_settings.py`: `AppSettings` model.
- `employee.py`: `Employee` model, statuses (`EmployeeStatus`), work modes (`WorkMode`), and seniority (`ExperienceLevel`).
- `candidate.py`: `Candidate` model, statuses (`CandidateStatus`), and AI assessment scores.
- `resume.py`: `Resume` model, hash storage, and text contents.
- `job_description.py`: `JobDescription` model and employment commitment types (`EmploymentType`).

### B. High-Scale Indexing & Multi-Tenant Isolation
To ensure high-performance tenant isolation (capable of scaling to millions of resumes and hundreds of thousands of employees), all queries are designed to filter by `company_id`. To support this, **composite indexes** have been implemented on the database tables:
- `employees`:
  - `ix_employees_company_status` on `(company_id, status)`
  - `ix_employees_company_department` on `(company_id, department)`
  - `ix_employees_company_role` on `(company_id, role)`
  - `ix_employees_company_created_at` on `(company_id, created_at)`
- `candidates`:
  - `ix_candidates_company_status` on `(company_id, status)`
  - `ix_candidates_company_email` on `(company_id, email)`
  - `ix_candidates_company_created_at` on `(company_id, created_at)`
- `resumes`:
  - `ix_resumes_company_candidate` on `(company_id, candidate_id)` (Unique)
  - `ix_resumes_company_hash` on `(company_id, resume_hash)`
- `job_descriptions`:
  - `ix_job_descriptions_company_title` on `(company_id, title)`
  - `ix_job_descriptions_company_department` on `(company_id, department)`
  - `ix_job_descriptions_company_jd_hash` on `(company_id, jd_hash)`
  - `ix_job_descriptions_company_created_at` on `(company_id, created_at)`

### C. Advanced Features & Security
1. **Deferred Salary Loading**: The sensitive employee `salary` field uses `deferred` loading:
   ```python
   salary: Mapped[Optional[Decimal]] = deferred(mapped_column(Numeric(12, 2)))
   ```
   This prevents accidental exposure of salary data in general queries.
2. **Audit Compatibility**: Tables include `created_by` and `updated_by` UUID fields (optional for V1) to track who created/modified each record.
3. **Soft-Delete Lifecycle**: Logical delete is implemented via the `is_deleted` boolean column on all entities, ensuring records can be marked inactive without breaking database referential integrity.
4. **Candidate Score Range Check Constraint**: Enforces that candidate `match_score` lies within `0.00` and `100.00`:
   ```python
   CheckConstraint("match_score >= 0.0 AND match_score <= 100.0", name="chk_candidates_match_score")
   ```

---

## 3. Database Migration Lifecycle Validation
The Alembic migration script was generated at `alembic/versions/0004_create_hr_foundation_tables.py`.

The migration lifecycle has been successfully verified:
1. **Upgrade**: `alembic upgrade head` correctly creates tables, columns, indexes, check constraints, and custom Postgres ENUM types.
2. **Downgrade**: `alembic downgrade 0003_create_users_table` rolls back all changes, dropping the tables, indexes, and custom types cleanly.
3. **Upgrade (Re-apply)**: Successfully re-applies migrations to restore schema state.

---

## 4. Verification and Test Results
A robust suite of unit and integration tests was added in `tests/test_phase2_2_hr_models.py`.

The tests cover:
- **Model Creation Success**: Verifies that Employee, Candidate, Resume, and JobDescription can be written and read with appropriate types and default enums.
- **Self-referential Manager Hierarchy**: Verifies manager-subordinate connections and bidirectional lists.
- **One-to-One Relationships**: Tests User-Employee and Candidate-Resume mappings.
- **Candidate Match Score Limits**: Asserts that `IntegrityError` is raised if `match_score` is set above `100` or below `0`.
- **Tenant-Scoped Unique Constraints**: Verifies that duplicate employee emails are allowed *across different companies*, but rejected *within the same company*.
- **Deferred Loading**: Asserts that employee `salary` is in the unloaded state when the object is queried, and lazy-loads successfully on demand.
- **Soft Delete and Tenant Isolation Queries**: Verifies logical delete flags and `company_id` filter separation.
- **Programmatic Migration Verification**: Executes downgrade and upgrade commands programmatically to validate safety.

### Test Output Summary
All 46 test cases passed successfully in `3.23s`.
```bash
tests/test_phase2_2_hr_models.py::TestHRModels::test_create_employee_success PASSED
tests/test_phase2_2_hr_models.py::TestHRModels::test_employee_manager_hierarchy PASSED
tests/test_phase2_2_hr_models.py::TestHRModels::test_employee_user_relationship PASSED
tests/test_phase2_2_hr_models.py::TestHRModels::test_employee_email_uniqueness_per_tenant PASSED
tests/test_phase2_2_hr_models.py::TestHRModels::test_candidate_resume_one_to_one PASSED
tests/test_phase2_2_hr_models.py::TestHRModels::test_candidate_match_score_check_constraint PASSED
tests/test_phase2_2_hr_models.py::TestHRModels::test_job_description_jsonb_and_enums PASSED
tests/test_phase2_2_hr_models.py::TestHRModels::test_employee_salary_deferred_loading PASSED
tests/test_phase2_2_hr_models.py::TestHRModels::test_employee_soft_delete_lifecycle PASSED
tests/test_phase2_2_hr_models.py::TestHRModels::test_tenant_isolation_employees PASSED
tests/test_phase2_2_hr_models.py::test_migration_lifecycle PASSED
======================== 46 passed, 1 warning in 3.23s =========================
```
