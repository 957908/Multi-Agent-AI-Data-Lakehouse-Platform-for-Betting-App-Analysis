-- ============================================================
-- PostgreSQL Initialization Script – SentinelX Trust AI
-- Runs once on first container start (docker-entrypoint-initdb.d)
-- Author: Radhika Patil – DevOps (sourced from Priya Iyer's schema.sql)
-- ============================================================

-- Enable UUID generation extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- Table: etl_runs
-- Tracks execution history of the ETL ingestion pipeline
-- ============================================================
CREATE TABLE IF NOT EXISTS etl_runs (
    id               SERIAL PRIMARY KEY,
    run_path         VARCHAR(255) UNIQUE NOT NULL,
    records_scraped  INTEGER DEFAULT 0,
    records_processed INTEGER DEFAULT 0,
    records_failed   INTEGER DEFAULT 0,
    status           VARCHAR(50) NOT NULL,
    processed_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- Table: payment_records
-- Curated Silver/Gold layer payment data from scraper output
-- ============================================================
CREATE TABLE IF NOT EXISTS payment_records (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    schema_version   VARCHAR(10) NOT NULL DEFAULT '1.1',
    scraper_version  VARCHAR(10) NOT NULL DEFAULT '1.0.0',
    source_platform  VARCHAR(100) NOT NULL,
    extraction_status VARCHAR(50) NOT NULL,
    extraction_method VARCHAR(100) NOT NULL,
    site             VARCHAR(100) NOT NULL,
    page_type        VARCHAR(100) NOT NULL DEFAULT 'deposit_page',
    payment_type     VARCHAR(100) NOT NULL,
    payment_name     VARCHAR(100) NOT NULL,
    currency         VARCHAR(10) NOT NULL,
    country          VARCHAR(10) NOT NULL,
    bonus_name       VARCHAR(255),
    support_type     VARCHAR(100),
    support_value    VARCHAR(255),
    status           VARCHAR(50) NOT NULL DEFAULT 'active',
    source_url       TEXT NOT NULL,
    scraped_at       TIMESTAMP NOT NULL,
    extracted_data   JSONB NOT NULL DEFAULT '{}',
    row_hash         VARCHAR(64) UNIQUE NOT NULL,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast hash-based deduplication lookups
CREATE INDEX IF NOT EXISTS idx_payment_records_row_hash ON payment_records(row_hash);
CREATE INDEX IF NOT EXISTS idx_payment_records_site ON payment_records(site);
CREATE INDEX IF NOT EXISTS idx_payment_records_status ON payment_records(status);
CREATE INDEX IF NOT EXISTS idx_payment_records_scraped_at ON payment_records(scraped_at);
