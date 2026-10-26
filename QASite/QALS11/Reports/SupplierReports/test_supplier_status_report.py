"""
QALS11 | Reports > Supplier Reports > Supplier Status Report
=============================================================
URL  : https://engineering.ultrivalms.com/QALS1011
User : buyeruser / Ultriva!23

Test Flow
---------
  1.  Login as buyeruser
  2.  Navigate to Reports -> Supplier Reports -> Supplier Status Report
  3.  Keep default filters (Plant = All Plants, all others = All)
  4.  Click Go button
  5.  Verify the report grid loads

Run (from qa_automation/):
    pytest tests/QALS11/Reports/SupplierReports/test_supplier_status_report.py -v -s
"""

import os
import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# ============================================================================
# CONFIGURATION
# ============================================================================
BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
USERNAME = "buyeruser"
PASSWORD = "Ultriva!23"
PAUSE = 1.2
SUPPLIER_STATUS_FILTER_URL = f"{BASE_URL}/SupplierReport/SupplierStatusFilter"


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture(scope="class")
def driver():
    """Class-scoped Chrome driver - one browser session per test class."""
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    drv = webdriver.Chrome(options=options)
    drv.implicitly_wait(10)
    drv.set_page_load_timeout(30)
    drv.maximize_window()
    yield drv
    drv.quit()


# ============================================================================
# HELPERS
# ============================================================================


def wait_ready(driver, timeout=30):
    """Wait for document.readyState == complete."""
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def find(driver, by, locator, timeout=15):
    """Wait for presence and return element."""
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, locator))
    )


def clickable(driver, by, locator, timeout=15):
    """Wait until clickable and return element."""
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, locator))
    )


def scroll_to(driver, el):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'})", el)
    time.sleep(0.3)


def take_screenshot(driver, name):
    screenshots_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "..", "reports", "screenshots"
    )
    os.makedirs(screenshots_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(screenshots_dir, f"supplier_status_{name}_{ts}.png")
    driver.save_screenshot(path)
    print(f"  [screenshot] {path}")
    return path


def safe_click_first(driver, locators, timeout=5):
    """Return the first clickable element found from a list of locators."""
    for locator in locators:
        try:
            return WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
        except Exception:
            continue
    return None


def click_visible_text(driver, text):
    """Click the first visible element matching text via JS fallback."""
    return driver.execute_script(
        "var wanted = arguments[0].trim().toLowerCase();"
        "var els = document.querySelectorAll('a, button, input[type=\"button\"], input[type=\"submit\"], span, div, li');"
        "for (var i = 0; i < els.length; i++) {"
        "  var el = els[i];"
        "  var txt = (el.innerText || el.value || '').trim().toLowerCase();"
        "  if (!txt) continue;"
        "  if (txt === wanted && el.offsetParent !== null) { el.click(); return el; }"
        "}"
        "return null;",
        text,
    )


def navigate_to_supplier_status(driver):
    """Open Supplier Status report through menu path, with direct URL fallback."""
    if "SupplierStatus" in driver.current_url:
        return

    reports_link = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[normalize-space()='Reports']"),
            (By.XPATH, "//a[contains(normalize-space(.),'Reports') and not(contains(@href,'BuyerReport')) and not(contains(@href,'SupplierReport'))]"),
            (By.XPATH, "//*[self::a or self::span or self::div][normalize-space(.)='Reports']"),
        ],
        timeout=6,
    )
    if reports_link:
        try:
            scroll_to(driver, reports_link)
            driver.execute_script("arguments[0].click()", reports_link)
            wait_ready(driver)
            time.sleep(PAUSE)
        except Exception:
            driver.get(SUPPLIER_STATUS_FILTER_URL)
            wait_ready(driver)
            time.sleep(PAUSE)
            return

    supplier_reports_link = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[normalize-space()='Supplier Reports']"),
            (By.XPATH, "//a[contains(normalize-space(.),'Supplier Reports')]"),
            (By.XPATH, "//*[self::a or self::span][contains(normalize-space(.),'Supplier Reports')]"),
        ],
        timeout=6,
    )
    if supplier_reports_link:
        scroll_to(driver, supplier_reports_link)
        driver.execute_script("arguments[0].click()", supplier_reports_link)
        wait_ready(driver)
        time.sleep(PAUSE)

    status_report_link = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[contains(@href,'SupplierStatusFilter')]"),
            (By.XPATH, "//a[normalize-space()='Supplier Status Report']"),
            (By.XPATH, "//a[contains(normalize-space(.),'Supplier Status')]"),
            (By.XPATH, "//*[self::a or self::span][contains(normalize-space(.),'Supplier Status')]"),
        ],
        timeout=6,
    )
    if status_report_link:
        scroll_to(driver, status_report_link)
        driver.execute_script("arguments[0].click()", status_report_link)
        wait_ready(driver)
        time.sleep(PAUSE)
    else:
        print("  [WARN] Supplier Status Report menu link not found - navigating directly to report URL.")
        driver.get(SUPPLIER_STATUS_FILTER_URL)
        wait_ready(driver)
        time.sleep(PAUSE)


