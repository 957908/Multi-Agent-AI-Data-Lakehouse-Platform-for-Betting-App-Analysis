"""
File: payment.py
Purpose:
    Defines the PaymentRecord model schema using Pydantic for data integrity.
Author: R. Rayri Sharma
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform for Betting Site Intelligence
Created By: R. Rayri Sharma
Reviewed By: Tech Lead & Solution Architect (HQ Chat)
Version: 1.0
"""

# Standard Library
from typing import Optional, Dict, Any

# Third Party
from pydantic import BaseModel, Field


class PaymentRecord(BaseModel):
    """
    Structured model for a single payment method extraction.
    Enforces types and default values complying with JSON schema contract version 1.1.
    """
    schema_version: str = Field(default="1.1")
    scraper_version: str = Field(default="1.0.0")
    source_platform: str
    extraction_status: str
    extraction_method: str
    site: str
    page_type: str = Field(default="deposit_page")
    payment_type: str
    payment_name: str
    currency: str = Field(default="INR")
    country: str = Field(default="IN")
    bonus_name: Optional[str] = None
    support_type: Optional[str] = "live_chat"
    support_value: Optional[str] = None
    status: str = Field(default="active")
    source_url: str
    scraped_at: str
    extracted_data: Dict[str, Any] = Field(default_factory=dict)
