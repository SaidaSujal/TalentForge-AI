# TalentForge AI — Performance Targets

## Purpose
This document defines practical performance targets for TalentForge AI.

These are engineering targets, not strict guarantees. They guide implementation, testing, optimization, and interview explanation.

## General Performance Principles

- Use SQL and Pandas before AI.
- Use local logic where possible.
- Cache repeatable AI responses.
- Retrieve only required RAG chunks.
- Avoid long startup tasks.
- Avoid embedding or AI calls during app boot.
- Keep dashboard queries aggregated and indexed.

## Page Load Targets

| Page | Target |
|---|---|
| Dashboard with demo data | < 2 seconds |
| Employees page | < 2 seconds |
| Candidates page | < 2 seconds |
| Policy documents page | < 2 seconds |
| Export center | < 2 seconds |

## API Response Targets

| Endpoint Type | Target |
|---|---|
| Health check | < 300 ms |
| Dashboard KPI API | < 1 second |
| CRUD APIs | < 800 ms |
| Search API | < 1.5 seconds |
| Export metadata API | < 1 second |
| AI cache hit | < 1 second |
| AI cache miss | Depends on model/API latency |

## AI Operation Targets

| Operation | Target |
|---|---|
| JD generation | < 15 seconds |
| Interview kit generation | < 15 seconds |
| Email text generation | < 10 seconds |
| Resume scoring per resume | < 20 seconds |
| Performance review generation | < 20 seconds |
| Policy chatbot answer | < 15 seconds |
| Cached policy chatbot answer | < 2 seconds |
| Attrition base score | < 1 second |
| Retention strategy generation | < 20 seconds |

## Batch Processing Targets

| Task | Target |
|---|---|
| Upload validation for 10 resumes | < 5 seconds |
| Local parsing for 10 resumes | < 10 seconds |
| Resume screening for 10 resumes | < 3 minutes |
| Resume screening for 20 resumes | < 6 minutes |
| Policy document chunking | < 30 seconds for normal HR policy PDFs |
| Export generation | < 10 seconds for normal reports |

## RAG Targets

| RAG Step | Target |
|---|---|
| Query embedding | < 3 seconds |
| pgvector similarity search | < 1 second |
| Top-k retrieval | top 3–5 chunks only |
| Answer generation | < 15 seconds |
| Cached answer | < 2 seconds |

## Database Targets

- Use indexes on `company_id`, `status`, `department`, `role`, `created_at`.
- Use pagination for large tables.
- Avoid loading full tables into memory.
- Avoid N+1 queries.
- Use SQL aggregation for dashboard metrics.
- Use Pandas only after scoped data retrieval.

## Render + Neon Considerations

- Render free tier may spin down when idle.
- First request after spin-down may be slow.
- Do not perform heavy work at startup.
- Run migrations manually or via controlled deployment step.
- Keep connection pooling conservative for Neon.

## Frontend Performance Rules

- Avoid unnecessary JavaScript libraries.
- Use server-rendered Jinja2 for core UI.
- Load charts only on pages that need them.
- Disable buttons during AI operations.
- Show loading states for long-running tasks.
- Use pagination for tables.

## Optimization Checklist

- [ ] Dashboard uses SQL aggregation
- [ ] Table pages use pagination
- [ ] AI cache is checked before NVIDIA calls
- [ ] RAG retrieves only top 3–5 chunks
- [ ] Full resumes/PDFs are never sent to LLM
- [ ] Uploads are deleted after processing
- [ ] Large exports are generated server-side
- [ ] Indexes exist for common filters
- [ ] No heavy work runs at startup
