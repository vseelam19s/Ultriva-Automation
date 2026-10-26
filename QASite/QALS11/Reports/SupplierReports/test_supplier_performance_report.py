"""
QALS11 | Reports > Supplier Reports > Supplier Performance Report
=================================================================
URL  : https://engineering.ultrivalms.com/QALS1011
User : supnewuser / Ultriva!23

Test Flow
---------
    1. Login as supnewuser
  2. Switch Application to Supplier
  3. Navigate to Reports -> Supplier Performance Report
  4. Set Date Range as Past One Year and keep default values
  5. Click Show Report and verify Supplier Performance By Plant data
  6. Click plant link "TCEK-Ram" and verify Supplier Performance By Item No data
  7. Click any Item No and verify Suppliers Performance Report By CardID data
  8. Click Back to Summary
  9. Click Change Filter and verify return to report filter page

Run (from qa_automation/):
    pytest tests/QALS11/Reports/SupplierReports/test_supplier_performance_report.py -v -s
"""

import datetime as dt
import os
import time

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
USERNAME = "supnewuser"
PASSWORD = "Ultriva!23"
PAUSE = 1.2

SUPPLIER_PERF_FILTER_URL = (
    "https://engineering.ultrivalms.com/QALS1011/SupplierReport/SuppliersPerformanceFilter"
)


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


def take_screenshot(driver, name):
    screenshots_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "..", "reports", "screenshots"
    )
    os.makedirs(screenshots_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(screenshots_dir, f"supplier_performance_supplier_{name}_{ts}.png")
    driver.save_screenshot(path)
    print(f"  [screenshot] {path}")
    return path


def switch_application_to_supplier(driver):
    """Switch the top application selector to Supplier context."""
    body_text = driver.find_element(By.TAG_NAME, "body").text
    if "Application (Supplier)" in body_text:
        return True

    select_locators = [
        (By.XPATH, "//label[contains(normalize-space(.),'Application')]/following::select[1]"),
        (By.XPATH, "//select[contains(@id,'Application') or contains(@name,'Application')]"),
    ]
    for by, locator in select_locators:
        try:
            sel_el = WebDriverWait(driver, 6).until(
                EC.presence_of_element_located((by, locator))
            )
            sel = Select(sel_el)
            for option in sel.options:
                if "supplier" in option.text.lower():
                    sel.select_by_visible_text(option.text)
                    wait_ready(driver)
                    time.sleep(PAUSE)
                    body = driver.find_element(By.TAG_NAME, "body").text
                    return "Application (Supplier)" in body or "Supplier" in option.text
        except Exception:
            continue

    # Custom dropdown fallback
    app_dropdown = safe_click_first(
        driver,
        [
            (By.XPATH, "//*[contains(normalize-space(.),'Application')]/following::*[contains(@class,'select2') or contains(@class,'dropdown')][1]"),
            (By.XPATH, "//span[contains(normalize-space(.),'Application')]/following::span[1]"),
        ],
        timeout=5,
    )
    if app_dropdown:
        scroll_to(driver, app_dropdown)
        driver.execute_script("arguments[0].click();", app_dropdown)
        time.sleep(0.5)

        supplier_option = safe_click_first(
            driver,
            [
                (By.XPATH, "//*[self::li or self::a or self::div or self::span][contains(normalize-space(.),'Supplier')]"),
            ],
            timeout=5,
        )
        if supplier_option:
            driver.execute_script("arguments[0].click();", supplier_option)
            wait_ready(driver)
            time.sleep(PAUSE)

    body_text = driver.find_element(By.TAG_NAME, "body").text
    return "Application (Supplier)" in body_text or "Application" in body_text and "Supplier" in body_text


def navigate_to_supplier_performance_filter(driver):
    """Open Supplier Performance report via menu path, with direct URL fallback."""
    if "SuppliersPerformanceFilter" in driver.current_url:
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
            driver.execute_script("arguments[0].click();", reports_link)
            wait_ready(driver)
            time.sleep(PAUSE)
        except Exception:
            pass

    perf_link = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[contains(@href,'SuppliersPerformanceFilter')]"),
            (By.XPATH, "//a[contains(@href,'SuppliersPerformance')]"),
            (By.XPATH, "//a[normalize-space()='Supplier Performance Report']"),
            (By.XPATH, "//a[contains(normalize-space(.),'Supplier Performance')]"),
            (By.XPATH, "//*[self::a or self::span][contains(normalize-space(.),'Supplier Performance')]"),
        ],
        timeout=6,
    )
    if perf_link:
        scroll_to(driver, perf_link)
        driver.execute_script("arguments[0].click();", perf_link)
        wait_ready(driver)
        time.sleep(PAUSE)

    if "SuppliersPerformanceFilter" in driver.current_url:
        return

    # If report summary opened directly, use Change Filter to go to filter page.
    if "SuppliersPerformance" in driver.current_url and "Filter" not in driver.current_url:
        if click_change_filter(driver):
            wait_ready(driver)
            time.sleep(PAUSE)

    if "SuppliersPerformanceFilter" in driver.current_url:
        return

    driver.get(SUPPLIER_PERF_FILTER_URL)
    wait_ready(driver)
    time.sleep(PAUSE)


