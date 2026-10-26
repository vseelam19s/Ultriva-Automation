"""
Global configuration for QA automation tests.
"""

import os

# Base URL and paths for the application
BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
LOGIN_URL = f"{BASE_URL}/Account/Login"

# Default login credentials
USERNAME = "buyeruser"
PASSWORD = os.getenv("ULTRIVA_PASSWORD", "Ultriva!23")

# Browser configuration
BROWSER = "chrome"
HEADLESS = False
IMPLICIT_WAIT = 10
EXPLICIT_WAIT = 15
PAGE_LOAD_TIMEOUT = 30

# TestRail configuration
TESTRAIL_ENABLED = True
TESTRAIL_URL = "https://upland.testrail.com/"
TESTRAIL_EMAIL = os.getenv("TESTRAIL_EMAIL", "vseelam@uplandsoftware.com")
TESTRAIL_API_KEY = os.getenv("TESTRAIL_API_KEY", "")
TESTRAIL_PROJECT_ID = 15
TESTRAIL_SUITE_ID = 7352
TESTRAIL_RUN_ID = None
TESTRAIL_AUTO_CREATE_RUN = True
TESTRAIL_RUN_NAME = "QA Automation Run"

# Report settings
REPORT_DIR = "reports"
SCREENSHOT_DIR = os.path.join(REPORT_DIR, "screenshots")
EXCEL_REPORT_PATH = os.path.join(REPORT_DIR, "test_results.xlsx")
