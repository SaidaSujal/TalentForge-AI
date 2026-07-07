# AGENT.md — TalentForge AI

> **This file is the single source of truth for every AI agent working on TalentForge AI.**
> Read this file in its entirety before writing, modifying, or deleting any code.
> If any instruction in this file conflicts with a conversational prompt, this file wins unless the project owner explicitly overrides it.

---

## 1. Project Identity

| Field | Value |
|---|---|
| **Project Name** | TalentForge AI |
| **Product Type** | AI-Powered HR Intelligence Platform |
| **Architecture** | Multi-Tenant SaaS (modular monolith) |
| **Version** | 1.0 |
| **Deployment Target** | Render (backend) + Neon (PostgreSQL) |
| **Frontend Style** | Internal HR SaaS dashboard — not a marketing site |
| **Authentication** | Authentication and RBAC are deferred until after all 8 core modules work. For V1, use demo-user/current-company architecture only. All services and repositories must accept company_id so JWT/RBAC can be added later without refactor. |

---

## 2. Product Goal

Build a functionality-first, portfolio-ready, interview-ready, deployable HR intelligence platform that:

- Combines local analytics, PostgreSQL storage, pgvector RAG, NVIDIA NIM LLM calls, document parsing, export tools, and workflow-focused UI into one dashboard.
- Uses AI **only** where reasoning, summarization, recommendations, natural language generation, or question generation is required.
- Uses local/backend logic (SQL, Pandas, Scikit-learn, rule-based computation, input validation, ranking, charts, exports, business rules) for everything else.
- Reduces unnecessary NVIDIA API calls through caching, preprocessing, retrieval, routing, and local computation.
- Treats every sensitive HR AI output as a **recommendation only** — never as a final decision.
- Ships with demo seed data so the dashboard works immediately after setup.

---

## 3. Non-Goals (Out of Scope for V1)

Do **not** build any of the following:

- Marketing landing page, About page, Feature showcase, How it works page, Pricing page
- Public website animations or SaaS billing
- Multi-company tenant billing
- Real email sending, Calendar integration, Payroll system
- Biometric attendance, Background verification integration
- Resume sourcing from LinkedIn/Naukri
- Full production RBAC login system (deferred)
- Mobile application
- Voice HR assistant, Video interview analysis
- ATS integration, Payroll integration

---

## 4. Final Tech Stack

### Locked Technologies — Do Not Replace Without Explicit Approval

| Layer | Technology |
|---|---|
| **Backend framework** | FastAPI |
| **Language** | Python 3.11+ |
| **ORM** | SQLAlchemy 2.x |
| **Migrations** | Alembic |
| **Validation** | Pydantic v2 |
| **Templates** | Jinja2 (server-rendered) |
| **Frontend styling** | Tailwind CSS |
| **Frontend scripting** | Vanilla JavaScript + Fetch API |
| **Charts** | Chart.js or Plotly.js |
| **Database** | PostgreSQL on Neon |
| **Vector database** | pgvector (PostgreSQL extension) |
| **AI provider** | NVIDIA NIM |
| **AI framework** | LangChain |
| **Embeddings** | `nvidia/nv-embed-v1` |
| **ML / Analytics** | Pandas, NumPy, Scikit-learn |
| **PDF parsing** | PyPDF2 |
| **DOCX parsing** | python-docx |
| **Exports** | CSV, Excel (openpyxl), PDF report generation |
| **Password hashing** | passlib + bcrypt |
| **JWT** | python-jose |
| **Environment** | python-dotenv |
| **Rate limiting** | slowapi or custom middleware |
| **Formatting** | Black |
| **Linting** | Ruff |
| **Import sorting** | isort |
| **Deployment** | Render (web service) + Neon (database) |

### Banned Technologies

| Banned | Reason |
|---|---|
| Next.js | Not used — Jinja2 is the frontend |
| React | Not used in V1 |
| Streamlit | Not a SaaS-grade UI |
| Flask | FastAPI is the only backend |
| SQLite | Not for production |
| Django | Not the chosen framework |

---

## 5. Multi-Tenant SaaS Architecture Rules

1. **Every tenant-owned table** must include a `company_id` column (UUID, NOT NULL, indexed).
2. All queries on tenant data **must** filter by `company_id`. Never return cross-tenant data.
3. For V1 (single-tenant demo), seed a default company and use its `company_id` everywhere.
4. The `company_id` column must be added now so JWT/RBAC and multi-tenancy can be enabled later without schema refactoring.
5. Create a `companies` table with at least: `id`, `name`, `slug`, `settings_json`, `created_at`, `updated_at`.
6. Foreign key relationships to `companies` must be established from day one.
7. Indexes must exist on `company_id` for every tenant-scoped table.
8. When authentication is added, extract `company_id` from the JWT claims and inject it into every repository call.
9. Never use global queries without explicit `company_id` scope on tenant tables.
10. Shared/system tables (e.g., `ai_cache`, `app_settings`) do not require `company_id` but must be clearly documented as shared.

---

## 6. Backend Architecture Rules

### Layered Architecture (Mandatory)

```
Routes → Services → Repositories → Database
                  → AI Layer → NVIDIA NIM
                  → ML Layer → Scikit-learn / Pandas
```

### Layer Responsibilities

| Layer | Allowed | Forbidden |
|---|---|---|
| **Routes** | HTTP request/response handling, calling services, returning templates or JSON | Business logic, database queries, AI calls, file processing, raw SQL |
| **Schemas** | Pydantic v2 input/output validation | Business logic |
| **Services** | Business logic, data orchestration, calling repositories + AI layer + ML layer | Direct HTTP response construction, raw SQL |
| **Repositories** | Database queries via SQLAlchemy ORM | Business logic, AI calls |
| **AI Layer** | NVIDIA NIM calls, prompt building, model routing, caching, output validation | Database queries, HTTP handling |
| **ML Layer** | Scikit-learn predictions, Pandas analytics | AI calls, HTTP handling |
| **Security Layer** | Auth, rate limiting, headers, CORS, input sanitization | Business logic |