def ensure_filter_page(driver):
    """Ensure Supplier Performance filter context is open."""
    if "SuppliersPerformanceFilter" in driver.current_url:
        return True

    has_date_range = False
    has_show = False

    try:
        find(
            driver,
            By.XPATH,
            "//label[contains(.,'Date Range')]/following::input[1] | //input[contains(@id,'DateRange') or contains(@name,'DateRange')] | //select[contains(@id,'DateRange') or contains(@name,'DateRange')]",
            timeout=5,
        )
        has_date_range = True
    except Exception:
        pass

    try:
        safe_click_first(
            driver,
            [
                (By.XPATH, "//button[contains(normalize-space(.),'Show Report')]"),
                (By.XPATH, "//a[contains(normalize-space(.),'Show Report')]"),
                (By.XPATH, "//input[@type='submit' and contains(@value,'Show Report')]"),
                (By.XPATH, "//*[@id='btnSubmit' or contains(@id,'ShowReport') or contains(@id,'showReport')]"),
            ],
            timeout=3,
        )
        has_show = True
    except Exception:
        pass

    return has_date_range and has_show


def set_date_range_past_one_year(driver):
    """Set Date Range to Past One Year with robust handling for select or text input."""
    # 1) Dropdown/select option path
    select_locators = [
        (By.ID, "DateRange"),
        (By.NAME, "DateRange"),
        (By.XPATH, "//select[contains(@id,'DateRange') or contains(@name,'DateRange')]"),
    ]
    for by, locator in select_locators:
        try:
            sel_el = WebDriverWait(driver, 4).until(
                EC.presence_of_element_located((by, locator))
            )
            sel = Select(sel_el)
            for option in sel.options:
                if "past one year" in option.text.lower():
                    sel.select_by_visible_text(option.text)
                    time.sleep(0.6)
                    return True
        except Exception:
            continue

    # 2) Try opening custom date range menu and click "Past One Year"
    trigger = safe_click_first(
        driver,
        [
            (By.XPATH, "//label[contains(.,'Date Range')]/following::input[1]"),
            (By.XPATH, "//input[contains(@id,'DateRange') or contains(@name,'DateRange')]"),
            (By.XPATH, "//*[contains(normalize-space(.),'Date Range')]/following::input[1]"),
        ],
        timeout=5,
    )
    if trigger:
        scroll_to(driver, trigger)
        try:
            trigger.click()
        except Exception:
            driver.execute_script("arguments[0].click();", trigger)
        time.sleep(0.8)

        option = safe_click_first(
            driver,
            [
                (By.XPATH, "//*[self::li or self::a or self::span or self::div][normalize-space(.)='Past One Year']"),
                (By.XPATH, "//*[self::li or self::a or self::span or self::div][contains(normalize-space(.),'Past One Year')]"),
            ],
            timeout=4,
        )
        if option:
            driver.execute_script("arguments[0].click();", option)
            time.sleep(0.7)
            return True

    # 3) Text range path: set MM/DD/YYYY-MM/DD/YYYY for trailing 365 days
    end_date = dt.date.today()
    start_date = end_date - dt.timedelta(days=365)
    range_value = f"{start_date:%m/%d/%Y}-{end_date:%m/%d/%Y}"

    input_locators = [
        (By.ID, "DateRange"),
        (By.NAME, "DateRange"),
        (By.XPATH, "//label[contains(.,'Date Range')]/following::input[1]"),
        (By.XPATH, "//input[contains(@id,'DateRange') or contains(@name,'DateRange') or contains(@placeholder,'Date')]"),
    ]
    for by, locator in input_locators:
        try:
            inp = WebDriverWait(driver, 4).until(
                EC.presence_of_element_located((by, locator))
            )
            scroll_to(driver, inp)
            driver.execute_script(
                "arguments[0].value = arguments[1];"
                "arguments[0].dispatchEvent(new Event('input', {bubbles: true}));"
                "arguments[0].dispatchEvent(new Event('change', {bubbles: true}));",
                inp,
                range_value,
            )
            time.sleep(0.6)
            val = inp.get_attribute("value") or ""
            if end_date.strftime("%m/%d/%Y") in val:
                return True
        except Exception:
            continue

    return False


