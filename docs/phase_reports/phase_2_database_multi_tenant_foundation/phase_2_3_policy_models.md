# Project
TalentForge AI

# Phase
2 — Database & Multi-Tenant Foundation

# Subphase
2.3 — Policy Models

# Status
✅ COMPLETED

# Date
2026-07-08

# Objective
Design and implement the database foundation for the HR Policy RAG Chatbot, including document metadata, text chunk segmentation, vector embedding columns, and dynamic migration fallbacks.

# Overview
This subphase introduces the tables needed to represent uploaded HR manual files and their chunked text segments. High-dimensional vector embeddings are stored in `pgvector` columns with dynamic fallback index generation.

# Architecture Decisions
- Bind all records to `company_id` using composite indices.
- Enforce partial unique indexes on active policy documents (filtering by `is_deleted = false`) to prevent duplicate names and document content hashes within a tenant.
- Enforce unique index on `(company_id, document_id, chunk_index)` to prevent duplicate segments.
- Map embedding vector dimension to 1024 to support standard high-scale LLM encoders (e.g. `nvidia/nv-embed-v1`).
- Dynamically detect `pgvector` version in migrations to generate HNSW indexes for modern versions, IVFFlat for older versions, or skip vector indexes entirely on local sqlite/non-vector setups.

# Files Created
### `app/db/models/policy_document.py`
- **path:** [policy_document.py](file:///Users/sujal/TalentForge%20AI/app/db/models/policy_document.py)
- **purpose:** Defines PolicyDocument model, status enum (PolicyDocumentStatus), and content hash storage.
- **classes:** `PolicyDocument`, `PolicyDocumentStatus`
- **methods:** None

### `app/db/models/policy_chunk.py`
- **path:** [policy_chunk.py](file:///Users/sujal/TalentForge%20AI/app/db/models/policy_chunk.py)
- **purpose:** Defines PolicyChunk model and 1024-dimension vector embeddings.
- **classes:** `PolicyChunk`
- **methods:** None

### `tests/test_phase2_3_policy_models.py`
- **path:** [test_phase2_3_policy_models.py](file:///Users/sujal/TalentForge%20AI/tests/test_phase2_3_policy_models.py)
- **purpose:** Verifies Policy models constraints, relationships, dimensions, soft deletes, and migrations.
- **classes:** `TestPolicyModels`
- **methods:** `test_policy_document_creation_success`, `test_policy_chunk_creation_and_vector`, `test_wrong_vector_dimension_rejection`, `test_document_active_uniqueness_constraints`, `test_duplicate_allowed_after_soft_delete`, `test_chunk_unique_index_constraint`, `test_relationships_and_cascade`, `test_tenant_isolation`, `test_indexed_at_and_chunk_count_fields`, `test_migration_lifecycle`

### `alembic/versions/0005_create_policy_tables.py`
- **path:** [0005_create_policy_tables.py](file:///Users/sujal/TalentForge%20AI/alembic/versions/0005_create_policy_tables.py)
- **purpose:** Database schema migration script for PolicyDocument and PolicyChunk tables.
- **classes:** None
- **methods:** `upgrade`, `downgrade`

# Files Modified
### `app/db/models/company.py`
- **path:** [company.py](file:///Users/sujal/TalentForge%20AI/app/db/models/company.py)
- **exact changes:** Added relationships pointing to PolicyDocument and PolicyChunk.
- **why changes were required:** Establish bidirectional navigation.

### `app/db/models/__init__.py`
- **path:** [__init__.py](file:///Users/sujal/TalentForge%20AI/app/db/models/__init__.py)
- **exact changes:** Imported `PolicyDocument` and `PolicyChunk`.
- **why changes were required:** Enable auto-discovery by Alembic.

# Database Changes
- Tables created: `policy_documents`, `policy_chunks`
- Custom Postgres ENUM: `policy_document_status_enum`
- Partial unique indexes: `uq_policy_documents_active_name`, `uq_policy_documents_active_hash`
- Vector index on `policy_chunks.embedding` using dynamic HNSW/IVFFlat fallback.

# Repository Changes
None.

# Seeder Changes
None.

# Testing
- new tests: 10 tests in `test_phase2_3_policy_models.py`
- previous tests: 18 tests (Phase 1 + Phase 2.1 + Phase 2.2)
- total tests: 28 tests (cumulative)
- validation commands:
  ```bash
  PYTHONPATH=. .venv/bin/pytest tests/test_phase2_3_policy_models.py -v
  ```

# Validation Results
All tests passed:
- `TestPolicyModels.test_policy_document_creation_success` PASSED
- `TestPolicyModels.test_policy_chunk_creation_and_vector` PASSED
- `TestPolicyModels.test_wrong_vector_dimension_rejection` PASSED
- `TestPolicyModels.test_document_active_uniqueness_constraints` PASSED
- `TestPolicyModels.test_duplicate_allowed_after_soft_delete` PASSED
- `TestPolicyModels.test_chunk_unique_index_constraint` PASSED
- `TestPolicyModels.test_relationships_and_cascade` PASSED
- `TestPolicyModels.test_tenant_isolation` PASSED
- `TestPolicyModels.test_indexed_at_and_chunk_count_fields` PASSED
- `test_migration_lifecycle` PASSED

# Security Validation
- Unique active upload hashes prevent data injection duplication.
- Verified that invalid vector dimensions are rejected at the DB constraint level.

# Tenant Isolation Validation
- Composite indexes established on `(company_id, document_hash)` and `(company_id, document_id)` to partition query paths by tenant.

# Performance Notes
- HNSW Cosine vector index generated when pgvector >= 0.5.0, falling back to IVFFlat, ensuring query efficiency under scale.

# Remaining Limitations
- None.

# Deliverables
- PolicyDocument and PolicyChunk models in `policy_document.py` and `policy_chunk.py`.
- Migration script `0005_create_policy_tables.py`.
- Unit tests in `test_phase2_3_policy_models.py`.
