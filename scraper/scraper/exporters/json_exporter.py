"""
File: json_exporter.py
Purpose:
    Exports extracted structured payment items to standard compliant JSON files.
Author: R. Niraj Kadam
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform for Betting Site Intelligence
Created By: R. Niraj Kadam
Reviewed By: Tech Lead & Solution Architect (HQ Chat)
Version: 1.0
"""

# Standard Library
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

# Local Imports
from config.settings import OUTPUT_DIR

# Setup Logger
logger = logging.getLogger("scraper.exporters.json_exporter")


class JsonExporter:
    """
    Handles structured record formatting and local file persistence in JSON format.
    """

    def __init__(self, output_dir: str = OUTPUT_DIR) -> None:
        """
        Initializes the JsonExporter with output path.
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized JsonExporter with output directory: {self.output_dir.resolve()}")

    def export(self, records: List[Dict[str, Any]], filename: str) -> str:
        """
        Saves list of records as a prettified JSON array file.
        """
        if not filename.endswith(".json"):
            filename += ".json"
            
        filepath = self.output_dir / filename
        logger.info(f"Exporting {len(records)} records to: {filepath}")
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=4, ensure_ascii=False)
            logger.info("Export completed successfully.")
            return str(filepath)
        except Exception as error:
            logger.error(f"Failed to export records to JSON: {str(error)}")
            raise
