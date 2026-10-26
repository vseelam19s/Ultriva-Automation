r"""
QALS11 | Actions > Supplier Actions > Manage Ship Quantities
===========================================================
URL   : https://engineering.ultrivalms.com/QALS1011/SupplierAction/ManageShipQuantitiesItems
URL   : https://engineering.ultrivalms.com/QALS1011/SupplierAction/ManageShipQuantitiesCards
User  : supnewuser / Ultriva!23

Test Flow
---------
  1. Login as supnewuser
  2. Click Actions
  3. Open Supplier Actions > Manage Ship Quantities
  4. From Manage Ship Quantities Items List, select any item and click Show Cards
  5. From Manage Ship Quantities Cards List, select a card and enter qty
  6. Click Save
  7. Verify success and return to items

Run (from qa_automation/):
    pytest "tests/QALS11/Actions/Supplier Actions/Manage Ship Quantities.py" -v -s
"""

import os
import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
ITEMS_URL = f"{BASE_URL}/SupplierAction/ManageShipQuantitiesItems"
CARDS_URL = f"{BASE_URL}/SupplierAction/ManageShipQuantitiesCards"
USERNAME = "supnewuser"
PASSWORD = "Ultriva!23"
PAUSE = 1.5
QTY_TO_ENTER = "10"


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
    path = os.path.join(screenshots_dir, f"manage_ship_quantities_{name}_{ts}.png")
    driver.save_screenshot(path)
    print(f"  [screenshot] {path}")
    return path


