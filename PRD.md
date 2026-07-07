# TalentForge AI — Product Requirements Document (PRD)

## 1. Document Control

**Project Name:** TalentForge AI  
**Product Type:** AI-Powered HR Intelligence Platform  
**Document:** Product Requirements Document  
**Version:** 1.0  
**Status:** Ready for Antigravity implementation planning  
**Deployment Target:** Render + Neon PostgreSQL  
**Frontend Style:** Real HR SaaS dashboard, not marketing website  
**Authentication:** Authentication and RBAC are deferred until after all 8 core modules work. For V1, use demo-user/current-company architecture only. All services and repositories must accept company_id so JWT/RBAC can be added later without refactor.

---

## 2. Product Vision

TalentForge AI is a functionality-first HR intelligence platform that helps HR teams complete major HR workflows from one dashboard. The platform combines local analytics, PostgreSQL data storage, pgvector RAG, NVIDIA NIM LLM calls, document parsing, export tools, and workflow-focused UI.

The system must be portfolio-ready, interview-ready, deployable, and realistic enough to demonstrate how AI can support HR operations without replacing human HR decisions.

---

## 3. Core Product Principle

Use AI only where reasoning, summarization, recommendations, natural language generation, or question generation is required.

Use local/backend logic for everything else:

- SQL filtering
- Pandas analytics
- Scikit-learn or rule-based prediction
- Input validation
- Ranking tables
- Charts
- Export generation
- Dashboard metrics
- File validation
- Business rules

The product must reduce unnecessary NVIDIA API calls through caching, preprocessing, retrieval, routing, and local computation.

---

## 4. In Scope

The first working version must include these 8 modules:

1. Resume Screening
2. HR Policy Chatbot with RAG
3. Job Description Generator
4. Employee Onboarding Assistant
5. Performance Review Generator
6. Employee Attrition Prediction
7. Learning Recommendation Engine
8. Interview Kit Generator

The app must also include:

- Dashboard
- Employee data management
- Candidate data management
- Policy document management
- Export features
- Sample/demo data
- PostgreSQL + pgvector database
- NVIDIA NIM integration
- AI response caching
- Render + Neon deployment readiness
- Security-first project setup

---

## 5. Out of Scope for V1

Do not build these in the first version:

- Marketing landing page
- About page
- Feature showcase page
- How it works page
- Pricing page
- Public website animations
- SaaS billing
- Multi-company tenant billing
- Real email sending
- Calendar integration
- Payroll system
- Biometric attendance
- Background verification integration
- Resume sourcing from LinkedIn/Naukri
- Full production RBAC login system

Authentication and RBAC will be added only after all features work correctly.

---

## 6. Target Users

V1 will be used as a single internal HR dashboard without login.

Future role model:

- Admin
- HR Manager
- Recruiter
- Employee
- Manager

Since authentication is deferred, V1 must still be structured so RBAC can be added later without rewriting the entire app.

---

## 7. Final Technology Stack

### Backend

- FastAPI
- Python
- SQLAlchemy 2.x
- Alembic
- Pydantic v2
- Jinja2 templates

### Frontend

- HTML
- Tailwind CSS
- JavaScript
- Fetch API
- Chart.js or Plotly.js
- Jinja2 server-rendered templates

### Database

- PostgreSQL on Neon
- pgvector for vector search

### AI

- NVIDIA NIM APIs
- LangChain
- NVIDIA embedding model: `nvidia/nv-embed-v1`

### ML and Analytics

- Pandas
- NumPy
- Scikit-learn

### Documents and Export

- PDF parsing
- DOCX parsing
- CSV export
- Excel export
- PDF report export

### Deployment

- Render Web Service
- Neon PostgreSQL
- Environment variables only

---

## 8. Architecture Requirements

The backend must follow this structure:

```text
Routes → Services → Repositories → Database
```

Rules:

- Routes only handle HTTP request/response.
- Services contain business logic.
- Repositories contain database queries.
- AI calls happen only inside AI service layers.
- Database queries must not be written inside route files.
- Frontend must not contain business logic.
- No direct raw user input should be sent to LLM prompts.

---

## 9. Proposed Folder Structure

