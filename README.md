<p align="center">
  <img src="https://img.shields.io/badge/SentinelX%20Trust%20AI-v1.0.0--RC1-cyan?style=for-the-badge&logo=ai&logoColor=white" alt="SentinelX Trust AI banner" />
</p>

<h1 align="center">🛡️ SentinelX Trust AI</h1>
<p align="center">
  <b>Multi-Agent AI Data Lakehouse Platform for Betting App Payment Analysis</b>
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue.svg?style=flat-square" alt="Python Version" /></a>
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-5.0.0-009688.svg?style=flat-square" alt="FastAPI" /></a>
  <a href="https://spark.apache.org/"><img src="https://img.shields.io/badge/PySpark-3.5.0-E25A1C.svg?style=flat-square" alt="PySpark" /></a>
  <a href="https://playwright.dev/"><img src="https://img.shields.io/badge/Playwright-1.40.0-2EAD33.svg?style=flat-square" alt="Playwright" /></a>
  <a href="https://www.docker.com/"><img src="https://img.shields.io/badge/Docker-Enabled-2496ED.svg?style=flat-square" alt="Docker" /></a>
  <a href="https://prometheus.io/"><img src="https://img.shields.io/badge/Prometheus-Telemetry-E6522C.svg?style=flat-square" alt="Prometheus" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square" alt="License" /></a>
</p>

---

## 📖 Overview
**SentinelX Trust AI** is an enterprise-grade, open-source-ready Multi-Agent AI Data Lakehouse Platform designed for automated browser telemetry acquisition, medallion data lakehouse processing, dynamic risk profiling, and trust score intelligence of betting app payment gateways.

It provides a complete end-to-end framework to:
1. **Scrape** hidden payment endpoints of betting sites (e.g. 1xBet, Melbet) using automated Playwright sessions.
2. **Process** raw data using PySpark into Bronze, Silver, and Gold Medallion Lakehouse structures.
3. **Analyze** risk profiles with Random Forest, Isolation Forest, and K-Means models.
4. **Index & Query** anomalies using Semantic FAISS vector indexes and Retrieval-Augmented Generation (RAG).
5. **Monitor** performance with Grafana dashboards, Prometheus telemetry metrics, and Nginx SSL proxy gateways.

---

## 🏗️ System Architecture & Data Flow

```mermaid
flowchart TD
    subgraph Data Acquisition ["1. Data Acquisition Layer (Rayri Sharma)"]
        Scrapers["Playwright Scrapers"] --> |Raw JSON| RawData["data/raw/"]
    end

    subgraph Data Lakehouse ["2. Data Engineering & Lakehouse (Priya Iyer)"]
        RawData --> Bronze["Bronze Layer (Raw Backups)"]
        Bronze --> Spark["PySpark Ingestion Engine"]
        Spark --> |Validation Failures| DLQ["output/dlq/ (Dead Letter Queue)"]
        Spark --> |Cleaned & Deduplicated| Silver["Silver Layer (payment_records)"]
        Silver --> |Pre-Aggregation| Gold["Gold Layer (gold_platform_analytics & insights)"]
    end

    subgraph AI Engine ["3. AI Intelligence Layer (Arjun Mehta)"]
        Gold --> TrustEngine["Rule-Based Trust Engine (0-100)"]
        Gold --> AIAnalysis["AI Risk & Report Generator"]
        Gold --> RAG["Provider-Agnostic RAG Search"]
    end

    subgraph Backend API ["4. FastAPI REST API (Arjun Mehta)"]
        TrustEngine & AIAnalysis & RAG & Silver & Gold --> API["FastAPI REST Server"]
        API --> Auth["JWT & Role-Based Security (RBAC)"]
        API --> Cache["In-Memory TTL Cache (<15ms)"]
    end

    subgraph Observability ["5. DevOps & Telemetry (Radhika Patil)"]
        API --> Metrics["/metrics (Prometheus Instrumentation)"]
        API --> Health["/api/v1/health (Uptime Monitoring)"]
    end
```

---

## ⚡ Core Platform Capabilities

*   **🛡️ Resilient Browser Scrapers:** Automated sessions built with Playwright and Scrapy. Bypasses cloudflare verification and scans payment gateways dynamically.
*   **📐 Medallion Data Lakehouse:** PySpark & Parquet/Delta Lake pipeline managing **Bronze** (raw ingestion), **Silver** (cleaned and deduplicated payment records), and **Gold** (pre-computed analytics) layers.
*   **🧠 Explainable Risk Scoring Engine:** Rule-based AI evaluates site reliability scores (0-100), risk flags, and confidence ratings, categorizing risks into `LOW`, `MEDIUM`, or `HIGH`.
*   **🔍 Semantic Vector Search & RAG:** Embeddings generated using `all-MiniLM-L6-v2` indexed in a FAISS vector database to answer natural language queries using a local LLM.
*   **⚡ Sub-15ms REST APIs:** FastAPI backend server with JWT, role-based access control (RBAC), and TTL caching delivering rapid responses.
*   **📊 Full-Stack Observability:** Live Next.js dashboard, Grafana metrics dashboards, and Nginx reverse SSL proxies.