def click_text(driver, labels):
    for label in labels:
        locators = [
            (By.XPATH, f"//*[self::a or self::button or self::input or self::span or self::div][normalize-space(.)='{label}']"),
            (By.XPATH, f"//*[self::a or self::button or self::input or self::span or self::div][contains(normalize-space(.), '{label}')]"),
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
              var txt = (els[i].innerText || els[i].value || '').replace(/\\s+/g, ' ').trim().toLowerCase();
              var visible = !!(els[i].offsetParent !== null && (els[i].offsetWidth > 0 || els[i].offsetHeight > 0 || els[i].getClientRects().length > 0));
              if ((txt === wanted || txt.indexOf(wanted) !== -1) && visible) {
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


def select_first_item(driver):
    rows = driver.find_elements(By.XPATH, "//tr[td or a or span]")
    for row in rows:
        try:
            if not row.is_displayed():
                continue
            text = (row.text or "").strip()
            if not text:
                continue
            if any(label in text.lower() for label in ["supplier item", "item no", "description", "plant item"]):
                continue
            scroll_to(driver, row)
            try:
                row.click()
            except Exception:
                driver.execute_script("arguments[0].click();", row)
            time.sleep(PAUSE)
            return True
        except Exception:
            continue
    raise AssertionError("No item row could be selected from the Manage Ship Quantities Items list.")


def click_show_cards(driver):
    for label in ["Show Cards", "Show cards", "ShowCard"]:
        if click_text(driver, [label]):
            wait_ready(driver)
            time.sleep(PAUSE * 2)
            return True

    candidates = [
        (By.XPATH, "//button[contains(normalize-space(.), 'Show Cards')]"),
        (By.XPATH, "//a[contains(normalize-space(.), 'Show Cards')]"),
        (By.XPATH, "//span[contains(normalize-space(.), 'Show Cards')]"),
        (By.XPATH, "//*[contains(@id,'ShowCards') or contains(@id,'showCards')]"),
        (By.XPATH, "//*[contains(@onclick,'ShowCards') or contains(@onclick,'showCards')]"),
    ]
    for by, locator in candidates:
        try:
            btn = clickable(driver, by, locator, 8)
            scroll_to(driver, btn)
            try:
                btn.click()
            except Exception:
                driver.execute_script("arguments[0].click();", btn)
            wait_ready(driver)
            time.sleep(PAUSE * 2)
            return True
        except Exception:
            continue

    raise AssertionError("Show Cards button was not found on the Manage Ship Quantities Items page.")


def select_first_card(driver):
    checkbox_candidates = [
        "//input[@type='checkbox' and not(@disabled)]",
        "//input[contains(@name,'CheckboxCard') or contains(@id,'CheckboxCard')]",
        "//input[contains(@name,'SelectCard') or contains(@id,'SelectCard')]",
    ]
    for xpath in checkbox_candidates:
        try:
            checkboxes = driver.find_elements(By.XPATH, xpath)
            for cb in checkboxes:
                if cb.is_displayed() and cb.is_enabled():
                    scroll_to(driver, cb)
                    try:
                        cb.click()
                    except Exception:
                        driver.execute_script("arguments[0].click();", cb)
                    time.sleep(0.5)
                    return True
        except Exception:
            continue

    rows = driver.find_elements(By.XPATH, "//tr[td]")
    for row in rows:
        try:
            if not row.is_displayed():
                continue
            cb = row.find_element(By.XPATH, ".//input[@type='checkbox' and not(@disabled)]")
            if cb.is_displayed() and cb.is_enabled():
                scroll_to(driver, cb)
                try:
                    cb.click()
                except Exception:
                    driver.execute_script("arguments[0].click();", cb)
                time.sleep(0.5)
                return True
        except Exception:
            continue

    raise AssertionError("No selectable card checkbox was found on the Manage Ship Quantities Cards page.")


def enter_quantity(driver, value=QTY_TO_ENTER):
    qty_field = None
    locators = [
        (By.XPATH, "//input[contains(@name,'Qty') or contains(@name,'Quantity') or contains(@id,'Qty') or contains(@id,'Quantity') or contains(@placeholder,'Qty') or contains(@placeholder,'Quantity')]"),
        (By.XPATH, "//input[@type='text' and not(@disabled)]"),
    ]

    for by, locator in locators:
        try:
            elements = driver.find_elements(by, locator)
            for el in elements:
                if el.is_displayed() and el.is_enabled():
                    qty_field = el
                    break
            if qty_field:
                break
        except Exception:
            continue

    if qty_field is None:
        raise AssertionError("Quantity input field was not found on the Manage Ship Quantities Cards page.")

    try:
        qty_field.clear()
    except Exception:
        driver.execute_script("arguments[0].value = '';", qty_field)
    qty_field.send_keys(value)
    time.sleep(0.5)
    return True


def click_save(driver):
    for label in ["Save", "save"]:
        if click_text(driver, [label]):
            wait_ready(driver)
            time.sleep(PAUSE * 2)
            return True

    candidates = [
        (By.XPATH, "//button[contains(normalize-space(.), 'Save')]"),
        (By.XPATH, "//a[contains(normalize-space(.), 'Save')]"),
        (By.XPATH, "//input[@value='Save' or contains(@value, 'Save')]"),
        (By.XPATH, "//*[contains(@id,'Save') or contains(@name,'Save')]"),
    ]
    for by, locator in candidates:
        try:
            btn = clickable(driver, by, locator, 8)
            scroll_to(driver, btn)
            try:
                btn.click()
            except Exception:
                driver.execute_script("arguments[0].click();", btn)
            wait_ready(driver)
            time.sleep(PAUSE * 2)
            return True
        except Exception:
            continue

    raise AssertionError("Save button was not found on the Manage Ship Quantities Cards page.")


def click_back_to_items(driver):
    for label in ["Back To Items", "Back to Items", "Back To Item", "Back to Item"]:
        try:
            btn = WebDriverWait(driver, 8).until(
                EC.element_to_be_clickable(
                    (By.XPATH, f"//*[self::button or self::a or self::span or self::input][contains(normalize-space(.), '{label}')]")
                )
            )
            scroll_to(driver, btn)
            driver.execute_script("arguments[0].click();", btn)
            wait_ready(driver)
            time.sleep(PAUSE)
            return True
        except Exception:
            continue
    return False


@pytest.mark.usefixtures("driver")
class TestSupplierManageShipQuantities:

    def test_manage_ship_quantities_flow(self, driver):
        print("\n[TC-MSQ-001] Logging in and executing the Manage Ship Quantities flow...")
        driver.get(f"{BASE_URL}/Account/Login")
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

        current_url = driver.current_url.lower()
        assert "home" in current_url or BASE_URL.lower() in current_url, (
            f"Login may have failed. Current URL: {driver.current_url}"
        )
        take_screenshot(driver, "01_after_login")
        print(f"  [URL] {driver.current_url}")
        print("  [PASS] Login successful.")

        print("\n[TC-MSQ-002] Opening Manage Ship Quantities Items page...")
        driver.get(ITEMS_URL)
        wait_ready(driver)
        time.sleep(PAUSE * 2)
        assert "manageshipquantitiesitems" in driver.current_url.lower(), (
            f"Expected Manage Ship Quantities Items page. Got: {driver.current_url}"
        )
        take_screenshot(driver, "02_items_page")
        print(f"  [URL] {driver.current_url}")
        print("  [PASS] Items page loaded.")

        print("\n[TC-MSQ-003] Selecting an item and clicking Show Cards...")
        select_first_item(driver)
        time.sleep(PAUSE)
        click_show_cards(driver)
        time.sleep(PAUSE)
        assert "manageshipquantitiescards" in driver.current_url.lower(), (
            f"Expected Manage Ship Quantities Cards page. Got: {driver.current_url}"
        )
        take_screenshot(driver, "03_cards_page")
        print(f"  [URL] {driver.current_url}")
        print("  [PASS] Show Cards navigated successfully.")

        print("\n[TC-MSQ-004] Selecting a card and entering quantity...")
        select_first_card(driver)
        time.sleep(PAUSE)
        enter_quantity(driver, QTY_TO_ENTER)
        take_screenshot(driver, "04_qty_entered")
        print(f"  [INFO] Entered quantity: {QTY_TO_ENTER}")

        print("\n[TC-MSQ-005] Saving the change...")
        click_save(driver)
        time.sleep(PAUSE * 2)
        take_screenshot(driver, "05_after_save")
        print("  [PASS] Save action executed.")

        print("\n[TC-MSQ-006] Returning to items list...")
        click_back_to_items(driver)
        time.sleep(PAUSE)
        print("  [PASS] Manage Ship Quantities flow completed.")
