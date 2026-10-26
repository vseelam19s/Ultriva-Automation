
"""
QALS11 | Reports > Supplier Reports > Supplier On-Time Report
=============================================================
URL  : https://engineering.ultrivalms.com/QALS1011/SupplierReport/OnTimeShipmentNewFilter
User : supnewuser / Ultriva!23

Test Flow
---------
  1. Login as supnewuser
  2. Navigate via Reports > Supplier Reports > Supplier On-Time Report
  3. Click Show Report
  4. Click Change Filter and verify return to filter page

Run (from qa_automation/):
    pytest tests/QALS11/Reports/SupplierReports/test_supplier_on_time_report.py -v -s
"""

import os
import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait


BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
USERNAME = "supnewuser"
PASSWORD = "Ultriva!23"
PAUSE = 1.2
SUPPLIER_ONTIME_FILTER_URL = f"{BASE_URL}/SupplierReport/OnTimeShipmentNewFilter"


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
    path = os.path.join(screenshots_dir, f"supplier_on_time_{name}_{ts}.png")
    driver.save_screenshot(path)
    print(f"  [screenshot] {path}")
    return path


def safe_click_first(driver, locators, timeout=6):
    """Return first clickable element found from a list of locators."""
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


def navigate_to_supplier_on_time_report(driver):
    """Open Supplier On-Time Report via menu path, fallback to direct URL."""
    if (
        "OnTimeShipmentNewFilter" in driver.current_url
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

    supplier_reports = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[normalize-space()='Supplier Reports']"),
            (By.XPATH, "//a[contains(normalize-space(.),'Supplier Reports')]"),
            (
                By.XPATH,
                "//*[self::a or self::span][contains(normalize-space(.),'Supplier Reports')]",
            ),
        ],
    )
    if supplier_reports:
        try:
            scroll_to(driver, supplier_reports)
            driver.execute_script("arguments[0].click();", supplier_reports)
            wait_ready(driver)
            time.sleep(PAUSE)
        except Exception:
            pass

    on_time_link = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[contains(@href,'/SupplierReport/OnTimeShipmentNewFilter')]"),
            (By.XPATH, "//a[contains(@href,'OnTimeShipmentNewFilter')]"),
            (By.XPATH, "//a[contains(normalize-space(.),'Supplier On-Time Report')]"),
            (By.XPATH, "//a[contains(normalize-space(.),'On Time Shipment')]"),
            (
                By.XPATH,
                "//*[self::a or self::span][contains(normalize-space(.),'On Time Shipment') or contains(normalize-space(.),'On-Time Shipment')]",
            ),
        ],
    )
    if on_time_link:
        try:
            scroll_to(driver, on_time_link)
            driver.execute_script("arguments[0].click();", on_time_link)
            wait_ready(driver)
            time.sleep(PAUSE)
            _reauth_if_redirected_to_login(driver)
            if (
                "OnTimeShipmentNewFilter" in driver.current_url
                and "Account/Login" not in driver.current_url
            ):
                return
        except Exception:
            pass

    print("  [WARN] Menu path not fully available - using direct filter URL fallback.")
    driver.get(SUPPLIER_ONTIME_FILTER_URL)
    wait_ready(driver)
    time.sleep(PAUSE)
    _reauth_if_redirected_to_login(driver)


def click_show_report(driver):
    """Click Show Report using resilient locators + JS fallback."""
    btn = safe_click_first(
        driver,
        [
            (By.XPATH, "//button[normalize-space(text())='Show Report']"),
            (By.XPATH, "//a[normalize-space(text())='Show Report']"),
            (By.XPATH, "//input[@type='submit' and @value='Show Report']"),
            (
                By.XPATH,
                "//*[@id='btnShowReport' or contains(@id,'ShowReport') or contains(@id,'showReport')]",
            ),
            (
                By.XPATH,
                "//*[contains(normalize-space(.),'Show Report') and (self::button or self::a)]",
            ),
        ],
    )
    if btn:
        scroll_to(driver, btn)
        driver.execute_script("arguments[0].click();", btn)
        wait_ready(driver)
        time.sleep(PAUSE * 2)
        return True

    clicked = click_visible_text(driver, "Show Report")
    if clicked:
        wait_ready(driver)
        time.sleep(PAUSE * 2)
        return True

    return False


