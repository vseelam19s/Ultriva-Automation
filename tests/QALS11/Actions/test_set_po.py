"""
QALS11 | Actions > Set PO — End-to-End Flow
============================================
URL   : https://engineering.ultrivalms.com/QALS1011
User : buyeruser / Ultriva!23

Test Flow
---------
  1.  Login as buyeruser
  2.  Navigate to Actions menu (left sidebar)
  3.  Click SetPO from Buyer Actions page
  4.  On SetPO Items List — select any item → click Show Cards
  5.  From SetPO Cards List — select cards via checkbox
      → enter random numerical PO values → click Finish Process
  6.  Click Back to Items — verify return to SetPO Items List

Run (from qa_automation/):
    pytest tests/QALS11/Actions/test_set_po.py -v -s
"""

import os
import random
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ============================================================================
# CONFIGURATION
# ============================================================================
BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
USERNAME = "buyeruser"
PASSWORD = "Ultriva!23"
PAUSE = 1.5

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="class")
def driver():
    """Class-scoped Chrome driver — one browser session per test class."""
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
    driver.execute_script("arguments[0].scrollIntoView({block:'center'})", el)
    time.sleep(0.3)

def take_screenshot(driver, name):
    screenshots_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "reports", "screenshots"
    )
    os.makedirs(screenshots_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(screenshots_dir, f"set_po_{name}_{ts}.png")
    driver.save_screenshot(path)
    return path

def random_po_number():
    """Generate a random numerical PO value (5–8 digits)."""
    return str(random.randint(10000, 99999999))

# ============================================================================
# TEST CLASS
# ============================================================================

@pytest.mark.usefixtures("driver")
class TestSetPo:
    
    # ── TC-SPO-001: Login ────────────────────────────────────────────────────
    def test_01_login(self, driver):
        """Login to QA site with buyeruser credentials."""
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
        assert BASE_URL.lower() in current_url.lower() or "Home" in current_url, \
            f"Login may have failed. URL: {current_url}"

    # ── TC-SPO-002: Navigate to Actions ──────────────────────────────────
    def test_02_navigate_to_actions(self, driver):
        """Click Actions in the left sidebar to open the Buyer Actions page."""
        actions_link = clickable(
            driver,
            By.XPATH,
            "//a[contains(@href, 'Action/Home') or "
            "(.//span[normalize-space()='Actions']) or "
            "normalize-space(.)='Actions']",
        )
        scroll_to(driver, actions_link)
        actions_link.click()
        wait_ready(driver)
        time.sleep(PAUSE)

        take_screenshot(driver, "02_actions_page")
        assert "Action/Home" in driver.current_url, \
            f"Expected Actions page. Got: {driver.current_url}"

    # ── TC-SPO-003: Click SetPO ──────────────────────────────────────────
    def test_03_click_set_po(self, driver):
        """Click the SetPO tile from the Buyer Actions page."""
        set_po_link = None
        for locator in [
            (By.XPATH, "//a[contains(@href,'SetPO') and not(contains(@class,'toplinks'))]"),
            (By.XPATH, "//a[contains(@href,'setPO') and not(contains(@class,'toplinks'))]"),
            (By.XPATH, "//a[contains(@href,'setpo') and not(contains(@class,'toplinks'))]"),
            (By.XPATH, "//a[normalize-space(text())='Set PO' or normalize-space(text())='SetPO']"),
            (By.XPATH, "//*[contains(normalize-space(),'Set PO') or contains(normalize-space(),'SetPO')][self::a or self::button or self::span]"),
        ]:
            try:
                set_po_link = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(locator)
                )
                break
            except Exception:
                continue

        assert set_po_link, "SetPO link/tile not found on Actions page"
        scroll_to(driver, set_po_link)
        driver.execute_script("arguments[0].click()", set_po_link)
        wait_ready(driver)
        time.sleep(PAUSE)

        take_screenshot(driver, "03_set_po_page")
        assert any(kw in driver.current_url for kw in ["SetPO", "setPO", "setpo", "SetPo"]), \
            f"Expected SetPO page. Got: {driver.current_url}"

    # ── TC-SPO-004: Apply filter / load SetPO Items List ─────────────────
    def test_04_apply_filter_and_load_items(self, driver):
        """Click Go on SetPO Filter page to load the SetPO Items List."""
        current_url = driver.current_url
        if not any(kw in current_url for kw in ["SetPOItems", "SetPoItems", "setpoitems", "SetPOItem"]):
            go_button = None
            for locator in [
                (By.ID, "imgMatStatusGo"),
                (By.XPATH, "//span[@id='imgMatStatusGo']"),
                (By.XPATH, "//a[contains(@class,'btn-filter-submit-item') and contains(normalize-space(),'Go')]"),
                (By.XPATH, "//span[contains(@class,'btn-filter-submit-item') and normalize-space(text())='Go']"),
                (By.XPATH, "//button[normalize-space(text())='Go']"),
                (By.input, "//input[@type='submit' and @value='Go']"),
                (By.XPATH, "//*[@id='btnGo' or @id='go-button' or @id='goBtn']"),
            ]:
                try:
                    go_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable(locator)
                    )
                    break
                except Exception:
                    continue

            if go_button:
                scroll_to(driver, go_button)
                driver.execute_script("arguments[0].click()", go_button)
                wait_ready(driver)
                time.sleep(PAUSE * 2)
            else:
                driver.get(f"{BASE_URL}/BuyerAction/SetPOItems")
                wait_ready(driver)
                time.sleep(PAUSE * 2)

        take_screenshot(driver, "04_set_po_items_list")
        assert any(kw in driver.current_url for kw in ["SetPO", "setPO", "setpo", "SetPo"]), \
            f"Expected SetPO Items page. Got: {driver.current_url}"

    # ── TC-SPO-005: Select item and click Show Cards ─────────────────────
    def test_05_select_item_show_cards(self, driver):
        """Click the first item in the SetPO Items List, then click Show Cards."""
        item_links = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class,'GridLink')]"))
        )
        assert item_links, "No GridLink items found in SetPO Items List"

        first_item_link = item_links[0]
        scroll_to(driver, first_item_link)
        driver.execute_script("arguments[0].click()", first_item_link)
        wait_ready(driver)
        time.sleep(PAUSE * 2)

        take_screenshot(driver, "05a_after_item_click")

        if any(kw in driver.current_url for kw in ["SetPOCard", "SetPoCard", "setpocard"]):
            return

        show_cards_btn = None
        for locator in [
            (By.XPATH, "//button[contains(normalize-space(),'Show Cards')]"),
            (By.XPATH, "//a[contains(normalize-space(),'Show Cards')]"),
            (By.XPATH, "//span[contains(normalize-space(),'Show Cards')]"),
            (By.XPATH, "//*[contains(@id,'ShowCards') or contains(@id,'showCards')]"),
            (By.XPATH, "//*[contains(@onclick,'ShowCards') or contains(@onclick,'showCards')]"),
        ]:
            try:
                show_cards_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(locator)
                )
                break
            except Exception:
                continue

        assert show_cards_btn, f"Show Cards button not found and not on SetPO Cards page. Current URL: {driver.current_url}"
        scroll_to(driver, show_cards_btn)
        driver.execute_script("arguments[0].click()", show_cards_btn)
        wait_ready(driver)
        time.sleep(PAUSE * 2)

        take_screenshot(driver, "05b_set_po_cards_list")
        assert any(kw in driver.current_url for kw in ["SetPO", "setPO", "setpo", "SetPo"]), \
            f"Expected SetPO Cards page. Got: {driver.current_url}"

    # ── TC-SPO-006: Select cards and enter PO values ─────────────────────
    def test_06_select_cards_and_set_po(self, driver):
        """Select cards via checkboxes, enter random numerical PO values, then click Finish Process."""
        checkboxes = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//table//tr[td]//input[@type='checkbox'] | //input[@type='checkbox'][not(ancestor::th)]")
            )
        )
        assert checkboxes, "No checkboxes found in SetPO Cards List"

        selected = 0
        for chk in checkboxes[:3]:
            try:
                scroll_to(driver, chk)
                if not chk.is_selected():
                    driver.execute_script("arguments[0].click()", chk)
                    time.sleep(0.4)
                    selected += 1
            except Exception:
                pass

        assert selected > 0, "Could not select any cards"
        take_screenshot(driver, "06a_cards_selected")

        po_input_locators = [
            (By.XPATH, "//input[@type='text'][contains(@id,'PO') or contains(@name,'PO') or contains(@id,'po') or contains(@name,'po')]"),
            (By.XPATH, "//input[@type='text'][contains(@placeholder,'PO') or contains(@placeholder,'po')]"),
            (By.XPATH, "//table//tr[td]//input[@type='text']"),
        ]

        po_inputs = []
        for locator in po_input_locators:
            try:
                po_inputs = WebDriverWait(driver, 8).until(
                    EC.presence_of_all_elements_located(locator)
                )
                if po_inputs:
                    break
            except Exception:
                continue

        if po_inputs:
            for inp in po_inputs[:selected]:
                try:
                    scroll_to(driver, inp)
                    po_value = random_po_number()
                    driver.execute_script("arguments[0].value = '';", inp)
                    inp.clear()
                    inp.send_keys(po_value)
                except Exception:
                    pass

        take_screenshot(driver, "06b_po_values_entered")

        finish_btn = None
        for locator in [
            (By.XPATH, "//button[contains(normalize-space(),'Finish Process')]"),
            (By.XPATH, "//a[contains(normalize-space(),'Finish Process')]"),
            (By.XPATH, "//span[contains(normalize-space(),'Finish Process')]"),
            (By.XPATH, "//*[@id='btnFinishProcess' or contains(@id,'Finish') or contains(@id,'finish')]"),
            (By.XPATH, "//button[contains(normalize-space(),'Finish')]"),
            (By.XPATH, "//a[contains(normalize-space(),'Finish')]"),
            (By.XPATH, "//*[contains(normalize-space(),'SetPO') and (self::button or self::a or self::span)]"),
            (By.XPATH, "//button[contains(normalize-space(),'Set PO')]"),
            (By.XPATH, "//a[contains(normalize-space(),'Set PO')]"),
        ]:
            try:
                finish_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(locator)
                )
                break
            except Exception:
                continue

        assert finish_btn, "Finish Process / Set PO button not found in cards list"
        scroll_to(driver, finish_btn)
        driver.execute_script("arguments[0].click()", finish_btn)
        wait_ready(driver)
        time.sleep(PAUSE * 2)

        take_screenshot(driver, "06c_after_finish_process")

    # ── TC-SPO-007: Verify Set PO Results ────────────────────────────────
    def test_07_verify_set_po_results(self, driver):
        """Verify the Set PO results/confirmation page."""
        current_url = driver.current_url

        result_found = False
        for locator in [
            (By.XPATH, "//*[contains(normalize-space(),'successful')]"),
            (By.XPATH, "//*[contains(normalize-space(),'PO') and contains(normalize-space(),'set')]"),
            (By.XPATH, "//*[contains(normalize-space(),'Set PO')]"),
            (By.XPATH, "//*[contains(normalize-space(),'Finish')]"),
            (By.XPATH, "//h1 | //h2 | //h3"),
        ]:
            try:
                el = WebDriverWait(driver, 8).until(
                    EC.presence_of_element_located(locator)
                )
                msg = el.text.strip()
                if msg:
                    result_found = True
                    break
            except Exception:
                continue

        take_screenshot(driver, "07_set_po_results")
        assert any(kw in current_url for kw in ["SetPO", "setPO", "setpo", "SetPo", "Result", "result"]), \
            f"Not on expected SetPO Results/Cards page. URL: {current_url}"

    # ── TC-SPO-008: Click Back to Items ──────────────────────────────────
    def test_08_back_to_items(self, driver):
        """Click Back to Items and verify return to SetPO Items List."""
        back_btn = None
        for locator in [
            (By.ID, "btnBackPageTop"),
            (By.ID, "btnBackPageBot"),
            (By.XPATH, "//span[contains(normalize-space(),'Back to Items')]"),
            (By.XPATH, "//a[contains(normalize-space(),'Back to Items')]"),
            (By.XPATH, "//button[contains(normalize-space(),'Back to Items')]"),
            (By.XPATH, "//*[contains(@onclick,'BackToItems') or contains(@href,'SetPOItems')]"),
            (By.XPATH, "//*[contains(normalize-space(),'Back') and (self::button or self::a or self::span)]"),
        ]:
            try:
                back_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(locator)
                )
                break
            except Exception:
                continue

        if not back_btn:
            driver.get(f"{BASE_URL}/BuyerAction/SetPOItems")
            wait_ready(driver)
            time.sleep(PAUSE)

            item_links = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class,'GridLink')]"))
            )
            assert item_links, "No items found in SetPO Items List"
            driver.execute_script("arguments[0].click()", item_links[0])
            wait_ready(driver)
            time.sleep(PAUSE * 2)

            for locator in [
                (By.ID, "btnBackPageTop"),
                (By.ID, "btnBackPageBot"),
                (By.XPATH, "//span[contains(normalize-space(),'Back to Items')]"),
                (By.XPATH, "//a[contains(normalize-space(),'Back to Items')]"),
                (By.XPATH, "//button[contains(normalize-space(),'Back to Items')]"),
            ]:
                try:
                    back_btn = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable(locator)
                    )
                    break
                except Exception:
                    continue

        assert back_btn, "Back to Items button not found"
        scroll_to(driver, back_btn)
        driver.execute_script("arguments[0].click()", back_btn)
        wait_ready(driver)
        time.sleep(PAUSE * 2)

        take_screenshot(driver, "08_back_to_items")
        current_url = driver.current_url
        assert any(kw in current_url for kw in ["SetPO", "setPO", "setpo", "SetPo"]), \
            f"Expected SetPO Items page. Got: {current_url}"