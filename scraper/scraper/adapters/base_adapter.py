"""
File: base_adapter.py
Purpose:
    Abstract base adapter defining the lifecycle of data acquisition for target sites.
Author: R. Rayri Sharma
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform for Betting Site Intelligence
Created By: R. Rayri Sharma
Reviewed By: Tech Lead & Solution Architect (HQ Chat)
Version: 1.0
"""

# Standard Library
from abc import ABC, abstractmethod
import logging
from typing import Dict, Any, List

# Third Party
from playwright.sync_api import Page, BrowserContext

# Local Imports
from models.payment import PaymentRecord
from core.screenshot import take_screenshot
from core.utils import save_html
from exporters.json_exporter import JsonExporter

# Setup Logger
logger = logging.getLogger("scraper.adapters.base_adapter")


class BaseAdapter(ABC):
    """
    Defines the contract and template routines for site-specific scraping adapters.
    """

    def __init__(
        self,
        page: Page,
        context: BrowserContext,
        site_name: str,
        base_url: str,
        selectors: Dict[str, str],
    ) -> None:
        """
        Initializes the adapter with Playwright page, context, and configurations.
        """
        self.page = page
        self.context = context
        self.site_name = site_name
        self.base_url = base_url
        self.selectors = selectors
        self.records: List[PaymentRecord] = []
        logger.info(f"Initialized BaseAdapter for: {self.site_name}")

    def get_site_name(self) -> str:
        """
        Returns the target site identifier.
        """
        return self.site_name

    def open_homepage(self) -> None:
        """
        Opens the target website landing page.
        """
        logger.info(f"Opening home page for {self.site_name}: {self.base_url}")
        self.page.goto(self.base_url)
        self.page.wait_for_load_state("load")

    @abstractmethod
    def login_if_required(self) -> None:
        """
        Authenticates session if expired or not logged in.
        Must be implemented by concrete adapters.
        """
        pass

    @abstractmethod
    def navigate_to_deposit(self) -> None:
        """
        Handles transition clicks or direct URLs to reach the deposit portal.
        Must be implemented by concrete adapters.
        """
        pass

    def wait_for_payment_page(self) -> None:
        """
        Blocks execution until the payment container elements load into view.
        """
        container_sel = self.selectors.get("payment_container", "")
        if container_sel:
            logger.info(f"Waiting for payment container: {container_sel}")
            self.page.locator(container_sel).wait_for(state="visible", timeout=15000)

    @abstractmethod
    def discover_payment_methods(self) -> List[PaymentRecord]:
        """
        Finds payment methods and extracts basic details.
        Must be implemented by concrete adapters.
        """
        pass

    @abstractmethod
    def extract_payment_details(self) -> List[PaymentRecord]:
        """
        Clicks payment options and parses detailed transaction parameters.
        Must be implemented by concrete adapters.
        """
        pass

    def validate_data(self) -> bool:
        """
        Validates all extracted records against the Pydantic data model.
        """
        logger.info(f"Validating {len(self.records)} records against the Pydantic PaymentRecord model...")
        try:
            for record in self.records:
                # Triggers validation checks of type hints and fields
                PaymentRecord.model_validate(record)
            logger.info("Data validation passed successfully.")
            return True
        except Exception as error:
            logger.error(f"Data validation failed: {str(error)}")
            return False

    def capture_evidence(self, name: str) -> None:
        """
        Saves screenshot and HTML states for debugging and audit proofing.
        """
        logger.info(f"Saving evidence snapshot for: {name}")
        take_screenshot(self.page, f"{self.site_name}_{name}")
        save_html(self.page, f"{self.site_name}_{name}")

    def export_json(self, filename: str) -> str:
        """
        Saves the validated records list into output directory.
        """
        exporter = JsonExporter()
        raw_list = [record.model_dump() for record in self.records]
        return exporter.export(raw_list, filename)

    def close(self) -> None:
        """
        Ensures the page session is closed.
        """
        logger.info(f"Closing adapter page for: {self.site_name}")
        self.page.close()