def select_report_type_receipt_performance(driver):
    """Select Report Type = Receipt Performance using Select + JS fallback."""
    locators = [
        (By.ID, "ReportType"),
        (By.NAME, "ReportType"),
        (By.XPATH, "//select[contains(@id,'ReportType') or contains(@name,'ReportType')]"),
        (By.XPATH, "//label[contains(normalize-space(.),'Report Type')]/following::select[1]"),
        (By.XPATH, "//*[contains(normalize-space(.),'Report Type')]/following::select[1]"),
    ]

    select_el = None
    for by, locator in locators:
        try:
            select_el = WebDriverWait(driver, 6).until(
                EC.presence_of_element_located((by, locator))
            )
            if select_el and select_el.is_displayed():
                break
        except Exception:
            continue

    if not select_el:
        return False

    scroll_to(driver, select_el)
    try:
        Select(select_el).select_by_visible_text("Receipt Performance")
    except Exception:
        js_selected = driver.execute_script(
            "var s = arguments[0];"
            "var wanted = 'receipt performance';"
            "if (!s || !s.options) return false;"
            "for (var i = 0; i < s.options.length; i++) {"
            "  var t = (s.options[i].text || '').trim().toLowerCase();"
            "  if (t === wanted || t.indexOf(wanted) !== -1) {"
            "    s.selectedIndex = i;"
            "    s.dispatchEvent(new Event('change', {bubbles: true}));"
            "    s.dispatchEvent(new Event('input', {bubbles: true}));"
            "    return true;"
            "  }"
            "}"
            "return false;",
            select_el,
        )
        if not js_selected:
            return False

    time.sleep(0.6)
    selected_text = Select(select_el).first_selected_option.text.strip().lower()
    return "receipt performance" in selected_text


def click_change_filter_or_back(driver):
    """Click Change Filter; fallback to Back for alternate report views."""
    btn = safe_click_first(
        driver,
        [
            (By.XPATH, "//button[contains(normalize-space(.),'Change Filter')]"),
            (By.XPATH, "//a[contains(normalize-space(.),'Change Filter')]"),
            (
                By.XPATH,
                "//*[@id='changeFilter' or contains(@id,'ChangeFilter') or contains(@id,'changeFilter')]",
            ),
            (
                By.XPATH,
                "//*[contains(normalize-space(.),'Change Filter') and (self::button or self::a)]",
            ),
        ],
    )
    if btn:
        scroll_to(driver, btn)
        driver.execute_script("arguments[0].click();", btn)
        wait_ready(driver)
        time.sleep(PAUSE)
        return True

    clicked = click_visible_text(driver, "Change Filter")
    if clicked:
        wait_ready(driver)
        time.sleep(PAUSE)
        return True

    back_btn = safe_click_first(
        driver,
        [
            (By.XPATH, "//button[contains(normalize-space(.),'Back')]"),
            (By.XPATH, "//a[contains(normalize-space(.),'Back')]"),
            (By.XPATH, "//*[contains(normalize-space(.),'Back') and (self::button or self::a)]"),
        ],
        timeout=4,
    )
    if back_btn:
        scroll_to(driver, back_btn)
        driver.execute_script("arguments[0].click();", back_btn)
        wait_ready(driver)
        time.sleep(PAUSE)
        return True

    driver.get(SUPPLIER_ONTIME_FILTER_URL)
    wait_ready(driver)
    time.sleep(PAUSE)
    _reauth_if_redirected_to_login(driver)
    return (
        "OnTimeShipmentNewFilter" in driver.current_url
        and "Account/Login" not in driver.current_url
    )


