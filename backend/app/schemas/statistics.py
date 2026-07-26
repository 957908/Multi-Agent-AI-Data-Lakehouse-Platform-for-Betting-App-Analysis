"""
File: statistics.py
Purpose:
    Pydantic schemas representing platform analytical statistics and pipeline execution metrics.
Author: Arjun Mehta
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 1.0
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field


class SiteDistribution(BaseModel):
    site: str
    count: int


class PaymentTypeDistribution(BaseModel):
    payment_type: str
    count: int


class CountryDistribution(BaseModel):
    country: str
    count: int


class PlatformStatisticsResponse(BaseModel):
    """
    Consolidated analytics summary of payment records in database.
    """
    total_records: int = Field(..., description="Total payment records stored")
    unique_sites: int = Field(..., description="Number of unique source sites")
    unique_payment_types: int = Field(..., description="Number of unique payment types")
    distribution_by_site: List[SiteDistribution] = Field(default_factory=list)
    distribution_by_type: List[PaymentTypeDistribution] = Field(default_factory=list)
    distribution_by_country: List[CountryDistribution] = Field(default_factory=list)


class IngestionMetricsResponse(BaseModel):
    """
    Ingestion telemetry and performance metrics derived from ETL runs.
    """
    total_runs: int = Field(..., description="Total runs logged")
    successful_runs: int = Field(..., description="Total successful runs")
    failed_runs: int = Field(..., description="Total failed runs")
    total_scraped_records: int = Field(..., description="Total raw scraped records")
    total_processed_records: int = Field(..., description="Total processed silver/gold records")
    total_failed_records: int = Field(..., description="Total rejected/invalid records")
    success_rate: float = Field(..., description="Deduplicated processing success rate percent")
