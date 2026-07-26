# Development Rules

Version: 1.0
Project: SentinelX AI – Multi-Agent Data Lakehouse Platform
Status: Active

---

# 1. Purpose

This document defines the engineering standards, coding conventions,
approved technologies, security policies, AI development guidelines,
and operational boundaries for the SentinelX AI project.

Every contributor, including AI coding assistants, must follow these rules.

---

# 2. Core Principles

- Build production-quality code.
- Prefer readability over cleverness.
- Keep the project modular.
- Write secure code by default.
- Follow SOLID principles.
- Avoid unnecessary complexity.
- Every feature must be documented.
- Every feature should be testable.

---

# 3. AI Development Rules

The AI assistant must:

✔ Explain code before generating it.

✔ Generate clean and readable code.

✔ Follow project folder structure.

✔ Reuse existing modules.

✔ Avoid duplicate code.

✔ Generate type-safe code.

✔ Follow naming conventions.

✔ Add comments only where necessary.

✔ Suggest improvements.

✔ Explain errors.

The AI must never:

❌ Rewrite unrelated files.

❌ Break existing features.

❌ Generate insecure code.

❌ Hardcode secrets.

❌ Ignore project architecture.

❌ Introduce unnecessary dependencies.

---

# 4. Approved Technologies

Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS
- shadcn/ui

Backend

- Python
- FastAPI
- SQLAlchemy
- Alembic

Database

- PostgreSQL

Scraping

- Playwright
- Scrapy
- BeautifulSoup

Streaming

- Kafka

Big Data

- Spark

Lakehouse

- Iceberg
- MinIO

AI

- LangChain
- LangGraph
- Ollama
- FAISS
- Sentence Transformers

Deployment

- Docker
- Docker Compose

Monitoring

- Prometheus
- Grafana

---

# 5. Technologies to Avoid

Avoid unless discussed first.

- Django
- Flask
- MongoDB
- Firebase
- PHP
- jQuery

Reason

Keep architecture consistent.

---

# 6. Folder Rules

Each folder must have one responsibility.

Example

backend/api

Only API routes.

backend/services

Business logic only.

backend/models

Database models only.

backend/schemas

Pydantic schemas only.

No business logic inside routes.

---

# 7. Coding Standards

Python

PEP8

Type hints required

Docstrings for public functions

Maximum function size

~50 lines (preferred)

Maximum file size

~500 lines (split when larger)

---

# 8. Naming Conventions

Classes

PascalCase

Example

PaymentAnalyzer

Variables

snake_case

Example

payment_type

Functions

snake_case

Example

calculate_risk()

Constants

UPPER_CASE

Example

MAX_RETRY

---

# 9. Error Handling

Never ignore exceptions.

Always

Log

Return meaningful messages

Handle expected failures

Example

try

except

finally

Avoid

except:

Use

except ValueError

except HTTPException

etc.

---

# 10. Logging Rules

Use Python logging.

Levels

INFO

WARNING

ERROR

CRITICAL

Never use print() in production code.

---

# 11. Security Rules

Never store passwords.

Never commit secrets.

Use .env

Hash passwords

Validate inputs

Escape SQL

Use JWT Authentication

Enable CORS correctly

---

# 12. API Rules

RESTful APIs

Consistent response format

Proper HTTP Status Codes

Version APIs

/api/v1/

Document using Swagger.

---

# 13. Database Rules

Use PostgreSQL.

Never write raw SQL unless required.

Use SQLAlchemy ORM.

Use Alembic for migrations.

Normalize tables.

Create indexes when necessary.

---

# 14. Git Rules

One feature per branch.

Meaningful commit messages.

Example

feat: add scraper service

fix: resolve login issue

docs: update architecture

---

# 15. Testing Rules

Every service should be testable.

Unit Tests

Integration Tests

API Tests

---

# 16. Documentation Rules

Every module must include:

Purpose

Inputs

Outputs

Dependencies

Example usage

---

# 17. Performance Rules

Avoid duplicate queries.

Use async where appropriate.

Cache repeated operations.

Paginate large datasets.

---

# 18. Operational Boundaries

Only scrape publicly accessible data.

Respect website policies.

Do not bypass authentication.

Do not collect private user information.

Use the project only for educational and research purposes.

---

# 19. Code Review Checklist

Before merging:

✓ Code builds successfully

✓ Tests pass

✓ Documentation updated

✓ No secrets committed

✓ Naming conventions followed

✓ Error handling implemented

✓ Logging added

✓ Architecture respected

---

# 20. Definition of Done

A feature is complete only if:

✓ Code implemented

✓ Tested

✓ Documented

✓ Reviewed

✓ Committed

✓ Working locally

---

End of Development Rules