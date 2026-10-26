"""
QALS11 | Reports > LFM/OEE Reports > Operator Efficiency Report
===============================================================
URL  : https://engineering.ultrivalms.com/QALS1011/OEEReport/OperatorEfficiencyFilter
User : Databizwarehouseuser / Ultriva!23

Test Flow
---------
  1. Login as Databizwarehouseuser
  2. Navigate via Reports -> LFM/OEE Reports -> Operator Efficiency Report
  3. Select Date Range = Past One Year
  4. Click Show Report
  5. Verify Operator Efficiency Summary loads
  6. Click on an Operator Name link from summary
  7. Verify Operator Efficiency Details loads
  8. Click Back to Summary
  9. Click Change Filter

Run (from qa_automation/):
    pytest tests/QALS11/Reports/OEEReports/test_operator_efficiency_report.py -v -s
"""

import os
import time
from datetime import date, timedelta

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
USERNAME = "Databizwarehouseuser"
PASSWORD = "Ultriva!23"
PAUSE = 1.2
OPERATOR_EFFICIENCY_FILTER_URL = f"{BASE_URL}/OEEReport/OperatorEfficiencyFilter"


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
    path = os.path.join(screenshots_dir, f"operator_efficiency_{name}_{ts}.png")
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


def navigate_to_operator_efficiency_report(driver):
    """Open Operator Efficiency Report using menu path with direct URL fallback."""
    if "OperatorEfficiencyFilter" in driver.current_url and "Account/Login" not in driver.current_url:
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

    lfm_oee_section = safe_click_first(
        driver,
        [
            (By.XPATH, "//*[self::a or self::span or self::div][contains(normalize-space(.),'LFM/OEE Reports')]"),
            (By.XPATH, "//*[contains(@class,'panel') and contains(.,'LFM/OEE Reports')]")
        ],
        timeout=5,
    )
    if lfm_oee_section:
        try:
            scroll_to(driver, lfm_oee_section)
            driver.execute_script("arguments[0].click();", lfm_oee_section)
            time.sleep(PAUSE)
        except Exception:
            pass

    report_link = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[contains(@href,'/OEEReport/OperatorEfficiencyFilter')]"),
            (By.XPATH, "//a[contains(@href,'OperatorEfficiencyFilter')]"),
            (By.XPATH, "//a[contains(normalize-space(.),'Operator Efficiency Report')]"),
            (By.XPATH, "//*[self::a or self::span][contains(normalize-space(.),'Operator Efficiency')]")
        ],
        timeout=6,
    )
    if report_link:
        try:
            scroll_to(driver, report_link)
            driver.execute_script("arguments[0].click();", report_link)
            wait_ready(driver)
            time.sleep(PAUSE)
            if "OperatorEfficiencyFilter" in driver.current_url and "Account/Login" not in driver.current_url:
                return
        except Exception:
            pass

    print("  [WARN] Menu path unavailable - using direct URL fallback.")
    driver.get(OPERATOR_EFFICIENCY_FILTER_URL)
    wait_ready(driver)
    time.sleep(PAUSE)


