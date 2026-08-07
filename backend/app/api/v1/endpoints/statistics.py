"""
File: statistics.py
Purpose:
    Exposes analytical aggregation statistics and ETL pipeline ingestion metrics.
Author: Niraj Kadam
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 1.0
"""

import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.connection import get_db_session
from core.security import RoleChecker
from repositories.payment_repository import PaymentRepository
from repositories.etl_repository import ETLRepository
from schemas.statistics import PlatformStatisticsResponse, IngestionMetricsResponse
from schemas.response import APIResponse

logger = logging.getLogger("backend.api.statistics")
router = APIRouter(tags=["analytics-metrics"])

# Require any valid role for viewing analytics
reader_auth = Depends(RoleChecker(allowed_roles=["reader", "analyst", "admin"]))


@router.get("/statistics", response_model=APIResponse[PlatformStatisticsResponse])
def get_platform_statistics(
    db: Session = Depends(get_db_session),
    current_user: dict = reader_auth
) -> APIResponse[PlatformStatisticsResponse]:
    """
    Exposes analytical distributions and totals of curated payment records.
    """
    logger.info(f"Generating platform stats requested by {current_user.get('email')}")
    stats_data = PaymentRepository.get_statistics(db)
    response_data = PlatformStatisticsResponse(**stats_data)
    
    return APIResponse(
        success=True,
        message="Platform statistics calculated successfully",
        data=response_data
    )


@router.get("/metrics", response_model=APIResponse[IngestionMetricsResponse])
def get_ingestion_metrics(
    db: Session = Depends(get_db_session),
    current_user: dict = reader_auth
) -> APIResponse[IngestionMetricsResponse]:
    """
    Exposes telemetry metrics regarding pipeline execution runs and success rates.
    """
    logger.info(f"Generating ETL ingestion metrics requested by {current_user.get('email')}")
    metrics_data = ETLRepository.get_metrics(db)
    response_data = IngestionMetricsResponse(**metrics_data)
    
    return APIResponse(
        success=True,
        message="Ingestion metrics calculated successfully",
        data=response_data
    )