def click_show_report(driver):
    """Click Show Report on filter page."""
    btn = safe_click_first(
        driver,
        [
            (By.XPATH, "//button[normalize-space()='Show Report']"),
            (By.XPATH, "//a[normalize-space()='Show Report']"),
            (By.XPATH, "//input[@type='submit' and @value='Show Report']"),
            (By.XPATH, "//*[@id='btnSubmit' or contains(@id,'ShowReport') or contains(@id,'showReport')]"),
            (By.XPATH, "//*[contains(normalize-space(.),'Show Report') and (contains(@class,'btn') or contains(@class,'button'))]"),
        ],
        timeout=8,
    )
    if btn:
        scroll_to(driver, btn)
        driver.execute_script("arguments[0].click();", btn)
        wait_ready(driver)
        time.sleep(PAUSE * 1.5)
        return True

    if click_visible_text(driver, "Show Report"):
        wait_ready(driver)
        time.sleep(PAUSE * 1.5)
        return True

    return False


def click_change_filter(driver):
    """Click Change Filter button if present."""
    btn = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[contains(normalize-space(.),'Change Filter')]"),
            (By.XPATH, "//button[contains(normalize-space(.),'Change Filter')]"),
            (By.XPATH, "//input[@type='button' and contains(@value,'Change Filter')]"),
            (By.XPATH, "//*[contains(@id,'changeFilter') or contains(@id,'ChangeFilter')]"),
        ],
        timeout=6,
    )
    if btn:
        scroll_to(driver, btn)
        try:
            btn.click()
        except Exception:
            driver.execute_script("arguments[0].click();", btn)
        return True

    return click_visible_text(driver, "Change Filter") is not None


def click_back_to_summary(driver):
    """Click Back to Summary button if present."""
    btn = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[contains(normalize-space(.),'Back to Summary')]"),
            (By.XPATH, "//button[contains(normalize-space(.),'Back to Summary')]"),
            (By.XPATH, "//input[@type='button' and contains(@value,'Back to Summary')]"),
            (By.XPATH, "//*[contains(@id,'backToSummary') or contains(@class,'back-summary')]"),
        ],
        timeout=8,
    )
    if btn:
        scroll_to(driver, btn)
        try:
            btn.click()
        except Exception:
            driver.execute_script("arguments[0].click();", btn)
        return True

    return click_visible_text(driver, "Back to Summary") is not None


def has_table_data_rows(driver, min_rows=1):
    """Return True when at least min_rows body rows with data cells exist."""
    rows = driver.find_elements(By.XPATH, "//tbody/tr[td]")
    return len(rows) >= min_rows


