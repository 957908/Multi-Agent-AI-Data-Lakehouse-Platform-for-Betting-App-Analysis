"""
File: browser.py
Purpose:
    Low-level Playwright browser process and context manager.
Author: R. Niraj Kadam
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform for Betting Site Intelligence
Created By: R. Niraj Kadam
Reviewed By: Tech Lead & Solution Architect (HQ Chat)
Version: 1.1
"""

# Standard Library
import logging
from typing import Optional, Dict, Any

# Third Party
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Playwright

# Local Imports
from config.settings import (
    HEADLESS,
    WAIT_TIMEOUT,
    USER_AGENT,
    VIEWPORT_WIDTH,
    VIEWPORT_HEIGHT,
    LOCALE,
    TIMEZONE,
)

# Setup Logger
logger = logging.getLogger("scraper.core.browser")


class BrowserManager:
    """
    Manages Playwright browser instance lifecycle and browser contexts.
    """

    def __init__(self, headless: Optional[bool] = None, wait_timeout: Optional[int] = None) -> None:
        """
        Initializes the browser manager using centralized settings.
        """
        self.headless: bool = headless if headless is not None else HEADLESS
        self.wait_timeout: int = wait_timeout if wait_timeout is not None else WAIT_TIMEOUT
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None

        logger.info(
            f"Initialized BrowserManager: headless={self.headless}, timeout={self.wait_timeout}s"
        )

    def start_browser(self) -> Browser:
        """
        Launches the Chromium browser process with custom anti-detection arguments.
        """
        logger.info("Launching browser process via Playwright...")
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-extensions",
                ],
            )
            logger.info("Browser process launched successfully.")
            return self.browser
        except Exception as error:
            logger.error(f"Failed to launch browser process: {str(error)}")
            self.close_browser()
            raise

    def create_context(self, storage_state_path: Optional[str] = None) -> BrowserContext:
        """
        Creates an isolated browser context with anti-detection configurations.
        """
        if not self.browser:
            logger.error("Attempted to create context without launching browser.")
            raise RuntimeError("Browser process is not running. Call start_browser() first.")

        logger.info("Creating browser context...")
        
        # Evasion parameters loaded from config/settings.py
        context_args: Dict[str, Any] = {
            "user_agent": USER_AGENT,
            "viewport": {"width": VIEWPORT_WIDTH, "height": VIEWPORT_HEIGHT},
            "locale": LOCALE,
            "timezone_id": TIMEZONE,
            "ignore_https_errors": True,
        }

        if storage_state_path:
            logger.info(f"Loading persistent storage state from: {storage_state_path}")
            context_args["storage_state"] = storage_state_path

        try:
            self.context = self.browser.new_context(**context_args)
            
            # Script injection to spoof navigator.webdriver detection
            self.context.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            
            logger.info("Browser context created successfully.")
            return self.context
        except Exception as error:
            logger.error(f"Failed to create browser context: {str(error)}")
            raise

    def close_browser(self) -> None:
        """
        Ensures active page contexts, browser processes, and Playwright objects are cleanly terminated.
        """
        logger.info("Starting browser shutdown sequence...")
        try:
            if self.context:
                logger.info("Closing browser context...")
                self.context.close()
                self.context = None
            
            if self.browser:
                logger.info("Closing browser process...")
                self.browser.close()
                self.browser = None
                
            if self.playwright:
                logger.info("Stopping Playwright context manager...")
                self.playwright.stop()
                self.playwright = None
                
            logger.info("Browser teardown complete.")
        except Exception as error:
            logger.critical(f"Error during browser process cleanup: {str(error)}")
            self.context = None
            self.browser = None
            self.playwright = None