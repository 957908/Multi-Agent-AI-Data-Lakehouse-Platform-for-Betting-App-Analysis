"""
File: payment_records.py
Purpose:
    Exposes read-only API endpoints to query curated betting platform payment records.
Author: Arjun Mehta
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 1.0
"""

import logging
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from database.connection import get_db_session
from core.security import RoleChecker
from core.exceptions import NotFoundException, ValidationException
from repositories.payment_repository import PaymentRepository
from schemas.payment import PaymentRecordResponse, PaymentRecordListResponse
from schemas.response import APIResponse

logger = logging.getLogger("backend.api.payment_records")
router = APIRouter(prefix="/payment-records", tags=["payment-records"])

# Require any valid role for viewing records
reader_auth = Depends(RoleChecker(allowed_roles=["reader", "analyst", "admin"]))


@router.get("", response_model=APIResponse[PaymentRecordListResponse])
def get_payment_records(
    site: Optional[str] = Query(None, description="Filter by betting site platform"),
    payment_type: Optional[str] = Query(None, description="Filter by payment method type (e.g. UPI, Crypto)"),
    status: Optional[str] = Query(None, description="Filter by record extraction status"),
    country: Optional[str] = Query(None, description="Filter by platform operation country"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    size: int = Query(20, ge=1, le=100, description="Page size limit"),
    sort_by: str = Query("created_at", description="Field name to sort by"),
    sort_order: str = Query("desc", description="Sort order direction ('asc' or 'desc')"),
    db: Session = Depends(get_db_session),
    current_user: dict = reader_auth
) -> APIResponse[PaymentRecordListResponse]:
    """
    Retrieves a paginated, filtered list of payment records from the curated database.
    """
    if sort_order.lower() not in ("asc", "desc"):
        raise ValidationException("sort_order must be either 'asc' or 'desc'")

    records, total = PaymentRepository.list_records(
        db=db,
        site=site,
        payment_type=payment_type,
        status=status,
        country=country,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_order=sort_order
    )

    # Compute total pages
    pages = (total + size - 1) // size if total > 0 else 0

    response_data = PaymentRecordListResponse(
        records=[PaymentRecordResponse.model_validate(r) for r in records],
        total=total,
        page=page,
        size=size,
        pages=pages
    )

    return APIResponse(
        success=True,
        message="Payment records retrieved successfully",
        data=response_data
    )


@router.get("/{record_id}", response_model=APIResponse[PaymentRecordResponse])
def get_payment_record_by_id(
    record_id: UUID,
    db: Session = Depends(get_db_session),
    current_user: dict = reader_auth
) -> APIResponse[PaymentRecordResponse]:
    """
    Retrieves the complete attributes of a specific payment record by ID.
    """
    record = PaymentRepository.get_by_id(db, record_id)
    if not record:
        raise NotFoundException(f"Payment record not found with ID: {record_id}")

    return APIResponse(
        success=True,
        message="Payment record retrieved successfully",
        data=PaymentRecordResponse.model_validate(record)
    )
