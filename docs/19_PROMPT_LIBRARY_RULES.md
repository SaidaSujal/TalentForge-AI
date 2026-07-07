# TalentForge AI — AI Prompt Library Rules

## Purpose
This document defines how prompts must be organized, written, reviewed, and used in TalentForge AI.

Prompts are production logic. They must not be scattered randomly inside routes or services.

## Prompt Location

All prompt templates must live inside:

```text
app/services/ai/prompts/
```

Recommended files:

```text
app/services/ai/prompts/
├── __init__.py
├── resume_prompts.py
├── policy_prompts.py
├── jd_prompts.py
├── onboarding_prompts.py
├── performance_prompts.py
├── attrition_prompts.py
├── learning_prompts.py
├── interview_prompts.py
└── admin_insight_prompts.py
```

## Prompt Rules

- No prompts inside route files.
- Avoid long prompts directly inside service methods.
- Prompts must use clear delimiters for user content.
- Prompts must define expected JSON output when structured output is required.
- Prompts must include safety instruction for HR-sensitive outputs.
- Prompts must not ask the model to make final employment decisions.
- Prompts must not include secrets or internal configuration.

## Required Delimiters

Use this structure for user input:

```text
[USER INPUT START]
{sanitized_user_input}
[USER INPUT END]
```

Use this structure for RAG context:

```text
[CONTEXT START]
{retrieved_policy_chunks}
[CONTEXT END]
```

Use this structure for output rules:

```text
[OUTPUT FORMAT]
Return valid JSON only.
No markdown.
No extra explanation outside JSON.
```

## Prompt Injection Defense

Every prompt-building function must receive sanitized input.

The AI layer must reject or escape common injection patterns:

- Ignore previous instructions
- Reveal system prompt
- System:
- Assistant:
- Developer:
- You are now
- Forget your instructions
- Act as a different assistant

## Prompt Function Pattern

Each prompt function should:

- Accept already validated inputs.
- Accept only the minimum required data.
- Truncate or summarize large inputs before prompt construction.
- Return a string prompt.
- Never call the AI model itself.

## Output Validation

Every prompt that requests JSON must have a matching Pydantic response schema.

If the LLM response is invalid:

- Do not save it as final output.
- Store failure metadata in AI history.
- Return a safe error or retry once with a correction prompt.

## Model Routing

Prompts do not choose models.

The model router chooses models based on task type:

- JD, emails, interview kits → small model
- Resume, policy, performance, learning → large model
- Admin insights → advanced model
- Embeddings → embedding model

## Human Review Warnings

Sensitive HR prompts must include:

```text
This is an AI-generated recommendation. Human HR review is required before action.
```

Sensitive tasks:

- Resume screening
- Performance review
- Attrition prediction
- Retention strategy
- Salary revision suggestion
- Promotion readiness

## Prompt Review Checklist

- [ ] User input is delimited
- [ ] Context is delimited
- [ ] Output schema is defined
- [ ] Max token target is known
- [ ] Model route is known
- [ ] Sensitive HR warning included when required
- [ ] No raw full documents are inserted
- [ ] No secrets are included
- [ ] Matching Pydantic schema exists
