# TalentForge AI — Definition of Ready

## Purpose
Definition of Ready decides when a feature is ready to be implemented.

A feature must not be started until these requirements are clear. This prevents Antigravity or any AI agent from generating incomplete, inconsistent, or insecure code.

## Global Definition of Ready

A feature is ready for implementation only when:

- The feature scope is clear.
- Required input fields are known.
- Expected output is known.
- Database tables are known.
- API endpoints are known.
- Validation rules are known.
- Security risks are considered.
- AI model routing is decided.
- Cache strategy is decided.
- Export requirement is known.
- Dashboard impact is known.
- Human review warning requirement is known.
- Tests required are known.

## Required Questions Before Any Feature

## Product

- What user problem does this solve?
- Which HR role uses it?
- What is the expected workflow?
- What is out of scope?

## Data

- What data does the feature need?
- Which tables are involved?
- Is the data tenant-owned?
- Does it require `company_id`?
- Does it store AI history?

## AI

- Is AI truly needed?
- Can local logic solve part of the task first?
- Which NVIDIA model should be used?
- Is the response cacheable?
- What prompt template is needed?
- What output schema should be validated?
- Does the output need explainability?

## Security

- What user inputs are accepted?
- What validation is required?
- Is file upload involved?
- Could prompt injection happen?
- Could tenant data leak?
- Does it expose sensitive HR data?

## UI

- What page or component is needed?
- What loading state is needed?
- What empty state is needed?
- What error state is needed?
- Does it need charts or tables?
- Does it need export buttons?

## Testing

- What happy path tests are needed?
- What error path tests are needed?
- What validation tests are needed?
- What AI/mock tests are needed?

## Feature Ready Checklist

Before implementation, confirm:

- [ ] Module documented
- [ ] Route names planned
- [ ] Service responsibility clear
- [ ] Repository responsibility clear
- [ ] Pydantic schemas planned
- [ ] Database model planned
- [ ] company_id handling planned
- [ ] AI model routing planned
- [ ] Prompt template planned
- [ ] AI output schema planned
- [ ] Cache strategy planned
- [ ] Error handling planned
- [ ] UI states planned
- [ ] Export requirement planned
- [ ] Test cases planned

## Module-Specific Readiness

## Resume Screening

Ready only when PDF + DOCX parsing, JD inputs, candidate status workflow, resume scoring JSON, export formats, and human review warning are defined.

## HR Policy Chatbot

Ready only when document formats, chunking strategy, citation format, fallback answer, pgvector schema, and prompt injection rules are defined.

## JD Generator

Ready only when input fields, JD sections, export formats, cache key strategy, and small model routing are confirmed.

## Onboarding Assistant

Ready only when new hire fields, task tracking, copy-only email text, and export format are defined.

## Performance Review

Ready only when review inputs, rating explanation, bias check, human review warning, and export format are defined.

## Attrition Prediction

Ready only when local scoring factors, risk thresholds, AI retention trigger, and decision-support warning are defined.

## Learning Recommendation

Ready only when current role, target role, skills input, skill gap output, training tracking, and export format are defined.

## Interview Kit Generator

Ready only when role inputs, interview structure, rubric format, export format, and small model routing are confirmed.

## Final Rule

If a feature is not ready, do not start coding it. First update the relevant documentation, then implement.
