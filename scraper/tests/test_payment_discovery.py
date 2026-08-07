"""
File: test_payment_discovery.py
Purpose:
    Tests the PaymentDiscovery component parsing and category inferences.
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
from core.payment_discovery import PaymentDiscovery


class TestPaymentDiscovery(unittest.TestCase):
    """
    Test suite for PaymentDiscovery.
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

    def test_infer_payment_type(self):
        """
        Assures mapped method titles resolve to correct category formats.
        """
        discovery = PaymentDiscovery(self.page)
        self.assertEqual(discovery._infer_payment_type("UPI Fast"), "upi")
        self.assertEqual(discovery._infer_payment_type("PhonePe Instant"), "upi")
        self.assertEqual(discovery._infer_payment_type("Bank Transfer"), "bank_transfer")
        self.assertEqual(discovery._infer_payment_type("IMPS"), "bank_transfer")
        self.assertEqual(discovery._infer_payment_type("Bitcoin"), "cryptocurrency")
        self.assertEqual(discovery._infer_payment_type("USDT (Trc20)"), "cryptocurrency")
        self.assertEqual(discovery._infer_payment_type("Skrill Wallet"), "e-wallet")
        self.assertEqual(discovery._infer_payment_type("Net Banking"), "net_banking")
        self.assertEqual(discovery._infer_payment_type("Visa Card"), "other")


if __name__ == "__main__":
    unittest.main()
