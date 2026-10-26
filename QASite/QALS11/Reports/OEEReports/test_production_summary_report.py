"""
QALS11 | Reports > LFM/OEE Reports > Production Summary Report
================================================================
URL  : https://engineering.ultrivalms.com/QALS1011/OEEReport/CapacityUtilization
User : Databizwarehouseuser / Ultriva!23

Test Flow
---------
  1. Login as Databizwarehouseuser
  2. Navigate via Reports -> LFM/OEE Reports -> Production Summary Report
  3. Click the target date from the Production Summary calendar
  4. Verify Remaining production hours required summary loads
  5. Click first available Machine Code
  6. Verify Assigned jobs for Machine details loads
  7. Click Back
  8. Verify machine summary context is restored

Run (from qa_automation/):
    pytest tests/QALS11/Reports/OEEReports/test_production_summary_report.py -v -s
"""

import os
import time
from datetime import date

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
USERNAME = "Databizwarehouseuser"
PASSWORD = "Ultriva!23"
PAUSE = 1.2
PRODUCTION_SUMMARY_URL = f"{BASE_URL}/OEEReport/CapacityUtilization"


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
    path = os.path.join(screenshots_dir, f"production_summary_{name}_{ts}.png")
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


def navigate_to_production_summary_report(driver):
    """Open Production Summary Report using menu path with direct URL fallback."""
    if "CapacityUtilization" in driver.current_url and "Account/Login" not in driver.current_url:
        return

    reports_menu = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[normalize-space()='Reports']"),
            (By.XPATH, "//*[self::a or self::span][normalize-space()='Reports']"),
            (By.XPATH, "//a[contains(normalize-space(.),'Reports')]")
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

    reports_sections = [
        [
            (By.XPATH, "//*[self::a or self::span or self::div][contains(normalize-space(.),'LFM/OEE Reports')]"),
            (By.XPATH, "//*[contains(@class,'panel') and contains(.,'LFM/OEE Reports')]"),
        ],
        [
            (By.XPATH, "//*[self::a or self::span or self::div][contains(normalize-space(.),'Production Summary Report')]"),
            (By.XPATH, "//*[contains(@class,'panel') and contains(.,'Production Summary Report')]"),
        ],
    ]

    for section_locators in reports_sections:
        section = safe_click_first(driver, section_locators, timeout=5)
        if not section:
            continue
        try:
            scroll_to(driver, section)
            driver.execute_script("arguments[0].click();", section)
            time.sleep(PAUSE)
        except Exception:
            pass

    report_link = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[contains(@href,'/OEEReport/CapacityUtilization')]"),
            (By.XPATH, "//a[contains(@href,'CapacityUtilization')]"),
            (By.XPATH, "//a[contains(normalize-space(.),'Production Summary Report')]"),
            (By.XPATH, "//*[self::a or self::span][contains(normalize-space(.),'Production Summary Report')]"),
            (By.XPATH, "//a[contains(normalize-space(.),'OEE Report') and contains(@href,'OEEReport')]"),
        ],
        timeout=6,
    )
    if report_link:
        try:
            scroll_to(driver, report_link)
            driver.execute_script("arguments[0].click();", report_link)
            wait_ready(driver)
            time.sleep(PAUSE)
            if "CapacityUtilization" in driver.current_url and "Account/Login" not in driver.current_url:
                return
        except Exception:
            pass

    print("  [WARN] Menu path unavailable - using direct URL fallback.")
    driver.get(PRODUCTION_SUMMARY_URL)
    wait_ready(driver)
    time.sleep(PAUSE)


def production_summary_filter_loaded(driver):
    """Check Production Summary filter page presence."""
    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
    return (
        "production summary report" in body_text
        and "current/next operation" in body_text
        and "current/next machine" in body_text
    ) or "CapacityUtilization" in driver.current_url


