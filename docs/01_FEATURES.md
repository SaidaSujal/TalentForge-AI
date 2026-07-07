# Features

## Overview

TalentForge AI consists of eight AI-powered HR modules. Each module works independently while sharing database, AI services, backend infrastructure, and future authentication (pre-wired with company_id for V1).

---

# Feature 1 — Resume Screening

## Purpose

Automatically analyze resumes and rank candidates.

## Input

- PDF/DOCX Resume
- Job Description

## Local Processing

- Text extraction
- Regex
- Pandas cleaning
- Skill extraction
- Education extraction
- Experience calculation

## AI Tasks

- Resume summary
- Candidate strengths
- Weaknesses
- Skill gap analysis

## Output

- Match Score
- Resume Summary
- Missing Skills
- Hiring Recommendation

---

# Feature 2 — HR Policy Chatbot

## Purpose

Answer HR policy questions using company documents.

## Input

Employee Question

## Technologies

- RAG
- LangChain
- NVIDIA Embeddings
- Vector Database

## Output

Grounded answer with document citations.

---

# Feature 3 — Job Description Generator

## Purpose

Generate professional Job Descriptions.

## Inputs

- Job Title
- Skills
- Experience
- Department

## Output

- Responsibilities
- Qualifications
- Required Skills
- Preferred Skills

---

# Feature 4 — Employee Onboarding Assistant

## Purpose

Guide newly hired employees.

## Features

- Welcome Guide
- Company Policies
- Required Documents
- First Week Checklist
- FAQ

---

# Feature 5 — Performance Review Generator

## Purpose

Generate structured employee reviews.

## Local Processing

- Attendance
- KPI Analysis
- Performance Metrics

## AI Output

- Performance Summary
- Strengths
- Weaknesses
- Improvement Suggestions

---

# Feature 6 — Attrition Prediction

## Purpose

Predict employee resignation risk.

## ML Inputs

- Attendance
- Salary
- Overtime
- Satisfaction
- Promotions
- Department

## Output

- Attrition Probability
- Risk Level
- Retention Suggestions

---

# Feature 7 — Learning Recommendation System

## Purpose

Recommend personalized employee learning paths.

## Inputs

- Skills
- Role
- Performance

## Output

- Recommended Courses
- Learning Path
- Certifications

---

# Feature 8 — Interview Kit Generator

## Purpose

Generate interview questions automatically.

## Inputs

- Job Role
- Skills
- Experience

## Output

- Technical Questions
- HR Questions
- Scenario Questions
- Expected Answers
- Evaluation Rubric

---

# Shared Features

- Authentication (deferred for V1, pre-wired with company_id)
- Dashboard
- Notifications
- Analytics
- Search
- File Upload
- User Profile
- Admin Panel
- Activity Logs
- AI Usage Tracking

---

# Future Features

- Voice HR Assistant
- Video Interview Analysis
- Email Automation
- ATS Integration
- Payroll Integration
- Calendar Integration
- Multi-Company Support
- Mobile Application

---

**End of 01_FEATURES.md**