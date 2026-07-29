"""
File: test_adapter_factory.py
Purpose:
    Tests the AdapterFactory dynamic instantiation and scope boundaries.
Author: R. Rayri Sharma
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform for Betting Site Intelligence
Created By: R. Rayri Sharma
Reviewed By: Tech Lead & Solution Architect (HQ Chat)
Version: 1.1
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
from adapters.factory import AdapterFactory
from adapters.onexbet.adapter import OneXBetAdapter
from adapters.melbet.adapter import MelbetAdapter
from adapters.tencric.adapter import TenCricAdapter
from adapters.twentytwoxbet.adapter import TwentyTwoXBetAdapter


class TestAdapterFactory(unittest.TestCase):
    """
    Test suite for AdapterFactory.
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

    def test_factory_returns_onexbet_adapter(self):
        """
        Asserts that the factory correctly returns the OneXBetAdapter class for 'onexbet' site.
        """
        adapter = AdapterFactory.get_adapter(
            site_name="onexbet",
            page=self.page,
            context=self.context,
            base_url="https://1xlite-12947.pro/en",
            selectors={}
        )
        self.assertIsInstance(adapter, OneXBetAdapter)
        self.assertEqual(adapter.get_site_name(), "onexbet")

    def test_factory_returns_melbet_adapter(self):
        """
        Asserts that the factory correctly returns the MelbetAdapter class.
        """
        adapter = AdapterFactory.get_adapter(
            site_name="melbet",
            page=self.page,
            context=self.context,
            base_url="https://melbet.mobi/en",
            selectors={}
        )
        self.assertIsInstance(adapter, MelbetAdapter)
        self.assertEqual(adapter.get_site_name(), "melbet")

    def test_factory_returns_tencric_adapter(self):
        """
        Asserts that the factory correctly returns the TenCricAdapter class.
        """
        adapter = AdapterFactory.get_adapter(
            site_name="10cric",
            page=self.page,
            context=self.context,
            base_url="https://10cric.com",
            selectors={}
        )
        self.assertIsInstance(adapter, TenCricAdapter)
        self.assertEqual(adapter.get_site_name(), "10cric")

    def test_factory_returns_twentytwoxbet_adapter(self):
        """
        Asserts that the factory correctly returns the TwentyTwoXBetAdapter class.
        """
        adapter = AdapterFactory.get_adapter(
            site_name="22xbet",
            page=self.page,
            context=self.context,
            base_url="https://22bet.com",
            selectors={}
        )
        self.assertIsInstance(adapter, TwentyTwoXBetAdapter)
        self.assertEqual(adapter.get_site_name(), "22xbet")

    def test_factory_returns_tencric_alias(self):
        """
        Asserts that the factory correctly returns the TencricAdapter alias for 'tencric' site.
        """
        adapter = AdapterFactory.get_adapter(
            site_name="tencric",
            page=self.page,
            context=self.context,
            base_url="https://10cric.com",
            selectors={}
        )
        self.assertEqual(adapter.get_site_name(), "tencric")

    def test_factory_returns_twentytwobet_alias(self):
        """
        Asserts that the factory correctly returns the TwentyTwoBetAdapter alias for 'twentytwobet' site.
        """
        adapter = AdapterFactory.get_adapter(
            site_name="twentytwobet",
            page=self.page,
            context=self.context,
            base_url="https://22bet.com",
            selectors={}
        )
        self.assertEqual(adapter.get_site_name(), "twentytwobet")

    def test_factory_invalid_site_raises_value_error(self):
        """
        Asserts that the factory raises ValueError for completely unknown site keys.
        """
        with self.assertRaises(ValueError):
            AdapterFactory.get_adapter(
                site_name="invalid_platform",
                page=self.page,
                context=self.context,
                base_url="https://invalid.com",
                selectors={}
            )


if __name__ == "__main__":
    unittest.main()