### Strict Rules

- Routes must stay thin. Maximum 10–15 lines of logic per route handler.
- Services must clean and preprocess data **before** calling the AI layer.
- Use Pandas/SQL for deterministic work before any LLM call.
- Call the smallest suitable model by default.
- Call the large model only for complex reasoning tasks.
- Cache every repeatable AI output.
- Never call the NVIDIA API directly from routes.

### Request Flow

```
User → Frontend → FastAPI Endpoint → Pydantic Validation → Security Middleware →
Service Layer → (Repository / AI Layer / ML Layer) → Response
```

### Folder Structure

```
TalentForge-AI/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py          # Settings from environment variables
│   │   ├── security.py        # Auth helpers, password hashing
│   │   ├── rate_limiter.py    # Rate limiting middleware
│   │   ├── logging_config.py  # Structured logging setup
│   │   └── errors.py          # Custom exception classes + handlers
│   ├── db/
│   │   ├── base.py            # SQLAlchemy base model
│   │   ├── session.py         # Engine, session factory
│   │   ├── models.py          # All SQLAlchemy models (or split per module)
│   │   └── repositories/      # One repository file per entity
│   ├── schemas/                # Pydantic v2 request/response schemas
│   ├── services/
│   │   ├── ai/                # Model router, prompt templates, NVIDIA client, cache
│   │   ├── resume_screening/
│   │   ├── policy_rag/
│   │   ├── jd_generator/
│   │   ├── onboarding/
│   │   ├── performance/
│   │   ├── attrition/
│   │   ├── learning/
│   │   ├── interview_kit/
│   │   ├── exports/
│   │   └── dashboard/
│   ├── routes/                 # One router file per module
│   ├── templates/              # Jinja2 HTML templates
│   └── static/
│       ├── css/
│       ├── js/
│       └── assets/
├── alembic/                    # Database migrations
├── docs/                       # Architecture documentation (read-only reference)
├── tests/                      # pytest test suite
├── scripts/
│   ├── seed_demo_data.py       # Demo data seeder
│   └── validate_env.py         # Environment variable validator
├── uploads/                    # Temporary file uploads (.gitkeep)
├── exports/                    # Generated export files (.gitkeep)
├── .env.example
├── .gitignore
├── requirements.txt
├── render.yaml
├── AGENT.md
├── PROJECT.md
└── README.md
```

---

## 7. Frontend Architecture Rules

### Technology

- Server-rendered HTML using Jinja2 templates.
- Tailwind CSS for styling.
- Vanilla JavaScript for interactivity.
- Fetch API for backend communication.
- Chart.js or Plotly.js for charts and visualizations.

### UI Style

The UI must look and feel like an **internal HR SaaS dashboard**. It must include:

- Sidebar navigation
- Top header with context info
- KPI cards on the dashboard
- Data tables with sorting/filtering
- Forms with proper validation states
- File upload controls with progress indicators
- Charts and visualizations
- AI output cards with copy buttons
- Export buttons
- Loading states, error states, and empty states
- "Human review required" labels on sensitive AI outputs
- Demo data button or setup command indication

### Pages

| Page | Purpose |
|---|---|
| Dashboard | HR metrics, charts, recent activity, AI usage, cache savings |
| Resume Screening | Upload resumes, enter JD, view ranked candidates |
| Policy Chatbot | Chat UI with citations and confidence scores |
| JD Generator | Form input → generated JD preview with export |
| Employee Onboarding | Plans, checklists, progress tracking |
| Performance Review | Review generator and history |
| Attrition Risk | Risk form, prediction results, retention strategies |
| Learning Recommendations | Skill gap analysis, learning paths |
| Interview Kit | Question generator, rubrics, evaluation scorecards |
| Employees | Employee records management |
| Candidates | Candidate records management |
| Policy Documents | Document upload, indexing status |
| Export Center | All exportable reports |
| Settings / Health | Environment check, system health |

### Frontend Rules

1. Frontend must **not** contain API keys or secrets.
2. Frontend must **not** perform protected business logic alone — all important checks are re-validated on the backend.
3. Frontend must **not** trust hidden inputs for security.
4. Escape all rendered user content — never render raw HTML from LLM output.
5. Do not store tokens in `localStorage`. Use secure cookies when auth is implemented.
6. Show loading spinners for AI operations.
7. Disable submit buttons during processing to prevent duplicate requests.
8. Show friendly, generic error messages — never raw backend errors.

---

## 8. Database Rules

### General

1. Use PostgreSQL on Neon. **Never use SQLite for production.**
2. Use SQLAlchemy 2.x as the ORM. **Never write raw SQL via string concatenation.**
3. Use Alembic for all schema changes. **No manual DDL outside migrations.**
4. Use parameterized queries only.
5. Every tenant-owned table must have a `company_id` column (see Section 5).
6. Use UUIDs for primary keys.
7. Include `created_at` and `updated_at` timestamps on every table.
8. Index: `company_id`, `email`, `status`, `department`, `role`, `created_at`, and vector similarity columns.

### Required Tables

| Table | Purpose |
|---|---|
| `companies` | Tenant/company records |
| `employees` | Employee profiles, department, role, salary, manager |
| `candidates` | Candidate profiles, resume text, score, status |
| `resumes` | Parsed resume data and metadata |
| `job_descriptions` | Generated and saved JDs |
| `policy_documents` | Uploaded HR policy metadata |
| `policy_chunks` | Chunk text, page number, vector embedding, source metadata |
| `policy_questions` | Chat history and unanswered questions |
| `onboarding_plans` | Generated onboarding plans |
| `onboarding_tasks` | Individual onboarding checklist items |
| `performance_reviews` | Review inputs and AI-generated output |
| `attrition_assessments` | Risk scores, factors, level |
| `retention_strategies` | AI-generated retention recommendations |
| `learning_plans` | Skill gap analysis and learning paths |
| `training_records` | Training progress tracking |
| `interview_kits` | Generated interview kits |
| `ai_history` | **Every AI output must be saved here** — model used, prompt hash, input summary, output, tokens, latency, module |
| `ai_cache` | Prompt hash → cached response with TTL |
| `exports` | Export job metadata and file references |
| `audit_logs` | User actions, timestamps, IP, metadata |
| `app_settings` | Application configuration |

