# TalentForge AI

> **Enterprise-Grade AI-Powered HR Intelligence Platform**
> Multi-tenant SaaS · FastAPI · Neon PostgreSQL · pgvector · NVIDIA NIM

---

## 1. Project Overview

TalentForge AI is a functionality-first, enterprise-oriented Human Resources intelligence SaaS platform. The system is designed to streamline critical HR operations by combining server-side business rules, local machine learning models, RAG (Retrieval-Augmented Generation) policy search, and advanced LLM (Large Language Model) reasoning.

This application is designed as a modular monolith optimized for clean separation of concerns, high performance, strict multi-tenant data isolation, and deployment to cloud architectures.

---

## 2. Current Completion Status

The project is currently at the end of **Phase 2 — Database & Multi-Tenant Foundation**.
- **Database Schema**: 17 tables mapped via SQLAlchemy 2.0 Declarative ORM models.
- **Tenant Isolation**: Database-level isolation using `company_id` columns and compound indexes, managed authoritatively via Tenant Repository wrappers.
- **Security Foundation**: Bcrypt-hashed password management, append-only logs for system records, and sensitive salary deferred loading.
- **Seeding & Idempotency**: Namespace-based stable UUID seeder for deterministic data initialization.
- **Testing Coverage**: 100% passing test suite covering constraints, cascades, repository scopes, and seeder isolation.

*Note: Phase 3 (AI Infrastructure) and Phase 4 (RAG Infrastructure) are pending.*

---

## 3. Technology Stack

- **Backend Framework**: FastAPI (Python 3.11+)
- **Database**: Neon PostgreSQL (Relational) + pgvector (Vector search)
- **Object Relational Mapper (ORM)**: SQLAlchemy 2.0 (declarative mapping)
- **Database Migrations**: Alembic
- **Validation**: Pydantic v2 (Request/Response schemas)
- **AI Integrations**: NVIDIA NIM + LangChain (with `nvidia/nv-embed-v1` embeddings)
- **ML / Analytics**: Pandas, NumPy, Scikit-learn
- **Security**: passlib + bcrypt (password hashing), Python-jose (JWT)
- **Templating / UI**: Jinja2 + Tailwind CSS + Vanilla JavaScript (internal dashboard styling)
- **Testing**: pytest (with anyio async backend)
- **Formatting / Linting**: Black, Ruff, isort

---

## 4. Architecture Overview

TalentForge AI enforces a strict multi-layered backend flow:

```
Routes (HTTP) ──> Schemas (Pydantic) ──> Services (Business Logic)
                                                  │
                ┌─────────────────────────────────┼──────────────────────────────┐
                ▼                                 ▼                              ▼
    Repositories (SQLAlchemy)               AI Layer (NVIDIA NIM)        ML Layer (Scikit-learn)
                │                                 │                              │
                ▼                                 ▼                              ▼
    PostgreSQL (Neon / pgvector)             LLM Cache / Logs              Pandas Analytics
```

- **Routes**: Handle request/response mappings. No business logic or DB calls are allowed here.
- **Services**: Orchestrate the workflows, clean data, and call repositories or AI/ML components.
- **Repositories**: Encapsulate all database operations.
  - `BaseRepository[ModelType]`: Low-level database helper functions.
  - `TenantRepository[ModelType]`: Inherits from `BaseRepository` and forces strict `company_id` filtering on all operations.

---

## 5. Project Structure

