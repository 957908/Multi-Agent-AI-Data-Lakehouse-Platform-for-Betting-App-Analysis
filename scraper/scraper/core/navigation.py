"""
File: navigation.py
Purpose:
    Handles browser navigation flows, login popup activation, and target page discovery.
    Enhanced with configurable timeouts, connection diagnostics, and retry logic.
Author: R. Rayri Sharma
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform for Betting Site Intelligence
Created By: R. Rayri Sharma
Reviewed By: Tech Lead & Solution Architect (HQ Chat)
Version: 2.0
"""

# Standard Library
import logging
import time
from typing import Dict, Optional

# Third Party
from playwright.sync_api import Page

# Local Imports
from core.retry_utils import retry_operation

# Setup Logger
logger = logging.getLogger("scraper.core.navigation")


class NavigationManager:
    """
    Manages complex page state transitions, including popup activation, connection diagnostics, and retry logic.
    """

    def __init__(self, page: Page) -> None:
        """
        Initializes the NavigationManager with the target Page.
        """
        self.page = page
        logger.info("Initialized Resilient NavigationManager.")

    def open_login_popup(self, selectors: Dict[str, str]) -> None:
        """
        Activates the login popup modal if it is not already visible in the viewport.
        """
        logger.info("Checking if login form is already open...")
        username_sel = selectors["username"]
        
        try:
            # Check if username field is already visible on the screen
            if self.page.locator(username_sel).first.is_visible():
                logger.info("Login form is already visible. Skipping popup activation.")
                return
        except Exception:
            pass

        logger.info("Login form not visible. Locating trigger button...")
        trigger_sel = selectors.get("login_popup_button")
        if not trigger_sel:
            logger.error("No login_popup_button selector defined in configuration.")
            raise ValueError("Configuration missing login_popup_button selector.")

        logger.info(f"Clicking login popup trigger: {trigger_sel}")
        self.page.locator(trigger_sel).first.wait_for(state="visible", timeout=8000)
        self.page.locator(trigger_sel).first.click()

        # Wait for the username field to be loaded and visible
        logger.info(f"Waiting for username selector '{username_sel}' to appear...")
        self.page.locator(username_sel).first.wait_for(state="visible", timeout=8000)
        logger.info("Login popup activated successfully.")

    def navigate_to_url(self, url: str, timeout_ms: int = 20000) -> None:
        """
        Performs a direct navigation to a target URL with configurable timeout and connection diagnostics.
        """
        logger.info(f"Navigating page to URL: {url} (timeout={timeout_ms}ms)")
        
        def attempt_navigation():
            self.page.goto(url, timeout=timeout_ms)
            self.page.wait_for_load_state("load", timeout=timeout_ms)

        try:
            # Wrap navigation in centralized retry runner
            retry_operation(
                attempt_navigation,
                retries=3,
                delay=2.0,
                exceptions=(Exception,),
                action_name=f"Navigation to {url}"
            )
            logger.info("Navigation complete and page loaded successfully.")
        except Exception as error:
            # Trigger Connection Diagnostics
            self._diagnose_navigation_error(url, error)
            raise

    def navigate_to_deposit(self, selectors: Dict[str, str]) -> None:
        """
        Clicks deposit buttons to transition the UI to the deposit/recharge gateway page.
        """
        deposit_btn_sel = selectors.get("deposit_button")
        if not deposit_btn_sel:
            logger.error("No deposit_button selector defined in configuration.")
            raise ValueError("Configuration missing deposit_button selector.")

        logger.info(f"Locating and clicking deposit button: {deposit_btn_sel}")
        
        def perform_deposit_click():
            self.page.locator(deposit_btn_sel).first.wait_for(state="visible", timeout=10000)
            self.page.locator(deposit_btn_sel).first.click()
            self.page.wait_for_load_state("networkidle", timeout=15000)

        try:
            retry_operation(
                perform_deposit_click,
                retries=3,
                delay=1.0,
                exceptions=(Exception,),
                action_name="Navigate to Deposit Panel"
            )
            logger.info("Click transition to deposit panel complete.")
        except Exception as error:
            logger.warning(f"Failed to navigate via deposit button click: {str(error)}")
            raise

    def _diagnose_navigation_error(self, url: str, error: Exception) -> None:
        """
        Analyzes exception logs to print structured connection diagnostics warnings.
        """
        err_msg = str(error).upper()
        logger.error("================ CONNECTION DIAGNOSTICS ==================")
        logger.error(f"Target URL: {url}")
        
        if "ERR_NAME_NOT_RESOLVED" in err_msg:
            logger.error("Diagnostic Result: [DNS FAILURE] The target hostname could not be resolved.")
        elif "ERR_CONNECTION_TIMED_OUT" in err_msg or "TIMEOUT" in err_msg:
            logger.error("Diagnostic Result: [TIMEOUT] Connection timed out. The web server is offline or blocking requests.")
        elif "ERR_CONNECTION_REFUSED" in err_msg:
            logger.error("Diagnostic Result: [CONNECTION REFUSED] The target server rejected connection requests.")
        else:
            logger.error(f"Diagnostic Result: [UNCLASSIFIED FAILURE] {str(error)}")
            
        logger.error("==========================================================")