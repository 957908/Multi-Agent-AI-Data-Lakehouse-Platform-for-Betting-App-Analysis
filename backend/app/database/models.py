"""
File: models.py
Purpose:
    SQLAlchemy ORM models for database schema representation.
Author: Priya Iyer
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 1.0
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from database.connection import Base


class ETLRun(Base):
    """
    Tracks execution runs of the ETL pipeline for incremental processing.
    """
    __tablename__ = "etl_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_path = Column(String(255), unique=True, nullable=False)
    records_scraped = Column(Integer, default=0)
    records_processed = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    status = Column(String(50), nullable=False)
    processed_at = Column(DateTime, default=datetime.utcnow, server_default=text("CURRENT_TIMESTAMP"))


class PaymentRecordModel(Base):
    """
    Curated storage schema for betting platform payment structures (Silver/Gold layer).
    """
    __tablename__ = "payment_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()"))
    schema_version = Column(String(10), default="1.1", nullable=False)
    scraper_version = Column(String(10), default="1.0.0", nullable=False)
    source_platform = Column(String(100), nullable=False)
    extraction_status = Column(String(50), nullable=False)
    extraction_method = Column(String(100), nullable=False)
    site = Column(String(100), nullable=False)
    page_type = Column(String(100), default="deposit_page", nullable=False)
    payment_type = Column(String(100), nullable=False)
    payment_name = Column(String(100), nullable=False)
    currency = Column(String(10), nullable=False)
    country = Column(String(10), nullable=False)
    bonus_name = Column(String(255), nullable=True)
    support_type = Column(String(100), nullable=True)
    support_value = Column(String(255), nullable=True)
    status = Column(String(50), default="active", nullable=False)
    source_url = Column(Text, nullable=False)
    scraped_at = Column(DateTime, nullable=False)
    extracted_data = Column(JSONB, default=dict, nullable=False)
    row_hash = Column(String(64), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime, default=datetime.utcnow, server_default=text("CURRENT_TIMESTAMP"), onupdate=datetime.utcnow)
