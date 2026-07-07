# AI Model Routing
## Provider
Use NVIDIA NIM API for LLMs and embeddings.
## Default Rule
Use the smallest suitable model first.  
Use large models only for complex reasoning.
## Models
Small model: `meta/llama-3.1-8b-instruct`  
Large model: `meta/llama-3.1-70b-instruct`  
Advanced model: `nvidia/llama-3.3-nemotron-super-49b-v1.5`  
Embedding model: `nvidia/nv-embed-v1`
## Routing Table
Simple chat, JD drafts, emails, interview questions → small model  
Resume scoring, policy reasoning, performance review → large model  
Admin insights, complex workforce analysis → advanced model  
Policy chunks and user questions → embedding model
## Cost Rules
Cache every repeatable AI response.  
Limit max tokens per request.  
Do Pandas preprocessing before LLM.  
Never send full resumes, PDFs, or database rows to LLM.
## Safety Rules
All prompts must use delimiters.  
Raw user input must not go directly into system prompts.  
Validate LLM output before saving to database.  
AI outputs are recommendations, not final HR decisions.

## Model Provider Flexibility & Decoupling
The project must be model-provider-flexible to prevent vendor lock-in and ease transition between providers or hosted endpoint updates.
- **Centralized Configuration:** All AI model IDs, API keys, base URLs, timeout values, retry counts, max token limits, and routing alias associations must come from environment variables (`.env`) and the centralized config (`app/core/config.py`).
- **AI Client Adapter:** All AI model requests must execute through a generic AI client adapter. No service, route, prompt file, or feature module may instantiate provider-specific SDK clients directly or hardcode direct API endpoints.
- **Model Router:** All AI interactions must query the `model_router` to resolve task aliases (e.g., `jd_draft`, `resume_scoring`) into model aliases.
- **Decoupled Updates:** If model names, keys, or compatible hosted endpoints change later, updates must be made only to `.env` or deployment environment variables. No code changes in feature modules or services are permitted for these configuration updates.