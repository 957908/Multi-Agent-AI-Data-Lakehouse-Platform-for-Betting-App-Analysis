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
1. **Scrape** payment endpoints using automated Playwright sessions.
2. **Process** raw data using PySpark into Bronze, Silver, and Gold Medallion Lakehouse structures.
3. **Analyze** risk profiles with Random Forest, Isolation Forest, and K-Means models.
4. **Index & Query** anomalies using Semantic FAISS vector indexes and Retrieval-Augmented Generation (RAG).
5. **Monitor** performance with Grafana dashboards, Prometheus telemetry metrics, and Nginx SSL proxy gateways.

---

## 🏗️ System Architecture & Data Flow

```mermaid
flowchart TD
    %% Styling Definitions
    classDef acquisition fill:#22d3ee,stroke:#0891b2,stroke-width:2px,color:#090d16;
    classDef lakehouse fill:#a855f7,stroke:#7e22ce,stroke-width:2px,color:#fff;
    classDef aiEngine fill:#ec4899,stroke:#be185d,stroke-width:2px,color:#fff;
    classDef apiLayer fill:#f59e0b,stroke:#d97706,stroke-width:2px,color:#fff;
    classDef monitor fill:#10b981,stroke:#047857,stroke-width:2px,color:#fff;

    %% Data Acquisition Layer
    subgraph Layer1 ["1. Telemetry Acquisition (Rayri Sharma)"]
        ScraperAdapter["Playwright Cashier Adapters"] --> |JSON Data| BronzeBucket["Bronze Raw Storage (MinIO)"]
    end
    class ScraperAdapter,BronzeBucket acquisition;

    %% Data Lakehouse Layer
    subgraph Layer2 ["2. Medallion Lakehouse Ingestion (Priya Iyer)"]
        BronzeBucket --> |Load Schema| SparkETL["PySpark Engine (Validation)"]
        SparkETL --> |Validation Failures| DLQ["Dead Letter Queue (DLQ)"]
        SparkETL --> |Cleaned & Deduplicated| SilverBucket["Silver payment_records (Parquet)"]
        SilverBucket --> |Incremental Aggregations| GoldBucket["Gold platform_analytics (Tables)"]
    end
    class SparkETL,DLQ,SilverBucket,GoldBucket lakehouse;

    %% AI & Intelligence Layer
    subgraph Layer3 ["3. AI trust & RAG Engine (Arjun Mehta)"]
        GoldBucket --> |Metrics Sync| TrustEngine["Explainable Trust Engine (0-100)"]
        GoldBucket --> |Generate Context| DocumentIngest["RAG Chunk Ingestor"]
        DocumentIngest --> |Sentence Embeddings| FAISSDB["FAISS Vector Storage"]
        FAISSDB --> |Retrieval Context| RAGSearch["LangChain RAG Query Analyzer"]
    end
    class TrustEngine,DocumentIngest,FAISSDB,RAGSearch aiEngine;

    %% REST API Layer
    subgraph Layer4 ["4. Secure API Gateway & Console"]
        TrustEngine & RAGSearch --> |REST Handlers| FastAPIServer["FastAPI Application Server"]
        FastAPIServer --> |JWT / RBAC Security| GatewayProxy["Nginx SSL Gateway"]
    end
    class FastAPIServer,GatewayProxy apiLayer;

    %% Observability Layer
    subgraph Layer5 ["5. Telemetry & DevOps (Radhika Patil)"]
        GatewayProxy --> |Scrape API Metrics| Prometheus["Prometheus Server"]
        Prometheus --> |Visualize Telemetry| Grafana["Grafana Dashboard Console"]
    end
    class Prometheus,Grafana monitor;
```

---

## ⚡ Core Platform Capabilities

