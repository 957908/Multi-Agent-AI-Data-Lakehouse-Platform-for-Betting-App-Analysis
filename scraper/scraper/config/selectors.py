# ============================================================
# File Name:
#     selectors.py
#
# Module:
#     Configuration
#
# Purpose:
#     Store CSS selectors for every supported website.
#
# Why?
#     Website selectors change frequently.
#     Keeping them in one place makes maintenance easier.
#
# Used By:
#     LoginManager
#     NavigationManager
#     PaymentDiscovery
# ============================================================


ONEXBET = {

    # --------------------------------------------------------
    # Login
    # --------------------------------------------------------

    "username": "#username",

    "password": "#username-password",

    "login_button": "button[type='submit']",

    # --------------------------------------------------------
    # Navigation
    # --------------------------------------------------------

    "deposit_button": "",

    # --------------------------------------------------------
    # Payment
    # --------------------------------------------------------

    "payment_container": "",

    "upi": "",

    "bank": "",

    "crypto": ""
}
ONEXBET = {
    "login_popup_button": "button.auth-dropdown-trigger",

    "username": "#username",

    "password": "#username-password",

    "login_button": "button[type='submit']",
}