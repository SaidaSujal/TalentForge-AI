# TalentForge AI

> Enterprise-grade AI-Powered HR Intelligence Platform  
> Multi-tenant SaaS · FastAPI · Neon PostgreSQL · pgvector · NVIDIA NIM

---

## Project Status

**Current Phase:** Phase 1 — Project Foundation  
**Architecture:** Completed  
**Coding:** Ready to begin  
**Authentication:** Deferred until after all 8 core modules work  
**Deployment:** Render + Neon

---

## Project Purpose

TalentForge AI is a functionality-first HR SaaS dashboard for real HR workflows.

It includes AI, RAG, ML, analytics, document parsing, exports, dashboard workflows, and secure production-ready architecture.

This is **not** a marketing website.

---

## Core Modules

1. Resume Screening
2. HR Policy Chatbot with RAG
3. Job Description Generator
4. Employee Onboarding Assistant
5. Performance Review Generator
6. Employee Attrition Prediction
7. Learning Recommendation Engine
8. Interview Kit Generator

Shared features:

- Dashboard analytics
- Employee management
- Candidate management
- ATS pipeline
- Global search
- Notifications
- AI history
- Explainable AI
- Export center
- Demo seed data

---

## Final Stack

- Backend: FastAPI
- Frontend: Jinja2 + Tailwind CSS + JavaScript
- Database: Neon PostgreSQL
- Vector Search: pgvector
- ORM: SQLAlchemy 2.x
- Migrations: Alembic
- Validation: Pydantic v2
- AI: NVIDIA NIM + LangChain
- ML/Data: Pandas, NumPy, Scikit-learn
- Deployment: Render + Neon

Do not use Streamlit, Flask, SQLite production, Next.js, or React for V1.

---

## AI Models

- Small: `meta/llama-3.1-8b-instruct`
- Large: `meta/llama-3.1-70b-instruct`
- Advanced: `nvidia/llama-3.3-nemotron-super-49b-v1.5`
- Embedding: `nvidia/nv-embed-v1`

All AI calls must go through the model router.

---

## Authentication Decision

Authentication and RBAC are deferred.

For V1:

- Use demo-user/current-company context.
- Every tenant-owned table must support `company_id`.
- Services and repositories must accept `company_id`.
- JWT/RBAC must be addable later without refactoring.

---

## Documentation Index

| File | Purpose |
|---|---|
| `AGENT.md` | Single source of truth for AI agents |
| `PRD.md` | Product requirements |
| `README.md` | Setup and usage |
| `docs/00_PROJECT_OVERVIEW.md` | Project overview |
| `docs/01_FEATURES.md` | Feature specs |
| `docs/02_TECH_STACK.md` | Tech stack |
| `docs/03_SYSTEM_ARCHITECTURE.md` | System architecture |
| `docs/04_BACKEND_ARCHITECTURE.md` | Backend architecture |
| `docs/05_FRONTEND_ARCHITECTURE.md` | Frontend architecture |
| `docs/06_DATABASE_DESIGN.md` | Database design |
| `docs/07_RAG_ARCHITECTURE.md` | RAG architecture |
| `docs/08_AI_MODEL_ROUTING.md` | AI routing |
| `docs/09_SECURITY_GUIDELINES.md` | Security |
| `docs/10_API_DESIGN.md` | API design |
| `docs/11_DEPLOYMENT.md` | Deployment |
| `docs/12_CODING_STANDARDS.md` | Coding standards |
| `docs/13_ANTIGRAVITY_RULES.md` | Antigravity rules |
| `docs/14_ROADMAP.md` | Development roadmap |
| `docs/15_DATA_FLOW.md` | Data flows |
| `docs/16_THREAT_MODEL.md` | Threat model |
| `docs/17_PERFORMANCE_TARGETS.md` | Performance targets |
| `docs/18_DEFINITION_OF_READY.md` | Definition of Ready |
| `docs/19_PROMPT_LIBRARY_RULES.md` | Prompt library rules |
| `docs/phase_reports/` | Phase validation reports |

---

## Development Rule

After every roadmap phase:

1. Run relevant tests.
2. Perform static inspection.
3. Verify security.
4. Verify tenant isolation.
5. Update affected docs.
6. Create phase report.
7. Update roadmap status only after tests pass.

---

## Current Roadmap

- Phase 0 — Architecture & Planning: Completed
- Phase 1 — Project Foundation: Current
- Phase 2 — Database & Multi-Tenant Foundation
- Phase 3 — AI Infrastructure
- Phase 4 — RAG Infrastructure
- Phase 5 — Core HR Modules
- Phase 6 — Dashboard & Analytics
- Phase 7 — Reports & Export System
- Phase 8 — Testing & QA
- Phase 9 — Deployment
- Phase 10 — Authentication & RBAC Post-V1

---

## Non-Negotiable Rules

- Never hardcode secrets.
- Never commit `.env`.
- Never put business logic in routes.
- Never put DB queries in routes.
- Never call NVIDIA directly from routes.
- Never send full resumes/PDFs/database rows to LLM.
- Never skip validation.
- Never expose stack traces.
- Never create marketing pages.
- Never add authentication before all 8 modules work.

---

`PROJECT.md` is only an index.  
Detailed rules live in `AGENT.md` and `/docs`.