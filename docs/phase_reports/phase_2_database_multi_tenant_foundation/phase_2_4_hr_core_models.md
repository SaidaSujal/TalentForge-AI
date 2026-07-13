# Project
TalentForge AI

# Phase
2 — Database & Multi-Tenant Foundation

# Subphase
2.4 — HR Core Models & Workflows

# Status
✅ COMPLETED

# Date
2026-07-09

# Objective
Implement database schemas, SQLAlchemy models, Postgres enums, check constraints, and migrations for secondary HR workflows (onboarding, performance reviews, attrition assessments, learning plans, interview kits).

# Overview
This subphase defines 8 tables for core HR workflows, implementing check constraints, composite indexes for Pandas analytics, SHAP explainability support in JSONB, and human-in-the-loop validation markers.

# Architecture Decisions
- Bind all workflow records to `company_id` to enforce multi-tenancy.
- Enforce partial unique index on `OnboardingPlan` to allow only one active onboarding roadmap per employee.
- Enforce check constraints on rating scales and percentages (`progress_percent`, `risk_score`, `readiness_score`, `manager_satisfaction_score`, `attendance_percent`).
- Implement self-referential version tracking on performance reviews and learning plans using a `previous_version_id` column.
- Use `SET NULL` foreign keys for references to managers so that deleting manager users preserves reviews.
- Store machine learning SHAP values in the `risk_factors` (JSONB) column on `AttritionAssessment`.

