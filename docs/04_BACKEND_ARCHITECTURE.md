# Backend Architecture
## Framework
Use FastAPI as the only backend framework.  
Do not use Flask or Streamlit.
## Layers
Routes: receive HTTP requests and return responses.  
Schemas: validate request and response data with Pydantic v2.  
Services: contain business logic for each HR feature.  
Repositories: handle database queries only.  
AI Layer: handles provider-agnostic model adapters, prompt building, caching, and routing.  
Security Layer: handles auth, rate limiting, headers, and validation.
## Backend Flow
Request → Route → Schema Validation → Security Check → Service → Repository/AI/ML → Response
## Main Modules
auth: deferred for V1, pre-wired with company_id context; login, signup, JWT, sessions post-V1  
users: user profile and roles  
candidates: resume screening  
employees: employee records  
policies: policy upload and RAG chatbot  
jobs: JD generation  
onboarding: onboarding assistant  
performance: performance reviews  
attrition: ML risk prediction  
training: learning recommendations  
interviews: interview kit generator  
analytics: dashboard metrics  
ai: generic client adapter, model router, prompt templates  
core: config, database, logging, exceptions, security
## Route Rules
Routes must stay thin.  
No business logic inside routes.  
No direct AI provider calls inside routes (all AI requests must execute via service layer and the model router).  
No raw SQL inside routes.  
No file processing inside routes.
## Service Rules
Services clean and process data before AI calls.  
Use Pandas before LLM where possible.  
Call small model by default.  
Call large model only for complex reasoning.  
Cache repeated AI outputs.
## Database Rules
Use SQLAlchemy ORM.  
Use Alembic migrations.  
Use parameterized queries only.  
Never build SQL using string concatenation.
## Error Handling
Return generic errors to frontend.  
Log detailed errors only on server.  
Never expose stack traces, paths, secrets, or database errors.
## Security Rules
Validate every request.  
Rate limit every endpoint.  
Protect routes with JWT (deferred for V1; pre-wired via company_id context).  
Use secure cookies when sessions are added.  
Sanitize file uploads before processing.