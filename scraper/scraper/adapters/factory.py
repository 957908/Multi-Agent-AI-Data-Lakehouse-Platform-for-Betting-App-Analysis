"""
File: factory.py
Purpose:
    AdapterFactory for instantiating the correct site adapter dynamically.
Author: R. Rayri Sharma
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform for Betting Site Intelligence
Created By: R. Rayri Sharma
Reviewed By: Tech Lead & Solution Architect (HQ Chat)
Version: 1.1
"""

# Standard Library
import logging
from typing import Dict, Type

# Third Party
from playwright.sync_api import Page, BrowserContext

# Local Imports
from adapters.base_adapter import BaseAdapter
from adapters.onexbet.adapter import OneXBetAdapter
from adapters.melbet.adapter import MelbetAdapter
from adapters.tencric.adapter import TenCricAdapter, TencricAdapter
from adapters.twentytwoxbet.adapter import TwentyTwoXBetAdapter, TwentyTwoBetAdapter

# Setup Logger
logger = logging.getLogger("scraper.adapters.factory")


class AdapterFactory:
    """
    Factory class to return concrete adapter instances dynamically.
    """

    _registry: Dict[str, Type[BaseAdapter]] = {
        "onexbet": OneXBetAdapter,
        "1xbet": OneXBetAdapter,
        "melbet": MelbetAdapter,
        "10cric": TenCricAdapter,
        "tencric": TencricAdapter,
        "twentytwobet": TwentyTwoBetAdapter,
        "twentytwoxbet": TwentyTwoXBetAdapter,
        "22xbet": TwentyTwoXBetAdapter,
    }

    @classmethod
    def get_adapter(
        cls,
        site_name: str,
        page: Page,
        context: BrowserContext,
        base_url: str,
        selectors: Dict[str, str],
    ) -> BaseAdapter:
        """
        Instantiates and returns the corresponding BaseAdapter subclass based on site_name.
        """
        normalized_name = site_name.lower().strip()
        logger.info(f"Factory resolving adapter for: {normalized_name}")

        if normalized_name in cls._registry:
            adapter_class = cls._registry[normalized_name]
            return adapter_class(page, context, normalized_name, base_url, selectors)
        
        logger.error(f"Unknown site name supplied to factory: {normalized_name}")
        raise ValueError(f"No adapter registered for site name: {site_name}")
