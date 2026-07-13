# Project
TalentForge AI

# Phase
2 — Database & Multi-Tenant Foundation

# Subphase
2.6 — Repository Layer

# Status
✅ COMPLETED

# Date
2026-07-11

# Objective
Build a robust, generic, and tenant-scoped data access boundary that enforces multi-tenancy at the query builder layer, restricts mass-assignment parameters, and handles driver exceptions cleanly.

# Overview
This subphase introduces base and entity-specific repositories (User, Employee, Candidate, AuditLog, AICache, AIHistory, ExportJob). They enforce `company_id` constraints on all operations, protect write-once records, and execute concurrent cache upserts.

# Architecture Decisions
- Implement `BaseRepository` with common asynchronous database CRUD operations.
- Implement `TenantRepository` extending `BaseRepository` that forces the authoritative tenant ID onto all queries and updates.
- Block client-provided `company_id` overrides on write/update calls to prevent cross-tenant privilege escalation.
- Catch database exceptions and translate database integrity violations (FK, duplicate, constraint failures) into generic domain-specific exceptions.
- Restrict list paging sizes to a maximum of 100 rows per request.
- Order all list operations deterministically by `id` or creation timestamp to ensure repeatable cursor-based paging.
- Mark `AuditLog` and `AIHistory` repositories as read-only/append-only (`WriteProtectedError` on update/delete).

