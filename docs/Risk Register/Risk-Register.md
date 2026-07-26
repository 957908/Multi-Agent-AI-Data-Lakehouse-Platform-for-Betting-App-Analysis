# Risk Register - SentinelX Trust AI

This document tracks identified project risks, their impact, likelihood, and mitigation strategies. It is updated weekly during engineering operations review.

## Active Risks

| Risk ID | Description | Category | Likelihood | Impact | Mitigation Strategy | Owner | Status |
|---|---|---|---|---|---|---|---|
| **RSK-001** | Large Data Processing & Database Scale | Technical | Medium | High | Use Apache Iceberg, MinIO, and Spark for the lakehouse layout, and utilize PostgreSQL connection pooling. | Priya Iyer | Open |
| **RSK-002** | AI Model Inaccuracies / Hallucinations | Technical | Medium | High | Implement strict output schema validation, prompt engineering reviews, and ground model responses using RAG with local FAISS vector stores. | Arjun Mehta | Open |
| **RSK-003** | Web Scraper Session Expiration / IP Blocking | Technical | High | High | Implement session persistence in Playwright, randomized user agents, delay intervals, and proxy integration. | Rayri Sharma | Open |
| **RSK-004** | Untracked Configuration / Secret Leakage | Security | Low | Critical | Enforce strict git status hooks, keep `.env` in the root `.gitignore`, and use Docker environment injection. | Radhika Patil | Closed (Mitigated) |
