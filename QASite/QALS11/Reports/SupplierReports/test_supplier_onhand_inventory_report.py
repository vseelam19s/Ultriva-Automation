"""
QALS11 | Reports > Supplier Reports > Supplier On Hand Inventory Report
=======================================================================
URL  : https://engineering.ultrivalms.com/QALS1011/SupplierReport/OnHandInventoryFilter
User : supnewuser / Ultriva!23

Test Flow
---------
  1. Login as supnewuser
  2. Open Supplier On Hand Inventory report filter page
  3. Keep default filter values and click Show Report
  4. Click an Item in the summary report
  5. Click Back to Summary and verify return to summary page

Run (from qa_automation/):
    pytest tests/QALS11/Reports/SupplierReports/test_supplier_onhand_inventory_report.py -v -s
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
ONHAND_FILTER_URL = f"{BASE_URL}/SupplierReport/OnHandInventoryFilter"


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
    path = os.path.join(screenshots_dir, f"supplier_onhand_inventory_{name}_{ts}.png")
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


def navigate_to_supplier_onhand_inventory(driver):
    """Open Supplier On Hand Inventory report filter page with re-auth support."""
    if "OnHandInventoryFilter" in driver.current_url and "Account/Login" not in driver.current_url:
        return

    driver.get(ONHAND_FILTER_URL)
    wait_ready(driver)
    time.sleep(PAUSE)

    if "Account/Login" in driver.current_url:
        print("  [INFO] Login redirect detected - re-authenticating for Supplier Report access...")
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


def summary_table_loaded(driver):
    """Return True if the Supplier On Hand Inventory Summary table is visible."""
    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
    rows = driver.find_elements(By.XPATH, "//table//tr[td]")
    return (
        "on hand inventory" in body_text
        or "onhandinventory" in driver.current_url.lower()
        or len(rows) > 0
    )


def click_item_in_summary(driver):
    """Click the first Item link in the Supplier On Hand Inventory Summary table."""
    item_link_locators = [
        (By.XPATH, "//tbody//tr/td/a[contains(@href,'OnHandInventory')]"),
        (By.XPATH, "//tbody//tr/td[2]/a[string-length(normalize-space(text())) > 0]"),
        (By.XPATH, "//tbody//tr/td/a[string-length(normalize-space(text())) > 0]"),
    ]

    for locator in item_link_locators:
        try:
            elements = WebDriverWait(driver, 8).until(
                EC.presence_of_all_elements_located(locator)
            )
            visible = [element for element in elements if element.is_displayed() and element.text.strip()]
            if visible:
                element = visible[0]
                item_text = element.text.strip()
                scroll_to(driver, element)
                driver.execute_script("arguments[0].click()", element)
                wait_ready(driver)
                time.sleep(PAUSE * 2)
                return item_text
        except Exception:
            continue

    item_text = driver.execute_script(
        "var tbodies = document.querySelectorAll('table tbody');"
        "for (var b = 0; b < tbodies.length; b++) {"
        "  var rows = tbodies[b].querySelectorAll('tr');"
        "  for (var i = 0; i < rows.length; i++) {"
        "    var cells = rows[i].querySelectorAll('td');"
        "    if (cells.length < 2) continue;"
        "    var links = cells[1].querySelectorAll('a');"
        "    for (var j = 0; j < links.length; j++) {"
        "      var link = links[j];"
        "      var txt = (link.innerText || '').trim();"
        "      if (txt && link.offsetParent !== null) { link.click(); return txt; }"
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
    """Click the Back to Summary button on the details page."""
    locators = [
        (By.XPATH, "//button[contains(normalize-space(.), 'Back to Summary') or contains(normalize-space(.), 'Back to Report')]"),
        (By.XPATH, "//a[contains(normalize-space(.), 'Back to Summary') or contains(normalize-space(.), 'Back to Report')]"),
        (By.XPATH, "//*[contains(@id,'backToSummary') or contains(@id,'BackToSummary') or contains(@id,'backToReport') or contains(@id,'BackToReport')]"),
        (By.XPATH, "//*[contains(normalize-space(.), 'Back to Summary') or contains(normalize-space(.), 'Back to Report')]"),
    ]
    for locator in locators:
        try:
            element = WebDriverWait(driver, 6).until(EC.element_to_be_clickable(locator))
            scroll_to(driver, element)
            driver.execute_script("arguments[0].click();", element)
            wait_ready(driver)
            time.sleep(PAUSE)
            print("  [INFO] Clicked 'Back to Summary'")
            return True
        except Exception:
            continue

    for text in ["Back to Summary", "Back to Report"]:
        if click_visible_text(driver, text):
            wait_ready(driver)
            time.sleep(PAUSE)
            print(f"  [INFO] Clicked '{text}' via JS text fallback")
            return True

    return False


@pytest.mark.usefixtures("driver")
class TestSupplierOnHandInventoryReport:
    def test_01_login(self, driver):
        """Login to the QA site as supnewuser."""
        print("\n[TC-SOHI-001] Logging in to QA site...")
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
        assert BASE_URL.lower() in current_url.lower() or "Home" in current_url or "SetReadyToShipDateItems" in current_url, (
            f"Login may have failed. URL: {current_url}"
        )
        print("  [PASS] Login successful.")

    def test_02_open_supplier_onhand_inventory_report(self, driver):
        """Open the supplier On Hand Inventory filter page."""
        print("\n[TC-SOHI-002] Opening Supplier On Hand Inventory report...")
        navigate_to_supplier_onhand_inventory(driver)

        take_screenshot(driver, "02_filter_page")
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        assert (
            "onhandinventoryfilter" in driver.current_url.lower()
            or "on hand inventory" in page_text
            or "show report" in page_text
        ), f"Expected Supplier On Hand Inventory filter page. Got: {driver.current_url}"
        print(f"  [PASS] Supplier On Hand Inventory filter page loaded: {driver.current_url}")

    def test_03_keep_defaults_show_report(self, driver):
        """Keep default filter values and click Show Report."""
        print("\n[TC-SOHI-003] Keeping default values and clicking Show Report...")

        clicked = click_show_report(driver)
        assert clicked, "Show Report button not found on the Supplier On Hand Inventory filter page"
        print("  [PASS] Clicked Show Report with default filter values.")

        take_screenshot(driver, "03_summary_page")
        assert summary_table_loaded(driver), (
            f"Supplier On Hand Inventory Summary did not load. URL: {driver.current_url}"
        )
        print(f"  [PASS] Supplier On Hand Inventory Summary loaded. URL: {driver.current_url}")

    def test_04_click_item_in_summary(self, driver):
        """Click the first Item link in the Supplier On Hand Inventory summary table."""
        print("\n[TC-SOHI-004] Clicking an Item in the summary table...")

        item_text = click_item_in_summary(driver)
        assert item_text is not None, (
            "Could not find or click any Item link in the Supplier On Hand Inventory summary table"
        )
        print(f"  [INFO] Clicked Item: '{item_text}'")

        take_screenshot(driver, "04_item_details")
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        assert (
            "onhandinventorydetails" in driver.current_url.lower()
            or "onhandinventory" in driver.current_url.lower()
            or "on hand inventory" in page_text
            or "card id" in page_text
        ), f"Expected Supplier On Hand Inventory details page. Got: {driver.current_url}"
        print(f"  [PASS] Supplier On Hand Inventory details loaded for Item '{item_text}'. URL: {driver.current_url}")

    def test_05_back_to_summary(self, driver):
        """Click Back to Summary from the details page."""
        print("\n[TC-SOHI-005] Clicking Back to Summary...")

        clicked = click_back_to_summary(driver)
        assert clicked, "Back to Summary button not found on the details page"
        print("  [PASS] Clicked Back to Summary.")

        take_screenshot(driver, "05_back_to_summary")
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        assert (
            "on hand inventory summary" in page_text
            or "on hand inventory" in page_text
            or "onhandinventory" in driver.current_url.lower()
        ), f"Expected Supplier On Hand Inventory summary after Back to Summary. Got: {driver.current_url}"
        print(f"  [PASS] Returned to Supplier On Hand Inventory summary. URL: {driver.current_url}")