"""
File: etl.py
Purpose:
    Pydantic schemas for ETL pipeline execution runs.
Author: Arjun Mehta
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 1.0
"""

from datetime import datetime
from typing import List
from pydantic import BaseModel


class ETLRunResponse(BaseModel):
    """
    Schema representing a logged execution run of the ETL pipeline.
    """
    id: int
    run_path: str
    records_scraped: int
    records_processed: int
    records_failed: int
    status: str
    processed_at: datetime

    class Config:
        from_attributes = True


class ETLRunListResponse(BaseModel):
    """
    List wrapper for ETL runs.
    """
    runs: List[ETLRunResponse]
    total: int
