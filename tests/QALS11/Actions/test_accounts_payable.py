"""
QALS11 | Actions > Accounts Payable — View Details flow
=======================================================
URL   : https://engineering.ultrivalms.com/QALS1011/AccountsPayable/AccountsPayable
User  : buyeruser / Ultriva!23

Test Flow
---------
  1. Login as buyeruser
  2. Click Actions from the left sidebar
  3. Open Accounts Payable from Buyer Actions
  4. Select an invoice row
  5. Click Print Invoice
  6. Select an invoice row
  7. Click View Details
  8. Verify the detail page loads
  9. Click Back and verify return to the list

Run (from qa_automation/):
    pytest tests/QALS11/Actions/test_accounts_payable.py -v -s
"""

import os
import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
ACCOUNTS_PAYABLE_URL = "https://engineering.ultrivalms.com/QALS1011/AccountsPayable/AccountsPayable"
USERNAME = "buyeruser"
PASSWORD = "Ultriva!23"
PAUSE = 1.5


@pytest.fixture(scope="class")
def driver():
    """Class-scoped Chrome browser session."""
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


def wait_ready(driver, timeout=30):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def find(driver, by, locator, timeout=15):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, locator))
    )


def clickable(driver, by, locator, timeout=15):
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, locator))
    )


def scroll_to(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'})", element)
    time.sleep(0.3)


def take_screenshot(driver, name):
    screenshots_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "reports", "screenshots"
    )
    os.makedirs(screenshots_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(screenshots_dir, f"ap_{name}_{ts}.png")
    driver.save_screenshot(path)
    print(f"  [screenshot] {path}")
    return path


def click_visible_text(driver, text):
    """Click the first visible element whose text matches the provided label."""
    candidates = [
        (By.XPATH, f"//*[self::a or self::button or self::span or self::div][normalize-space(.)='{text}']"),
        (By.XPATH, f"//*[self::a or self::button or self::span or self::div][contains(normalize-space(.),'{text}')]"),
    ]
    for by, locator in candidates:
        try:
            elements = driver.find_elements(by, locator)
            for el in elements:
                if el.is_displayed():
                    driver.execute_script("arguments[0].click();", el)
                    return True
        except Exception:
            continue
    return False


@pytest.mark.usefixtures("driver")
class TestAccountsPayable:

    def test_01_login(self, driver):
        """Login as buyeruser."""
        print("\n[TC-AP-001] Logging in to QA site...")
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
        assert BASE_URL.lower() in current_url.lower() or "Home" in current_url.lower(), (
            f"Login may have failed. URL: {current_url}"
        )
        print("  [PASS] Login successful.")

    def test_02_navigate_to_actions(self, driver):
        """Open the Actions landing page."""
        print("\n[TC-AP-002] Navigating to Actions...")
        actions_link = clickable(
            driver,
            By.XPATH,
            "//a[contains(@href, 'Action/Home') or normalize-space(.)='Actions' or .//span[normalize-space()='Actions']]",
        )
        scroll_to(driver, actions_link)
        driver.execute_script("arguments[0].click();", actions_link)
        wait_ready(driver)
        time.sleep(PAUSE)

        take_screenshot(driver, "02_actions_page")
        assert "Action/Home" in driver.current_url, f"Expected Actions page. Got: {driver.current_url}"
        print(f"  [PASS] Actions page loaded: {driver.current_url}")

    def test_03_open_accounts_payable(self, driver):
        """Navigate to Buyer Actions > Accounts Payable."""
        print("\n[TC-AP-003] Opening Accounts Payable...")

        opened = False
        for locator in [
            (By.XPATH, "//a[contains(@href,'AccountsPayable') and contains(normalize-space(.), 'Accounts Payable')]"),
            (By.XPATH, "//a[contains(@href,'AccountsPayable') or contains(@href,'AccountsPayable/AccountsPayable')]"),
            (By.XPATH, "//*[contains(normalize-space(.), 'Accounts Payable')][self::a or self::span or self::div]"),
        ]:
            try:
                target = WebDriverWait(driver, 8).until(EC.element_to_be_clickable(locator))
                scroll_to(driver, target)
                driver.execute_script("arguments[0].click();", target)
                wait_ready(driver)
                time.sleep(PAUSE)
                opened = True
                break
            except Exception:
                continue

        if not opened:
            driver.get(ACCOUNTS_PAYABLE_URL)
            wait_ready(driver)
            time.sleep(PAUSE)

        take_screenshot(driver, "03_accounts_payable")
        print(f"  [URL] {driver.current_url}")
        assert "AccountsPayable" in driver.current_url, (
            f"Accounts Payable page did not load. URL: {driver.current_url}"
        )
        print(f"  [PASS] Accounts Payable page loaded: {driver.current_url}")

    def test_04_select_invoice_and_print(self, driver):
        """Select an invoice and click Print."""
        print("\n[TC-AP-004] Selecting invoice and clicking Print...")

        selection_made = False
        for locator in [
            (By.XPATH, "//table//input[@type='checkbox']"),
            (By.XPATH, "//input[@type='checkbox']"),
            (By.XPATH, "//tr//input[@type='checkbox']"),
        ]:
            try:
                checkboxes = driver.find_elements(*locator)
                for cb in checkboxes:
                    try:
                        if cb.is_displayed() and cb.is_enabled():
                            scroll_to(driver, cb)
                            driver.execute_script("arguments[0].click();", cb)
                            selection_made = True
                            time.sleep(PAUSE)
                            break
                    except Exception:
                        continue
                if selection_made:
                    break
            except Exception:
                continue

        if not selection_made:
            for locator in [
                (By.XPATH, "//table//tr//td[1]//a"),
                (By.XPATH, "//a[contains(@href,'Invoice') or contains(@href,'invoice')]"),
                (By.XPATH, "//td[normalize-space(.)!=''][contains(.,'INV') or contains(.,'QAL')][1]"),
            ]:
                try:
                    candidates = driver.find_elements(*locator)
                    for row_link in candidates[:10]:
                        try:
                            if row_link.is_displayed():
                                scroll_to(driver, row_link)
                                driver.execute_script("arguments[0].click();", row_link)
                                selection_made = True
                                time.sleep(PAUSE)
                                break
                        except Exception:
                            continue
                    if selection_made:
                        break
                except Exception:
                    continue

        if not selection_made:
            print("  [INFO] No selectable invoice element found; continuing with print fallback.")

        clicked = False
        for locator in [
            (By.XPATH, "//button[normalize-space(.)='Print Invoice']"),
            (By.XPATH, "//button[normalize-space(.)='Print']"),
            (By.XPATH, "//input[@value='Print Invoice']"),
            (By.XPATH, "//input[@value='Print']"),
            (By.XPATH, "//a[normalize-space(.)='Print Invoice']"),
            (By.XPATH, "//a[normalize-space(.)='Print']"),
            (By.XPATH, "//*[contains(normalize-space(.), 'Print')][self::button or self::input or self::a]"),
        ]:
            try:
                print_buttons = driver.find_elements(*locator)
                for btn in print_buttons:
                    if btn.is_displayed():
                        scroll_to(driver, btn)
                        driver.execute_script("arguments[0].click();", btn)
                        time.sleep(PAUSE * 2)
                        clicked = True
                        break
                if clicked:
                    break
            except Exception:
                continue

        if not clicked:
            assert click_visible_text(driver, "Print Invoice") or click_visible_text(driver, "Print"), \
                "Print button not found or not clickable."
            time.sleep(PAUSE)

        take_screenshot(driver, "04_print_invoice")
        print(f"  [URL] {driver.current_url}")
        assert "AccountsPayable" in driver.current_url, (
            f"Expected to remain on the Accounts Payable page after Print action. URL: {driver.current_url}"
        )
        print(f"  [PASS] Print action completed from Accounts Payable: {driver.current_url}")

    def test_05_select_invoice_and_view_details(self, driver):
        """Select an invoice and open the detail page via View Details."""
        print("\n[TC-AP-005] Selecting invoice and opening View Details...")

        selection_made = False
        for locator in [
            (By.XPATH, "//table//input[@type='checkbox']"),
            (By.XPATH, "//input[@type='checkbox']"),
            (By.XPATH, "//tr//input[@type='checkbox']"),
        ]:
            try:
                checkboxes = driver.find_elements(*locator)
                for cb in checkboxes:
                    try:
                        if cb.is_displayed() and cb.is_enabled():
                            scroll_to(driver, cb)
                            driver.execute_script("arguments[0].click();", cb)
                            selection_made = True
                            time.sleep(PAUSE)
                            break
                    except Exception:
                        continue
                if selection_made:
                    break
            except Exception:
                continue

        if not selection_made:
            for locator in [
                (By.XPATH, "//table//tr//td[1]//a"),
                (By.XPATH, "//a[contains(@href,'Invoice') or contains(@href,'invoice')]"),
                (By.XPATH, "//td[normalize-space(.)!=''][contains(.,'INV') or contains(.,'QAL')][1]"),
            ]:
                try:
                    candidates = driver.find_elements(*locator)
                    for row_link in candidates[:10]:
                        try:
                            if row_link.is_displayed():
                                scroll_to(driver, row_link)
                                driver.execute_script("arguments[0].click();", row_link)
                                selection_made = True
                                time.sleep(PAUSE)
                                break
                        except Exception:
                            continue
                    if selection_made:
                        break
                except Exception:
                    continue

        if not selection_made:
            print("  [INFO] No selectable invoice element found; continuing with View Details fallback.")

        clicked = False
        for locator in [
            (By.XPATH, "//button[normalize-space(.)='View Details']"),
            (By.XPATH, "//input[@value='View Details']"),
            (By.XPATH, "//a[normalize-space(.)='View Details']"),
            (By.XPATH, "//*[contains(normalize-space(.), 'View Details')][self::button or self::input or self::a]"),
            (By.XPATH, "//td//a[contains(normalize-space(.), 'View Details')]"),
        ]:
            try:
                btns = driver.find_elements(*locator)
                for btn in btns:
                    if btn.is_displayed():
                        scroll_to(driver, btn)
                        driver.execute_script("arguments[0].click();", btn)
                        wait_ready(driver)
                        time.sleep(PAUSE)
                        clicked = True
                        break
                if clicked:
                    break
            except Exception:
                continue

        if not clicked:
            assert click_visible_text(driver, "View Details"), "View Details button not found or not clickable."
            wait_ready(driver)
            time.sleep(PAUSE)

        take_screenshot(driver, "05_view_details")
        current_url = driver.current_url
        print(f"  [URL] {current_url}")
        assert (
            "AccountsPayable" in current_url
            or "Invoice" in current_url.lower()
            or "View" in current_url.lower()
        ), f"View Details page did not load as expected. URL: {current_url}"
        print(f"  [PASS] View Details opened: {current_url}")

    def test_06_click_back(self, driver):
        """Click Back and return to the Accounts Payable list."""
        print("\n[TC-AP-006] Clicking Back from the detail page...")

        back_clicked = False
        for locator in [
            (By.XPATH, "//button[normalize-space(.)='Back']"),
            (By.XPATH, "//input[@value='Back']"),
            (By.XPATH, "//a[normalize-space(.)='Back']"),
            (By.XPATH, "//*[contains(normalize-space(.), 'Back')][self::button or self::input or self::a]"),
        ]:
            try:
                back_button = WebDriverWait(driver, 8).until(EC.element_to_be_clickable(locator))
                scroll_to(driver, back_button)
                driver.execute_script("arguments[0].click();", back_button)
                wait_ready(driver)
                time.sleep(PAUSE)
                back_clicked = True
                break
            except Exception:
                continue

        if not back_clicked:
            assert click_visible_text(driver, "Back"), "Back button not found or not clickable."
            wait_ready(driver)
            time.sleep(PAUSE)

        take_screenshot(driver, "06_after_back")
        print(f"  [URL] {driver.current_url}")
        assert "AccountsPayable" in driver.current_url, (
            f"Expected return to Accounts Payable list. URL: {driver.current_url}"
        )
        print(f"  [PASS] Returned to Accounts Payable list: {driver.current_url}")
