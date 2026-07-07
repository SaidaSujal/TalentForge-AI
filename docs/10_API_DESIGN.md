# API Design
## Base
Backend framework: FastAPI  
API prefix: `/api/v1`  
Response format: JSON  
Validation: Pydantic v2  
Authentication: Authentication and RBAC are deferred until after all 8 core modules work. For V1, use demo-user/current-company architecture only. All services and repositories must accept company_id so JWT/RBAC can be added later without refactor.
## Response Standard
Success:
`{ "success": true, "data": {}, "message": "OK" }`
Error:
`{ "success": false, "error": "Safe user message" }`
Never return stack traces, file paths, SQL errors, or secrets.
## Route Groups
Auth: `/api/v1/auth`  
Users: `/api/v1/users`  
Employees: `/api/v1/employees`  
Candidates: `/api/v1/candidates`  
Jobs: `/api/v1/jobs`  
Policies: `/api/v1/policies`  
Chatbot: `/api/v1/chatbot`  
Performance: `/api/v1/performance`  
Attrition: `/api/v1/attrition`  
Training: `/api/v1/training`  
Interviews: `/api/v1/interviews`  
Analytics: `/api/v1/analytics`  
AI Usage: `/api/v1/ai-usage`
## Core Endpoints
`POST /auth/signup`  
`POST /auth/login`  
`POST /auth/logout`  
`GET /users/me`  
`GET /dashboard/summary`
`GET /health`
## Resume APIs
`POST /candidates/upload-resume`  
`POST /candidates/screen`  
`GET /candidates`  
`GET /candidates/{candidate_id}`  
`PATCH /candidates/{candidate_id}/status`
## Policy RAG APIs
`POST /policies/upload`  
`GET /policies`  
`DELETE /policies/{policy_id}`  
`POST /chatbot/ask`
## HR Feature APIs
`POST /jobs/generate`  
`POST /onboarding/generate`  
`POST /performance/generate-review`  
`POST /attrition/predict`  
`POST /training/recommend`  
`POST /interviews/generate-kit`
## API Rules
All inputs must be validated.  
All protected APIs must check authentication (deferred for V1; pre-wired with company_id).  
All role-specific APIs must check authorization (deferred for V1; pre-wired with company_id).  
All LLM APIs must use rate limiting.  
All file APIs must validate file type and size.  
Routes must call services, not database or LLM directly.
## Status Codes
200: success  
201: created  
400: bad request  
401: unauthenticated  
403: forbidden  
404: not found  
422: validation error  
429: rate limited  
500: generic server error
## Security
Use CORS allowlist.  
Use secure headers.  
Use safe error messages.  
Log detailed errors server-side only.  
Never expose internal IDs when avoidable.