"""
File: search.py
Purpose:
    REST API endpoints for multi-criteria search and platform filtering.
Author: Arjun Mehta
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 5.0
"""

import math
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from database.connection import get_db_session
from repositories.payment_repository import PaymentRepository
from schemas.search import PaginatedSearchResponse
from schemas.payment import PaymentRecordResponse
from schemas.response import APIResponse

router = APIRouter(prefix="/search", tags=["Search"])


@router.get(
    "",
    response_model=APIResponse[PaginatedSearchResponse],
    status_code=status.HTTP_200_OK,
    summary="Search Payment Records & Platforms",
    description="Multi-criteria search endpoint supporting free text search, platform filtering, country/currency filters, trust score range, risk level, pagination, and sorting."
)
def search_records(
    q: Optional[str] = Query(None, description="Free text search query"),
    site: Optional[str] = Query(None, description="Platform site name filter"),
    payment_name: Optional[str] = Query(None, description="Payment gateway/method name"),
    payment_type: Optional[str] = Query(None, description="Payment category filter"),
    country: Optional[str] = Query(None, description="Country ISO code (e.g. IN)"),
    currency: Optional[str] = Query(None, description="Currency code (e.g. INR)"),
    status_filter: Optional[str] = Query(None, alias="status", description="Record status (active/inactive)"),
    min_trust_score: Optional[float] = Query(None, ge=0.0, le=100.0, description="Minimum trust score filter"),
    max_trust_score: Optional[float] = Query(None, ge=0.0, le=100.0, description="Maximum trust score filter"),
    risk_level: Optional[str] = Query(None, description="Risk level filter (LOW, MEDIUM, HIGH)"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("scraped_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort direction (asc/desc)"),
    db: Session = Depends(get_db_session)
):
    """
    Executes paginated search across payment records in the database.
    """
    repo = PaymentRepository(db)
    records, total = repo.search_records(
        q=q,
        site=site,
        payment_name=payment_name,
        payment_type=payment_type,
        country=country,
        currency=currency,
        status=status_filter,
        min_trust_score=min_trust_score,
        max_trust_score=max_trust_score,
        risk_level=risk_level,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_order=sort_order
    )

    pages = math.ceil(total / size) if size > 0 else 1
    items = [PaymentRecordResponse.model_validate(r) for r in records]

    payload = PaginatedSearchResponse(
        total=total,
        page=page,
        size=size,
        pages=pages,
        items=items
    )

    return APIResponse(
        success=True,
        message=f"Search retrieved {len(items)} record(s) out of {total} total match(es).",
        data=payload
    )
