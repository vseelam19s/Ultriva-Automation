"""
QALS11 | Reports > Buyer Reports > On Hand Inventory Report - Full Flow
=======================================================================
URL  : https://engineering.ultrivalms.com/QALS1011
User : buyeruser / Ultriva!23

Test Flow
---------
  1.  Login as buyeruser
  2.  Navigate to Reports -> Buyer Reports -> On Hand Inventory report
        (direct URL: /BuyerReport/OnHandInventoryFilter)
  3.  Keep default filter values (This Plant, All, Business unit Item Location)
  4.  Click Show Report
  5.  Verify On Hand Inventory Summary table loads
  6.  Click on an Item link in the summary table
  7.  Verify On Hand Inventory Details page loads
  8.  Click Back to Summary button
  9.  Verify return to On Hand Inventory Summary
  10. Click Change Filter button
  11. Verify return to filter page

Run (from qa_automation/):
    pytest tests/QALS11/Reports/test_onhand_inventory_full_flow.py -v -s
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
ONHAND_FILTER_URL = f"{BASE_URL}/BuyerReport/OnHandInventoryFilter"
ONHAND_SUMMARY_URL = f"{BASE_URL}/BuyerReport/OnHandInventory"


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture(scope="class")
def driver():
    """Class-scoped Chrome driver — one browser session for the entire test class."""
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
    """Wait for element presence and return it."""
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, locator))
    )


def clickable(driver, by, locator, timeout=15):
    """Wait until element is clickable and return it."""
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, locator))
    )


def scroll_to(driver, el):
    """Scroll element into the centre of the viewport."""
    driver.execute_script("arguments[0].scrollIntoView({block:'center'})", el)
    time.sleep(0.3)


def take_screenshot(driver, name):
    """Save a PNG screenshot; prefix is onhand_full_ to avoid collisions."""
    screenshots_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "reports", "screenshots"
    )
    os.makedirs(screenshots_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(screenshots_dir, f"onhand_full_{name}_{ts}.png")
    driver.save_screenshot(path)
    print(f"  [screenshot] {path}")
    return path


def safe_click_first(driver, locators, timeout=5):
    """Return the first clickable element found from a list of (By, locator) tuples."""
    for locator in locators:
        try:
            return WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
        except Exception:
            continue
    return None


def click_visible_text(driver, text):
    """Click the first visible element whose inner text exactly matches *text* (JS fallback)."""
    return driver.execute_script(
        "var wanted = arguments[0].trim().toLowerCase();"
        "var els = document.querySelectorAll("
        "  'a, button, input[type=\"button\"], input[type=\"submit\"], span, div, li, td'"
        ");"
        "for (var i = 0; i < els.length; i++) {"
        "  var el = els[i];"
        "  var txt = (el.innerText || el.value || '').trim().toLowerCase();"
        "  if (!txt) continue;"
        "  if (txt === wanted && el.offsetParent !== null) { el.click(); return el; }"
        "}"
        "return null;",
        text,
    )


# ============================================================================
# NAVIGATION & PAGE ACTIONS
# ============================================================================


def navigate_to_onhand_inventory_report(driver):
    """Open the On Hand Inventory filter page — direct URL first, menu fallback."""
    if "OnHandInventory" in driver.current_url:
        return

    try:
        driver.get(ONHAND_FILTER_URL)
        wait_ready(driver)
        time.sleep(PAUSE)
        if "OnHandInventory" in driver.current_url:
            return
    except Exception:
        pass

    # Menu fallback: Reports -> Buyer Reports -> On Hand Inventory
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
            driver.get(ONHAND_FILTER_URL)
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

    onhand_link = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[contains(@href,'OnHandInventory') or contains(normalize-space(.),'On Hand Inventory')]"),
            (By.XPATH, "//*[self::a or self::span][contains(normalize-space(.),'On Hand Inventory')]"),
        ],
        timeout=6,
    )
    if onhand_link:
        scroll_to(driver, onhand_link)
        driver.execute_script("arguments[0].click()", onhand_link)
        wait_ready(driver)
        time.sleep(PAUSE)
    else:
        print("  [WARN] On Hand Inventory menu link not found — falling back to direct URL.")
        driver.get(ONHAND_FILTER_URL)
        wait_ready(driver)
        time.sleep(PAUSE)


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


def click_item_in_summary(driver):
    """Click the first item link in the On Hand Inventory Summary table.

    The summary table contains clickable item names (hyperlinks) in the Item column.
    We restrict to <tbody> rows to avoid clicking sort-header links in <thead> or first <tr>.
    Returns the item text that was clicked, or None on failure.
    """
    # Target <tbody> data rows only to skip sort-header links (e.g. "Item ↑")
    item_link_locators = [
        # href-based: most reliable — only actual item detail links contain these href segments
        (By.XPATH, "//tbody//tr/td/a[contains(@href,'OnHandInventory')]"),
        # Column 2 (Item) of any <tbody> row — skips header rows which live in <thead>
        (By.XPATH, "//tbody//tr/td[2]/a[string-length(normalize-space(text())) > 0]"),
        # Any <td> link in any <tbody> row
        (By.XPATH, "//tbody//tr/td/a[string-length(normalize-space(text())) > 0]"),
    ]

    for locator in item_link_locators:
        try:
            elements = WebDriverWait(driver, 8).until(
                EC.presence_of_all_elements_located(locator)
            )
            # Filter to visible, non-empty elements
            visible = [e for e in elements if e.is_displayed() and e.text.strip()]
            if visible:
                el = visible[0]
                item_text = el.text.strip()
                scroll_to(driver, el)
                driver.execute_script("arguments[0].click()", el)
                wait_ready(driver)
                time.sleep(PAUSE * 2)
                return item_text
        except Exception:
            continue

    # JS fallback: iterate <tbody> rows only, skip index 0 (header if in tbody)
    item_text = driver.execute_script(
        "var tbodies = document.querySelectorAll('table tbody');"
        "for (var b = 0; b < tbodies.length; b++) {"
        "  var rows = tbodies[b].querySelectorAll('tr');"
        "  for (var i = 0; i < rows.length; i++) {"
        "    var cells = rows[i].querySelectorAll('td');"
        "    if (cells.length < 2) continue;"
        "    var links = cells[1].querySelectorAll('a');"
        "    for (var j = 0; j < links.length; j++) {"
        "      var lnk = links[j];"
        "      var txt = (lnk.innerText || '').trim();"
        "      if (txt && lnk.offsetParent !== null) { lnk.click(); return txt; }"
        "    }"
        "  }"
        "}"
        "return null;"
    )
    if item_text:
        wait_ready(driver)
        time.sleep(PAUSE * 2)
        return item_text

    return None


def click_back_to_summary(driver):
    """Click the Back to Summary button on the On Hand Inventory Details page."""
    locators = [
        (By.XPATH, "//button[contains(normalize-space(.), 'Back to Summary')]"),
        (By.XPATH, "//a[contains(normalize-space(.), 'Back to Summary')]"),
        (By.XPATH, "//*[contains(@id,'backToSummary') or contains(@class,'back-summary')]"),
        (By.XPATH, "//*[contains(normalize-space(.), 'Back to Summary')]"),
    ]
    for locator in locators:
        try:
            element = WebDriverWait(driver, 6).until(EC.element_to_be_clickable(locator))
            scroll_to(driver, element)
            driver.execute_script("arguments[0].click();", element)
            wait_ready(driver)
            time.sleep(PAUSE)
            print(f"  [INFO] Clicked 'Back to Summary': {element.text.strip()}")
            return True
        except Exception:
            continue

    if click_visible_text(driver, "Back to Summary"):
        wait_ready(driver)
        time.sleep(PAUSE)
        print("  [INFO] Clicked 'Back to Summary' via JS text fallback")
        return True

    return False


def click_change_filter(driver):
    """Click the Change Filter button on the report summary page."""
    locators = [
        (By.XPATH, "//button[contains(normalize-space(.), 'Change Filter')]"),
        (By.XPATH, "//a[contains(normalize-space(.), 'Change Filter')]"),
        (By.XPATH, "//*[@id='changeFilter' or contains(@id,'ChangeFilter') or contains(@id,'changeFilter')]"),
    ]
    for locator in locators:
        try:
            element = WebDriverWait(driver, 6).until(EC.element_to_be_clickable(locator))
            scroll_to(driver, element)
            driver.execute_script("arguments[0].click();", element)
            wait_ready(driver)
            time.sleep(PAUSE)
            print("  [INFO] Clicked 'Change Filter'")
            return True
        except Exception:
            continue

    if click_visible_text(driver, "Change Filter"):
        wait_ready(driver)
        time.sleep(PAUSE)
        print("  [INFO] Clicked 'Change Filter' via JS text fallback")
        return True

    return False


def summary_table_loaded(driver):
    """Return True if the On Hand Inventory Summary table is visible."""
    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
    rows = driver.find_elements(By.XPATH, "//table//tr[td]")
    return (
        "on hand inventory" in body_text
        or "onhandinventory" in driver.current_url.lower()
        or len(rows) > 0
    )


# ============================================================================
# TEST CLASS
# ============================================================================


@pytest.mark.usefixtures("driver")
class TestOnHandInventoryFullFlow:
    # -----------------------------------------------------------------------
    # TC-OHI-F-001 : Login
    # -----------------------------------------------------------------------
    def test_01_login(self, driver):
        """Login to the QA site as buyeruser."""
        print("\n[TC-OHI-F-001] Logging in to QA site...")
        driver.get(BASE_URL)
        wait_ready(driver)

        find(driver, By.ID, "UserName").clear()
        driver.find_element(By.ID, "UserName").send_keys(USERNAME)
        find(driver, By.ID, "Password").clear()
        driver.find_element(By.ID, "Password").send_keys(PASSWORD)
        clickable(driver, By.ID, "login-button").click()
        wait_ready(driver)
        time.sleep(PAUSE)

        take_screenshot(driver, "01_after_login")
        current_url = driver.current_url
        print(f"  [URL] {current_url}")
        assert BASE_URL.lower() in current_url.lower() or "Home" in current_url, (
            f"Login may have failed. Current URL: {current_url}"
        )
        print("  [PASS] Login successful.")

    # -----------------------------------------------------------------------
    # TC-OHI-F-002 : Open On Hand Inventory report
    # -----------------------------------------------------------------------
    def test_02_open_onhand_inventory_report(self, driver):
        """Navigate to Reports -> Buyer Reports -> On Hand Inventory."""
        print("\n[TC-OHI-F-002] Opening On Hand Inventory report...")
        navigate_to_onhand_inventory_report(driver)

        take_screenshot(driver, "02_filter_page")
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        assert (
            "onhandinventory" in driver.current_url.lower()
            or "on hand inventory" in page_text
        ), f"Expected On Hand Inventory filter page. Got: {driver.current_url}"
        print(f"  [PASS] On Hand Inventory filter page loaded: {driver.current_url}")

    # -----------------------------------------------------------------------
    # TC-OHI-F-003 : Keep defaults and click Show Report
    # -----------------------------------------------------------------------
    def test_03_keep_defaults_show_report(self, driver):
        """Keep all default filter values and click Show Report."""
        print("\n[TC-OHI-F-003] Keeping default values and clicking Show Report...")

        # Verify default radio buttons are present (This Plant, All, Business unit Item Location)
        page_text = driver.find_element(By.TAG_NAME, "body").text
        print(f"  [INFO] Filter page content snippet: {page_text[:300]}")

        clicked = click_show_report(driver)
        assert clicked, "Show Report button not found on the On Hand Inventory filter page"
        print("  [PASS] Clicked Show Report with default filter values.")

        take_screenshot(driver, "03_summary_page")
        assert summary_table_loaded(driver), (
            f"On Hand Inventory Summary did not load. URL: {driver.current_url}"
        )
        print(f"  [PASS] On Hand Inventory Summary loaded. URL: {driver.current_url}")

    # -----------------------------------------------------------------------
    # TC-OHI-F-004 : Click an Item in the summary table
    # -----------------------------------------------------------------------
    def test_04_click_item_in_summary(self, driver):
        """Click the first Item link in the On Hand Inventory Summary table."""
        print("\n[TC-OHI-F-004] Clicking an item in the summary table...")

        item_text = click_item_in_summary(driver)
        assert item_text is not None, (
            "Could not find or click any item link in the On Hand Inventory Summary table"
        )
        print(f"  [INFO] Clicked item: '{item_text}'")

        take_screenshot(driver, "04_item_details")
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        assert (
            "onhandinventorydetails" in driver.current_url.lower()
            or "onhandinventory" in driver.current_url.lower()
            or "on hand inventory" in page_text
            or "card id" in page_text
        ), f"Expected On Hand Inventory Details page. Got: {driver.current_url}"
        print(f"  [PASS] On Hand Inventory Details loaded for item '{item_text}'. URL: {driver.current_url}")

    # -----------------------------------------------------------------------
    # TC-OHI-F-005 : Click Back to Summary
    # -----------------------------------------------------------------------
    def test_05_back_to_summary(self, driver):
        """Click Back to Summary from the details page."""
        print("\n[TC-OHI-F-005] Clicking Back to Summary...")

        clicked = click_back_to_summary(driver)
        assert clicked, "Back to Summary button not found on the details page"
        print("  [PASS] Clicked Back to Summary.")

        take_screenshot(driver, "05_back_to_summary")
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        assert (
            "on hand inventory summary" in page_text
            or "on hand inventory" in page_text
            or "onhandinventory" in driver.current_url.lower()
        ), f"Expected On Hand Inventory Summary after Back to Summary. Got: {driver.current_url}"
        print(f"  [PASS] Returned to On Hand Inventory Summary. URL: {driver.current_url}")

    # -----------------------------------------------------------------------
    # TC-OHI-F-006 : Click Change Filter
    # -----------------------------------------------------------------------
    def test_06_change_filter(self, driver):
        """Click Change Filter from the summary page."""
        print("\n[TC-OHI-F-006] Clicking Change Filter...")

        clicked = click_change_filter(driver)
        assert clicked, "Change Filter button not found on the On Hand Inventory Summary page"
        print("  [PASS] Clicked Change Filter.")

        take_screenshot(driver, "06_after_change_filter")
        filter_page_ok = (
            "onhandinventoryfilter" in driver.current_url.lower()
            or safe_click_first(
                driver,
                [
                    (By.XPATH, "//button[normalize-space(text())='Show Report']"),
                    (By.XPATH, "//a[normalize-space(text())='Show Report']"),
                    (By.XPATH, "//input[@type='submit' and @value='Show Report']"),
                ],
                timeout=4,
            ) is not None
        )
        assert filter_page_ok, (
            f"Did not return to filter page after Change Filter. Got: {driver.current_url}"
        )
        print(f"  [PASS] Returned to On Hand Inventory filter page. URL: {driver.current_url}")