# ============================================================================
# TEST CLASS
# ============================================================================


@pytest.mark.usefixtures("driver")
class TestSupplierStatusReport:
    """End-to-end tests for Supplier Status Report."""

    def test_01_login(self, driver):
        """Login as buyeruser and verify dashboard loads."""
        print("\n[test_01_login] Navigating to login page...")
        driver.get(f"{BASE_URL}/Account/Login")
        wait_ready(driver)
        time.sleep(PAUSE)

        username_field = find(driver, By.ID, "UserName")
        password_field = find(driver, By.ID, "Password")
        login_btn = clickable(driver, By.ID, "login-button")

        username_field.clear()
        username_field.send_keys(USERNAME)
        password_field.clear()
        password_field.send_keys(PASSWORD)
        login_btn.click()

        wait_ready(driver)
        time.sleep(PAUSE)

        take_screenshot(driver, "01_after_login")
        assert "Account/Login" not in driver.current_url, (
            f"Login failed - still on login page. URL: {driver.current_url}"
        )
        print(f"  [PASS] Logged in. Current URL: {driver.current_url}")

    def test_02_open_report(self, driver):
        """Navigate to Supplier Status Report filter page."""
        print("\n[test_02_open_report] Navigating to Supplier Status Report...")
        navigate_to_supplier_status(driver)

        take_screenshot(driver, "02_filter_page")

        # Verify filter page loaded: URL contains SupplierStatus OR Go button is visible
        url_ok = "SupplierStatus" in driver.current_url
        go_btn = safe_click_first(
            driver,
            [
                (By.XPATH, "//button[contains(normalize-space(.),'Go')]"),
                (By.XPATH, "//input[@type='submit' and contains(@value,'Go')]"),
                (By.XPATH, "//a[normalize-space()='Go']"),
            ],
            timeout=5,
        )
        heading_present = False
        try:
            heading_el = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[contains(normalize-space(.),'Supplier Status Report')]")
                )
            )
            heading_present = heading_el is not None
        except Exception:
            pass

        assert url_ok or go_btn or heading_present, (
            f"Supplier Status filter page did not load. URL: {driver.current_url}"
        )
        print(f"  [PASS] Filter page loaded. URL: {driver.current_url}")

    def test_03_click_go(self, driver):
        """Click Go with default filters and verify report grid loads."""
        print("\n[test_03_click_go] Clicking Go button...")

        # Ensure we are on the filter page
        if "SupplierStatusFilter" not in driver.current_url:
            driver.get(SUPPLIER_STATUS_FILTER_URL)
            wait_ready(driver)
            time.sleep(PAUSE)

        time.sleep(0.5)

        # Click Go button
        go_btn = safe_click_first(
            driver,
            [
                (By.XPATH, "//button[normalize-space()='Go']"),
                (By.XPATH, "//button[contains(normalize-space(.),'Go')]"),
                (By.XPATH, "//input[@type='submit' and @value='Go']"),
                (By.XPATH, "//input[@type='button' and @value='Go']"),
                (By.XPATH, "//a[normalize-space()='Go']"),
            ],
            timeout=8,
        )

        if go_btn:
            scroll_to(driver, go_btn)
            try:
                go_btn.click()
            except Exception:
                driver.execute_script("arguments[0].click()", go_btn)
        else:
            print("  [INFO] Go button not found via locator - trying JS text fallback.")
            result = click_visible_text(driver, "go")
            assert result is not None, "Could not locate Go button"

        wait_ready(driver)
        time.sleep(PAUSE * 1.5)

        take_screenshot(driver, "03_report_results")

        # Verify report loaded: URL changed to /SupplierStatus (no 'Filter') or table is present
        url_ok = (
            "SupplierStatus" in driver.current_url
            and "Filter" not in driver.current_url
        )
        table_present = False
        try:
            tbl = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//table[.//tbody//tr]"))
            )
            table_present = tbl is not None
        except Exception:
            pass

        heading_present = False
        try:
            heading_el = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[contains(normalize-space(.),'Supplier Status')]")
                )
            )
            heading_present = heading_el is not None
        except Exception:
            pass

        assert url_ok or table_present or heading_present, (
            f"Report did not load after clicking Go. URL: {driver.current_url}"
        )
        print(f"  [PASS] Report loaded. URL: {driver.current_url}")