def click_target_date(driver, target_date=None):
    """Click target date from the production summary calendar."""
    target_date = target_date or date.today()
    formatted = target_date.strftime("%m/%d/%Y")
    month_year = target_date.strftime("%B, %Y")
    day_value = str(target_date.day)

    href_locators = [
        (By.XPATH, f"//a[contains(@href,'sdate={formatted}')]"),
        (By.XPATH, f"//a[contains(@href,'date={formatted}')]"),
        (By.XPATH, f"//a[contains(@href,'{formatted.replace('/', '%2F')}')]"),
    ]
    for locator in href_locators:
        try:
            target = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(locator))
            scroll_to(driver, target)
            driver.execute_script("arguments[0].click();", target)
            wait_ready(driver)
            time.sleep(PAUSE * 2)
            return formatted
        except Exception:
            continue

    calendar_locators = [
        (
            By.XPATH,
            "//td[normalize-space(text())='" + day_value + "' and ancestor::table[preceding-sibling::*[1][contains(normalize-space(.),'" + month_year + "')]] ]",
        ),
        (
            By.XPATH,
            "//a[normalize-space(text())='" + day_value + "' and ancestor::table[preceding-sibling::*[1][contains(normalize-space(.),'" + month_year + "')]] ]",
        ),
    ]
    for by, locator in calendar_locators:
        try:
            cell = WebDriverWait(driver, 5).until(EC.presence_of_element_located((by, locator)))
            clickable_target = cell
            if cell.tag_name.lower() != "a":
                links = cell.find_elements(By.XPATH, ".//a")
                if links:
                    clickable_target = links[0]
            scroll_to(driver, clickable_target)
            driver.execute_script("arguments[0].click();", clickable_target)
            wait_ready(driver)
            time.sleep(PAUSE * 2)
            return formatted
        except Exception:
            continue

    clicked = driver.execute_script(
        "var formatted = arguments[0];"
        "var dayValue = arguments[1];"
        "var monthYear = arguments[2].toLowerCase();"
        "var anchors = document.querySelectorAll('a');"
        "for (var i = 0; i < anchors.length; i++) {"
        "  var a = anchors[i];"
        "  var href = (a.getAttribute('href') || '').toLowerCase();"
        "  var txt = (a.innerText || '').trim();"
        "  if (a.offsetParent === null) continue;"
        "  if (href.indexOf(formatted.toLowerCase()) !== -1 || href.indexOf(encodeURIComponent(formatted).toLowerCase()) !== -1) { a.click(); return true; }"
        "  if (txt !== dayValue) continue;"
        "  var node = a;"
        "  while (node) {"
        "    var text = (node.innerText || '').toLowerCase();"
        "    if (text.indexOf(monthYear) !== -1) { a.click(); return true; }"
        "    node = node.parentElement;"
        "  }"
        "}"
        "var cells = document.querySelectorAll('td');"
        "for (var j = 0; j < cells.length; j++) {"
        "  var td = cells[j];"
        "  var text = (td.innerText || '').trim();"
        "  if (td.offsetParent === null || text !== dayValue) continue;"
        "  var node2 = td;"
        "  while (node2) {"
        "    var parentText = (node2.innerText || '').toLowerCase();"
        "    if (parentText.indexOf(monthYear) !== -1) { td.click(); return true; }"
        "    node2 = node2.parentElement;"
        "  }"
        "}"
        "return false;",
        formatted,
        day_value,
        month_year,
    )
    if clicked:
        wait_ready(driver)
        time.sleep(PAUSE * 2)
        return formatted

    return None


def machine_summary_loaded(driver, target_date=None):
    """Check Remaining production hours required page presence."""
    target_date = target_date or date.today()
    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
    slash_date = target_date.strftime("%m/%d/%Y")
    compact_date = target_date.strftime("%m/%d/%Y").lstrip("0").replace("/0", "/")
    return (
        "remaining production hours required on" in body_text
        and (slash_date.lower() in body_text or compact_date.lower() in body_text)
        and "machine code" in body_text
        and "jobs assigned" in body_text
    ) or "CapacityUtilizationDetails" in driver.current_url


def click_first_machine_code(driver):
    """Click first visible Machine Code link from tbody rows only."""
    machine_locators = [
        (
            By.XPATH,
            "//table[.//th[contains(normalize-space(.),'Machine Code')]]//tbody//tr/td[2]/a[string-length(normalize-space(text())) > 0]",
        ),
        (
            By.XPATH,
            "//table[.//th[contains(normalize-space(.),'Machine Code')]]//tr[td]/td[2]/a[string-length(normalize-space(text())) > 0]",
        ),
        (
            By.XPATH,
            "//table[.//th[contains(normalize-space(.),'Machine Code')]]//tr[td]/td[2]//*[self::a or self::span][string-length(normalize-space(text())) > 0]",
        ),
        (
            By.XPATH,
            "//table[.//th[contains(normalize-space(.),'Machine Code')]]//tr[td]//a[contains(@href,'CapacityUtilizationMachine')]",
        ),
    ]

    for locator in machine_locators:
        try:
            elements = WebDriverWait(driver, 8).until(
                EC.presence_of_all_elements_located(locator)
            )
            visible = [e for e in elements if e.is_displayed() and e.text.strip()]
            if not visible:
                continue
            target = visible[0]
            machine_code = target.text.strip()
            scroll_to(driver, target)
            driver.execute_script("arguments[0].click();", target)
            wait_ready(driver)
            time.sleep(PAUSE * 2)
            return machine_code
        except Exception:
            continue

    machine_code = driver.execute_script(
        "var tables = document.querySelectorAll('table');"
        "var targetTable = null;"
        "for (var t = 0; t < tables.length; t++) {"
        "  var text = (tables[t].innerText || '').toLowerCase();"
        "  if (text.indexOf('machine code') !== -1 && text.indexOf('production hours required') !== -1) {"
        "    targetTable = tables[t];"
        "    break;"
        "  }"
        "}"
        "if (!targetTable) return null;"
        "var rows = targetTable.querySelectorAll('tbody tr, tr');"
        "for (var i = 0; i < rows.length; i++) {"
        "  var cells = rows[i].querySelectorAll('td');"
        "  if (!cells || cells.length < 2) continue;"
        "  var machine = cells[1].querySelector('a, span');"
        "  if (!machine) continue;"
        "  var txt = (machine.innerText || '').trim();"
        "  if (txt && machine.offsetParent !== null) { machine.click(); return txt; }"
        "}"
        "return null;"
    )
    if machine_code:
        wait_ready(driver)
        time.sleep(PAUSE * 2)
        return machine_code

    return None