def get_body_text(driver):
    return (driver.find_element(By.TAG_NAME, "body").text or "").lower()


# ============================================================================
# TEST CLASS
# ============================================================================


@pytest.mark.usefixtures("driver")
class TestSupplierPerformanceReport:
    """End-to-end tests for Supplier Performance report drill-down flow."""

    def test_01_login_and_switch_to_supplier_application(self, driver):
        """Login and switch application context to Supplier."""
        print("\n[test_01_login_and_switch_to_supplier_application] Logging in...")
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

        assert "Account/Login" not in driver.current_url, (
            f"Login failed - still on login page. URL: {driver.current_url}"
        )

        switched = switch_application_to_supplier(driver)
        take_screenshot(driver, "01_after_login_and_app_switch")
        assert switched, "Failed to switch application context to Supplier"
        print(f"  [PASS] Logged in and switched to Supplier. URL: {driver.current_url}")

    def test_02_open_supplier_performance_filter(self, driver):
        """Open Supplier Performance report filter page."""
        print("\n[test_02_open_supplier_performance_filter] Opening filter page...")
        navigate_to_supplier_performance_filter(driver)

        # If page opened as summary, force return to filter.
        if "SuppliersPerformance" in driver.current_url and "Filter" not in driver.current_url:
            clicked = click_change_filter(driver)
            if clicked:
                wait_ready(driver)
                time.sleep(PAUSE)

        take_screenshot(driver, "02_filter_page")
        assert ensure_filter_page(driver), (
            f"Supplier Performance filter page not loaded. URL: {driver.current_url}"
        )
        print(f"  [PASS] Filter page loaded. URL: {driver.current_url}")

    def test_03_set_past_one_year_and_show_report(self, driver):
        """Set date range as past one year and open By Plant report."""
        print("\n[test_03_set_past_one_year_and_show_report] Setting date range and showing report...")

        if not ensure_filter_page(driver):
            navigate_to_supplier_performance_filter(driver)
            assert ensure_filter_page(driver), "Unable to reach Supplier Performance filter page"

        set_ok = set_date_range_past_one_year(driver)
        assert set_ok, "Could not set Date Range to Past One Year"

        shown = click_show_report(driver)
        assert shown, "Show Report button not found/clickable"

        take_screenshot(driver, "03_by_plant_report")
        body = get_body_text(driver)
        assert (
            "supplier performance by plant" in body
            or ("suppliersperformance" in driver.current_url.lower() and "filter" not in driver.current_url.lower())
        ), f"By Plant report context not detected. URL: {driver.current_url}"
        assert has_table_data_rows(driver, min_rows=1), "By Plant report has no data rows"
        print(f"  [PASS] By Plant report loaded with data. URL: {driver.current_url}")

    def test_04_click_plant_tcek_ram_and_verify_item_report(self, driver):
        """Click plant link TCEK-Ram and verify By Item report with data."""
        print("\n[test_04_click_plant_tcek_ram_and_verify_item_report] Clicking TCEK-Ram...")

        plant_link = safe_click_first(
            driver,
            [
                (By.XPATH, "//tbody//tr//td//a[normalize-space()='TCEK-Ram']"),
                (By.XPATH, "//a[normalize-space()='TCEK-Ram']"),
                (By.XPATH, "//tbody//tr//td//a[contains(normalize-space(.),'TCEK-Ram')]"),
            ],
            timeout=10,
        )
        assert plant_link is not None, "Plant link 'TCEK-Ram' not found on By Plant report"

        scroll_to(driver, plant_link)
        try:
            plant_link.click()
        except Exception:
            driver.execute_script("arguments[0].click();", plant_link)

        wait_ready(driver)
        time.sleep(PAUSE)

        take_screenshot(driver, "04_by_item_report")
        body = get_body_text(driver)
        assert (
            "supplier performance by item no" in body
            or "suppliersperformancedetails" in driver.current_url.lower()
        ), f"By Item report context not detected. URL: {driver.current_url}"
        assert has_table_data_rows(driver, min_rows=1), "By Item report has no data rows"
        print(f"  [PASS] By Item report loaded with data. URL: {driver.current_url}")

    def test_05_click_any_item_and_verify_cardid_report(self, driver):
        """Click first available item number and verify CardID report data."""
        print("\n[test_05_click_any_item_and_verify_cardid_report] Clicking first item...")

        def click_item_candidate(index=0):
            raw_links = driver.find_elements(
                By.XPATH,
                "//tbody//tr[td]/td[1]//a[normalize-space()!=''] | //table//tr[td]/td[1]//a[normalize-space()!='']",
            )
            if not raw_links:
                return None

            blocked = {
                "item",
                "cards to be shipped",
                "shipped cards",
                "shipped cards on time",
                "partially shipped cards",
                "delivery performance",
                "suggestion",
                "total",
            }

            valid = []
            for ln in raw_links:
                txt = (ln.text or ln.get_attribute("innerText") or "").strip()
                low = txt.lower()
                if not txt or low in blocked:
                    continue
                # Item codes are typically compact tokens; avoid human-readable metric labels.
                if " " in txt and not any(ch.isdigit() for ch in txt):
                    continue
                valid.append((txt, ln))

            if not valid:
                return None

            text, pick = valid[min(index, len(valid) - 1)]
            scroll_to(driver, pick)
            try:
                pick.click()
            except Exception:
                driver.execute_script("arguments[0].click();", pick)
            return text

        first_text = click_item_candidate(0)
        assert first_text is not None, "No data-row item link found on By Item report"
        print(f"  [INFO] Clicking item: {first_text}")

        wait_ready(driver)
        time.sleep(PAUSE)

        body = get_body_text(driver)
        in_cardid_context = (
            "suppliers performance report by cardid" in body
            or "suppliersperformancedetailsdetails" in driver.current_url.lower()
            or "cardid" in body
        )

        # If still on item summary, retry with the next candidate by re-querying fresh elements.
        if not in_cardid_context:
            second_text = click_item_candidate(1)
            if second_text:
                print(f"  [INFO] First click stayed on item summary; retrying with: {second_text}")
                wait_ready(driver)
                time.sleep(PAUSE)
                body = get_body_text(driver)
                in_cardid_context = (
                    "suppliers performance report by cardid" in body
                    or "suppliersperformancedetailsdetails" in driver.current_url.lower()
                    or "cardid" in body
                )

        take_screenshot(driver, "05_cardid_report")
        assert in_cardid_context, f"CardID report context not detected. URL: {driver.current_url}"
        assert has_table_data_rows(driver, min_rows=1), "CardID report has no data rows"
        print(f"  [PASS] CardID report loaded with data. URL: {driver.current_url}")

    def test_06_back_to_summary_then_change_filter(self, driver):
        """Click Back to Summary, then Change Filter and verify filter page."""
        print("\n[test_06_back_to_summary_then_change_filter] Navigating back via buttons...")

        back_ok = click_back_to_summary(driver)
        assert back_ok, "Back to Summary button not found/clickable"
        wait_ready(driver)
        time.sleep(PAUSE)

        take_screenshot(driver, "06_after_back_to_summary")
        body_after_back = get_body_text(driver)
        assert (
            "supplier performance by item no" in body_after_back
            or "supplier performance by plant" in body_after_back
            or "suppliersperformancedetails" in driver.current_url.lower()
        ), f"Expected summary context after Back to Summary. URL: {driver.current_url}"

        change_ok = click_change_filter(driver)
        assert change_ok, "Change Filter button not found/clickable"
        wait_ready(driver)
        time.sleep(PAUSE)

        take_screenshot(driver, "07_after_change_filter")
        assert ensure_filter_page(driver), (
            f"Did not return to Supplier Performance filter page after Change Filter. URL: {driver.current_url}"
        )
        print(f"  [PASS] Returned to filter page via Change Filter. URL: {driver.current_url}")
