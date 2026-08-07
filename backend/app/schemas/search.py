"""
File: search.py
Purpose:
    Pydantic schemas for multi-criteria search and filtered platform search results.
Author: Niraj Kadam
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 5.0
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from schemas.payment import PaymentRecordResponse


class SearchQueryParams(BaseModel):
    """
    Query parameters model for search APIs.
    """
    q: Optional[str] = Field(None, description="Free text query matching platform, payment name, or bonus")
    site: Optional[str] = Field(None, description="Filter by platform site domain")
    payment_name: Optional[str] = Field(None, description="Filter by payment gateway/method name")
    payment_type: Optional[str] = Field(None, description="Filter by payment category")
    country: Optional[str] = Field(None, description="Filter by country code (e.g., IN, BR)")
    currency: Optional[str] = Field(None, description="Filter by currency code (e.g., INR, BRL)")
    status: Optional[str] = Field(None, description="Filter by record status (active, inactive)")
    min_trust_score: Optional[float] = Field(None, ge=0.0, le=100.0, description="Minimum trust score filter")
    max_trust_score: Optional[float] = Field(None, ge=0.0, le=100.0, description="Maximum trust score filter")
    risk_level: Optional[str] = Field(None, description="Risk level filter (LOW, MEDIUM, HIGH)")
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(20, ge=1, le=100, description="Items per page")
    sort_by: str = Field("scraped_at", description="Field name to sort by")
    sort_order: str = Field("desc", description="Sort order: asc or desc")


class PaginatedSearchResponse(BaseModel):
    """
    Paginated search result payload.
    """
    total: int = Field(..., example=42, description="Total matching records count")
    page: int = Field(..., example=1, description="Current page number")
    size: int = Field(..., example=20, description="Page size")
    pages: int = Field(..., example=3, description="Total number of pages")
    items: List[PaymentRecordResponse] = Field(default_factory=list, description="Matching payment records")
