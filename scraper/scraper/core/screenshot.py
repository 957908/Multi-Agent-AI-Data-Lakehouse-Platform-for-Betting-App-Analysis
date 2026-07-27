"""
File: screenshot.py
Purpose:
    Utility functions for capturing screenshots during scraping sessions.
Author: R. Rayri Sharma
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform for Betting Site Intelligence
Created By: R. Rayri Sharma
Reviewed By: Tech Lead & Solution Architect (HQ Chat)
Version: 1.0
"""

# Standard Library
from datetime import datetime
import logging
from pathlib import Path

# Third Party
from playwright.sync_api import Page

# Local Imports
from config.settings import OUTPUT_DIR, SCREENSHOT

# Setup Logger
logger = logging.getLogger("scraper.core.screenshot")


def take_screenshot(page: Page, name: str) -> str:
    """
    Captures screenshot of the current page state if enabled in settings.
    Saves it to the output/screenshots/ folder.
    """
    if not SCREENSHOT:
        logger.debug("Screenshot capture is disabled in settings. Skipping.")
        return ""

    # Ensure directories exist
    screenshots_dir = Path(OUTPUT_DIR) / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{name}_{timestamp}.png"
    filepath = screenshots_dir / filename

    logger.info(f"Capturing page screenshot to: {filepath}")
    try:
        page.screenshot(path=str(filepath), full_page=False)
        logger.info("Screenshot saved successfully.")
        return str(filepath)
    except Exception as error:
        logger.error(f"Failed to capture screenshot: {str(error)}")
        return ""
