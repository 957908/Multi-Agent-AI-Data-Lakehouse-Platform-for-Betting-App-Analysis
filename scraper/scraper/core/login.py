"""
File: login.py
Purpose:
    Handles authentication flows on target websites using Playwright with manual fallback.
Author: R. Niraj Kadam
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform for Betting Site Intelligence
Created By: R. Niraj Kadam
Reviewed By: Tech Lead & Solution Architect (HQ Chat)
Version: 1.0
"""

# Standard Library
import logging
from typing import Dict

# Third Party
from playwright.sync_api import Page

# Local Imports
from config.settings import USERNAME, PASSWORD, HEADLESS

# Setup Logger
logger = logging.getLogger("scraper.core.login")


class LoginManager:
    """
    Manages automated authentication and manual intervention fallbacks.
    """

    def __init__(self, page: Page, username: str = USERNAME, password: str = PASSWORD) -> None:
        """
        Initializes the LoginManager with standard target page and credentials.
        """
        self.page = page
        self.username = username
        self.password = password
        logger.info("Initialized LoginManager.")

    def login(self, selectors: Dict[str, str], fallback_manual: bool = True) -> bool:
        """
        Executes the login workflow. Falls back to terminal-prompted manual login if automated login fails.
        """
        logger.info("Initiating login sequence...")
        
        try:
            # 1. Fill Username
            username_selector = selectors["username"]
            logger.info(f"Waiting for username field: {username_selector}")
            self.page.locator(username_selector).first.wait_for(state="visible", timeout=8000)
            self.page.locator(username_selector).first.fill(self.username)
            logger.info("Username field filled.")

            # 2. Fill Password
            password_selector = selectors["password"]
            logger.info(f"Waiting for password field: {password_selector}")
            self.page.locator(password_selector).first.wait_for(state="visible", timeout=8000)
            self.page.locator(password_selector).first.fill(self.password)
            logger.info("Password field filled.")

            # 3. Click Login Submit Button
            login_btn_selector = selectors["login_button"]
            logger.info(f"Clicking login submit button: {login_btn_selector}")
            self.page.locator(login_btn_selector).first.wait_for(state="visible", timeout=8000)
            self.page.locator(login_btn_selector).first.click()
            
            # Wait for network idle state to let redirection occur
            self.page.wait_for_load_state("networkidle", timeout=10000)
            logger.info("Login form submitted successfully.")
            return True

        except Exception as error:
            logger.error(f"Automated login flow failed: {str(error)}")
            
            if fallback_manual and not HEADLESS:
                logger.warning("Headed mode detected. Falling back to MANUAL login...")
                print("\n" + "=" * 70)
                print(" !!!  AUTOMATED LOGIN BARRIER / CAPTCHA DETECTED  !!!")
                print(" Please log in manually inside the opened browser window.")
                print(" Once you are successfully logged in, return here and press [ENTER].")
                print("=" * 70 + "\n")
                
                # Pauses script execution until the user manually authenticates and hits enter
                input("Press [ENTER] to continue after manual authentication...")
                logger.info("Manual authentication override accepted.")
                return True
            else:
                logger.critical("Manual login fallback unavailable in headless execution mode.")
                raise Exception(
                    "Authentication failure. Automated login failed and manual fallback is disabled in headless mode."
                )