```text
TalentForge-AI/
├── app/
│   ├── main.py                # FastAPI entrypoint
│   ├── core/
│   │   ├── config.py          # Pydantic Settings management
│   │   ├── security.py        # Password hashing & security headers
│   │   ├── rate_limiter.py    # Request limits middleware
│   │   ├── logging_config.py  # Structured JSON logging
│   │   └── errors.py          # Custom exceptions & handlers
│   ├── db/
│   │   ├── base.py            # SQLAlchemy base class
│   │   ├── session.py         # Sessionmaker & connections
│   │   ├── models.py          # Alembic metadata registry
│   │   ├── models/            # Package containing ORM modular models
│   │   └── repositories/      # Repository layer implementation
│   ├── schemas/               # Input/Output validation schemas
│   ├── services/              # Business logic modules (Resume screening, RAG, JD, etc.)
│   ├── routes/                # FastAPI router endpoints
│   ├── templates/             # Jinja2 HTML templates
│   └── static/                # Compiled CSS, JS, and images
├── alembic/                   # Schema migrations package
├── docs/                      # Technical specifications and reports
│   └── phase_reports/         # Completed subphase reports
├── tests/                     # Unit and integration test suite
├── scripts/
│   ├── seed_demo_data.py      # Idempotent demo seeder
│   └── validate_env.py        # Settings validation script
├── uploads/                   # Temporary file uploads (.gitkeep)
├── exports/                   # Exported CSV, Excel, PDF (.gitkeep)
├── .env.example               # Placeholder values for environment variables
├── .gitignore                 # Excludes .env, caches, and build artifacts
├── requirements.txt           # Python packages manifest
├── render.yaml                # Infrastructure configuration for Render
├── PROJECT.md                 # Index of directories and files
└── README.md                  # This file
```

---

## 6. Environment Setup

### Prerequisites
- Python 3.11+
- PostgreSQL database with pgvector extension enabled

### Setup Instructions
1. **Clone the Repository** and navigate to the project directory:
   ```bash
   cd "TalentForge AI"
   ```

2. **Initialize Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup Environment File**:
   Copy `.env.example` to `.env` and configure your credentials:
   ```bash
   cp .env.example .env
   ```

---

## 7. Configuration (.env.example)

Configure the following variables in your `.env` file:

```env
# ── Application ───────────────────────────────────────────────────────────────
APP_NAME=TalentForge AI
APP_ENV=development
SECRET_KEY=change-me-to-a-random-64-char-string

# ── Database ──────────────────────────────────────────────────────────────────
# Connection string (sslmode=require is mandatory for Neon)
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST/DBNAME?sslmode=require

# ── NVIDIA NIM (or other Model Provider) ──────────────────────────────────────
NVIDIA_API_KEY=nvapi-your-key-here
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1

# Model identifiers
NVIDIA_SMALL_MODEL=meta/llama-3.1-8b-instruct
NVIDIA_LARGE_MODEL=meta/llama-3.1-70b-instruct
NVIDIA_ADVANCED_MODEL=nvidia/llama-3.3-nemotron-super-49b-v1.5
NVIDIA_EMBEDDING_MODEL=nvidia/nv-embed-v1

# AI Client Configuration (provider-agnostic)
AI_TIMEOUT_SECONDS=30
AI_MAX_RETRIES=3
AI_MAX_TOKENS_SMALL=1024
AI_MAX_TOKENS_LARGE=2048
AI_MAX_TOKENS_ADVANCED=4096

# ── CORS ──────────────────────────────────────────────────────────────────────
ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

# ── File Upload ───────────────────────────────────────────────────────────────
MAX_UPLOAD_SIZE_MB=10

# ── AI Response Cache ─────────────────────────────────────────────────────────
CACHE_TTL_HOURS=24

# ── Rate Limiting ─────────────────────────────────────────────────────────────
RATE_LIMIT_PUBLIC=20/minute
RATE_LIMIT_AI=10/minute
RATE_LIMIT_AUTH=5/minute

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_LEVEL=INFO

# ── Demo / Multi-Tenant Placeholder ──────────────────────────────────────────
DEMO_COMPANY_ID=00000000-0000-0000-0000-000000000001
DEMO_USER_ID=00000000-0000-0000-0000-000000000001
DEMO_ADMIN_PASSWORD=change-me-to-a-secure-development-password
```

---

## 8. Run Commands

### Environment Variable Verification
Verify that the configuration does not contain missing variables or placeholder values:
```bash
python scripts/validate_env.py
```

