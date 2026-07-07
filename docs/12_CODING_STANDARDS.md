# Coding Standards
## Python
Use Python 3.11+.  
Use type hints for functions.  
Use clear names, not shortcuts.  
Use small functions with one purpose.  
Use docstrings for services and complex logic.
## Structure
Routes stay thin.  
Business logic goes in services.  
Database logic goes in repositories.  
AI logic goes in AI layer.  
Validation goes in schemas.  
Shared config goes in core.
## Naming
Files: snake_case.py  
Classes: PascalCase  
Functions: snake_case  
Constants: UPPER_SNAKE_CASE  
API paths: kebab-case
## Formatting
Use Black for formatting.  
Use Ruff for linting.  
Use isort for imports.  
Keep imports clean and grouped.
## Error Handling
Use custom exceptions.  
Return safe user messages.  
Log detailed errors server-side only.  
Never expose stack traces.
## Security
No hardcoded secrets.  
No raw SQL string concatenation.  
No raw user input in prompts.  
No sensitive data in logs.  
Validate all request data.
## AI Code
All LLM calls go through model router.  
All prompts use delimiters.  
All repeatable outputs use cache.  
All AI output must be validated before saving.
## Comments
Comment why, not obvious what.  
Avoid noisy comments.  
Use TODO only with clear reason.
## Tests
Write tests for services, APIs, validation, auth, RAG, and security rules.