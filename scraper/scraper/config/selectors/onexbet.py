"""
File: onexbet.py
Purpose:
    Define CSS/XPath selectors specifically for 1xBet based on production dump.
    Enhanced with CSS selector fallback chains (comma-separated OR rules) for high resilience.
Author: R. Rayri Sharma
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform for Betting Site Intelligence
Created By: R. Rayri Sharma
Reviewed By: Tech Lead & Solution Architect (HQ Chat)
Version: 1.2
"""

SELECTORS = {
    # Login Modal Selectors
    "login_popup_button": "button.auth-dropdown-trigger, a.login-btn, button.login, .login-trigger",
    "username": "#username, input[name='username'], input[type='text'][placeholder*='ID'], input[type='text']",
    "password": "#username-password, input[name='password'], input[type='password']",
    "login_button": "button[type='submit'], button.submit-login, button.login-btn",
    
    # Navigation Selectors
    "deposit_button": "a.deposit-button, button.deposit-btn, .deposit, a.deposit, a.deposit-link",
    
    # Discovery Selection Grid (updated from production script)
    "payment_container": ".deposit-page, .deposit-page__main, .deposit__content, .payment-container, .deposit-methods-list, .payment-grid",
    "payment_item": "button.payment-method.payment-list-methods__button, button.payment-list-methods__button, .payment-item, .deposit-method-box, .method-item, div.payment-item, .deposit-page__method",
    "payment_title": ".payment-method__name, .payment-title, .method-title, .payment-name, h3.title, .deposit-method-title",
    
    # Dynamic Field Popup Extraction Selectors
    "upi_id_field": ".upi-id, .payee-upi, .upi-field, .upi-val, .upi-address",
    "bank_account_field": ".bank-account, .account-number, .bank-field, .bank-num, .account-no, .payee-acc",
    "ifsc_code_field": ".ifsc-code, .ifsc, .ifsc-field, .ifsc-val, .payee-ifsc"
}
