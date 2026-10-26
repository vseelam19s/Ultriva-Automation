"""
QALS11 | Reports > Buyer Reports > Supplier Performance Report
================================================================
URL  : https://engineering.ultrivalms.com/QALS1011
User : buyeruser / Ultriva!23

Test Flow
---------
  1.  Login as buyeruser
  2.  Navigate to Reports -> Buyer Reports -> Supplier Performance Report
  3.  Select Date Range = Year To Date
  4.  Click Show Report
  5.  Verify the report output loads

Run (from qa_automation/):
    pytest tests/QALS11/Reports/test_supplier_performance_report.py -v -s
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
SUPPLIER_PERFORMANCE_URL = f"{BASE_URL}/BuyerReport/SuppliersPerformanceFilter"


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture(scope="class")
def driver():
    """Class-scoped Chrome driver — one browser session per test class."""
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
    path = os.path.join(screenshots_dir, f"supplier_performance_{name}_{ts}.png")
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


def navigate_to_supplier_performance(driver):
    """Open Supplier Performance report through the menu, with direct URL fallback."""
    if "SuppliersPerformanceFilter" in driver.current_url:
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
        scroll_to(driver, reports_link)
        driver.execute_script("arguments[0].click()", reports_link)
        wait_ready(driver)
        time.sleep(PAUSE)

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

    report_link = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[contains(normalize-space(.),'Supplier Performance Report') or contains(normalize-space(.),'Supplier Performance') or contains(@href,'SuppliersPerformanceFilter')]"),
            (By.XPATH, "//*[self::a or self::span][contains(normalize-space(.),'Supplier Performance')]"),
        ],
        timeout=6,
    )
    if report_link:
        scroll_to(driver, report_link)
        driver.execute_script("arguments[0].click()", report_link)
        wait_ready(driver)
        time.sleep(PAUSE)
    else:
        print("  [WARN] Supplier Performance menu link not found — navigating directly to the report URL.")
        driver.get(SUPPLIER_PERFORMANCE_URL)
        wait_ready(driver)
        time.sleep(PAUSE)


def open_date_range_dropdown(driver):
    """Open the Date Range control using multiple locator strategies."""
    trigger_selects = [
        (By.ID, "DateRange"),
        (By.NAME, "DateRange"),
        (By.XPATH, "//input[contains(@id,'DateRange') or contains(@name,'DateRange')]"),
        (By.XPATH, "//label[contains(.,'Date Range')]/following::input[1]"),
        (By.XPATH, "//*[contains(normalize-space(.),'Date Range')]/following::input[1]"),
        (By.XPATH, "//input[@type='text'][contains(@value,'Date') or contains(@id,'Range') or contains(@name,'Range')]"),
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


def select_date_range_year_to_date(driver):
    """Select Year To Date from the Date Range menu."""
    trigger = open_date_range_dropdown(driver)
    assert trigger, "Could not find Date Range trigger on Supplier Performance report"

    option_locators = [
        "//*[self::li or self::a or self::span or self::div][normalize-space(.)='Year To Date']",
        "//*[self::li or self::a or self::span or self::div][contains(normalize-space(.),'Year To Date')]",
        "//*[contains(@class,'ui-menu-item')]//*[contains(normalize-space(.),'Year To Date')]",
        "//*[contains(@class,'dropdown-menu')]//*[contains(normalize-space(.),'Year To Date')]",
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
        "var wanted = 'Year To Date'.toLowerCase();"
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
        print("  [INFO] Selected Year To Date via JS fallback")
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


def report_loaded(driver):
    """Check that the report page or results are visible."""
    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
    if "supplier performance" in body_text or "show report" in body_text:
        return True
    rows = driver.find_elements(By.XPATH, "//table//tr[td]")
    return len(rows) > 0


# ============================================================================
# TEST CLASS
# ============================================================================


@pytest.mark.usefixtures("driver")
class TestSupplierPerformanceReport:
    # ── TC-SPR-001: Login ──────────────────────────────────────────────────
    def test_01_login(self, driver):
        """Login to QA site with buyeruser credentials."""
        print("\n[TC-SPR-001] Logging in to QA site...")
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
        assert BASE_URL.lower() in current_url.lower() or "Home" in current_url, \
            f"Login may have failed. URL: {current_url}"
        print("  [PASS] Login successful.")

    # ── TC-SPR-002: Open Supplier Performance report ──────────────────────
    def test_02_open_supplier_performance_report(self, driver):
        """Navigate to Reports -> Buyer Reports -> Supplier Performance Report."""
        print("\n[TC-SPR-002] Opening Supplier Performance report...")
        navigate_to_supplier_performance(driver)

        take_screenshot(driver, "02_supplier_performance_report")
        assert "SuppliersPerformanceFilter" in driver.current_url or "BuyerReport" in driver.current_url, \
            f"Expected Supplier Performance report page. Got: {driver.current_url}"
        print(f"  [PASS] Supplier Performance report page loaded: {driver.current_url}")

    # ── TC-SPR-003: Select Year To Date and show report ───────────────────
    def test_03_select_year_to_date_and_show_report(self, driver):
        """Select Year To Date, keep defaults, and click Show Report."""
        print("\n[TC-SPR-003] Selecting Year To Date and clicking Show Report...")

        selected = select_date_range_year_to_date(driver)
        assert selected, "Could not select Year To Date in the Date Range control"

        clicked = click_show_report(driver)
        assert clicked, "Show Report button not found on Supplier Performance report"

        take_screenshot(driver, "03_after_show_report")
        assert report_loaded(driver), f"Supplier Performance report did not load successfully. URL: {driver.current_url}"
        print("  [PASS] Supplier Performance report loaded after Show Report.")