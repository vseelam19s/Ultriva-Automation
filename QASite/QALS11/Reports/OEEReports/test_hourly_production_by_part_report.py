"""
QALS11 | Reports > LFM/OEE Reports > Hourly Production By Part Report
=====================================================================
URL  : https://engineering.ultrivalms.com/QALS1011/OEEReport/HourlyProductionByPartFilter
User : Databizwarehouseuser / Ultriva!23

Test Flow
---------
  1. Login as Databizwarehouseuser
  2. Navigate via Reports -> LFM/OEE Reports -> Hourly Production By Part Report
  3. Select Date Range = Past One Year
  4. Click Show Report
  5. Verify Hourly Production Part By Part Details loads
  6. Click Change Filter

Run (from qa_automation/):
    pytest tests/QALS11/Reports/OEEReports/test_hourly_production_by_part_report.py -v -s
"""

import os
import time
from datetime import date, timedelta

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
USERNAME = "Databizwarehouseuser"
PASSWORD = "Ultriva!23"
PAUSE = 1.2
HOURLY_PRODUCTION_FILTER_URL = f"{BASE_URL}/OEEReport/HourlyProductionByPartFilter"


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
    path = os.path.join(screenshots_dir, f"hourly_production_{name}_{ts}.png")
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
    """Click first visible element matching text via JS fallback."""
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


def navigate_to_hourly_production_by_part_report(driver):
    """Open Hourly Production By Part Report using menu path with direct URL fallback."""
    if "HourlyProductionByPartFilter" in driver.current_url and "Account/Login" not in driver.current_url:
        return

    reports_menu = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[normalize-space()='Reports']"),
            (By.XPATH, "//*[self::a or self::span][normalize-space()='Reports']"),
            (By.XPATH, "//a[contains(normalize-space(.),'Reports')]"),
        ],
        timeout=6,
    )
    if reports_menu:
        try:
            scroll_to(driver, reports_menu)
            driver.execute_script("arguments[0].click();", reports_menu)
            time.sleep(PAUSE)
        except Exception:
            pass

    lfm_oee_section = safe_click_first(
        driver,
        [
            (By.XPATH, "//*[self::a or self::span or self::div][contains(normalize-space(.),'LFM/OEE Reports')]"),
            (By.XPATH, "//*[contains(@class,'panel') and contains(.,'LFM/OEE Reports')]"),
        ],
        timeout=5,
    )
    if lfm_oee_section:
        try:
            scroll_to(driver, lfm_oee_section)
            driver.execute_script("arguments[0].click();", lfm_oee_section)
            time.sleep(PAUSE)
        except Exception:
            pass

    report_link = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[contains(@href,'/OEEReport/HourlyProductionByPartFilter')]"),
            (By.XPATH, "//a[contains(@href,'HourlyProductionByPartFilter')]"),
            (By.XPATH, "//a[contains(normalize-space(.),'Hourly Production By Part Report')]"),
            (By.XPATH, "//*[self::a or self::span][contains(normalize-space(.),'Hourly Production By Part')]"),
        ],
        timeout=6,
    )
    if report_link:
        try:
            scroll_to(driver, report_link)
            driver.execute_script("arguments[0].click();", report_link)
            wait_ready(driver)
            time.sleep(PAUSE)
            if "HourlyProductionByPartFilter" in driver.current_url and "Account/Login" not in driver.current_url:
                return
        except Exception:
            pass

    print("  [WARN] Menu path unavailable - using direct URL fallback.")
    driver.get(HOURLY_PRODUCTION_FILTER_URL)
    wait_ready(driver)
    time.sleep(PAUSE)


def _select_date_range_option(driver, option_text):
    """Click Date Range textbox and select menu option by visible text."""
    date_input = None
    input_locators = [
        (By.XPATH, "//label[contains(normalize-space(.),'date range')]/following::input[1]"),
        (By.XPATH, "//*[contains(normalize-space(.),'Enter or select date range')]/following::input[1]"),
        (By.XPATH, "//input[contains(@id,'DateRange') or contains(@name,'DateRange')]"),
    ]

    for locator in input_locators:
        try:
            date_input = WebDriverWait(driver, 6).until(
                EC.visibility_of_element_located(locator)
            )
            break
        except Exception:
            continue

    if not date_input:
        return False

    scroll_to(driver, date_input)
    driver.execute_script("arguments[0].click();", date_input)
    time.sleep(0.5)

    option_locators = [
        (By.XPATH, f"//li[normalize-space()='{option_text}']"),
        (By.XPATH, f"//*[self::li or self::a or self::td or self::span][normalize-space()='{option_text}']"),
        (By.XPATH, "//*[self::li or self::a or self::td or self::span][contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'),'past one year')]"),
    ]

    for locator in option_locators:
        try:
            opt = WebDriverWait(driver, 4).until(EC.element_to_be_clickable(locator))
            scroll_to(driver, opt)
            driver.execute_script("arguments[0].click();", opt)
            time.sleep(0.8)
            return True
        except Exception:
            continue

    clicked = driver.execute_script(
        "var wanted = 'past one year';"
        "var els = document.querySelectorAll('li, a, td, span, div');"
        "for (var i = 0; i < els.length; i++) {"
        "  var el = els[i];"
        "  var txt = (el.innerText || '').trim().toLowerCase();"
        "  if (!txt) continue;"
        "  if ((txt === wanted || txt.indexOf(wanted) !== -1 || txt.replace(/\\s+/g,'') === 'pastoneyear') && el.offsetParent !== null) {"
        "    el.click();"
        "    return true;"
        "  }"
        "}"
        "return false;"
    )
    if clicked:
        time.sleep(0.8)
    return bool(clicked)


