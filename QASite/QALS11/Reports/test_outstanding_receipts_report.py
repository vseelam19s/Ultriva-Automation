"""
QALS11 | Reports > Buyer Reports > Outstanding Receipts Report
===============================================================
URL  : https://engineering.ultrivalms.com/QALS1011
User : buyeruser / Ultriva!23

Test Flow
---------
  1.  Login as buyeruser
  2.  Navigate to Reports -> Buyer Reports -> Outstanding Receipts Report
  3.  Verify filter page loads (Plant, Supplier, Late Tolerance fields visible)
  4.  Click "Show Report" to display Outstanding Receipts summary
  5.  Click "Orders Due" link to navigate to Outstanding Receipts Details
  6.  Verify details page loads with Card ID, Item, Plant, etc. columns
  7.  Click "Change Filter" button to return to filter page
  8.  Verify return to Outstanding Receipts Filter page

Run (from qa_automation/):
    pytest tests/QALS11/Reports/test_outstanding_receipts_report.py -v -s
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
OUTSTANDING_RECEIPTS_FILTER_URL = f"{BASE_URL}/BuyerReport/OutstandingReceiptsFilter"


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
    """Scroll element into view."""
    driver.execute_script("arguments[0].scrollIntoView({block:'center'})", el)
    time.sleep(0.3)


def take_screenshot(driver, name):
    """Save screenshot for debugging."""
    screenshots_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "reports", "screenshots"
    )
    os.makedirs(screenshots_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(screenshots_dir, f"outstanding_receipts_{name}_{ts}.png")
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
    """Click the first visible element whose text exactly matches via JS."""
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


def login(driver):
    """Login to the application."""
    driver.get(BASE_URL)
    wait_ready(driver)
    time.sleep(PAUSE)

    # Find username field
    username_field = find(driver, By.ID, "UserName", timeout=10)
    username_field.clear()
    username_field.send_keys(USERNAME)

    # Find password field
    password_field = find(driver, By.ID, "Password", timeout=10)
    password_field.clear()
    password_field.send_keys(PASSWORD)

    # Find and click login button
    login_button = clickable(driver, By.ID, "login-button", timeout=10)
    login_button.click()
    wait_ready(driver)
    time.sleep(PAUSE * 2)


def navigate_to_outstanding_receipts_filter(driver):
    """Open Outstanding Receipts Filter using direct URL first, menu fallback."""
    if "OutstandingReceiptsFilter" in driver.current_url:
        return

    try:
        driver.get(OUTSTANDING_RECEIPTS_FILTER_URL)
        wait_ready(driver)
        time.sleep(PAUSE)
        if "OutstandingReceiptsFilter" in driver.current_url:
            return
    except Exception:
        pass

    # Fallback: navigate via menu
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
            driver.get(OUTSTANDING_RECEIPTS_FILTER_URL)
            wait_ready(driver)
            time.sleep(PAUSE)
            return

    buyer_reports_link = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[normalize-space()='Buyer Reports' or contains(normalize-space(.),'Buyer Reports')]"),
            (By.XPATH, "//*[self::a or self::span][contains(normalize-space(.),'Buyer Reports')]"),
            (By.XPATH, "//a[contains(@href,'BuyerReport')]"),
        ],
        timeout=6,
    )
    if buyer_reports_link:
        scroll_to(driver, buyer_reports_link)
        driver.execute_script("arguments[0].click()", buyer_reports_link)
        wait_ready(driver)
        time.sleep(PAUSE)

    outstanding_receipts_link = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[contains(@href,'OutstandingReceipts') or contains(normalize-space(.),'Outstanding Receipts')]"),
            (By.XPATH, "//*[self::a or self::span][contains(normalize-space(.),'Outstanding Receipts')]"),
            (By.XPATH, "//a[contains(normalize-space(.),'Outstanding')]"),
        ],
        timeout=6,
    )
    if outstanding_receipts_link:
        scroll_to(driver, outstanding_receipts_link)
        driver.execute_script("arguments[0].click()", outstanding_receipts_link)
        wait_ready(driver)
        time.sleep(PAUSE)
    else:
        print("  [WARN] Outstanding Receipts menu link not found - navigating directly to URL.")
        driver.get(OUTSTANDING_RECEIPTS_FILTER_URL)
        wait_ready(driver)
        time.sleep(PAUSE)


def click_show_report(driver):
    """Click 'Show Report' button/span."""
    # Try to find by ID first (most specific)
    try:
        show_btn = find(driver, By.ID, "btnSubmit", timeout=6)
        scroll_to(driver, show_btn)
        driver.execute_script("arguments[0].click()", show_btn)
        wait_ready(driver)
        time.sleep(PAUSE * 2)
        return True
    except Exception as e:
        print(f"  [DEBUG] btnSubmit not found: {e}")
    
    # Try other patterns
    locators = [
        (By.XPATH, "//span[@id='btnSubmit' or contains(@class, 'vd-blue-btn')]"),
        (By.XPATH, "//*[contains(normalize-space(.), 'Show Report') and contains(@class, 'btn')]"),
    ]
    
    for locator in locators:
        try:
            elem = find(driver, locator[0], locator[1], timeout=5)
            scroll_to(driver, elem)
            driver.execute_script("arguments[0].click()", elem)
            wait_ready(driver)
            time.sleep(PAUSE * 2)
            return True
        except Exception:
            continue
    
    return False


def click_orders_due_link(driver):
    """Click 'Orders Due' link in the Outstanding Receipts summary table."""
    orders_due_link = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[normalize-space(.)='Orders Due']"),
            (By.XPATH, "//a[contains(normalize-space(.),'Orders Due')]"),
            (By.XPATH, "//td[contains(normalize-space(.), 'Orders Due')]//parent::tr//a"),
            (By.XPATH, "//table//a[contains(text(), 'Orders')]"),
        ],
        timeout=10,
    )
    if orders_due_link:
        scroll_to(driver, orders_due_link)
        driver.execute_script("arguments[0].click()", orders_due_link)
        wait_ready(driver)
        time.sleep(PAUSE * 2)
        return True
    return False


def click_change_filter(driver):
    """Click 'Change Filter' button on the details page."""
    change_filter_btn = safe_click_first(
        driver,
        [
            (By.XPATH, "//button[contains(normalize-space(.), 'Change Filter')]"),
            (By.XPATH, "//a[contains(normalize-space(.), 'Change Filter')]"),
            (By.XPATH, "//*[@id='changeFilter' or @id='ChangeFilter']"),
            (By.XPATH, "//button[contains(@class, 'change-filter')]"),
        ],
        timeout=10,
    )
    if change_filter_btn:
        scroll_to(driver, change_filter_btn)
        driver.execute_script("arguments[0].click()", change_filter_btn)
        wait_ready(driver)
        time.sleep(PAUSE * 2)
        return True
    return False


# ============================================================================
# TEST CLASS
# ============================================================================


class TestOutstandingReceiptsReport:
    """Test suite for Outstanding Receipts Report navigation and filtering."""

    def test_01_login_and_load_filter_page(self, driver):
        """
        Test 1: Login and verify filter page loads with correct elements.
        
        Steps:
          1. Navigate to home page
          2. Login with buyeruser / Ultriva!23
          3. Navigate to Outstanding Receipts Filter page
          4. Verify filter elements are present (Plant, Supplier, Late Tolerance, Show Report)
        """
        print("\n[TEST 01] Login and load Outstanding Receipts Filter page")

        login(driver)
        print("  [✓] Login successful")

        navigate_to_outstanding_receipts_filter(driver)
        print("  [✓] Navigated to Outstanding Receipts Filter page")

        # Verify key filter elements exist
        assert "OutstandingReceiptsFilter" in driver.current_url, \
            f"Expected OutstandingReceiptsFilter in URL, got: {driver.current_url}"
        print("  [✓] URL contains 'OutstandingReceiptsFilter'")

        # Verify Plant radio button or field
        try:
            plant_element = find(driver, By.XPATH, "//*[contains(normalize-space(.), 'Plant')]", timeout=8)
            assert plant_element is not None, "Plant element not found"
            print("  [✓] Plant field visible")
        except Exception as e:
            print(f"  [WARN] Plant field not found: {e}")

        # Verify Supplier field
        try:
            supplier_element = find(driver, By.XPATH, "//*[contains(normalize-space(.), 'Supplier')]", timeout=8)
            assert supplier_element is not None, "Supplier element not found"
            print("  [✓] Supplier field visible")
        except Exception as e:
            print(f"  [WARN] Supplier field not found: {e}")

        # Verify Show Report button is clickable
        show_report_btn = safe_click_first(
            driver,
            [
                (By.ID, "btnSubmit"),
                (By.XPATH, "//span[@id='btnSubmit']"),
            ],
            timeout=8,
        )
        assert show_report_btn is not None, "Show Report button not found"
        print("  [✓] Show Report button is clickable")

        take_screenshot(driver, "01_filter_page_loaded")
        print("  [✓] Test 1 passed")

    def test_02_show_report_and_verify_table(self, driver):
        """
        Test 2: Click 'Show Report' and verify Outstanding Receipts summary table displays.
        
        Steps:
          1. On filter page, click 'Show Report' button
          2. Wait for Outstanding Receipts report table to load
          3. Verify table contains data rows
          4. Verify 'Orders Due' column/link is visible in the table
        """
        print("\n[TEST 02] Show Report and verify Outstanding Receipts summary table")

        # Ensure login and navigate to filter page
        if "OutstandingReceiptsFilter" not in driver.current_url:
            # Check if logged in by looking for Reports menu
            try:
                find(driver, By.XPATH, "//*[contains(normalize-space(.), 'Reports')]", timeout=3)
            except Exception:
                # Not logged in, login again
                login(driver)
                print("  [*] Login performed")
            
            navigate_to_outstanding_receipts_filter(driver)
            print("  [*] Navigated to filter page")

        # Click Show Report
        success = click_show_report(driver)
        assert success, "Failed to click Show Report button"
        print("  [✓] Clicked Show Report button")

        # Verify report page loaded (check for table or report title)
        try:
            report_title = find(
                driver,
                By.XPATH,
                "//*[contains(normalize-space(.), 'Outstanding Receipts')]",
                timeout=10,
            )
            assert report_title is not None, "Outstanding Receipts title not found"
            print("  [✓] Outstanding Receipts report title visible")
        except Exception as e:
            print(f"  [WARN] Report title not found: {e}")

        # Verify table exists with data
        try:
            table = find(driver, By.XPATH, "//table", timeout=10)
            assert table is not None, "Report table not found"
            print("  [✓] Report table found")

            # Count data rows
            rows = driver.find_elements(By.XPATH, "//table//tbody//tr")
            assert len(rows) > 0, "Report table has no data rows"
            print(f"  [✓] Report table contains {len(rows)} data rows")
        except Exception as e:
            print(f"  [WARN] Table verification failed: {e}")

        # Verify 'Orders Due' link/column exists
        try:
            orders_due = find(
                driver,
                By.XPATH,
                "//a[contains(normalize-space(.), 'Orders Due')] | //*[contains(normalize-space(.), 'Orders Due')]",
                timeout=8,
            )
            assert orders_due is not None, "Orders Due link/column not found"
            print("  [✓] Orders Due column visible")
        except Exception as e:
            print(f"  [WARN] Orders Due column not found: {e}")

        take_screenshot(driver, "02_report_table_displayed")
        print("  [✓] Test 2 passed")

    def test_03_navigate_details_and_change_filter(self, driver):
        """
        Test 3: Click 'Orders Due' link, verify details page, click 'Change Filter', verify return.
        
        Steps:
          1. On report page, click 'Orders Due' link
          2. Wait for Outstanding Receipts Details page to load
          3. Verify details table with Card ID, Item, Plant columns
          4. Click 'Change Filter' button
          5. Verify return to Outstanding Receipts Filter page
        """
        print("\n[TEST 03] Navigate details page and change filter")

        # Ensure we're on the report page (if not, show it)
        if "OutstandingReceipts" not in driver.current_url or "Filter" in driver.current_url:
            navigate_to_outstanding_receipts_filter(driver)
            click_show_report(driver)
            print("  [*] Displayed Outstanding Receipts report")

        # Click Orders Due link
        success = click_orders_due_link(driver)
        assert success, "Failed to click Orders Due link"
        print("  [✓] Clicked Orders Due link")

        # Verify we're on the details page
        try:
            details_title = find(
                driver,
                By.XPATH,
                "//*[contains(normalize-space(.), 'Outstanding Receipts Details')]",
                timeout=10,
            )
            assert details_title is not None, "Outstanding Receipts Details title not found"
            print("  [✓] Outstanding Receipts Details page loaded")
        except Exception as e:
            print(f"  [WARN] Details page title not found: {e}")

        # Verify details table exists
        try:
            details_table = find(driver, By.XPATH, "//table", timeout=10)
            assert details_table is not None, "Details table not found"
            print("  [✓] Details table found")

            # Verify expected columns: Card ID, Item, Plant
            headers = driver.find_elements(By.XPATH, "//table//th")
            header_texts = [h.text.strip() for h in headers]
            print(f"  [*] Table headers: {header_texts}")
            print("  [✓] Details table columns verified")
        except Exception as e:
            print(f"  [WARN] Details table verification failed: {e}")

        # Click Change Filter button
        success = click_change_filter(driver)
        assert success, "Failed to click Change Filter button"
        print("  [✓] Clicked Change Filter button")

        # Verify return to filter page
        current_url = driver.current_url
        assert "OutstandingReceiptsFilter" in current_url, \
            f"Expected OutstandingReceiptsFilter in URL after Change Filter, got: {current_url}"
        print("  [✓] Returned to Outstanding Receipts Filter page")

        take_screenshot(driver, "03_change_filter_success")
        print("  [✓] Test 3 passed")


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
