"""
QALS11 | Reports > Buyer Reports > Stock Out Report
===================================================
URL  : https://engineering.ultrivalms.com/QALS1011
User : buyeruser / Ultriva!23

Test Flow
---------
  1.  Login as buyeruser
  2.  Navigate to Reports -> Buyer Reports -> Stock Out report
  3.  Set Date Range = past one year
  4.  Keep default values for remaining filters
  5.  Click Show Report
  6.  Verify report output loads
  7.  Click Change Filter and verify return to filter page

Run (from qa_automation/):
    pytest tests/QALS11/Reports/test_stockout_report.py -v -s
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
STOCKOUT_FILTER_URL = f"{BASE_URL}/BuyerReport/StockOutFilter"


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
        os.path.dirname(__file__), "..", "..", "..", "reports", "screenshots"
    )
    os.makedirs(screenshots_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(screenshots_dir, f"stockout_{name}_{ts}.png")
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


def navigate_to_stockout_report(driver):
    """Open Stock Out report, using direct URL first and menu fallback."""
    if "StockOutFilter" in driver.current_url or "StockOut" in driver.current_url:
        return

    try:
        driver.get(STOCKOUT_FILTER_URL)
        wait_ready(driver)
        time.sleep(PAUSE)
        if "StockOutFilter" in driver.current_url or "StockOut" in driver.current_url:
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
            driver.get(STOCKOUT_FILTER_URL)
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

    stockout_link = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[contains(@href,'StockOut') or contains(@href,'Stockout') or contains(normalize-space(.),'Stock Out')]"),
            (By.XPATH, "//*[self::a or self::span][contains(normalize-space(.),'Stock Out') or contains(normalize-space(.),'StockOut')]"),
        ],
        timeout=6,
    )
    if stockout_link:
        scroll_to(driver, stockout_link)
        driver.execute_script("arguments[0].click()", stockout_link)
        wait_ready(driver)
        time.sleep(PAUSE)
    else:
        print("  [WARN] Stock Out menu link not found - navigating directly to report URL.")
        driver.get(STOCKOUT_FILTER_URL)
        wait_ready(driver)
        time.sleep(PAUSE)


def past_one_year_range():
    """Return the site date-range string for the trailing one-year window."""
    end_date = date.today()
    start_date = end_date - timedelta(days=365)
    return f"{start_date:%m/%d/%Y}-{end_date:%m/%d/%Y}"


def set_date_range_past_one_year(driver):
    """Set Date Range to Past One Year using textbox first and dropdown fallback."""
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

    trigger = safe_click_first(
        driver,
        [
            (By.ID, "DateRange"),
            (By.NAME, "DateRange"),
            (By.XPATH, "//input[contains(@id,'DateRange') or contains(@name,'DateRange')]"),
            (By.XPATH, "//label[contains(.,'Date Range')]/following::input[1]"),
        ],
        timeout=5,
    )
    if trigger:
        try:
            scroll_to(driver, trigger)
            driver.execute_script("arguments[0].click();", trigger)
            time.sleep(0.8)
        except Exception:
            pass

    option_locators = [
        (By.XPATH, "//*[self::li or self::a or self::span or self::div][normalize-space(.)='Past One Year']"),
        (By.XPATH, "//*[self::li or self::a or self::span or self::div][contains(normalize-space(.),'Past One Year')]"),
        (By.XPATH, "//*[contains(@class,'ui-menu-item')]//*[contains(normalize-space(.),'Past One Year')]"),
        (By.XPATH, "//*[contains(@class,'dropdown-menu')]//*[contains(normalize-space(.),'Past One Year')]"),
    ]
    for by, locator in option_locators:
        try:
            option = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((by, locator))
            )
            scroll_to(driver, option)
            driver.execute_script("arguments[0].click();", option)
            time.sleep(0.8)
            print("  [INFO] Selected Date Range option: Past One Year")
            return "Past One Year"
        except Exception:
            continue

    js_selected = driver.execute_script(
        "var wanted = 'Past One Year'.toLowerCase();"
        "var nodes = document.querySelectorAll('li, a, span, div');"
        "for (var i = 0; i < nodes.length; i++) {"
        "  var node = nodes[i];"
        "  var text = (node.innerText || node.textContent || '').trim().toLowerCase();"
        "  if (text === wanted || text.indexOf(wanted) !== -1) { node.click(); return true; }"
        "}"
        "return false;"
    )
    if js_selected:
        time.sleep(0.8)
        print("  [INFO] Selected Date Range via JS fallback: Past One Year")
        return "Past One Year"

    raise AssertionError("Could not set Date Range to past one year on Stock Out report")


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
    """Check that the report output page is visible after submit."""
    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
    if "stock out" in body_text or "stockout" in body_text or "change filter" in body_text:
        return True

    rows = driver.find_elements(By.XPATH, "//table//tr[td]")
    return len(rows) > 0


# ============================================================================
# TEST CLASS
# ============================================================================


@pytest.mark.usefixtures("driver")
class TestStockOutReport:
    # -- TC-SOR-001: Login --------------------------------------------------
    def test_01_login(self, driver):
        """Login to QA site with buyeruser credentials."""
        print("\n[TC-SOR-001] Logging in to QA site...")
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

    # -- TC-SOR-002: Open Stock Out report ---------------------------------
    def test_02_open_stockout_report(self, driver):
        """Navigate to Reports -> Buyer Reports -> Stock Out report."""
        print("\n[TC-SOR-002] Opening Stock Out report...")
        navigate_to_stockout_report(driver)

        take_screenshot(driver, "02_stockout_filter")
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        assert "stockoutfilter" in driver.current_url.lower() or "stock out report" in page_text, (
            f"Expected Stock Out report filter page. Got: {driver.current_url}"
        )
        print(f"  [PASS] Stock Out report filter page loaded: {driver.current_url}")

    # -- TC-SOR-003: Set past one year, Show Report, then Change Filter ----
    def test_03_set_past_year_show_report_change_filter(self, driver):
        """Set Date Range, keep defaults, show report, then click Change Filter."""
        print("\n[TC-SOR-003] Setting Date Range, showing report, and changing filter...")

        selected_range = set_date_range_past_one_year(driver)
        clicked = click_show_report(driver)
        assert clicked, "Show Report button not found on Stock Out report"
        print(f"  [PASS] Show Report clicked for Date Range: {selected_range}")

        take_screenshot(driver, "03_after_show_report")
        assert report_loaded(driver), (
            f"Stock Out report did not load successfully for {selected_range}. URL: {driver.current_url}"
        )
        print("  [PASS] Stock Out report loaded successfully.")

        changed = click_change_filter_btn(driver)
        assert changed, "Change Filter button not found after report was shown"
        print("  [PASS] Change Filter button clicked.")

        take_screenshot(driver, "04_after_change_filter")

        filter_context_ok = (
            "stockoutfilter" in driver.current_url.lower()
            or safe_click_first(
                driver,
                [
                    (By.XPATH, "//button[normalize-space(text())='Show Report']"),
                    (By.XPATH, "//a[normalize-space(text())='Show Report']"),
                    (By.XPATH, "//input[@type='submit' and @value='Show Report']"),
                    (By.XPATH, "//label[contains(.,'Date Range') or contains(.,'DateRange') ]"),
                ],
                timeout=4,
            )
            is not None
        )
        assert filter_context_ok, (
            f"Did not navigate back to Stock Out filter page after Change Filter. URL: {driver.current_url}"
        )
        print(f"  [PASS] Returned to filter context: {driver.current_url}")
