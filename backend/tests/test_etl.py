"""
File: test_etl.py
Purpose:
    Integration testing for the PySpark ETL pipeline.
    Mocks PostgreSQL connections to enable 100% local validation.
Author: Priya Iyer
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 1.0
"""

import sys
import os
import json
import shutil
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Ensure backend/app/ is in python path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from config.settings import settings
from services.etl.spark_etl import SparkETLPipeline


class TestETLPipeline(unittest.TestCase):
    """
    Test suite verifying ETL validations, transformations, deduplications,
    and DLQ/Report generation using local Spark.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """Sets up temporary folders and test datasets."""
        cls.test_dir = Path(__file__).resolve().parent / "test_data"
        cls.test_dir.mkdir(exist_ok=True)
        
        # Override paths to target the test data directory
        settings.RAW_DATA_DIR = str(cls.test_dir / "raw")
        settings.BRONZE_DATA_DIR = str(cls.test_dir / "bronze")
        settings.SILVER_DATA_DIR = str(cls.test_dir / "silver")
        settings.DLQ_DIR = str(cls.test_dir / "dlq")
        settings.REPORTS_DIR = str(cls.test_dir / "reports")

        # Create a mock raw run path directory
        cls.run_path = "2026-07-26/12-00"
        cls.raw_run_dir = Path(settings.RAW_DATA_DIR) / cls.run_path
        cls.raw_run_dir.mkdir(parents=True, exist_ok=True)

        # Mock scraped JSON data
        cls.mock_data = [
            # Record 1: Valid payment record
            {
                "schema_version": "1.1",
                "scraper_version": "1.0.0",
                "source_platform": "10cric",
                "extraction_status": "success",
                "extraction_method": "playwright_sync",
                "site": "10cric",
                "page_type": "deposit_page",
                "payment_type": "upi instant", # Standardizes to UPI
                "payment_name": "UPI Netbanking",
                "currency": "INR",
                "country": "IN",
                "bonus_name": "Welcome Bonus",
                "support_type": "live_chat",
                "support_value": "https://10cric.support",
                "status": "success", # Standardizes to active
                "source_url": "https://10cric.com/payments",
                "scraped_at": "2026-07-26T12:00:00Z",
                "extracted_data": {"min_deposit": "500"}
            },
            # Record 2: Duplicate of Record 1 but older (scraped_at = 11:59:00Z)
            # Should be discarded during Spark deduplication
            {
                "schema_version": "1.1",
                "scraper_version": "1.0.0",
                "source_platform": "10cric",
                "extraction_status": "success",
                "extraction_method": "playwright_sync",
                "site": "10cric",
                "page_type": "deposit_page",
                "payment_type": "upi instant",
                "payment_name": "UPI Netbanking",
                "currency": "INR",
                "country": "IN",
                "bonus_name": "Welcome Bonus",
                "support_type": "live_chat",
                "support_value": "https://10cric.support",
                "status": "success",
                "source_url": "https://10cric.com/payments",
                "scraped_at": "2026-07-26T11:59:00Z",
                "extracted_data": {"min_deposit": "500"}
            },
            # Record 3: Invalid payment record (missing required 'payment_name' and invalid URL)
            # Should be routed to DLQ
            {
                "schema_version": "1.1",
                "scraper_version": "1.0.0",
                "source_platform": "melbet",
                "extraction_status": "success",
                "extraction_method": "playwright_sync",
                "site": "melbet",
                "page_type": "deposit_page",
                "payment_type": "crypto",
                "payment_name": "", # Violation: required key
                "currency": "USD",
                "country": "BG",
                "source_url": "invalid-url-no-protocol", # Violation: invalid URL
                "scraped_at": "2026-07-26T12:00:00Z"
            }
        ]

        # Write mock data to JSON file
        with open(cls.raw_run_dir / "mock_payments.json", "w", encoding="utf-8") as f:
            json.dump(cls.mock_data, f)

    @classmethod
    def tearDownClass(cls) -> None:
        """Cleans up the temporary directories."""
        if cls.test_dir.exists():
            shutil.rmtree(cls.test_dir, ignore_errors=True)

    @patch("services.etl.spark_etl.get_db")
    def test_full_pipeline_flow(self, mock_get_db) -> None:
        """
        Tests the end-to-end ingestion, validation, deduplication, 
        DLQ generation, and Parquet exports.
        """
        # Mock database session and queries
        mock_session = MagicMock()
        mock_get_db.return_value.__enter__.return_value = mock_session

        # Instantiate pipeline
        pipeline = SparkETLPipeline()

        try:
            # Inject a mock run log query to return no existing runs (so it runs)
            mock_session.query.return_value.filter.return_value.first.return_value = None

            # Execute pipeline for the mock run path
            success = pipeline.process_run(self.run_path)
            
            # Assertions
            self.assertTrue(success, "Pipeline execution failed.")

            # 1. Verify Bronze Layer (Raw Parquet Backup)
            bronze_path = Path(settings.BRONZE_DATA_DIR) / self.run_path
            self.assertTrue(bronze_path.exists(), "Bronze layer directory was not created.")
            self.assertTrue(list(bronze_path.glob("*.parquet")), "Bronze Parquet backup is missing.")

            # 2. Verify DLQ Output (Invalid records isolated)
            dlq_file = Path(settings.DLQ_DIR) / "2026-07-26" / "invalid_records.json"
            self.assertTrue(dlq_file.exists(), "DLQ file was not generated.")
            
            with open(dlq_file, "r", encoding="utf-8") as df:
                dlq_records = json.load(df)
                self.assertEqual(len(dlq_records), 1, "DLQ should contain exactly one invalid record.")
                self.assertEqual(dlq_records[0]["site"], "melbet")
                self.assertIn("__validation_errors__", dlq_records[0], "DLQ record should contain validation errors.")

            # 3. Verify Silver Layer (Transformed and Deduplicated)
            silver_path = Path(settings.SILVER_DATA_DIR) / self.run_path
            self.assertTrue(silver_path.exists(), "Silver layer directory was not created.")
            self.assertTrue(list(silver_path.glob("*.parquet")), "Silver Parquet data is missing.")

            # Read Silver Parquet using pandas to verify content and deduplication
            import pandas as pd
            silver_files = list(silver_path.glob("*.parquet"))
            silver_pdf = pd.concat([pd.read_parquet(f) for f in silver_files], ignore_index=True)
            silver_records = silver_pdf.to_dict(orient="records")

            # Assert deduplication: original mock had 2 valid duplicates (one newer, one older).
            # The older duplicate should be removed, leaving exactly 1 record.
            self.assertEqual(len(silver_records), 1, "Silver layer deduplication failed.")
            
            clean_rec = silver_records[0]
            self.assertEqual(clean_rec["payment_type"], "UPI", "Payment type normalization failed.")
            self.assertEqual(clean_rec["status"], "active", "Status normalization failed.")
            self.assertEqual(clean_rec["scraped_at"], "2026-07-26T12:00:00Z", "Deduplication did not pick the latest scraped_at timestamp.")

            # 4. Verify Quality Report
            report_file = Path(settings.REPORTS_DIR) / self.run_path / "etl_quality_report.md"
            self.assertTrue(report_file.exists(), "Data quality report was not generated.")

        finally:
            pipeline.shutdown()


if __name__ == "__main__":
    unittest.main()
