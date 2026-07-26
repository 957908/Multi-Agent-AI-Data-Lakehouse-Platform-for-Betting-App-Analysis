"""
File: etl.py
Purpose:
    Exposes endpoints to retrieve history and metrics of the ETL ingestion pipeline.
Author: Arjun Mehta
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 1.0
"""

import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.connection import get_db_session
from core.security import RoleChecker
from repositories.etl_repository import ETLRepository
from schemas.etl import ETLRunResponse, ETLRunListResponse
from schemas.response import APIResponse

logger = logging.getLogger("backend.api.etl")
router = APIRouter(prefix="/etl", tags=["etl"])

# Restrict to Analyst and Admin roles only
analyst_auth = Depends(RoleChecker(allowed_roles=["analyst", "admin"]))


@router.get("/runs", response_model=APIResponse[ETLRunListResponse])
def get_etl_runs(
    limit: int = 100,
    db: Session = Depends(get_db_session),
    current_user: dict = analyst_auth
) -> APIResponse[ETLRunListResponse]:
    """
    Retrieves execution history log records of the ETL pipeline.
    """
    logger.info(f"Retrieving ETL runs (limit={limit}) requested by {current_user.get('email')}")
    
    runs, total = ETLRepository.list_runs(db, limit)
    
    response_data = ETLRunListResponse(
        runs=[ETLRunResponse.model_validate(r) for r in runs],
        total=total
    )

    return APIResponse(
        success=True,
        message="ETL runs history retrieved successfully",
        data=response_data
    )
