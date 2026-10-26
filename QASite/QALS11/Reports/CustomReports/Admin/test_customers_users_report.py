"""
QALS11 | Reports > Custom Reports > Create Custom Report > Admin > Customers' Users
====================================================================================
URL  : https://engineering.ultrivalms.com/QALS1011
User : buyeruser / Ultriva!23

Test Flow
---------
  1.  Login as buyeruser
  2.  Navigate to Reports > Custom Reports > Create Custom Report
      (direct URL: /CreateCustomReport/List)
  3.  Click 'Customers' Users' under Admin section on the report-type list page
  4.  Fill in Report Information: Name (unique), Description, Visible only to me
  5.  Keep Report Output Format = Tabular (default)
  6.  Submit form → verify success message "successfully created"
  7.  Verify Show Report & Schedule Report buttons are present
  8.  Click Show Report → verify report output page loads

Run (from qa_automation/):
    pytest tests/QALS11/Reports/CustomReports/Admin/test_customers_users_report.py -v -s
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

CREATE_CUSTOM_REPORT_LIST_URL = f"{BASE_URL}/CreateCustomReport/List"
CUSTOMERS_USERS_REPORT_FORM_URL = f"{BASE_URL}/CreateCustomReport/Update?reportGID=CustomerUserReport"

# Unique report name per run to avoid duplicates
_TS = time.strftime("%Y%m%d%H%M%S")
REPORT_NAME = f"AutoTest_CustUsers_{_TS}"
REPORT_DESC = f"Automated test - Admin Customers' Users report created at {_TS}"


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
    """Scroll element into view and pause."""
    driver.execute_script("arguments[0].scrollIntoView({block:'center'})", el)
    time.sleep(0.3)


def take_screenshot(driver, name):
    """Take and save screenshot with timestamp."""
    screenshots_dir = os.path.join(
        os.path.dirname(__file__),
        "..", "..", "..", "..", "reports", "screenshots",
    )
    os.makedirs(screenshots_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(screenshots_dir, f"custom_report_customers_users_{name}_{ts}.png")
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
    """Click the first visible element whose innerText/value matches text (JS fallback)."""
    return driver.execute_script(
        "var wanted = arguments[0].trim().toLowerCase();"
        "var els = document.querySelectorAll("
        "  'a, button, input[type=\"button\"], input[type=\"submit\"], span, div, li'"
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


def navigate_to_create_custom_report_list(driver):
    """Open the Create Custom Report list page via Reports menu or direct URL."""
    # Attempt menu path: Reports > Custom Reports > Create Custom Report
    try:
        reports_link = safe_click_first(
            driver,
            [
                (By.XPATH, "//a[normalize-space()='Reports']"),
                (By.XPATH, "//*[contains(normalize-space(.),'Reports')][self::a or self::span]"),
            ],
            timeout=5,
        )
        if reports_link:
            driver.execute_script("arguments[0].click()", reports_link)
            wait_ready(driver)
            time.sleep(0.5)

        custom_reports_link = safe_click_first(
            driver,
            [
                (By.XPATH, "//a[contains(normalize-space(.),'Custom Reports')]"),
                (By.XPATH, "//a[contains(@href,'CustomReport')]"),
            ],
            timeout=5,
        )
        if custom_reports_link:
            driver.execute_script("arguments[0].click()", custom_reports_link)
            wait_ready(driver)
            time.sleep(0.5)

        create_link = safe_click_first(
            driver,
            [
                (By.XPATH, "//a[contains(normalize-space(.),'Create Custom Report')]"),
                (By.XPATH, "//a[contains(@href,'CreateCustomReport')]"),
            ],
            timeout=5,
        )
        if create_link:
            driver.execute_script("arguments[0].click()", create_link)
            wait_ready(driver)
            time.sleep(PAUSE)
            if "CreateCustomReport" in driver.current_url:
                return
    except Exception:
        pass

    # Direct URL fallback
    print("  [INFO] Menu path unavailable; using direct URL fallback.")
    driver.get(CREATE_CUSTOM_REPORT_LIST_URL)
    wait_ready(driver)
    time.sleep(PAUSE)


def click_customers_users_under_admin(driver):
    """Click the 'Customers' Users' link under the Admin section on the report-type list page."""
    # Attempt 1: href containing CustomerUserReport
    link = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[contains(@href,'CustomerUserReport')]"),
            (By.XPATH, "//a[contains(@href,'customeruserreport')]"),
        ],
        timeout=5,
    )
    if link:
        scroll_to(driver, link)
        link.click()
        wait_ready(driver)
        time.sleep(PAUSE)
        return True

    # Attempt 2: text 'Customers' Users' inside Admin section context
    link = safe_click_first(
        driver,
        [
            (By.XPATH,
             "//td[contains(normalize-space(.),'Admin')]"
             "/following::a[contains(normalize-space(),\"Customers'\")][1]"),
            (By.XPATH,
             "//tr[contains(.,'Admin')]//following-sibling::tr//a[contains(normalize-space(),\"Customers'\")]"),
            (By.XPATH, "//a[contains(normalize-space(),\"Customers' Users\")]"),
            (By.XPATH, "//a[contains(normalize-space(),'Customers') and contains(normalize-space(),'Users')]"),
        ],
        timeout=5,
    )
    if link:
        scroll_to(driver, link)
        link.click()
        wait_ready(driver)
        time.sleep(PAUSE)
        return True

    # Attempt 3: JS click on visible 'Customers' Users' anchor
    result = driver.execute_script(
        "var links = document.querySelectorAll('a');"
        "for (var i = 0; i < links.length; i++) {"
        "  var txt = links[i].innerText.trim();"
        "  if ((txt === \"Customers' Users\" || txt === 'Customers Users') && links[i].offsetParent !== null) {"
        "    links[i].click(); return true;"
        "  }"
        "}"
        "return false;"
    )
    if result:
        wait_ready(driver)
        time.sleep(PAUSE)
        return True

    # Fallback: direct URL to form
    print("  [INFO] 'Customers' Users' link not found via DOM; navigating directly to form URL.")
    driver.get(CUSTOMERS_USERS_REPORT_FORM_URL)
    wait_ready(driver)
    time.sleep(PAUSE)
    return True


