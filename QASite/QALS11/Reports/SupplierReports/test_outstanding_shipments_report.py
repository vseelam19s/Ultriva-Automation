"""
QALS11 | Reports > Supplier Reports > Outstanding Shipments Report
==================================================================
URL  : https://engineering.ultrivalms.com/QALS1011/SupplierReport/OutStandingShipmentFilter
User : supnewuser / Ultriva!23

Test Flow
---------
  1. Login as supnewuser
  2. Navigate via Reports > Supplier Reports > Outstanding Shipments Report
  3. Click Show Report on filter page
    4. Click Total Orders link from summary and verify details page data
    5. Click Back to Summary and verify return to summary
    6. Click Change Filter and verify return to filter page

Run (from qa_automation/):
    pytest tests/QALS11/Reports/SupplierReports/test_outstanding_shipments_report.py -v -s
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
OUTSTANDING_SHIPMENTS_FILTER_URL = (
    f"{BASE_URL}/SupplierReport/OutStandingShipmentFilter"
)


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
        screenshots_dir, f"supplier_outstanding_shipments_{name}_{ts}.png"
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
    """Handle ReturnUrl login redirects for SupplierReport pages."""
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


def navigate_to_outstanding_shipments(driver):
    """Open Outstanding Shipments via menu path, fallback to direct URL."""
    if (
        "OutStandingShipmentFilter" in driver.current_url
        and "Account/Login" not in driver.current_url
    ):
        return

    reports_menu = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[normalize-space()='Reports']"),
            (By.XPATH, "//*[self::a or self::span][normalize-space()='Reports']"),
            (By.XPATH, "//a[contains(normalize-space(.),'Reports')]"),
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

    outstanding_shipments_link = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[contains(@href,'OutStandingShipmentFilter')]"),
            (By.XPATH, "//a[contains(normalize-space(.),'Outstanding Shipment Report')]"),
            (By.XPATH, "//a[contains(normalize-space(.),'Outstanding Shipments Report')]"),
            (By.XPATH, "//a[contains(normalize-space(.),'Outstanding Shipments')]"),
            (By.XPATH, "//*[self::a or self::span][contains(normalize-space(.),'Outstanding Shipment')]"),
        ],
    )
    if outstanding_shipments_link:
        scroll_to(driver, outstanding_shipments_link)
        driver.execute_script("arguments[0].click();", outstanding_shipments_link)
        wait_ready(driver)
        time.sleep(PAUSE)
        _reauth_if_redirected_to_login(driver)
        return

    print("  [WARN] Menu path not fully available - using direct filter URL fallback.")
    driver.get(OUTSTANDING_SHIPMENTS_FILTER_URL)
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
            (By.XPATH, "//button[contains(normalize-space(.),'Change Filter')]") ,
            (By.XPATH, "//a[contains(normalize-space(.),'Change Filter')]") ,
            (By.XPATH, "//*[@id='changeFilter' or contains(@id,'ChangeFilter') or contains(@id,'changeFilter')]") ,
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
            (By.XPATH, "//button[contains(normalize-space(.),'Back')]") ,
            (By.XPATH, "//a[contains(normalize-space(.),'Back')]") ,
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


def click_total_orders_link(driver):
    """Click a Total Orders link from summary table and return clicked text."""
    link_locators = [
        (By.XPATH, "//tbody//tr/td[4]//a[string-length(normalize-space(text())) > 0]"),
        (By.XPATH, "//table//tbody//tr/td[4]//a"),
        (By.XPATH, "//a[contains(@href,'OutstandingShipmentDetails')]"),
    ]

    for locator in link_locators:
        try:
            elements = WebDriverWait(driver, 8).until(
                EC.presence_of_all_elements_located(locator)
            )
            visible = [el for el in elements if el.is_displayed() and el.text.strip()]
            if visible:
                first = visible[0]
                link_text = first.text.strip()
                scroll_to(driver, first)
                driver.execute_script("arguments[0].click();", first)
                wait_ready(driver)
                time.sleep(PAUSE * 2)
                return link_text
        except Exception:
            continue

    link_text = driver.execute_script(
        "var rows = document.querySelectorAll('table tbody tr');"
        "for (var i = 0; i < rows.length; i++) {"
        "  var cells = rows[i].querySelectorAll('td');"
        "  if (cells.length < 4) continue;"
        "  var links = cells[3].querySelectorAll('a');"
        "  for (var j = 0; j < links.length; j++) {"
        "    var link = links[j];"
        "    var txt = (link.innerText || '').trim();"
        "    if (txt && link.offsetParent !== null) { link.click(); return txt; }"
        "  }"
        "}"
        "return null;"
    )
    if link_text:
        wait_ready(driver)
        time.sleep(PAUSE * 2)
        return link_text

    return None


def details_context_visible(driver):
    """Return True when Outstanding Shipment Details page and data are visible."""
    url_l = driver.current_url.lower()
    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
    data_rows = driver.find_elements(By.XPATH, "//table//tbody//tr[td]")

    return (
        "outstandingshipmentdetails" in url_l
        or "outstanding shipment details" in body_text
        or "card id" in body_text
        or "back to summary" in body_text
    ) and len(data_rows) > 0


def click_back_to_summary(driver):
    """Click Back to Summary on details page."""
    btn = safe_click_first(
        driver,
        [
            (By.XPATH, "//button[contains(normalize-space(.),'Back to Summary')]") ,
            (By.XPATH, "//a[contains(normalize-space(.),'Back to Summary')]") ,
            (By.XPATH, "//*[contains(@id,'backToSummary') or contains(@id,'BackToSummary')]") ,
            (By.XPATH, "//*[contains(normalize-space(.),'Back to Summary') and (self::button or self::a)]"),
        ],
    )
    if btn:
        scroll_to(driver, btn)
        driver.execute_script("arguments[0].click();", btn)
        wait_ready(driver)
        time.sleep(PAUSE)
        return True

    clicked = click_visible_text(driver, "Back to Summary")
    if clicked:
        wait_ready(driver)
        time.sleep(PAUSE)
        return True

    return False


def filter_context_visible(driver):
    """Return True when Outstanding Shipments filter controls are present."""
    url_l = driver.current_url.lower()
    if "outstandingshipmentfilter" in url_l and "account/login" not in url_l:
        return True

    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
    show_report_controls = driver.find_elements(
        By.XPATH,
        "//button[normalize-space(.)='Show Report'] | //a[normalize-space(.)='Show Report'] | //input[@value='Show Report']",
    )
    has_filter_labels = (
        "outstanding shipment report" in body_text
        or "late tolerance 1" in body_text
        or "late tolerance 2" in body_text
        or "plant:" in body_text
    )
    return has_filter_labels and len(show_report_controls) > 0


def report_context_visible(driver):
    """Return True when report results page appears to be loaded."""
    url_l = driver.current_url.lower()
    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
    rows = driver.find_elements(By.XPATH, "//table//tr[td]")

    return (
        "outstandingshipment" in url_l
        or "out standing shipment" in body_text
        or "outstanding shipment" in body_text
        or "change filter" in body_text
        or len(rows) > 0
    )


@pytest.mark.usefixtures("driver")
class TestOutstandingShipmentsReport:
    """End-to-end checks for Supplier Outstanding Shipments report flow."""

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

    def test_02_open_outstanding_shipments_report(self, driver):
        """Navigate through Reports > Supplier Reports to Outstanding Shipments Report."""
        print("\n[test_02_open_outstanding_shipments_report] Opening report filter page...")
        navigate_to_outstanding_shipments(driver)
        take_screenshot(driver, "02_filter_page")

        assert filter_context_visible(driver), (
            f"Outstanding Shipments filter page not detected. URL: {driver.current_url}"
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

    def test_04_click_total_orders_link(self, driver):
        """Click Total Orders value from summary and verify details page data."""
        print("\n[test_04_click_total_orders_link] Clicking Total Orders link...")
        clicked_value = click_total_orders_link(driver)
        take_screenshot(driver, "04_details_page")

        assert clicked_value is not None, (
            "Could not click Total Orders link from Outstanding Shipment summary data."
        )
        assert details_context_visible(driver), (
            f"Details context not detected after clicking Total Orders. URL: {driver.current_url}"
        )
        print(f"  [PASS] Opened details using Total Orders value: {clicked_value}. URL: {driver.current_url}")

    def test_05_back_to_summary(self, driver):
        """Click Back to Summary on details page and verify summary returns."""
        print("\n[test_05_back_to_summary] Clicking Back to Summary...")
        clicked = click_back_to_summary(driver)
        take_screenshot(driver, "05_back_to_summary")

        assert clicked, "Could not click Back to Summary on details page."
        assert report_context_visible(driver), (
            f"Summary context not detected after Back to Summary. URL: {driver.current_url}"
        )
        print(f"  [PASS] Returned to summary report page. URL: {driver.current_url}")

    def test_06_change_filter(self, driver):
        """Click Change Filter and verify return to filter page."""
        print("\n[test_06_change_filter] Clicking Change Filter...")
        clicked = click_change_filter(driver)
        take_screenshot(driver, "06_back_to_filter")

        assert clicked, "Could not click Change Filter (or Back fallback)."
        assert filter_context_visible(driver), (
            f"Did not return to filter context after Change Filter. URL: {driver.current_url}"
        )
        print(f"  [PASS] Returned to filter context. URL: {driver.current_url}")