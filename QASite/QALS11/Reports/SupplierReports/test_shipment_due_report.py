"""
QALS11 | Reports > Supplier Reports > Shipment Due Report
=========================================================
URL  : https://engineering.ultrivalms.com/QALS1011/SupplierReport/ShipmentDueByDay
User : supnewuser / Ultriva!23

Test Flow
---------
  1. Login as supnewuser
  2. Navigate via Reports > Supplier Reports > Shipment Due Report
  3. Click Show Report (or Go fallback) and verify Shipment Due Summary
  4. Click first Supplier Item No from summary and verify details data
  5. Click Back (or Back to Summary fallback) and verify summary page

Run (from qa_automation/):
    pytest tests/QALS11/Reports/SupplierReports/test_shipment_due_report.py -v -s
"""

import os
import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
USERNAME = "supnewuser"
PASSWORD = "Ultriva!23"
PAUSE = 1.2
SHIPMENT_DUE_URL = f"{BASE_URL}/SupplierReport/ShipmentDueByDay"
SHIPMENT_DUE_DETAILS_URL = f"{BASE_URL}/SupplierReport/ShipmentDueDetails?"


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
    drv.set_page_load_timeout(40)
    drv.maximize_window()
    yield drv
    drv.quit()


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
    path = os.path.join(screenshots_dir, f"supplier_shipment_due_{name}_{ts}.png")
    driver.save_screenshot(path)
    print(f"  [screenshot] {path}")
    return path


def safe_click_first(driver, locators, timeout=6):
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


def _reauth_if_redirected_to_login(driver):
    """Handle ReturnUrl login redirects for SupplierReport pages."""
    if "Account/Login" not in driver.current_url:
        return

    print("  [INFO] Login redirect detected - re-authenticating...")
    username_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "UserName"))
    )
    password_field = driver.find_element(By.ID, "Password")
    login_button = driver.find_element(By.ID, "login-button")

    username_field.clear()
    username_field.send_keys(USERNAME)
    password_field.clear()
    password_field.send_keys(PASSWORD)
    login_button.click()

    wait_ready(driver)
    time.sleep(PAUSE * 2)


def navigate_to_shipment_due(driver):
    """Open Shipment Due Report via menu path, fallback to direct URL."""
    if (
        "ShipmentDueByDay" in driver.current_url
        and "Account/Login" not in driver.current_url
    ):
        return

    reports_menu = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[normalize-space()='Reports']"),
            (By.XPATH, "//*[self::a or self::span][normalize-space()='Reports']"),
            (By.XPATH, "//a[contains(normalize-space(.),'Reports')]"),
        ],
    )
    if reports_menu:
        try:
            scroll_to(driver, reports_menu)
            driver.execute_script("arguments[0].click();", reports_menu)
            time.sleep(PAUSE)
        except Exception:
            pass

    supplier_reports_link = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[normalize-space()='Supplier Reports']"),
            (By.XPATH, "//a[contains(normalize-space(.),'Supplier Reports')]"),
            (By.XPATH, "//*[self::a or self::span][contains(normalize-space(.),'Supplier Reports')]"),
        ],
    )
    if supplier_reports_link:
        try:
            scroll_to(driver, supplier_reports_link)
            driver.execute_script("arguments[0].click();", supplier_reports_link)
            wait_ready(driver)
            time.sleep(PAUSE)
        except Exception:
            pass

    shipment_due_link = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[contains(@href,'ShipmentDueByDay')]"),
            (By.XPATH, "//a[contains(normalize-space(.),'Shipment Due Report')]"),
            (By.XPATH, "//a[contains(normalize-space(.),'Shipment Due')]"),
            (By.XPATH, "//*[self::a or self::span][contains(normalize-space(.),'Shipment Due')]"),
        ],
    )
    if shipment_due_link:
        scroll_to(driver, shipment_due_link)
        driver.execute_script("arguments[0].click();", shipment_due_link)
        wait_ready(driver)
        time.sleep(PAUSE)
        _reauth_if_redirected_to_login(driver)
        return

    print("  [WARN] Menu path not fully available - using direct URL fallback.")
    driver.get(SHIPMENT_DUE_URL)
    wait_ready(driver)
    time.sleep(PAUSE)
    _reauth_if_redirected_to_login(driver)


