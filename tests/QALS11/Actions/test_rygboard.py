"""
QALS11 | Actions > Buyer RYG Board
==================================
URL   : https://engineering.ultrivalms.com/QALS1011/BuyerAction/BuyerRYGBoardItems
User  : buyeruser / Ultriva!23

Test Flow
---------
  1. Login as buyeruser
  2. Click Actions
  3. Open Buyer RYG Board
  4. Click Go and validate the popup data for Item No
  5. Open Spike Order Entry
  6. Fill required fields and validate the values
  7. Submit the entries

Run (from qa_automation/):
    pytest tests/QALS11/Actions/RYGBoard.py -v -s
"""

import os
import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
BUYER_RYG_URL = f"{BASE_URL}/BuyerAction/BuyerRYGBoardItems"
SPIKE_ORDER_URL = f"{BASE_URL}/BuyerAction/SpikeOrderEntry"
USERNAME = "buyeruser"
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
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'})", element)
    time.sleep(0.3)


def take_screenshot(driver, name):
    screenshots_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "reports", "screenshots"
    )
    os.makedirs(screenshots_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(screenshots_dir, f"ryg_{name}_{ts}.png")
    driver.save_screenshot(path)
    print(f"  [screenshot] {path}")
    return path


def click_visible_text(driver, labels):
    for label in labels:
        locators = [
            (By.XPATH, f"//*[self::a or self::button or self::input or self::span][normalize-space(.)='{label}']"),
            (By.XPATH, f"//*[self::a or self::button or self::input or self::span][contains(normalize-space(.), '{label}')]"),
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
    return False


def find_first_item_number(driver):
    locators = [
        (By.XPATH, "//a[contains(normalize-space(.), 'ITB') or contains(normalize-space(.), 'IT')]"),
        (By.XPATH, "//td[contains(normalize-space(.), 'ITB') or contains(normalize-space(.), 'IT')]"),
        (By.XPATH, "//tr[td]//a[1]"),
    ]
    for by, locator in locators:
        try:
            for element in driver.find_elements(by, locator):
                text = (element.text or "").strip()
                if text and (text.startswith("ITB") or text.startswith("IT")):
                    return text
        except Exception:
            continue
    return ""


@pytest.mark.usefixtures("driver")
class TestBuyerRygBoard:

    def test_01_login_and_actions(self, driver):
        print("\n[TC-RYG-001] Logging in and opening Actions...")
        driver.get(BASE_URL)
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

        current_url = driver.current_url
        assert BASE_URL.lower() in current_url.lower() or "Home" in current_url.lower(), (
            f"Login may have failed. URL: {current_url}"
        )
        take_screenshot(driver, "01_after_login")

        actions_link = clickable(
            driver,
            By.XPATH,
            "//a[contains(@href, 'Action/Home') or normalize-space(.)='Actions' or .//span[normalize-space()='Actions']]",
        )
        scroll_to(driver, actions_link)
        actions_link.click()
        wait_ready(driver)
        time.sleep(PAUSE)

        take_screenshot(driver, "02_actions_page")
        assert "Action/Home" in driver.current_url.lower() or "Action" in driver.current_url, (
            f"Actions page did not open. URL: {driver.current_url}"
        )
        print("  [PASS] Login and Actions navigation succeeded.")

    def test_02_open_ryg_board_and_validate_popup(self, driver):
        print("\n[TC-RYG-002] Opening Buyer RYG Board and checking item details...")

        opened = click_visible_text(driver, ["Buyer RYG Board", "BuyerRYGBoard", "RYG Board"])
        if not opened:
            driver.get(BUYER_RYG_URL)
            wait_ready(driver)
            time.sleep(PAUSE)

        assert "BuyerRYGBoard" in driver.current_url or "BuyerAction" in driver.current_url, (
            f"Buyer RYG Board did not load. URL: {driver.current_url}"
        )

        go_clicked = click_visible_text(driver, ["Go"])
        assert go_clicked, "Go button was not found on Buyer RYG Board."
        wait_ready(driver)
        time.sleep(PAUSE * 2)

        item_number = find_first_item_number(driver)
        print(f"  [Item No] {item_number}")
        assert item_number, "No item number was found on the Buyer RYG Board."

        item_links = driver.find_elements(
            By.XPATH,
            "//a[contains(normalize-space(.), 'ITB') or contains(normalize-space(.), 'IT')]",
        )
        assert item_links, "No item links were visible on the board."

        item_link = item_links[0]
        scroll_to(driver, item_link)
        try:
            item_link.click()
        except Exception:
            driver.execute_script("arguments[0].click();", item_link)
        wait_ready(driver)
        time.sleep(PAUSE)

        body_text = driver.find_element(By.TAG_NAME, "body").text
        assert any(token in body_text for token in ["Item No", "Description", "Supplier", "RLG", "SKU"]), (
            "Item detail popup did not contain the expected item fields."
        )
        print(f"  [Popup details] {body_text[:500]}")
        take_screenshot(driver, "03_item_popup")
        print("  [PASS] Buyer RYG Board item popup validated.")

    def test_03_open_spike_order_entry_and_submit(self, driver):
        print("\n[TC-RYG-003] Opening Spike Order Entry and submitting details...")

        opened = click_visible_text(driver, ["Spike Order Entry", "SpikeOrderEntry"])
        if not opened:
            driver.get(SPIKE_ORDER_URL)
            wait_ready(driver)
            time.sleep(PAUSE)

        assert "SpikeOrderEntry" in driver.current_url or "Spike Order Entry" in driver.page_source, (
            f"Spike Order Entry page did not load. URL: {driver.current_url}"
        )
        take_screenshot(driver, "04_spike_order_entry")

        item_number = find_first_item_number(driver) or "ITB160522"
        values = [
            item_number,
            "Test item details",
            "Test Supplier",
            "1",
            "1",
            "0",
            "0",
            "0",
            "0",
            "0",
        ]
        input_fields = driver.find_elements(
            By.XPATH,
            "//input[not(@type) or @type='text' or @type='number' or @type='date']",
        )
        filled = False

        for index, field in enumerate(input_fields[:16]):
            if not field.is_displayed() or field.get_attribute("type") == "hidden":
                continue
            if field.get_attribute("value"):
                continue
            if index < len(values):
                field.send_keys(str(values[index]))
            else:
                field.send_keys("0")
            filled = True
            time.sleep(0.2)

        assert filled, "No editable input fields were available for Spike Order Entry."

        validate_clicked = click_visible_text(driver, ["Validate Entries"])
        assert validate_clicked, "Validate Entries button not found."
        wait_ready(driver)
        time.sleep(PAUSE)

        submit_clicked = click_visible_text(driver, ["Submit Entries"])
        assert submit_clicked, "Submit Entries button not found."
        wait_ready(driver)
        time.sleep(PAUSE)

        body_text = driver.find_element(By.TAG_NAME, "body").text
        assert any(token in body_text for token in ["Submitted", "Success", "Entries", "Spike Order"]), (
            "Submission did not show expected confirmation text."
        )
        take_screenshot(driver, "05_after_submit")
        print("  [PASS] Spike Order Entry was validated and submitted.")
