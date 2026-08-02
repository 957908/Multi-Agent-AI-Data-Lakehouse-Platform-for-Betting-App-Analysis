# 🗄️ SentinelX Trust AI — Database & Lakehouse Schema Guide

**Version:** 1.0.0  
**Storage Stack:** PostgreSQL 15+ & PySpark Parquet Lakehouse  

---

## 📊 PostgreSQL Relational Schema & ER Diagram

```mermaid
erDiagram
    PAYMENT_RECORDS {
        uuid id PK
        string schema_version
        string scraper_version
        string source_platform
        string extraction_status
        string extraction_method
        string site
        string page_type
        string payment_type
        string payment_name
        string currency
        string country
        string bonus_name
        string support_type
        string support_value
        string status
        text source_url
        datetime scraped_at
        jsonb extracted_data
        string row_hash UK
        datetime created_at
        datetime updated_at
    }

    GOLD_PLATFORM_ANALYTICS {
        string site PK
        float trust_score
        string trust_level
        float confidence_score
        int total_payment_methods
        int active_payment_methods
        jsonb supported_countries
        jsonb top_payment_methods
        text risk_summary
        jsonb risk_flags
        datetime last_scraped_at
        datetime updated_at
    }

    GOLD_PAYMENT_METHOD_INSIGHTS {
        int id PK
        string site
        string payment_type
        string payment_name
        int total_records
        int active_count
        float reliability_score
        jsonb supported_countries
        datetime updated_at
    }

    ETL_RUNS {
        int id PK
        string run_path UK
        int records_scraped
        int records_processed
        int records_failed
        string status
        datetime processed_at
    }

    GOLD_PLATFORM_ANALYTICS ||--o{ PAYMENT_RECORDS : aggregates
    GOLD_PLATFORM_ANALYTICS ||--o{ GOLD_PAYMENT_METHOD_INSIGHTS : contains
```

---

## 🏛️ Medallion Data Lakehouse Layers

```text
/data
├── raw/       # Unprocessed Scraper JSON Outputs (Source Ingestion)
├── bronze/    # Raw Parquet Archives (Backups with Ingestion Metadata)
├── silver/    # Cleaned, Normalized & Deduplicated Records (payment_records)
└── gold/      # Pre-aggregated Platform Analytics & Trust Metrics
```

### 🥉 Bronze Layer (`data/bronze/`)
- **Format:** Parquet / Raw JSON Archive.
- **Description:** Preserves immutable raw extraction snapshots from Playwright scrapers with added `ingested_at` timestamps.

### 🥈 Silver Layer (`payment_records`)
- **Table Name:** `payment_records`
- **Description:** Schema-validated, standardized, and deduplicated payment records. Unique constraint enforced via `row_hash` SHA-256 hash.

### 🥇 Gold Layer (`gold_platform_analytics` & `gold_payment_method_insights`)
- **Table Names:** `gold_platform_analytics` and `gold_payment_method_insights`.
- **Description:** Pre-computed analytics summaries enabling sub-15ms API response latencies for trust scores, regional coverage, and channel reliability metrics.

---

## 🚫 Dead Letter Queue (`output/dlq/`)

Records failing validation during PySpark ETL processing (missing mandatory fields, invalid currency format, or unparseable JSON) are isolated into `output/dlq/invalid_records.json` alongside error reason metadata for auditing.
