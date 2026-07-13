"""
TalentForge AI — Demo Data Seeder
=================================
Seeds the database with a safe, deterministic, and idempotent demo tenant.

Usage:
    python scripts/seed_demo_data.py
    python scripts/seed_demo_data.py --reset-demo-data
    python scripts/seed_demo_data.py --allow-remote-development
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import os
import sys
import uuid
from datetime import date, datetime
from decimal import Decimal
from urllib.parse import urlparse

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import hash_password
from app.db.models import (
    ApprovalStatus,
    AttritionAssessment,
    AuditLog,
    Candidate,
    CandidateStatus,
    Company,
    Employee,
    EmployeeStatus,
    EmploymentType,
    ExperienceLevel,
    InterviewKit,
    JobDescription,
    LearningPlan,
    OnboardingPlan,
    OnboardingStatus,
    OnboardingTask,
    OnboardingTaskCategory,
    PerformanceReview,
    PolicyDocument,
    PolicyDocumentStatus,
    Resume,
    RetentionStrategy,
    RetentionStrategyStatus,
    ReviewStatus,
    RiskLevel,
    TaskStatus,
    TrainingRecord,
    TrainingStatus,
    User,
    WorkMode,
)
from app.db.session import AsyncSessionLocal

# ─── UUID Strategy ───────────────────────────────────────────────────────────
SEED_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_DNS, "seed.talentforge.example.com")


def get_uuid(key: str) -> uuid.UUID:
    """Generate a stable UUID5 based on a DNS-mapped seed namespace."""
    return uuid.uuid5(SEED_NAMESPACE, key)


DEMO_COMPANY_ID = uuid.UUID(settings.demo_company_id)
DEMO_USER_ID = uuid.UUID(settings.demo_user_id)

# ─── Base Seeding Data ────────────────────────────────────────────────────────

company_data = {
    "id": DEMO_COMPANY_ID,
    "name": "Development Enterprise Inc.",
    "slug": "dev-enterprise",
    "settings_json": "{}",
    "is_active": True,
}

user_data = {
    "id": DEMO_USER_ID,
    "email": "admin@example.com",
    "password_hash": "",  # dynamically generated during seeding
    "role": "admin",
    "company_id": DEMO_COMPANY_ID,
    "is_active": True,
}

employees_data = [
    {
        "id": get_uuid("employee_1"),
        "company_id": DEMO_COMPANY_ID,
        "user_id": DEMO_USER_ID,
        "first_name": "Taylor",
        "last_name": "Vance",
        "email": "taylor.vance@example.com",
        "phone": "+1-555-0101",
        "department": "Human Resources",
        "role": "HR Director",
        "salary": Decimal("120000.00"),
        "status": EmployeeStatus.ACTIVE,
        "role_enum": "admin",
        "work_mode": WorkMode.OFFICE,
        "experience_level": ExperienceLevel.DIRECTOR,
        "current_skills": ["Leadership", "Strategic Planning", "HR Compliance"],
        "target_role": None,
        "is_deleted": False,
    },
    {
        "id": get_uuid("employee_2"),
        "company_id": DEMO_COMPANY_ID,
        "user_id": None,
        "first_name": "Morgan",
        "last_name": "Finch",
        "email": "morgan.finch@example.com",
        "phone": "+1-555-0102",
        "department": "Engineering",
        "role": "Engineering Manager",
        "salary": Decimal("95000.00"),
        "status": EmployeeStatus.ACTIVE,
        "role_enum": "manager",
        "work_mode": WorkMode.HYBRID,
        "experience_level": ExperienceLevel.LEAD,
        "current_skills": ["Software Engineering", "Team Management", "Agile"],
        "target_role": "Director of Engineering",
        "is_deleted": False,
    },
    {
        "id": get_uuid("employee_3"),
        "company_id": DEMO_COMPANY_ID,
        "user_id": None,
        "first_name": "Jordan",
        "last_name": "Blake",
        "email": "jordan.blake@example.com",
        "phone": "+1-555-0103",
        "department": "Sales",
        "role": "Sales Manager",
        "salary": Decimal("90000.00"),
        "status": EmployeeStatus.ACTIVE,
        "role_enum": "manager",
        "work_mode": WorkMode.HYBRID,
        "experience_level": ExperienceLevel.LEAD,
        "current_skills": ["Sales Management", "Negotiation", "Business Development"],
        "target_role": "VP of Sales",
        "is_deleted": False,
    },
    {
        "id": get_uuid("employee_4"),
        "company_id": DEMO_COMPANY_ID,
        "user_id": None,
        "first_name": "Alex",
        "last_name": "Chen",
        "email": "alex.chen@example.com",
        "phone": "+1-555-0104",
        "department": "Engineering",
        "role": "Senior Software Engineer",
        "salary": Decimal("80000.00"),
        "status": EmployeeStatus.ACTIVE,
        "role_enum": "employee",
        "work_mode": WorkMode.REMOTE,
        "experience_level": ExperienceLevel.SENIOR,
        "current_skills": ["Python", "FastAPI", "SQLAlchemy", "PostgreSQL"],
        "target_role": "Engineering Manager",
        "is_deleted": False,
    },
    {
        "id": get_uuid("employee_5"),
        "company_id": DEMO_COMPANY_ID,
        "user_id": None,
        "first_name": "Sam",
        "last_name": "Rivera",
        "email": "sam.rivera@example.com",
        "phone": "+1-555-0105",
        "department": "Engineering",
        "role": "Software Engineer",
        "salary": Decimal("65000.00"),
        "status": EmployeeStatus.ACTIVE,
        "role_enum": "employee",
        "work_mode": WorkMode.REMOTE,
        "experience_level": ExperienceLevel.MID,
        "current_skills": ["JavaScript", "HTML", "CSS", "Tailwind CSS"],
        "target_role": "Senior Software Engineer",
        "is_deleted": False,
    },
    {
        "id": get_uuid("employee_6"),
        "company_id": DEMO_COMPANY_ID,
        "user_id": None,
        "first_name": "Casey",
        "last_name": "Kim",
        "email": "casey.kim@example.com",
        "phone": "+1-555-0106",
        "department": "Engineering",
        "role": "Quality Engineer",
        "salary": Decimal("60000.00"),
        "status": EmployeeStatus.ACTIVE,
        "role_enum": "employee",
        "work_mode": WorkMode.HYBRID,
        "experience_level": ExperienceLevel.MID,
        "current_skills": ["QA Automation", "Selenium", "Pytest", "CI/CD"],
        "target_role": "Senior QA Engineer",
        "is_deleted": False,
    },
    {
        "id": get_uuid("employee_7"),
        "company_id": DEMO_COMPANY_ID,
        "user_id": None,
        "first_name": "Robin",
        "last_name": "Patel",
        "email": "robin.patel@example.com",
        "phone": "+1-555-0107",
        "department": "Human Resources",
        "role": "Recruiter",
        "salary": Decimal("55000.00"),
        "status": EmployeeStatus.ACTIVE,
        "role_enum": "employee",
        "work_mode": WorkMode.HYBRID,
        "experience_level": ExperienceLevel.MID,
        "current_skills": ["Talent Acquisition", "Technical Recruiting", "Sourcing"],
        "target_role": "Lead Recruiter",
        "is_deleted": False,
    },
    {
        "id": get_uuid("employee_8"),
        "company_id": DEMO_COMPANY_ID,
        "user_id": None,
        "first_name": "Kelly",
        "last_name": "Green",
        "email": "kelly.green@example.com",
        "phone": "+1-555-0108",
        "department": "Human Resources",
        "role": "HR Associate",
        "salary": Decimal("45000.00"),
        "status": EmployeeStatus.ONBOARDING,
        "role_enum": "employee",
        "work_mode": WorkMode.OFFICE,
        "experience_level": ExperienceLevel.JUNIOR,
        "current_skills": ["Onboarding", "Data Entry", "Microsoft Office"],
        "target_role": "HR Specialist",
        "is_deleted": False,
    },
    {
        "id": get_uuid("employee_9"),
        "company_id": DEMO_COMPANY_ID,
        "user_id": None,
        "first_name": "Pat",
        "last_name": "Martinez",
        "email": "pat.martinez@example.com",
        "phone": "+1-555-0109",
        "department": "Sales",
        "role": "Sales Rep",
        "salary": Decimal("50000.00"),
        "status": EmployeeStatus.ACTIVE,
        "role_enum": "employee",
        "work_mode": WorkMode.REMOTE,
        "experience_level": ExperienceLevel.MID,
        "current_skills": ["Cold Calling", "Lead Generation", "Sales Pitching"],
        "target_role": "Senior Sales Rep",
        "is_deleted": False,
    },
    {
        "id": get_uuid("employee_10"),
        "company_id": DEMO_COMPANY_ID,
        "user_id": None,
        "first_name": "Chris",
        "last_name": "Taylor",
        "email": "chris.taylor@example.com",
        "phone": "+1-555-0110",
        "department": "Sales",
        "role": "Sales Associate",
        "salary": Decimal("40000.00"),
        "status": EmployeeStatus.ACTIVE,
        "role_enum": "employee",
        "work_mode": WorkMode.HYBRID,
        "experience_level": ExperienceLevel.JUNIOR,
        "current_skills": ["Customer Relations", "Communication", "Sales Support"],
        "target_role": "Sales Rep",
        "is_deleted": False,
    },
]

employee_managers = {
    get_uuid("employee_1"): None,
    get_uuid("employee_2"): get_uuid("employee_1"),
    get_uuid("employee_3"): get_uuid("employee_1"),
    get_uuid("employee_4"): get_uuid("employee_2"),
    get_uuid("employee_5"): get_uuid("employee_2"),
    get_uuid("employee_6"): get_uuid("employee_2"),
    get_uuid("employee_7"): get_uuid("employee_1"),
    get_uuid("employee_8"): get_uuid("employee_1"),
    get_uuid("employee_9"): get_uuid("employee_3"),
    get_uuid("employee_10"): get_uuid("employee_3"),
}

candidates_data = [
    {
        "id": get_uuid("candidate_1"),
        "company_id": DEMO_COMPANY_ID,
        "first_name": "Avery",
        "last_name": "Sterling",
        "email": "avery.sterling@example.com",
        "phone": "+1-555-0111",
        "status": CandidateStatus.APPLIED,
        "experience_years": Decimal("3.5"),
        "education": "BS in Computer Science from State University",
        "current_role": "Software Developer",
        "skills": ["Python", "Django", "PostgreSQL"],
        "match_score": Decimal("72.50"),
        "scorecard_json": {"technical": 70, "communication": 75},
        "suggested_questions": [
            "What is a Django model?",
            "Explain PostgreSQL indexing.",
        ],
        "interview_invitation_text": "Dear Avery, we would like to invite you for an interview...",
        "is_deleted": False,
    },
    {
        "id": get_uuid("candidate_2"),
        "company_id": DEMO_COMPANY_ID,
        "first_name": "Riley",
        "last_name": "Brooks",
        "email": "riley.brooks@example.com",
        "phone": "+1-555-0112",
        "status": CandidateStatus.SCREENED,
        "experience_years": Decimal("5.0"),
        "education": "MS in Software Engineering from Tech Institute",
        "current_role": "Backend Engineer",
        "skills": ["Python", "FastAPI", "SQLAlchemy", "Redis"],
        "match_score": Decimal("84.00"),
        "scorecard_json": {"technical": 85, "communication": 80},
        "suggested_questions": [
            "Explain ASGI vs WSGI.",
            "What is SQLAlchemy yield status?",
        ],
        "interview_invitation_text": "Dear Riley, thank you for screening with us...",
        "is_deleted": False,
    },
    {
        "id": get_uuid("candidate_3"),
        "company_id": DEMO_COMPANY_ID,
        "first_name": "Quinn",
        "last_name": "Parker",
        "email": "quinn.parker@example.com",
        "phone": "+1-555-0113",
        "status": CandidateStatus.SHORTLISTED,
        "experience_years": Decimal("8.0"),
        "education": "BS in Software Engineering",
        "current_role": "Senior Developer",
        "skills": ["Python", "FastAPI", "Docker", "Kubernetes", "AWS"],
        "match_score": Decimal("89.50"),
        "scorecard_json": {"technical": 90, "leadership": 85},
        "suggested_questions": [
            "Design a scalable RAG chatbot system.",
            "How do you manage Docker security?",
        ],
        "interview_invitation_text": "Dear Quinn, you have been shortlisted for the final round...",
        "is_deleted": False,
    },
    {
        "id": get_uuid("candidate_4"),
        "company_id": DEMO_COMPANY_ID,
        "first_name": "Logan",
        "last_name": "Carter",
        "email": "logan.carter@example.com",
        "phone": "+1-555-0114",
        "status": CandidateStatus.INTERVIEWING,
        "experience_years": Decimal("6.5"),
        "education": "BS in IT",
        "current_role": "Backend Developer",
        "skills": ["Java", "Spring Boot", "MySQL", "Docker"],
        "match_score": Decimal("92.00"),
        "scorecard_json": {"technical": 95, "communication": 88},
        "suggested_questions": [
            "Explain Spring Dependency Injection.",
            "How do you optimize DB queries?",
        ],
        "interview_invitation_text": "Dear Logan, we look forward to our technical panel interview...",
        "is_deleted": False,
    },
    {
        "id": get_uuid("candidate_5"),
        "company_id": DEMO_COMPANY_ID,
        "first_name": "Hayden",
        "last_name": "Cross",
        "email": "hayden.cross@example.com",
        "phone": "+1-555-0115",
        "status": CandidateStatus.OFFERED,
        "experience_years": Decimal("4.0"),
        "education": "BS in Computer Engineering",
        "current_role": "Full Stack Developer",
        "skills": ["JavaScript", "React", "Node.js", "MongoDB"],
        "match_score": Decimal("81.50"),
        "scorecard_json": {"technical": 80, "cultural": 83},
        "suggested_questions": [
            "Explain virtual DOM in React.",
            "How do you secure Node.js APIs?",
        ],
        "interview_invitation_text": "Dear Hayden, we are pleased to offer you the position...",
        "is_deleted": False,
    },
    {
        "id": get_uuid("candidate_6"),
        "company_id": DEMO_COMPANY_ID,
        "first_name": "Reese",
        "last_name": "Winters",
        "email": "reese.winters@example.com",
        "phone": "+1-555-0116",
        "status": CandidateStatus.HIRED,
        "experience_years": Decimal("10.0"),
        "education": "PhD in Computer Science",
        "current_role": "Lead Architect",
        "skills": ["Python", "FastAPI", "Go", "Distributed Systems"],
        "match_score": Decimal("95.00"),
        "scorecard_json": {"technical": 98, "architecture": 95},
        "suggested_questions": [
            "How do you coordinate distributed locks?",
            "Explain vector database search optimization.",
        ],
        "interview_invitation_text": "Dear Reese, welcome to our organization...",
        "is_deleted": False,
    },
    {
        "id": get_uuid("candidate_7"),
        "company_id": DEMO_COMPANY_ID,
        "first_name": "Skylar",
        "last_name": "Vance",
        "email": "skylar.vance@example.com",
        "phone": "+1-555-0117",
        "status": CandidateStatus.REJECTED,
        "experience_years": Decimal("1.5"),
        "education": "Associate Degree in IT",
        "current_role": "Junior Developer",
        "skills": ["HTML", "CSS", "Basic JS"],
        "match_score": Decimal("48.00"),
        "scorecard_json": {"technical": 40, "communication": 60},
        "suggested_questions": [
            "Explain flexbox in CSS.",
            "What is an event listener?",
        ],
        "interview_invitation_text": "Dear Skylar, thank you for your application, however...",
        "is_deleted": False,
    },
    {
        "id": get_uuid("candidate_8"),
        "company_id": DEMO_COMPANY_ID,
        "first_name": "Dakota",
        "last_name": "Hayes",
        "email": "dakota.hayes@example.com",
        "phone": "+1-555-0118",
        "status": CandidateStatus.APPLIED,
        "experience_years": Decimal("2.0"),
        "education": "Self-taught, boot camp graduate",
        "current_role": "Web Developer",
        "skills": ["PHP", "Laravel", "MySQL"],
        "match_score": Decimal("65.00"),
        "scorecard_json": {"technical": 65, "communication": 65},
        "suggested_questions": [
            "Explain MVC pattern in Laravel.",
            "How do you handle migrations?",
        ],
        "interview_invitation_text": "Dear Dakota, we have received your application...",
        "is_deleted": False,
    },
]

resumes_data = [
    {
        "id": get_uuid(f"resume_{i}"),
        "company_id": DEMO_COMPANY_ID,
        "candidate_id": get_uuid(f"candidate_{i}"),
        "file_name": f"resume_candidate_{i}.pdf",
        "file_path": None,
        "file_size": 12400 + i * 200,
        "mime_type": "application/pdf",
        "raw_text": f"Resume of Candidate {i}. Highly skilled professional with experience in Java, Python, and SQL.",
        "resume_hash": hashlib.sha256(
            f"Resume of Candidate {i}. Highly skilled professional with experience in Java, Python, and SQL.".encode(
                "utf-8"
            )
        ).hexdigest(),
        "is_deleted": False,
    }
    for i in range(1, 9)
]

job_descriptions_data = [
    {
        "id": get_uuid("jd_1"),
        "company_id": DEMO_COMPANY_ID,
        "title": "Software Engineer",
        "department": "Engineering",
        "experience_level": ExperienceLevel.MID,
        "location": "Remote",
        "employment_type": EmploymentType.FULL_TIME,
        "salary_range": "$60,000 - $80,000",
        "job_description_text": "# Software Engineer\n\nWe are looking for a Mid-level Software Engineer to join our Engineering department...",
        "required_skills": ["Python", "FastAPI", "SQLAlchemy"],
        "preferred_skills": ["Docker", "Redis"],
        "responsibilities": [
            "Develop clean APIs",
            "Maintain unit tests",
            "Collaborate with product teams",
        ],
        "requirements": [
            "3+ years of experience with Python",
            "BS in CS or equivalent",
        ],
        "benefits": ["Remote work", "Health insurance", "PTO"],
        "ats_keywords": ["Python Developer", "FastAPI", "API Engineer"],
        "variants": {"linkedin_post": "We are hiring! Software Engineer..."},
        "jd_hash": hashlib.sha256("jd_1_hash".encode("utf-8")).hexdigest(),
        "is_deleted": False,
    },
    {
        "id": get_uuid("jd_2"),
        "company_id": DEMO_COMPANY_ID,
        "title": "HR Specialist",
        "department": "Human Resources",
        "experience_level": ExperienceLevel.SENIOR,
        "location": "Office",
        "employment_type": EmploymentType.FULL_TIME,
        "salary_range": "$50,000 - $70,000",
        "job_description_text": "# HR Specialist\n\nWe are seeking a Senior HR Specialist to lead recruitment and employee onboarding...",
        "required_skills": [
            "Talent Acquisition",
            "Technical Recruiting",
            "HR Compliance",
        ],
        "preferred_skills": ["Conflict Resolution", "Jira"],
        "responsibilities": [
            "Handle onboarding workflows",
            "Source candidates",
            "Maintain HR records",
        ],
        "requirements": [
            "5+ years of experience in HR",
            "Excellent communication skills",
        ],
        "benefits": ["Onsite cafeteria", "401k match", "Dental insurance"],
        "ats_keywords": ["HR Generalist", "Recruiter", "HR Specialist"],
        "variants": {"linkedin_post": "Join Acme! HR Specialist opening..."},
        "jd_hash": hashlib.sha256("jd_2_hash".encode("utf-8")).hexdigest(),
        "is_deleted": False,
    },
    {
        "id": get_uuid("jd_3"),
        "company_id": DEMO_COMPANY_ID,
        "title": "Sales Specialist",
        "department": "Sales",
        "experience_level": ExperienceLevel.JUNIOR,
        "location": "Hybrid",
        "employment_type": EmploymentType.CONTRACT,
        "salary_range": "$40,000 - $50,000",
        "job_description_text": "# Sales Specialist\n\nWe are looking for a Junior Sales Specialist to support sales operations and representative outbound calls...",
        "required_skills": ["Communication", "Customer Support", "Sales CRM"],
        "preferred_skills": ["HubSpot", "Negotiation"],
        "responsibilities": [
            "Qualify outbound leads",
            "Prepare sales summaries",
            "Maintain customer details",
        ],
        "requirements": ["1+ years of experience in sales", "Active listening skills"],
        "benefits": ["Performance bonus", "Flexible hybrid schedule"],
        "ats_keywords": [
            "Sales Rep",
            "Business Development Representative",
            "Sales Associate",
        ],
        "variants": {"linkedin_post": "Acme is hiring a Sales Specialist!"},
        "jd_hash": hashlib.sha256("jd_3_hash".encode("utf-8")).hexdigest(),
        "is_deleted": False,
    },
]

policy_documents_data = [
    {
        "id": get_uuid("policy_doc_1"),
        "company_id": DEMO_COMPANY_ID,
        "name": "Leave Policy 2026",
        "description": "Standard leaves, PTO limits, and holidays handbook.",
        "category": "Benefits",
        "status": PolicyDocumentStatus.UPLOADED,
        "file_name": "leave_policy_2026.pdf",
        "file_path": None,
        "file_size": 245000,
        "mime_type": "application/pdf",
        "document_hash": hashlib.sha256(
            "leave_policy_2026_hash".encode("utf-8")
        ).hexdigest(),
        "chunk_count": 0,
        "indexed_at": None,
        "error_message": None,
        "is_deleted": False,
    },
    {
        "id": get_uuid("policy_doc_2"),
        "company_id": DEMO_COMPANY_ID,
        "name": "Information Security Guidelines",
        "description": "Compliance standards for IT resources and data security.",
        "category": "Compliance",
        "status": PolicyDocumentStatus.UPLOADED,
        "file_name": "it_security_guidelines.pdf",
        "file_path": None,
        "file_size": 189000,
        "mime_type": "application/pdf",
        "document_hash": hashlib.sha256(
            "it_security_guidelines_hash".encode("utf-8")
        ).hexdigest(),
        "chunk_count": 0,
        "indexed_at": None,
        "error_message": None,
        "is_deleted": False,
    },
]

onboarding_plans_data = [
    {
        "id": get_uuid("onboarding_plan_1"),
        "company_id": DEMO_COMPANY_ID,
        "employee_id": get_uuid("employee_8"),
        "status": OnboardingStatus.IN_PROGRESS,
        "progress_percent": Decimal("40.00"),
        "welcome_email_text": "Dear Kelly, Welcome to Development Enterprise Inc.!",
        "team_announcement_text": "Team, please welcome Kelly Green to the HR department!",
        "plan_data_json": {
            "milestones": ["Day 1 Setup", "Week 1 Training", "Month 1 Review"]
        },
        "is_deleted": False,
    }
]

onboarding_tasks_data = [
    {
        "id": get_uuid("onboarding_task_1"),
        "company_id": DEMO_COMPANY_ID,
        "plan_id": get_uuid("onboarding_plan_1"),
        "title": "Submit signed offer letter",
        "description": "HR department requires signed documents.",
        "category": OnboardingTaskCategory.DOCUMENT,
        "status": TaskStatus.COMPLETED,
        "due_date": date(2026, 7, 10),
        "completed_at": datetime(2026, 7, 10, 10, 0, 0),
        "is_deleted": False,
    },
    {
        "id": get_uuid("onboarding_task_2"),
        "company_id": DEMO_COMPANY_ID,
        "plan_id": get_uuid("onboarding_plan_1"),
        "title": "Set up work laptop",
        "description": "Log in to corporate email, Slack, and development tools.",
        "category": OnboardingTaskCategory.TOOL,
        "status": TaskStatus.COMPLETED,
        "due_date": date(2026, 7, 12),
        "completed_at": datetime(2026, 7, 12, 9, 30, 0),
        "is_deleted": False,
    },
    {
        "id": get_uuid("onboarding_task_3"),
        "company_id": DEMO_COMPANY_ID,
        "plan_id": get_uuid("onboarding_plan_1"),
        "title": "Meet with Manager",
        "description": "Introductory meeting to discuss target role and objectives.",
        "category": OnboardingTaskCategory.MEETING,
        "status": TaskStatus.IN_PROGRESS,
        "due_date": date(2026, 7, 13),
        "completed_at": None,
        "is_deleted": False,
    },
    {
        "id": get_uuid("onboarding_task_4"),
        "company_id": DEMO_COMPANY_ID,
        "plan_id": get_uuid("onboarding_plan_1"),
        "title": "Read Leave Policy",
        "description": "Read standard leave handbook on first week.",
        "category": OnboardingTaskCategory.TASK,
        "status": TaskStatus.PENDING,
        "due_date": date(2026, 7, 15),
        "completed_at": None,
        "is_deleted": False,
    },
    {
        "id": get_uuid("onboarding_task_5"),
        "company_id": DEMO_COMPANY_ID,
        "plan_id": get_uuid("onboarding_plan_1"),
        "title": "Complete Security Quiz",
        "description": "Required IT compliance training quiz.",
        "category": OnboardingTaskCategory.GOAL,
        "status": TaskStatus.PENDING,
        "due_date": date(2026, 7, 20),
        "completed_at": None,
        "is_deleted": False,
    },
]

performance_reviews_data = [
    {
        "id": get_uuid("performance_review_1"),
        "company_id": DEMO_COMPANY_ID,
        "employee_id": get_uuid("employee_4"),
        "manager_id": get_uuid("employee_2"),
        "review_period": "Annual 2025",
        "status": ReviewStatus.COMPLETED,
        "goals_achieved": 5,
        "total_goals": 5,
        "attendance_percent": Decimal("98.50"),
        "manager_observations": "Alex is an exceptional senior developer, demonstrating great leadership.",
        "peer_feedback": "Alex is very helpful and writes clean code.",
        "review_summary": "Static demo draft — human review required. Outstanding performance.",
        "rating_suggestion": "Exceeds Expectations",
        "key_achievements": {
            "achievements": ["Completed RAG backend", "Integrated pgvector"]
        },
        "development_areas": {"improvement": ["System Design Architecture"]},
        "bias_check_notes": "None detected.",
        "promotion_readiness": True,
        "salary_revision_label": "Suggest 10% Increase",
        "smart_goals": {
            "next_goals": ["Learn Go language", "Optimize HNSW vector searches"]
        },
        "development_plan": "Continue technical leadership progression.",
        "pip_details": {},
        "signed_off_at": datetime(2026, 1, 15, 12, 0, 0),
        "is_deleted": False,
        "version_number": 1,
        "previous_version_id": None,
        "human_review_required": False,
        "reviewed_by": DEMO_USER_ID,
        "reviewed_at": datetime(2026, 1, 15, 12, 0, 0),
        "approval_status": ApprovalStatus.APPROVED,
    },
    {
        "id": get_uuid("performance_review_2"),
        "company_id": DEMO_COMPANY_ID,
        "employee_id": get_uuid("employee_9"),
        "manager_id": get_uuid("employee_3"),
        "review_period": "Annual 2025",
        "status": ReviewStatus.DRAFT,
        "goals_achieved": 3,
        "total_goals": 5,
        "attendance_percent": Decimal("92.00"),
        "manager_observations": "Pat meets most sales targets but should focus on lead consistency.",
        "peer_feedback": "Pat has good energy but can improve team sync.",
        "review_summary": "Static demo draft — human review required. Meets expectations.",
        "rating_suggestion": "Meets Expectations",
        "key_achievements": {"achievements": ["Met Q3 quota"]},
        "development_areas": {"improvement": ["Lead follow-ups"]},
        "bias_check_notes": "None.",
        "promotion_readiness": False,
        "salary_revision_label": "No Salary Adjustment",
        "smart_goals": {"next_goals": ["Increase cold calls", "Learn HubSpot"]},
        "development_plan": "Sales training and representative practice sessions.",
        "pip_details": {},
        "signed_off_at": None,
        "is_deleted": False,
        "version_number": 1,
        "previous_version_id": None,
        "human_review_required": True,
        "reviewed_by": None,
        "reviewed_at": None,
        "approval_status": ApprovalStatus.PENDING,
    },
]

attrition_assessments_data = [
    {
        "id": get_uuid("attrition_assessment_1"),
        "company_id": DEMO_COMPANY_ID,
        "employee_id": get_uuid("employee_9"),
        "risk_score": Decimal("82.00"),
        "risk_level": RiskLevel.HIGH,
        "risk_factors": {"satisfaction": -1.2, "overtime": 0.8},
        "stay_interview_questions": {
            "questions": ["Are you satisfied with work hours?"]
        },
        "replacement_cost": Decimal("15000.00"),
        "manager_satisfaction_score": Decimal("2.0"),
        "overtime_hours": Decimal("25.0"),
        "is_active_assessment": True,
        "is_deleted": False,
        "human_review_required": True,
        "reviewed_by": None,
        "reviewed_at": None,
        "approval_status": ApprovalStatus.PENDING,
    },
    {
        "id": get_uuid("attrition_assessment_2"),
        "company_id": DEMO_COMPANY_ID,
        "employee_id": get_uuid("employee_4"),
        "risk_score": Decimal("10.50"),
        "risk_level": RiskLevel.LOW,
        "risk_factors": {"satisfaction": 1.5, "overtime": -0.5},
        "stay_interview_questions": {"questions": ["What keeps you motivated?"]},
        "replacement_cost": Decimal("25000.00"),
        "manager_satisfaction_score": Decimal("4.8"),
        "overtime_hours": Decimal("2.0"),
        "is_active_assessment": True,
        "is_deleted": False,
        "human_review_required": True,
        "reviewed_by": None,
        "reviewed_at": None,
        "approval_status": ApprovalStatus.PENDING,
    },
]

retention_strategies_data = [
    {
        "id": get_uuid("retention_strategy_1"),
        "company_id": DEMO_COMPANY_ID,
        "assessment_id": get_uuid("attrition_assessment_1"),
        "employee_id": get_uuid("employee_9"),
        "recommendations": {
            "benefits": "Increase base commission.",
            "environment": "Adjust overtime limit.",
        },
        "action_plan": "Static demo draft — human review required. Meet with Jordan to adjust workloads.",
        "status": RetentionStrategyStatus.PROPOSED,
        "is_deleted": False,
        "version_number": 1,
        "previous_version_id": None,
        "human_review_required": True,
        "reviewed_by": None,
        "reviewed_at": None,
        "approval_status": ApprovalStatus.PENDING,
    }
]

learning_plans_data = [
    {
        "id": get_uuid("learning_plan_1"),
        "company_id": DEMO_COMPANY_ID,
        "employee_id": get_uuid("employee_5"),
        "current_role": "Software Engineer",
        "target_role": "Senior Software Engineer",
        "readiness_score": Decimal("75.00"),
        "skill_gap_analysis": {"missing": ["System Architecture", "FastAPI Advanced"]},
        "learning_path_json": {
            "path": ["Read FastAPI docs", "Complete System Design Course"]
        },
        "estimated_roi": "High ROI: Team gains local architect competency.",
        "is_deleted": False,
        "version_number": 1,
        "previous_version_id": None,
        "human_review_required": True,
        "reviewed_by": None,
        "reviewed_at": None,
        "approval_status": ApprovalStatus.PENDING,
    },
    {
        "id": get_uuid("learning_plan_2"),
        "company_id": DEMO_COMPANY_ID,
        "employee_id": get_uuid("employee_9"),
        "current_role": "Sales Rep",
        "target_role": "Sales Manager",
        "readiness_score": Decimal("45.00"),
        "skill_gap_analysis": {"missing": ["Leadership", "Budgeting"]},
        "learning_path_json": {
            "path": ["Watch sales leadership course", "Shadow Jordan"]
        },
        "estimated_roi": "Medium ROI: Internal promotion preparation.",
        "is_deleted": False,
        "version_number": 1,
        "previous_version_id": None,
        "human_review_required": True,
        "reviewed_by": None,
        "reviewed_at": None,
        "approval_status": ApprovalStatus.PENDING,
    },
]

training_records_data = [
    {
        "id": get_uuid("training_record_1"),
        "company_id": DEMO_COMPANY_ID,
        "employee_id": get_uuid("employee_5"),
        "plan_id": get_uuid("learning_plan_1"),
        "course_name": "Advanced Python Coding",
        "provider": "Coursera",
        "skill_targeted": "Python",
        "status": TrainingStatus.IN_PROGRESS,
        "progress_percent": Decimal("60.00"),
        "cost": Decimal("150.00"),
        "started_at": date(2026, 6, 1),
        "completed_at": None,
        "certificate_url": None,
        "is_deleted": False,
    },
    {
        "id": get_uuid("training_record_2"),
        "company_id": DEMO_COMPANY_ID,
        "employee_id": get_uuid("employee_5"),
        "plan_id": get_uuid("learning_plan_1"),
        "course_name": "FastAPI Basics",
        "provider": "Udemy",
        "skill_targeted": "FastAPI",
        "status": TrainingStatus.COMPLETED,
        "progress_percent": Decimal("100.00"),
        "cost": Decimal("50.00"),
        "started_at": date(2026, 5, 10),
        "completed_at": date(2026, 5, 20),
        "certificate_url": "http://example.com/cert/fastapi-basics",
        "is_deleted": False,
    },
    {
        "id": get_uuid("training_record_3"),
        "company_id": DEMO_COMPANY_ID,
        "employee_id": get_uuid("employee_6"),
        "plan_id": None,
        "course_name": "Introduction to QA Automation",
        "provider": "LinkedIn Learning",
        "skill_targeted": "QA Automation",
        "status": TrainingStatus.COMPLETED,
        "progress_percent": Decimal("100.00"),
        "cost": Decimal("0.00"),
        "started_at": date(2026, 4, 1),
        "completed_at": date(2026, 4, 5),
        "certificate_url": None,
        "is_deleted": False,
    },
]

interview_kits_data = [
    {
        "id": get_uuid("interview_kit_1"),
        "company_id": DEMO_COMPANY_ID,
        "job_role": "Software Engineer",
        "department": "Engineering",
        "experience_level": ExperienceLevel.MID,
        "duration_minutes": 60,
        "key_skills": {"skills": ["Python", "FastAPI"]},
        "interview_structure": {
            "parts": ["Intro (5m)", "Coding (45m)", "Wrap-up (10m)"]
        },
        "question_bank": {
            "questions": ["Explain ASGI vs WSGI.", "What is a python generator?"]
        },
        "evaluation_rubric": {"criteria": ["Code Quality", "Problem Solving"]},
        "panel_guide": "Guide for mid level python interviewers.",
        "is_template": True,
        "is_deleted": False,
        "version_number": 1,
        "previous_version_id": None,
        "human_review_required": True,
        "reviewed_by": None,
        "reviewed_at": None,
        "approval_status": ApprovalStatus.PENDING,
    },
    {
        "id": get_uuid("interview_kit_2"),
        "company_id": DEMO_COMPANY_ID,
        "job_role": "Recruiter",
        "department": "Human Resources",
        "experience_level": ExperienceLevel.SENIOR,
        "duration_minutes": 45,
        "key_skills": {"skills": ["Technical Sourcing", "Interview Coordination"]},
        "interview_structure": {
            "parts": ["Intro (5m)", "Behavioral (30m)", "Wrap-up (10m)"]
        },
        "question_bank": {
            "questions": [
                "Describe your technical sourcing process.",
                "How do you handle difficult panels?",
            ]
        },
        "evaluation_rubric": {"criteria": ["Sourcing depth", "Communication"]},
        "panel_guide": "Guide for recruiting team interviewers.",
        "is_template": True,
        "is_deleted": False,
        "version_number": 1,
        "previous_version_id": None,
        "human_review_required": True,
        "reviewed_by": None,
        "reviewed_at": None,
        "approval_status": ApprovalStatus.PENDING,
    },
]

audit_log_data = {
    "id": get_uuid("audit_log_seed"),
    "company_id": DEMO_COMPANY_ID,
    "user_id": None,
    "module": "seed",
    "action": "seed_demo_data",
    "entity_type": "system",
    "entity_id": "demo",
    "metadata_json": {"details": "Initial demo dataset initialized"},
    "ip_address": "127.0.0.1",
    "user_agent": "TalentForge AI Seeder",
}


# ─── Seeder Operations ────────────────────────────────────────────────────────


async def delete_demo_data(session: AsyncSession) -> dict[str, int]:
    """Delete seeded demo data using stable UUID lists in reverse dependency order."""
    deleted_counts = {}

    # 1. Audit Logs
    audit_uuid = get_uuid("audit_log_seed")
    res = await session.execute(delete(AuditLog).where(AuditLog.id == audit_uuid))
    deleted_counts["audit_logs"] = res.rowcount

    # 2. Training Records
    training_uuids = [get_uuid(f"training_record_{i}") for i in range(1, 4)]
    res = await session.execute(
        delete(TrainingRecord).where(TrainingRecord.id.in_(training_uuids))
    )
    deleted_counts["training_records"] = res.rowcount

    # 3. Learning Plans
    plan_uuids = [get_uuid(f"learning_plan_{i}") for i in range(1, 3)]
    res = await session.execute(
        delete(LearningPlan).where(LearningPlan.id.in_(plan_uuids))
    )
    deleted_counts["learning_plans"] = res.rowcount

    # 4. Retention Strategies
    strategy_uuids = [get_uuid("retention_strategy_1")]
    res = await session.execute(
        delete(RetentionStrategy).where(RetentionStrategy.id.in_(strategy_uuids))
    )
    deleted_counts["retention_strategies"] = res.rowcount

    # 5. Attrition Assessments
    attrition_uuids = [get_uuid(f"attrition_assessment_{i}") for i in range(1, 3)]
    res = await session.execute(
        delete(AttritionAssessment).where(AttritionAssessment.id.in_(attrition_uuids))
    )
    deleted_counts["attrition_assessments"] = res.rowcount

    # 6. Performance Reviews
    review_uuids = [get_uuid(f"performance_review_{i}") for i in range(1, 3)]
    res = await session.execute(
        delete(PerformanceReview).where(PerformanceReview.id.in_(review_uuids))
    )
    deleted_counts["performance_reviews"] = res.rowcount

    # 7. Onboarding Tasks
    task_uuids = [get_uuid(f"onboarding_task_{i}") for i in range(1, 6)]
    res = await session.execute(
        delete(OnboardingTask).where(OnboardingTask.id.in_(task_uuids))
    )
    deleted_counts["onboarding_tasks"] = res.rowcount

    # 8. Onboarding Plans
    onb_uuids = [get_uuid("onboarding_plan_1")]
    res = await session.execute(
        delete(OnboardingPlan).where(OnboardingPlan.id.in_(onb_uuids))
    )
    deleted_counts["onboarding_plans"] = res.rowcount

    # 9. Interview Kits
    kit_uuids = [get_uuid(f"interview_kit_{i}") for i in range(1, 3)]
    res = await session.execute(
        delete(InterviewKit).where(InterviewKit.id.in_(kit_uuids))
    )
    deleted_counts["interview_kits"] = res.rowcount

    # 10. Resumes
    resume_uuids = [get_uuid(f"resume_{i}") for i in range(1, 9)]
    res = await session.execute(delete(Resume).where(Resume.id.in_(resume_uuids)))
    deleted_counts["resumes"] = res.rowcount

    # 11. Candidates
    cand_uuids = [get_uuid(f"candidate_{i}") for i in range(1, 9)]
    res = await session.execute(delete(Candidate).where(Candidate.id.in_(cand_uuids)))
    deleted_counts["candidates"] = res.rowcount

    # 12. Job Descriptions
    jd_uuids = [get_uuid(f"jd_{i}") for i in range(1, 4)]
    res = await session.execute(
        delete(JobDescription).where(JobDescription.id.in_(jd_uuids))
    )
    deleted_counts["job_descriptions"] = res.rowcount

    # 13. Policy Documents
    policy_uuids = [get_uuid(f"policy_doc_{i}") for i in range(1, 3)]
    res = await session.execute(
        delete(PolicyDocument).where(PolicyDocument.id.in_(policy_uuids))
    )
    deleted_counts["policy_documents"] = res.rowcount

    # 14. Unset cyclic references in employees first
    emp_uuids = [get_uuid(f"employee_{i}") for i in range(1, 11)]
    await session.execute(
        update(Employee)
        .where(Employee.id.in_(emp_uuids))
        .values(manager_id=None, user_id=None)
    )

    # 15. Employees
    res = await session.execute(delete(Employee).where(Employee.id.in_(emp_uuids)))
    deleted_counts["employees"] = res.rowcount

    # 16. Users
    res = await session.execute(delete(User).where(User.id == DEMO_USER_ID))
    deleted_counts["users"] = res.rowcount

    # 17. Company
    res = await session.execute(delete(Company).where(Company.id == DEMO_COMPANY_ID))
    deleted_counts["companies"] = res.rowcount

    await session.flush()
    return deleted_counts


async def seed_data(session: AsyncSession, admin_password: str) -> dict[str, int]:
    """Seed demo datasets using direct models to support stable UUID overrides."""
    counts = {
        "companies": 0,
        "users": 0,
        "employees": 0,
        "candidates": 0,
        "resumes": 0,
        "job_descriptions": 0,
        "policy_documents": 0,
        "onboarding_plans": 0,
        "onboarding_tasks": 0,
        "performance_reviews": 0,
        "attrition_assessments": 0,
        "retention_strategies": 0,
        "learning_plans": 0,
        "training_records": 0,
        "interview_kits": 0,
        "audit_logs": 0,
    }

    # 1. Company
    comp = await session.get(Company, company_data["id"])
    if not comp:
        comp = Company(**company_data)
        session.add(comp)
        counts["companies"] += 1

    # 2. User
    usr = await session.get(User, user_data["id"])
    if not usr:
        user_payload = dict(user_data)
        user_payload["password_hash"] = hash_password(admin_password)
        usr = User(**user_payload)
        session.add(usr)
        counts["users"] += 1

    # 3. Employees (without manager_id first)
    for emp_dict in employees_data:
        emp = await session.get(Employee, emp_dict["id"])
        if not emp:
            data = dict(emp_dict)
            data["manager_id"] = None
            emp = Employee(**data)
            session.add(emp)
            counts["employees"] += 1

    await session.flush()

    # Update manager_id links on employees in second pass (only if manager_id is currently None)
    for emp_dict in employees_data:
        emp = await session.get(Employee, emp_dict["id"])
        if (
            emp
            and emp.manager_id is None
            and employee_managers[emp_dict["id"]] is not None
        ):
            emp.manager_id = employee_managers[emp_dict["id"]]
            session.add(emp)

    # 4. Candidates
    for cand_dict in candidates_data:
        cand = await session.get(Candidate, cand_dict["id"])
        if not cand:
            cand = Candidate(**cand_dict)
            session.add(cand)
            counts["candidates"] += 1

    # 5. Resumes
    for res_dict in resumes_data:
        res = await session.get(Resume, res_dict["id"])
        if not res:
            res = Resume(**res_dict)
            session.add(res)
            counts["resumes"] += 1

    # 6. Job Descriptions
    for jd_dict in job_descriptions_data:
        jd = await session.get(JobDescription, jd_dict["id"])
        if not jd:
            jd = JobDescription(**jd_dict)
            session.add(jd)
            counts["job_descriptions"] += 1

    # 7. Policy Documents
    for pol_dict in policy_documents_data:
        pol = await session.get(PolicyDocument, pol_dict["id"])
        if not pol:
            pol = PolicyDocument(**pol_dict)
            session.add(pol)
            counts["policy_documents"] += 1

    # 8. Onboarding Plans
    for plan_dict in onboarding_plans_data:
        plan = await session.get(OnboardingPlan, plan_dict["id"])
        if not plan:
            plan = OnboardingPlan(**plan_dict)
            session.add(plan)
            counts["onboarding_plans"] += 1

    # 9. Onboarding Tasks
    for task_dict in onboarding_tasks_data:
        task = await session.get(OnboardingTask, task_dict["id"])
        if not task:
            task = OnboardingTask(**task_dict)
            session.add(task)
            counts["onboarding_tasks"] += 1

    # 10. Performance Reviews
    for rev_dict in performance_reviews_data:
        rev = await session.get(PerformanceReview, rev_dict["id"])
        if not rev:
            rev = PerformanceReview(**rev_dict)
            session.add(rev)
            counts["performance_reviews"] += 1

    # 11. Attrition Assessments
    for assess_dict in attrition_assessments_data:
        assess = await session.get(AttritionAssessment, assess_dict["id"])
        if not assess:
            assess = AttritionAssessment(**assess_dict)
            session.add(assess)
            counts["attrition_assessments"] += 1

    # 12. Retention Strategies
    for strat_dict in retention_strategies_data:
        strat = await session.get(RetentionStrategy, strat_dict["id"])
        if not strat:
            strat = RetentionStrategy(**strat_dict)
            session.add(strat)
            counts["retention_strategies"] += 1

    # 13. Learning Plans
    for lplan_dict in learning_plans_data:
        lplan = await session.get(LearningPlan, lplan_dict["id"])
        if not lplan:
            lplan = LearningPlan(**lplan_dict)
            session.add(lplan)
            counts["learning_plans"] += 1

    # 14. Training Records
    for tr_dict in training_records_data:
        tr = await session.get(TrainingRecord, tr_dict["id"])
        if not tr:
            tr = TrainingRecord(**tr_dict)
            session.add(tr)
            counts["training_records"] += 1

    # 15. Interview Kits
    for kit_dict in interview_kits_data:
        kit = await session.get(InterviewKit, kit_dict["id"])
        if not kit:
            kit = InterviewKit(**kit_dict)
            session.add(kit)
            counts["interview_kits"] += 1

    # 16. Audit Log
    aud = await session.get(AuditLog, audit_log_data["id"])
    if not aud:
        aud = AuditLog(**audit_log_data)
        session.add(aud)
        counts["audit_logs"] += 1

    await session.flush()
    return counts


async def main() -> None:
    """Main execution entry point representing seeder safeguards and setup."""
    parser = argparse.ArgumentParser(description="Seed TalentForge AI demo data.")
    parser.add_argument(
        "--reset-demo-data",
        action="store_true",
        help="Reset and reseed stable demo data.",
    )
    parser.add_argument(
        "--allow-remote-development",
        action="store_true",
        help="Allow seeding against remote Neon development databases.",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("TalentForge AI — Demo Data Seeder")
    print("=" * 60)
    print()

    # 1. DEMO_ADMIN_PASSWORD verification
    demo_admin_password = os.environ.get("DEMO_ADMIN_PASSWORD")
    if not demo_admin_password:
        print(
            "Error: DEMO_ADMIN_PASSWORD environment variable is missing or empty. Seeding aborted.",
            file=sys.stderr,
        )
        sys.exit(1)

    # 2. Environment protection checks
    app_env = (settings.app_env or "").lower().strip()
    if app_env == "production":
        print(
            "Error: Seeding is completely blocked in production environments.",
            file=sys.stderr,
        )
        sys.exit(1)

    if app_env not in ("development", "testing"):
        print(
            f"Error: Unknown application environment '{settings.app_env}'. Seeding aborted.",
            file=sys.stderr,
        )
        sys.exit(1)

    # 3. Connection parsing and masking
    db_url = settings.database_url
    if not db_url:
        print(
            "Error: DATABASE_URL settings is empty. Seeding aborted.",
            file=sys.stderr,
        )
        sys.exit(1)

    parsed_url = urlparse(db_url)
    hostname = parsed_url.hostname or ""
    masked_url = f"Host: {hostname or 'unknown'}, Database: {parsed_url.path.lstrip('/') or 'unknown'}"
    print(f"Target Database: {masked_url}")

    # 4. Remote development verification
    if hostname not in ("localhost", "127.0.0.1", ""):
        if not args.allow_remote_development:
            print(
                "Error: Seeding to a remote database requires the '--allow-remote-development' flag.",
                file=sys.stderr,
            )
            sys.exit(1)

    # 5. DB Transaction wrapper
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                if args.reset_demo_data:
                    print("Resetting existing demo dataset records...")
                    deleted = await delete_demo_data(session)
                    print(
                        f"  Cleaned: Company={deleted.get('companies', 0)}, "
                        f"Employees={deleted.get('employees', 0)}, "
                        f"Candidates={deleted.get('candidates', 0)}, "
                        f"Workflows={deleted.get('onboarding_plans', 0) + deleted.get('learning_plans', 0) + deleted.get('performance_reviews', 0)}"
                    )

                print("Seeding demo tenant database...")
                created = await seed_data(session, demo_admin_password)

                print()
                print("Seeding completed successfully:")
                print(f"  Companies created: {created['companies']}")
                print(f"  Users created:     {created['users']}")
                print(f"  Employees created: {created['employees']}")
                print(f"  Candidates:        {created['candidates']}")
                print(f"  Resumes:           {created['resumes']}")
                print(f"  Job Descriptions:  {created['job_descriptions']}")
                print(f"  Policy Documents:  {created['policy_documents']}")
                print(f"  Onboarding Plans:  {created['onboarding_plans']}")
                print(f"  Onboarding Tasks:  {created['onboarding_tasks']}")
                print(f"  Reviews:           {created['performance_reviews']}")
                print(f"  Assessments:       {created['attrition_assessments']}")
                print(f"  Strategies:        {created['retention_strategies']}")
                print(f"  Learning Plans:    {created['learning_plans']}")
                print(f"  Training Records:  {created['training_records']}")
                print(f"  Interview Kits:    {created['interview_kits']}")
                print(f"  Audit Logs:        {created['audit_logs']}")

    except Exception as exc:
        print(f"\nSeeding FAILED with exception: {exc}", file=sys.stderr)
        print("All changes have been rolled back.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
