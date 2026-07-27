"""
File: settings.py
Purpose:
    Central configuration manager for the entire project.
Author: R. Rayri Sharma
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform for Betting Site Intelligence
Created By: R. Rayri Sharma
Reviewed By: Tech Lead & Solution Architect (HQ Chat)
Version: 1.1
"""

# Standard Library
import os
from pathlib import Path

# Third Party
from dotenv import load_dotenv

# ============================================================
# Constants
# ============================================================
DEFAULT_TIMEOUT_MS = 30000  # Default timeout in milliseconds for Playwright
DEFAULT_RETRIES = 3         # Default retry count for network operations

# ============================================================
# Load Environment Variables
# ============================================================
# Load configurations from .env at the root of the workspace
env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(dotenv_path=env_path)

# ============================================================
# Credentials
# ============================================================
USERNAME = os.getenv("USERNAME", "")
PASSWORD = os.getenv("PASSWORD", "")

# ============================================================
# Website URLs
# ============================================================
ONEXBET_URL = os.getenv("ONEXBET_URL", "")
MELBET_URL = os.getenv("MELBET_URL", "")
TENCRIC_URL = os.getenv("TENCRIC_URL", "")
PLAY22_URL = os.getenv("PLAY22_URL", "")

# ============================================================
# Browser Configuration
# ============================================================
HEADLESS = os.getenv("HEADLESS", "False").lower() == "true"
WAIT_TIMEOUT = int(os.getenv("WAIT_TIMEOUT", 20))  # in seconds

# Anti-detection & Evasion Defaults
USER_AGENT = os.getenv(
    "USER_AGENT",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
VIEWPORT_WIDTH = int(os.getenv("VIEWPORT_WIDTH", 1920))
VIEWPORT_HEIGHT = int(os.getenv("VIEWPORT_HEIGHT", 1080))
LOCALE = os.getenv("LOCALE", "en-US")
TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")

# ============================================================
# Output and Telemetry Settings
# ============================================================
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
SCREENSHOT = os.getenv("SCREENSHOT", "True").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")