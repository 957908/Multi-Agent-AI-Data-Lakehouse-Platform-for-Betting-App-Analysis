"""
File: base.py
Purpose:
    Define common selector interface expectations for all adapters.
Author: R. Rayri Sharma
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform for Betting Site Intelligence
Created By: R. Rayri Sharma
Reviewed By: Tech Lead & Solution Architect (HQ Chat)
Version: 1.0
"""

# Dict template representing expected keys for any site selector config.
REQUIRED_SELECTOR_KEYS = [
    "login_popup_button",
    "username",
    "password",
    "login_button",
    "deposit_button",
    "payment_container",
    "payment_item",
    "payment_title",
    "upi_id_field",
    "bank_account_field",
    "ifsc_code_field",
]
