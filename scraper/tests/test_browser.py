"""
File: test_browser.py
Purpose:
    Unit tests for Playwright BrowserManager execution.
Author: R. Niraj Kadam
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform for Betting Site Intelligence
Created By: R. Niraj Kadam
Reviewed By: Tech Lead & Solution Architect (HQ Chat)
Version: 1.1
"""

# Standard Library
import sys
import unittest
from pathlib import Path

# Add scraper/scraper to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent / "scraper"))

# Local Imports
from core.browser import BrowserManager


class TestBrowserManager(unittest.TestCase):
    """
    Test suite for Playwright BrowserManager.
    """

    def test_browser_launch_and_close(self):
        """
        Verifies that the BrowserManager can start a browser process, 
        initialize a context, and tear everything down cleanly.
        """
        manager = BrowserManager(headless=True)
        try:
            browser = manager.start_browser()
            self.assertIsNotNone(browser)
            self.assertIsNotNone(manager.browser)
            
            context = manager.create_context()
            self.assertIsNotNone(context)
            self.assertIsNotNone(manager.context)
            
            page = context.new_page()
            self.assertIsNotNone(page)
            
        finally:
            manager.close_browser()
            self.assertIsNone(manager.browser)
            self.assertIsNone(manager.context)
            self.assertIsNone(manager.playwright)


if __name__ == "__main__":
    unittest.main()