# Files Created
### `app/db/models/onboarding_plan.py`
- **path:** [onboarding_plan.py](file:///Users/sujal/TalentForge%20AI/app/db/models/onboarding_plan.py)
- **purpose:** Defines OnboardingPlan model, enums (OnboardingStatus), progress checks.
- **classes:** `OnboardingPlan`, `OnboardingStatus`
- **methods:** None

### `app/db/models/onboarding_task.py`
- **path:** [onboarding_task.py](file:///Users/sujal/TalentForge%20AI/app/db/models/onboarding_task.py)
- **purpose:** Defines OnboardingTask model, category enum (OnboardingTaskCategory), status enum (TaskStatus).
- **classes:** `OnboardingTask`, `OnboardingTaskCategory`, `TaskStatus`
- **methods:** None

### `app/db/models/performance_review.py`
- **path:** [performance_review.py](file:///Users/sujal/TalentForge%20AI/app/db/models/performance_review.py)
- **purpose:** Defines PerformanceReview model and status enum (ReviewStatus).
- **classes:** `PerformanceReview`, `ReviewStatus`
- **methods:** None

### `app/db/models/attrition_assessment.py`
- **path:** [attrition_assessment.py](file:///Users/sujal/TalentForge%20AI/app/db/models/attrition_assessment.py)
- **purpose:** Defines AttritionAssessment model.
- **classes:** `AttritionAssessment`
- **methods:** None

### `app/db/models/retention_strategy.py`
- **path:** [retention_strategy.py](file:///Users/sujal/TalentForge%20AI/app/db/models/retention_strategy.py)
- **purpose:** Defines RetentionStrategy model and approval enum (ApprovalStatus).
- **classes:** `RetentionStrategy`, `ApprovalStatus`
- **methods:** None

### `app/db/models/learning_plan.py`
- **path:** [learning_plan.py](file:///Users/sujal/TalentForge%20AI/app/db/models/learning_plan.py)
- **purpose:** Defines LearningPlan model.
- **classes:** `LearningPlan`
- **methods:** None

### `app/db/models/training_record.py`
- **path:** [training_record.py](file:///Users/sujal/TalentForge%20AI/app/db/models/training_record.py)
- **purpose:** Defines TrainingRecord model and status enum (TrainingStatus).
- **classes:** `TrainingRecord`, `TrainingStatus`
- **methods:** None

### `app/db/models/interview_kit.py`
- **path:** [interview_kit.py](file:///Users/sujal/TalentForge%20AI/app/db/models/interview_kit.py)
- **purpose:** Defines InterviewKit model.
- **classes:** `InterviewKit`
- **methods:** None

### `tests/test_phase2_4_workflow_models.py`
- **path:** [test_phase2_4_workflow_models.py](file:///Users/sujal/TalentForge%20AI/tests/test_phase2_4_workflow_models.py)
- **purpose:** Verifies constraints, unique indexes, self-referential relations, and cascades for HR Core workflows.
- **classes:** `TestWorkflowModels`
- **methods:** `test_onboarding_plan_and_task_creation`, `test_onboarding_plan_progress_check_constraint`, `test_onboarding_plan_unique_active_employee_index`, `test_performance_review_lifecycle`, `test_attrition_assessment_and_retention_strategy`, `test_learning_plan_and_training_records`, `test_interview_kit_lifecycle`

### `alembic/versions/0006_create_workflow_tables.py`
- **path:** [0006_create_workflow_tables.py](file:///Users/sujal/TalentForge%20AI/alembic/versions/0006_create_workflow_tables.py)
- **purpose:** Database schema migration script for the 8 core workflow tables.
- **classes:** None
- **methods:** `upgrade`, `downgrade`

# Files Modified
### `app/db/models/__init__.py`
- **path:** [__init__.py](file:///Users/sujal/TalentForge%20AI/app/db/models/__init__.py)
- **exact changes:** Imported OnboardingPlan, OnboardingTask, PerformanceReview, AttritionAssessment, RetentionStrategy, LearningPlan, TrainingRecord, and InterviewKit.
- **why changes were required:** Make all models discoverable by Alembic for migrations.

# Database Changes
- Tables created: `onboarding_plans`, `onboarding_tasks`, `performance_reviews`, `attrition_assessments`, `retention_strategies`, `learning_plans`, `training_records`, `interview_kits`
- Custom Postgres ENUMs: `onboarding_status_enum`, `onboarding_task_category_enum`, `task_status_enum`, `review_status_enum`, `risk_level_enum`, `retention_strategy_status_enum`, `approval_status_enum`, `training_status_enum`
- Check constraints added to enforce numeric data ranges.

# Repository Changes
None.

# Seeder Changes
None.

# Testing
- new tests: 7 tests in `test_phase2_4_workflow_models.py`
- previous tests: 28 tests (Phase 1 + Phase 2.1 + Phase 2.2 + Phase 2.3)
- total tests: 35 tests (cumulative)
- validation commands:
  ```bash
  PYTHONPATH=. .venv/bin/pytest tests/test_phase2_4_workflow_models.py -v
  ```

# Validation Results
All tests passed:
- `TestWorkflowModels.test_onboarding_plan_and_task_creation` PASSED
- `TestWorkflowModels.test_onboarding_plan_progress_check_constraint` PASSED
- `TestWorkflowModels.test_onboarding_plan_unique_active_employee_index` PASSED
- `TestWorkflowModels.test_performance_review_lifecycle` PASSED
- `TestWorkflowModels.test_attrition_assessment_and_retention_strategy` PASSED
- `TestWorkflowModels.test_learning_plan_and_training_records` PASSED
- `TestWorkflowModels.test_interview_kit_lifecycle` PASSED

# Security Validation
- Verified human-in-the-loop approval checks on `RetentionStrategy` and `InterviewKit` models.
- Verified that deleting a supervisor retains review logs with NULL.

# Tenant Isolation Validation
- Checked that onboarding plans and other workflows are filtered by `company_id`.

# Performance Notes
- Composite indexes added to speed up queries grouping by `(company_id, status)` or `(company_id, employee_id)`.

# Remaining Limitations
- None.

# Deliverables
- SQLAlchemy models and migration script `0006_create_workflow_tables.py`.
- Unit tests in `test_phase2_4_workflow_models.py`.