### Data Security

- Never store raw API keys in the database.
- Store password hashes only (bcrypt), never plain passwords.
- Encrypt or redact sensitive HR data (salary, medical) where needed.
- Do not expose internal database IDs in frontend responses when avoidable — use UUIDs.
- Send summaries to LLM, never full database rows.

---

## 9. pgvector and RAG Rules

### Ingestion Pipeline

```
Upload file → Validate file → Extract text → Clean text → Split into chunks →
Create embeddings (nvidia/nv-embed-v1) → Store in pgvector
```

### Chunking Rules

| Parameter | Value |
|---|---|
| Chunk size | 500–800 characters |
| Overlap | 80–120 characters |
| Metadata per chunk | document name, page number, category, chunk ID, company_id |

### Embedding Rules

1. Use `nvidia/nv-embed-v1` for all embeddings.
2. Embed documents **only** when uploaded or updated. Do not re-embed unchanged documents.
3. Store embeddings in a pgvector `vector` column.
4. Store source metadata alongside every vector.
5. Enable pgvector through Alembic migration: `CREATE EXTENSION IF NOT EXISTS vector;`
6. Use cosine similarity or inner product based on embedding normalization.

### Retrieval Rules

```
User question → Validate question → Embed question → Similarity search →
Retrieve top 3–5 chunks → Build prompt with delimited context → Call LLM →
Return answer with source citations
```

1. Retrieve **top 3–5 chunks only**. Never send full policy documents to the LLM.
2. If the answer is not found in the retrieved context, respond: "This information was not found in the uploaded policies. Please contact HR directly."
3. Always include citations: document name, page/section, chunk reference.
4. Include a confidence score with every answer.
5. Save unanswered questions for HR review.
6. Track frequently asked questions for analytics.

### RAG Prompt Structure

```
[SYSTEM INSTRUCTIONS]
You are an HR policy assistant. Answer ONLY using the provided context.
If the answer is not in the context, say you cannot find it and suggest contacting HR.
Always cite the source document and section.

[CONTEXT START]
--- Document: {doc_name}, Page: {page}, Chunk: {chunk_id} ---
{chunk_text}
--- End Chunk ---
[CONTEXT END]

[USER QUESTION START]
{sanitized_user_question}
[USER QUESTION END]

[OUTPUT RULES]
Respond in JSON: {"answer": "...", "confidence": 0.0-1.0, "citations": [...], "needs_hr_review": bool}
```

### RAG Security

- Scan questions for prompt injection patterns before processing.
- Never allow uploaded policy text to override system instructions.
- Do not expose vector IDs, internal metadata, database IDs, or file paths in responses.

---

## 10. NVIDIA NIM AI Model Routing Rules

### Model Registry

| Alias | Model ID | Use Cases |
|---|---|---|
| **Small** | `meta/llama-3.1-8b-instruct` | Simple chat, JD drafts, email text, interview questions, short summaries, welcome messages |
| **Large** | `meta/llama-3.1-70b-instruct` | Resume scoring, policy reasoning, performance review generation, learning plan generation |
| **Advanced** | `nvidia/llama-3.3-nemotron-super-49b-v1.5` | Admin insights, complex workforce analysis, multi-document reasoning |
| **Embedding** | `nvidia/nv-embed-v1` | Policy chunk embeddings, user question embeddings |

### Routing Logic

The model router must **automatically** select the correct model based on task type. No manual model selection in service code — always go through the router.

```python
# Pseudocode — model_router.py
def get_model(task_type: str) -> str:
    ROUTING_TABLE = {
        "jd_draft": "small",
        "email_text": "small",
        "interview_questions": "small",
        "welcome_message": "small",
        "simple_summary": "small",
        "resume_scoring": "large",
        "policy_reasoning": "large",
        "performance_review": "large",
        "learning_plan": "large",
        "retention_strategy": "large",
        "admin_insight": "advanced",
        "workforce_analysis": "advanced",
        "embedding": "embedding",
    }
    return ROUTING_TABLE.get(task_type, "small")  # Default to small
```

### AI Call Rules

1. Every AI call must go through the model router — never call NVIDIA directly from services or routes.
2. Every AI output must be saved in the `ai_history` table with: model used, prompt hash, input summary (not raw input), output, token count, latency, module name.
3. Every AI score or prediction must include **explainability** — the model must explain why it produced a score/rating.
4. Every sensitive HR AI output (performance reviews, attrition predictions, hiring recommendations) must be labeled as **"recommendation only — human review required"**.
5. Validate LLM JSON output before saving to the database. Reject malformed responses.
6. Never execute LLM output as code.

### Model Provider Flexibility & Decoupling

The project must be model-provider-flexible to prevent vendor lock-in and enable seamless provider or hosted model transitions:
1. **Centralized Configuration:** All AI model IDs, API keys, base URLs, timeout values, connection settings, and token limits must be managed by the centralized `Settings` class (`app/core/config.py`) via environment variables.
2. **AI Client Adapter:** All model invocations must go through an abstract/generic AI client adapter. No service, route, prompt file, or feature module may instantiate provider-specific SDK clients directly or hardcode API calls.
3. **Model Router:** All service/feature logic must resolve model aliases through the `model_router` (`app/services/ai/model_router.py`), specifying task-based or size-based aliases rather than direct provider model IDs.
4. **Configuration-Driven Updates:** If model names, API keys, or compatible hosted endpoints change, modifications must be made only in the `.env` file or deployment environment variables, requiring no codebase rewrites of feature modules or services.

---

## 11. API Cost-Saving Rules

