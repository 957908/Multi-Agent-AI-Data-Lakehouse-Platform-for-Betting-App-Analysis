"""
File: etl_repository.py
Purpose:
    Encapsulates database access patterns for the etl_runs tracking table.
Author: Niraj Kadam
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 1.0
"""

from typing import List, Tuple, Dict, Any
from sqlalchemy import func, desc
from sqlalchemy.orm import Session
from database.models import ETLRun


class ETLRepository:
    """
    Repository class providing access methods for ETLRun model tracking logs.
    """

    @staticmethod
    def list_runs(db: Session, limit: int = 100) -> Tuple[List[ETLRun], int]:
        """
        Retrieves historical execution runs of the ETL pipeline, sorted by processing date.
        """
        query = db.query(ETLRun)
        total_count = query.count()
        runs = query.order_by(desc(ETLRun.processed_at)).limit(limit).all()
        return runs, total_count

    @staticmethod
    def get_metrics(db: Session) -> Dict[str, Any]:
        """
        Aggregates operational metrics across all ETL ingestion runs.
        """
        total_runs = db.query(ETLRun).count()
        success_runs = db.query(ETLRun).filter(ETLRun.status.ilike("success")).count()
        failed_runs = db.query(ETLRun).filter(ETLRun.status.ilike("failed")).count()

        # Sum of records
        sums = db.query(
            func.sum(ETLRun.records_scraped).label("scraped"),
            func.sum(ETLRun.records_processed).label("processed"),
            func.sum(ETLRun.records_failed).label("failed")
        ).first()

        total_scraped = int(sums.scraped or 0) if sums else 0
        total_processed = int(sums.processed or 0) if sums else 0
        total_failed = int(sums.failed or 0) if sums else 0

        # Calculate success rate percent
        total_attempts = total_processed + total_failed
        success_rate = round((total_processed / total_attempts) * 100, 2) if total_attempts > 0 else 0.0

        return {
            "total_runs": total_runs,
            "successful_runs": success_runs,
            "failed_runs": failed_runs,
            "total_scraped_records": total_scraped,
            "total_processed_records": total_processed,
            "total_failed_records": total_failed,
            "success_rate": success_rate
        }
