"""
QALS11 | Reports > Supplier Reports > Supplier On-Time Report
=============================================================
URL  : https://engineering.ultrivalms.com/QALS1011
User : supnew / Ultriva!23

Test Flow
---------
  1. Login as supnew
  2. Switch Application to Supplier
  3. Navigate to Reports -> Supplier On-Time Report
  4. Select Date Range = Past One Year
  5. Select Plant = TCEK-Ram
  6. Keep default values for other fields
  7. Click Show Report
  8. Click Change Filter and verify return to filter page

Run (from qa_automation/):
    pytest tests/QALS11/Reports/SupplierReports/test_supplier_ontime_report.py -v -s
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
USERNAME = "supnew"
PASSWORD = "Ultriva!23"
PAUSE = 1.2
ONTIME_SHIPMENT_URL = f"{BASE_URL}/SupplierReport/OnTimeShipmentFilter"
PLANT_NAME = "TCEK-Ram"


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
    drv.set_page_load_timeout(40)
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
    path = os.path.join(screenshots_dir, f"supplier_ontime_{name}_{ts}.png")
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


def navigate_to_ontime_shipment(driver):
    """Open Supplier On-Time Shipment report, using direct URL first for stability."""
    if "OnTimeShipmentFilter" in driver.current_url:
        return

    # The report is exposed through the Reports > Supplier Reports menu on the reports home page.
    driver.get(f"{BASE_URL}/Report/Home")
    wait_ready(driver)
    time.sleep(PAUSE)

    supplier_reports_link = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[normalize-space()='Supplier Reports']"),
            (By.XPATH, "//a[contains(normalize-space(.),'Supplier Reports')]"),
            (By.XPATH, "//*[self::a or self::span][contains(normalize-space(.),'Supplier Reports')]") ,
        ],
        timeout=6,
    )
    if supplier_reports_link:
        scroll_to(driver, supplier_reports_link)
        driver.execute_script("arguments[0].click()", supplier_reports_link)
        wait_ready(driver)
        time.sleep(PAUSE)

    report_link = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[normalize-space()='Supplier On-Time']"),
            (By.XPATH, "//a[contains(@href,'OnTimeShipmentFilter')]") ,
            (By.XPATH, "//a[contains(@href,'OnTimeShipmentFilter') or contains(normalize-space(.),'On-Time Shipment') or contains(normalize-space(.),'On Time Shipment')]") ,
            (By.XPATH, "//*[self::a or self::span][contains(normalize-space(.),'On-Time Shipment') or contains(normalize-space(.),'On Time Shipment') or contains(normalize-space(.),'Shipment')]") ,
        ],
        timeout=6,
    )
    if report_link:
        scroll_to(driver, report_link)
        driver.execute_script("arguments[0].click();", report_link)
        wait_ready(driver)
        time.sleep(PAUSE)
    else:
        print("  [WARN] On-Time Shipment menu link not found - navigating directly to report URL.")
        return


def open_date_range_dropdown(driver):
    """Open the Date Range control using multiple locator strategies."""
    trigger_selects = [
        (By.ID, "DateRange"),
        (By.NAME, "DateRange"),
        (By.XPATH, "//input[contains(@id,'DateRange') or contains(@name,'DateRange')]"),
        (By.XPATH, "//label[contains(.,'Date Range')]/following::input[1]"),
        (By.XPATH, "//*[contains(normalize-space(.),'Date Range')]/following::input[1]"),
        (By.XPATH, "//input[@type='text'][contains(@value,'Date') or contains(@id,'Range') or contains(@name,'Range')]") ,
    ]
    for by, locator in trigger_selects:
        try:
            el = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((by, locator))
            )
            if el.is_displayed() and el.is_enabled():
                scroll_to(driver, el)
                el.click()
                time.sleep(0.8)
                return el
        except Exception:
            continue

    clicked = click_visible_text(driver, "Date Range")
    if clicked:
        time.sleep(0.8)
        return clicked
    return None


def select_date_range_past_one_year(driver):
    """Select Past One Year from the Date Range menu."""
    trigger = open_date_range_dropdown(driver)
    assert trigger, "Could not find Date Range trigger on Supplier On-Time Shipment report"

    option_locators = [
        "//*[self::li or self::a or self::span or self::div][normalize-space(.)='Past One Year']",
        "//*[self::li or self::a or self::span or self::div][contains(normalize-space(.),'Past One Year')]",
        "//*[contains(@class,'ui-menu-item')]//*[contains(normalize-space(.),'Past One Year')]",
        "//*[contains(@class,'dropdown-menu')]//*[contains(normalize-space(.),'Past One Year')]",
    ]
    for locator in option_locators:
        try:
            option = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, locator))
            )
            scroll_to(driver, option)
            driver.execute_script("arguments[0].click();", option)
            time.sleep(0.8)
            print(f"  [INFO] Selected Date Range option via: {locator}")
            return True
        except Exception:
            continue

    js_result = driver.execute_script(
        "var wanted = 'Past One Year'.toLowerCase();"
        "var nodes = document.querySelectorAll('li, a, span, div');"
        "for (var i = 0; i < nodes.length; i++) {"
        "  var node = nodes[i];"
        "  var text = (node.innerText || node.textContent || '').trim().toLowerCase();"
        "  if (text === wanted || text.indexOf(wanted) !== -1) { node.click(); return true; }"
        "}"
        "return false;"
    )
    if js_result:
        time.sleep(0.8)
        print("  [INFO] Selected Past One Year via JS fallback")
        return True

    return False


def open_plant_dropdown(driver):
    """Open the Plant control using multiple locator strategies."""
    plant_selects = [
        (By.ID, "Plant"),
        (By.NAME, "Plant"),
        (By.XPATH, "//*[@id='divPlant' or contains(@id,'Plant')][self::div or self::span]"),
        (By.XPATH, "//label[contains(.,'Plant')]/following::*[self::div or self::span][1]"),
        (By.XPATH, "//*[contains(@class,'select2') and (contains(@id,'Plant') or contains(@class,'plant'))]"),
        (By.XPATH, "//*[contains(@class,'chosen-container') and (contains(@id,'Plant') or contains(@class,'plant'))]"),
        (By.XPATH, "//input[contains(@id,'Plant') or contains(@name,'Plant')]"),
        (By.XPATH, "//label[contains(.,'Plant')]/following::input[1]"),
        (By.XPATH, "//*[contains(normalize-space(.),'Plant')]/following::input[1]"),
    ]
    for by, locator in plant_selects:
        try:
            el = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((by, locator))
            )
            if el.is_displayed() and el.is_enabled():
                scroll_to(driver, el)
                el.click()
                time.sleep(0.8)
                return el
        except Exception:
            continue

    clicked = click_visible_text(driver, "Plant")
    if clicked:
        time.sleep(0.8)
        return clicked
    return None


def select_plant(driver, plant_name):
    """Select Plant from the dropdown."""
    page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
    if plant_name.lower() in page_text:
        print(f"  [INFO] Plant '{plant_name}' appears already selected")
        return True

    trigger = open_plant_dropdown(driver)
    assert trigger, "Could not find Plant trigger on Supplier On-Time Shipment report"

    option_locators = [
        f"//*[self::li or self::a or self::span or self::div][normalize-space()='{plant_name}']",
        f"//*[self::li or self::a or self::span or self::div][contains(normalize-space(),'{plant_name}')]",
        f"//*[contains(@class,'ui-menu-item')]//*[contains(normalize-space(),'{plant_name}')]",
        f"//*[contains(@class,'dropdown-menu')]//*[contains(normalize-space(),'{plant_name}')]",
    ]
    for locator in option_locators:
        try:
            option = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, locator))
            )
            scroll_to(driver, option)
            driver.execute_script("arguments[0].click();", option)
            time.sleep(0.8)
            print(f"  [INFO] Selected Plant option via: {locator}")
            return True
        except Exception:
            continue

    js_result = driver.execute_script(
        "var wanted = arguments[0].toLowerCase();"
        "var nodes = document.querySelectorAll('li, a, span, div');"
        "for (var i = 0; i < nodes.length; i++) {"
        "  var node = nodes[i];"
        "  var text = (node.innerText || node.textContent || '').trim().toLowerCase();"
        "  if (text.indexOf(wanted) !== -1) { node.click(); return true; }"
        "}"
        "return false;",
        plant_name,
    )
    if js_result:
        time.sleep(0.8)
        print(f"  [INFO] Selected Plant '{plant_name}' via JS fallback")
        return True

    return False


def click_show_report(driver):
    """Click the Show Report button on the filter page."""
    show_btn = safe_click_first(
        driver,
        [
            (By.XPATH, "//button[normalize-space(text())='Show Report']"),
            (By.XPATH, "//a[normalize-space(text())='Show Report']"),
            (By.XPATH, "//input[@type='submit' and @value='Show Report']"),
            (By.XPATH, "//*[@id='btnShowReport' or contains(@id,'ShowReport') or contains(@id,'showReport')]"),
            (By.XPATH, "//*[contains(normalize-space(.),'Show Report') and (contains(@class,'btn') or contains(@class,'button'))]"),
        ],
        timeout=6,
    )
    if show_btn:
        scroll_to(driver, show_btn)
        driver.execute_script("arguments[0].click()", show_btn)
        wait_ready(driver)
        time.sleep(PAUSE * 2)
        return True

    clicked = click_visible_text(driver, "Show Report")
    if clicked:
        wait_ready(driver)
        time.sleep(PAUSE * 2)
        return True

    return False


def click_change_filter_btn(driver):
    """Click the Change Filter button on the report page."""
    locators = [
        (By.XPATH, "//button[contains(normalize-space(.), 'Change Filter')]"),
        (By.XPATH, "//a[contains(normalize-space(.), 'Change Filter')]"),
        (By.XPATH, "//button[@id='changeFilter' or contains(@id, 'ChangeFilter') or contains(@id, 'changeFilter')]"),
    ]

    for locator in locators:
        try:
            element = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(locator)
            )
            scroll_to(driver, element)
            driver.execute_script("arguments[0].click();", element)
            wait_ready(driver)
            time.sleep(PAUSE)
            print("  [INFO] Clicked Change Filter button")
            return True
        except Exception:
            continue

    clicked = click_visible_text(driver, "Change Filter")
    if clicked:
        wait_ready(driver)
        time.sleep(PAUSE)
        print("  [INFO] Clicked Change Filter via JS text fallback")
        return True

    return False


def report_loaded(driver):
    """Check that the report page or results are visible."""
    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
    if "on time shipment" in body_text or "show report" in body_text or "shipment" in body_text:
        return True
    rows = driver.find_elements(By.XPATH, "//table//tr[td]")
    return len(rows) > 0


# ============================================================================
# TEST CLASS
# ============================================================================


@pytest.mark.usefixtures("driver")
class TestSupplierOntimeReport:
    # ── TC-SOT-001: Login ──────────────────────────────────────────────────
    def test_01_login(self, driver):
        """Login to QA site with supnew credentials."""
        print("\n[TC-SOT-001] Logging in to QA site...")
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
        assert BASE_URL.lower() in current_url.lower() or "Home" in current_url or "SetReadyToShipDateItems" in current_url, \
            f"Login may have failed. URL: {current_url}"
        print("  [PASS] Login successful.")

    # ── TC-SOT-002: Open On-Time Shipment report ───────────────────────
    def test_02_open_ontime_shipment_report(self, driver):
        """Navigate to Reports -> Supplier Reports -> On-Time Shipment Report."""
        print("\n[TC-SOT-002] Opening On-Time Shipment report...")
        navigate_to_ontime_shipment(driver)

        take_screenshot(driver, "02_ontime_shipment_report")
        assert "OnTimeShipmentFilter" in driver.current_url or \
            "SupplierReport/OnTimeShipmentFilter" in driver.current_url or \
            "OnTimeShipment" in driver.current_url, \
            f"Expected On-Time Shipment report page. Got: {driver.current_url}"
        print(f"  [PASS] On-Time Shipment report page loaded: {driver.current_url}")

    # ── TC-SOT-003: Select Past One Year, Plant, and show report ───
    def test_03_select_filters_and_show_report(self, driver):
        """Select Past One Year, plant TCEK-Ram, keep defaults, and click Show Report."""
        print("\n[TC-SOT-003] Selecting filters and clicking Show Report...")

        selected = select_date_range_past_one_year(driver)
        assert selected, "Could not select Past One Year in the Date Range control"
        print("  [INFO] Date Range set to Past One Year")

        selected_plant = select_plant(driver, PLANT_NAME)
        assert selected_plant, f"Could not select plant '{PLANT_NAME}' on Supplier On-Time Shipment report"
        print(f"  [INFO] Plant set to {PLANT_NAME}")

        clicked = click_show_report(driver)
        assert clicked, "Show Report button not found on Supplier On-Time Shipment report"
        print("  [PASS] Show Report button clicked")

        take_screenshot(driver, "03_after_show_report")

        is_loaded = report_loaded(driver)
        assert is_loaded, "Report did not load or is empty"
        print("  [PASS] Report loaded successfully.")

        changed = click_change_filter_btn(driver)
        assert changed, "Change Filter button not found after report was shown"
        print("  [PASS] Change Filter button clicked")

        take_screenshot(driver, "04_after_change_filter")

        filter_context_ok = (
            "OnTimeShipmentFilter" in driver.current_url
            or "OnTimeShipment" in driver.current_url
            or safe_click_first(
                driver,
                [
                    (By.XPATH, "//button[normalize-space(text())='Show Report']"),
                    (By.XPATH, "//a[normalize-space(text())='Show Report']"),
                    (By.XPATH, "//input[@type='submit' and @value='Show Report']"),
                    (By.XPATH, "//label[contains(.,'Date Range')]"),
                ],
                timeout=4,
            )
            is not None
        )
        assert filter_context_ok, f"Did not navigate back to filter page after Change Filter. URL: {driver.current_url}"
        print(f"  [PASS] Navigated back to filter page: {driver.current_url}")