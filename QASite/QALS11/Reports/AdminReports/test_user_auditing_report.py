"""
QALS11 | Reports > Admin Reports > User Auditing Report
=======================================================
URL  : https://engineering.ultrivalms.com/QALS1011
User : buyeruser / Ultriva!23

Test Flow
---------
  1.  Login as buyeruser
  2.  Open User Auditing Report filter page
  3.  Ensure table = EboUser
  4.  Select Date Range = Year To Date
  5.  Click Show Report
  6.  Verify report output loads
  7.  Click Change Filter and verify return to filter page

Run (from qa_automation/):
    pytest tests/QALS11/Reports/AdminReports/test_user_auditing_report.py -v -s
"""

import os
import time
from datetime import date

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

# ============================================================================
# CONFIGURATION
# ============================================================================
BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
USERNAME = "buyeruser"
PASSWORD = "Ultriva!23"
PAUSE = 1.2
AUDITING_REPORT_FILTER_URL = f"{BASE_URL}/AdminReport/AuditingReportFilter"


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
    """Scroll element into view and pause."""
    driver.execute_script("arguments[0].scrollIntoView({block:'center'})", el)
    time.sleep(0.3)


def take_screenshot(driver, name):
    """Take and save screenshot with timestamp."""
    screenshots_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "reports", "screenshots"
    )
    os.makedirs(screenshots_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(screenshots_dir, f"user_auditing_{name}_{ts}.png")
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


def year_to_date_range():
    """Return date range string from Jan 1 to today in site format."""
    today = date.today()
    start = date(today.year, 1, 1)
    return f"{start:%m/%d/%Y}-{today:%m/%d/%Y}"


def navigate_to_user_auditing_report(driver):
    """Open User Auditing report using direct URL."""
    if "AuditingReport" in driver.current_url:
        return

    driver.get(AUDITING_REPORT_FILTER_URL)
    wait_ready(driver)
    time.sleep(PAUSE)


def ensure_ebouser_selected(driver):
    """Ensure the report table selection is EboUser."""
    table_field = safe_click_first(
        driver,
        [
            (By.ID, "Table"),
            (By.NAME, "Table"),
            (By.XPATH, "//select[@id='Table' or @name='Table']"),
            (By.XPATH, "//label[contains(.,'Table')]/following::select[1]"),
            (By.XPATH, "//*[contains(normalize-space(.),'Table:')]/following::select[1]"),
            (By.XPATH, "//select[option[normalize-space(.)='EboUser']]"),
        ],
        timeout=5,
    )

    if not table_field:
        for select_el in driver.find_elements(By.TAG_NAME, "select"):
            try:
                if not select_el.is_displayed():
                    continue
                option_texts = [
                    option.text.strip() for option in Select(select_el).options if option.text
                ]
                if "EboUser" in option_texts:
                    table_field = select_el
                    break
            except Exception:
                continue

    assert table_field, "Could not find Table selector on Auditing Report filter page"

    scroll_to(driver, table_field)
    Select(table_field).select_by_visible_text("EboUser")
    time.sleep(0.5)
    selected_value = Select(table_field).first_selected_option.text.strip()
    assert selected_value == "EboUser", f"Expected EboUser table, got {selected_value!r}"
    print("  [PASS] Table selection confirmed as EboUser.")


def open_date_range_dropdown(driver):
    """Open Date Range control using multiple locators."""
    trigger_selects = [
        (By.ID, "DateRange"),
        (By.NAME, "DateRange"),
        (By.XPATH, "//input[contains(@id,'DateRange') or contains(@name,'DateRange')]"),
        (By.XPATH, "//label[contains(.,'Date Range')]/following::input[1]"),
        (By.XPATH, "//*[contains(normalize-space(.),'Date Range')]/following::input[1]"),
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


def select_year_to_date(driver):
    """Select Year To Date from dropdown, fallback to direct textbox assignment."""
    trigger = open_date_range_dropdown(driver)
    if trigger:
        option_locators = [
            "//*[self::li or self::a or self::span or self::div][normalize-space(.)='Year To Date']",
            "//*[self::li or self::a or self::span or self::div][normalize-space(.)='Year to Date']",
            "//*[self::li or self::a or self::span or self::div][contains(normalize-space(.),'Year To Date') or contains(normalize-space(.),'Year to Date')]",
            "//*[contains(@class,'ui-menu-item')]//*[contains(normalize-space(.),'Year') and contains(normalize-space(.),'Date')]",
            "//*[contains(@class,'dropdown-menu')]//*[contains(normalize-space(.),'Year') and contains(normalize-space(.),'Date')]",
        ]
        for locator in option_locators:
            try:
                option = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, locator))
                )
                scroll_to(driver, option)
                driver.execute_script("arguments[0].click();", option)
                time.sleep(0.8)
                print("  [INFO] Selected Year To Date from dropdown")
                return True
            except Exception:
                continue

        js_result = driver.execute_script(
            "var wanted = ['year to date', 'year to date range'];"
            "var nodes = document.querySelectorAll('li, a, span, div');"
            "for (var i = 0; i < nodes.length; i++) {"
            "  var node = nodes[i];"
            "  var text = (node.innerText || node.textContent || '').trim().toLowerCase();"
            "  if (!text) continue;"
            "  for (var j = 0; j < wanted.length; j++) {"
            "    if (text === wanted[j] || text.indexOf(wanted[j]) !== -1) { node.click(); return true; }"
            "  }"
            "}"
            "return false;"
        )
        if js_result:
            time.sleep(0.8)
            print("  [INFO] Selected Year To Date via JS fallback")
            return True

    date_range = year_to_date_range()
    input_locators = [
        (By.XPATH, "//td[contains(normalize-space(.),'Date Range')]/following-sibling::td//input[1]"),
        (By.XPATH, "//*[contains(normalize-space(.),'Date Range')]/following::input[1]"),
        (By.XPATH, "//input[contains(@id,'DateRange') or contains(@name,'DateRange')]"),
        (By.XPATH, "//input[@type='text' and contains(@value,'/') and contains(@value,'-')]") ,
    ]
    for locator in input_locators:
        try:
            date_input = WebDriverWait(driver, 6).until(
                EC.visibility_of_element_located(locator)
            )
            scroll_to(driver, date_input)
            driver.execute_script(
                "arguments[0].focus();"
                "arguments[0].value = arguments[1];"
                "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));"
                "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));"
                "arguments[0].blur();",
                date_input,
                date_range,
            )
            time.sleep(0.8)
            current_value = (date_input.get_attribute("value") or "").strip()
            if current_value == date_range:
                print(f"  [INFO] Date Range textbox set to {date_range}")
                return True
        except Exception:
            continue

    return False


