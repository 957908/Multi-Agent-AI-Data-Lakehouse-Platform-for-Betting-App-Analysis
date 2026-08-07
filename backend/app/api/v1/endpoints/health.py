"""
File: health.py
Purpose:
    Exposes application-wide health checks and database availability.
Author: Niraj Kadam
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 1.0
"""

import logging
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from database.connection import get_db_session
from schemas.response import APIResponse

from core.exceptions import BaseAppException

logger = logging.getLogger("backend.api.health")
router = APIRouter()


@router.get("/health", response_model=APIResponse[dict])
def check_health(db: Session = Depends(get_db_session)) -> APIResponse[dict]:
    """
    Returns application and database connectivity health status.
    """
    try:
        # Trivial test query to check PostgreSQL availability
        db.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Health check failed to query database: {str(e)}")
        raise BaseAppException("Database connectivity is degraded", status_code=500)

    return APIResponse(
        success=True,
        message="System health checked.",
        data={
            "status": "online",
            "database": "healthy"
        }
    )
