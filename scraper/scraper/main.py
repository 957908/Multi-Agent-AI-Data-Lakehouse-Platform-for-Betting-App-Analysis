"""
File: main.py
Purpose:
    - Launch Chromium browser
    - Open target website
    - Allow manual login
    - Save authenticated session
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright


# -------------------------------------------------------------------
# Load Environment Variables
# -------------------------------------------------------------------

load_dotenv()

TARGET_URL = os.getenv("ONEXBET_URL")

if not TARGET_URL:
    raise ValueError("ONEXBET_URL is missing in .env file")


# -------------------------------------------------------------------
# Create Required Directories
# -------------------------------------------------------------------

Path("auth").mkdir(exist_ok=True)
Path("logs").mkdir(exist_ok=True)
Path("output").mkdir(exist_ok=True)


# -------------------------------------------------------------------
# Main Function
# -------------------------------------------------------------------

def main():

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False,
            slow_mo=300
        )

        context = browser.new_context()

        page = context.new_page()

        print(f"\nOpening: {TARGET_URL}")

        page.goto(TARGET_URL)

        input("\nLogin manually and press ENTER...")

        context.storage_state(path="auth/storage_state.json")

        print("\n✅ Session saved successfully.")

        browser.close()


# -------------------------------------------------------------------
# Entry Point
# -------------------------------------------------------------------

if __name__ == "__main__":
    main()