```text
TalentForge-AI/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── rate_limiter.py
│   │   ├── logging_config.py
│   │   └── errors.py
│   ├── db/
│   │   ├── base.py
│   │   ├── session.py
│   │   ├── models.py
│   │   └── repositories/
│   ├── schemas/
│   ├── services/
│   │   ├── ai/
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
│   ├── routes/
│   ├── templates/
│   └── static/
│       ├── css/
│       ├── js/
│       └── assets/
├── alembic/
├── docs/
│   ├── 00_PROJECT_OVERVIEW.md
│   ├── 01_FEATURES.md
│   ├── 02_TECH_STACK.md
│   ├── 03_SYSTEM_ARCHITECTURE.md
│   ├── 04_BACKEND_ARCHITECTURE.md
│   ├── 05_FRONTEND_ARCHITECTURE.md
│   ├── 06_DATABASE_DESIGN.md
│   ├── 07_RAG_ARCHITECTURE.md
│   ├── 08_AI_MODEL_ROUTING.md
│   ├── 09_SECURITY_GUIDELINES.md
│   ├── 10_API_DESIGN.md
│   ├── 11_DEPLOYMENT.md
│   ├── 12_CODING_STANDARDS.md
│   ├── 13_ANTIGRAVITY_RULES.md
│   ├── 14_ROADMAP.md
│   └── PRD.md
├── tests/
├── scripts/
│   ├── seed_demo_data.py
│   └── validate_env.py
├── uploads/
│   └── .gitkeep
├── exports/
│   └── .gitkeep
├── .env.example
├── .gitignore
├── requirements.txt
├── render.yaml
├── PROJECT.md
└── README.md
```

---

## 10. UI Requirements

The UI must look like an internal HR SaaS dashboard.

Pages:

- Dashboard
- Resume Screening
- Policy Chatbot
- Job Description Generator
- Employee Onboarding
- Performance Review
- Attrition Risk
- Learning Recommendations
- Interview Kit
- Employees
- Candidates
- Policy Documents
- Export Center
- Settings / Environment Check

UI must include:

- Sidebar navigation
- Top header
- KPI cards
- Tables
- Forms
- Upload controls
- Charts
- AI output cards
- Copy buttons for AI-generated text
- Export buttons
- Loading states
- Error states
- Empty states
- Demo data button or setup command

Do not create marketing sections.

---

## 11. Module 1 — Resume Screening

### Purpose

Help HR upload multiple resumes and compare candidates against a job description.

### Inputs

- Job role
- Job description
- Minimum score threshold
- Resume files: PDF + DOCX

### Required Features

- Bulk resume upload
- PDF and DOCX text extraction
- Local extraction of email, phone, basic skills, experience indicators
- AI scoring against job description
- Candidate ranking table
- Matching skills
- Missing skills
- Strengths
- Red flags
- Recommendation: shortlist / maybe / reject
- Suggested interview questions
- Score distribution chart
- Candidate status update
- AI-generated interview invitation text for HR to copy
- Export results to CSV and Excel

### AI Usage

- One LLM call per resume after local preprocessing
- Cache by resume hash + job description hash
- Do not send full resume if too large
- Send trimmed, relevant text only

### Output

- Candidate scorecard
- Ranked table
- Detailed candidate analysis
- Exportable report

---

## 12. Module 2 — HR Policy Chatbot with RAG

### Purpose

Allow HR or employees to ask policy-related questions based only on uploaded company documents.

### Supported Documents

- Company policies
- Employee handbook
- Offer letters
- Leave rules

### Supported File Types

- PDF
- DOCX

### Required Features

- Upload policy documents
- Select document category
- Extract text
- Chunk text
- Generate embeddings with NVIDIA embedding API
- Store chunks and embeddings in PostgreSQL pgvector
- Ask natural language questions
- Retrieve top relevant chunks
- Generate answer using only retrieved chunks
- Show citations: document name, page/section, chunk reference
- Show confidence score
- Save unanswered questions for HR review
- Show frequently asked questions analytics
- Show document list and indexing status

### RAG Rules

- Never send full documents to the LLM
- Use top chunks only
- Clearly delimit retrieved context
- If answer is not in context, say HR should review
- All answers must include citations when sources exist

---

## 13. Module 3 — Job Description Generator

### Purpose

Generate ATS-friendly job descriptions quickly.

### Inputs