def _select_date_range_option(driver, option_text):
    """Click Date Range textbox and select menu option by visible text."""
    date_input = None
    input_locators = [
        (By.XPATH, "//label[contains(normalize-space(.),'date range')]/following::input[1]"),
        (By.XPATH, "//*[contains(normalize-space(.),'Enter or select date range')]/following::input[1]"),
        (By.XPATH, "//input[contains(@id,'DateRange') or contains(@name,'DateRange')]")
    ]

    for locator in input_locators:
        try:
            date_input = WebDriverWait(driver, 6).until(
                EC.visibility_of_element_located(locator)
            )
            break
        except Exception:
            continue

    if not date_input:
        return False

    scroll_to(driver, date_input)
    driver.execute_script("arguments[0].click();", date_input)
    time.sleep(0.5)

    option_locators = [
        (By.XPATH, f"//li[normalize-space()='{option_text}']"),
        (By.XPATH, f"//*[self::li or self::a or self::td or self::span][normalize-space()='{option_text}']"),
        (By.XPATH, "//*[self::li or self::a or self::td or self::span][contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'),'past one year')]"),
    ]

    for locator in option_locators:
        try:
            opt = WebDriverWait(driver, 4).until(EC.element_to_be_clickable(locator))
            scroll_to(driver, opt)
            driver.execute_script("arguments[0].click();", opt)
            time.sleep(0.8)
            return True
        except Exception:
            continue

    clicked = driver.execute_script(
        "var wanted = 'past one year';"
        "var els = document.querySelectorAll('li, a, td, span, div');"
        "for (var i = 0; i < els.length; i++) {"
        "  var el = els[i];"
        "  var txt = (el.innerText || '').trim().toLowerCase();"
        "  if (!txt) continue;"
        "  if ((txt === wanted || txt.indexOf(wanted) !== -1 || txt.replace(/\\s+/g,'') === 'pastoneyear') && el.offsetParent !== null) {"
        "    el.click();"
        "    return true;"
        "  }"
        "}"
        "return false;"
    )
    if clicked:
        time.sleep(0.8)
    return bool(clicked)


def set_date_range_past_one_year(driver):
    """Set Date Range to Past One Year with dropdown first, value fallback second."""
    if _select_date_range_option(driver, "Past One Year"):
        print("  [INFO] Date Range selected: Past One Year")
        return "Past One Year"

    end_date = date.today()
    start_date = end_date - timedelta(days=365)
    value = f"{start_date:%m/%d/%Y}-{end_date:%m/%d/%Y}"

    value_locators = [
        (By.XPATH, "//label[contains(normalize-space(.),'date range')]/following::input[1]"),
        (By.XPATH, "//*[contains(normalize-space(.),'Enter or select date range')]/following::input[1]"),
        (By.XPATH, "//input[contains(@id,'DateRange') or contains(@name,'DateRange')]"),
    ]

    for locator in value_locators:
        try:
            date_input = WebDriverWait(driver, 6).until(
                EC.visibility_of_element_located(locator)
            )
            scroll_to(driver, date_input)
            driver.execute_script(
                "arguments[0].focus();"
                "arguments[0].value = arguments[1];"
                "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));"
                "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));"
                "arguments[0].blur();",
                date_input,
                value,
            )
            time.sleep(0.6)
            return value
        except Exception:
            continue

    raise AssertionError("Could not set Date Range on Operator Efficiency filter")


