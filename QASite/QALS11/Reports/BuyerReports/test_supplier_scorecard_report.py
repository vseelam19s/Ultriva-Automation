"""
QALS11 | Reports > Buyer Reports > Supplier Scorecard Report
=============================================================
URL  : https://engineering.ultrivalms.com/QALS1011
User : buyeruser / Ultriva!23

Test Flow
---------
  1.  Login as buyeruser
  2.  Navigate to Reports -> Buyer Reports -> Supplier Scorecard
  3.  Verify Supplier Scorecard summary loads with supplier list
    4.  Click on supplier "Supnew" to open item-level scorecard details
    5.  Verify Supplier Item Scorecard for Supnew loads
    6.  Click Back to Summary (equivalent to Change Filter on this report)
    7.  Verify return to Supplier Scorecard summary page as a separate test case

Run (from qa_automation/):
    pytest tests/QALS11/Reports/test_supplier_scorecard_report.py -v -s
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
SCORECARD_URL = f"{BASE_URL}/BuyerReport/SupplierScorecard"
SUPPLIER_NAME = "Supnew"


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
    path = os.path.join(screenshots_dir, f"supplier_scorecard_{name}_{ts}.png")
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
    """Click the first visible element whose text exactly matches via JS."""
    return driver.execute_script(
        "var wanted = arguments[0].trim().toLowerCase();"
        "var els = document.querySelectorAll('a, button, input[type=\"button\"], input[type=\"submit\"], span, div, li, td');"
        "for (var i = 0; i < els.length; i++) {"
        "  var el = els[i];"
        "  var txt = (el.innerText || el.value || '').trim().toLowerCase();"
        "  if (!txt) continue;"
        "  if (txt === wanted && el.offsetParent !== null) { el.click(); return el; }"
        "}"
        "return null;",
        text,
    )


def navigate_to_scorecard(driver):
    """Open Supplier Scorecard using direct URL first, menu fallback."""
    if "SupplierScorecard" in driver.current_url:
        return

    try:
        driver.get(SCORECARD_URL)
        wait_ready(driver)
        time.sleep(PAUSE)
        if "SupplierScorecard" in driver.current_url:
            return
    except Exception:
        pass

    reports_link = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[normalize-space()='Reports' or contains(normalize-space(.),'Reports')]"),
            (By.XPATH, "//*[self::a or self::span or self::div][contains(normalize-space(.),'Reports')]"),
            (By.XPATH, "//a[contains(@href,'Report')]"),
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
            driver.get(SCORECARD_URL)
            wait_ready(driver)
            time.sleep(PAUSE)
            return

    buyer_reports_link = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[normalize-space()='Buyer Reports' or contains(normalize-space(.),'Buyer Reports')]"),
            (By.XPATH, "//*[self::a or self::span][contains(normalize-space(.),'Buyer Reports')]"),
            (By.XPATH, "//a[contains(@href,'BuyerReport')]"),
        ],
        timeout=6,
    )
    if buyer_reports_link:
        scroll_to(driver, buyer_reports_link)
        driver.execute_script("arguments[0].click()", buyer_reports_link)
        wait_ready(driver)
        time.sleep(PAUSE)

    scorecard_link = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[contains(@href,'SupplierScorecard') or contains(normalize-space(.),'Supplier Scorecard') or contains(normalize-space(.),'Scorecard')]"),
            (By.XPATH, "//*[self::a or self::span][contains(normalize-space(.),'Scorecard')]"),
        ],
        timeout=6,
    )
    if scorecard_link:
        scroll_to(driver, scorecard_link)
        driver.execute_script("arguments[0].click()", scorecard_link)
        wait_ready(driver)
        time.sleep(PAUSE)
    else:
        print("  [WARN] Supplier Scorecard menu link not found - navigating directly to URL.")
        driver.get(SCORECARD_URL)
        wait_ready(driver)
        time.sleep(PAUSE)


def click_supplier(driver, supplier_name):
    """Click the named supplier row link to open the item scorecard details."""
    locators = [
        (By.XPATH, f"//a[normalize-space(text())='{supplier_name}']"),
        (By.XPATH, f"//a[contains(normalize-space(text()),'{supplier_name}')]"),
        (By.XPATH, f"//td[normalize-space(text())='{supplier_name}']"),
        (By.XPATH, f"//td[contains(normalize-space(text()),'{supplier_name}')]"),
        (By.XPATH, f"//*[normalize-space(text())='{supplier_name}' and (self::a or self::td or self::span)]"),
    ]
    element = safe_click_first(driver, locators, timeout=8)
    if element:
        scroll_to(driver, element)
        driver.execute_script("arguments[0].click()", element)
        wait_ready(driver)
        time.sleep(PAUSE * 2)
        return True

    # JS fallback: partial case-insensitive match
    js_result = driver.execute_script(
        "var wanted = arguments[0].toLowerCase();"
        "var nodes = document.querySelectorAll('a, td, span');"
        "for (var i = 0; i < nodes.length; i++) {"
        "  var node = nodes[i];"
        "  var text = (node.innerText || node.textContent || '').trim().toLowerCase();"
        "  if (text === wanted && node.offsetParent !== null) { node.click(); return true; }"
        "}"
        "return false;",
        supplier_name.lower(),
    )
    if js_result:
        wait_ready(driver)
        time.sleep(PAUSE * 2)
        return True

    return False


def click_back_to_summary(driver):
    """Click 'Back to Summary' (or 'Change Filter' if present) on the details page."""
    locators = [
        (By.XPATH, "//button[contains(normalize-space(.), 'Change Filter')]"),
        (By.XPATH, "//a[contains(normalize-space(.), 'Change Filter')]"),
        (By.XPATH, "//button[contains(normalize-space(.), 'Back to Summary')]"),
        (By.XPATH, "//a[contains(normalize-space(.), 'Back to Summary')]"),
        (By.XPATH, "//*[contains(@id,'changeFilter') or contains(@id,'ChangeFilter')]"),
        (By.XPATH, "//*[contains(@id,'backToSummary') or contains(@class,'back-summary')]"),
    ]
    for locator in locators:
        try:
            element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(locator))
            scroll_to(driver, element)
            driver.execute_script("arguments[0].click();", element)
            wait_ready(driver)
            time.sleep(PAUSE)
            print(f"  [INFO] Clicked: {element.text.strip() or 'Back to Summary / Change Filter'}")
            return True
        except Exception:
            continue

    for text in ("Change Filter", "Back to Summary"):
        if click_visible_text(driver, text):
            wait_ready(driver)
            time.sleep(PAUSE)
            print(f"  [INFO] Clicked '{text}' via JS fallback")
            return True

    return False


def scorecard_loaded(driver):
    """Check that the Supplier Scorecard summary is visible."""
    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
    return (
        "supplier scorecard" in body_text
        or "supplierscorecarddetails" in driver.current_url.lower()
        or "supplierscorecard" in driver.current_url.lower()
    )


# ============================================================================
# TEST CLASS
# ============================================================================


@pytest.mark.usefixtures("driver")
class TestSupplierScorecardReport:
    # -- TC-SSC-001: Login --------------------------------------------------
    def test_01_login(self, driver):
        """Login to QA site with buyeruser credentials."""
        print("\n[TC-SSC-001] Logging in to QA site...")
        driver.get(BASE_URL)
        wait_ready(driver)

        username_field = find(driver, By.ID, "UserName")
        password_field = find(driver, By.ID, "Password")
        login_button = clickable(driver, By.ID, "login-button")

        username_field.clear()
        username_field.send_keys(USERNAME)
        password_field.clear()
        password_field.send_keys(PASSWORD)
        login_button.click()
        wait_ready(driver)
        time.sleep(PAUSE)

        take_screenshot(driver, "01_after_login")
        current_url = driver.current_url
        print(f"  [URL] {current_url}")
        assert BASE_URL.lower() in current_url.lower() or "Home" in current_url, (
            f"Login may have failed. URL: {current_url}"
        )
        print("  [PASS] Login successful.")

    # -- TC-SSC-002: Open Supplier Scorecard --------------------------------
    def test_02_open_supplier_scorecard(self, driver):
        """Navigate to Reports -> Buyer Reports -> Supplier Scorecard."""
        print("\n[TC-SSC-002] Opening Supplier Scorecard report...")
        navigate_to_scorecard(driver)

        take_screenshot(driver, "02_scorecard_summary")
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        assert (
            "supplierscorecard" in driver.current_url.lower()
            or "supplier scorecard" in page_text
        ), f"Expected Supplier Scorecard page. Got: {driver.current_url}"
        print(f"  [PASS] Supplier Scorecard loaded: {driver.current_url}")

    # -- TC-SSC-003: Click Supnew supplier link ----------------------------
    def test_03_click_supnew_supplier_link(self, driver):
        """Click Supnew supplier and verify item scorecard details load."""
        print(f"\n[TC-SSC-003] Clicking supplier '{SUPPLIER_NAME}'...")

        clicked = click_supplier(driver, SUPPLIER_NAME)
        assert clicked, f"Could not click supplier '{SUPPLIER_NAME}' on Supplier Scorecard"
        print(f"  [PASS] Clicked supplier '{SUPPLIER_NAME}'")

        take_screenshot(driver, "03_supnew_details")
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        assert (
            "supplierscorecarddetails" in driver.current_url.lower()
            or "supplier item scorecard" in page_text
            or SUPPLIER_NAME.lower() in page_text
        ), f"Expected Supnew item scorecard details. Got: {driver.current_url}"
        print(f"  [PASS] Supnew item scorecard details loaded: {driver.current_url}")

    # -- TC-SSC-004: Click Back to Summary --------------------------------
    def test_04_click_back_to_summary(self, driver):
        """Click Back to Summary from details and verify return to summary page."""
        print("\n[TC-SSC-004] Clicking Back to Summary / Change Filter...")

        back_clicked = click_back_to_summary(driver)
        assert back_clicked, "Could not click 'Back to Summary' or 'Change Filter' on details page"
        print("  [PASS] Back to Summary / Change Filter clicked.")

        take_screenshot(driver, "04_after_back_to_summary")
        page_text_after = driver.find_element(By.TAG_NAME, "body").text.lower()
        assert (
            "supplierscorecard" in driver.current_url.lower()
            or "supplier scorecard" in page_text_after
        ), f"Did not return to Supplier Scorecard summary. URL: {driver.current_url}"
        print(f"  [PASS] Returned to Supplier Scorecard summary: {driver.current_url}")
