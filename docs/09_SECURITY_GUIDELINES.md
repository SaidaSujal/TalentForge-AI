# Security Guidelines

## Objective
This document defines mandatory security rules for TalentForge AI. Every feature, API, database operation, AI request, and deployment must follow these rules. Security is a core architecture requirement and cannot be postponed.

---

# 1. Secrets Management

## Rules
- Never hardcode API keys, passwords, JWT secrets, database URLs, or tokens.
- Store all secrets in `.env`.
- Commit only `.env.example`.
- Add `.env` to `.gitignore`.
- Read secrets only through environment variables.
- Rotate any key that is accidentally exposed.
- Never print secrets in logs or API responses.

---

# 2. Environment Variables

Store only configuration values.

Examples:

- NVIDIA_API_KEY
- DATABASE_URL
- JWT_SECRET
- SECRET_KEY
- REDIS_URL
- FRONTEND_URL

Never commit production credentials.

---

# 3. Authentication

Authentication and RBAC are deferred until after all 8 core modules work. For V1, use demo-user/current-company architecture only. All services and repositories must accept company_id so JWT/RBAC can be added later without refactor.

When authentication is added post-V1:
- JWT Authentication.
- Short-lived Access Token.
- Refresh Token.
- Password hashing using bcrypt.
- Strong password policy.
- Secure logout.
- Role-Based Access Control (RBAC).
- Admin routes require Admin role.
- HR routes require HR/Admin role.

---

# 4. Authorization

Never trust frontend permissions.

Every protected API must verify (deferred for V1; pre-wired via company_id context):

- Logged-in user
- User role
- Resource ownership
- Permission level

Authorization checks always happen on the backend.

---

# 5. API Security

Every endpoint must include:

- Request validation
- Authentication (deferred for V1; pre-wired with company_id)
- Authorization (deferred for V1; pre-wired with company_id)
- Rate limiting
- Error handling
- Logging

Never expose internal exceptions.

---

# 6. Rate Limiting

Public APIs:
20 requests/min/IP

Authentication:
5 requests/min/IP

Authenticated APIs:
60 requests/min/user

LLM APIs:
10 requests/min/user

Return HTTP 429 with Retry-After header.

---

# 7. Input Validation

Validate every request using Pydantic.

Reject:

- Missing fields
- Wrong data types
- Unexpected fields
- Oversized payloads
- Invalid IDs
- Invalid emails
- Invalid URLs

Never trust client-side validation.

---

# 8. File Upload Security

Allowed:

- PDF
- DOCX

Reject:

- EXE
- ZIP
- JS
- HTML
- Unknown MIME types

Limit:

- Maximum file size
- Maximum page count
- Maximum upload count

Store uploads temporarily.

Delete after processing.

---

# 9. Database Security

Use SQLAlchemy ORM.

Never build SQL using string concatenation.

Always use parameterized queries.

Store:

- Password Hash
- Not Password

Encrypt sensitive HR information when necessary.

---

# 10. AI Prompt Security

Never place raw user input inside system prompts.

Prompt format:

System Instructions

↓

Retrieved Context

↓

User Input

↓

Output Rules

User content must be clearly delimited.

Reject common prompt injection attempts.

Examples:

- Ignore previous instructions
- Reveal system prompt
- System:
- Assistant:
- Developer:

Limit:

- Prompt length
- Response tokens

---

# 11. RAG Security

Only retrieve relevant chunks.

Never expose:

- Vector IDs
- Internal metadata
- Database IDs
- File paths

Always include document citations.

Reject answers when confidence is low.

---

# 12. AI Output Validation

Validate every AI response.

Check:

- Empty output
- JSON format
- Required fields
- Maximum length
- Sensitive information
- Hallucinated citations

Do not save invalid outputs.

---

# 13. Security Headers

Enable:

- Content-Security-Policy
- X-Frame-Options
- X-Content-Type-Options
- Referrer-Policy
- Permissions-Policy
- Strict-Transport-Security

Disable unnecessary browser features.

---

# 14. CORS

Never use:

*

Use allowlist only.

Example:

- localhost
- Production Frontend URL

Reject unknown origins.

---

# 15. HTTPS

Production must use HTTPS.

Redirect HTTP to HTTPS.

Cookies:

- HttpOnly
- Secure
- SameSite=Strict

---

# 16. Error Handling

Never return:

- Stack trace
- SQL error
- File path
- API key
- Environment variables
- Internal exception

Frontend receives generic messages only.

Detailed logs remain server-side.

---

# 17. Logging

Log:

- Login
- Logout
- Upload
- AI Request
- Database Error
- Permission Denied
- Admin Actions

Never log:

- Password
- JWT
- API Keys
- Resume Content
- Employee PII

---

# 18. AI Cost Protection

Before calling LLM:

- Validate
- Clean
- Normalize
- Process with Pandas
- Apply business rules
- Query database
- Search vector DB

Call AI only if necessary.

Cache repeat responses.

Use smallest suitable model.

---

# 19. Resume Security

Extract:

- Name
- Skills
- Experience
- Education

Remove temporary files immediately.

Never expose resumes publicly.

Store only required data.

---

# 20. Employee Data Protection

Treat as confidential:

- Salary
- Performance
- Attendance
- Medical
- Personal Details

Only authorized users may access employee records.

---

# 21. Deployment Security

Production Checklist

✓ Environment variables configured

✓ Debug mode disabled

✓ HTTPS enabled

✓ CORS configured

✓ Rate limiting enabled

✓ Logging enabled

✓ Secure headers enabled

✓ Database backups enabled

✓ API keys rotated

✓ Secrets removed from repository

---

# 22. Development Rules

Before every commit:

- Check for secrets
- Check .gitignore
- Check environment variables
- Check logs
- Check API responses
- Run security tests

Never push secrets to GitHub.

---

# 23. Antigravity Rules

Antigravity must NEVER:

- Hardcode credentials
- Remove validation
- Disable authentication (pre-wiring must not be bypassed)
- Disable rate limiting
- Disable logging
- Return stack traces
- Expose environment variables
- Skip authorization (pre-wiring must not be bypassed)
- Trust frontend validation
- Send raw user input directly to LLM

Antigravity must ALWAYS:

- Use .env
- Validate requests
- Use parameterized queries
- Follow layered architecture
- Keep business logic in services
- Keep routes thin
- Apply security middleware
- Preserve this document

---

# Final Rule

Security is mandatory.

No feature is considered complete until it satisfies every rule in this document.