"""
TalentForge AI — Modular Models Package
=======================================
Aggregates all database models in one package namespace for Alembic and SQLAlchemy discovery.
"""

from app.db.models.ai_cache import AICache
from app.db.models.ai_history import AIHistory
from app.db.models.app_settings import AppSettings
from app.db.models.attrition_assessment import AttritionAssessment, RiskLevel
from app.db.models.audit_log import AuditLog
from app.db.models.candidate import Candidate, CandidateStatus
from app.db.models.company import Company
from app.db.models.employee import Employee, EmployeeStatus, ExperienceLevel, WorkMode
from app.db.models.export_job import ExportJob, ExportStatus, ExportType
from app.db.models.interview_kit import InterviewKit
from app.db.models.job_description import EmploymentType, JobDescription
from app.db.models.learning_plan import LearningPlan
from app.db.models.onboarding_plan import OnboardingPlan, OnboardingStatus
from app.db.models.onboarding_task import (
    OnboardingTask,
    OnboardingTaskCategory,
    TaskStatus,
)
from app.db.models.performance_review import (
    ApprovalStatus,
    PerformanceReview,
    ReviewStatus,
)
from app.db.models.policy_chunk import PolicyChunk
from app.db.models.policy_document import PolicyDocument, PolicyDocumentStatus
from app.db.models.resume import Resume
from app.db.models.retention_strategy import RetentionStrategy, RetentionStrategyStatus
from app.db.models.training_record import TrainingRecord, TrainingStatus
from app.db.models.user import User

__all__ = [
    "Company",
    "User",
    "AppSettings",
    "Employee",
    "EmployeeStatus",
    "WorkMode",
    "ExperienceLevel",
    "Candidate",
    "CandidateStatus",
    "Resume",
    "JobDescription",
    "EmploymentType",
    "PolicyDocument",
    "PolicyDocumentStatus",
    "PolicyChunk",
    "OnboardingPlan",
    "OnboardingStatus",
    "OnboardingTask",
    "OnboardingTaskCategory",
    "TaskStatus",
    "PerformanceReview",
    "ReviewStatus",
    "ApprovalStatus",
    "AttritionAssessment",
    "RiskLevel",
    "RetentionStrategy",
    "RetentionStrategyStatus",
    "LearningPlan",
    "TrainingRecord",
    "TrainingStatus",
    "InterviewKit",
    "AICache",
    "AIHistory",
    "AuditLog",
    "ExportJob",
    "ExportType",
    "ExportStatus",
]
