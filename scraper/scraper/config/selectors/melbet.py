"""
File: melbet.py
Purpose:
    Define CSS/XPath selectors specifically for Melbet.
    Enhanced with CSS selector fallback chains (comma-separated OR rules) for high resilience.
Author: R. Rayri Sharma
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform for Betting Site Intelligence
Created By: R. Rayri Sharma
Reviewed By: Tech Lead & Solution Architect (HQ Chat)
Version: 1.1
"""

SELECTORS = {
    # Login Modal Selectors
    "login_popup_button": "a.login-btn, button.login, .login-trigger, a.login-btn",
    "username": "input[name='username'], input[type='text'][placeholder*='ID'], input[type='text']",
    "password": "input[name='password'], input[type='password']",
    "login_button": "button.submit-login, button.login-btn",
    
    # Navigation Selectors
    "deposit_button": "a.deposit, button.deposit-btn, .deposit-btn, a.deposit-link",
    
    # Discovery Selection Grid
    "payment_container": ".payment-container, .deposit-methods-list, .deposit-page, .payment-grid, .deposit__content",
    "payment_item": ".payment-item, .deposit-method-box, .method-item, div.payment-item, .deposit-page__method",
    "payment_title": ".payment-title, .method-title, .payment-name, h3.title, .deposit-method-title",
    
    # Dynamic Field Popup Extraction Selectors
    "upi_id_field": ".upi-field, .payee-upi, .upi-val, .upi-address",
    "bank_account_field": ".bank-field, .account-number, .bank-num, .account-no, .payee-acc",
    "ifsc_code_field": ".ifsc-field, .ifsc, .ifsc-val, .ifsc-code, .payee-ifsc"
}