### Mandatory Cost Controls

| Control | Implementation |
|---|---|
| **AI response cache** | `ai_cache` table — hash(prompt + model) → cached response with TTL |
| **Resume hash cache** | hash(resume_text + jd_text) → cached score |
| **JD generation cache** | hash(normalized title + skills + level) → cached JD |
| **Interview kit cache** | hash(role + level + skills) → cached kit |
| **Policy question cache** | hash(question_embedding) → cached answer |
| **Embedding reuse** | Do not re-embed unchanged documents |
| **Local preprocessing** | Clean, normalize, extract with Pandas/regex before any LLM call |
| **Token limits** | Enforce strict `max_tokens` per request type |
| **Rate limiting** | LLM endpoints: max 10 requests/min/user |
| **Input length limits** | Truncate oversized inputs before sending to LLM |
| **Top-k retrieval** | RAG retrieves top 3–5 chunks, never full documents |
| **Cache TTL** | Configurable via `CACHE_TTL_HOURS` env var (default: 24 hours) |

### Processing Order (Before Every LLM Call)

```
1. Validate input
2. Check cache (return cached response if hit)
3. Clean and normalize input
4. Preprocess with Pandas / SQL / business rules
5. If LLM is truly needed, build prompt with preprocessed data
6. Route to smallest suitable model
7. Call NVIDIA NIM
8. Validate output
9. Cache response
10. Save to ai_history
11. Return to service
```

### Dashboard Metric

The dashboard must show "API calls saved by cache" as a KPI card.

---

## 12. Security Rules

### 12.1 Secrets Management

- **Never** hardcode API keys, passwords, JWT secrets, database URLs, or tokens.
- Create `.env` before any application code.
- Add `.env` to `.gitignore`.
- Create `.env.example` with placeholder values.
- Read secrets **only** through environment variables (`python-dotenv` → `os.getenv()`).
- Rotate any key that is accidentally exposed.
- Never print, log, or return secrets in API responses.

### Required `.env.example`

```env
APP_NAME=TalentForge AI
APP_ENV=development
SECRET_KEY=change-me-to-a-random-string
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST/DB?sslmode=require
NVIDIA_API_KEY=nvapi-your-key-here
NVIDIA_SMALL_MODEL=meta/llama-3.1-8b-instruct
NVIDIA_MEDIUM_MODEL=meta/llama-3.1-70b-instruct
NVIDIA_LARGE_MODEL=nvidia/llama-3.3-nemotron-super-49b-v1.5
NVIDIA_EMBEDDING_MODEL=nvidia/nv-embed-v1
ALLOWED_ORIGINS=http://localhost:8000
MAX_UPLOAD_SIZE_MB=10
CACHE_TTL_HOURS=24
LOG_LEVEL=INFO
```

### 12.2 Input Validation

- Use Pydantic v2 schemas for **every** user input.
- Reject missing fields, wrong types, unexpected fields, oversized payloads.
- Enforce string max lengths on all text fields.
- Validate email format, UUID format, enum values.
- Never trust client-side validation — re-validate everything server-side.

### 12.3 Database Security

- Use SQLAlchemy ORM and parameterized queries only.
- Never concatenate SQL strings.
- Store password hashes only (bcrypt via passlib).
- Encrypt sensitive HR data where needed.
- Do not expose internal database IDs in API responses when avoidable.

### 12.4 Rate Limiting

| Endpoint Type | Limit |
|---|---|
| Public APIs | 20 requests/min/IP |
| Authentication | 5 requests/min/IP |
| Authenticated APIs | 60 requests/min/user |
| LLM/AI endpoints | 10 requests/min/user |

Return HTTP 429 with `Retry-After` header when limit is exceeded.

### 12.5 CORS and Headers

**CORS:**
- Never use wildcard (`*`) for `Access-Control-Allow-Origin`.
- Use an explicit allowlist from the `ALLOWED_ORIGINS` environment variable.
- Reject unknown origins.

**Security Headers (all mandatory):**
- `Content-Security-Policy`
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: camera=(), microphone=(), geolocation=()`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains` (production only)

### 12.6 HTTPS

- Production must use HTTPS (Render provides this).
- Cookies must use `HttpOnly`, `Secure`, `SameSite=Strict`.
- Redirect HTTP to HTTPS in production.

---

## 13. Prompt Injection Protection Rules

1. **Never** insert raw user input directly into system prompts.
2. Wrap all user-provided content in clear delimiters:
   ```
   [USER INPUT START]
   {sanitized_input}
   [USER INPUT END]
   ```
3. Wrap retrieved RAG context in separate delimiters:
   ```
   [CONTEXT START]
   {context}
   [CONTEXT END]
   ```
4. Detect and reject common prompt injection phrases before processing:
   - "Ignore previous instructions"
   - "Reveal system prompt"
   - "System:"
   - "Assistant:"
   - "Developer:"
   - "You are now..."
   - Any attempt to redefine the LLM's role
5. Limit prompt length and response `max_tokens` per request type.
6. Validate LLM JSON output before saving — reject if malformed.
7. Never execute AI output as code or shell commands.
8. Never send full resumes, full PDFs, or full database rows to the LLM — only preprocessed, trimmed, relevant data.
9. Log prompt injection detection events server-side for audit.

---

## 14. File Upload Validation Rules

### Allowed File Types