- Job title
- Department
- Experience level
- Required skills
- Preferred skills
- Location
- Employment type
- Tone
- Company summary

### Required Features

- Generate complete JD
- Required vs preferred qualifications
- Responsibilities
- Skills
- Benefits section
- ATS keywords
- Salary range suggestion as optional AI-generated estimate
- LinkedIn-style post
- Naukri/Indeed-style summary
- Internal hiring note
- Optimize existing JD
- Save generated JD
- Copy output buttons
- Export as PDF, DOCX, and TXT

### AI Usage

- Small/medium model
- Cache by normalized job title + skills + level

---

## 14. Module 4 — Employee Onboarding Assistant

### Purpose

Generate and track onboarding plans for new hires.

### Inputs

- Employee name
- Role
- Department
- Manager
- Start date
- Work mode
- Experience level

### Required Features

- Personalized onboarding plan
- Day 1 schedule
- Week 1 tasks
- Month 1 roadmap
- 30/60/90 day goals
- Document checklist
- Tools/access checklist
- People to meet
- Manager guidance
- Welcome email text for HR to copy
- Team announcement text for HR to copy
- Task completion tracking
- Progress percentage
- Status: pending / in progress / on track / behind / complete
- Export onboarding plan as PDF

### AI Usage

- One LLM call to generate plan
- One LLM call to generate email texts if requested
- Local logic for progress tracking

---

## 15. Module 5 — Performance Review Generator

### Purpose

Help managers create structured, balanced performance reviews.

### Inputs

- Employee
- Role
- Review period
- Goals achieved
- Total goals
- Manager observations
- Attendance percentage
- Peer feedback

### Required Features

- AI-generated review summary
- Rating suggestion
- Key achievements
- Development areas
- Bias check
- Promotion readiness
- Salary revision recommendation label
- Next-period SMART goals
- Development plan
- PIP generator for low performers
- Team performance summary chart
- Save review history
- Export performance review as PDF

### Important Safety Rule

AI output must be treated as a draft. Human HR/manager review is required before using the final review.

---

## 16. Module 6 — Employee Attrition Prediction

### Purpose

Identify employees who may need retention attention.

### Inputs

- Employee salary
- Performance rating
- Tenure
- Promotion history
- Manager satisfaction score
- Overtime hours
- Team attrition rate
- Department
- Role

### Required Features

- Local risk score calculation
- Risk level: low / medium / high / critical
- Risk factor explanation
- Replacement cost estimate
- Department-wise risk chart
- At-risk employee table
- AI-generated retention strategy only for high/critical risk
- Stay interview questions
- Risk trend history
- Export attrition risk report

### AI Usage

- Zero AI for base risk score
- AI only for high/critical retention recommendations

### Important Safety Rule

Attrition prediction must not be used as an automatic employment decision. It is only a decision-support tool.

---

## 17. Module 7 — Learning Recommendation Engine

### Purpose

Recommend learning paths based on current skills and target role.

### Inputs

- Employee
- Current role
- Target role
- Current skills
- Experience level
- Department

### Required Features

- Skill gap analysis
- Readiness score
- Critical missing skills
- Learning path by phase
- Free resource suggestions
- Certification suggestions
- Timeline
- Training status tracking
- Department skill gap report
- Training ROI estimate
- Export learning plan

### AI Usage

- AI for learning path and recommendations
- Local logic for progress tracking and department summaries

---

## 18. Module 8 — Interview Kit Generator

### Purpose

Create standardized interview kits for fair candidate evaluation.

### Inputs

- Job role
- Department
- Experience level
- Key skills
- Interview duration
- Panel members

### Required Features

- Interview structure
- Technical questions
- Behavioral questions
- Situational questions
- Culture-fit questions
- Difficulty levels
- Expected answer points
- Evaluation rubric
- Scorecard weights
- Panel guide
- Red-flag answer notes
- Candidate Q&A guide
- Interview checklist
- Save reusable question bank
- Export interview kit as PDF/DOCX

### AI Usage

- Small/medium model
- Cache by role + level + skills

---

## 19. Dashboard Requirements

Dashboard must show:

### KPI Cards

- Total employees
- Total candidates
- Shortlisted candidates
- Pending reviews
- High/critical attrition count
- Pending onboarding tasks
- Pending training items
- Policy questions asked
- API calls saved by cache

