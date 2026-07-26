"""
File: twentytwoxbet.py
Purpose:
    Define CSS/XPath selectors specifically for 22XBet.
    Enhanced with CSS selector fallback chains (comma-separated OR rules) for high resilience.
Author: R. Rayri Sharma
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform for Betting Site Intelligence
Created By: R. Rayri Sharma
Reviewed By: Tech Lead & Solution Architect (HQ Chat)
Version: 1.1
"""

SELECTORS = {
    "login_popup_button": "button.auth-modal-open, a.login-btn, .login-btn",
    "username": "input[type='text'][placeholder*='ID'], input[type='text'], input[name='username']",
    "password": "input[type='password']",
    "login_button": "button.auth-submit, button.login-btn",
    "deposit_button": "a.deposit-btn, button.deposit-btn, .deposit-btn, a.deposit",
    "payment_container": ".payments-list, .deposit-page, .payment-grid, .deposit__content",
    "payment_item": ".payment-option, .method-item, div.payment-item, .deposit-page__method",
    "payment_title": ".payment-option-name, .payment-name, h3.title, .deposit-method-title",
    "upi_id_field": ".upi-address, .upi-val, .payee-upi",
    "bank_account_field": ".account-no, .bank-num, .account-number, .payee-acc",
    "ifsc_code_field": ".ifsc-no, .ifsc-val, .ifsc-code, .payee-ifsc"
}