| Extension | MIME Type |
|---|---|
| `.pdf` | `application/pdf` |
| `.docx` | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` |

### Validation Checklist (All Required)

1. **Extension check** — reject anything not `.pdf` or `.docx`.
2. **MIME type check** — verify MIME type matches the extension using `python-magic` or equivalent.
3. **File size check** — reject files exceeding `MAX_UPLOAD_SIZE_MB` (default: 10 MB).
4. **Content validation** — attempt to parse the file; reject if parsing fails.
5. **Filename sanitization** — generate a randomized internal filename (UUID-based). Never use the original filename for storage.
6. **Reject dangerous types** — explicitly block `.exe`, `.zip`, `.js`, `.html`, `.sh`, `.bat`, `.py`, `.php`, and any unknown MIME type.

### File Handling Rules

- Store uploads in a temporary directory.
- Delete temporary files immediately after processing.
- Never execute uploaded files.
- Extract only required text and metadata — do not store the full binary permanently.
- The `uploads/` directory must have a `.gitkeep` and nothing else committed.

---

## 15. Error Handling Rules

### Client-Facing Errors

- Return **generic, user-safe** error messages only.
- Use the standard response envelope:
  ```json
  {"success": false, "error": "Something went wrong. Please try again."}
  ```
- Never return: stack traces, SQL errors, file paths, API keys, environment variables, internal exception details, or database error messages.

### Server-Side Errors

- Log **detailed** error information server-side only.
- Use custom exception classes for different error categories.
- Use FastAPI exception handlers to catch and sanitize all errors before response.

### HTTP Status Codes

| Code | Usage |
|---|---|
| 200 | Success |
| 201 | Created |
| 400 | Bad request / validation error |
| 401 | Unauthenticated |
| 403 | Forbidden / insufficient permissions |
| 404 | Not found |
| 422 | Unprocessable entity |
| 429 | Rate limited |
| 500 | Internal server error (generic message to client) |

### Success Response Format

```json
{"success": true, "data": {}, "message": "OK"}
```

---

## 16. Logging Rules

### What to Log

- Application startup and shutdown
- Login / logout events
- File upload events (metadata only)
- AI requests: model, task type, token count, latency, cache hit/miss
- Database errors (sanitized)
- Permission denied events
- Admin actions
- Rate limit violations
- Prompt injection detection events

### What to NEVER Log

- Passwords or password hashes
- JWT tokens
- API keys or secrets
- Resume content or full text
- Employee PII (salary, SSN, medical data, personal details)
- Full LLM prompts containing user data
- Full database query results

### Implementation

- Use Python `logging` module with structured JSON formatting.
- Configure log levels via `LOG_LEVEL` environment variable.
- In production, write logs to stdout (Render captures stdout).
- Use a centralized `logging_config.py` in `app/core/`.

---

## 17. Testing Rules

### Required Test Categories

| Category | What to Test |
|---|---|
| **Unit tests — Services** | Business logic for every HR module |
| **Unit tests — Repositories** | Database queries return expected results |
| **Validation tests** | Pydantic schema acceptance and rejection |
| **File validation tests** | Upload MIME type, extension, size, content checks |
| **Prompt injection tests** | Injection phrase detection and blocking |
| **RAG retrieval tests** | Correct chunks retrieved, citations included |
| **AI cache tests** | Cache hit returns cached response, cache miss calls API |
| **Export tests** | CSV, Excel, PDF generation produces valid files |
| **Dashboard tests** | Aggregation queries return correct KPIs |
| **Migration tests** | Alembic migrations apply and rollback cleanly |
| **Health endpoint test** | `GET /api/v1/health` returns `{"status": "healthy"}` |
| **Render startup test** | `uvicorn app.main:app` starts without error |

### Test Rules

- Use `pytest` as the test framework.
- All tests must pass before deployment: `pytest`
- Mock NVIDIA API calls in tests — never make real API calls in CI.
- Use a test database or SQLite for unit tests (production uses PostgreSQL).
- Tests must not depend on external services being available.
- Write tests for both happy paths and error paths.

---

## 18. Deployment Rules (Render + Neon)

### Render Configuration

| Setting | Value |
|---|---|
| **Build command** | `pip install -r requirements.txt` |
| **Start command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Health check path** | `/api/v1/health` |
| **Environment** | All secrets set via Render dashboard environment variables |

### Neon Configuration

1. Create a Neon PostgreSQL database.
2. Copy the `DATABASE_URL` connection string (must include `?sslmode=require`).
3. Set `DATABASE_URL` in Render environment variables.
4. Run Alembic migrations before first production use.
5. Enable pgvector: `CREATE EXTENSION IF NOT EXISTS vector;` (via migration).

### Free Tier Considerations

- Render free tier spins down idle services — first request after idle will be slow.
- Avoid long-running startup tasks (e.g., embedding/indexing at boot).
- Run embedding and indexing as request-triggered or background-safe tasks.
- Use database connection pooling carefully to stay within Neon free tier limits.

### Deployment Checklist

- [ ] Environment variables configured in Render dashboard
- [ ] Debug mode disabled (`APP_ENV=production`)
- [ ] HTTPS enabled (Render default)
- [ ] CORS allowlist configured for production domain
- [ ] Rate limiting enabled
- [ ] Security headers enabled
- [ ] Logging enabled (stdout)
- [ ] Database migrations applied
- [ ] pgvector extension enabled
- [ ] Demo seed data loaded
- [ ] Health endpoint `/api/v1/health` returns `{"status": "healthy"}`
- [ ] No secrets committed to repository
- [ ] `.env` is in `.gitignore`

### `render.yaml` Template

```yaml
services:
  - type: web
    name: talentforge-ai
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: NVIDIA_API_KEY
        sync: false
      - key: SECRET_KEY
        sync: false
      - key: APP_ENV
        value: production