### Database Migrations (Alembic)
Run migrations to initialize or upgrade the database:
```bash
# Verify migration heads
PYTHONPATH=. .venv/bin/alembic heads

# Run database upgrades to the head revision
PYTHONPATH=. .venv/bin/alembic upgrade head

# Perform schema downgrade safety validation
PYTHONPATH=. .venv/bin/alembic downgrade e61edd53de79
PYTHONPATH=. .venv/bin/alembic upgrade head
```

### Seeding Demo Data
To seed the database with stable, deterministic mock tenant values:
```bash
# Ordinary seeding
PYTHONPATH=. .venv/bin/python scripts/seed_demo_data.py

# Reseeding / resetting existing data (Safe and idempotent)
PYTHONPATH=. .venv/bin/python scripts/seed_demo_data.py --reset-demo-data

# Seeding to remote database
PYTHONPATH=. .venv/bin/python scripts/seed_demo_data.py --allow-remote-development
```

### Testing Commands
Execute the test suite using `pytest`:
```bash
PYTHONPATH=. .venv/bin/pytest -v
```

### Formatting, Linting, and Sorting
Apply and verify style guidelines across Python files:
```bash
# Programmatic import sorting
.venv/bin/isort app scripts tests alembic
.venv/bin/isort --check-only app scripts tests alembic

# Code formatting
.venv/bin/black app scripts tests alembic
.venv/bin/black --check app scripts tests alembic

# Code linting
.venv/bin/ruff check app scripts tests alembic
```

---

## 9. Security Notes

- **Secrets Management**: Secrets are stored only in the environment or `.env` and are loaded via Pydantic Settings. The `.env` file is explicitly ignored in `.gitignore`.
- **Tenant Partitioning**: All database records (excluding shared settings) are linked to a specific company using `company_id`. Repository queries strictly filter by `company_id` to prevent cross-tenant exposure.
- **Compliance Logging**: System audit logs (`audit_logs`) and AI history (`ai_invocation_histories`) are write-protected (read and create operations only; updates or deletes are forbidden).
- **Password Security**: Password hashes are cryptographically encrypted using bcrypt. Plain-text passwords are never stored in the database.
- **Salary Data**: Confidentially stored salaries utilize SQLAlchemy `deferred` loading to prevent columns from loading unless requested explicitly.
- **No Secrets Committed**: Validated that no development database credentials or sensitive API keys are stored in the codebase or version control.

---

## 10. Deployment Target

The platform is designed to be deployed to:
- **FastAPI Backend**: Render Web Service
- **Database Layer**: Neon PostgreSQL (with connection pooling limits configured in `app/db/session.py` to prevent free tier overload)
- **Vector Search**: Neon pgvector extension

---

## 11. Roadmap

- [x] **Phase 0** — Architecture & Planning
- [x] **Phase 1** — Project Foundation (FastAPI skeleton, Database configuration)
- [x] **Phase 2** — Database & Multi-Tenant Foundation (Models, Repositories, Seeder)
- [ ] **Phase 3** — AI Infrastructure (NVIDIA NIM Model Routing, Cache System)
- [ ] **Phase 4** — RAG Infrastructure (PDF parsing, Chunks indexing, Policy Chatbot)
- [ ] **Phase 5** — Core HR Modules (Resume Screening, Job Description Generator, Onboarding, etc.)
- [ ] **Phase 6** — Dashboard & Analytics (KPI counters, Chart.js integrations)
- [ ] **Phase 7** — Reports & Export System (Excel, PDF, CSV formatting)
- [ ] **Phase 8** — Testing & QA
- [ ] **Phase 9** — Cloud Deployment
- [ ] **Phase 10** — Authentication & RBAC Post-V1 (Deferred JWT)

---

## 12. Current Limitations

- **Authentication**: JWT token verification and RBAC routes are deferred until Phase 10. The system uses a mock `DemoUser` context injected via FastAPI dependencies.
- **External AI/API Calls**: Currently mocked or unimplemented until Phase 3 and Phase 4.
- **Frontend Pages**: Dashboard and module screens are templates only, pending backend service integration in subsequent roadmap phases.
