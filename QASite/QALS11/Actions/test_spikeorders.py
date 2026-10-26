"""
QALS11 | Actions > Spike Order Entry — Buyer flow
==================================================
URL   : https://engineering.ultrivalms.com/QALS1011/BuyerAction/SpikeOrderEntry
User  : buyeruser / Ultriva!23

Test Flow
---------
  1. Login as buyeruser
  2. Click Actions
  3. Open Spike Order Entry from Buyer Actions
  4. Select any item/row
  5. Click Validate Entries
  6. Click Submit Entries
  7. Re-open Spike Order Entry and validate page availability

Run (from qa_automation/):
    pytest tests/QALS11/Actions/Spikeorders.py -v -s
"""

import os
import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
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


def scroll_to(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'})", element)
    time.sleep(0.3)


def take_screenshot(driver, name):
    screenshots_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "reports", "screenshots"
    )
    os.makedirs(screenshots_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(screenshots_dir, f"spikeorders_{name}_{ts}.png")
    driver.save_screenshot(path)
    print(f"  [screenshot] {path}")
    return path


def click_visible_text(driver, labels):
    """Click a visible labeled button/link if present."""
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
                        time.sleep(1.0)
                        return True
            except Exception:
                continue
    return False


def select_any_item_row(driver):
    """Select the first visible row or checkbox on the Spike Order Entry table."""
    for locator in [
        "//table//tbody//tr//input[@type='checkbox']",
        "//input[@type='checkbox']",
        "//table//tr[td]//td[1]",
        "//tr[td]//td[1]",
    ]:
        try:
            elements = driver.find_elements(By.XPATH, locator)
            for element in elements:
                if element.is_displayed() and element.is_enabled():
                    scroll_to(driver, element)
                    try:
                        element.click()
                    except Exception:
                        driver.execute_script("arguments[0].click();", element)
                    time.sleep(1.0)
                    return True
        except Exception:
            continue

    rows = driver.find_elements(By.XPATH, "//table//tbody//tr[td]")
    for row in rows[:10]:
        try:
            if row.is_displayed():
                scroll_to(driver, row)
                try:
                    row.click()
                except Exception:
                    driver.execute_script("arguments[0].click();", row)
                time.sleep(1.0)
                return True
        except Exception:
            continue
    return False


@pytest.mark.usefixtures("driver")
class TestSpikeOrderEntry:

    def test_01_spike_order_entry_flow(self, driver):
        print("\n[TC-SPO-001] Logging in and starting Spike Order Entry flow...")

        driver.get(BASE_URL)
        wait_ready(driver)

        user_field = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "UserName"))
        )
        pass_field = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "Password"))
        )
        login_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.ID, "login-button"))
        )

        user_field.clear()
        user_field.send_keys(USERNAME)
        pass_field.clear()
        pass_field.send_keys(PASSWORD)
        login_button.click()
        wait_ready(driver)
        time.sleep(PAUSE)

        current_url = driver.current_url
        assert BASE_URL.lower() in current_url.lower() or "Home" in current_url.lower(), (
            f"Login may have failed. URL: {current_url}"
        )
        take_screenshot(driver, "01_after_login")
        print(f"  [URL] {current_url}")

        actions_link = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//a[contains(@href, 'Action/Home') or normalize-space(.)='Actions' or .//span[normalize-space()='Actions']]",
                )
            )
        )
        scroll_to(driver, actions_link)
        actions_link.click()
        wait_ready(driver)
        time.sleep(PAUSE)

        current_url_lower = driver.current_url.lower()
        assert "action/home" in current_url_lower or "action" in current_url_lower, (
            f"Actions page did not load. URL: {driver.current_url}"
        )
        take_screenshot(driver, "02_actions_page")
        print("  [PASS] Actions page opened successfully.")

        driver.get(SPIKE_ORDER_URL)
        wait_ready(driver)
        time.sleep(PAUSE)

        current_url_lower = driver.current_url.lower()
        assert "spikeorderentry" in current_url_lower or "spike order entry" in driver.page_source.lower(), (
            f"Spike Order Entry page did not load. URL: {driver.current_url}"
        )
        take_screenshot(driver, "03_spike_order_entry_loaded")
        print(f"  [URL] {driver.current_url}")

        selected = select_any_item_row(driver)
        assert selected, "No selectable item row was found on the Spike Order Entry page."
        take_screenshot(driver, "04_item_row_selected")
        print("  [PASS] An item row was selected.")

        validate_clicked = click_visible_text(driver, ["Validate Entries"])
        assert validate_clicked, "Validate Entries button was not found or not clickable."
        wait_ready(driver)
        time.sleep(PAUSE * 2)
        take_screenshot(driver, "05_after_validate")
        print("  [PASS] Validate Entries action executed.")

        submit_clicked = click_visible_text(driver, ["Submit Entries"])
        assert submit_clicked, "Submit Entries button was not found or not clickable."
        wait_ready(driver)
        time.sleep(PAUSE * 2)
        take_screenshot(driver, "06_after_submit")
        print("  [PASS] Submit Entries action executed.")

        reopened = click_visible_text(driver, ["Spike Order Entry", "SpikeOrderEntry"])
        if not reopened:
            driver.get(SPIKE_ORDER_URL)
            wait_ready(driver)
            time.sleep(PAUSE)

        take_screenshot(driver, "07_returned_to_spike_order_entry")
        current_url_lower = driver.current_url.lower()
        assert "spikeorderentry" in current_url_lower or "spike order entry" in driver.page_source.lower(), (
            f"Could not reopen Spike Order Entry. URL: {driver.current_url}"
        )
        print("  [PASS] Spike Order Entry flow completed successfully.")
