"""
TalentForge AI — Modular Models Package
=======================================
Aggregates all database models in one package namespace for Alembic and SQLAlchemy discovery.
"""

from app.db.models.company import Company
from app.db.models.user import User
from app.db.models.app_settings import AppSettings
from app.db.models.employee import Employee, EmployeeStatus, WorkMode, ExperienceLevel
from app.db.models.candidate import Candidate, CandidateStatus
from app.db.models.resume import Resume
from app.db.models.job_description import JobDescription, EmploymentType

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
]
