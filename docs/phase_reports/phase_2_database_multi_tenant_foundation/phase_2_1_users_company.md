# Phase 2.1 Users & Company — Subphase Report

**Project:** TalentForge AI  
**Phase:** 2 — Database & Multi-Tenant Foundation  
**Subphase:** 2.1 — Users & Company  
**Status:** ✅ COMPLETED  
**Date:** 2026-07-06  
**Validated By:** Antigravity

---

## Overview
Phase 2.1 implements the foundational structure for user identities within TalentForge AI's multi-tenant architecture. It establishes the `User` model, registers it for Alembic discovery, builds the corresponding database migrations, and adds unit testing coverage for constraints and model functionality.

---

## Goal
The goal of this subphase was to:
1. Define a persistent `User` database model mapping to the `users` table.
2. Link every user to a parent tenant (`Company`) via a foreign key (`company_id`).
3. Set up appropriate database indices, uniqueness constraints (e.g., email), and cascading deletion behavior.
4. Support bcrypt password hashing for secure authentication storage.
5. Create and run the Alembic database migration to generate the `users` table.
6. Verify and test the model's integrity constraints, relationships, and password helpers.

---

## Files Created
- **[Alembic Migration]** [0003_create_users_table.py](file:///Users/sujal/TalentForge%20AI/alembic/versions/0003_create_users_table.py): Alembic schema migration script that defines the `users` table layout, columns, unique email index, foreign key pointing to `companies.id`, and creation/modification timestamps.
- **[Unit Tests]** [test_phase2_1_users.py](file:///Users/sujal/TalentForge%20AI/tests/test_phase2_1_users.py): Contains 5 test cases focusing on User creation, uniqueness constraints, bidirectional relationships with the Company model, foreign key requirements, and password hashing utility verification.

---

## Files Modified
- **[Database Model Definition]** [models_foundation.py](file:///Users/sujal/TalentForge%20AI/app/db/models_foundation.py): Added the `User` SQLAlchemy class mapping to the `users` table, defining columns like `email`, `password_hash`, `role`, `company_id`, and `is_active`. Also added a bidirectional relationship on the `Company` model linking to `users` (using cascade delete).
- **[Alembic Registry]** [models.py](file:///Users/sujal/TalentForge%20AI/app/db/models.py): Imported `User` from `models_foundation.py` to ensure it is registered on the declarative metadata for Alembic discovery.

---

## Database Changes
- **New Table:** `users`
- **Columns:**
  - `id` (UUID): Primary Key, default `gen_random_uuid()`
  - `email` (String(255)): Unique, Indexed, Not Null — stores the user's primary login identifier.
  - `password_hash` (String(255)): Not Null — stores the bcrypt-hashed representation of the user's password.
  - `role` (String(50)): Not Null, default `'employee'` — stores user permissions (e.g., `admin`, `hr_manager`, `recruiter`, `employee`, `manager`).
  - `company_id` (UUID): Foreign Key linking to `companies.id`, `ondelete="CASCADE"`, Indexed, Not Null.
  - `is_active` (Boolean): Not Null, default `true` — supports soft deletion and temporary accounts lockouts.
  - `created_at` (DateTime): Timezone-aware timestamp of creation (default `now()`), Not Null.
  - `updated_at` (DateTime): Timezone-aware timestamp of last update (default `now()`), Not Null.
- **Constraints & Indexes:**
  - Unique Constraint: `uq_users_email` on `email`.
  - Database Index: `ix_users_email` on `email` for fast login lookup.
  - Database Index: `ix_users_company_id` on `company_id` to speed up tenant-isolated querying.
  - Foreign Key Constraint: `users.company_id` -> `companies.id` with cascade deletion to prevent orphaned user records.

---

## Model Explanation
The `User` model integrates with the foundation database architecture:
- Inherits from `Base`, `UUIDPrimaryKeyMixin`, and `TimestampMixin` to satisfy the requirements for UUID keys and automatic timestamp injection.
- Defines database-level comments on all columns to maintain documentation readability.
- Establishes a bidirectional SQLAlchemy relationship:
  - `User.company` relationship resolves the parent `Company` instance.
  - `Company.users` relationship resolves the child list of users belonging to the company, defined with `cascade="all, delete-orphan"`.

---

## Alembic Migration
The migration script is numbered `0003_create_users_table.py`. 
- **`upgrade()`**: Implements table generation via `op.create_table()` with precise data types and PostgreSQL comments. It then creates the unique constraint `uq_users_email` and indexes `ix_users_email` and `ix_users_company_id`.
- **`downgrade()`**: Drops the `users` table via `op.drop_table("users")` during rollback.

---

## Security Changes
- The password hashing implementation uses **passlib**'s `CryptContext` configured with the **bcrypt** hashing algorithm.
- Added test coverage ensuring that plaintext passwords are never stored directly in the database (`password_hash != raw_password`) and that validation works bidirectionally (matching hashes return `True`, mismatched hashes return `False`).

---

## Tenant Isolation
- Every user is bound to a `Company` by the `company_id` attribute.
- The `company_id` field has database-level `NOT NULL` and `FOREIGN KEY` constraints.
- Validated via unit testing: attempts to insert a user without a valid, existing `company_id` will trigger a database `IntegrityError`.

---

## Tests Executed
The test suite in `tests/test_phase2_1_users.py` was executed. It includes the following test classes/functions:
- `test_create_user_success`: Verifies correct instantiation and retrieval of user records with expected values.
- `test_user_company_relationship`: Validates bidirectional SQLAlchemy relationships and eager relationship loading.
- `test_user_email_uniqueness`: Confirms that two users with the same email cannot exist, throwing an `IntegrityError`.
- `test_user_company_fk_requirement`: Confirms that creating a user with a non-existent `company_id` fails with an `IntegrityError`.
- `test_user_password_hashing`: Tests password hashing logic, verification correctness, and prevents plain-text leakage.

---

## Commands Executed
```bash
# Generate the migration script
alembic revision --autogenerate -m "create users table"

# Apply migrations up to head
alembic upgrade head

# Run tests
.venv/bin/pytest tests/test_phase2_1_users.py
```

---

## Validation Results
All 5 tests run and pass successfully:
```text
tests/test_phase2_1_users.py::TestUserModel::test_create_user_success PASSED
tests/test_phase2_1_users.py::TestUserModel::test_user_company_relationship PASSED
tests/test_phase2_1_users.py::TestUserModel::test_user_email_uniqueness PASSED
tests/test_phase2_1_users.py::TestUserModel::test_user_company_fk_requirement PASSED
tests/test_phase2_1_users.py::TestUserModel::test_user_password_hashing PASSED
```

---

## Bugs Found
- None.

---

## Bugs Fixed
- N/A.

---

## Architecture Compliance
- **UUID requirement**: Met. The `users.id` and `users.company_id` columns both utilize the UUID data type.
- **Tenant Isolation**: Met. `company_id` is required, indexed, and verified via foreign key.
- **Zero hardcoded secrets**: Met. All configurations are handled via settings; password hashing salts are handled automatically by bcrypt.
- **Timestamps**: Met. Uses `TimestampMixin` to automatically track UTC `created_at` and `updated_at` timestamps.

---

## Known Limitations
- End-user authentication (endpoints for registration, login, JWT token emission) is postponed until Phase 10 (per planning decisions). For V1, the `DemoUser` middleware continues to serve mock requests, but the database schema itself is ready to support full RBAC.

---

## Ready for Phase 2.2
Yes. With the foundation of `Company` and `User` schemas complete, the database structure is ready for the core HR resources: Employees, Candidates, Resumes, and Job Descriptions.
