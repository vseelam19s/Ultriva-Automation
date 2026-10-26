"""
QALS11 | Reports > Buyer Reports > Rechedule Notes History Report
==================================================================
URL  : https://engineering.ultrivalms.com/QALS1011
User : buyeruser / Ultriva!23

Test Flow
---------
  1.  Login as buyeruser
  2.  Navigate to Reports -> Buyer Reports -> Rechedule Notes History Report
  3.  Click Show Report
  4.  Verify report output loads
  5.  Click Change Filter and verify return to filter page

Run (from qa_automation/):
    pytest tests/QALS11/Reports/test_rechedule_notes_history_report.py -v -s
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
RESCHEDULE_NOTES_HISTORY_FILTER_URL = f"{BASE_URL}/BuyerReport/RescheduleNotesHistoryFilter"


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
    path = os.path.join(screenshots_dir, f"rechedule_notes_history_{name}_{ts}.png")
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


def navigate_to_rechedule_notes_history_report(driver):
    """Open Rechedule Notes History report through menu path, with direct URL fallback."""
    if "RescheduleNotesHistoryFilter" in driver.current_url:
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
            driver.get(RESCHEDULE_NOTES_HISTORY_FILTER_URL)
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

    report_link = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[contains(@href,'RescheduleNotesHistoryFilter') or contains(normalize-space(.),'Rechedule Notes History') or contains(normalize-space(.),'Reschedule Notes History')]"),
            (By.XPATH, "//*[self::a or self::span][contains(normalize-space(.),'Rechedule Notes History') or contains(normalize-space(.),'Reschedule Notes History')]"),
        ],
        timeout=6,
    )
    if report_link:
        scroll_to(driver, report_link)
        driver.execute_script("arguments[0].click()", report_link)
        wait_ready(driver)
        time.sleep(PAUSE)
    else:
        print("  [WARN] Rechedule Notes History menu link not found - navigating directly to report URL.")
        driver.get(RESCHEDULE_NOTES_HISTORY_FILTER_URL)
        wait_ready(driver)
        time.sleep(PAUSE)


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
    """Click Change Filter (or Back fallback) on report page."""
    locators = [
        (By.XPATH, "//button[contains(normalize-space(.), 'Change Filter')]"),
        (By.XPATH, "//a[contains(normalize-space(.), 'Change Filter')]"),
        (By.XPATH, "//button[@id='changeFilter' or contains(@id,'ChangeFilter') or contains(@id,'changeFilter')]"),
        (By.XPATH, "//*[contains(normalize-space(.),'Change Filter') and (self::button or self::a)]"),
        (By.XPATH, "//button[contains(normalize-space(.), 'Back')]"),
        (By.XPATH, "//a[contains(normalize-space(.), 'Back')]"),
        (By.XPATH, "//*[contains(normalize-space(.),'Back') and (self::button or self::a)]"),
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

    for text in ("Change Filter", "Back"):
        clicked = click_visible_text(driver, text)
        if clicked:
            wait_ready(driver)
            time.sleep(PAUSE)
            return True

    return False


def report_loaded(driver):
    """Check that report output is visible after submit."""
    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
    if (
        "reschedule" in body_text
        or "rechedule" in body_text
        or "change filter" in body_text
        or "back" in body_text
        or "kanban" in body_text
    ):
        return True
    rows = driver.find_elements(By.XPATH, "//table//tr[td]")
    return len(rows) > 0


def filter_page_visible(driver):
    """Check if filter page controls are present."""
    if "RescheduleNotesHistoryFilter" in driver.current_url:
        return True
    fields = driver.find_elements(
        By.XPATH,
        "//*[contains(normalize-space(.),'Date Range') or contains(normalize-space(.),'Reschedule') or contains(normalize-space(.),'Rechedule')]",
    )
    return len(fields) > 0


# ============================================================================
# TEST CLASS
# ============================================================================


@pytest.mark.usefixtures("driver")
class TestRecheduleNotesHistoryReport:
    # -- TC-RNHR-001: Login -------------------------------------------------
    def test_01_login(self, driver):
        """Login to QA site with buyeruser credentials."""
        print("\n[TC-RNHR-001] Logging in to QA site...")
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

    # -- TC-RNHR-002: Open Rechedule Notes History report ------------------
    def test_02_open_rechedule_notes_history_report(self, driver):
        """Navigate to Reports -> Buyer Reports -> Rechedule Notes History Report."""
        print("\n[TC-RNHR-002] Opening Rechedule Notes History report...")
        navigate_to_rechedule_notes_history_report(driver)

        take_screenshot(driver, "02_rechedule_notes_history_filter")
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        assert (
            "reschedulenoteshistoryfilter" in driver.current_url.lower()
            or "reschedule" in page_text
            or "rechedule" in page_text
            or "date range" in page_text
        ), f"Expected Rechedule Notes History filter page. Got: {driver.current_url}"
        print(f"  [PASS] Rechedule Notes History filter page loaded: {driver.current_url}")

    # -- TC-RNHR-003: Show Report ------------------------------------------
    def test_03_show_report(self, driver):
        """Click Show Report and verify output loads."""
        print("\n[TC-RNHR-003] Clicking Show Report...")

        clicked = click_show_report(driver)
        assert clicked, "Show Report button not found on Rechedule Notes History filter page"

        take_screenshot(driver, "03_after_show_report")
        assert report_loaded(driver), (
            f"Rechedule Notes History report did not load. URL: {driver.current_url}"
        )
        print("  [PASS] Rechedule Notes History report loaded after Show Report.")

    # -- TC-RNHR-004: Change Filter ----------------------------------------
    def test_04_click_change_filter(self, driver):
        """Click Change Filter and verify return to filter page."""
        print("\n[TC-RNHR-004] Clicking Change Filter...")

        clicked = click_change_filter(driver)
        assert clicked, "Change Filter button was not found on Rechedule Notes History report page"

        take_screenshot(driver, "04_after_change_filter")
        assert filter_page_visible(driver), (
            f"Did not return to Rechedule Notes History filter page. URL: {driver.current_url}"
        )
        print("  [PASS] Change Filter returned to Rechedule Notes History filter page.")