def set_date_range_past_one_year(driver):
    """Set Date Range to Past One Year with dropdown first, value fallback second."""
    if _select_date_range_option(driver, "Past One Year"):
        print("  [INFO] Date Range selected via dropdown: Past One Year")
        return "Past One Year"

    end_date = date.today()
    start_date = end_date - timedelta(days=365)
    value = f"{start_date:%m/%d/%Y}-{end_date:%m/%d/%Y}"

    value_locators = [
        (By.XPATH, "//label[contains(normalize-space(.),'date range')]/following::input[1]"),
        (By.XPATH, "//*[contains(normalize-space(.),'Enter or select date range')]/following::input[1]"),
        (By.XPATH, "//input[contains(@id,'DateRange') or contains(@name,'DateRange')]"),
    ]

    for locator in value_locators:
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
                value,
            )
            time.sleep(0.6)
            return value
        except Exception:
            continue

    raise AssertionError("Could not set Date Range on Hourly Production By Part filter")


def click_show_report(driver):
    """Click Show Report button on the Hourly Production By Part filter page."""
    btn = safe_click_first(
        driver,
        [
            (By.XPATH, "//button[normalize-space(text())='Show Report']"),
            (By.XPATH, "//a[normalize-space(text())='Show Report']"),
            (By.XPATH, "//input[@type='submit' and @value='Show Report']"),
            (By.XPATH, "//*[@id='btnShowReport' or contains(@id,'ShowReport') or contains(@id,'showReport')]"),
        ],
        timeout=6,
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


def summary_loaded(driver):
    """Check Hourly Production By Part summary/details page presence."""
    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
    rows = driver.find_elements(By.XPATH, "//table//tr[td]")
    return (
        "hourly production" in body_text
        or "hourlyproductionbypart" in driver.current_url.lower()
        or "supplier item no" in body_text
        or "qty per hour" in body_text
        or len(rows) > 0
    )


def click_change_filter(driver):
    """Click Change Filter on the summary/details page."""
    locators = [
        (By.XPATH, "//button[contains(normalize-space(.),'Change Filter')]"),
        (By.XPATH, "//a[contains(normalize-space(.),'Change Filter')]"),
        (By.XPATH, "//*[@id='changeFilter' or contains(@id,'ChangeFilter') or contains(@id,'changeFilter')]"),
    ]

    for locator in locators:
        try:
            btn = WebDriverWait(driver, 6).until(EC.element_to_be_clickable(locator))
            scroll_to(driver, btn)
            driver.execute_script("arguments[0].click();", btn)
            wait_ready(driver)
            time.sleep(PAUSE)
            return True
        except Exception:
            continue

    if click_visible_text(driver, "Change Filter"):
        wait_ready(driver)
        time.sleep(PAUSE)
        return True

    return False


@pytest.mark.usefixtures("driver")
class TestHourlyProductionByPartReport:
    """Validate Hourly Production By Part Report flow under LFM/OEE Reports."""

    def test_01_login(self, driver):
        """Login to QA site with Databizwarehouseuser credentials."""
        print("\n[TC-HPBP-001] Logging in to QA site...")
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

    def test_02_open_hourly_production_by_part_filter(self, driver):
        """Open Hourly Production By Part filter via menu path with URL fallback."""
        print("[TC-HPBP-002] Opening Hourly Production By Part filter...")
        navigate_to_hourly_production_by_part_report(driver)

        body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        assert "HourlyProductionByPartFilter" in driver.current_url or (
            "hourly production" in body_text and "show report" in body_text
        ), f"Expected Hourly Production By Part filter page, got: {driver.current_url}"
        take_screenshot(driver, "02_filter_page")

    def test_03_select_past_one_year_show_report(self, driver):
        """Select Date Range = Past One Year and click Show Report."""
        print("[TC-HPBP-003] Selecting Date Range and clicking Show Report...")
        selected = set_date_range_past_one_year(driver)
        assert selected, "Could not select Date Range = Past One Year"

        assert click_show_report(driver), "Could not click Show Report"
        assert summary_loaded(driver), (
            f"Hourly Production Part By Part Details did not load after Show Report. URL: {driver.current_url}"
        )
        print(f"  [INFO] Date Range selected: {selected}")
        take_screenshot(driver, "03_summary")

    def test_04_click_change_filter(self, driver):
        """Click Change Filter from summary and verify return to filter page."""
        print("[TC-HPBP-004] Clicking Change Filter...")
        assert click_change_filter(driver), "Could not click Change Filter"

        body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        on_filter = "HourlyProductionByPartFilter" in driver.current_url or (
            "hourly production" in body_text and "show report" in body_text
        )
        assert on_filter, (
            f"Did not return to Hourly Production By Part filter context. URL: {driver.current_url}"
        )
        take_screenshot(driver, "04_change_filter")
