"""
File: run_tests.py
Purpose:
    Executes all unittest files inside the tests/ directory.
Author: R. Niraj Kadam
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform for Betting Site Intelligence
Created By: R. Niraj Kadam
Reviewed By: Tech Lead & Solution Architect (HQ Chat)
Version: 1.0
"""

import sys
import unittest
from pathlib import Path

# Add scraper/scraper to sys.path
sys.path.append(str(Path(__file__).resolve().parent / "scraper"))

def main():
    print("=== Running SentinelX Trust AI Data Acquisition Unit Tests ===")
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=str(Path(__file__).resolve().parent / "tests"), pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(not result.wasSuccessful())

if __name__ == "__main__":
    main()
