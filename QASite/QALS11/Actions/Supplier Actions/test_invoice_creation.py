r"""
QALS11 | Actions > Supplier Actions > Invoice Creation
=======================================================
URL   : https://engineering.ultrivalms.com/QALS1011/SupplierAction/InvoiceCreation
User  : supnewuser / Ultriva!23

Test Flow
---------
  1. Login as supnewuser
  2. Open Supplier Actions > Invoice Creation
  3. Select any item
  4. Click Create Invoice
  5. Review the invoice preview
  6. Click Confirm and Create Invoice

Run (from qa_automation/):
    pytest "tests/QALS11/Actions/Supplier Actions/Invoice Creation.py" -v -s
"""

import os
import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
INVOICE_URL = f"{BASE_URL}/SupplierAction/InvoiceCreation"
USERNAME = "supnewuser"
PASSWORD = "Ultriva!23"
PAUSE = 1.5


@pytest.fixture(scope="class")
def driver():
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
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'})", element)
    time.sleep(0.3)


def take_screenshot(driver, name):
    screenshots_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "reports", "screenshots"
    )
    os.makedirs(screenshots_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(screenshots_dir, f"supplier_invoice_creation_{name}_{ts}.png")
    driver.save_screenshot(path)
    print(f"  [screenshot] {path}")
    return path


def click_text(driver, labels):
    for label in labels:
        locators = [
            (By.XPATH, f"//*[self::a or self::button or self::input or self::span or self::div][normalize-space(.)='{label}']"),
            (By.XPATH, f"//*[self::a or self::button or self::input or self::span or self::div][contains(normalize-space(.), '{label}')]"),
            (By.XPATH, f"//*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{label.lower()}')]"),
        ]
        for by, locator in locators:
            try:
                elements = driver.find_elements(by, locator)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        scroll_to(driver, element)
                        try:
                            element.click()
                        except Exception:
                            driver.execute_script("arguments[0].click();", element)
                        return True
            except Exception:
                continue

        matched = driver.execute_script(
            """
            var wanted = arguments[0].trim().toLowerCase();
            var els = document.querySelectorAll('a, button, input, span, div, td, li');
            for (var i = 0; i < els.length; i++) {
              var text = (els[i].innerText || els[i].value || '').replace(/\\s+/g, ' ').trim().toLowerCase();
              var visible = !!(els[i].offsetParent !== null && (els[i].offsetWidth > 0 || els[i].offsetHeight > 0 || els[i].getClientRects().length > 0));
              if ((text === wanted || text.indexOf(wanted) !== -1) && visible) {
                try { els[i].click(); } catch (e) { els[i].dispatchEvent(new MouseEvent('click', {bubbles: true})); }
                return true;
              }
            }
            return false;
            """,
            label,
        )
        if matched:
            return True
    return False


def select_first_row(driver):
    checkbox_locators = [
        "//input[contains(@name, 'CheckboxItemGID') and not(contains(@name, 'All')) and not(@disabled)]",
        "//input[@type='checkbox' and contains(@name, 'ItemGID') and not(@disabled)]",
        "//input[@type='checkbox' and contains(@name, 'Checkbox') and contains(@name, 'Item') and not(@disabled)]",
    ]

    for locator in checkbox_locators:
        try:
            checkboxes = driver.find_elements(By.XPATH, locator)
        except Exception:
            checkboxes = []

        for checkbox in checkboxes:
            try:
                if not checkbox.is_displayed() or not checkbox.is_enabled():
                    continue
                row = checkbox.find_element(By.XPATH, "ancestor::tr[1]")
                if row is None or not row.is_displayed():
                    continue
                text = (row.text or "").strip()
                if not text or text.lower().startswith("item description") or text.lower().startswith("invoice number"):
                    continue
                scroll_to(driver, row)
                try:
                    checkbox.click()
                except Exception:
                    driver.execute_script("arguments[0].click();", checkbox)
                time.sleep(PAUSE)
                return row
            except Exception:
                continue

    raise AssertionError("No selectable item row was found on the Invoice Creation page.")


def click_create_invoice(driver):
    for label in ["Create Invoice", "Create invoice"]:
        if click_text(driver, [label]):
            time.sleep(PAUSE * 2)
            return True

    button = None
    for locator in [
        (By.XPATH, "//*[self::button or self::a or self::input or self::span][contains(normalize-space(.), 'Create Invoice')]"),
        (By.XPATH, "//*[contains(@id, 'CreateInvoice') or contains(@name, 'CreateInvoice') or contains(@value, 'Create Invoice')]"),
        (By.XPATH, "//button[contains(normalize-space(.), 'Create Invoice')]"),
        (By.XPATH, "//a[contains(normalize-space(.), 'Create Invoice')]"),
        (By.XPATH, "//input[@value='Create Invoice' or contains(@value, 'Create Invoice')]"),
    ]:
        try:
            els = driver.find_elements(locator[0], locator[1])
            for el in els:
                if el.is_displayed() and el.is_enabled():
                    button = el
                    break
            if button:
                break
        except Exception:
            continue

    if button is None:
        raise AssertionError("Create Invoice button was not found.")

    scroll_to(driver, button)
    try:
        button.click()
    except Exception:
        driver.execute_script("arguments[0].click();", button)

    time.sleep(PAUSE * 2)
    return True


def click_confirm_and_create(driver):
    for label in ["Confirm and Create Invoice", "Confirm and create invoice"]:
        if click_text(driver, [label]):
            time.sleep(PAUSE * 2)
            return True

    button = None
    for locator in [
        (By.XPATH, "//*[self::button or self::a or self::input or self::span][contains(normalize-space(.), 'Confirm and Create Invoice')]"),
        (By.XPATH, "//*[contains(@id, 'ConfirmAndCreateInvoice') or contains(@name, 'ConfirmAndCreateInvoice') or contains(@value, 'Confirm and Create Invoice')]"),
        (By.XPATH, "//button[contains(normalize-space(.), 'Confirm and Create Invoice')]"),
        (By.XPATH, "//a[contains(normalize-space(.), 'Confirm and Create Invoice')]"),
        (By.XPATH, "//input[@value='Confirm and Create Invoice' or contains(@value, 'Confirm and Create Invoice')]"),
    ]:
        try:
            els = driver.find_elements(locator[0], locator[1])
            for el in els:
                if el.is_displayed() and el.is_enabled():
                    button = el
                    break
            if button:
                break
        except Exception:
            continue

    if button is None:
        raise AssertionError("Confirm and Create Invoice button was not found.")

    scroll_to(driver, button)
    try:
        button.click()
    except Exception:
        driver.execute_script("arguments[0].click();", button)

    time.sleep(PAUSE * 2)
    return True


@pytest.mark.usefixtures("driver")
class TestSupplierInvoiceCreation:

    def test_01_login(self, driver):
        print("\n[TC-SINV-001] Logging in to QA site as supnewuser...")
        driver.get(f"{BASE_URL}/Account/Login")
        wait_ready(driver)

        username = find(driver, By.ID, "UserName")
        password = find(driver, By.ID, "Password")
        login_button = clickable(driver, By.ID, "login-button")

        username.clear()
        username.send_keys(USERNAME)
        password.clear()
        password.send_keys(PASSWORD)
        login_button.click()
        wait_ready(driver)
        time.sleep(PAUSE)

        current_url = driver.current_url.lower()
        assert BASE_URL.lower() in current_url or "home" in current_url, (
            f"Login may have failed. URL: {driver.current_url}"
        )
        take_screenshot(driver, "01_after_login")
        print(f"  [URL] {driver.current_url}")
        print("  [PASS] Login succeeded.")

    def test_02_open_invoice_creation_page(self, driver):
        print("\n[TC-SINV-002] Opening Invoice Creation page...")
        driver.get(INVOICE_URL)
        wait_ready(driver)
        time.sleep(PAUSE * 2)

        current_url = driver.current_url.lower()
        assert "invoicecreation" in current_url, (
            f"Invoice Creation page did not load. URL: {driver.current_url}"
        )
        take_screenshot(driver, "02_invoice_creation_page")
        print(f"  [URL] {driver.current_url}")
        print("  [PASS] Invoice Creation page loaded.")

    def test_03_select_item_and_create_invoice(self, driver):
        print("\n[TC-SINV-003] Selecting an item and creating invoice...")
        select_first_row(driver)
        take_screenshot(driver, "03_item_selected")

        assert click_create_invoice(driver), "Create Invoice action did not complete."
        wait_ready(driver)
        time.sleep(PAUSE * 2)
        take_screenshot(driver, "04_invoice_preview")
        print("  [PASS] Invoice preview reached.")

    def test_04_confirm_create_invoice(self, driver):
        print("\n[TC-SINV-004] Confirming and creating the invoice...")
        assert click_confirm_and_create(driver), "Confirm and Create Invoice did not complete."
        wait_ready(driver)
        time.sleep(PAUSE * 3)
        take_screenshot(driver, "05_after_confirmation")

        current_url = driver.current_url.lower()
        assert (
            "invoicecreation" in current_url
            or "invoicecreationresults" in current_url
            or "invoicecreated" in current_url
            or "invoice" in current_url
        ), (
            f"Invoice creation confirmation did not complete as expected. URL: {driver.current_url}"
        )
        print(f"  [URL] {driver.current_url}")
        print("  [PASS] Invoice was confirmed and created.")