```

---

## 19. Future Authentication / RBAC Compatibility Rules

Authentication is deferred to post-V1, but the codebase must be **pre-wired** so it can be added without refactoring.

### Pre-Wiring Requirements

1. Every route handler must accept an optional `current_user` dependency (defaulting to a demo user for V1).
2. Every service method that accesses tenant data must accept `company_id` as a parameter.
3. Create a `get_current_user` dependency in `app/core/security.py` that returns a demo user for V1 and can later be swapped to JWT validation.
4. Create a `roles` table or enum: `admin`, `hr_manager`, `recruiter`, `employee`, `manager`.
5. Include a `role` column in the `users` table.
6. Include a `company_id` foreign key in the `users` table.
7. Database models for users must include: `id`, `email`, `password_hash`, `role`, `company_id`, `is_active`, `created_at`, `updated_at`.
8. The demo user for V1 should have `role=admin` and the default `company_id`.

### When Auth Is Added Later

- JWT access token: short-lived (15–30 min)
- Refresh token: limited lifetime (7 days)
- `HttpOnly`, `Secure`, `SameSite=Strict` cookies
- CSRF protection
- RBAC enforcement on every protected route (server-side only)
- Never trust frontend role assertions

---

## 20. Code Style Rules

### Python

- Python 3.11+ required.
- Type hints on all function signatures.
- Docstrings on all service functions and complex logic.
- Clear, descriptive names — no abbreviations or single-letter variables (except loop counters).
- Small, focused functions with a single responsibility.
- Remove unused imports and dead code.

### Naming Conventions

| Item | Convention | Example |
|---|---|---|
| Files | `snake_case.py` | `resume_service.py` |
| Classes | `PascalCase` | `ResumeScreeningService` |
| Functions | `snake_case` | `calculate_match_score` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_UPLOAD_SIZE_MB` |
| API paths | `kebab-case` | `/api/v1/resume-screening` |
| Database tables | `snake_case` | `performance_reviews` |
| Environment variables | `UPPER_SNAKE_CASE` | `NVIDIA_API_KEY` |

### Formatting

- **Black** for code formatting.
- **Ruff** for linting.
- **isort** for import sorting.
- Keep imports clean and grouped: stdlib → third-party → local.

### Comments

- Comment **why**, not the obvious what.
- Avoid noisy comments.
- Use `TODO:` only with a clear reason and context.
- Never leave commented-out code in production.

---

## 21. Git Rules

1. **Never** commit `.env` — it must be in `.gitignore`.
2. **Never** push secrets, API keys, or credentials to the repository.
3. Keep commits focused on one task or feature.
4. Write clear, descriptive commit messages.
5. Do not rename or delete files unless explicitly requested.
6. Do not refactor unrelated code when implementing a feature.
7. Before every commit, verify:
   - No secrets in the diff
   - `.gitignore` includes `.env`, `__pycache__/`, `.venv/`, `uploads/*`, `exports/*`
   - No large binary files committed
8. Branch naming (when applicable): `feature/module-name`, `fix/issue-description`, `chore/task-name`

### Required `.gitignore` Entries

```
.env
__pycache__/
*.pyc
.venv/
venv/
*.egg-info/
dist/
build/
uploads/*
!uploads/.gitkeep
exports/*
!exports/.gitkeep
.DS_Store
*.sqlite3
```

---

## 22. Documentation Rules

1. Maintain the `/docs` folder as the architecture reference. Do not delete or restructure existing docs without explicit approval.
2. `AGENT.md` (this file) is the single source of truth for agent behavior. Update it when project decisions change.
3. `README.md` must include: project description, setup instructions, environment variable list, seed data command, and deployment steps.
4. Every new module should have inline docstrings explaining its purpose.
5. API routes should be documented with FastAPI's built-in OpenAPI/Swagger support.
6. Keep `requirements.txt` up to date with every new dependency.
7. Record architectural decisions in the relevant docs file.

---

## 23. Definition of Done

A feature is considered **complete** only when ALL of the following are true:

- [ ] Feature works end-to-end from the UI
- [ ] Input validation is implemented (Pydantic schema)
- [ ] All queries filter by `company_id` where applicable
- [ ] AI output is saved in `ai_history`
- [ ] AI scores/predictions include explainability text
- [ ] Sensitive HR AI output shows "recommendation only — human review required"
- [ ] AI calls go through the model router (correct model selected)
- [ ] AI response caching is implemented for repeatable requests
- [ ] File uploads (if any) pass all 6 validation checks
- [ ] Error handling returns generic messages to the client
- [ ] Detailed errors are logged server-side only
- [ ] No secrets are hardcoded
- [ ] Rate limiting is applied to AI/LLM endpoints
- [ ] Export functionality works (where applicable)
- [ ] Loading, error, and empty states exist in the UI
- [ ] Tests are written and passing
- [ ] No `TODO` or placeholder code remains
- [ ] Code passes Black, Ruff, and isort checks

---

## 24. Things NEVER to Do

This is an absolute blocklist. Violating any of these rules is a critical failure.

| # | Rule |
|---|---|
| 1 | **Never** use Streamlit |
| 2 | **Never** use Flask |
| 3 | **Never** use Next.js or React for this project |
| 4 | **Never** use SQLite for production deployment |
| 5 | **Never** hardcode API keys, secrets, passwords, or database URLs |
| 6 | **Never** skip `.env` setup — it must exist before app code |
| 7 | **Never** commit `.env` to version control |
| 8 | **Never** place business logic inside route handlers |
| 9 | **Never** place database queries inside route handlers |
| 10 | **Never** call the NVIDIA API directly from routes — use the AI service layer |
| 11 | **Never** send full resumes, full PDFs, or full database rows to the LLM |
| 12 | **Never** send raw user input directly into system prompts |
| 13 | **Never** build SQL using string concatenation |
| 14 | **Never** return stack traces, SQL errors, file paths, or secrets in API responses |
| 15 | **Never** log passwords, JWT tokens, API keys, resume content, or employee PII |
| 16 | **Never** use wildcard `*` for CORS origins |
| 17 | **Never** trust frontend-only validation for security |
| 18 | **Never** execute LLM output as code |
| 19 | **Never** make automatic HR decisions without a human review warning |
| 20 | **Never** create marketing pages (landing, about, pricing, how-it-works) |
| 21 | **Never** store uploads permanently on server disk — extract data and delete |
| 22 | **Never** enable debug mode in production |
| 23 | **Never** expose internal database IDs or file paths to the frontend |
| 24 | **Never** replace locked technologies without explicit project owner approval |
| 25 | **Never** skip AI output validation before saving to the database |
| 26 | **Never** skip `company_id` filtering on tenant-owned queries |
| 27 | **Never** add authentication before all 8 core HR modules work correctly |
| 28 | **Never** use AI where local logic (SQL, Pandas, Scikit-learn, rules) is sufficient |
| 29 | **Never** generate placeholder/stub code when a complete implementation is possible |
| 30 | **Never** delete or restructure `/docs` without explicit approval |

