# Antigravity Development Rules

## Objective
Antigravity must follow these rules throughout the project. Never change architecture, technology, or security decisions unless explicitly instructed.

## General Rules
- Read all files in `/docs` before generating code.
- Follow the documented architecture exactly.
- Modify only the files required for the requested task.
- Never refactor unrelated code.
- Keep the project modular and production-ready.

## Technology Rules
- Backend: FastAPI only.
- Frontend: HTML, Tailwind CSS, JavaScript, Jinja2.
- ORM: SQLAlchemy 2.x.
- Validation: Pydantic v2.
- Database: PostgreSQL (Neon).
- Vector Store: pgvector.
- AI Framework: LangChain.
- AI Provider: NVIDIA NIM (must be model-provider-flexible via config/adapter/router).

Do not replace any technology without approval.

## Folder Rules
- Keep routes, services, repositories, schemas, and models separate.
- Do not place business logic inside routes.
- Do not place database queries inside routes.
- Do not create unnecessary folders or duplicate code.

## AI Rules
- AI/LLM Provider Flexibility: The codebase must be fully model-provider-flexible. All AI model IDs, API keys, base URLs, timeouts, max tokens, and routing rules must come from environment variables and centralized config only.
- No direct provider API calls: No service, route, prompt template, or feature module may hardcode model names or instantiate provider SDKs directly. All requests must route through:
  1. Centralized config (`app/core/config.py`)
  2. Generic AI client adapter
  3. Model router (`app/services/ai/model_router.py`)
- Use Pandas before calling any LLM whenever possible.
- Use the model router for every AI request.
- Use the smallest suitable model first.
- Cache repeatable AI responses.
- Never send full resumes, PDFs, or database tables to the LLM.
- Never call the AI provider APIs directly from routes.

## RAG Rules
- Use RAG only for HR policy documents.
- Retrieve only the top relevant chunks.
- Always return document citations.
- Never send the entire document to the LLM.

## Security Rules
- Never hardcode API keys or secrets.
- Always read configuration from `.env`.
- Validate every request.
- Protect routes with authentication and authorization (deferred for V1; pre-wired via company_id context).
- Apply rate limiting where required.
- Never expose stack traces or internal errors.
- Never trust frontend validation.

## Database Rules
- Use SQLAlchemy ORM only.
- Use Alembic for schema changes.
- Use parameterized queries.
- Never concatenate SQL strings.

## Coding Rules
- Write clean, readable code.
- Use meaningful names.
- Keep functions small and focused.
- Remove unused imports and dead code.
- Avoid duplicated logic.

## Git Rules
- Do not modify `.env`.
- Do not commit secrets.
- Keep commits focused on one task.
- Do not rename files unless requested.

## Permanent Development Workflow
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


## Never Do
- Change project architecture.
- Replace libraries or frameworks.
- Disable security features.
- Skip validation.
- Add unnecessary dependencies.
- Delete existing functionality without permission.
- Generate placeholder code when a complete implementation is possible.

## Final Rule
If any user request conflicts with the documentation in `/docs`, ask for confirmation before changing the architecture or breaking established project rules.