def click_show_report(driver):
    """Click Show Report button."""
    show_report_btn = safe_click_first(
        driver,
        [
            (By.ID, "ShowReport"),
            (By.NAME, "ShowReport"),
            (By.XPATH, "//button[contains(text(),'Show Report')]"),
            (By.XPATH, "//a[normalize-space()='Show Report' or .//*[normalize-space()='Show Report']]") ,
            (By.XPATH, "//*[contains(@class,'btn') and (.//*[normalize-space()='Show Report'] or normalize-space()='Show Report')]") ,
            (By.XPATH, "//input[@type='submit' and contains(@value,'Show Report')]"),
        ],
        timeout=5,
    )

    if show_report_btn:
        scroll_to(driver, show_report_btn)
        driver.execute_script("arguments[0].click();", show_report_btn)
        print("  [INFO] Show Report button clicked via safe_click_first.")
        return

    result = driver.execute_script(
        "var wanted = arguments[0].trim().toLowerCase();"
        "var nodes = document.querySelectorAll('a, button, span, div');"
        "for (var i = 0; i < nodes.length; i++) {"
        "  var node = nodes[i];"
        "  var txt = (node.innerText || node.textContent || node.value || '').trim().toLowerCase();"
        "  if (!txt || txt !== wanted) continue;"
        "  var clickable = node.closest('a,button,[role=button],input[type=submit],input[type=button]') || node;"
        "  if (clickable.offsetParent !== null) { clickable.click(); return true; }"
        "}"
        "return false;",
        "Show Report",
    )
    assert result, "Show Report button not found"
    print("  [INFO] Show Report button clicked via JS fallback.")


