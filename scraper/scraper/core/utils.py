"""
File: utils.py
Purpose:
    General helper functions and setup configurations for logging and HTML capture.
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
from config.settings import OUTPUT_DIR, LOG_LEVEL


def setup_logging() -> None:
    """
    Initializes system-wide logging with Console and File outputs.
    """
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / "scraper.log"
    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(str(log_file), encoding="utf-8")
        ]
    )
    logging.getLogger("scraper").info(f"Logging initialized. Level={LOG_LEVEL}, File={log_file}")


def save_html(page: Page, name: str) -> str:
    """
    Saves the complete outer HTML markup of the page for troubleshooting.
    """
    html_dir = Path(OUTPUT_DIR) / "html"
    html_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{name}_{timestamp}.html"
    filepath = html_dir / filename

    logger = logging.getLogger("scraper.core.utils")
    logger.info(f"Saving outer HTML state to: {filepath}")
    
    try:
        content = page.content()
        filepath.write_text(content, encoding="utf-8")
        logger.info("HTML state dump completed successfully.")
        return str(filepath)
    except Exception as error:
        logger.error(f"Failed to save HTML dump: {str(error)}")
        return ""
