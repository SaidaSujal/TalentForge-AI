"""
TalentForge AI — Database Repositories Package
===============================================
Aggregates all repository classes in one package namespace.
"""

from app.db.repositories.ai_cache import AICacheRepository
from app.db.repositories.ai_history import AIHistoryRepository
from app.db.repositories.audit import AuditRepository
from app.db.repositories.base import BaseRepository, TenantRepository
from app.db.repositories.candidate import CandidateRepository
from app.db.repositories.employee import EmployeeRepository
from app.db.repositories.export_job import ExportJobRepository
from app.db.repositories.user import UserRepository

__all__ = [
    "BaseRepository",
    "TenantRepository",
    "UserRepository",
    "EmployeeRepository",
    "CandidateRepository",
    "AuditRepository",
    "AICacheRepository",
    "AIHistoryRepository",
    "ExportJobRepository",
]
