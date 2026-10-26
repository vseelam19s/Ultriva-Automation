"""
QALS11 | Actions > Supplier Actions > Accept RunLine Cards
=========================================================
URL   : https://engineering.ultrivalms.com/QALS1011/SupplierAction/AcceptCards
User  : supnewuser / Ultriva!23

Test Flow
---------
  1. Login as supnewuser
  2. Open Actions > Accept (Accept Items List)
  3. Click Runline Cards -> Accept Waiting At Runline Cards List
  4. Select two cards
  5. Click Accept -> Accept Waiting At Runline Cards Results
  6. Select the cards on the results page and click Confirm
  7. Verify both cards were successfully accepted

Run (from qa_automation/):
    pytest tests/QALS11/Actions/test_accept_runline_cards.py -v -s
"""

import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
USERNAME = "supnewuser"
PASSWORD = "Ultriva!23"
PAUSE = 1.5
CARDS_TO_ACCEPT = 2


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


def select_checkboxes(driver, checkboxes, count):
    """Check exactly `count` boxes from the list; uncheck any others."""
    for index, cb in enumerate(checkboxes):
        should_check = index < count
        if cb.is_selected() != should_check:
            scroll_to(driver, cb)
            try:
                cb.click()
            except Exception:
                driver.execute_script("arguments[0].click();", cb)


@pytest.mark.usefixtures("driver")
class TestSupplierAcceptRunLineCards:
    selected_cards = []

    def test_01_login(self, driver):
        driver.get(f"{BASE_URL}/Account/Login")
        wait_ready(driver)
        find(driver, By.ID, "UserName").send_keys(USERNAME)
        find(driver, By.ID, "Password").send_keys(PASSWORD)
        clickable(driver, By.ID, "login-button").click()
        wait_ready(driver)
        time.sleep(PAUSE)
        assert "Account/Login" not in driver.current_url, f"Login failed. URL: {driver.current_url}"

    def test_02_open_accept_items_list(self, driver):
        driver.get(f"{BASE_URL}/SupplierAction/AcceptFilter")
        wait_ready(driver)
        clickable(driver, By.ID, "AcceptItems_tbrAcceptRunline")
        assert "AcceptFilter" in driver.current_url or "AcceptItems" in driver.current_url

    def test_03_open_runline_cards_list(self, driver):
        runline_btn = clickable(driver, By.ID, "AcceptItems_tbrAcceptRunline")
        scroll_to(driver, runline_btn)
        runline_btn.click()
        wait_ready(driver)
        WebDriverWait(driver, 20).until(EC.url_contains("SupplierAction/AcceptCards"))
        assert "Accept Waiting At Runline Cards List" in find(driver, By.TAG_NAME, "body").text, (
            "Accept Waiting At Runline Cards List did not open."
        )

    def test_04_select_two_cards(self, driver):
        card_selector = "tr[gid] input.GridCheckbox"
        WebDriverWait(driver, 20).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, card_selector)) >= CARDS_TO_ACCEPT
        )
        card_checkboxes = driver.find_elements(By.CSS_SELECTOR, card_selector)
        select_checkboxes(driver, card_checkboxes, CARDS_TO_ACCEPT)
        selected = [cb.get_attribute("value") for cb in card_checkboxes if cb.is_selected()]
        assert len(selected) == CARDS_TO_ACCEPT, f"Expected {CARDS_TO_ACCEPT} selected cards, got {selected}"
        type(self).selected_cards = selected

    def test_05_click_accept(self, driver):
        # Print PO is intentionally never clicked in this flow.
        accept_button = clickable(driver, By.ID, "btndoActTop")
        scroll_to(driver, accept_button)
        accept_button.click()
        WebDriverWait(driver, 20).until(EC.url_contains("SupplierAction/AcceptResults"))
        wait_ready(driver)
        time.sleep(PAUSE)
        assert "Accept Waiting At Runline Cards Results" in find(driver, By.TAG_NAME, "body").text

    def test_06_select_result_cards_and_confirm(self, driver):
        result_checkboxes = [
            cb for cb in driver.find_elements(By.CSS_SELECTOR, "input.GridCheckbox")
            if cb.get_attribute("name").startswith("AltAcceptCards_") and "_All" not in cb.get_attribute("name")
        ]
        assert len(result_checkboxes) == CARDS_TO_ACCEPT, (
            f"Expected {CARDS_TO_ACCEPT} cards on the results page, found {len(result_checkboxes)}."
        )
        select_checkboxes(driver, result_checkboxes, CARDS_TO_ACCEPT)

        confirm_button = clickable(driver, By.ID, "actConfirm")
        scroll_to(driver, confirm_button)
        confirm_button.click()

    def test_07_verify_cards_accepted(self, driver):
        WebDriverWait(driver, 30).until(
            lambda d: "Following Cards were successful" in d.find_element(By.TAG_NAME, "body").text
        )
        body_text = driver.find_element(By.TAG_NAME, "body").text
        assert body_text.count("Runline Card successfully accepted.") == CARDS_TO_ACCEPT, body_text
        for card_id in self.selected_cards:
            assert card_id in body_text, f"{card_id} missing from the success list."