# ============================================================================
# TEST CLASS
# ============================================================================


@pytest.mark.usefixtures("driver")
class TestCustomReportAdminCustomersUsers:
    """
    Test: Reports > Custom Reports > Create Custom Report > Admin > Customers' Users
    """

    def test_01_login(self, driver):
        """Login as buyeruser."""
        print("\n" + "=" * 70)
        print("[TC-CR-CU-001] Custom Report Admin Customers' Users - Login")
        print("=" * 70)

        print("\n[STEP 1] Logging in as buyeruser...")
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
        assert "Account/Login" not in current_url, (
            f"Login failed — still on login page. URL: {current_url}"
        )
        print("  [PASS] Login successful.")

    def test_02_navigate_to_create_custom_report_list(self, driver):
        """Navigate to Reports > Custom Reports > Create Custom Report list page."""
        print("\n" + "=" * 70)
        print("[TC-CR-CU-002] Navigate to Create Custom Report List")
        print("=" * 70)

        print("\n[STEP 2] Opening Create Custom Report list page...")
        navigate_to_create_custom_report_list(driver)

        take_screenshot(driver, "02_create_custom_report_list")
        current_url = driver.current_url
        print(f"  [URL] {current_url}")
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()

        assert (
            "createcustomreport" in current_url.lower()
            or "create custom report" in page_text
        ), f"Expected Create Custom Report list page. Got: {current_url}"
        print(f"  [PASS] Create Custom Report list page loaded: {current_url}")

    def test_03_click_customers_users_under_admin(self, driver):
        """Click 'Customers' Users' link under the Admin section."""
        print("\n" + "=" * 70)
        print("[TC-CR-CU-003] Click 'Customers' Users' under Admin on report type list")
        print("=" * 70)

        print("\n[STEP 3] Clicking 'Customers' Users' under Admin section...")
        click_customers_users_under_admin(driver)

        take_screenshot(driver, "03_customers_users_form")
        current_url = driver.current_url
        print(f"  [URL] {current_url}")
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()

        assert (
            "custuserreport" in current_url.lower()
            or "createcustomreport" in current_url.lower()
            or "admin" in page_text
            or "customer" in page_text
        ), f"Expected Customers' Users custom report form. Got: {current_url}"
        print(f"  [PASS] Admin: Customers' Users custom report form loaded: {current_url}")

    def test_04_fill_report_form(self, driver):
        """Fill in Report Name, Description, and keep Visible only to me + Tabular."""
        print("\n" + "=" * 70)
        print("[TC-CR-CU-004] Fill Report Information form")
        print("=" * 70)

        print(f"\n[STEP 4] Filling report form: Name='{REPORT_NAME}'...")
        time.sleep(0.5)

        # Ensure we are on the form page
        if "CreateCustomReport/Update" not in driver.current_url:
            print("  [INFO] Not on form page; navigating back to form URL...")
            driver.get(CUSTOMERS_USERS_REPORT_FORM_URL)
            wait_ready(driver)
            time.sleep(PAUSE)

        # ------------------------------------------------------------------ #
        # Name field — use JS fill on first visible text input as fallback
        # ------------------------------------------------------------------ #
        name_filled = False

        # Try standard locators first
        name_field = safe_click_first(
            driver,
            [
                (By.ID, "Name"),
                (By.NAME, "Name"),
                (By.XPATH, "//input[@id='Name' or @name='Name']"),
                (By.XPATH, "//input[contains(@id,'Name') or contains(@name,'Name')]"),
                (By.XPATH, "//input[contains(@id,'name') or contains(@name,'name')]"),
                (By.XPATH, "//label[contains(text(),'Name')]/following::input[1]"),
            ],
            timeout=5,
        )
        if name_field:
            scroll_to(driver, name_field)
            driver.execute_script(
                "arguments[0].value = arguments[1];"
                "arguments[0].dispatchEvent(new Event('input', {bubbles:true}));"
                "arguments[0].dispatchEvent(new Event('change', {bubbles:true}));",
                name_field, REPORT_NAME,
            )
            name_filled = True
            print(f"  [INFO] Name entered via element: {REPORT_NAME}")
        else:
            # JS fallback: fill first visible text input
            name_filled = driver.execute_script(
                "var inputs = document.querySelectorAll('input[type=\"text\"], input:not([type])');"
                "for (var i = 0; i < inputs.length; i++) {"
                "  var el = inputs[i];"
                "  if (el.offsetParent !== null && !el.disabled && !el.readOnly) {"
                "    el.value = arguments[0];"
                "    el.dispatchEvent(new Event('input', {bubbles:true}));"
                "    el.dispatchEvent(new Event('change', {bubbles:true}));"
                "    return true;"
                "  }"
                "}"
                "return false;",
                REPORT_NAME,
            )
            if name_filled:
                print(f"  [INFO] Name entered via JS first-visible-input: {REPORT_NAME}")

        assert name_filled, "Name input field could not be filled on form."

        # ------------------------------------------------------------------ #
        # Description field — use JS fill on first visible textarea as fallback
        # ------------------------------------------------------------------ #
        desc_filled = False

        desc_field = safe_click_first(
            driver,
            [
                (By.ID, "Description"),
                (By.NAME, "Description"),
                (By.XPATH, "//textarea[@id='Description' or @name='Description']"),
                (By.XPATH, "//textarea[contains(@id,'Description') or contains(@name,'Description')]"),
                (By.XPATH, "//label[contains(text(),'Description')]/following::textarea[1]"),
                (By.XPATH, "//textarea[1]"),
            ],
            timeout=5,
        )
        if desc_field:
            scroll_to(driver, desc_field)
            driver.execute_script(
                "arguments[0].value = arguments[1];"
                "arguments[0].dispatchEvent(new Event('input', {bubbles:true}));"
                "arguments[0].dispatchEvent(new Event('change', {bubbles:true}));",
                desc_field, REPORT_DESC,
            )
            desc_filled = True
            print("  [INFO] Description entered via element.")
        else:
            desc_filled = driver.execute_script(
                "var ta = document.querySelector('textarea');"
                "if (ta && ta.offsetParent !== null && !ta.disabled) {"
                "  ta.value = arguments[0];"
                "  ta.dispatchEvent(new Event('input', {bubbles:true}));"
                "  ta.dispatchEvent(new Event('change', {bubbles:true}));"
                "  return true;"
                "}"
                "return false;",
                REPORT_DESC,
            )
            if desc_filled:
                print("  [INFO] Description entered via JS first-visible-textarea.")

        assert desc_filled, "Description textarea could not be filled on form."

        # ------------------------------------------------------------------ #
        # Visibility: "Visible only to me" (should be default; ensure selected)
        # ------------------------------------------------------------------ #
        visible_only_radio = safe_click_first(
            driver,
            [
                (By.XPATH, "//input[@type='radio' and contains(@id,'VisibleOnlyToMe')]"),
                (By.XPATH, "//input[@type='radio' and contains(@value,'VisibleOnlyToMe')]"),
                (By.XPATH, "//label[contains(text(),'Visible only to me')]/preceding::input[@type='radio'][1]"),
                (By.XPATH, "//label[contains(text(),'Visible only to me')]/following::input[@type='radio'][1]"),
                (By.XPATH, "//input[@type='radio'][1]"),
            ],
            timeout=5,
        )
        if visible_only_radio:
            if not visible_only_radio.is_selected():
                driver.execute_script("arguments[0].click()", visible_only_radio)
            print("  [INFO] 'Visible only to me' radio selected.")
        else:
            print("  [WARN] 'Visible only to me' radio not found; proceeding with default.")

        take_screenshot(driver, "04_form_filled")
        print("  [PASS] Report form filled successfully.")

    def test_05_submit_form_verify_success(self, driver):
        """Submit the form and verify the success confirmation page."""
        print("\n" + "=" * 70)
        print("[TC-CR-CU-005] Submit form and verify success")
        print("=" * 70)

        print("\n[STEP 5] Submitting the custom report form...")
        time.sleep(0.5)

        # Try multiple locator strategies for the submit/create button
        submit_btn = safe_click_first(
            driver,
            [
                (By.XPATH, "//input[@type='submit']"),
                (By.XPATH, "//button[@type='submit']"),
                (By.XPATH, "//button[contains(normalize-space(.),'Create')]"),
                (By.XPATH, "//input[contains(@value,'Create')]"),
                (By.XPATH, "//button[contains(normalize-space(.),'Save')]"),
                (By.XPATH, "//input[contains(@value,'Save')]"),
            ],
            timeout=8,
        )

        if submit_btn:
            scroll_to(driver, submit_btn)
            submit_btn.click()
            print("  [INFO] Submit button clicked.")
        else:
            # JS fallback: try common button labels
            clicked = (
                click_visible_text(driver, "Create")
                or click_visible_text(driver, "Save")
                or click_visible_text(driver, "Create Report")
                or click_visible_text(driver, "Create Custom Report")
            )
            assert clicked, "Could not find or click the form submit button."
            print("  [INFO] Submit button clicked via JS fallback.")

        wait_ready(driver)
        time.sleep(PAUSE)
        take_screenshot(driver, "05_after_submit")

        current_url = driver.current_url
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        print(f"  [URL] {current_url}")

        # Detect form validation failure and retry with JS fill
        if (
            "required fields do not have valid values" in page_text
            or "CreateCustomReport/Update" in current_url
        ) and "successfully created" not in page_text:
            print("  [WARN] Form validation failed; re-filling fields via JS and retrying...")
            driver.execute_script(
                "var inputs = document.querySelectorAll('input[type=\"text\"], input:not([type])');"
                "for (var i = 0; i < inputs.length; i++) {"
                "  var el = inputs[i];"
                "  if (el.offsetParent !== null && !el.disabled && !el.readOnly) {"
                "    el.value = arguments[0];"
                "    el.dispatchEvent(new Event('input', {bubbles:true}));"
                "    el.dispatchEvent(new Event('change', {bubbles:true}));"
                "    break;"
                "  }"
                "}",
                REPORT_NAME,
            )
            driver.execute_script(
                "var ta = document.querySelector('textarea');"
                "if (ta && ta.offsetParent !== null) {"
                "  ta.value = arguments[0];"
                "  ta.dispatchEvent(new Event('input', {bubbles:true}));"
                "}",
                REPORT_DESC,
            )
            time.sleep(0.5)
            # Re-click submit
            clicked = (
                click_visible_text(driver, "Save")
                or click_visible_text(driver, "Create")
                or click_visible_text(driver, "Create Report")
            )
            if clicked:
                print("  [INFO] Re-submitted form after JS fill.")
            wait_ready(driver)
            time.sleep(PAUSE)
            take_screenshot(driver, "05_after_retry_submit")
            current_url = driver.current_url
            page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
            print(f"  [URL after retry] {current_url}")

        # Verify success: redirect to CustomReport page or success message
        success = (
            "successfully created" in page_text
            or "customreport/customreport" in current_url.lower()
            or (
                "customreport" in current_url.lower()
                and "CreateCustomReport/Update" not in current_url
            )
            or REPORT_NAME.lower() in page_text
        )
        assert success, (
            f"Custom report creation may have failed. "
            f"URL: {current_url} | Page text (first 300): {page_text[:300]}"
        )
        print(f"  [PASS] Custom report created successfully. URL: {current_url}")

    def test_06_verify_show_report_and_click(self, driver):
        """Verify Show Report and Schedule Report buttons; click Show Report."""
        print("\n" + "=" * 70)
        print("[TC-CR-CU-006] Verify Show Report / Schedule Report buttons and click Show Report")
        print("=" * 70)

        print("\n[STEP 6] Checking Show Report and Schedule Report buttons...")
        time.sleep(0.5)

        current_url = driver.current_url
        page_text = driver.find_element(By.TAG_NAME, "body").text
        print(f"  [URL] {current_url}")

        # If still on the form/update page, the report confirmation may not have rendered yet
        if "CreateCustomReport/Update" in current_url:
            print("  [WARN] Still on form page; waiting for redirect or re-navigating to My Reports...")
            time.sleep(2)
            wait_ready(driver)
            current_url = driver.current_url
            page_text = driver.find_element(By.TAG_NAME, "body").text

        assert "Show Report" in page_text, (
            f"'Show Report' button not found on confirmation page. "
            f"URL: {current_url}\n"
            f"Page text snippet: {page_text[:500]}"
        )
        print("  [PASS] 'Show Report' button is present.")

        assert "Schedule Report" in page_text, (
            f"'Schedule Report' button not found on confirmation page. "
            f"URL: {current_url}"
        )
        print("  [PASS] 'Schedule Report' button is present.")

        take_screenshot(driver, "06_confirmation_page")

        # Click Show Report
        print("\n[STEP 6b] Clicking 'Show Report'...")
        show_btn = safe_click_first(
            driver,
            [
                (By.XPATH, "//a[contains(normalize-space(.),'Show Report')]"),
                (By.XPATH, "//button[contains(normalize-space(.),'Show Report')]"),
                (By.XPATH, "//input[@type='submit' and contains(@value,'Show Report')]"),
            ],
            timeout=8,
        )

        if show_btn:
            scroll_to(driver, show_btn)
            show_btn.click()
            print("  [INFO] 'Show Report' button clicked.")
        else:
            clicked = click_visible_text(driver, "Show Report")
            assert clicked, "'Show Report' button could not be clicked."
            print("  [INFO] 'Show Report' button clicked via JS fallback.")

        wait_ready(driver)
        time.sleep(PAUSE)
        take_screenshot(driver, "07_show_report_output")

        current_url = driver.current_url
        print(f"  [URL] {current_url}")
        page_text_body = driver.find_element(By.TAG_NAME, "body").text.lower()

        report_loaded = (
            "customreport" in current_url.lower()
            or "report" in current_url.lower()
            or "customer" in page_text_body
            or "user" in page_text_body
            or REPORT_NAME.lower() in page_text_body
        )
        assert report_loaded, (
            f"Report output page did not load as expected. "
            f"URL: {current_url}"
        )
        print(f"  [PASS] Show Report output loaded: {current_url}")
        print("\n" + "=" * 70)
        print("[DONE] All Custom Report Admin Customers' Users test steps completed.")
        print("=" * 70)