---

## 25. Feature Implementation Checklist — All 8 HR Modules

### Module 1: Resume Screening

- [ ] Bulk resume upload endpoint (PDF + DOCX)
- [ ] File validation (MIME, extension, size, content)
- [ ] Text extraction (PyPDF2, python-docx)
- [ ] Local extraction: email, phone, skills, experience (regex + Pandas)
- [ ] AI scoring against job description (large model via router)
- [ ] Candidate ranking table with score distribution chart
- [ ] Per-candidate scorecard: match score, matching skills, missing skills, strengths, red flags
- [ ] Recommendation label: shortlist / maybe / reject
- [ ] Suggested interview questions per candidate
- [ ] AI-generated interview invitation text (copy button)
- [ ] Candidate status update endpoint
- [ ] Cache by hash(resume_text + jd_text)
- [ ] Send only trimmed, relevant text to LLM — never full resume
- [ ] Save AI output to `ai_history` with explainability
- [ ] Export results to CSV and Excel
- [ ] "Human review required" label on AI recommendations
- [ ] Loading, error, and empty states in UI

### Module 2: HR Policy Chatbot (RAG)

- [ ] Policy document upload endpoint (PDF + DOCX)
- [ ] Document category selection
- [ ] Text extraction and cleaning
- [ ] Chunking (500–800 chars, 80–120 overlap)
- [ ] Embedding generation via `nvidia/nv-embed-v1`
- [ ] Store chunks + embeddings in pgvector with metadata
- [ ] Chat UI with question input
- [ ] Question validation + prompt injection scanning
- [ ] Embed question → similarity search → retrieve top 3–5 chunks
- [ ] Build delimited prompt with context
- [ ] Generate answer using retrieved chunks only (large model)
- [ ] Response includes: answer, confidence score, citations (doc name, page, chunk)
- [ ] "Not found in policies — contact HR" fallback
- [ ] Save unanswered questions for HR review
- [ ] FAQ analytics (most asked questions)
- [ ] Document list and indexing status page
- [ ] Do not re-embed unchanged documents
- [ ] Save AI output to `ai_history`
- [ ] Cache by hash(question_embedding)

### Module 3: Job Description Generator

- [ ] Input form: title, department, experience, required skills, preferred skills, location, employment type, tone, company summary
- [ ] AI-generated complete JD (small model): responsibilities, required qualifications, preferred qualifications, skills, benefits, ATS keywords
- [ ] Salary range suggestion (AI-generated estimate, labeled as estimate)
- [ ] LinkedIn-style post variant
- [ ] Naukri/Indeed-style summary variant
- [ ] Internal hiring note variant
- [ ] Optimize existing JD feature
- [ ] Save generated JD to database
- [ ] Copy output buttons for each section
- [ ] Export as PDF, DOCX, and TXT
- [ ] Cache by hash(normalized title + skills + level)
- [ ] Save AI output to `ai_history`
- [ ] Loading, error, and empty states

### Module 4: Employee Onboarding Assistant

- [ ] Input form: employee name, role, department, manager, start date, work mode, experience level
- [ ] AI-generated personalized onboarding plan (small model)
- [ ] Day 1 schedule, Week 1 tasks, Month 1 roadmap
- [ ] 30/60/90 day goals
- [ ] Document checklist
- [ ] Tools/access checklist
- [ ] People to meet list
- [ ] Manager guidance notes
- [ ] Welcome email text (copy button)
- [ ] Team announcement text (copy button)
- [ ] Task completion tracking (local logic — checkboxes)
- [ ] Progress percentage and status: pending / in progress / on track / behind / complete
- [ ] Export onboarding plan as PDF
- [ ] Save AI output to `ai_history`

### Module 5: Performance Review Generator

- [ ] Input form: employee, role, review period, goals achieved/total, manager observations, attendance %, peer feedback
- [ ] AI-generated review summary (large model)
- [ ] Rating suggestion with explainability
- [ ] Key achievements list
- [ ] Development areas
- [ ] Bias check flag
- [ ] Promotion readiness assessment
- [ ] Salary revision recommendation label (recommendation only)
- [ ] Next-period SMART goals
- [ ] Development plan
- [ ] PIP generator for low performers
- [ ] Team performance summary chart
- [ ] Save review history
- [ ] Export performance review as PDF
- [ ] **"Draft only — human review required before use"** label prominently displayed
- [ ] Save AI output to `ai_history` with explainability

### Module 6: Employee Attrition Prediction

- [ ] Input form: salary, performance rating, tenure, promotion history, manager satisfaction, overtime hours, team attrition rate, department, role
- [ ] Local risk score calculation (Scikit-learn / rule-based — **zero AI for base score**)
- [ ] Risk level: low / medium / high / critical
- [ ] Risk factor explanation (local explainability)
- [ ] Replacement cost estimate (formula-based)
- [ ] Department-wise risk chart
- [ ] At-risk employee table
- [ ] AI-generated retention strategy **only for high/critical** risk (large model)
- [ ] Stay interview questions
- [ ] Risk trend history
- [ ] Export attrition risk report (PDF/CSV)
- [ ] **"Decision-support tool only — not for automatic employment decisions"** label
- [ ] Save AI output to `ai_history` with explainability
- [ ] Save attrition assessments to database

### Module 7: Learning Recommendation Engine

- [ ] Input form: employee, current role, target role, current skills, experience level, department
- [ ] Skill gap analysis (local logic + AI)
- [ ] Readiness score
- [ ] Critical missing skills list
- [ ] Learning path by phase (AI-generated, large model)
- [ ] Free resource suggestions
- [ ] Certification suggestions
- [ ] Timeline
- [ ] Training status tracking (local logic — checkboxes)
- [ ] Department skill gap report
- [ ] Training ROI estimate
- [ ] Export learning plan as PDF
- [ ] Save AI output to `ai_history`

