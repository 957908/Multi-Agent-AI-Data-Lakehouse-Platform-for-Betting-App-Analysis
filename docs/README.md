<p align="center">
  <img src="https://img.shields.io/badge/SentinelX%20Trust%20AI-Documentation%20Portal-violet?style=for-the-badge&logo=googledocs&logoColor=white" alt="SentinelX Documentation Banner" />
</p>

<h1 align="center">Documentation Portal — SentinelX Trust AI</h1>
<p align="center">
  <b>Comprehensive engineering index, architecture specifications, and operational manuals for the platform.</b>
</p>

---

## 🗺️ Modern Platform Architecture Map
The following interactive data flow illustrates the real-time interaction between automated web scrapers, the PySpark Medallion Lakehouse, vector storage, and the FastAPI gateway layer:

```mermaid
graph TD
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

## 📂 Documentation Directory Index

Select a file link below to read the comprehensive specs, diagrams, and setups for each platform module:

### 📁 Project Governance & Vision
Overview of product definitions, requirements, and compliance metrics:

| Document | Type | Purpose / Description |
| :--- | :---: | :--- |
| **[Product Requirements (PRD)](file:///d:/kadam/Multi-Agent-AI-Data-Lakehouse-Platform-for-Betting-App-Analysis/docs/PRD/PRD.md)** | 📄 Spec | Core product features, user stories, and platform requirements. |
| **[Technical Specifications (TRD)](file:///d:/kadam/Multi-Agent-AI-Data-Lakehouse-Platform-for-Betting-App-Analysis/docs/Architecture/TRD.md)** | 📄 Spec | Technical prerequisites, data structures, and operational boundaries. |
| **[Active Risk Register](file:///d:/kadam/Multi-Agent-AI-Data-Lakehouse-Platform-for-Betting-App-Analysis/docs/Risk%20Register/Risk-Register.md)** | 🛠️ Log | Ongoing assessment of system security, scale, and database risks. |

<br />

### 📁 System Architecture & Guidelines
Detailed layout directories of database configurations, networks, and coding guidelines:

| Document | Type | Purpose / Description |
| :--- | :---: | :--- |
| **[System Architecture Guide](file:///d:/kadam/Multi-Agent-AI-Data-Lakehouse-Platform-for-Betting-App-Analysis/docs/architecture.md)** | 🆕 Active | Core modular structure, component sequence diagrams, and execution SLAs. |
| **[Database & Lakehouse Schema](file:///d:/kadam/Multi-Agent-AI-Data-Lakehouse-Platform-for-Betting-App-Analysis/docs/database_schema.md)** | 🆕 Active | PostgreSQL ORM schemas, ER diagrams, and Medallion layouts. |
| **[AI & Trust Engine Specs](file:///d:/kadam/Multi-Agent-AI-Data-Lakehouse-Platform-for-Betting-App-Analysis/docs/ai_trust_engine.md)** | 🆕 Active | Math logic formulas, RAG embeddings specs, and TTL caching mechanism. |
| **[Design System Brief](file:///d:/kadam/Multi-Agent-AI-Data-Lakehouse-Platform-for-Betting-App-Analysis/docs/Architecture/Design-System.md)** | 🛠️ Guide | Frontend layout guidelines, theme colors, and style tokens. |
| **[Developer Onboarding Guide](file:///d:/kadam/Multi-Agent-AI-Data-Lakehouse-Platform-for-Betting-App-Analysis/docs/developer_guide.md)** | 🆕 Active | Developer local setup rules, env config, and branching strategies. |

<br />

### 📁 API & Specifications
Technical specifications for endpoints, caching, and automated cashiers:

| Document | Type | Purpose / Description |
| :--- | :---: | :--- |
| **[REST API Reference Guide](file:///d:/kadam/Multi-Agent-AI-Data-Lakehouse-Platform-for-Betting-App-Analysis/docs/api_reference.md)** | 🆕 Active | OpenAPI routes specs, requests/responses, and authentication levels. |
| **[Medallion ETL Pipeline](file:///d:/kadam/Multi-Agent-AI-Data-Lakehouse-Platform-for-Betting-App-Analysis/docs/etl_pipeline.md)** | 🆕 Active | PySpark data ingestion, schemas, transformations, and output targets. |
| **[Scrapers & Telemetry Guide](file:///d:/kadam/Multi-Agent-AI-Data-Lakehouse-Platform-for-Betting-App-Analysis/docs/scrapers_guide.md)** | 🆕 Active | Playwright headless browser setups, cookies, proxies, and error retries. |

<br />

### 📁 Sprint Operations & Planning
Operational tracking logs, changes, and audit reports:

| Document | Type | Purpose / Description |
| :--- | :---: | :--- |
| **[Phase 5 Audit Report](file:///d:/kadam/Multi-Agent-AI-Data-Lakehouse-Platform-for-Betting-App-Analysis/docs/audit_report.md)** | 🆕 Active | File audit trace report, inventory maps, and architecture diagrams. |
| **[Implementation Roadmap](file:///d:/kadam/Multi-Agent-AI-Data-Lakehouse-Platform-for-Betting-App-Analysis/docs/Sprint%20Reports/Phases.md)** | 🛠️ Road | Comprehensive sprint breakdown phases from Phase 1 through Phase 10. |
| **[Project Memory log](file:///d:/kadam/Multi-Agent-AI-Data-Lakehouse-Platform-for-Betting-App-Analysis/docs/Sprint%20Reports/Memory.md)** | 🛠️ Log | Living journal tracking key architectural approvals and updates. |
| **[System Changelog](file:///d:/kadam/Multi-Agent-AI-Data-Lakehouse-Platform-for-Betting-App-Analysis/docs/CHANGELOG/CHANGELOG.md)** | 🛠️ Log | Version release tracking history. |

---

## 🛠️ Run Guide Reference
For a complete guide to running the project containers, seeding PostgreSQL, and launching the Next.js frontend, see the master runner handbook:
👉 **[Master Operational RUN_GUIDE.md](file:///d:/kadam/Multi-Agent-AI-Data-Lakehouse-Platform-for-Betting-App-Analysis/RUN_GUIDE.md)**