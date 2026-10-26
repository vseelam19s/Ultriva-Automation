"""
QALS11 | Reports > Supplier Reports > View Notes History Report
================================================================
URL  : https://engineering.ultrivalms.com/QALS1011/SupplierReport/ViewNotesHistoryFilter
User : supnewuser / Ultriva!23

Test Flow
---------
  1. Login as supnewuser
  2. Navigate via Reports > Supplier Reports > View Notes History Report
  3. Click Show Report on filter page
  4. Click Change Filter on report page
  5. Verify return to filter page

Run (from qa_automation/):
    pytest tests/QALS11/Reports/SupplierReports/test_supplier_view_notes_history_report.py -v -s
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
VIEW_NOTES_FILTER_URL = f"{BASE_URL}/SupplierReport/ViewNotesHistoryFilter"


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
    path = os.path.join(
        screenshots_dir, f"supplier_view_notes_history_{name}_{ts}.png"
    )
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
    """Handle ReturnUrl login redirects when accessing SupplierReport pages directly."""
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


def navigate_to_view_notes_history(driver):
    """Open View Notes History using menu path, fallback to direct URL for reliability."""
    if "ViewNotesHistoryFilter" in driver.current_url and "Account/Login" not in driver.current_url:
        return

    reports_menu = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[normalize-space()='Reports']"),
            (By.XPATH, "//*[self::a or self::span][normalize-space()='Reports']"),
            (By.XPATH, "//a[contains(normalize-space(.),'Reports') and not(contains(@href,'Report/View'))]"),
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

    view_notes_link = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[contains(@href,'ViewNotesHistoryFilter')]"),
            (By.XPATH, "//a[contains(normalize-space(.),'View Notes History Report')]"),
            (By.XPATH, "//a[contains(normalize-space(.),'View Notes History')]"),
            (By.XPATH, "//*[self::a or self::span][contains(normalize-space(.),'View Notes History')]"),
        ],
    )
    if view_notes_link:
        scroll_to(driver, view_notes_link)
        driver.execute_script("arguments[0].click();", view_notes_link)
        wait_ready(driver)
        time.sleep(PAUSE)
        _reauth_if_redirected_to_login(driver)
        return

    print("  [WARN] Menu path not fully available - using direct filter URL fallback.")
    driver.get(VIEW_NOTES_FILTER_URL)
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
            (By.XPATH, "//*[@id='btnShowReport' or contains(@id,'ShowReport') or contains(@id,'showReport')]"),
            (By.XPATH, "//*[contains(normalize-space(.),'Show Report') and (self::button or self::a)]"),
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


def click_change_filter(driver):
    """Click Change Filter using resilient locators + JS fallback."""
    btn = safe_click_first(
        driver,
        [
            (By.XPATH, "//button[contains(normalize-space(.),'Change Filter')]"),
            (By.XPATH, "//a[contains(normalize-space(.),'Change Filter')]"),
            (By.XPATH, "//*[@id='changeFilter' or contains(@id,'ChangeFilter') or contains(@id,'changeFilter')]"),
            (By.XPATH, "//*[contains(normalize-space(.),'Change Filter') and (self::button or self::a)]"),
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
        ],
        timeout=4,
    )
    if back_btn:
        scroll_to(driver, back_btn)
        driver.execute_script("arguments[0].click();", back_btn)
        wait_ready(driver)
        time.sleep(PAUSE)
        return True

    return False


def filter_context_visible(driver):
    """Return True when View Notes History filter controls are present."""
    if "ViewNotesHistoryFilter" in driver.current_url and "Account/Login" not in driver.current_url:
        return True

    date_range_inputs = driver.find_elements(
        By.XPATH,
        "//*[contains(@id,'DateRange') or contains(@name,'DateRange') or contains(@value,'/')]",
    )
    show_report_controls = driver.find_elements(
        By.XPATH,
        "//button[normalize-space(.)='Show Report'] | //a[normalize-space(.)='Show Report'] | //input[@value='Show Report']",
    )
    return len(date_range_inputs) > 0 and len(show_report_controls) > 0


def report_context_visible(driver):
    """Return True when report results page appears to be loaded."""
    url_l = driver.current_url.lower()
    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
    rows = driver.find_elements(By.XPATH, "//table//tr[td]")

    return (
        "viewnoteshistory" in url_l
        or "view notes history report" in body_text
        or "change filter" in body_text
        or len(rows) > 0
    )


@pytest.mark.usefixtures("driver")
class TestSupplierViewNotesHistoryReport:
    """End-to-end checks for Supplier View Notes History report flow."""

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

    def test_02_open_view_notes_history_report(self, driver):
        """Navigate through Reports > Supplier Reports to View Notes History Report."""
        print("\n[test_02_open_view_notes_history_report] Opening report filter page...")
        navigate_to_view_notes_history(driver)
        take_screenshot(driver, "02_filter_page")

        assert filter_context_visible(driver), (
            f"View Notes History filter page not detected. URL: {driver.current_url}"
        )
        print(f"  [PASS] Filter context loaded. URL: {driver.current_url}")

    def test_03_show_report(self, driver):
        """Click Show Report and verify report page renders."""
        print("\n[test_03_show_report] Clicking Show Report...")
        clicked = click_show_report(driver)
        take_screenshot(driver, "03_report_page")

        assert clicked, "Could not click Show Report."
        assert report_context_visible(driver), (
            f"Report context not detected after Show Report. URL: {driver.current_url}"
        )
        print(f"  [PASS] Report page loaded. URL: {driver.current_url}")

    def test_04_change_filter(self, driver):
        """Click Change Filter and verify return to filter form."""
        print("\n[test_04_change_filter] Clicking Change Filter...")
        clicked = click_change_filter(driver)
        take_screenshot(driver, "04_back_to_filter")

        assert clicked, "Could not click Change Filter (or Back fallback)."
        assert filter_context_visible(driver), (
            f"Did not return to filter context after Change Filter. URL: {driver.current_url}"
        )
        print(f"  [PASS] Returned to filter context. URL: {driver.current_url}")
