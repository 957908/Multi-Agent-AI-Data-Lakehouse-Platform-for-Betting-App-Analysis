"""
File: session.py
Purpose:
    Session state manager for authentication persistence.
    Enhanced with cookie expiration checks and audit logging.
Author: R. Rayri Sharma
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform for Betting Site Intelligence
Created By: R. Rayri Sharma
Reviewed By: Tech Lead & Solution Architect (HQ Chat)
Version: 2.0
"""

# Standard Library
import logging
from pathlib import Path
import time

# Third Party
from playwright.sync_api import BrowserContext, Page

# Setup Logger
logger = logging.getLogger("scraper.core.session")


class SessionManager:
    """
    Manages loading, saving, validation, and cookie expiration audits of persistent storage states.
    """

    def __init__(self, session_dir: str = "auth") -> None:
        """
        Initializes the session manager and ensures the authentication directory exists.
        """
        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(exist_ok=True)
        logger.info(f"Initialized SessionManager with directory: {self.session_dir.resolve()}")

    def get_state_path(self, site_name: str) -> str:
        """
        Returns the standard file path for a site's storage state.
        """
        return str(self.session_dir / f"{site_name}_state.json")

    def has_session(self, site_name: str) -> bool:
        """
        Checks if a saved storage state file exists for the site.
        """
        state_file = self.session_dir / f"{site_name}_state.json"
        exists = state_file.exists() and state_file.stat().st_size > 0
        logger.info(f"Session check for {site_name}: exists={exists}")
        return exists

    def save_session(self, context: BrowserContext, site_name: str) -> str:
        """
        Exports cookies and localStorage data from the active context to disk.
        """
        state_path = self.get_state_path(site_name)
        logger.info(f"Saving browser context storage state to: {state_path}")
        try:
            context.storage_state(path=state_path)
            logger.info("[Session Audit] New login performed and session state saved successfully.")
            return state_path
        except Exception as error:
            logger.error(f"Failed to save storage state: {str(error)}")
            raise

    def clear_session(self, site_name: str) -> None:
        """
        Removes a stored session state from disk.
        """
        state_path = self.session_dir / f"{site_name}_state.json"
        if state_path.exists():
            logger.info(f"[Session Audit] Session expired/invalid. Clearing storage state for: {site_name}")
            try:
                state_path.unlink()
                logger.info("Session state file deleted successfully.")
            except Exception as error:
                logger.error(f"Failed to delete session state file: {str(error)}")

    def verify_session(self, page: Page, verification_selector: str, timeout_ms: int = 5000) -> bool:
        """
        Checks if the active page shows logged-in indicators.
        Returns True if authenticated, False otherwise.
        """
        logger.info(f"Verifying session using selector '{verification_selector}' (timeout={timeout_ms}ms)...")
        try:
            page.wait_for_selector(verification_selector, timeout=timeout_ms, state="visible")
            logger.info("[Session Audit] Session verified: Logged-in indicator element detected.")
            return True
        except Exception:
            logger.warning("[Session Audit] Session verification failed: Logged-in indicator not found.")
            return False

    def verify_session_cookies(self, context: BrowserContext) -> bool:
        """
        Inspects stored cookies inside the active context and checks their expiration timestamps.
        """
        try:
            cookies = context.cookies()
            if not cookies:
                logger.warning("[Session Audit] No cookies found in active browser context. Cookie validation: FAILED.")
                return False
                
            current_time = time.time()
            expired_cookies_count = 0
            
            for cookie in cookies:
                expires = cookie.get("expires")
                if expires is not None:
                    # 'expires' is a float/int epoch timestamp
                    if expires < current_time:
                        expired_cookies_count += 1
                        
            logger.info(
                f"[Session Audit] Cookie validation result: Total Cookies={len(cookies)}, "
                f"Expired={expired_cookies_count}."
            )
            
            if expired_cookies_count == len(cookies) and len(cookies) > 0:
                logger.warning("[Session Audit] All session cookies have expired.")
                return False
                
            return True
        except Exception as error:
            logger.error(f"[Session Audit] Failed to validate context cookies: {str(error)}")
            return False
