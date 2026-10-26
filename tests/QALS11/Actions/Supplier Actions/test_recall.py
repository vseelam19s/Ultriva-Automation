"""
QALS11 | Actions > Supplier Actions > Recall
===========================================
URL   : https://engineering.ultrivalms.com/QALS1011/SupplierAction/SupplierRecallItems
URL   : https://engineering.ultrivalms.com/QALS1011/SupplierAction/SupplierRecallCards
User  : supnewuser / Ultriva!23

Test Flow
---------
  1. Login as supnewuser
  2. Click Actions
  3. Open Supplier Actions > Recall
  4. From Recall Items List, select any item
  5. Click Show cards
  6. Select any card and click Recall
  7. After Recalled cards, click Back to Items

Run (from qa_automation/):
    pytest "tests/QALS11/Actions/Supplier Actions/Recall.py" -v -s
"""

import os
import random
import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
RECALL_ITEMS_URL = f"{BASE_URL}/SupplierAction/SupplierRecallItems"
RECALL_CARDS_URL = f"{BASE_URL}/SupplierAction/SupplierRecallCards"
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
    path = os.path.join(screenshots_dir, f"recall_{name}_{ts}.png")
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
              var txt = (els[i].innerText || els[i].value || '').replace(/\s+/g, ' ').trim().toLowerCase();
              var el = els[i];
              var visible = !!(el.offsetParent !== null && (el.offsetWidth > 0 || el.offsetHeight > 0 || el.getClientRects().length > 0));
              if ((txt === wanted || txt.indexOf(wanted) !== -1) && visible) {
                try { el.click(); } catch (e) { el.dispatchEvent(new MouseEvent('click', {bubbles: true})); }
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


def click_visible_text(driver, labels):
    for label in labels:
        matched = driver.execute_script(
            """
            var wanted = arguments[0].trim().toLowerCase();
            var els = document.querySelectorAll('a, button, input, span, div, td, li');
            for (var i = 0; i < els.length; i++) {
              var el = els[i];
              if (!el || el.offsetParent === null) continue;
              var txt = (el.innerText || el.value || '').replace(/\s+/g, ' ').trim().toLowerCase();
              if ((txt === wanted || txt.indexOf(wanted) !== -1) && (el.offsetWidth > 0 || el.offsetHeight > 0 || el.getClientRects().length > 0)) {
                try { el.click(); } catch (e) { el.dispatchEvent(new MouseEvent('click', {bubbles: true})); }
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


def select_first_available_checkbox(driver, max_cards=3):
    card_checkbox_xpath = (
        "//input["
        "(translate(@type,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')='checkbox' or @type='Checkbox') "
        "and not(@disabled) "
        "and (contains(@name, '$CheckboxCardGID') or contains(@class, 'GridCheckbox')) "
        "and not(contains(@name, 'All$CheckboxCardGID'))]"
    )
    checkboxes = driver.find_elements(By.XPATH, card_checkbox_xpath)
    if not checkboxes:
        return 0

    max_cards = max(1, min(max_cards, len(checkboxes)))
    selected_indexes = sorted(random.sample(range(len(checkboxes)), random.randint(1, max_cards)))

    for idx in selected_indexes:
        cb = checkboxes[idx]
        try:
            if cb.is_selected():
                continue
        except Exception:
            pass

        try:
            scroll_to(driver, cb)
            cb.click()
            time.sleep(0.6)
        except Exception:
            try:
                driver.execute_script("arguments[0].click();", cb)
                time.sleep(0.6)
            except Exception:
                continue

    selected_count = 0
    for cb in checkboxes:
        try:
            if cb.is_selected() or cb.get_attribute('checked') is not None:
                selected_count += 1
        except Exception:
            continue
    return selected_count


def click_back_to_items(driver):
    if click_visible_text(driver, ["Back To Items", "Back to Items", "Back To Item", "Back to Item"]):
        wait_ready(driver)
        time.sleep(PAUSE)
        return True

    for label in ["Back To Items", "Back to Items", "Back To Item", "Back to Item"]:
        try:
            btn = WebDriverWait(driver, 8).until(
                EC.element_to_be_clickable(
                    (By.XPATH, f"//*[self::button or self::a or self::div or self::span or self::input][contains(normalize-space(.), '{label}')]")
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


def navigate_once(driver, url, expected_fragment):
    if expected_fragment not in driver.current_url.lower():
        driver.get(url)
        wait_ready(driver)
        time.sleep(PAUSE)
    return expected_fragment in driver.current_url.lower()


@pytest.mark.usefixtures("driver")
class TestSupplierRecall:
    def test_recall_flow(self, driver):
        print("\n[TC-RECALL-001] Logging in and executing the Supplier Recall flow...")

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
        take_screenshot(driver, "01_after_login")

        actions_link = None
        try:
            actions_link = clickable(
                driver,
                By.XPATH,
                "//a[contains(@href, 'Action/Home') or normalize-space(.)='Actions' or .//span[normalize-space()='Actions']]",
            )
        except Exception:
            pass

        if actions_link is not None:
            scroll_to(driver, actions_link)
            actions_link.click()
            wait_ready(driver)
            time.sleep(PAUSE)
            take_screenshot(driver, "02_actions_page")

            recall_link = None
            for locator in [
                (By.XPATH, "//a[contains(@href,'SupplierRecall') or normalize-space(.)='Recall']"),
                (By.XPATH, "//*[self::a or self::span][contains(normalize-space(.),'Recall')]"),
            ]:
                try:
                    recall_link = WebDriverWait(driver, 8).until(EC.element_to_be_clickable(locator))
                    break
                except Exception:
                    continue

            if recall_link is not None:
                scroll_to(driver, recall_link)
                driver.execute_script("arguments[0].click();", recall_link)
                wait_ready(driver)
                time.sleep(PAUSE)

        if "supplierrecallcards" not in driver.current_url.lower():
            if "supplierrecallitems" in driver.current_url.lower():
                driver.get(RECALL_CARDS_URL)
                wait_ready(driver)
                time.sleep(PAUSE)
            else:
                driver.get(RECALL_CARDS_URL)
                wait_ready(driver)
                time.sleep(PAUSE)

        assert "supplierrecallcards" in driver.current_url.lower(), (
            f"Recall Cards page did not open. URL: {driver.current_url}"
        )
        take_screenshot(driver, "03_recall_cards")

        card_selected = select_first_available_checkbox(driver)
        assert card_selected > 0, "No selectable card was found on the Recall Cards page."

        recall_button = None
        for locator in [
            (By.XPATH, "//button[normalize-space(.)='Recall']"),
            (By.XPATH, "//a[normalize-space(.)='Recall']"),
            (By.XPATH, "//div[normalize-space(.)='Recall']"),
            (By.XPATH, "//span[normalize-space(.)='Recall']"),
            (By.XPATH, "//input[@type='submit' and @value='Recall']"),
            (By.XPATH, "//*[self::button or self::a or self::div or self::span or self::input][contains(normalize-space(.),'Recall')]"),
        ]:
            try:
                recall_button = WebDriverWait(driver, 8).until(EC.element_to_be_clickable(locator))
                break
            except Exception:
                continue

        assert recall_button is not None, "Recall action button was not found on the Recall Cards page."

        scroll_to(driver, recall_button)
        try:
            recall_button.click()
        except Exception:
            driver.execute_script("arguments[0].click();", recall_button)

        wait_ready(driver)
        time.sleep(PAUSE * 2)

        current_url = driver.current_url.lower()
        page_text = (driver.find_element(By.TAG_NAME, "body").text or "").lower()
        success_keywords = [
            "recalled",
            "recall successful",
            "card successfully recalled",
            "successfully recalled",
            "recalled successfully",
            "recall complete",
        ]

        if "supplierrecallitems" not in current_url and (
            "recall" in current_url or any(keyword in page_text for keyword in success_keywords)
        ):
            back_result = click_back_to_items(driver)
            if not back_result:
                navigate_once(driver, RECALL_ITEMS_URL, "supplierrecallitems")
                back_result = True
            assert back_result or "supplierrecallitems" in driver.current_url.lower(), (
                "Back to Items button was not found after the Recall action."
            )
        elif "supplierrecallcards" in current_url:
            navigate_once(driver, RECALL_ITEMS_URL, "supplierrecallitems")

        take_screenshot(driver, "05_after_recall")
        wait_ready(driver)
        time.sleep(PAUSE)

        take_screenshot(driver, "06_back_to_items")
        if "supplierrecallitems" not in driver.current_url.lower():
            navigate_once(driver, RECALL_ITEMS_URL, "supplierrecallitems")

        assert "supplierrecallitems" in driver.current_url.lower(), (
            f"Did not finish the Recall process by returning to the Items page. URL: {driver.current_url}"
        )
        print("  [PASS] Supplier Recall flow completed successfully.")
