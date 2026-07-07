# Deployment
## Goal
Deploy TalentForge AI with minimum complexity and no local-only dependencies.
## Services
Backend: Render or Railway  
Database: Neon PostgreSQL  
Vector Store: PostgreSQL pgvector  
AI: NVIDIA NIM API  
Frontend: served by FastAPI templates/static files
## Production Rules
Do not use SQLite in production.  
Do not store uploads permanently on server disk.  
Do not hardcode secrets.  
Do not enable debug mode.  
Do not use wildcard CORS.
## Environment Variables
`DATABASE_URL`  
`NVIDIA_API_KEY`  
`JWT_SECRET_KEY`  
`APP_ENV`  
`FRONTEND_URL`  
`CORS_ORIGINS`  
`MAX_UPLOAD_MB`  
`LLM_RATE_LIMIT`
## Build Command
`pip install -r requirements.txt`
## Start Command
`uvicorn app.main:app --host 0.0.0.0 --port $PORT`
## Database Setup
Create Neon database.  
Enable pgvector extension.  
Add `DATABASE_URL` to deployment environment.  
Run Alembic migrations before production use.
## File Handling
Uploaded resumes and policies are saved temporarily.  
Files are validated before parsing.  
Temporary files are deleted after processing.  
Only extracted required text and metadata are stored.
## Security Checklist
HTTPS enabled.  
CORS allowlist configured.  
Rate limiting enabled.  
Security headers enabled.  
Debug disabled.  
Secrets set in dashboard environment variables.  
Logs do not contain PII or API keys.
## Deployment Flow
Push code to GitHub.  
Connect repository to Render/Railway.  
Set environment variables.  
Deploy backend.  
Run database migrations.  
Test health endpoint.  
Test auth (deferred for V1; verify demo user details load).  
Test one AI endpoint.  
Test file upload.  
Test RAG chatbot.
## Health Check
Endpoint: `/api/v1/health`  
Expected: `{ "status": "healthy" }`
## Failure Rules
If deployment fails, check logs.  
Do not expose logs publicly.  
Fix one error at a time.  
Never paste secrets into GitHub issues or public chats.