---

## 📁 Repository Directory Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── api/v1/          # REST API Route Controllers & Endpoints
│   │   ├── config/          # Centralized Pydantic Settings & Environment Loaders
│   │   ├── core/            # Security (JWT/RBAC), Caching & Exception Handlers
│   │   ├── database/        # PostgreSQL Connection, Schemas & Seed Scripts
│   │   ├── repositories/    # Data Access Layer (PaymentRepository, GoldRepository)
│   │   ├── schemas/         # Pydantic Input/Output Schemas & Generic Envelopes
│   │   ├── services/        # AI Services (TrustEngine, RAGService, AIAnalysisService)
│   │   └── server.py        # Main FastAPI Application Server Entrypoint
│   └── tests/               # Unit, Integration, E2E Simulation & Benchmark Suites
├── etl/                     # PySpark Medallion Lakehouse Pipeline Jobs (Priya)
├── scrapers/                # Playwright Web Scraping Adapters & Controllers (Rayri)
├── frontend/                # Next.js 15 Tailwind Dashboard UI Console (Radhika)
├── docs/                    # Architectural & Operational Technical Documentation
├── RUN_GUIDE.md             # Consolidated Master Run & Operational Guide
├── docker-compose.yml       # Production Docker Container Orchestration
└── README.md                # Project Landing Page Documentation
```

---

## 🚀 Quick Start Guide

### 1. Launch Docker Infrastructure
Spin up PostgreSQL, FastAPI, Nginx Gateway, and Observability containers:
```bash
docker-compose -f deployment/docker-compose.yml up -d --build
```

### 2. Initialize PostgreSQL Schemas & Seed Data
Initialize database tables and populate records from the local environment:
```bash
# Create database tables
docker-compose -f deployment/docker-compose.yml exec backend python main.py --init-db

# Seed sample transactions & platform analytics
.\.venv\Scripts\python backend/app/database/seed_db.py
```

### 3. Launch Frontend Dashboard
Build and run the Next.js production console:
```bash
cd frontend
npm install
npm run build
npm run start
```
*The dashboard is now online at **[http://localhost:3000](http://localhost:3000)**.*

---

## 📊 Core API Endpoints

| Group | Method | Path | Description | Access |
| :--- | :--- | :--- | :--- | :--- |
| **Health** | `GET` | `/api/v1/health` | System health & DB connection status | Public |
| **Auth** | `POST` | `/api/v1/auth/login` | Authenticates credentials & issues JWT | Public |
| **Gold** | `GET` | `/api/v1/gold/platforms` | Search Gold platform trust analytics | Public |
| **Gold** | `GET` | `/api/v1/gold/platforms/{site}` | Get platform trust analytics for site | Public |
| **Gold** | `GET` | `/api/v1/gold/insights` | Pre-computed payment method insights | Public |
| **Search** | `GET` | `/api/v1/search` | Multi-criteria search with trust score filters | Reader |
| **AI** | `POST` | `/api/v1/trust-score` | Calculate Trust Score & rule evaluations | Analyst |
| **AI** | `POST` | `/api/v1/analyze` | Generate AI Risk & Recommendation Report | Analyst |
| **AI** | `POST` | `/api/v1/rag/query` | Provider-agnostic RAG natural language search | Analyst |
| **Telemetry**| `GET` | `/metrics` | Prometheus metrics scraping endpoint | Public |

*   **Interactive Swagger Documentation:** [https://localhost/docs](https://localhost/docs)
*   **ReDoc Specifications:** [https://localhost/redoc](https://localhost/redoc)

---

## 🧪 Running the Test Suite

Execute the full suite of unit tests, integration tests, E2E simulations, and benchmark runners:
```bash
python -m unittest backend/tests/test_ai_services.py backend/tests/test_api.py backend/tests/test_full_integration.py backend/tests/run_e2e_simulation.py backend/tests/benchmark_performance.py
```

---

## 👥 Engineering Team & Credits

*   👨‍💻 **Arjun Mehta** — Senior Backend & AI Engineer
*   👩‍💻 **Priya Iyer** — Senior Data Engineer
*   👨‍💻 **Rayri Sharma** — Data Acquisition Engineer
*   👩‍💻 **Radhika Patil** — Senior DevOps Engineer