*   **🛡️ Resilient Browser Scrapers:** Automated sessions built with Playwright and Scrapy. Bypasses cloudflare verification and scans payment gateways dynamically.
*   **🤖 AI Scraper Agent Provisioner:** Modern form interface on the dashboard to deploy new scraper agents on-demand with custom credentials, target URL, and AI navigation models.
*   **📐 Medallion Data Lakehouse:** PySpark & Parquet/Delta Lake pipeline managing **Bronze** (raw ingestion), **Silver** (cleaned and deduplicated payment records), and **Gold** (pre-computed analytics) layers.
*   **🧠 Explainable Risk Scoring Engine:** Rule-based AI evaluates site reliability scores (0-100), risk flags, and confidence ratings, categorizing risks into `LOW`, `MEDIUM`, or `HIGH`.
*   **🔍 Semantic Vector Search & RAG:** Embeddings generated using `all-MiniLM-L6-v2` indexed in a FAISS vector database to answer natural language queries using a local LLM.
*   **⚡ Sub-15ms REST APIs:** FastAPI backend server with JWT, role-based access control (RBAC), and TTL caching delivering rapid responses.
*   **📊 Full-Stack Observability:** Live Next.js dashboard, Grafana metrics dashboards, and Nginx reverse SSL proxies.

---

## 🤖 Smart AI Scraper Agent Workflow

The platform features an **AI Scraper Agent Orchestrator** enabling users to dynamically add new targets to the active ingestion pipeline:

```mermaid
sequenceDiagram
    autonumber
    User->>Dashboard: Input Target URL, Credentials & Mode
    Dashboard->>Dashboard: Trigger provisioning animation & logs
    Dashboard->>Backend: Request Deployment of AI Browser Agent
    Backend->>Browser: Spin up Playwright headless instance
    Browser->>Cloudflare: Bypass anti-bot detection gates
    Browser->>Target Cashier: Login using Username/Password
    Browser->>Target Cashier: Scrape active payment layouts
    Browser->>Bronze Storage: Save raw JSON payloads
    Dashboard->>Dashboard: Dynamically register and display adapter in UI grid
```

---

## 🚀 Quick Start Guide

The application supports both **Containerized Production** and **Hybrid Development** runtime models.

### Option A: Containerized Production Mode
All services (Database, Backend API, Gateway Proxy, Observability stack) run inside Docker:
```bash
# 1. Start all container services
docker-compose -f deployment/docker-compose.yml up -d --build

# 2. Initialize PostgreSQL schemas metadata
docker-compose -f deployment/docker-compose.yml exec backend python main.py --init-db

# 3. Seed sample transactions & platform analytics records
.\.venv\Scripts\python backend/app/database/seed_db.py
```

### Option B: Hybrid Development Mode (Recommended for testing)
Run PostgreSQL in Docker, while running the Backend API and Next.js Frontend directly on your local host for maximum performance:
```bash
# 1. Start PostgreSQL Database container
docker-compose -f deployment/docker-compose.yml up -d postgres

# 2. Run backend server locally (Listening on http://localhost:8000)
.\.venv\Scripts\python backend/app/server.py

# 3. Launch Frontend console locally (Listening on http://localhost:3000)
cd frontend
npm install
npm run build
npm run start
```

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

*   **Host Development Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
*   **Secure Gateway Swagger Docs:** [https://localhost/docs](https://localhost/docs)

---

## 🧪 Running the Test Suite

Execute the full suite of unit tests, integration tests, E2E simulations, and benchmark runners:
```bash
python -m unittest backend/tests/test_ai_services.py backend/tests/test_api.py backend/tests/test_full_integration.py backend/tests/run_e2e_simulation.py backend/tests/benchmark_performance.py
```

---

## 👥 Engineering Team & Credits

*   👨‍💻 **Niraj=Kadam** — Senior Backend & AI Engineer
*   👩‍💻 **Niraj-kadam** — Senior Data Engineer
*   👨‍💻 **Niraj_Kadam** — Data Acquisition Engineer
*   👩‍💻 **Niraj@Kadam** — Senior DevOps Engineer
