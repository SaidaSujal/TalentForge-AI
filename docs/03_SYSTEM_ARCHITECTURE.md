# System Architecture
## Pattern
TalentForge AI uses a modular monolith architecture.  
One FastAPI backend contains separate modules for HR features, AI services, database, security, and files.
## High-Level Flow
User → Frontend → FastAPI API → Service Layer → Database / Vector DB / AI Provider API → Response
## Main Components
Frontend: pages, forms, dashboards, upload screens, chat UI  
FastAPI Backend: routes, validation, auth (deferred for V1; pre-wired), services  
Database: users, employees, candidates, reviews, training, audit logs  
Vector Store: HR policy embeddings and citations  
AI Layer: model router, prompt builder, cache, generic client adapter  
ML Layer: attrition prediction and analytics  
Security Layer: auth (deferred for V1; pre-wired), rate limiting, validation, headers, safe logging
## Request Flow
1. User submits request from UI.
2. Frontend calls FastAPI endpoint.
3. Backend validates input with Pydantic.
4. Security middleware checks auth (deferred for V1; pre-wired), CORS, rate limit.
5. Service layer processes data locally first.
6. Pandas/ML/SQL handles deterministic work.
7. LLM is called only if needed.
8. Result is cached when possible.
9. Clean response is returned to frontend.
## AI Flow
Input → validation → cleaning → local processing → prompt builder → model router → client adapter → AI Provider API → output validation → response
## RAG Flow
Upload policy → parse text → chunk text → embed chunks → store vectors → retrieve top chunks → ask LLM → answer with sources
## Deployment View
Browser UI runs client-side.  
FastAPI backend runs on Render/Railway.  
PostgreSQL runs on Neon.  
Configured AI model provider (e.g., NVIDIA NIM or alternative) handles LLM and embeddings.  
File uploads are temporary and deleted after processing.
## Architecture Rules
Do not call LLM directly from routes.  
Routes call services only.  
Services call AI layer only when required.  
All secrets come from environment variables.  
All user input must be validated before database, filesystem, or LLM use.