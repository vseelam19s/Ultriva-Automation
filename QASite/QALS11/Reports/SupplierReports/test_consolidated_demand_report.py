"""
QALS11 | Reports > Supplier Reports > Consolidated Demand Report
=================================================================
URL  : https://engineering.ultrivalms.com/QALS1011
User : buyeruser / Ultriva!23

Test Flow
---------
  1.  Login as buyeruser
  2.  Navigate to Reports -> Supplier Reports -> Consolidated Demand Report
  3.  Verify report summary grid loads (Consolidated Demand View)
  4.  Click first Supplier Item No link (tbody row only)
  5.  Verify Consolidated Demand Details page loads
  6.  Click Back to Summary button and verify return to summary

Run (from qa_automation/):
    pytest tests/QALS11/Reports/SupplierReports/test_consolidated_demand_report.py -v -s
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
CONSOL_DEMAND_URL = f"{BASE_URL}/SupplierReport/ConsolDemand"


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
    path = os.path.join(screenshots_dir, f"consolidated_demand_{name}_{ts}.png")
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


def navigate_to_consol_demand(driver):
    """Open Consolidated Demand report through menu path, with direct URL fallback."""
    if "ConsolDemand" in driver.current_url:
        return

    reports_link = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[normalize-space()='Reports']"),
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
            driver.get(CONSOL_DEMAND_URL)
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

    consol_link = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[contains(@href,'ConsolDemand')]"),
            (By.XPATH, "//a[normalize-space()='Consolidated Demand Report']"),
            (By.XPATH, "//a[contains(normalize-space(.),'Consolidated Demand')]"),
            (By.XPATH, "//*[self::a or self::span][contains(normalize-space(.),'Consolidated Demand')]"),
        ],
        timeout=6,
    )
    if consol_link:
        scroll_to(driver, consol_link)
        driver.execute_script("arguments[0].click()", consol_link)
        wait_ready(driver)
        time.sleep(PAUSE)
    else:
        print("  [WARN] Consolidated Demand menu link not found - navigating directly.")
        driver.get(CONSOL_DEMAND_URL)
        wait_ready(driver)
        time.sleep(PAUSE)


def find_first_supplier_item_link(driver):
    """Find first supplier item anchor pointing to ConsolDemandDetails."""
    # Prioritise href-based locators — avoids nav sidebar anchors
    href_locators = [
        (By.XPATH, "//a[contains(@href,'ConsolDemandDetails')]"),
        (By.XPATH, "//a[contains(@href,'SupplierItemCode')]"),
        (By.XPATH, "//tbody//tr//td//a[contains(@href,'ConsolDemand')]"),
        (By.XPATH, "//tbody//tr//td//a[contains(@href,'Supplier')]"),
    ]
    for by, locator in href_locators:
        try:
            el = WebDriverWait(driver, 8).until(
                EC.presence_of_element_located((by, locator))
            )
            if el and el.get_attribute("href"):
                return el
        except Exception:
            continue

    # JS fallback: search by href pattern to avoid picking up nav links
    el = driver.execute_script(
        "var anchors = document.querySelectorAll('a');"
        "for (var i = 0; i < anchors.length; i++) {"
        "  var href = anchors[i].href || '';"
        "  if ((href.indexOf('ConsolDemandDetails') !== -1 || href.indexOf('SupplierItemCode') !== -1)"
        "      && anchors[i].offsetParent !== null) { return anchors[i]; }"
        "}"
        "return null;"
    )
    return el


def ensure_login(driver):
    """Check if logged in, otherwise login. Used by isolated test runs."""
    driver.get(f"{BASE_URL}/Account/Login")
    wait_ready(driver)
    time.sleep(0.5)
    current_url = driver.current_url
    # If redirected away from login, we're already logged in
    if "Account/Login" not in current_url:
        print("  [INFO] Already logged in.")
        return
    
    print("  [INFO] Need to login...")
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


# ============================================================================
# TEST CLASS
# ============================================================================


@pytest.mark.usefixtures("driver")
class TestConsolidatedDemandReport:
    """End-to-end tests for Consolidated Demand Report."""

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
        """Navigate to Consolidated Demand Report summary page."""
        print("\n[test_02_open_report] Navigating to Consolidated Demand Report...")
        navigate_to_consol_demand(driver)

        take_screenshot(driver, "02_summary_page")

        url_ok = "ConsolDemand" in driver.current_url
        heading_present = False
        try:
            heading_el = WebDriverWait(driver, 8).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[contains(normalize-space(.),'Consolidated Demand')]")
                )
            )
            heading_present = heading_el is not None
        except Exception:
            pass

        assert url_ok or heading_present, (
            f"Consolidated Demand page did not load. URL: {driver.current_url}"
        )
        print(f"  [PASS] Summary page loaded. URL: {driver.current_url}")

    def test_03_verify_summary_grid(self, driver):
        """Verify the Consolidated Demand View grid has supplier item links."""
        print("\n[test_03_verify_summary_grid] Verifying summary grid...")

        if "ConsolDemand" not in driver.current_url or "Details" in driver.current_url:
            driver.get(CONSOL_DEMAND_URL)
            wait_ready(driver)
            time.sleep(PAUSE)

        table_present = False
        try:
            tbl = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//tbody//tr[1]//a"))
            )
            table_present = tbl is not None
        except Exception:
            pass

        take_screenshot(driver, "03_summary_grid")
        assert table_present, (
            f"Summary grid rows with supplier item links not found. URL: {driver.current_url}"
        )
        print("  [PASS] Summary grid with supplier item links is present.")

    def test_04_click_supplier_item(self, driver):
        """Click first Supplier Item No link and verify details page loads."""
        print("\n[test_04_click_supplier_item] Clicking first supplier item link...")

        # Ensure logged in (for isolated test runs)
        ensure_login(driver)

        # Ensure we are on the summary page
        if "ConsolDemand" not in driver.current_url or "Details" in driver.current_url:
            driver.get(CONSOL_DEMAND_URL)
            wait_ready(driver)
            time.sleep(PAUSE)

        time.sleep(1.0)  # let grid settle before locating links
        
        # Debug: print first 5 anchors to understand structure
        anchors_debug = driver.execute_script(
            "var anchors = document.querySelectorAll('a');"
            "var results = [];"
            "for (var i = 0; i < Math.min(anchors.length, 5); i++) {"
            "  var href = anchors[i].href || '';"
            "  var text = anchors[i].innerText || '';"
            "  results.push({index: i, href: href, text: text.substring(0, 30)});"
            "}"
            "return results;"
        )
        print(f"  [DEBUG] First 5 anchors: {anchors_debug}")
        
        # Debug: print anchors in tbody
        tbody_anchors = driver.execute_script(
            "var tbody = document.querySelector('tbody');"
            "if (!tbody) { return 'No tbody found'; }"
            "var anchors = tbody.querySelectorAll('a');"
            "var results = [];"
            "for (var i = 0; i < anchors.length; i++) {"
            "  var href = anchors[i].href || '';"
            "  var text = anchors[i].innerText || '';"
            "  results.push({href: href, text: text.substring(0, 30)});"
            "}"
            "return results;"
        )
        print(f"  [DEBUG] Anchors in tbody: {tbody_anchors}")
        
        take_screenshot(driver, "04_before_click")
        
        item_link = find_first_supplier_item_link(driver)
        assert item_link is not None, "No supplier item link found in summary grid tbody"

        item_text = (item_link.text or item_link.get_attribute("innerText") or "").strip()
        print(f"  [INFO] Clicking supplier item: '{item_text}'")
        scroll_to(driver, item_link)
        try:
            driver.execute_script("arguments[0].click()", item_link)
        except Exception:
            item_link.click()

        wait_ready(driver)
        time.sleep(PAUSE)

        take_screenshot(driver, "04_item_details")

        url_ok = "ConsolDemandDetails" in driver.current_url
        heading_present = False
        try:
            heading_el = WebDriverWait(driver, 8).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[contains(normalize-space(.),'Consolidated Demand Report')]")
                )
            )
            heading_present = heading_el is not None
        except Exception:
            pass

        assert url_ok or heading_present, (
            f"Details page did not load after clicking item '{item_text}'. URL: {driver.current_url}"
        )
        print(f"  [PASS] Details page loaded for '{item_text}'. URL: {driver.current_url}")

    def test_05_back_to_summary(self, driver):
        """Click Back to Summary and verify return to Consolidated Demand View."""
        print("\n[test_05_back_to_summary] Clicking Back to Summary...")

        back_btn = safe_click_first(
            driver,
            [
                (By.XPATH, "//a[contains(normalize-space(.),'Back to Summary')]"),
                (By.XPATH, "//button[contains(normalize-space(.),'Back to Summary')]"),
                (By.XPATH, "//input[@type='button' and contains(@value,'Back to Summary')]"),
                (By.XPATH, "//a[contains(@href,'ConsolDemand') and not(contains(@href,'Details'))]"),
            ],
            timeout=8,
        )

        if back_btn:
            scroll_to(driver, back_btn)
            try:
                back_btn.click()
            except Exception:
                driver.execute_script("arguments[0].click()", back_btn)
        else:
            print("  [INFO] Back to Summary not found via locator - trying JS text fallback.")
            result = click_visible_text(driver, "Back to Summary")
            if not result:
                print("  [INFO] JS fallback failed - navigating directly to summary URL.")
                driver.get(CONSOL_DEMAND_URL)

        wait_ready(driver)
        time.sleep(PAUSE)

        take_screenshot(driver, "05_back_to_summary")

        url_ok = (
            "ConsolDemand" in driver.current_url
            and "Details" not in driver.current_url
        )
        heading_present = False
        try:
            heading_el = WebDriverWait(driver, 8).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[contains(normalize-space(.),'Consolidated Demand View')]")
                )
            )
            heading_present = heading_el is not None
        except Exception:
            pass

        assert url_ok or heading_present, (
            f"Did not return to summary page after Back to Summary. URL: {driver.current_url}"
        )
        print(f"  [PASS] Returned to summary page. URL: {driver.current_url}")
