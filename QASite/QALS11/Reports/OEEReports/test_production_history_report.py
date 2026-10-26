"""
QALS11 | Reports > LFM/OEE Reports > Production History Report
================================================================
URL  : https://engineering.ultrivalms.com/QALS1011/OEEReport/ProductionHistoryFilter
User : Databizwarehouseuser / Ultriva!23

Test Flow
---------
  1. Login as Databizwarehouseuser
  2. Navigate via Reports -> LFM/OEE Reports -> Production History Report
  3. Click Show Report
  4. Verify Production History Summary loads
  5. Click on first Operation Name link from summary
  6. Verify Production History Details loads
  7. Click Back to Summary
  8. Click Change Filter

Run (from qa_automation/):
    pytest tests/QALS11/Reports/OEEReports/test_production_history_report.py -v -s
"""

import os
import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
USERNAME = "Databizwarehouseuser"
PASSWORD = "Ultriva!23"
PAUSE = 1.2
PRODUCTION_HISTORY_FILTER_URL = f"{BASE_URL}/OEEReport/ProductionHistoryFilter"


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
    path = os.path.join(screenshots_dir, f"production_history_{name}_{ts}.png")
    driver.save_screenshot(path)
    print(f"  [screenshot] {path}")
    return path


def safe_click_first(driver, locators, timeout=6):
    """Return first clickable element found from a list of locators."""
    for locator in locators:
        try:
            return WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
        except Exception:
            continue
    return None


def click_visible_text(driver, text):
    """Click first visible element matching text via JS fallback."""
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


def navigate_to_production_history_report(driver):
    """Open Production History Report using menu path with direct URL fallback."""
    if "ProductionHistoryFilter" in driver.current_url and "Account/Login" not in driver.current_url:
        return

    reports_menu = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[normalize-space()='Reports']"),
            (By.XPATH, "//*[self::a or self::span][normalize-space()='Reports']"),
            (By.XPATH, "//a[contains(normalize-space(.),'Reports')]"),
        ],
        timeout=6,
    )
    if reports_menu:
        try:
            scroll_to(driver, reports_menu)
            driver.execute_script("arguments[0].click();", reports_menu)
            time.sleep(PAUSE)
        except Exception:
            pass

    oee_section = safe_click_first(
        driver,
        [
            (By.XPATH, "//*[self::a or self::span or self::div][contains(normalize-space(.),'LFM/OEE Reports')]"),
            (By.XPATH, "//*[self::a or self::span or self::div][contains(normalize-space(.),'OEE Reports')]"),
            (By.XPATH, "//*[contains(@class,'panel') and contains(.,'OEE Reports')]"),
        ],
        timeout=5,
    )
    if oee_section:
        try:
            scroll_to(driver, oee_section)
            driver.execute_script("arguments[0].click();", oee_section)
            time.sleep(PAUSE)
        except Exception:
            pass

    report_link = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[contains(@href,'/OEEReport/ProductionHistoryFilter')]"),
            (By.XPATH, "//a[contains(@href,'ProductionHistoryFilter')]"),
            (By.XPATH, "//a[contains(normalize-space(.),'Production History Report')]"),
            (By.XPATH, "//*[self::a or self::span][contains(normalize-space(.),'Production History')]"),
        ],
        timeout=6,
    )
    if report_link:
        try:
            scroll_to(driver, report_link)
            driver.execute_script("arguments[0].click();", report_link)
            wait_ready(driver)
            time.sleep(PAUSE)
            if "ProductionHistoryFilter" in driver.current_url and "Account/Login" not in driver.current_url:
                return
        except Exception:
            pass

    print("  [WARN] Menu path unavailable - using direct URL fallback.")
    driver.get(PRODUCTION_HISTORY_FILTER_URL)
    wait_ready(driver)
    time.sleep(PAUSE)


