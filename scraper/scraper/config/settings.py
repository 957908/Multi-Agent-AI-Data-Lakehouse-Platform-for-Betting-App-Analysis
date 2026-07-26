# ============================================================
# File : settings.py
#
# Purpose:
#     Central configuration manager for the entire project.
#
# Why:
#     Instead of hardcoding credentials and URLs,
#     we load everything from the .env file.
#
# Used By:
#     BrowserManager
#     LoginManager
#     PaymentDiscovery
#     Exporters
# ============================================================

import os
from dotenv import load_dotenv

# ------------------------------------------------------------
# Load .env file
# ------------------------------------------------------------

load_dotenv()

# ------------------------------------------------------------
# Credentials
# ------------------------------------------------------------

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

# ------------------------------------------------------------
# Website URLs
# ------------------------------------------------------------

ONEXBET_URL = os.getenv("ONEXBET_URL")
MELBET_URL = os.getenv("MELBET_URL")
TENCRIC_URL = os.getenv("TENCRIC_URL")
PLAY22_URL = os.getenv("PLAY22_URL")

# ------------------------------------------------------------
# Browser Configuration
# ------------------------------------------------------------

HEADLESS = os.getenv("HEADLESS", "False").lower() == "true"

WAIT_TIMEOUT = int(
    os.getenv("WAIT_TIMEOUT", 20)
)

# ------------------------------------------------------------
# Output
# ------------------------------------------------------------

OUTPUT_DIR = os.getenv(
    "OUTPUT_DIR",
    "output"
)