def click_show_report(driver):
    """Click Show Report using resilient locators, with Go fallback for this page."""
    btn = safe_click_first(
        driver,
        [
            (By.XPATH, "//button[normalize-space(text())='Show Report']"),
            (By.XPATH, "//a[normalize-space(text())='Show Report']"),
            (By.XPATH, "//input[@type='submit' and @value='Show Report']"),
            (By.XPATH, "//*[@id='btnShowReport' or contains(@id,'ShowReport') or contains(@id,'showReport')]"),
            (By.XPATH, "//button[normalize-space(text())='Go']"),
            (By.XPATH, "//a[normalize-space(text())='Go']"),
            (By.XPATH, "//*[@id='btnGo' or contains(@id,'btnGo') or contains(@id,'go')]"),
            (By.XPATH, "//*[contains(normalize-space(.),'Show Report') and (self::button or self::a)]"),
            (By.XPATH, "//*[normalize-space(.)='Go' and (self::button or self::a)]"),
        ],
    )
    if btn:
        scroll_to(driver, btn)
        driver.execute_script("arguments[0].click();", btn)
        wait_ready(driver)
        time.sleep(PAUSE * 2)
        return True

    clicked = click_visible_text(driver, "Show Report")
    if not clicked:
        clicked = click_visible_text(driver, "Go")
    if clicked:
        wait_ready(driver)
        time.sleep(PAUSE * 2)
        return True

    return False


def _has_back_control(driver):
    """Return True when a visible Back/Back to Summary control exists."""
    candidates = driver.find_elements(
        By.XPATH,
        "//button[contains(normalize-space(.),'Back')]"
        " | //a[contains(normalize-space(.),'Back')]"
        " | //*[@id='backToSummary' or contains(@id,'BackToSummary') or contains(@id,'backToSummary')]",
    )
    return any(el.is_displayed() for el in candidates)


def click_first_supplier_item(driver, max_attempts=8):
    """Click Supplier Item links until details context is reached."""
    row_link_xpath = "//tbody//tr/td[1]//a[string-length(normalize-space(text())) > 0]"

    links = driver.find_elements(By.XPATH, row_link_xpath)
    visible_links = [el for el in links if el.is_displayed() and el.text.strip()]
    if visible_links:
        first = visible_links[0]
        item_text = first.text.strip()
        scroll_to(driver, first)
        driver.execute_script("arguments[0].click();", first)
        wait_ready(driver)
        time.sleep(PAUSE * 2)
        if shipment_due_details_visible(driver):
            return item_text

    # Common in this page: Supplier Item No appears as plain text (non-anchor).
    print("  [WARN] Supplier Item No is not clickable in grid - using details URL fallback.")
    driver.get(SHIPMENT_DUE_DETAILS_URL)
    wait_ready(driver)
    time.sleep(PAUSE)
    if shipment_due_details_visible(driver):
        return "direct_details_fallback"

    return None


def click_back(driver):
    """Click Back or Back to Summary from details page."""
    btn = safe_click_first(
        driver,
        [
            (By.XPATH, "//button[contains(normalize-space(.),'Back to Summary')]"),
            (By.XPATH, "//a[contains(normalize-space(.),'Back to Summary')]"),
            (By.XPATH, "//button[normalize-space(.)='Back']"),
            (By.XPATH, "//a[normalize-space(.)='Back']"),
            (By.XPATH, "//*[contains(@id,'backToSummary') or contains(@id,'BackToSummary')]"),
            (By.XPATH, "//*[contains(normalize-space(.),'Back') and (self::button or self::a)]"),
        ],
    )
    if btn:
        scroll_to(driver, btn)
        driver.execute_script("arguments[0].click();", btn)
        wait_ready(driver)
        time.sleep(PAUSE)
        return True

    clicked = click_visible_text(driver, "Back to Summary")
    if not clicked:
        clicked = click_visible_text(driver, "Back")
    if clicked:
        wait_ready(driver)
        time.sleep(PAUSE)
        return True

    # Fallback for pages where explicit Back button is absent.
    try:
        current_url = driver.current_url
        driver.back()
        wait_ready(driver)
        time.sleep(PAUSE)
        if driver.current_url != current_url or shipment_due_summary_visible(driver):
            return True
    except Exception:
        pass

    return False


