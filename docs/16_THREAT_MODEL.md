# TalentForge AI — Security Threat Model

## Purpose
This document identifies the main security risks in TalentForge AI and defines required mitigations.

TalentForge AI handles sensitive HR data including resumes, employee profiles, performance reviews, salary information, policy documents, and AI-generated HR recommendations.

## Assets to Protect

| Asset | Risk |
|---|---|
| Employee data | Privacy leakage, unauthorized access |
| Candidate resumes | PII leakage |
| Company policies | Confidential document exposure |
| Performance reviews | Sensitive employment information |
| Attrition risk data | Misuse or reputational harm |
| AI outputs | Incorrect or unsafe recommendations |
| API keys | Account compromise and billing abuse |
| Database URL | Full database compromise |
| Uploaded files | Malware or malicious content |
| Tenant data | Cross-company data leakage |

## Threats and Mitigations

## 1. Hardcoded Secrets

Risk: API keys, database URLs, JWT secrets, or tokens may be accidentally committed.

Mitigation:

- Use `.env` only.
- Add `.env` to `.gitignore`.
- Provide `.env.example`.
- Validate required environment variables at startup.
- Never log secrets.
- Rotate any exposed key immediately.

## 2. Cross-Tenant Data Leakage

Risk: One company may see another company's data.

Mitigation:

- Every tenant-owned table must include `company_id`.
- Every repository query must filter by `company_id`.
- Services must require `company_id`.
- Add tenant-isolation tests.
- Authentication and RBAC are deferred until after all 8 core modules work. For V1, use demo-user/current-company architecture only. All services and repositories must accept company_id so JWT/RBAC can be added later without refactor.

## 3. Prompt Injection

Risk: Users or uploaded documents may try to override model instructions.

Mitigation:

- Delimit user input.
- Delimit RAG context separately.
- Reject common injection patterns.
- Never allow uploaded policy text to override system instructions.
- Validate AI output before saving.
- Never execute AI output as code.

## 4. Malicious File Uploads

Risk: Users may upload disguised executable files, oversized files, or corrupted files.

Mitigation:

- Allow only PDF and DOCX.
- Validate extension, MIME type, size, and parsability.
- Randomize internal filenames.
- Store uploads temporarily only.
- Delete files after processing.
- Never execute uploaded files.

## 5. SQL Injection

Risk: User input may reach unsafe queries.

Mitigation:

- Use SQLAlchemy ORM.
- Never concatenate SQL strings.
- Use Pydantic validation.
- Reject unexpected fields.
- Add max length constraints.

## 6. Sensitive Data in Logs

Risk: Logs may contain resumes, salaries, API keys, or full prompts.

Mitigation:

- Use structured logging.
- Log metadata only.
- Redact PII.
- Never log full resumes, full prompts, tokens, passwords, API keys, or salary details.
- Use generic client errors.

## 7. Unsafe AI Recommendations

Risk: AI outputs may be treated as final HR decisions.

Mitigation:

- Show: "Recommendation only — human review required."
- Resume screening must not auto-reject candidates.
- Attrition prediction must not trigger employment action automatically.
- Performance review output must be draft only.
- Save explainability for every AI score or prediction.

## 8. Excessive API Usage

Risk: Users may spam AI endpoints and exhaust NVIDIA limits.

Mitigation:

- Rate limit AI endpoints.
- Cache repeatable AI responses.
- Use smallest suitable model.
- Preprocess locally.
- Truncate inputs.
- Retrieve only top RAG chunks.
- Track AI usage in dashboard.

## 9. CORS Misconfiguration

Risk: Wildcard CORS can allow untrusted websites to access APIs.

Mitigation:

- Never use `*`.
- Use explicit `ALLOWED_ORIGINS`.
- Reject unknown origins.
- Configure production Render domain.

## 10. Error Information Leakage

Risk: Stack traces, SQL errors, file paths, or internal IDs may leak.

Mitigation:

- Use global exception handlers.
- Return generic error messages.
- Log detailed errors server-side only.
- Never expose internal file paths or raw DB errors.

## 11. Weak Future Authentication Integration

Risk: Adding auth later may require refactoring or insecure shortcuts.

Mitigation:

- Authentication and RBAC are deferred until after all 8 core modules work. For V1, use demo-user/current-company architecture only. All services and repositories must accept company_id so JWT/RBAC can be added later without refactor.
- Add users table from day one.
- Add company_id from day one.
- Add demo user dependency now.
- Keep all services company_id-aware.
- Build route structure so JWT/RBAC can replace demo user later.

## Security Testing Checklist

- [ ] No hardcoded secrets
- [ ] `.env` ignored by Git
- [ ] Every tenant query filters by `company_id`
- [ ] File upload validation works
- [ ] Prompt injection detection works
- [ ] AI output validation works
- [ ] Rate limiting works
- [ ] CORS allowlist works
- [ ] Security headers exist
- [ ] Client errors are generic
- [ ] Logs do not contain secrets or PII
