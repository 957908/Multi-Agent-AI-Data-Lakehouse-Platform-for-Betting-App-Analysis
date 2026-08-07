"""
File: test_selectors.py
Purpose:
    Unit tests for verifying modular selectors.
Author: R. Niraj Kadam
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform for Betting Site Intelligence
Created By: R. Niraj Kadam
Reviewed By: Tech Lead & Solution Architect (HQ Chat)
Version: 1.2
"""

# Standard Library
import sys
import unittest
from pathlib import Path

# Add scraper/scraper to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent / "scraper"))

# Local Imports
from config.selectors.onexbet import SELECTORS as ONEXBET_SELECTORS
from config.selectors.melbet import SELECTORS as MELBET_SELECTORS


class TestSelectors(unittest.TestCase):
    """
    Test suite for config/selectors/ modular site selectors.
    """

    def test_selectors_structure(self):
        """
        Verifies key selector configuration existence in the refactored modules.
        """
        self.assertIn("username", ONEXBET_SELECTORS)
        self.assertIn("password", ONEXBET_SELECTORS)
        self.assertIn("login_button", ONEXBET_SELECTORS)
        self.assertIn("login_popup_button", ONEXBET_SELECTORS)
        
        self.assertIn("username", MELBET_SELECTORS)
        self.assertIn("password", MELBET_SELECTORS)
        self.assertIn("login_button", MELBET_SELECTORS)


if __name__ == "__main__":
    unittest.main()