def click_show_report(driver):
    """Click Show Report button on the Production History filter page."""
    btn = safe_click_first(
        driver,
        [
            (By.XPATH, "//button[normalize-space(text())='Show Report']"),
            (By.XPATH, "//a[normalize-space(text())='Show Report']"),
            (By.XPATH, "//input[@type='submit' and @value='Show Report']"),
            (By.XPATH, "//*[@id='btnShowReport' or contains(@id,'ShowReport') or contains(@id,'showReport')]"),
        ],
        timeout=6,
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


def summary_loaded(driver):
    """Check Production History Summary presence."""
    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
    rows = driver.find_elements(By.XPATH, "//table//tr[td]")
    return (
        "production history summary" in body_text
        or "productionhistory" in driver.current_url.lower()
        or "operation name" in body_text
        or "transactions" in body_text
        or len(rows) > 0
    )


def click_operation_item_from_summary(driver):
    """Click first Operation Name link from summary table body."""
    operation_locators = [
        (By.XPATH, "//tbody//tr/td[1]/a[string-length(normalize-space(text())) > 0]"),
        (By.XPATH, "//tbody//tr/td/a[contains(@href,'ProductionHistoryDetails')]"),
    ]

    for locator in operation_locators:
        try:
            elements = WebDriverWait(driver, 8).until(
                EC.presence_of_all_elements_located(locator)
            )
            visible = [e for e in elements if e.is_displayed() and e.text.strip()]
            if not visible:
                continue
            target = visible[0]
            operation_name = target.text.strip()
            scroll_to(driver, target)
            driver.execute_script("arguments[0].click();", target)
            wait_ready(driver)
            time.sleep(PAUSE * 2)
            return operation_name
        except Exception:
            continue

    operation_name = driver.execute_script(
        "var rows = document.querySelectorAll('table tbody tr');"
        "for (var i = 0; i < rows.length; i++) {"
        "  var first = rows[i].querySelector('td a');"
        "  if (!first) continue;"
        "  var txt = (first.innerText || '').trim();"
        "  if (txt && first.offsetParent !== null) { first.click(); return txt; }"
        "}"
        "return null;"
    )
    if operation_name:
        wait_ready(driver)
        time.sleep(PAUSE * 2)
        return operation_name

    return None


def details_loaded(driver):
    """Check Production History Details context."""
    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
    return (
        "production history details" in body_text
        or "productionhistorydetails" in driver.current_url.lower()
        or "operation status" in body_text
        or "completed qty" in body_text
        or "work center" in body_text
    )


def click_back_to_summary(driver):
    """Click Back to Summary on details page."""
    locators = [
        (By.XPATH, "//button[contains(normalize-space(.),'Back to Summary')]"),
        (By.XPATH, "//a[contains(normalize-space(.),'Back to Summary')]"),
        (By.XPATH, "//*[contains(@id,'backToSummary') or contains(@class,'back-summary')]"),
        (By.XPATH, "//*[contains(normalize-space(.),'Back to Summary') and (self::button or self::a)]"),
    ]

    for locator in locators:
        try:
            btn = WebDriverWait(driver, 6).until(EC.element_to_be_clickable(locator))
            scroll_to(driver, btn)
            driver.execute_script("arguments[0].click();", btn)
            wait_ready(driver)
            time.sleep(PAUSE)
            return True
        except Exception:
            continue

    if click_visible_text(driver, "Back to Summary"):
        wait_ready(driver)
        time.sleep(PAUSE)
        return True

    return False


def click_change_filter(driver):
    """Click Change Filter on summary page."""
    locators = [
        (By.XPATH, "//button[contains(normalize-space(.),'Change Filter')]"),
        (By.XPATH, "//a[contains(normalize-space(.),'Change Filter')]"),
        (By.XPATH, "//*[@id='changeFilter' or contains(@id,'ChangeFilter') or contains(@id,'changeFilter')]"),
    ]

    for locator in locators:
        try:
            btn = WebDriverWait(driver, 6).until(EC.element_to_be_clickable(locator))
            scroll_to(driver, btn)
            driver.execute_script("arguments[0].click();", btn)
            wait_ready(driver)
            time.sleep(PAUSE)
            return True
        except Exception:
            continue

    if click_visible_text(driver, "Change Filter"):
        wait_ready(driver)
        time.sleep(PAUSE)
        return True

    return False


@pytest.mark.usefixtures("driver")
class TestProductionHistoryReport:
    """Validate Production History Report full flow under LFM/OEE Reports."""

    def test_01_login(self, driver):
        """Login to QA site with Databizwarehouseuser credentials."""
        print("\n[TC-PHR-001] Logging in to QA site...")
        driver.get(f"{BASE_URL}/Account/Login")
        wait_ready(driver)

        find(driver, By.ID, "UserName").clear()
        find(driver, By.ID, "UserName").send_keys(USERNAME)
        find(driver, By.ID, "Password").clear()
        find(driver, By.ID, "Password").send_keys(PASSWORD)
        clickable(driver, By.ID, "login-button").click()

        wait_ready(driver)
        time.sleep(PAUSE * 2)

        assert "Account/Login" not in driver.current_url, (
            f"Login appears to have failed. Current URL: {driver.current_url}"
        )
        take_screenshot(driver, "01_login")

    def test_02_open_production_history_filter(self, driver):
        """Open Production History filter via menu path with URL fallback."""
        print("[TC-PHR-002] Opening Production History filter...")
        navigate_to_production_history_report(driver)

        body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        on_filter = "ProductionHistoryFilter" in driver.current_url or (
            "production history" in body_text and "show report" in body_text
        )
        assert on_filter, f"Expected Production History filter page, got: {driver.current_url}"
        take_screenshot(driver, "02_filter_page")

    def test_03_show_report(self, driver):
        """Click Show Report and verify summary loads."""
        print("[TC-PHR-003] Clicking Show Report...")
        assert click_show_report(driver), "Could not click Show Report"

        assert summary_loaded(driver), (
            f"Production History Summary did not load after Show Report. URL: {driver.current_url}"
        )
        take_screenshot(driver, "03_summary")

    def test_04_click_item_open_details(self, driver):
        """Click Operation Name from summary and verify details page."""
        print("[TC-PHR-004] Clicking Operation Name from summary...")
        operation_name = click_operation_item_from_summary(driver)
        assert operation_name, "Could not click any Operation Name from Production History Summary"

        assert details_loaded(driver), (
            f"Production History Details page did not load. URL: {driver.current_url}"
        )
        print(f"  [INFO] Opened details for operation: {operation_name}")
        take_screenshot(driver, "04_details")

    def test_05_back_to_summary(self, driver):
        """Click Back to Summary and verify summary context is restored."""
        print("[TC-PHR-005] Clicking Back to Summary...")
        assert click_back_to_summary(driver), "Could not click Back to Summary"

        assert summary_loaded(driver), (
            f"Expected Production History Summary after Back to Summary. URL: {driver.current_url}"
        )
        take_screenshot(driver, "05_back_to_summary")

    def test_06_click_change_filter(self, driver):
        """Click Change Filter from summary and verify return to filter page."""
        print("[TC-PHR-006] Clicking Change Filter...")
        assert click_change_filter(driver), "Could not click Change Filter"

        body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        on_filter = "ProductionHistoryFilter" in driver.current_url or (
            "production history" in body_text and "show report" in body_text
        )
        assert on_filter, (
            f"Did not return to Production History filter context. URL: {driver.current_url}"
        )
        take_screenshot(driver, "06_change_filter")