### Charts

- Candidate pipeline chart
- Resume score distribution
- Department employee count
- Attrition risk distribution
- Training status distribution
- Policy questions trend
- Performance rating distribution

### Tables

- Recent candidates
- At-risk employees
- Pending onboarding
- Recent policy questions
- Recent generated documents

---

## 20. Export Requirements

The platform must support exports for:

- Candidate screening results: CSV, Excel
- Resume screening report: PDF
- Job description: TXT, DOCX, PDF
- Onboarding plan: PDF
- Performance review: PDF
- Attrition report: PDF/CSV
- Learning path: PDF
- Interview kit: PDF/DOCX
- Dashboard summary: PDF

Exports must be generated server-side.

---

## 21. Demo Data Requirements

V1 must include demo data so the project works immediately after setup.

Demo data must include:

- 10 employees
- 8 candidates
- 3 departments
- Sample performance records
- Sample training records
- Sample attrition risk values
- Sample policy text or sample policy document content
- Sample job roles
- Sample onboarding records

There must be a seed script:

```bash
python scripts/seed_demo_data.py
```

The app should show a clear message if no data exists.

---

## 22. Database Requirements

Use PostgreSQL on Neon.

Required database entities:

- employees
- candidates
- resumes
- job_descriptions
- policy_documents
- policy_chunks
- policy_questions
- onboarding_plans
- onboarding_tasks
- performance_reviews
- attrition_assessments
- retention_strategies
- learning_plans
- training_records
- interview_kits
- exports
- ai_cache
- audit_logs
- app_settings

Vector storage:

- Store embeddings in pgvector column.
- Store source metadata with each chunk.
- Enable pgvector through migration.
- Use cosine similarity or inner product depending on embedding normalization.

---

## 23. AI Model Routing Requirements

Do not use one model for all tasks.

### Small model tasks

- Email text
- Short JD variants
- Interview questions
- Simple summaries

### Medium model tasks

- Resume analysis
- Performance review generation
- Learning plan generation

### Large model tasks

- Policy reasoning
- Complex HR reasoning
- Multi-document answer generation

### Embedding model

- `nvidia/nv-embed-v1`

The model router must automatically choose the model based on task type.

---

## 24. AI Cost Saving Requirements

The system must include:

- AI response cache table
- Resume hash cache
- JD generation cache
- Interview kit cache
- Policy question cache
- Embedding reuse
- Local preprocessing before LLM
- Strict max token limits
- Rate limiting on LLM endpoints
- Input length limits
- Top-k retrieval for RAG

---

## 25. Security Requirements

Security must be included from the first code generation step.

### Secrets

- No hardcoded API keys
- `.env` must be created before app logic
- `.env` must be in `.gitignore`
- `.env.example` must include placeholders
- `DATABASE_URL`, `NVIDIA_API_KEY`, and secret values must come from environment variables only

### Validation

- Pydantic v2 schemas for every user input
- Reject unexpected fields where possible
- String max lengths
- File type validation
- File size limits
- MIME and extension checks

### File Uploads

Allowed:

- `.pdf`
- `.docx`

Required:

- Max file size limit
- Safe temporary storage
- Randomized internal filename
- No execution of uploaded files
- Delete temporary files after processing when possible

### LLM Prompt Injection Protection

- Never insert raw input directly into system prompts
- Wrap user content in delimiters
- Detect suspicious prompt injection phrases
- Limit retrieved context
- Validate JSON outputs
- Never execute AI output

### CORS and Headers

- Explicit CORS allowlist
- CSP
- X-Frame-Options
- X-Content-Type-Options
- Referrer-Policy
- Permissions-Policy
- HSTS in production

### Errors and Logs

- Generic error messages to users
- Detailed errors only in server logs
- No stack traces in UI/API responses
- No PII or secrets in logs

### Auth Deferred Rule

V1 can run without login, but the structure must make future authentication possible.

When auth is added later:

- JWT access token: short-lived
- Refresh token: limited lifetime
- HttpOnly secure cookies
- CSRF protection
- RBAC enforcement server-side

---

## 26. Deployment Requirements — Render + Neon

### Render Requirements

- App must expose FastAPI app through Uvicorn.
- Build command:

