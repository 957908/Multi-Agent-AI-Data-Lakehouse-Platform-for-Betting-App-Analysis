"""
File: gold.py
Purpose:
    Pydantic schemas for Gold Layer curated platform analytics and payment insights.
Author: Niraj Kadam
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 5.0
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class GoldPlatformAnalyticsResponse(BaseModel):
    """
    Schema for Gold Layer platform analytics summary.
    """
    site: str = Field(..., example="melbet", description="Platform domain or site identifier")
    trust_score: float = Field(..., example=85.5, description="Pre-computed Trust Score (0-100)")
    trust_level: str = Field(..., example="HIGH", description="Risk level (LOW, MEDIUM, HIGH)")
    confidence_score: float = Field(..., example=0.95, description="Confidence metric (0.0 to 1.0)")
    total_payment_methods: int = Field(..., example=14, description="Total distinct payment methods")
    active_payment_methods: int = Field(..., example=12, description="Active payment methods count")
    supported_countries: List[str] = Field(default_factory=list, description="List of supported country ISO codes")
    top_payment_methods: List[str] = Field(default_factory=list, description="Top active payment methods")
    risk_summary: str = Field(..., description="High-level risk summary")
    risk_flags: List[str] = Field(default_factory=list, description="Extracted risk indicators")
    last_scraped_at: datetime = Field(..., description="Timestamp of latest scraped data")
    updated_at: datetime = Field(..., description="Timestamp of last Gold aggregation")

    model_config = ConfigDict(from_attributes=True)


class GoldPaymentInsightResponse(BaseModel):
    """
    Schema for Gold Layer payment method insight.
    """
    id: Optional[int] = Field(None, description="Primary key ID")
    site: str = Field(..., example="melbet", description="Platform site domain")
    payment_type: str = Field(..., example="e-wallet", description="Payment category")
    payment_name: str = Field(..., example="Paytm", description="Payment gateway/method name")
    total_records: int = Field(..., example=15, description="Total extracted records")
    active_count: int = Field(..., example=14, description="Active status count")
    reliability_score: float = Field(..., example=93.3, description="Reliability score percentage")
    supported_countries: List[str] = Field(default_factory=list, description="Supported country codes")
    updated_at: datetime = Field(..., description="Timestamp of last update")

    model_config = ConfigDict(from_attributes=True)


class GoldSearchQueryParams(BaseModel):
    """
    Query parameters for filtering Gold platform analytics.
    """
    q: Optional[str] = Field(None, description="Free text search query")
    site: Optional[str] = Field(None, description="Platform site domain filter")
    risk_level: Optional[str] = Field(None, description="Filter by risk level (LOW, MEDIUM, HIGH)")
    min_trust_score: Optional[float] = Field(None, ge=0.0, le=100.0, description="Minimum trust score")
    max_trust_score: Optional[float] = Field(None, ge=0.0, le=100.0, description="Maximum trust score")
    country: Optional[str] = Field(None, description="Supported country ISO code filter")
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(20, ge=1, le=100, description="Items per page")
    sort_by: str = Field("trust_score", description="Field name to sort by")
    sort_order: str = Field("desc", description="Sort order: asc or desc")


class PaginatedGoldPlatformResponse(BaseModel):
    """
    Paginated search result payload for Gold platform analytics.
    """
    total: int = Field(..., example=10, description="Total matching platforms")
    page: int = Field(..., example=1, description="Current page number")
    size: int = Field(..., example=20, description="Page size")
    pages: int = Field(..., example=1, description="Total pages")
    items: List[GoldPlatformAnalyticsResponse] = Field(default_factory=list, description="Matching Gold platform analytics")
