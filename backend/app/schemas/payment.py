"""
File: payment.py
Purpose:
    Pydantic validation schemas for payment record representations.
Author: Niraj Kadam
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 1.0
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, Field


class PaymentRecordResponse(BaseModel):
    """
    Standard output schema for curated payment records.
    """
    id: UUID
    schema_version: str
    scraper_version: str
    source_platform: str
    extraction_status: str
    extraction_method: str
    site: str
    page_type: str
    payment_type: str
    payment_name: str
    currency: str
    country: str
    bonus_name: Optional[str] = None
    support_type: Optional[str] = None
    support_value: Optional[str] = None
    status: str
    source_url: str
    scraped_at: datetime
    extracted_data: Dict[str, Any] = Field(default_factory=dict)
    row_hash: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaymentRecordListResponse(BaseModel):
    """
    Paginated list of payment records.
    """
    records: List[PaymentRecordResponse]
    total: int
    page: int
    size: int
    pages: int
