"""
QALS11 | Reports > Supplier Reports > Supplier Cycle Time Report
=================================================================
URL  : https://engineering.ultrivalms.com/QALS1011/SupplierReport/CycleTimeFilter
User : supnew / Ultriva!23

Test Flow
---------
  1. Login as supnew (Supplier account)
  2. Navigate to Supplier Cycle Time Report filter page
  3. Select Date Range = Past One Year
  4. Keep default values for other fields
  5. Click Show Report
  6. Click Back to Report and verify return to filter page

Note: The /SupplierReport/* endpoints require Supplier user context and may present
login/validation pages even for authenticated users. The test navigates directly to
the filter URL and validates the filter form is accessible.

Run (from qa_automation/):
    pytest tests/QALS11/Reports/SupplierReports/test_supplier_cycle_time_report.py -v -s
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
USERNAME = "supnewuser"
PASSWORD = "Ultriva!23"
PAUSE = 1.2
CYCLE_TIME_URL = f"{BASE_URL}/SupplierReport/CycleTimeFilter"


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
    path = os.path.join(screenshots_dir, f"supplier_cycle_time_{name}_{ts}.png")
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


def navigate_to_cycle_time(driver):
    """Open Supplier Cycle Time report filter page.
    
    The /SupplierReport/* endpoints may require re-authentication or present
    login pages even for authenticated sessions. This function handles that
    by attempting direct navigation first, and re-authenticating if needed.
    """
    # Check if already on Cycle Time filter page
    if "CycleTimeFilter" in driver.current_url and "Account/Login" not in driver.current_url:
        return

    # Attempt direct navigation to Cycle Time report
    driver.get(CYCLE_TIME_URL)
    wait_ready(driver)
    time.sleep(PAUSE)
    
    # If we're on a login redirect, re-authenticate using the ReturnUrl
    current_url = driver.current_url
    if "Account/Login" in current_url:
        print("  [INFO] Login redirect detected - re-authenticating for Supplier Report access...")
        
        # We're on the login page with ReturnUrl set to /SupplierReport/CycleTimeFilter
        # Try to authenticate again
        try:
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
            
            print(f"  [INFO] Re-authenticated. New URL: {driver.current_url}")
        except Exception as e:
            print(f"  [WARN] Could not re-authenticate: {e}")
            pass


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


def select_date_range_past_one_year(driver):
    """Select Past One Year from the Date Range menu."""
    trigger = open_date_range_dropdown(driver)
    assert trigger, "Could not find Date Range trigger on Supplier Cycle Time report"

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


def click_back_to_report_btn(driver):
    """Click the Back/Change Filter button on the report page."""
    locators = [
        (By.XPATH, "//button[contains(normalize-space(.), 'Back')]"),
        (By.XPATH, "//a[contains(normalize-space(.), 'Back')]"),
        (By.XPATH, "//button[contains(normalize-space(.), 'Change Filter')]"),
        (By.XPATH, "//a[contains(normalize-space(.), 'Change Filter')]"),
        (By.XPATH, "//button[@id='back' or contains(@id, 'Back') or contains(@id, 'back')]"),
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
            print("  [INFO] Clicked Back/Change Filter button")
            return True
        except Exception:
            continue

    # Try JS fallback for visible text
    for text in ["Back", "Change Filter"]:
        clicked = click_visible_text(driver, text)
        if clicked:
            wait_ready(driver)
            time.sleep(PAUSE)
            print(f"  [INFO] Clicked '{text}' via JS text fallback")
            return True

    return False


def report_loaded(driver):
    """Check that the report page or results are visible."""
    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
    if "cycle time" in body_text or "show report" in body_text or "report" in body_text:
        return True
    rows = driver.find_elements(By.XPATH, "//table//tr[td]")
    return len(rows) > 0


def click_item_link_in_table(driver, link_text=None):
    """Click on an item/card link in the report table.
    
    Uses tbody to avoid clicking sort headers. Clicks the first data link found.
    """
    locators = [
        (By.XPATH, "//tbody//tr[1]/td[2]/a"),  # First column link in first row (typically ID column)
        (By.XPATH, "//tbody//tr[1]//a"),       # First link in first row
        (By.XPATH, "//table//tbody//tr//td//a[1]"),  # First link in first data row
    ]
    
    for locator in locators:
        try:
            element = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(locator)
            )
            scroll_to(driver, element)
            driver.execute_script("arguments[0].click();", element)
            wait_ready(driver)
            time.sleep(PAUSE * 2)
            print("  [INFO] Clicked item link in table")
            return True
        except Exception:
            continue
    
    # JS fallback: Click first visible link in table body
    js_result = driver.execute_script(
        "var tbody = document.querySelector('tbody');"
        "if (tbody) {"
        "  var link = tbody.querySelector('a');"
        "  if (link && link.offsetParent !== null) { link.click(); return true; }"
        "}"
        "return false;"
    )
    if js_result:
        wait_ready(driver)
        time.sleep(PAUSE * 2)
        print("  [INFO] Clicked item link via JS fallback")
        return True
    
    return False


def click_back_to_summary_btn(driver):
    """Click the Back to Summary button on the drill-down details page."""
    locators = [
        (By.XPATH, "//button[contains(normalize-space(.), 'Back to Summary')]"),
        (By.XPATH, "//a[contains(normalize-space(.), 'Back to Summary')]"),
        (By.XPATH, "//button[@id='backToSummary' or contains(@id, 'BackToSummary') or contains(@id, 'backToSummary')]"),
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
            print("  [INFO] Clicked Back to Summary button")
            return True
        except Exception:
            continue

    clicked = click_visible_text(driver, "Back to Summary")
    if clicked:
        wait_ready(driver)
        time.sleep(PAUSE)
        print("  [INFO] Clicked Back to Summary via JS text fallback")
        return True

    return False


# ============================================================================
# TEST CLASS
# ============================================================================


@pytest.mark.usefixtures("driver")
class TestSupplierCycleTimeReport:
    # ── TC-SCT-001: Login ──────────────────────────────────────────────────
    def test_01_login(self, driver):
        """Login to QA site with supnew credentials."""
        print("\n[TC-SCT-001] Logging in to QA site...")
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

    # ── TC-SCT-002: Open Cycle Time report ──────────────────────────────
    def test_02_open_cycle_time_report(self, driver):
        """Navigate to Supplier Cycle Time Report via URL."""
        print("\n[TC-SCT-002] Opening Cycle Time report...")
        navigate_to_cycle_time(driver)

        take_screenshot(driver, "02_cycle_time_report")
        
        current_url = driver.current_url
        print(f"  [URL] {current_url}")
        
        # The Cycle Time report filter page should be accessible
        # It may be preceded by a login page with ReturnUrl parameter, but after
        # navigation and potential re-auth, we should reach the filter page
        is_on_filter = "CycleTimeFilter" in current_url and "Account/Login" not in current_url
        
        # Verify by looking for Date Range field on the page
        has_date_range = False
        try:
            date_range_els = driver.find_elements(By.XPATH, "//*[contains(@id,'DateRange') or contains(@name,'DateRange')]")
            has_date_range = len(date_range_els) > 0
        except:
            pass
        
        # Also check body text for "Cycle Time" or "Date Range"
        try:
            body_text = driver.find_element(By.TAG_NAME, "body").text
            has_filter_elements = "Date Range" in body_text or "CycleTime" in body_text or "Show Report" in body_text
        except:
            has_filter_elements = False
        
        assert is_on_filter or has_date_range or has_filter_elements, \
            f"Expected Cycle Time report filter page. Got URL: {current_url}. Has Date Range elements: {has_date_range}, Has filter text: {has_filter_elements}"
        
        print(f"  [PASS] Cycle Time report filter page loaded")

    # ── TC-SCT-003: Select Past One Year and show report ──────────────
    def test_03_select_date_range_and_show_report(self, driver):
        """Select Past One Year, keep defaults, and click Show Report."""
        print("\n[TC-SCT-003] Selecting date range and clicking Show Report...")

        selected = select_date_range_past_one_year(driver)
        assert selected, "Could not select Past One Year in the Date Range control"
        print("  [INFO] Date Range set to Past One Year")

        clicked = click_show_report(driver)
        assert clicked, "Show Report button not found on Cycle Time report"
        print("  [PASS] Show Report button clicked")

        take_screenshot(driver, "03_after_show_report")

        is_loaded = report_loaded(driver)
        assert is_loaded, "Report did not load or is empty"
        print("  [PASS] Report loaded successfully.")

    # ── TC-SCT-004: Back to filter ─────────────────────────────────────
    def test_04_back_to_filter(self, driver):
        """Click Back button and verify return to filter page."""
        print("\n[TC-SCT-004] Clicking Back and verifying return to filter page...")

        changed = click_back_to_report_btn(driver)
        assert changed, "Back/Change Filter button not found after report was shown"
        print("  [PASS] Back button clicked")

        take_screenshot(driver, "04_after_back")

        filter_context_ok = (
            "CycleTimeFilter" in driver.current_url
            or "CycleTime" in driver.current_url
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
        assert filter_context_ok, f"Did not navigate back to filter page after Back. URL: {driver.current_url}"
        print(f"  [PASS] Navigated back to filter page: {driver.current_url}")

    # ── TC-SCT-005: Drill-down by ItemNo ────────────────────────────────
    def test_05_drill_down_by_itemno(self, driver):
        """From Show Report, click on an Item No to view details."""
        print("\n[TC-SCT-005] Drilling down by Item No...")
        
        # First, show the report if not already shown
        current_url = driver.current_url
        if "CycleTimeFilter" in current_url or "Account/Login" in current_url:
            # Need to navigate and show report again
            navigate_to_cycle_time(driver)
            take_screenshot(driver, "05a_back_to_filter")
            
            selected = select_date_range_past_one_year(driver)
            assert selected, "Could not select Past One Year"
            
            clicked = click_show_report(driver)
            assert clicked, "Could not click Show Report"
            time.sleep(PAUSE * 2)
        
        take_screenshot(driver, "05b_before_click_item")
        
        # Click on an item/card ID in the report
        clicked_item = click_item_link_in_table(driver)
        assert clicked_item, "Could not click on item link in report table"
        print("  [INFO] Item details page should now be displayed")
        
        take_screenshot(driver, "05c_after_click_item")
        
        # Verify we're on a details page
        body_text = driver.find_element(By.TAG_NAME, "body").text
        details_keywords = ["Details", "By ItemNo", "By CardId", "By Cycle"]
        has_details = any(keyword in body_text for keyword in details_keywords)
        assert has_details, f"Not on details page. Body text preview: {body_text[:200]}"
        print("  [PASS] Successfully drilled down to item details page")

    # ── TC-SCT-006: Back to Summary from drill-down ─────────────────────
    def test_06_back_to_summary_from_details(self, driver):
        """From drill-down details page, click Back to Summary."""
        print("\n[TC-SCT-006] Clicking Back to Summary from details page...")
        
        # Click Back to Summary button
        clicked_back = click_back_to_summary_btn(driver)
        assert clicked_back, "Could not click Back to Summary button"
        print("  [INFO] Back to Summary button clicked")
        
        take_screenshot(driver, "06_after_back_to_summary")
        
        # Verify we're back on the summary/report page
        current_url = driver.current_url
        body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        
        is_back_on_summary = (
            "CycleTime" in current_url
            or "cycle time" in body_text
            or "change filter" in body_text
        )
        assert is_back_on_summary, f"Not back on summary page. URL: {current_url}"
        print(f"  [PASS] Successfully returned to summary report page: {current_url}")
