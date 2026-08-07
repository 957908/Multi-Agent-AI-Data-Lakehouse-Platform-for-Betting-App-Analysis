"""
File: gold.py
Purpose:
    REST API endpoints for querying Gold Layer platform analytics and payment method insights.
Author: Niraj Kadam
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 5.0
"""

import math
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Path, status
from sqlalchemy.orm import Session

from database.connection import get_db_session
from repositories.gold_repository import GoldRepository
from schemas.gold import (
    GoldPlatformAnalyticsResponse,
    GoldPaymentInsightResponse,
    PaginatedGoldPlatformResponse
)
from schemas.response import APIResponse
from core.exceptions import NotFoundException
from core.cache import cache_response

router = APIRouter(prefix="/gold", tags=["Gold Layer Analytics"])


@router.get(
    "/platforms",
    response_model=APIResponse[PaginatedGoldPlatformResponse],
    status_code=status.HTTP_200_OK,
    summary="Search Gold Platform Analytics",
    description="Retrieves pre-computed Gold Layer platform analytics with trust score filtering, risk level criteria, and pagination."
)
def list_gold_platforms(
    q: Optional[str] = Query(None, description="Free text search query"),
    site: Optional[str] = Query(None, description="Platform site domain filter"),
    risk_level: Optional[str] = Query(None, description="Risk level filter (LOW, MEDIUM, HIGH)"),
    min_trust_score: Optional[float] = Query(None, ge=0.0, le=100.0, description="Minimum trust score filter"),
    max_trust_score: Optional[float] = Query(None, ge=0.0, le=100.0, description="Maximum trust score filter"),
    country: Optional[str] = Query(None, description="Country ISO code filter"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("trust_score", description="Field to sort by"),
    sort_order: str = Query("desc", description="Sort order: asc/desc"),
    db: Session = Depends(get_db_session)
):
    """
    Returns paginated Gold platform analytics records.
    """
    repo = GoldRepository(db)
    results, total = repo.list_platform_analytics(
        q=q,
        site=site,
        risk_level=risk_level,
        min_trust_score=min_trust_score,
        max_trust_score=max_trust_score,
        country=country,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_order=sort_order
    )

    pages = math.ceil(total / size) if size > 0 else 1
    items = [GoldPlatformAnalyticsResponse.model_validate(r) for r in results]

    payload = PaginatedGoldPlatformResponse(
        total=total,
        page=page,
        size=size,
        pages=pages,
        items=items
    )

    return APIResponse(
        success=True,
        message=f"Retrieved {len(items)} Gold platform analytics record(s) out of {total} total match(es).",
        data=payload
    )


@router.get(
    "/platforms/{site}",
    response_model=APIResponse[GoldPlatformAnalyticsResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Gold Analytics for Platform",
    description="Returns pre-computed Gold Layer analytics and Trust Score breakdown for a specific platform site."
)
def get_gold_platform_by_site(
    site: str = Path(..., examples=["melbet"], description="Platform site name"),
    db: Session = Depends(get_db_session)
):
    """
    Retrieves Gold platform analytics for a specific site.
    """
    repo = GoldRepository(db)
    result = repo.get_platform_analytics(site)
    if not result:
        raise NotFoundException(message=f"Gold analytics not found for platform '{site}'.")

    return APIResponse(
        success=True,
        message=f"Retrieved Gold analytics for platform '{site}'.",
        data=GoldPlatformAnalyticsResponse.model_validate(result)
    )


@router.get(
    "/insights",
    response_model=APIResponse[List[GoldPaymentInsightResponse]],
    status_code=status.HTTP_200_OK,
    summary="Search Gold Payment Method Insights",
    description="Retrieves pre-computed payment method reliability insights across platforms."
)
def search_gold_insights(
    site: Optional[str] = Query(None, description="Platform site domain filter"),
    payment_type: Optional[str] = Query(None, description="Payment category filter"),
    payment_name: Optional[str] = Query(None, description="Payment method name"),
    country: Optional[str] = Query(None, description="Country ISO code filter"),
    db: Session = Depends(get_db_session)
):
    """
    Returns list of Gold payment method insights.
    """
    repo = GoldRepository(db)
    results = repo.search_payment_insights(
        site=site,
        payment_type=payment_type,
        payment_name=payment_name,
        country=country
    )

    items = [GoldPaymentInsightResponse.model_validate(r) for r in results]
    return APIResponse(
        success=True,
        message=f"Retrieved {len(items)} Gold payment method insight(s).",
        data=items
    )
