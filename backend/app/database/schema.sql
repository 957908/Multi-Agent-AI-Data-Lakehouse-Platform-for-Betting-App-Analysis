-- Schema initialization for SentinelX Trust AI
-- Author: Priya Iyer
-- Company: SentinelX Labs
-- Version: 1.0

-- Enable UUID generation support
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Ingestion Run Catalog
CREATE TABLE IF NOT EXISTS etl_runs (
    id SERIAL PRIMARY KEY,
    run_path VARCHAR(255) UNIQUE NOT NULL,
    records_scraped INT DEFAULT 0,
    records_processed INT DEFAULT 0,
    records_failed INT DEFAULT 0,
    status VARCHAR(50) NOT NULL,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Curated Payment Records (Silver/Gold analytical table)
CREATE TABLE IF NOT EXISTS payment_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    schema_version VARCHAR(10) DEFAULT '1.1' NOT NULL,
    scraper_version VARCHAR(10) DEFAULT '1.0.0' NOT NULL,
    source_platform VARCHAR(100) NOT NULL,
    extraction_status VARCHAR(50) NOT NULL,
    extraction_method VARCHAR(100) NOT NULL,
    site VARCHAR(100) NOT NULL,
    page_type VARCHAR(100) DEFAULT 'deposit_page' NOT NULL,
    payment_type VARCHAR(100) NOT NULL,
    payment_name VARCHAR(100) NOT NULL,
    currency VARCHAR(10) NOT NULL,
    country VARCHAR(10) NOT NULL,
    bonus_name VARCHAR(255),
    support_type VARCHAR(100),
    support_value VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active' NOT NULL,
    source_url TEXT NOT NULL,
    scraped_at TIMESTAMP NOT NULL,
    extracted_data JSONB DEFAULT '{}'::jsonb NOT NULL,
    row_hash VARCHAR(64) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Optimization Indexes
CREATE INDEX IF NOT EXISTS idx_payment_records_site ON payment_records(site);
CREATE INDEX IF NOT EXISTS idx_payment_records_payment_type ON payment_records(payment_type);
CREATE INDEX IF NOT EXISTS idx_payment_records_row_hash ON payment_records(row_hash);

-- Gold Layer: Pre-computed platform analytics & trust summaries
CREATE TABLE IF NOT EXISTS gold_platform_analytics (
    site VARCHAR(100) PRIMARY KEY,
    trust_score NUMERIC(5, 2) NOT NULL,
    trust_level VARCHAR(50) NOT NULL,
    confidence_score NUMERIC(4, 2) NOT NULL,
    total_payment_methods INT NOT NULL,
    active_payment_methods INT NOT NULL,
    supported_countries JSONB NOT NULL,
    top_payment_methods JSONB NOT NULL,
    risk_summary TEXT NOT NULL,
    risk_flags JSONB NOT NULL,
    last_scraped_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Gold Layer: Pre-computed payment method insights
CREATE TABLE IF NOT EXISTS gold_payment_method_insights (
    id SERIAL PRIMARY KEY,
    site VARCHAR(100) NOT NULL,
    payment_type VARCHAR(100) NOT NULL,
    payment_name VARCHAR(100) NOT NULL,
    total_records INT NOT NULL,
    active_count INT NOT NULL,
    reliability_score NUMERIC(5, 2) NOT NULL,
    supported_countries JSONB NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_site_method UNIQUE (site, payment_type, payment_name)
);

-- Gold Layer Indexes
CREATE INDEX IF NOT EXISTS idx_gold_platform_site ON gold_platform_analytics(site);
CREATE INDEX IF NOT EXISTS idx_gold_insights_site ON gold_payment_method_insights(site);