### Module 8: Interview Kit Generator

- [ ] Input form: job role, department, experience level, key skills, interview duration, panel members
- [ ] AI-generated interview structure (small model)
- [ ] Technical questions with difficulty levels
- [ ] Behavioral questions
- [ ] Situational questions
- [ ] Culture-fit questions
- [ ] Expected answer points for each question
- [ ] Evaluation rubric with scorecard weights
- [ ] Panel guide (who asks what)
- [ ] Red-flag answer notes
- [ ] Candidate Q&A guide
- [ ] Interview checklist
- [ ] Save to reusable question bank
- [ ] Export interview kit as PDF/DOCX
- [ ] Cache by hash(role + level + skills)
- [ ] Save AI output to `ai_history`

### Shared: Dashboard

- [ ] KPI cards: total employees, total candidates, shortlisted, pending reviews, high/critical attrition count, pending onboarding, pending training, policy questions asked, API calls saved by cache
- [ ] Charts: candidate pipeline, resume score distribution, department employee count, attrition risk distribution, training status, policy questions trend, performance rating distribution
- [ ] Tables: recent candidates, at-risk employees, pending onboarding, recent policy questions, recent generated documents
- [ ] Data sourced from SQL aggregation (not AI)
- [ ] Demo data renders charts and tables immediately

### Shared: Demo Seed Data

- [ ] Seed script: `python scripts/seed_demo_data.py`
- [ ] 1 default company
- [ ] 10 employees across 3 departments
- [ ] 8 candidates with varied scores
- [ ] Sample performance records
- [ ] Sample training records
- [ ] Sample attrition risk values
- [ ] Sample policy text / content
- [ ] Sample job roles
- [ ] Sample onboarding records
- [ ] App shows clear message if no data exists

### Shared: Export Center

- [ ] Candidate screening results: CSV, Excel
- [ ] Resume screening report: PDF
- [ ] Job descriptions: TXT, DOCX, PDF
- [ ] Onboarding plans: PDF
- [ ] Performance reviews: PDF
- [ ] Attrition reports: PDF, CSV
- [ ] Learning plans: PDF
- [ ] Interview kits: PDF, DOCX
- [ ] Dashboard summary: PDF
- [ ] All exports generated server-side

---

## 26. Permanent Development Workflow

This workflow is mandatory for every future phase and subphase of TalentForge AI.

### Before starting ANY work on the project:
1. **Read ALL project documentation** before doing anything. This includes:
   - `AGENT.md`
   - `PRD.md`
   - `PROJECT.md`
   - Every file inside `docs/`
   - The current phase README inside `docs/phase_reports/`
   - Previous subphase reports for the current phase
   - `docs/14_ROADMAP.md`
   *Never start planning or coding without first reviewing the latest documentation.*

### Before starting every roadmap phase:
1. Read all project documentation.
2. Analyze the current project state.
3. Create a detailed implementation plan.
4. Split the phase into small subphases.
5. **Do NOT write code** until the implementation plan is reviewed and approved by the user.
6. Create or update the related phase folder inside `docs/phase_reports/`.
7. Store the approved implementation plan inside that phase folder `README.md` before implementation begins.

### During every subphase:
1. Implement **ONLY** the approved subphase.
2. Do not implement future subphases.
3. Modify only necessary files.
4. Follow the existing architecture exactly.
5. Keep the project modular and production-ready.

### After every completed subphase:
1. Run all relevant tests.
2. Fix every discovered bug.
3. Perform security validation.
4. Perform architecture validation.
5. Perform tenant isolation validation where applicable.
6. Give a detailed walkthrough in chat explaining:
   - Files created
   - Files modified
   - Why changes were made
   - Tests executed
   - Validation results
   - Known limitations
7. Create or update the corresponding subphase report.
8. Update the current phase README progress.
9. Update any affected documentation if required.

### After every completed roadmap phase:
1. Run full phase validation.
2. Create the final phase report.
3. Summarize:
   - Work completed
   - Files changed
   - Migrations
   - Tests
   - Bug fixes
   - Validation results
   - Remaining work
4. Update `docs/14_ROADMAP.md`.
5. **Do NOT start the next phase** until the user approves.

---

## Build Order

When implementing TalentForge AI, follow this sequence:

1. Security-first project initialization (`.env`, `.env.example`, `.gitignore`)
2. Folder structure creation
3. `requirements.txt` with all dependencies
4. FastAPI app skeleton (`app/main.py`)
5. Core config (`app/core/config.py`) and logging (`app/core/logging_config.py`)
6. Custom error handling (`app/core/errors.py`)
7. Database connection (`app/db/session.py`, `app/db/base.py`)
8. Alembic setup + pgvector extension migration
9. Core database models (all tables)
10. Demo seed script (`scripts/seed_demo_data.py`)
11. Dashboard (KPI cards, charts, tables)
12. Resume Screening module
13. HR Policy Chatbot with RAG + pgvector
14. JD Generator module
15. Onboarding Assistant module
16. Performance Review module
17. Attrition Prediction module
18. Learning Recommendation module
19. Interview Kit Generator module
20. Export Center
21. Test suite
22. Render deployment files (`render.yaml`) + deployment validation

---

## Conflict Resolution

If any user request conflicts with the rules in this document:

1. **Ask for confirmation** before changing architecture, technology, or security decisions.
2. This file takes precedence over conversational instructions unless the project owner explicitly overrides a specific rule.
3. If a rule in this file conflicts with a file in `/docs`, this file takes precedence (AGENT.md is the consolidated, authoritative source).
4. After any approved override, update this file to reflect the new decision.

---

*Last updated: 2026-07-03*
*Version: 1.0*
*Status: Active — binding on all AI agents*
