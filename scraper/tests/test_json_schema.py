"""
File: test_json_schema.py
Purpose:
    Tests the PaymentRecord Pydantic data model and Schema version 1.1 validation rules.
Author: R. Niraj Kadam
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform for Betting Site Intelligence
Created By: R. Niraj Kadam
Reviewed By: Tech Lead & Solution Architect (HQ Chat)
Version: 1.0
"""

# Standard Library
import sys
import unittest
from pathlib import Path

# Add scraper/scraper to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent / "scraper"))

# Local Imports
from models.payment import PaymentRecord


class TestJsonSchema(unittest.TestCase):
    """
    Test suite for checking that payment records match Pydantic schema constraints.
    """

    def test_valid_record(self):
        """
        Tests that a fully complete dictionary validations succeed.
        """
        raw_data = {
            "source_platform": "onexbet",
            "extraction_status": "success",
            "extraction_method": "playwright_sync",
            "site": "onexbet",
            "payment_type": "upi",
            "payment_name": "UPI Fast",
            "source_url": "https://1xlite-12947.pro/en/office/recharge/",
            "scraped_at": "2026-07-26T08:25:03Z",
            "extracted_data": {
                "upi_id": "merchant.pay@okaxis",
                "payee_name": "OneXBet Solutions Private Limited",
                "min_deposit": "500",
                "max_deposit": "50000"
            }
        }
        
        # Validating using Pydantic
        record = PaymentRecord(**raw_data)
        self.assertEqual(record.schema_version, "1.1")
        self.assertEqual(record.scraper_version, "1.0.0")
        self.assertEqual(record.payment_type, "upi")
        self.assertEqual(record.extracted_data["upi_id"], "merchant.pay@okaxis")

    def test_missing_required_fields_fails(self):
        """
        Tests that omitting a required field fails validation checks.
        """
        # Missing "source_platform" and "extraction_status"
        invalid_data = {
            "site": "onexbet",
            "payment_type": "upi",
            "payment_name": "UPI Fast",
            "source_url": "https://1xlite-12947.pro/en/office/recharge/",
            "scraped_at": "2026-07-26T08:25:03Z",
        }
        
        with self.assertRaises(Exception):
            PaymentRecord(**invalid_data)


if __name__ == "__main__":
    unittest.main()