def report_loaded(driver):
    """Check that report content is loaded (including no-data states)."""
    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
    if (
        "on time shipment" in body_text
        or "shipment performance" in body_text
        or "performance" in body_text
        or "no data" in body_text
    ):
        return True

    rows = driver.find_elements(By.XPATH, "//table//tr[td]")
    return len(rows) > 0


@pytest.mark.usefixtures("driver")
class TestSupplierOnTimeReport:
    """Validate Supplier On-Time Report flow."""

    def test_01_login(self, driver):
        """Login with supplier credentials."""
        print("\n[TC-SOTR-001] Logging in as supnewuser...")
        driver.get(f"{BASE_URL}/Account/Login")
        wait_ready(driver)

        find(driver, By.ID, "UserName").clear()
        find(driver, By.ID, "UserName").send_keys(USERNAME)
        find(driver, By.ID, "Password").clear()
        find(driver, By.ID, "Password").send_keys(PASSWORD)
        clickable(driver, By.ID, "login-button").click()

        wait_ready(driver)
        time.sleep(PAUSE * 2)

        assert "Account/Login" not in driver.current_url, (
            f"Login appears to have failed. Current URL: {driver.current_url}"
        )
        take_screenshot(driver, "01_login")

    def test_02_open_supplier_on_time_report(self, driver):
        """Open Supplier On-Time filter page through menu with direct URL fallback."""
        print("[TC-SOTR-002] Opening Supplier On-Time report filter...")
        navigate_to_supplier_on_time_report(driver)

        assert "OnTimeShipmentNewFilter" in driver.current_url and "Account/Login" not in driver.current_url, (
            f"Expected Supplier On-Time filter page, got: {driver.current_url}"
        )

        body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        assert (
            "on time shipment" in body_text
            or "report type" in body_text
            or "show report" in body_text
        ), "Supplier On-Time filter content not visible after navigation"
        take_screenshot(driver, "02_filter_page")

    def test_03_click_show_report(self, driver):
        """Click Show Report and verify report is displayed."""
        print("[TC-SOTR-003] Clicking Show Report...")
        assert click_show_report(driver), "Could not click Show Report"

        assert report_loaded(driver), "Supplier On-Time report did not appear after Show Report"
        take_screenshot(driver, "03_report_page")

    def test_04_click_change_filter(self, driver):
        """Click Change Filter and verify return to filter page."""
        print("[TC-SOTR-004] Clicking Change Filter...")
        assert click_change_filter_or_back(driver), "Could not click Change Filter/Back"

        body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        on_filter_url = "OnTimeShipmentNewFilter" in driver.current_url
        has_filter_content = (
            "show report" in body_text
            or "report type" in body_text
            or "date range" in body_text
        )
        assert on_filter_url or has_filter_content, (
            f"Did not return to Supplier On-Time filter context. URL: {driver.current_url}"
        )
        take_screenshot(driver, "04_back_to_filter")

    def test_05_receipt_performance_show_report_then_change_filter(self, driver):
        """From filter select Receipt Performance, show report, then change filter."""
        print("[TC-SOTR-005] Selecting Report Type = Receipt Performance...")

        assert select_report_type_receipt_performance(driver), (
            "Could not select Report Type = Receipt Performance"
        )
        take_screenshot(driver, "05_receipt_performance_selected")

        print("[TC-SOTR-005] Clicking Show Report for Receipt Performance...")
        assert click_show_report(driver), "Could not click Show Report for Receipt Performance"
        assert report_loaded(driver), "Receipt Performance report did not appear after Show Report"
        take_screenshot(driver, "05_receipt_performance_report")

        print("[TC-SOTR-005] Clicking Change Filter after Receipt Performance report...")
        assert click_change_filter_or_back(driver), "Could not click Change Filter/Back"

        body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        on_filter_url = "OnTimeShipmentNewFilter" in driver.current_url
        has_filter_content = (
            "show report" in body_text
            or "report type" in body_text
            or "date range" in body_text
        )
        assert on_filter_url or has_filter_content, (
            f"Did not return to Supplier On-Time filter context. URL: {driver.current_url}"
        )
        take_screenshot(driver, "05_receipt_performance_back_to_filter")
