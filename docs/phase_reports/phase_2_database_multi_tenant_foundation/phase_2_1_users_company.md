# Project
TalentForge AI

# Phase
2 — Database & Multi-Tenant Foundation

# Subphase
2.1 — Users & Company

# Status
✅ COMPLETED

# Date
2026-07-06

# Objective
Define and implement the foundational structures for user identity and tenant grouping (`Company`) in a multi-tenant database. Generate migrations and build unit test coverage.

# Overview
Subphase 2.1 establishes the core identity entities. It ensures every user is bound to a tenant (`Company`) via a foreign key constraint and implements secure bcrypt password hashing for user credentials.

# Architecture Decisions
- Use UUID primary keys for all database tables (implemented via `UUIDPrimaryKeyMixin`).
- Use database-level Cascade Delete (`ondelete="CASCADE"`) on `users.company_id` to ensure no orphaned users remain.
- Enforce unique index on `users.email` to prevent duplicate emails.
- Encrypt passwords using `passlib.context.PromptContext` / `crypt_context` configured with the `bcrypt` scheme.

# Files Created
### `tests/test_phase2_1_users.py`
- **path:** [test_phase2_1_users.py](file:///Users/sujal/TalentForge%20AI/tests/test_phase2_1_users.py)
- **purpose:** Verifies constraints, relationships, unique keys, and hashing of the User model.
- **classes:** `TestUserModel`
- **methods:** `test_create_user_success`, `test_user_company_relationship`, `test_user_email_uniqueness`, `test_user_company_fk_requirement`, `test_user_password_hashing`

### `alembic/versions/0003_create_users_table.py`
- **path:** [0003_create_users_table.py](file:///Users/sujal/TalentForge%20AI/alembic/versions/0003_create_users_table.py)
- **purpose:** Database schema migration script for the `users` table.
- **classes:** None
- **methods:** `upgrade`, `downgrade`

# Files Modified
### `app/db/models_foundation.py`
- **path:** [models_foundation.py](file:///Users/sujal/TalentForge%20AI/app/db/models_foundation.py)
- **exact changes:** Added `User` SQLAlchemy model with columns `id`, `email`, `password_hash`, `role`, `company_id`, `is_active`, `created_at`, `updated_at`. Defined `Company.users` bidirectional relationship with cascade.
- **why changes were required:** Core tenant and user relationship modeling.

### `app/db/models.py`
- **path:** [models.py](file:///Users/sujal/TalentForge%20AI/app/db/models.py)
- **exact changes:** Imported `User` model to register it for Alembic discovery.
- **why changes were required:** Enable auto-discovery of SQLAlchemy models by Alembic.

# Database Changes
- Table created: `users`
- Index created: `ix_users_email` (unique index on `email`)
- Index created: `ix_users_company_id` (index on `company_id`)
- Foreign Key: `users.company_id` -> `companies.id` (`ondelete="CASCADE"`)

# Repository Changes
None (Repository layer is built in Subphase 2.6).

# Seeder Changes
None (Seeding system is built in Subphase 2.7).

# Testing
- new tests: 5 tests in `test_phase2_1_users.py`
- previous tests: 2 tests (Phase 1)
- total tests: 7 tests (cumulative)
- validation commands:
  ```bash
  PYTHONPATH=. .venv/bin/pytest tests/test_phase2_1_users.py -v
  ```

# Validation Results
All tests passed:
- `TestUserModel.test_create_user_success` PASSED
- `TestUserModel.test_user_company_relationship` PASSED
- `TestUserModel.test_user_email_uniqueness` PASSED
- `TestUserModel.test_user_company_fk_requirement` PASSED
- `TestUserModel.test_user_password_hashing` PASSED

# Security Validation
- Verified that plaintext passwords are never written or logged.
- Verified password matching using `verify_password`.

# Tenant Isolation Validation
- Verified that a user cannot be created without a valid `company_id`.
- Verified Cascade Delete: deleting a company deletes all users belonging to that company.

# Performance Notes
- Database index added on `users.email` for high-performance authentication lookups.
- Database index added on `users.company_id` to optimize tenant-scoped queries.

# Remaining Limitations
- End-user endpoints (register, login) are deferred to later phases; currently, V1 relies on standard mock headers via `DemoUser` middleware.

# Deliverables
- Database migration script `0003_create_users_table.py`
- User model declaration in `models_foundation.py`
- Model unit tests in `test_phase2_1_users.py`
