# ============================================================
# File Name : navigation.py
#
# Purpose:
#     Open login popup only if it is not already open.
# ============================================================

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class NavigationManager:

    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    def open_login_popup(self):

        print("=" * 60)
        print("Checking Login Popup...")
        print("=" * 60)

        # -------------------------------------------------
        # Case 1 : Popup already open
        # -------------------------------------------------
        username_fields = self.driver.find_elements(By.ID, "username")

        visible = [e for e in username_fields if e.is_displayed()]

        if visible:
            print("✅ Login popup is already open.")
            return

        print("Login popup is not open.")

        # -------------------------------------------------
        # Case 2 : Click Log In button
        # -------------------------------------------------
        login_buttons = self.driver.find_elements(By.TAG_NAME, "button")

        for btn in login_buttons:

            try:
                if btn.text.strip().lower() == "log in":

                    print("Found Login button.")

                    self.driver.execute_script(
                        "arguments[0].click();",
                        btn
                    )

                    self.wait.until(
                        EC.visibility_of_element_located(
                            (By.ID, "username")
                        )
                    )

                    print("✅ Login popup opened.")

                    return

            except Exception:
                continue

        raise Exception("Could not find Log In button.")