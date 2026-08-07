"""
File: test_navigation.py
Purpose:
    Tests the NavigationManager popup triggers and routing.
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

# Third Party
from playwright.sync_api import sync_playwright

# Local Imports
from core.navigation import NavigationManager


class TestNavigation(unittest.TestCase):
    """
    Test suite for NavigationManager.
    """

    def setUp(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

    def tearDown(self):
        self.context.close()
        self.browser.close()
        self.playwright.stop()

    def test_navigate_to_url(self):
        """
        Verifies that NavigationManager completes direct navigations.
        """
        nav_mgr = NavigationManager(self.page)
        # Using a blank local page loading test to avoid external dependencies in unit testing
        nav_mgr.navigate_to_url("about:blank")
        self.assertEqual(self.page.url, "about:blank")


if __name__ == "__main__":
    unittest.main()
