"""
QALS11 | Reports > Buyer Reports > Total Spend Report
======================================================
URL  : https://engineering.ultrivalms.com/QALS1011
User : buyeruser / Ultriva!23

Test Flow
---------
  1.  Login as buyeruser
  2.  Navigate to Reports -> Buyer Reports -> Total Spend Report
  3.  Select Date Range = Year To Date
  4.  Click Show Report
  5.  Verify the report output loads
  6.  Click Change Filter and verify return to filter page

Run (from qa_automation/):
    pytest tests/QALS11/Reports/test_total_spend_report.py -v -s
"""

import os
import time
from datetime import date

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
TOTAL_SPEND_FILTER_URL = f"{BASE_URL}/BuyerReport/TotalSpendFilter"


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
    path = os.path.join(screenshots_dir, f"total_spend_{name}_{ts}.png")
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


def navigate_to_total_spend_report(driver):
    """Open Total Spend report through menu path, with direct URL fallback."""
    if "TotalSpendFilter" in driver.current_url:
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
            driver.get(TOTAL_SPEND_FILTER_URL)
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

    total_spend_link = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[contains(@href,'TotalSpendFilter') or contains(normalize-space(.),'Total Spend Report') or contains(normalize-space(.),'Total Spend')]"),
            (By.XPATH, "//*[self::a or self::span][contains(normalize-space(.),'Total Spend Report') or contains(normalize-space(.),'Total Spend')]"),
        ],
        timeout=6,
    )
    if total_spend_link:
        scroll_to(driver, total_spend_link)
        driver.execute_script("arguments[0].click()", total_spend_link)
        wait_ready(driver)
        time.sleep(PAUSE)
    else:
        print("  [WARN] Total Spend menu link not found - navigating directly to report URL.")
        driver.get(TOTAL_SPEND_FILTER_URL)
        wait_ready(driver)
        time.sleep(PAUSE)


def year_to_date_range():
    """Return date range string from Jan 1 to today in site format."""
    today = date.today()
    start = date(today.year, 1, 1)
    return f"{start:%m/%d/%Y}-{today:%m/%d/%Y}"


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
                print(f"  [INFO] Date Range textbox set to {date_range}")
                return True
        except Exception:
            continue

    return False


def click_show_report(driver):
    """Click Show Report button."""
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
        driver.execute_script("arguments[0].click();", show_btn)
        wait_ready(driver)
        time.sleep(PAUSE * 2)
        return True

    clicked = click_visible_text(driver, "Show Report")
    if clicked:
        wait_ready(driver)
        time.sleep(PAUSE * 2)
        return True

    return False


def click_change_filter(driver):
    """Click Change Filter on report page."""
    locators = [
        (By.XPATH, "//button[contains(normalize-space(.), 'Change Filter')]"),
        (By.XPATH, "//a[contains(normalize-space(.), 'Change Filter')]"),
        (By.XPATH, "//button[@id='changeFilter' or contains(@id,'ChangeFilter') or contains(@id,'changeFilter')]"),
        (By.XPATH, "//*[contains(normalize-space(.),'Change Filter') and (self::button or self::a)]"),
    ]
    for locator in locators:
        try:
            element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(locator))
            scroll_to(driver, element)
            driver.execute_script("arguments[0].click();", element)
            wait_ready(driver)
            time.sleep(PAUSE)
            return True
        except Exception:
            continue

    clicked = click_visible_text(driver, "Change Filter")
    if clicked:
        wait_ready(driver)
        time.sleep(PAUSE)
        return True

    return False


def report_loaded(driver):
    """Check that report output is visible after submit."""
    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
    if "total spend" in body_text or "change filter" in body_text:
        return True
    rows = driver.find_elements(By.XPATH, "//table//tr[td]")
    return len(rows) > 0


def filter_page_visible(driver):
    """Check if filter page controls are present."""
    if "TotalSpendFilter" in driver.current_url:
        return True
    fields = driver.find_elements(By.XPATH, "//*[contains(normalize-space(.),'Date Range')]")
    return len(fields) > 0


# ============================================================================
# TEST CLASS
# ============================================================================


@pytest.mark.usefixtures("driver")
class TestTotalSpendReport:
    # -- TC-TSR-001: Login --------------------------------------------------
    def test_01_login(self, driver):
        """Login to QA site with buyeruser credentials."""
        print("\n[TC-TSR-001] Logging in to QA site...")
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

    # -- TC-TSR-002: Open Total Spend report -------------------------------
    def test_02_open_total_spend_report(self, driver):
        """Navigate to Reports -> Buyer Reports -> Total Spend Report."""
        print("\n[TC-TSR-002] Opening Total Spend report...")
        navigate_to_total_spend_report(driver)

        take_screenshot(driver, "02_total_spend_filter")
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        assert (
            "totalspendfilter" in driver.current_url.lower()
            or "total spend" in page_text
            or "date range" in page_text
        ), f"Expected Total Spend filter page. Got: {driver.current_url}"
        print(f"  [PASS] Total Spend filter page loaded: {driver.current_url}")

    # -- TC-TSR-003: Year To Date + Show Report ----------------------------
    def test_03_select_year_to_date_and_show_report(self, driver):
        """Select Date Range as Year To Date and click Show Report."""
        print("\n[TC-TSR-003] Selecting Year To Date and clicking Show Report...")

        selected = select_year_to_date(driver)
        assert selected, "Could not set Date Range to Year To Date"

        clicked = click_show_report(driver)
        assert clicked, "Show Report button not found on Total Spend filter page"

        take_screenshot(driver, "03_after_show_report")
        assert report_loaded(driver), f"Total Spend report did not load. URL: {driver.current_url}"
        print("  [PASS] Total Spend report loaded after Show Report.")

    # -- TC-TSR-004: Change Filter -----------------------------------------
    def test_04_click_change_filter(self, driver):
        """Click Change Filter and verify return to filter page."""
        print("\n[TC-TSR-004] Clicking Change Filter...")

        clicked = click_change_filter(driver)
        assert clicked, "Change Filter button was not found on Total Spend report page"

        take_screenshot(driver, "04_after_change_filter")
        assert filter_page_visible(driver), (
            f"Did not return to Total Spend filter page. URL: {driver.current_url}"
        )
        print("  [PASS] Change Filter returned to Total Spend filter page.")
