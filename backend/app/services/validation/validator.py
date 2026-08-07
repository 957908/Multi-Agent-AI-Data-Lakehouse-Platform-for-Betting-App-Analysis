"""
File: validator.py
Purpose:
    Enforces schema validation rules on scraped payment records.
    Leverages the scraper's PaymentRecord model to guarantee data contract compliance.
Author: Niraj Kadam
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform
Version: 1.0
"""

import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from pydantic import ValidationError

# Dynamically add scraper/scraper to path to consume the contract models
PROJECT_ROOT = Path(__file__).resolve().parents[4]
SCRAPER_PATH = PROJECT_ROOT / "scraper" / "scraper"
if str(SCRAPER_PATH) not in sys.path:
    sys.path.append(str(SCRAPER_PATH))

from models.payment import PaymentRecord

logger = logging.getLogger("backend.services.validation.validator")


class DataValidator:
    """
    Validates raw dictionary payloads against the PaymentRecord schema,
    verifies critical fields, and routes invalid items to a Dead Letter Queue layout.
    """

    @staticmethod
    def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
        """
        Validates and parses date strings to verify compliance with ISO 8601 formatting.
        """
        for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        return None

    def validate_record(self, raw_data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Validates a single record against schema constraints.
        
        Returns:
            Tuple of (is_valid, validated_dict, error_message)
        """
        # 1. Null / Missing values on core fields
        if not raw_data:
            return False, None, "Record is empty"

        required_keys = ["site", "source_url", "scraped_at", "payment_type", "payment_name"]
        for key in required_keys:
            if not raw_data.get(key):
                return False, raw_data, f"Missing required core field: {key}"

        # 2. Verify timestamp parsing
        scraped_at_val = raw_data.get("scraped_at")
        parsed_date = self.parse_timestamp(str(scraped_at_val))
        if not parsed_date:
            return False, raw_data, f"Invalid scraped_at timestamp format: {scraped_at_val}"

        # 3. URL Syntax Check
        url = str(raw_data.get("source_url"))
        if not (url.startswith("http://") or url.startswith("https://")):
            return False, raw_data, f"Invalid source_url protocol: {url}"

        # 4. Pydantic Contract compliance check
        try:
            # Reconstruct model
            record_model = PaymentRecord(**raw_data)
            validated_dict = record_model.model_dump()
            
            # Keep python datetime object ready for DB loading
            validated_dict["scraped_at_datetime"] = parsed_date
            return True, validated_dict, None
        except ValidationError as val_err:
            errors_summary = "; ".join([f"{'.'.join(str(l) for l in err['loc'])}: {err['msg']}" for err in val_err.errors()])
            return False, raw_data, f"Pydantic Validation Error - {errors_summary}"
        except Exception as general_err:
            return False, raw_data, f"Unexpected validation failure: {str(general_err)}"

    def validate_batch(self, records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Processes a batch of records, classifying them into clean and invalid datasets.
        
        Returns:
            Tuple of (valid_records, invalid_records_with_errors)
        """
        valid_records: List[Dict[str, Any]] = []
        invalid_records: List[Dict[str, Any]] = []

        for index, record in enumerate(records):
            is_valid, processed_record, error_msg = self.validate_record(record)
            if is_valid and processed_record:
                valid_records.append(processed_record)
            else:
                bad_record = dict(record) if record else {}
                bad_record["__validation_errors__"] = error_msg or "Unknown Validation Error"
                bad_record["__record_index__"] = index
                invalid_records.append(bad_record)

        logger.info(f"Validated Batch: {len(valid_records)} passed, {len(invalid_records)} rejected.")
        return valid_records, invalid_records
