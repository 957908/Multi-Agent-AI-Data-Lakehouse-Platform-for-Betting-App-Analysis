# Structure

1. Project Mission

2. Development Principles

3. Approved Technology Stack

4. Forbidden Technologies

5. Coding Standards

6. Project Structure Rules

7. Frontend Rules

8. Backend Rules

9. Database Rules

10. AI & ML Rules

11. Security Rules

12. Error Handling

13. Logging Rules

14. API Rules

15. Testing Rules

16. Documentation Rules

17. Git Rules

18. Performance Rules

19. Code Review Checklist

20. AI Assistant Instructions

# Example Content
# 1. Project Mission
The goal is to build a production-ready AI Data Intelligence Platform.

Every implementation should prioritize:

- Readability
- Maintainability
- Scalability
- Security
- Performance
# 2. Development Principles
✅ Modular Code

✅ Clean Architecture

✅ SOLID Principles

✅ DRY

✅ KISS

✅ YAGNI

❌ No Quick Fixes

❌ No Hardcoded Secrets

❌ No Duplicate Logic
# 3. Approved Technologies
Frontend

✔ Next.js
✔ React
✔ TypeScript
✔ Tailwind
✔ shadcn/ui

Backend

✔ FastAPI
✔ SQLAlchemy
✔ Alembic

Database

✔ PostgreSQL

Scraping

✔ Playwright
✔ Scrapy

Big Data

✔ Kafka
✔ Spark

AI

✔ LangChain
✔ LangGraph
✔ Ollama
✔ FAISS

DevOps

✔ Docker
✔ Docker Compose
# 4. Forbidden Technologies
❌ jQuery

❌ PHP

❌ Flask

❌ SQLite (Production)

❌ Inline CSS

❌ Inline SQL

❌ Global Variables

❌ Hardcoded Passwords

❌ Random Folder Creation
5. Backend Rules
Every API

↓

Router

↓

Service

↓

Repository

↓

Database

Never access the database directly from API routes.

# 6. Frontend Rules
Page

↓

Component

↓

Hook

↓

API Service

Pages should never call APIs directly.

# 7. Database Rules
Every table

↓

created using Alembic migration

No manual schema changes.

Use UUID where appropriate.

Use timestamps.

Soft delete if needed.
# 8. AI Rules
LangGraph controls agents.

LangChain handles RAG.

Ollama runs models locally.

Agents must have a single responsibility.
# 9. Error Handling

Every API returns a consistent response:

{
  "success": true,
  "message": "",
  "data": {}
}
# 10. Security Rules
JWT Authentication

Environment Variables

bcrypt Password Hashing

HTTPS Ready

Input Validation

Rate Limiting

CORS Configuration
# 11. Logging
Application Logs

API Logs

Scraper Logs

Kafka Logs

AI Logs

Never use print() in production.

# 12. Git Rules
feature/auth

feature/scraper

feature/dashboard

feature/rag

fix/api

docs/trd

Commit example:

feat(scraper): add Playwright scraper for payment pages
# 13. AI Assistant Rules

हे आपल्या project साठी सर्वात महत्त्वाचं section असेल.

AI must:

✔ Explain before coding.

✔ Keep code modular.

✔ Follow existing folder structure.

✔ Never create duplicate functionality.

✔ Never replace working code without reason.

✔ Update documentation when architecture changes.

✔ Prefer maintainability over shortcuts.

✔ Use production-ready practices.

✔ Generate interview-quality code.

✔ Explain why a technology is chosen.

✔ Add comments only where they improve understanding.

✔ Suggest improvements without breaking existing modules.
