"""
File: adapter.py
Purpose:
    Concrete adapter implementing data acquisition lifecycle for 22XBet.
    Enhanced with cookie validation, verify audit logging, and session recovery.
Author: R. Niraj Kadam
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform for Betting Site Intelligence
Created By: R. Niraj Kadam
Reviewed By: Tech Lead & Solution Architect (HQ Chat)
Version: 2.0
"""

# Standard Library
import logging
from typing import List

# Local Imports
from adapters.base_adapter import BaseAdapter
from models.payment import PaymentRecord
from core.login import LoginManager
from core.navigation import NavigationManager
from core.payment_discovery import PaymentDiscovery
from core.session import SessionManager

# Setup Logger
logger = logging.getLogger("scraper.adapters.twentytwoxbet.adapter")


class TwentyTwoXBetAdapter(BaseAdapter):
    """
    Adapter implementing 22XBet navigation flows and payment discoveries.
    """

    def login_if_required(self) -> None:
        """
        Loads saved state if valid, else triggers automated/manual authentication.
        """
        session_mgr = SessionManager()
        has_state = session_mgr.has_session(self.site_name)
        
        if has_state:
            # Audit stored cookies expiration
            cookies_valid = session_mgr.verify_session_cookies(self.context)
            if not cookies_valid:
                logger.warning("[Session Audit] Stored session cookies failed verification audit.")
                session_mgr.clear_session(self.site_name)
                has_state = False
                
        login_popup_sel = self.selectors.get("login_popup_button", "")
        self.page.wait_for_timeout(2000)
        
        # Verify authenticated state indicator
        is_popup_trigger_visible = self.page.locator(login_popup_sel).is_visible() if login_popup_sel else True
        
        if not is_popup_trigger_visible and has_state:
            logger.info("[Session Audit] Session reused successfully (authenticated state verified).")
            return
            
        if has_state:
            logger.warning("[Session Audit] Session expired. Page requires re-authentication.")
            session_mgr.clear_session(self.site_name)
        else:
            logger.info("[Session Audit] No session state found. New login required.")

        logger.info("Triggering automated login sequence...")
        nav_mgr = NavigationManager(self.page)
        login_mgr = LoginManager(self.page)
        
        nav_mgr.open_login_popup(self.selectors)
        self.capture_evidence("login_modal")
        
        login_mgr.login(self.selectors)
        self.capture_evidence("login_success")
        
        session_mgr.save_session(self.context, self.site_name)

    def navigate_to_deposit(self) -> None:
        """
        Clicks deposit buttons to navigate to recharge sections.
        """
        logger.info("Navigating to 22XBet deposit panel...")
        nav_mgr = NavigationManager(self.page)
        try:
            nav_mgr.navigate_to_deposit(self.selectors)
            self.capture_evidence("deposit_portal")
        except Exception as error:
            logger.warning(f"Interactive deposit navigation failed: {str(error)}. Loading fallback URL.")
            deposit_url = f"{self.base_url}/office/recharge/"
            nav_mgr.navigate_to_url(deposit_url)
            self.capture_evidence("deposit_portal_fallback")

    def discover_payment_methods(self) -> List[PaymentRecord]:
        """
        Delegates scan loops to the PaymentDiscovery module and populates model records.
        """
        logger.info("Discovering payment methods...")
        self.wait_for_payment_page()
        
        # Save reference on instance to allow performance tracking
        self.discovery = PaymentDiscovery(self.page)
        raw_items = self.discovery.discover_methods(self.selectors, self.site_name)
        
        self.records = [PaymentRecord(**item) for item in raw_items]
        logger.info(f"Discovered and instantiated {len(self.records)} PaymentRecord models.")
        return self.records

    def extract_payment_details(self) -> List[PaymentRecord]:
        """
        Included inside discover_payment_methods template actions to prevent duplication.
        Returns the populated records list.
        """
        logger.info("Payment details extraction sequence completed during discovery click-through loops.")
        return self.records
