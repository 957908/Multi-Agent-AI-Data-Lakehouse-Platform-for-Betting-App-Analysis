"""
File: test_exporter.py
Purpose:
    Tests the JsonExporter functionality and directory creation.
Author: R. Rayri Sharma
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform for Betting Site Intelligence
Created By: R. Rayri Sharma
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
from exporters.json_exporter import JsonExporter


class TestExporter(unittest.TestCase):
    """
    Test suite for JsonExporter.
    """

    def test_export_saves_json_file(self):
        """
        Asserts that JsonExporter creates directory and files on local storage disk.
        """
        exporter = JsonExporter(output_dir="tests/test_output")
        records = [{"id": 1, "status": "active"}]
        filename = "test_export.json"
        
        try:
            export_path = exporter.export(records, filename)
            filepath = Path(export_path)
            
            self.assertTrue(filepath.exists())
            self.assertTrue(filepath.is_file())
            self.assertEqual(filepath.name, filename)
            
        finally:
            # Cleanup test artifacts
            test_dir = Path("tests/test_output")
            if test_dir.exists():
                for f in test_dir.iterdir():
                    f.unlink()
                test_dir.rmdir()


if __name__ == "__main__":
    unittest.main()