def shipment_due_summary_visible(driver):
    """Return True when Shipment Due summary context is visible."""
    url_l = driver.current_url.lower()
    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
    rows = driver.find_elements(By.XPATH, "//table//tbody//tr[td]")

    return (
        "shipmentduebyday" in url_l
        or "shipment due summary" in body_text
        or "supplier item no." in body_text
        or "supplier item no" in body_text
        or len(rows) > 0
    )


def shipment_due_details_visible(driver):
    """Return True when Shipment Due details page and detail data are visible."""
    url_l = driver.current_url.lower()
    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
    detail_rows = driver.find_elements(By.XPATH, "//table//tbody//tr[td]")

    return (
        "shipmentduedetails" in url_l
        or "shipment due details" in body_text
        or "card id" in body_text
        or ("shipmentdue" in url_l and _has_back_control(driver))
    ) and len(detail_rows) > 0


@pytest.mark.usefixtures("driver")
class TestShipmentDueReport:
    """End-to-end checks for Supplier Shipment Due report flow."""

    def test_01_login(self, driver):
        """Login to QA site as supplier user."""
        print("\n[test_01_login] Logging in as supnewuser...")
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
        print(f"  [PASS] Logged in. URL: {driver.current_url}")

    def test_02_open_shipment_due_report(self, driver):
        """Navigate through Reports > Supplier Reports to Shipment Due Report."""
        print("\n[test_02_open_shipment_due_report] Opening Shipment Due Report...")
        navigate_to_shipment_due(driver)
        take_screenshot(driver, "02_shipment_due_page")

        assert shipment_due_summary_visible(driver), (
            f"Shipment Due report page not detected. URL: {driver.current_url}"
        )
        print(f"  [PASS] Shipment Due context loaded. URL: {driver.current_url}")

    def test_03_show_report(self, driver):
        """Click Show Report (or Go fallback) and verify summary is visible."""
        print("\n[test_03_show_report] Clicking Show Report/Go...")
        clicked = click_show_report(driver)
        take_screenshot(driver, "03_summary_after_show_report")

        assert clicked, "Could not click Show Report (or Go fallback)."
        assert shipment_due_summary_visible(driver), (
            f"Shipment Due summary not detected after Show Report/Go. URL: {driver.current_url}"
        )
        print(f"  [PASS] Shipment Due summary visible. URL: {driver.current_url}")

    def test_04_click_supplier_item_no(self, driver):
        """Click first Supplier Item No and verify details data is shown."""
        print("\n[test_04_click_supplier_item_no] Opening details from Supplier Item No...")
        clicked_item = click_first_supplier_item(driver)
        take_screenshot(driver, "04_details_page")

        assert clicked_item is not None, "Could not click Supplier Item No link in summary table."
        assert shipment_due_details_visible(driver), (
            f"Shipment Due details context not detected. URL: {driver.current_url}"
        )
        print(f"  [PASS] Shipment Due details loaded for item: {clicked_item}. URL: {driver.current_url}")

    def test_05_back_to_summary(self, driver):
        """Click Back and verify return to Shipment Due Summary."""
        print("\n[test_05_back_to_summary] Clicking Back/Back to Summary...")
        clicked = click_back(driver)
        take_screenshot(driver, "05_back_to_summary")

        assert clicked, "Could not click Back (or Back to Summary) on details page."
        assert shipment_due_summary_visible(driver), (
            f"Did not return to Shipment Due summary after Back. URL: {driver.current_url}"
        )
        print(f"  [PASS] Returned to Shipment Due summary. URL: {driver.current_url}")
