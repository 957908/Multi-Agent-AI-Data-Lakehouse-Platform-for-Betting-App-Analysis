"""
File: tencric.py
Purpose:
    Define CSS/XPath selectors specifically for 10Cric.
    Enhanced with CSS selector fallback chains (comma-separated OR rules) for high resilience.
Author: R. Niraj Kadam
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform for Betting Site Intelligence
Created By: R. Niraj Kadam
Reviewed By: Tech Lead & Solution Architect (HQ Chat)
Version: 1.1
"""

SELECTORS = {
    "login_popup_button": "button.login-trigger, a.login-btn, .login-trigger",
    "username": "#login_username, input[type='text'][placeholder*='Username'], input[name='username']",
    "password": "#login_password, input[type='password']",
    "login_button": "button.login-submit, button.login-btn",
    "deposit_button": "a.deposit-link, button.deposit-btn, .deposit-btn, a.deposit",
    "payment_container": ".deposit-methods-list, .deposit-page, .payment-grid, .deposit__content",
    "payment_item": ".deposit-method-box, .method-item, div.payment-item, .deposit-page__method",
    "payment_title": ".method-title, .payment-name, h3.title, .deposit-method-title",
    "upi_id_field": ".upi-val, .upi-address, .payee-upi",
    "bank_account_field": ".bank-num, .account-number, .payee-acc",
    "ifsc_code_field": ".ifsc-val, .ifsc-code, .payee-ifsc"
}