# Files Created
### `app/db/repositories/base.py`
- **path:** [base.py](file:///Users/sujal/TalentForge%20AI/app/db/repositories/base.py)
- **purpose:** Abstract BaseRepository, TenantRepository, and SQLSTATE exception translates.
- **classes:** `BaseRepository`, `TenantRepository`
- **methods:** `get`, `list`, `create`, `update`, `delete`, `exists`, `count`, `handle_db_errors`

### `app/db/repositories/user.py`
- **path:** [user.py](file:///Users/sujal/TalentForge%20AI/app/db/repositories/user.py)
- **purpose:** UserRepository with active-user filtering and blocked physical deletes.
- **classes:** `UserRepository`
- **methods:** `get`, `list`, `delete`

### `app/db/repositories/employee.py`
- **path:** [employee.py](file:///Users/sujal/TalentForge%20AI/app/db/repositories/employee.py)
- **purpose:** EmployeeRepository supporting reports hierarchies and logical soft-deletes.
- **classes:** `EmployeeRepository`
- **methods:** `get_reports`, `delete`

### `app/db/repositories/candidate.py`
- **path:** [candidate.py](file:///Users/sujal/TalentForge%20AI/app/db/repositories/candidate.py)
- **purpose:** CandidateRepository with eager loading of Resumes.
- **classes:** `CandidateRepository`
- **methods:** `get_with_resume`

### `app/db/repositories/audit.py`
- **path:** [audit.py](file:///Users/sujal/TalentForge%20AI/app/db/repositories/audit.py)
- **purpose:** AuditRepository preventing log alterations.
- **classes:** `AuditRepository`
- **methods:** `update`, `delete`

### `app/db/repositories/ai_cache.py`
- **path:** [ai_cache.py](file:///Users/sujal/TalentForge%20AI/app/db/repositories/ai_cache.py)
- **purpose:** AICacheRepository handling native `ON CONFLICT DO UPDATE` upserts and TTL cleaning.
- **classes:** `AICacheRepository`
- **methods:** `upsert`, `clean_expired`

### `app/db/repositories/ai_history.py`
- **path:** [ai_history.py](file:///Users/sujal/TalentForge%20AI/app/db/repositories/ai_history.py)
- **purpose:** AIHistoryRepository with append-only protections.
- **classes:** `AIHistoryRepository`
- **methods:** `update`, `delete`

### `app/db/repositories/export_job.py`
- **path:** [export_job.py](file:///Users/sujal/TalentForge%20AI/app/db/repositories/export_job.py)
- **purpose:** ExportJobRepository tracking files and incrementing download counts.
- **classes:** `ExportJobRepository`
- **methods:** `increment_download_count`

### `tests/test_phase2_6_repository_layer.py`
- **path:** [test_phase2_6_repository_layer.py](file:///Users/sujal/TalentForge%20AI/tests/test_phase2_6_repository_layer.py)
- **purpose:** Comprehensive test suite covering tenant isolation, concurrent upserts, mass assignments, and SQLSTATE mappings.
- **classes:** `TestRepositoryLayer`
- **methods:** `test_tenant_read_isolation`, `test_tenant_update_isolation`, `test_tenant_delete_isolation`, `test_tenant_list_and_count_isolation`, `test_protected_fields_mass_assignment_protection`, `test_unknown_fields_rejected`, `test_strict_query_parameters`, `test_deterministic_ordering`, `test_explicit_soft_delete_lifecycle`, `test_user_active_filtering_consistency`, `test_append_only_protections`, `test_cache_expiry_and_metadata_refresh`, `test_concurrent_same_tenant_cache_upsert`, `test_atomic_download_count_increment`, `test_sqlstate_exception_translation`, `test_cache_service_zero_external_api_calls`

# Files Modified
### `app/db/repositories/__init__.py`
- **path:** [__init__.py](file:///Users/sujal/TalentForge%20AI/app/db/repositories/__init__.py)
- **exact changes:** Imported and exported all repository classes.
- **why changes were required:** Central entry point for repositories.

### `app/core/errors.py`
- **path:** [errors.py](file:///Users/sujal/TalentForge%20AI/app/core/errors.py)
- **exact changes:** Added `RecordAlreadyExistsError`, `ForeignKeyViolationError`, `DatabaseConstraintError`, `WriteProtectedError`, `ConcurrencyError`.
- **why changes were required:** Custom domain exceptions mapping to SQLSTATE database violations.

### `app/services/ai/cache.py`
- **path:** [cache.py](file:///Users/sujal/TalentForge%20AI/app/services/ai/cache.py)
- **exact changes:** Modified caching routines to use the new `AICacheRepository`.
- **why changes were required:** Integration with repository layer.

# Database Changes
None.

# Repository Changes
Built all User, Employee, Candidate, AuditLog, AICache, AIHistory, and ExportJob repository boundaries.

# Seeder Changes
None.

# Testing
- new tests: 16 tests in `test_phase2_6_repository_layer.py`
- previous tests: 46 tests (Phase 1 + Phase 2.1 + Phase 2.2 + Phase 2.3 + Phase 2.4 + Phase 2.5)
- total tests: 62 tests (cumulative)
- validation commands:
  ```bash
  PYTHONPATH=. .venv/bin/pytest tests/test_phase2_6_repository_layer.py -v
  ```

# Validation Results
All tests passed:
- `TestRepositoryLayer.test_tenant_read_isolation` PASSED
- `TestRepositoryLayer.test_tenant_update_isolation` PASSED
- `TestRepositoryLayer.test_tenant_delete_isolation` PASSED
- `TestRepositoryLayer.test_tenant_list_and_count_isolation` PASSED
- `TestRepositoryLayer.test_protected_fields_mass_assignment_protection` PASSED
- `TestRepositoryLayer.test_unknown_fields_rejected` PASSED
- `TestRepositoryLayer.test_strict_query_parameters` PASSED
- `TestRepositoryLayer.test_deterministic_ordering` PASSED
- `TestRepositoryLayer.test_explicit_soft_delete_lifecycle` PASSED
- `TestRepositoryLayer.test_user_active_filtering_consistency` PASSED
- `TestRepositoryLayer.test_append_only_protections` PASSED
- `TestRepositoryLayer.test_cache_expiry_and_metadata_refresh` PASSED
- `TestRepositoryLayer.test_concurrent_same_tenant_cache_upsert` PASSED
- `TestRepositoryLayer.test_atomic_download_count_increment` PASSED
- `TestRepositoryLayer.test_sqlstate_exception_translation` PASSED
- `TestRepositoryLayer.test_cache_service_zero_external_api_calls` PASSED

# Security Validation
- Mass assignment test proves database columns (`company_id`, timestamps) cannot be overwritten through client payloads.
- Strict page bounds (maximum 100 rows) protect endpoints against memory overflow attacks.

# Tenant Isolation Validation
- Direct tests show that updates, deletes, reads, and list counts to cross-tenant entities return NotFound exceptions.

# Performance Notes
- Concurrent cache upsert test verifies safety under high thread-contention rates.
- Atomic download-count increments run in a single DB query using RETURNING.

# Remaining Limitations
- None.

# Deliverables
- Base and specific Repository class files under `app/db/repositories/`.
- Repository unit tests in `test_phase2_6_repository_layer.py`.