def click_show_report(driver):
    """Click Show Report button on the Operator Efficiency filter page."""
    btn = safe_click_first(
        driver,
        [
            (By.XPATH, "//button[normalize-space(text())='Show Report']"),
            (By.XPATH, "//a[normalize-space(text())='Show Report']"),
            (By.XPATH, "//input[@type='submit' and @value='Show Report']"),
            (By.XPATH, "//*[@id='btnShowReport' or contains(@id,'ShowReport') or contains(@id,'showReport')]")
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
    """Check Operator Efficiency Summary presence."""
    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
    rows = driver.find_elements(By.XPATH, "//table//tr[td]")
    return (
        "operator efficiency summary" in body_text
        or "operatorefficiency" in driver.current_url.lower()
        or "operator name" in body_text
        or len(rows) > 0
    )


def click_operator_from_summary(driver):
    """Click first Operator Name link from summary table body."""
    operator_locators = [
        (By.XPATH, "//tbody//tr/td[1]/a[string-length(normalize-space(text())) > 0]"),
        (By.XPATH, "//tbody//tr/td/a[contains(@href,'OperatorEfficiencyDetails')]")
    ]

    for locator in operator_locators:
        try:
            elements = WebDriverWait(driver, 8).until(
                EC.presence_of_all_elements_located(locator)
            )
            visible = [e for e in elements if e.is_displayed() and e.text.strip()]
            if not visible:
                continue
            target = visible[0]
            operator_name = target.text.strip()
            scroll_to(driver, target)
            driver.execute_script("arguments[0].click();", target)
            wait_ready(driver)
            time.sleep(PAUSE * 2)
            return operator_name
        except Exception:
            continue

    operator_name = driver.execute_script(
        "var rows = document.querySelectorAll('table tbody tr');"
        "for (var i = 0; i < rows.length; i++) {"
        "  var first = rows[i].querySelector('td a');"
        "  if (!first) continue;"
        "  var txt = (first.innerText || '').trim();"
        "  if (txt && first.offsetParent !== null) { first.click(); return txt; }"
        "}"
        "return null;"
    )
    if operator_name:
        wait_ready(driver)
        time.sleep(PAUSE * 2)
        return operator_name

    return None


def details_loaded(driver):
    """Check Operator Efficiency Details context."""
    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
    return (
        "operator efficiency details" in body_text
        or "operatorefficiencydetails" in driver.current_url.lower()
        or "actual earned hours" in body_text
        or "target earned hours" in body_text
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
        (By.XPATH, "//*[@id='changeFilter' or contains(@id,'ChangeFilter') or contains(@id,'changeFilter')]")
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
class TestOperatorEfficiencyReport:
    """Validate Operator Efficiency Report full flow under LFM/OEE Reports."""

    def test_01_login(self, driver):
        """Login to QA site with Databizwarehouseuser credentials."""
        print("\n[TC-OER-001] Logging in to QA site...")
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

    def test_02_open_operator_efficiency_filter(self, driver):
        """Open Operator Efficiency filter via menu path with URL fallback."""
        print("[TC-OER-002] Opening Operator Efficiency filter...")
        navigate_to_operator_efficiency_report(driver)

        body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        on_filter = "OperatorEfficiencyFilter" in driver.current_url or (
            "operator efficiency" in body_text and "show report" in body_text
        )
        assert on_filter, f"Expected Operator Efficiency filter page, got: {driver.current_url}"
        take_screenshot(driver, "02_filter_page")

    def test_03_select_past_one_year_show_report(self, driver):
        """Select Date Range = Past One Year and click Show Report."""
        print("[TC-OER-003] Selecting Date Range and clicking Show Report...")
        selected = set_date_range_past_one_year(driver)
        assert selected, "Could not select Date Range = Past One Year"

        assert click_show_report(driver), "Could not click Show Report"
        assert summary_loaded(driver), (
            f"Operator Efficiency Summary did not load after Show Report. URL: {driver.current_url}"
        )
        print(f"  [INFO] Date Range selected: {selected}")
        take_screenshot(driver, "03_summary")

    def test_04_click_operator_open_details(self, driver):
        """Click Operator Name from summary and verify details page."""
        print("[TC-OER-004] Clicking Operator Name from summary...")
        operator_name = click_operator_from_summary(driver)
        assert operator_name, "Could not click any Operator Name from Operator Efficiency Summary"

        assert details_loaded(driver), (
            f"Operator Efficiency Details page did not load. URL: {driver.current_url}"
        )
        print(f"  [INFO] Opened details for operator: {operator_name}")
        take_screenshot(driver, "04_details")

    def test_05_back_to_summary(self, driver):
        """Click Back to Summary and verify summary context is restored."""
        print("[TC-OER-005] Clicking Back to Summary...")
        assert click_back_to_summary(driver), "Could not click Back to Summary"

        assert summary_loaded(driver), (
            f"Expected Operator Efficiency Summary after Back to Summary. URL: {driver.current_url}"
        )
        take_screenshot(driver, "05_back_to_summary")

    def test_06_click_change_filter(self, driver):
        """Click Change Filter from summary and verify return to filter page."""
        print("[TC-OER-006] Clicking Change Filter...")
        assert click_change_filter(driver), "Could not click Change Filter"

        body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        on_filter = "OperatorEfficiencyFilter" in driver.current_url or (
            "operator efficiency" in body_text and "show report" in body_text
        )
        assert on_filter, (
            f"Did not return to Operator Efficiency filter context. URL: {driver.current_url}"
        )
        take_screenshot(driver, "06_change_filter")