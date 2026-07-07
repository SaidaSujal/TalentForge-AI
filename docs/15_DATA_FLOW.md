# TalentForge AI — Data Flow Documentation

## Purpose
This document explains how data moves through TalentForge AI across all major workflows.

TalentForge AI is a multi-tenant HR SaaS platform. Every tenant-owned workflow must preserve `company_id` isolation from request entry to database query, AI processing, export generation, and dashboard analytics.

## Global Request Flow

```mermaid
flowchart TD
    A[User Action in Dashboard] --> B[FastAPI Route]
    B --> C[Pydantic Validation]
    C --> D[Security Middleware]
    D --> E[Service Layer]
    E --> F[Repository Layer]
    F --> G[(Neon PostgreSQL)]
    E --> H[AI Layer / Model Router]
    H --> I[NVIDIA NIM]
    E --> J[Response Formatter]
    J --> K[Jinja2 Template or JSON Response]
```

## Tenant Data Flow

```mermaid
flowchart TD
    A[Request] --> B[Demo/Future Auth User]
    B --> C[company_id resolved]
    C --> D[Service receives company_id]
    D --> E[Repository filters by company_id]
    E --> F[(Tenant-scoped PostgreSQL data)]
```

Rules:

- Every tenant-owned query must filter by `company_id`.
- No service may fetch tenant data without receiving `company_id`.
- Authentication and RBAC are deferred until after all 8 core modules work. For V1, use demo-user/current-company architecture only. All services and repositories must accept company_id so JWT/RBAC can be added later without refactor.

## Resume Screening Flow

```mermaid
flowchart TD
    A[HR uploads PDF/DOCX resumes + Job Description] --> B[File Validation]
    B --> C[Text Extraction]
    C --> D[Local Parsing: email, phone, skills, experience]
    D --> E[Hash resume + JD]
    E --> F{Cache Hit?}
    F -->|Yes| G[Return cached score]
    F -->|No| H[Trim relevant resume sections]
    H --> I[Model Router: Large Model]
    I --> J[NVIDIA NIM Resume Analysis]
    J --> K[Validate JSON Output]
    K --> L[Save Candidate + Resume Score]
    L --> M[Save AI History]
    M --> N[Show Ranked Candidate Table]
    N --> O[Export CSV/Excel/PDF]
```

Important rules:

- Never send full resumes to the LLM.
- AI output must include score, explanation, matching skills, missing skills, and recommendation.
- Every hiring recommendation must show human review required.

## HR Policy RAG Flow

```mermaid
flowchart TD
    A[HR uploads policy PDF/DOCX] --> B[Validate file]
    B --> C[Extract text]
    C --> D[Clean text]
    D --> E[Chunk text]
    E --> F[Embedding model: nvidia/nv-embed-v1]
    F --> G[Store chunks + vectors in pgvector]
    H[Employee asks question] --> I[Validate + injection scan]
    I --> J[Embed question]
    J --> K[Similarity search in pgvector]
    K --> L[Retrieve top 3-5 chunks]
    L --> M[Delimited RAG prompt]
    M --> N[Model Router: Large Model]
    N --> O[Answer with citations]
    O --> P[Save AI History + Chat Record]
```

Rules:

- RAG is used only for HR policy documents.
- Always cite document name and page/section.
- If context does not contain the answer, say it was not found and suggest contacting HR.

## Other Module Flows

### Job Description Generator

HR input → validation → normalize role/skills → cache check → small model → validate output → save JD → save AI history → export.

### Onboarding Assistant

New hire input → validation → small model → onboarding plan → save plan/tasks → save AI history → local progress tracking.

### Performance Review

Review input → validation → local goal calculation → large model → review draft + bias check → save review → save AI history → human review warning.

### Attrition Prediction

Employee risk input → validation → local ML/rule-based score → save risk explanation → high/critical check → large model retention strategy only when needed → save AI history.

### Learning Recommendation

Skill input → validation → local skill gap preprocessing → large model → learning plan → save AI history → training tracking.

### Interview Kit Generator

Role/skills input → validation → cache check → small model → interview kit → save AI history → export PDF/DOCX.

## Dashboard Data Flow

```mermaid
flowchart TD
    A[Dashboard Load] --> B[Dashboard Service]
    B --> C[SQL Aggregations by company_id]
    C --> D[(Neon PostgreSQL)]
    D --> E[KPI Cards]
    D --> F[Charts]
    D --> G[Recent Activity]
    D --> H[Notifications]
```

Rules:

- Dashboard analytics must come from SQL/Pandas, not AI.
- Dashboard must show demo data immediately after seeding.

## Export Data Flow

User clicks export → validate export type → fetch tenant-scoped data → generate file server-side → save export metadata → return download response.

Allowed formats: PDF, CSV, Excel, DOCX, TXT.

## AI History Flow

AI request → model router → NVIDIA NIM → validate output → save AI history → return output.

Every AI history record must store company_id, module name, task type, model used, prompt hash, input summary, output, cache status, latency, and created_at.

Never store full sensitive raw input in AI history.