```bash
pip install -r requirements.txt
```

- Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

- Use Render environment variables for secrets.
- Never commit `.env`.
- Include health endpoint:

```text
GET /api/v1/health
```

Health response:

```json
{"status":"healthy"}
```

### Neon Requirements

- Use `DATABASE_URL` from Neon.
- Require SSL in the connection string.
- Use SQLAlchemy engine.
- Run Alembic migrations.
- Enable pgvector extension through migration:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### Free Tier Considerations

- Render free web services can spin down when idle.
- First request after idle may be slow.
- Neon should be accessed through environment variables only.
- Use connection pooling carefully.
- Avoid long-running startup tasks.
- Run embedding/indexing as request-triggered/background-safe tasks, not blocking startup.

---

## 27. Environment Variables

Required `.env.example`:

```env
APP_NAME=TalentForge AI
APP_ENV=development
SECRET_KEY=change-me
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST/DB?sslmode=require
NVIDIA_API_KEY=nvapi-your-key-here
NVIDIA_SMALL_MODEL=replace-with-small-model
NVIDIA_MEDIUM_MODEL=replace-with-medium-model
NVIDIA_LARGE_MODEL=replace-with-large-model
NVIDIA_EMBEDDING_MODEL=nvidia/nv-embed-v1
ALLOWED_ORIGINS=http://localhost:8000
MAX_UPLOAD_SIZE_MB=10
CACHE_TTL_HOURS=24
```

---

## 28. API Requirements

All routes must return consistent JSON for API calls and templates for browser pages.

Required route groups:

```text
/dashboard
/employees
/candidates
/resume-screening
/policy-chatbot
/jd-generator
/onboarding
/performance
/attrition
/learning
/interview-kit
/exports
/settings
/api/v1/health
```

Heavy AI endpoints must be rate limited.

---

## 29. Testing Requirements

Required tests:

- Unit tests for services
- Unit tests for repositories
- File validation tests
- Prompt injection validation tests
- RAG retrieval tests
- AI cache tests
- Export generation tests
- Dashboard aggregation tests
- Database migration test
- Health endpoint test
- Render startup command test by local command

Minimum before deployment:

```bash
pytest
```

All tests must pass before deployment.

---

## 30. Acceptance Criteria

The project is considered V1 complete only when:

- All 8 modules work from UI
- Demo data loads successfully
- Neon database works
- pgvector RAG works
- PDF + DOCX upload works
- Exports work
- Dashboard charts work
- AI model routing works
- Cache saves repeated API calls
- No secrets are hardcoded
- `.env.example` exists
- `.gitignore` protects `.env`
- App deploys on Render
- `/api/v1/health` returns healthy
- Errors are user-safe
- Project can be explained in interview as functionality-first HR AI system

---

## 31. Build Order for Antigravity

Build in this order:

1. Security-first project initialization
2. Folder structure
3. `.env`, `.env.example`, `.gitignore`, requirements
4. FastAPI app skeleton
5. Config and logging
6. Database connection
7. Alembic setup
8. Core models
9. Demo seed script
10. Dashboard
11. Resume Screening
12. Policy RAG with pgvector
13. JD Generator
14. Onboarding Assistant
15. Performance Review
16. Attrition Prediction
17. Learning Recommendation
18. Interview Kit
19. Export Center
20. Tests
21. Render deployment files
22. Deployment validation

---

## 32. Non-Negotiable Rules for Antigravity

- Do not use Streamlit.
- Do not use Flask.
- Do not use SQLite for production.
- Do not hardcode secrets.
- Do not skip `.env` setup.
- Do not place business logic in routes.
- Do not send full documents to LLM.
- Do not create marketing pages.
- Do not add authentication until core features work.
- Do not use AI where local logic is enough.
- Do not make automatic HR decisions without human review warnings.

---

## 33. Final Product Summary

TalentForge AI is a production-oriented HR intelligence dashboard with 8 major AI-assisted HR modules. It uses FastAPI, Jinja2, Tailwind, JavaScript, PostgreSQL, pgvector, NVIDIA NIM, LangChain, Pandas, NumPy, and Scikit-learn. The platform prioritizes functionality, safe AI usage, low API cost, explainable outputs, exportable reports, and Render + Neon deployment readiness.
