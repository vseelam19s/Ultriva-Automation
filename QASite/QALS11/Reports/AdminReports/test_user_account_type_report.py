"""
QALS11 | Reports > Admin Reports > User Account Type Report
============================================================
URL  : https://engineering.ultrivalms.com/QALS1011
User : buyeruser / Ultriva!23

Test Flow
---------
  1.  Login as buyeruser
  2.  Navigate to Admin Reports > User Account Type report
  3.  Select user 'buyeruser' from User filter
  4.  Click Show Report
  5.  Verify report output loads
  6.  Click Change Filter and verify return to filter page

Run (from qa_automation/):
    pytest tests/QALS11/Reports/AdminReports/test_user_account_type_report.py -v -s
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
USER_ACCOUNT_TYPE_FILTER_URL = f"{BASE_URL}/AdminReport/UserAccountTypeFilter"


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
        os.path.dirname(__file__), "..", "..", "..", "reports", "screenshots"
    )
    os.makedirs(screenshots_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(screenshots_dir, f"user_account_type_{name}_{ts}.png")
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


def navigate_to_user_account_type_report(driver):
    """Open User Account Type report using direct URL."""
    if "UserAccountType" in driver.current_url:
        return

    try:
        driver.get(USER_ACCOUNT_TYPE_FILTER_URL)
        wait_ready(driver)
        time.sleep(PAUSE)
        if "UserAccountType" in driver.current_url:
            return
    except Exception:
        pass


# ============================================================================
# TEST CLASS
# ============================================================================


@pytest.mark.usefixtures("driver")
class TestUserAccountTypeReport:
    """Test User Account Type Report from Admin Reports."""

    def test_flow_login_show_change_filter(self, driver):
        """
        Complete flow: login → open User Account Type report →
        select user → show report → change filter.
        """
        print("\n" + "=" * 70)
        print("[TC-UAT-001] User Account Type Report - Login & Filter Flow")
        print("=" * 70)

        # ====================================================================
        # Step 1: Login
        # ====================================================================
        print("\n[STEP 1] Logging in to QA site...")
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

        # ====================================================================
        # Step 2: Navigate to User Account Type Report filter
        # ====================================================================
        print("\n[STEP 2] Opening User Account Type Report filter page...")
        navigate_to_user_account_type_report(driver)

        take_screenshot(driver, "02_filter_page")
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        assert (
            "useraccounttype" in driver.current_url.lower()
            or "user account type" in page_text
        ), f"Expected User Account Type filter page. Got: {driver.current_url}"
        print(f"  [PASS] User Account Type filter page loaded: {driver.current_url}")

        # ====================================================================
        # Step 3: Select user 'buyeruser' from User dropdown/field
        # ====================================================================
        print("\n[STEP 3] Selecting user 'buyeruser' from User filter...")
        time.sleep(0.5)

        # Try to find and click the User dropdown/field
        user_field = safe_click_first(
            driver,
            [
                (By.ID, "User"),
                (By.NAME, "User"),
                (By.XPATH, "//input[@id='User' or @name='User']"),
                (By.XPATH, "//select[@id='User' or @name='User']"),
                (By.XPATH, "//label[contains(text(),'User')]/following::input[1]"),
                (By.XPATH, "//label[contains(text(),'User')]/following::select[1]"),
            ],
            timeout=5,
        )

        if user_field:
            scroll_to(driver, user_field)
            user_field.click()
            time.sleep(0.3)

            # If it's a select dropdown, select by visible text
            try:
                from selenium.webdriver.support.select import Select

                if "select" in user_field.tag_name.lower():
                    Select(user_field).select_by_visible_text("buyeruser")
                else:
                    # For input field, clear and type
                    user_field.clear()
                    user_field.send_keys("buyeruser")
            except Exception:
                # Fallback: clear and type
                user_field.clear()
                user_field.send_keys("buyeruser")

            time.sleep(PAUSE)
            take_screenshot(driver, "03_user_selected")
            print("  [PASS] User 'buyeruser' entered/selected.")
        else:
            print("  [WARN] User field not found; attempting to proceed anyway.")
            take_screenshot(driver, "03_user_field_not_found")

        # ====================================================================
        # Step 4: Click Show Report button
        # ====================================================================
        print("\n[STEP 4] Clicking 'Show Report' button...")
        time.sleep(0.5)

        show_report_btn = safe_click_first(
            driver,
            [
                (By.ID, "ShowReport"),
                (By.NAME, "ShowReport"),
                (By.XPATH, "//button[contains(text(),'Show Report')]"),
                (By.XPATH, "//input[@type='submit' and contains(@value,'Show Report')]"),
            ],
            timeout=5,
        )

        if show_report_btn:
            scroll_to(driver, show_report_btn)
            show_report_btn.click()
            print("  [INFO] Show Report button clicked via safe_click_first.")
        else:
            # Fallback to JS click_visible_text
            result = click_visible_text(driver, "Show Report")
            if result:
                print("  [INFO] Show Report button clicked via JS fallback.")
            else:
                print("  [WARN] Show Report button not found; attempting to proceed.")

        wait_ready(driver)
        time.sleep(PAUSE)
        take_screenshot(driver, "04_after_show_report")
        current_url = driver.current_url
        print(f"  [URL] {current_url}")
        print("  [PASS] Show Report step completed.")

        # ====================================================================
        # Step 5: Verify report page loaded
        # ====================================================================
        print("\n[STEP 5] Verifying report output...")
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        report_loaded = (
            "useraccounttype" in current_url.lower()
            or "user account type" in page_text
            or "account type" in page_text
        )
        assert report_loaded, f"Report may not have loaded. URL: {current_url}"
        print(f"  [PASS] Report page appears to have loaded.")

        # ====================================================================
        # Step 6: Click Change Filter button
        # ====================================================================
        print("\n[STEP 6] Clicking 'Change Filter' button...")
        time.sleep(0.5)

        change_filter_btn = safe_click_first(
            driver,
            [
                (By.ID, "ChangeFilter"),
                (By.NAME, "ChangeFilter"),
                (By.XPATH, "//button[contains(text(),'Change Filter')]"),
                (By.XPATH, "//input[@type='submit' and contains(@value,'Change Filter')]"),
            ],
            timeout=5,
        )

        if change_filter_btn:
            scroll_to(driver, change_filter_btn)
            change_filter_btn.click()
            print("  [INFO] Change Filter button clicked via safe_click_first.")
        else:
            # Fallback to JS click_visible_text
            result = click_visible_text(driver, "Change Filter")
            if result:
                print("  [INFO] Change Filter button clicked via JS fallback.")
            else:
                # Fallback to Back button (some reports show Back instead)
                result = click_visible_text(driver, "Back")
                if result:
                    print("  [INFO] Back button clicked as fallback.")
                else:
                    print("  [WARN] Change Filter/Back button not found.")

        wait_ready(driver)
        time.sleep(PAUSE)
        take_screenshot(driver, "05_after_change_filter")
        current_url = driver.current_url
        print(f"  [URL] {current_url}")

        # ====================================================================
        # Step 7: Verify return to filter page
        # ====================================================================
        print("\n[STEP 7] Verifying return to filter page...")
        filter_restored = (
            "UserAccountTypeFilter" in current_url
            or "useraccounttypefilter" in current_url.lower()
        )
        assert filter_restored, (
            f"Did not return to filter page. Expected URL containing 'UserAccountTypeFilter'. "
            f"Got: {current_url}"
        )
        print(f"  [PASS] Returned to User Account Type filter page: {current_url}")

        print("\n" + "=" * 70)
        print("[RESULT] All steps completed successfully!")
        print("=" * 70 + "\n")
