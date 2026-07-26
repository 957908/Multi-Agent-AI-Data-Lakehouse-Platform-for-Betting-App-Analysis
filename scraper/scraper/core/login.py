# ============================================================
# File Name : login.py
#
# Module    : Core
#
# Purpose:
#     Automatically login into supported betting websites.
#
# Responsibilities:
#     1. Find visible username field
#     2. Find visible password field
#     3. Enter credentials
#     4. Click Login
#
# ============================================================

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from config.settings import USERNAME, PASSWORD
from config.selectors import ONEXBET


class LoginManager:

    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    # ---------------------------------------------------------
    # Find only the visible element
    # ---------------------------------------------------------
    def find_visible_element(self, selector):

        self.wait.until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, selector)
            )
        )

        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)

        print(f"\nSearching visible element: {selector}")
        print(f"Found {len(elements)} matching element(s)")

        for i, element in enumerate(elements):
            print(
                f"Element {i+1}: displayed={element.is_displayed()}"
            )

            if element.is_displayed():
                return element

        raise TimeoutException(
            f"No visible element found for selector: {selector}"
        )

    # ---------------------------------------------------------
    # Login
    # ---------------------------------------------------------
    def login(self):

        print("=" * 60)
        print("STARTING LOGIN")
        print("=" * 60)

        # ---------------- Username ----------------
        print("Entering Username...")

        username = self.find_visible_element(
            ONEXBET["username"]
        )

        username.clear()
        username.send_keys(USERNAME)

        print("Username entered.")

        # ---------------- Password ----------------
        print("Entering Password...")

        password = self.find_visible_element(
            ONEXBET["password"]
        )

        password.clear()
        password.send_keys(PASSWORD)

        print("Password entered.")

        # ---------------- Login Button ----------------
        print("Clicking Login Button...")

        login_button = self.find_visible_element(
            ONEXBET["login_button"]
        )

        login_button.click()

        print("Login submitted.")

        return True