def click_change_filter(driver):
    """Click Change Filter button with Back fallback."""
    change_filter_btn = safe_click_first(
        driver,
        [
            (By.ID, "ChangeFilter"),
            (By.NAME, "ChangeFilter"),
            (By.XPATH, "//button[contains(text(),'Change Filter')]"),
            (By.XPATH, "//input[@type='submit' and contains(@value,'Change Filter')]"),
        ],
        timeout=5,
    )

    if change_filter_btn:
        scroll_to(driver, change_filter_btn)
        change_filter_btn.click()
        print("  [INFO] Change Filter button clicked via safe_click_first.")
        return

    result = click_visible_text(driver, "Change Filter")
    if result:
        print("  [INFO] Change Filter button clicked via JS fallback.")
        return

    result = click_visible_text(driver, "Back")
    assert result, "Change Filter/Back button not found"
    print("  [INFO] Back button clicked as fallback.")


# ============================================================================
# TEST CLASS
# ============================================================================


@pytest.mark.usefixtures("driver")
class TestUserAuditingReport:
    """Test User Auditing Report from Admin Reports."""

    def test_flow_login_show_change_filter(self, driver):
        """Complete flow: login -> open report -> set filters -> show report -> change filter."""
        print("\n" + "=" * 70)
        print("[TC-UAR-001] User Auditing Report - Login & Filter Flow")
        print("=" * 70)

        print("\n[STEP 1] Logging in to QA site...")
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

        print("\n[STEP 2] Opening User Auditing Report filter page...")
        navigate_to_user_auditing_report(driver)

        take_screenshot(driver, "02_filter_page")
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        assert (
            "auditingreportfilter" in driver.current_url.lower()
            or "auditing report" in page_text
        ), f"Expected User Auditing filter page. Got: {driver.current_url}"
        print(f"  [PASS] User Auditing filter page loaded: {driver.current_url}")

        print("\n[STEP 3] Ensuring table = EboUser...")
        ensure_ebouser_selected(driver)
        take_screenshot(driver, "03_table_selected")

        print("\n[STEP 4] Selecting Date Range = Year To Date...")
        selected = select_year_to_date(driver)
        assert selected, "Could not set Date Range to Year To Date"
        take_screenshot(driver, "04_date_range_selected")
        print("  [PASS] Date Range configured.")

        print("\n[STEP 5] Clicking 'Show Report' button...")
        click_show_report(driver)
        wait_ready(driver)
        time.sleep(PAUSE)
        take_screenshot(driver, "05_after_show_report")
        current_url = driver.current_url
        print(f"  [URL] {current_url}")

        print("\n[STEP 6] Verifying report output...")
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        report_loaded = (
            "auditing report" in page_text
            and "ebouser" in page_text
            and "change filter" in page_text
        )
        assert report_loaded, f"Report may not have loaded correctly. URL: {current_url}"
        print("  [PASS] User Auditing report output loaded.")

        print("\n[STEP 7] Clicking 'Change Filter' button...")
        click_change_filter(driver)
        wait_ready(driver)
        time.sleep(PAUSE)
        take_screenshot(driver, "06_after_change_filter")
        current_url = driver.current_url
        print(f"  [URL] {current_url}")

        print("\n[STEP 8] Verifying return to filter page...")
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        filter_restored = (
            "auditingreportfilter" in current_url.lower()
            and "show report" in page_text
        )
        assert filter_restored, (
            f"Did not return to filter page. Expected URL containing 'AuditingReportFilter'. "
            f"Got: {current_url}"
        )
        print(f"  [PASS] Returned to User Auditing filter page: {current_url}")

        print("\n" + "=" * 70)
        print("[RESULT] All steps completed successfully!")
        print("=" * 70 + "\n")