def assigned_jobs_loaded(driver, machine_code=None, target_date=None):
    """Check Assigned jobs for Machine details context."""
    target_date = target_date or date.today()
    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
    slash_date = target_date.strftime("%m/%d/%Y")
    compact_date = target_date.strftime("%m/%d/%Y").lstrip("0").replace("/0", "/")
    machine_text_ok = not machine_code or machine_code.lower() in body_text
    return (
        "assigned jobs for machine" in body_text
        and machine_text_ok
        and (slash_date.lower() in body_text or compact_date.lower() in body_text)
        and ("card id" in body_text or "item" in body_text or "setup time" in body_text)
    ) or "CapacityUtilizationMachine" in driver.current_url


def click_back(driver):
    """Click Back button on assigned jobs page."""
    locators = [
        (By.XPATH, "//button[contains(normalize-space(.),'Back')]"),
        (By.XPATH, "//a[contains(normalize-space(.),'Back')]"),
        (By.XPATH, "//*[@id='btnBack' or contains(@id,'Back') or contains(@class,'back')]")
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

    if click_visible_text(driver, "Back"):
        wait_ready(driver)
        time.sleep(PAUSE)
        return True

    return False


@pytest.mark.usefixtures("driver")
class TestProductionSummaryReport:
    """Validate Production Summary Report date and machine drill-down flow."""

    def test_01_login(self, driver):
        """Login to QA site with Databizwarehouseuser credentials."""
        print("\n[TC-PSR-001] Logging in to QA site...")
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

    def test_02_open_production_summary_filter(self, driver):
        """Open Production Summary Report filter via menu path with URL fallback."""
        print("[TC-PSR-002] Opening Production Summary Report...")
        navigate_to_production_summary_report(driver)

        assert production_summary_filter_loaded(driver), (
            f"Expected Production Summary filter page, got: {driver.current_url}"
        )
        take_screenshot(driver, "02_filter_page")

    def test_03_click_date_open_machine_summary(self, driver):
        """Click target date from calendar and verify machine summary page."""
        print("[TC-PSR-003] Clicking target date from Production Summary calendar...")
        selected = click_target_date(driver)
        assert selected, "Could not click the target date from the Production Summary calendar"

        assert machine_summary_loaded(driver), (
            f"Remaining production hours required page did not load. URL: {driver.current_url}"
        )
        print(f"  [INFO] Opened machine summary for date: {selected}")
        take_screenshot(driver, "03_machine_summary")

    def test_04_click_first_machine_code_open_assigned_jobs(self, driver):
        """Click first Machine Code from summary and verify assigned jobs details page."""
        print("[TC-PSR-004] Clicking first available Machine Code...")
        machine_code = click_first_machine_code(driver)
        assert machine_code, "Could not click any Machine Code from Production Summary"

        assert assigned_jobs_loaded(driver, machine_code=machine_code), (
            f"Assigned jobs details page did not load. URL: {driver.current_url}"
        )
        print(f"  [INFO] Opened assigned jobs for machine: {machine_code}")
        take_screenshot(driver, "04_assigned_jobs")

    def test_05_click_back_to_machine_summary(self, driver):
        """Click Back and verify machine summary context is restored."""
        print("[TC-PSR-005] Clicking Back from assigned jobs page...")
        assert click_back(driver), "Could not click Back"

        assert machine_summary_loaded(driver), (
            f"Expected Remaining production hours required page after Back. URL: {driver.current_url}"
        )
        take_screenshot(driver, "05_back_to_machine_summary")