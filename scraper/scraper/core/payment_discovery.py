"""
File: payment_discovery.py
Purpose:
    Discovers payment methods and extracts detailed transaction coordinates (UPI, Bank transfer, limits).
    Enhanced with lazy-load scroll sweeps, unhandled modal dismissals, centralized retries, 
    and availability detection.
Author: R. Rayri Sharma
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform for Betting Site Intelligence
Created By: R. Rayri Sharma
Reviewed By: Tech Lead & Solution Architect (HQ Chat)
Version: 2.0
"""

# Standard Library
from datetime import datetime
import logging
import re
from typing import Dict, Any, List

# Third Party
from playwright.sync_api import Page

# Local Imports
from core.screenshot import take_screenshot
from core.retry_utils import retry_operation

# Setup Logger
logger = logging.getLogger("scraper.core.payment_discovery")


class PaymentDiscovery:
    """
    Handles payment gateway option scanning, modal click-through, and data coordinate extraction.
    """

    def __init__(self, page: Page) -> None:
        """
        Initializes PaymentDiscovery with the target Page.
        """
        self.page = page
        self.popup_dismissals_count = 0
        self.retries_executed_count = 0
        logger.info("Initialized Resilient PaymentDiscovery module.")

    def discover_methods(self, selectors: Dict[str, str], site_name: str, page_type: str = "deposit_page") -> List[Dict[str, Any]]:
        """
        Scans the payment page, iterates over payment options, clicks them, and extracts raw metadata.
        Supports dynamic payment iframes, multi-depth confirmation click loops, new tab popups, and reload resets.
        """
        logger.info(f"Starting payment discovery for: {site_name} (page_type={page_type})")
        payment_records: List[Dict[str, Any]] = []

        container_selector = selectors.get("payment_container", "")
        item_selector = selectors.get("payment_item", "")
        title_selector = selectors.get("payment_title", "")

        if not container_selector or not item_selector:
            logger.error("Missing payment container or item selector in configurations.")
            return []

        # Keep track of initial deposit/withdrawal URL for reloading SPA state
        deposit_url = self.page.url

        try:
            # 1. Resolve Root Target Context (Support Iframes)
            target_root = self._get_target_root(selectors)
            
            # Wait for container loading
            target_root.locator(container_selector).wait_for(state="visible", timeout=15000)

            # 2. Lazy-Load Scroll Sweep
            try:
                container_locator = target_root.locator(container_selector)
                if container_locator.count() > 0:
                    logger.info("Performing lazy-loading scroll sweep on payment container...")
                    # Scroll container to bottom
                    container_locator.first.evaluate("element => element.scrollTop = element.scrollHeight")
                    self.page.wait_for_timeout(1000)
                    # Scroll container back to top
                    container_locator.first.evaluate("element => element.scrollTop = 0")
                    self.page.wait_for_timeout(1000)
            except Exception as scroll_error:
                logger.debug(f"Lazy-loading scroll sweep notice: {str(scroll_error)}")

            # 3. Handle overlay dialog dismissals
            self._dismiss_blocker_popups(target_root)

            # Retrieve option names
            items = target_root.locator(item_selector)
            item_count = items.count()
            logger.info(f"Detected {item_count} payment method items on page.")
            
            method_names = []
            for i in range(item_count):
                try:
                    title_loc = items.nth(i).locator(title_selector)
                    name = title_loc.text_content().strip() if title_loc.count() > 0 else f"Method {i+1}"
                    method_names.append(name)
                except Exception:
                    method_names.append(f"Method {i+1}")

            # Loop through option targets
            for index, payment_name in enumerate(method_names):
                logger.info(f"Processing payment method [{index + 1}/{len(method_names)}]: {payment_name}")

                # Reload/Reset SPA base page between operations to ensure fresh SPA state
                if index > 0:
                    logger.info(f"Reloading SPA base page: {deposit_url}")
                    self.page.goto(deposit_url)
                    self.page.wait_for_load_state("networkidle")
                    target_root = self._get_target_root(selectors)
                    target_root.locator(container_selector).wait_for(state="visible", timeout=15000)
                    self._dismiss_blocker_popups(target_root)

                # Re-locate payment item by title
                item = None
                items = target_root.locator(item_selector)
                for k in range(items.count()):
                    try:
                        title_loc = items.nth(k).locator(title_selector)
                        name_text = title_loc.text_content().strip() if title_loc.count() > 0 else ""
                        if name_text == payment_name:
                            item = items.nth(k)
                            break
                    except Exception:
                        continue

                if not item:
                    logger.warning(f"Payment item '{payment_name}' not found after reload reset. Skipping.")
                    continue

                # Detect availability status dynamically from item text
                item_text = ""
                try:
                    item_text = item.text_content().lower()
                except Exception:
                    pass

                is_active = True
                if any(kw in item_text for kw in ["unavailable", "maintenance", "disabled", "inactive"]):
                    is_active = False
                    logger.warning(f"Payment method '{payment_name}' is flagged as inactive/disabled on site.")

                # Detect currency code dynamically
                currency_code = "INR"  # default base currency fallback
                if "usd" in item_text or "$" in item_text:
                    currency_code = "USD"
                elif "usdt" in item_text:
                    currency_code = "USDT"
                elif "eur" in item_text or "€" in item_text:
                    currency_code = "EUR"

                # Build record conforming to schema v1.1
                record = {
                    "schema_version": "1.1",
                    "scraper_version": "1.0.0",
                    "source_platform": site_name,
                    "extraction_status": "success",
                    "extraction_method": "playwright_sync",
                    "site": site_name,
                    "page_type": page_type,
                    "payment_type": self._infer_payment_type(payment_name),
                    "payment_name": payment_name,
                    "currency": currency_code,
                    "country": "IN",
                    "bonus_name": None,
                    "support_type": "live_chat",
                    "support_value": None,
                    "status": "active" if is_active else "inactive",
                    "source_url": self.page.url,
                    "scraped_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "extracted_data": {}
                }

                # Click item with centralized retry wrappers
                try:
                    logger.info(f"Clicking payment option: {payment_name}")
                    
                    # Expect popup window redirection checks
                    new_page = None
                    
                    def click_and_catch_popup():
                        nonlocal new_page
                        try:
                            with self.page.context.expect_page(timeout=3000) as new_page_info:
                                item.click(timeout=5000)
                            new_page = new_page_info.value
                            logger.info("Detected new redirect window opened by payment option.")
                            new_page.wait_for_load_state("networkidle")
                        except Exception:
                            # Standard inline click
                            item.click(timeout=5000)

                    # Wrap click action in the centralized retry wrapper
                    retry_operation(
                        click_and_catch_popup,
                        retries=3,
                        delay=1.0,
                        exceptions=(Exception,),
                        action_name=f"Click Payment Method: {payment_name}"
                    )

                    active_page = new_page if new_page else self.page
                    active_root = new_page if new_page else target_root

                    # Perform multi-depth gateway confirm button clicks
                    confirm_buttons = active_root.locator(
                        "button:has-text('CONFIRM'), button:has-text('Confirm'), "
                        "button:has-text('CONTINUE'), button:has-text('Continue'), "
                        "button:has-text('PROCEED'), button:has-text('Proceed'), "
                        "button:has-text('OK'), button:has-text('Ok'), "
                        "div.payment_modal_btn"
                    )
                    if confirm_buttons.count() > 0 and confirm_buttons.first.is_visible():
                        logger.info("Found clickable gateway confirmation button. Routing click...")
                        confirm_buttons.first.click()
                        active_page.wait_for_timeout(2000)

                    # Extract coordinates
                    details = self._extract_modal_details(selectors, active_root, active_page)
                    record["extracted_data"] = details

                    # Screenshot evidence
                    safe_name = payment_name.lower().replace(" ", "_")
                    take_screenshot(active_page, f"{site_name}_method_{safe_name}")

                    # Cleanup redirect tab
                    if new_page:
                        new_page.close()
                        logger.info("Closed payment gateway redirect tab successfully.")
                    else:
                        # Close inline overlay modal
                        self.page.keyboard.press("Escape")
                        self.page.wait_for_timeout(500)

                    logger.info(f"Successfully processed details for: {payment_name}")

                except Exception as click_error:
                    logger.error(f"Failed click-through details for payment item '{payment_name}': {str(click_error)}")
                    self.retries_executed_count += 3 # Record execution retries failure count
                    if 'new_page' in locals() and new_page:
                        try:
                            new_page.close()
                        except Exception:
                            pass
                    else:
                        self.page.keyboard.press("Escape")
                    record["extraction_status"] = "partial"

                payment_records.append(record)

        except Exception as error:
            logger.error(f"Fatal error during payment discovery flow: {str(error)}")
            raise

        return payment_records

    def _get_target_root(self, selectors: Dict[str, str]) -> Any:
        """
        Detects if payment methods are nested inside an iframe and returns the search context root.
        """
        target_root = self.page
        iframe_selectors = [
            "iframe[name*='payment']",
            "iframe[id*='payment']",
            "iframe[src*='paysystem']",
            "iframe[src*='deposit']",
            "iframe#payments_frame",
        ]
        
        for selector in iframe_selectors:
            try:
                iframe_locator = self.page.locator(selector)
                if iframe_locator.count() > 0 and iframe_locator.first.is_visible():
                    logger.info(f"Detected active payment iframe: {selector}. Routing inside iframe.")
                    target_root = self.page.frame_locator(selector)
                    break
            except Exception:
                continue
        return target_root

    def _dismiss_blocker_popups(self, target_root: Any) -> None:
        """
        Scans for known dialog close handles or overlay backdrops and auto-clicks them to keep list accessible.
        """
        popup_close_selectors = [
            "button.modal-close",
            ".popup-close",
            ".close-modal",
            "span.close",
            "button.alerts-cancel",
            ".close_modal_btn",
            ".dismiss-overlay"
        ]
        for popup_sel in popup_close_selectors:
            try:
                popup_loc = target_root.locator(popup_sel)
                if popup_loc.count() > 0 and popup_loc.first.is_visible():
                    logger.info(f"Detected overlay blocker popup. Dismissing: {popup_sel}")
                    popup_loc.first.click()
                    self.popup_dismissals_count += 1
                    self.page.wait_for_timeout(500)
            except Exception:
                continue

    def _infer_payment_type(self, name: str) -> str:
        """
        Helper to map payment method titles to target type categories.
        """
        name_lower = name.lower()
        if "upi" in name_lower or "paytm" in name_lower or "phonepe" in name_lower or "gpay" in name_lower:
            return "upi"
        elif "net" in name_lower or "banking" in name_lower:
            return "net_banking"
        elif "bank" in name_lower or "transfer" in name_lower or "imps" in name_lower or "neft" in name_lower:
            return "bank_transfer"
        elif "crypto" in name_lower or "usdt" in name_lower or "btc" in name_lower or "eth" in name_lower or "bitcoin" in name_lower or "ethereum" in name_lower:
            return "cryptocurrency"
        elif "wallet" in name_lower or "skrill" in name_lower or "neteller" in name_lower:
            return "e-wallet"
        return "other"

    def _extract_modal_details(self, selectors: Dict[str, str], target_root: Any, active_page: Page) -> Dict[str, Any]:
        """
        Extracts transaction numbers/IDs/limits.
        Combines strict selector parsing with fallback regex heuristics to ensure high reliability.
        """
        details: Dict[str, Any] = {
            "upi_id": None,
            "bank_account": None,
            "ifsc_code": None,
            "payee_name": None,
            "min_deposit": None,
            "max_deposit": None,
            "limit_info": None,
            "processing_time": "Instant",
            "transaction_fee": "Free"
        }

        # 1. Scrape via configured CSS selectors (including fallbacks)
        upi_id_sels = [selectors.get("upi_id_field"), ".upi-id", ".payee-upi"]
        bank_account_sels = [selectors.get("bank_account_field"), ".bank-account", ".account-number"]
        ifsc_code_sels = [selectors.get("ifsc_code_field"), ".ifsc-code", ".ifsc"]

        for upi_sel in upi_id_sels:
            if upi_sel:
                try:
                    upi_locator = target_root.locator(upi_sel)
                    if upi_locator.count() > 0 and upi_locator.first.is_visible():
                        details["upi_id"] = upi_locator.first.text_content().strip()
                        break
                except Exception:
                    continue

        for bank_sel in bank_account_sels:
            if bank_sel:
                try:
                    bank_locator = target_root.locator(bank_sel)
                    if bank_locator.count() > 0 and bank_locator.first.is_visible():
                        details["bank_account"] = bank_locator.first.text_content().strip()
                        break
                except Exception:
                    continue

        for ifsc_sel in ifsc_code_sels:
            if ifsc_sel:
                try:
                    ifsc_locator = target_root.locator(ifsc_sel)
                    if ifsc_locator.count() > 0 and ifsc_locator.first.is_visible():
                        details["ifsc_code"] = ifsc_locator.first.text_content().strip()
                        break
                except Exception:
                    continue

        # 2. Fallback dynamic regex parsing from visible page text
        try:
            body_text = active_page.locator("body").text_content() or ""
            
            # UPI ID Regex
            if not details["upi_id"]:
                upi_pattern = re.compile(r'[a-zA-Z0-9.\-_]+@[a-zA-Z0-9]+')
                found_upis = upi_pattern.findall(body_text)
                if found_upis:
                    details["upi_id"] = found_upis[0]

            # IFSC Code Regex
            if not details["ifsc_code"]:
                ifsc_pattern = re.compile(r'[A-Z]{4}0[A-Z0-9]{6}')
                ifsc_match = ifsc_pattern.search(body_text)
                if ifsc_match:
                    details["ifsc_code"] = ifsc_match.group(0)

            # Bank Account Number Regex
            if not details["bank_account"]:
                acc_pattern = re.compile(r'\b\d{9,18}\b')
                acc_matches = acc_pattern.findall(body_text)
                for match in acc_matches:
                    if details["ifsc_code"] and match in details["ifsc_code"]:
                        continue
                    details["bank_account"] = match
                    break

            # Crypto Address Regex
            crypto_address_pattern = re.compile(r'\b(0x[a-fA-F0-9]{40}|[13][a-km-zA-HJ-NP-Z1-9]{26,33}|T[A-Za-z1-9]{33})\b')
            crypto_match = crypto_address_pattern.search(body_text)
            if crypto_match:
                details["crypto_address"] = crypto_match.group(0)
                if not details["bank_account"]:
                    details["bank_account"] = crypto_match.group(0)

            # Processing time heuristics
            time_match = re.search(r'(instant|immediate|\d+\s*(?:min|minute|hour|day|working day)s?)', body_text, re.IGNORECASE)
            if time_match:
                details["processing_time"] = time_match.group(0).strip().capitalize()

            # Transaction fee heuristics
            fee_match = re.search(r'(free|0%\s*commission|no\s*(?:fee|charge|commission)|\d+(?:\.\d+)?%\s*(?:fee|charge|commission))', body_text, re.IGNORECASE)
            if fee_match:
                details["transaction_fee"] = fee_match.group(0).strip().capitalize()

            # Extraction of Limits and Payees
            for line in body_text.split("\n"):
                line_clean = line.strip()
                if not details["limit_info"] and any(kw in line_clean.lower() for kw in ["limit", "min", "max"]):
                    details["limit_info"] = line_clean
                    
                    # Try to split limits
                    try:
                        digits = re.findall(r'\b\d+[\d,]*\b', line_clean)
                        if len(digits) >= 2:
                            details["min_deposit"] = digits[0].replace(",", "")
                            details["max_deposit"] = digits[1].replace(",", "")
                        elif len(digits) == 1:
                            details["min_deposit"] = digits[0].replace(",", "")
                    except Exception:
                        pass
                
                if not details["payee_name"] and any(kw in line_clean.lower() for kw in ["beneficiary", "payee", "holder", "account name"]):
                    details["payee_name"] = line_clean.split(":")[-1].strip() if ":" in line_clean else line_clean
        except Exception as err:
            logger.debug(f"Regex page body extraction notice: {str(err)}")

        return details
