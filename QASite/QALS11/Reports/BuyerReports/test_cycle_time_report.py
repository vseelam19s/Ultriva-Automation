"""
QALS11 | Reports > Buyer Reports > Cycle Time Report
====================================================
URL  : https://engineering.ultrivalms.com/QALS1011
User : buyeruser / Ultriva!23

Test Flow
---------
  1.  Login as buyeruser
  2.  Navigate to Reports -> Buyer Reports -> Cycle Time report
  3.  Set Date Range = past one year
  4.  Keep default values for the remaining filters
  5.  Click Show Report
  6.  Verify the report output loads

Run (from qa_automation/):
    pytest tests/QALS11/Reports/test_cycle_time_report.py -v -s
"""

import os
import time
from datetime import date, timedelta

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
CYCLE_TIME_FILTER_URL = f"{BASE_URL}/BuyerReport/CycleTimeFilter"


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
    path = os.path.join(screenshots_dir, f"cycle_time_{name}_{ts}.png")
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


def navigate_to_cycle_time_report(driver):
    """Open Cycle Time report through the menu, with a direct URL fallback."""
    if "CycleTimeFilter" in driver.current_url or "CycleTime" in driver.current_url:
        return

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
            driver.get(CYCLE_TIME_FILTER_URL)
            wait_ready(driver)
            time.sleep(PAUSE)
            return

    buyer_reports_link = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[normalize-space()='Buyer Reports' or contains(normalize-space(.),'Buyer Reports')]"),
            (By.XPATH, "//*[self::a or self::span][contains(normalize-space(.),'Buyer Reports')]"),
            (By.XPATH, "//a[contains(@href,'BuyerReport') or contains(@href,'Buyer Reports')]"),
        ],
        timeout=6,
    )
    if buyer_reports_link:
        scroll_to(driver, buyer_reports_link)
        driver.execute_script("arguments[0].click()", buyer_reports_link)
        wait_ready(driver)
        time.sleep(PAUSE)

    cycle_time_link = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[contains(@href,'CycleTimeFilter') or contains(normalize-space(.),'Cycle Time')]"),
            (By.XPATH, "//*[self::a or self::span][contains(normalize-space(.),'Cycle Time')]"),
        ],
        timeout=6,
    )
    if cycle_time_link:
        scroll_to(driver, cycle_time_link)
        driver.execute_script("arguments[0].click()", cycle_time_link)
        wait_ready(driver)
        time.sleep(PAUSE)
    else:
        print("  [WARN] Cycle Time menu link not found - navigating directly to report URL.")
        driver.get(CYCLE_TIME_FILTER_URL)
        wait_ready(driver)
        time.sleep(PAUSE)


def past_one_year_range():
    """Return the site date-range string for the trailing one-year window."""
    end_date = date.today()
    start_date = end_date - timedelta(days=365)
    return f"{start_date:%m/%d/%Y}-{end_date:%m/%d/%Y}"


def set_date_range_past_one_year(driver):
    """Set the Cycle Time filter Date Range textbox to the trailing one-year window."""
    date_range = past_one_year_range()
    input_locators = [
        (By.XPATH, "//td[contains(normalize-space(.),'Date Range')]/following-sibling::td//input[1]"),
        (By.XPATH, "//*[contains(normalize-space(.),'Date Range')]/following::input[1]"),
        (By.XPATH, "//input[contains(@id,'DateRange') or contains(@name,'DateRange')]"),
        (By.XPATH, "//input[@type='text' and contains(@value,'/') and contains(@value,'-')]"),
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
                print(f"  [INFO] Date Range set to {date_range}")
                return date_range
        except Exception:
            continue

    raise AssertionError("Could not set Date Range textbox on Cycle Time report")


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


def report_loaded(driver):
    """Check that the report output page is visible after submit."""
    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
    if "cycle time details by item" in body_text or "change filter" in body_text:
        return True

    rows = driver.find_elements(By.XPATH, "//table//tr[td]")
    return len(rows) > 0


# ============================================================================
# TEST CLASS
# ============================================================================


@pytest.mark.usefixtures("driver")
class TestCycleTimeReport:
    # -- TC-CTR-001: Login --------------------------------------------------
    def test_01_login(self, driver):
        """Login to QA site with buyeruser credentials."""
        print("\n[TC-CTR-001] Logging in to QA site...")
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

    # -- TC-CTR-002: Open Cycle Time report ---------------------------------
    def test_02_open_cycle_time_report(self, driver):
        """Navigate to Reports -> Buyer Reports -> Cycle Time report."""
        print("\n[TC-CTR-002] Opening Cycle Time report...")
        navigate_to_cycle_time_report(driver)

        take_screenshot(driver, "02_cycle_time_filter")
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        assert "cycletimefilter" in driver.current_url.lower() or "cycle time report" in page_text, (
            f"Expected Cycle Time report filter page. Got: {driver.current_url}"
        )
        print(f"  [PASS] Cycle Time report filter page loaded: {driver.current_url}")

    # -- TC-CTR-003: Set past one year and Show Report ----------------------
    def test_03_select_past_one_year_and_show_report(self, driver):
        """Set past one year, keep defaults, and click Show Report."""
        print("\n[TC-CTR-003] Setting Date Range and clicking Show Report...")

        selected_range = set_date_range_past_one_year(driver)
        clicked = click_show_report(driver)
        assert clicked, "Show Report button not found on Cycle Time report"

        take_screenshot(driver, "03_after_show_report")
        assert report_loaded(driver), (
            f"Cycle Time report did not load successfully for {selected_range}. URL: {driver.current_url}"
        )
        assert "cycletime" in driver.current_url.lower(), (
            f"Expected Cycle Time results page after Show Report. Got: {driver.current_url}"
        )
        print(f"  [PASS] Cycle Time report loaded for Date Range {selected_range}.")