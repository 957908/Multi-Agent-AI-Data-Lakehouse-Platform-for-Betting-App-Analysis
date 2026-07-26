# 🛡️ SentinelX Trust AI
> **Multi-Agent AI Data Lakehouse Platform for Betting App Analysis**

---

## 🌟 Overview
**SentinelX Trust AI** is a production-ready AI-driven Data Intelligence platform designed to monitor, ingest, clean, stream, and analyze transaction data from digital platforms. It integrates automated browser scraping, distributed message streaming, big data lakehouse architectures, and local multi-agent AI networks to deliver instant risk mitigation and analytics.

---

## 🚀 Key Modules
The codebase is divided into modular monolithic components:

*   **🌐 Frontend Dashboard (`/frontend`):** A premium, responsive web app built using **Next.js 15, React, TypeScript, Tailwind CSS, and shadcn/ui** to visualize risk profiling, transaction histories, and AI analysis reports.
*   **🕷️ Data Acquisition Layer (`/scraper`):** High-performance automated web scraping engines using **Playwright** and **Scrapy** to handle browser sessions, bypass security prompts, and capture payment options/transactions securely.
*   **🏗️ Data Engineering Pipeline (Planned):** Built with **Apache Kafka, Apache Spark, MinIO, and Apache Iceberg** to form a Bronze-Silver-Gold lakehouse tier.
*   **🤖 AI & Analytics Engine (Planned):** Orchestrated by **LangGraph** and **LangChain** utilizing local **Ollama** models and **FAISS** vector search for semantic pattern matching.
*   **⚡ FastAPI Backend Services (Planned):** Asynchronous, high-performance API services structured into router, service, and repository layers for database transactions and configuration management.

---

## 📂 Directory Layout
```text
.
├── .github/                   # GitHub action workflows, Issue and PR templates
├── docs/                      # Standardized project documentation
│   ├── Project Vision/        # Project overview and vision briefs
│   ├── PRD/                   # Product Requirements Document
│   ├── Architecture/          # TRD, rules, coding specs, and design system guidelines
│   ├── API Design/            # API routing and scraping specs
│   ├── Sprint Reports/        # living memory logs and implementation roadmaps
│   ├── ADR/                   # Architecture Decision Records
│   ├── Risk Register/         # Active technical and security risk logs
│   ├── CHANGELOG/             # Release changelog tracking
│   └── README.md              # Documentation index mapping
├── frontend/                  # Next.js frontend application source
├── scraper/                   # Playwright/Scrapy core data acquisition source
├── .gitignore                 # Root level git ignore policies
└── README.md                  # Root project overview (this file)
```

---

## 🌲 Git Branching & Workflow
We follow a modified **GitFlow** branching strategy. Developers must never push directly to `main` or `develop`.

```text
main           [Protected] Production releases only (tagged releases)
 │
develop        [Protected] Active integration branch
 │
 ├── feature/*  Developer feature branches (e.g., feature/rayri-payment-acquisition)
 ├── release/*  Staging and pre-release configuration testing
 └── hotfix/*   Emergency production patches
```

### Pull Request & Merge Guidelines
1. Branch out from `develop` using prefix standard (`feature/*`, `fix/*`, `docs/*`).
2. Before submitting a PR, ensure local builds succeed and linting is clean.
3. Use the provided [PR Template](.github/pull_request_template.md) and link the corresponding GitHub Issue.
4. Obtain Tech Lead approval before final merging.

---

## ⚙️ Local Development Setup

### Prerequisites
*   Python 3.11+
*   Node.js 20+ (npm)
*   Docker & Docker Compose

### 1. Data Acquisition Engine
Navigate to `/scraper`:
```bash
pip install -r requirements.txt
playwright install
python scraper/main.py
```

### 2. Frontend Dashboard
Navigate to `/frontend`:
```bash
npm install
npm run dev
```

---

## 👥 Core Development Team
*   **Tech Lead:** Architecture & Final Approvals
*   **Radhika Patil:** Senior DevOps & Engineering Operations
*   **Rayri Sharma:** Senior Data Acquisition Engineer
*   **Priya Iyer:** Senior Data Engineer
*   **Arjun Mehta:** Senior AI & Backend Engineer
