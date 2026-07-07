# Frontend Architecture
## Approach
Use server-rendered HTML pages with Jinja2 templates, Tailwind CSS, and JavaScript.  
Do not use Streamlit.  
Do not build React/Next.js for V1 unless required later.
## Goals
Clean UI, fast loading, simple deployment, responsive design, and easy integration with FastAPI.
## Main Pages
Dashboard: HR metrics, charts, AI usage, recent activity  
Resume Screening: upload resumes, enter JD, view ranked candidates  
Policy Chatbot: chat UI with citations  
JD Generator: form and generated JD preview  
Onboarding: employee onboarding plans and checklist  
Performance: review generator and history  
Attrition: risk form, prediction result, retention suggestions  
Training: skill gap and learning recommendations  
Interview Kit: question generator and rubric  
Admin: users, roles, logs, settings
## UI Structure
templates/: Jinja2 HTML pages  
static/css/: custom CSS  
static/js/: page JavaScript  
static/assets/: icons, images, logos
## Frontend Rules
Frontend must not contain API keys.  
Frontend must not perform protected logic alone.  
Frontend must not trust hidden inputs for security.  
All important checks happen again on backend.
## API Communication
Use fetch() to call FastAPI endpoints.  
Show loading states for AI operations.  
Show friendly errors, not raw backend errors.  
Disable submit buttons during processing.
## UX Rules
Use modern HR SaaS style.  
Use cards, tables, charts, filters, and modals.  
Every AI output must show "Human review required" for sensitive HR decisions.  
Uploaded file status must be visible.
## Security Rules
Escape rendered user content.  
Do not render raw HTML from LLM output.  
Do not store tokens in localStorage.  
Use secure cookies when auth is implemented.