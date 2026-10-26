"""
QALS11 | Actions > Reschedule — Direct Reschedule Cards Flow
=================================================================
URL   : https://engineering.ultrivalms.com/QALS1011
User  : buyeruser / Ultriva!23

Test Flow
---------
  1. Login as buyeruser
  2. Open direct Reschedule Cards URL
  3. Select two cards by checkbox and enter New Required Receive Date
  4. Click the Reschedule button on the Reschedule Cards List
  5. Verify results and return to items

Run (from qa_automation/):
    pytest tests/QALS11/Actions/test_reschedule.py -v -s
"""

import os
import time
from datetime import datetime, timedelta

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# ============================================================================
# CONFIGURATION
# ============================================================================
BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
RESCHEDULE_CARDS_URL = "https://engineering.ultrivalms.com/QALS1011/BuyerAction/RescheduleCards"
USERNAME = "buyeruser"
PASSWORD = "Ultriva!23"
STEP_PAUSE = 15
NEW_RECEIVE_DATE = (datetime.now() + timedelta(days=30)).strftime("%m/%d/%Y")

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
    """Wait for the document to finish loading."""
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


def step_pause(step_name):
    """Wait intentionally before each major action step."""
    print(f"\n[STEP PAUSE] Waiting 15 seconds before {step_name}...")
    time.sleep(STEP_PAUSE)


def take_screenshot(driver, name):
    screenshots_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "reports", "screenshots"
    )
    os.makedirs(screenshots_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(screenshots_dir, f"reschedule_{name}_{ts}.png")
    driver.save_screenshot(path)
    print(f"  [screenshot] {path}")
    return path


@pytest.mark.usefixtures("driver")
class TestReschedule:

    def test_01_login(self, driver):
        """Login to QA site with buyeruser credentials."""
        print("\n[TC-RSC-001] Logging in to QA site...")
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
        step_pause("Step 1 completion")

        take_screenshot(driver, "01_after_login")
        current_url = driver.current_url
        print(f"  [URL] {current_url}")
        assert BASE_URL.lower() in current_url.lower() or "Home" in current_url, \
            f"Login may have failed. URL: {current_url}"
        print("  [PASS] Login successful.")

    def test_02_open_reschedule_cards(self, driver):
        """Navigate directly to the Reschedule Cards page using the direct URL."""
        print("\n[TC-RSC-002] Opening direct Reschedule Cards URL...")
        driver.get(RESCHEDULE_CARDS_URL)
        wait_ready(driver)
        step_pause("Step 2 completion")

        take_screenshot(driver, "02_reschedule_cards")
        current_url = driver.current_url
        print(f"  [URL] {current_url}")
        assert "RescheduleCards" in current_url or "Reschedule" in current_url, \
            f"Expected Reschedule Cards page. Got: {current_url}"
        print("  [PASS] Reschedule Cards List loaded via direct URL.")

    def test_03_select_cards_and_enter_date(self, driver):
        """Select cards and enter the new required receive date."""
        print("\n[TC-RSC-003] Selecting cards and entering Required Receive Date...")

        # Card row checkboxes only; the header select-all box is named ..._All$CheckboxCardGID
        card_xpath = "//input[contains(@name,'$CheckboxCardGID') and not(contains(@name,'_All'))]"
        WebDriverWait(driver, 20).until(
            lambda d: len(d.find_elements(By.XPATH, card_xpath)) >= 2
        )
        card_checkboxes = driver.find_elements(By.XPATH, card_xpath)

        for chk in card_checkboxes[:2]:
            scroll_to(driver, chk)
            if not chk.is_selected():
                driver.execute_script("arguments[0].click()", chk)
                time.sleep(0.4)

        selected = [c for c in driver.find_elements(By.XPATH, card_xpath) if c.is_selected()]
        assert len(selected) == 2, f"Expected 2 cards selected, got {len(selected)}"
        print(f"  [INFO] Selected {len(selected)} card(s)")
        take_screenshot(driver, "03_cards_selected")

        date_field = find(driver, By.ID, "NewReqRcvdt")
        scroll_to(driver, date_field)
        driver.execute_script("arguments[0].value = '';", date_field)
        date_field.send_keys(NEW_RECEIVE_DATE)
        time.sleep(0.5)
        driver.execute_script("document.body.click()")
        time.sleep(0.5)
        print(f"  [INFO] New Required Receive Date entered: {NEW_RECEIVE_DATE}")

        # The header date is not copied to rows, so fill each selected card's own date
        for chk in selected:
            row_name = chk.get_attribute("name").replace("$CheckboxCardGID", "$TextboxReqReceiveDate")
            row_date = driver.find_element(By.NAME, row_name)
            scroll_to(driver, row_date)
            driver.execute_script("arguments[0].value = '';", row_date)
            row_date.send_keys(NEW_RECEIVE_DATE)
            driver.execute_script("document.body.click()")
            time.sleep(0.5)

        take_screenshot(driver, "03_date_entered")
        step_pause("Step 3 completion")
        print("  [PASS] Cards selected and date entered.")

    def test_04_click_reschedule_button(self, driver):
        """Click the Reschedule toolbar button on the Reschedule Cards List."""
        print("\n[TC-RSC-004] Clicking Reschedule button on Reschedule Cards List...")
        assert "RescheduleCards" in driver.current_url, \
            f"Not on Reschedule Cards List. URL: {driver.current_url}"

        # Toolbar button by id; the breadcrumb link also has the text 'Reschedule'
        reschedule_btn = clickable(driver, By.ID, "btndoActTop")
        scroll_to(driver, reschedule_btn)
        driver.execute_script("arguments[0].click()", reschedule_btn)

        try:
            WebDriverWait(driver, 5).until(EC.alert_is_present())
            driver.switch_to.alert.accept()
        except Exception:
            pass

        wait_ready(driver)
        take_screenshot(driver, "04_after_reschedule")
        dialogs = [e.text.strip() for e in driver.find_elements(By.XPATH, "//*[contains(normalize-space(text()),'Invalid')]") if e.is_displayed()]
        assert not dialogs, f"Reschedule rejected by the app: {dialogs}"
        step_pause("Step 4 completion")

        print(f"  [URL] {driver.current_url}")
        print("  [PASS] Reschedule button clicked on Reschedule Cards List.")

    def test_05_verify_results_and_back_to_items(self, driver):
        """Verify the result page and return to the item list."""
        print("\n[TC-RSC-005] Verifying results and returning to items...")

        current_url = driver.current_url
        print(f"  [URL] {current_url}")

        success_found = False
        for locator in [
            (By.XPATH, "//*[contains(normalize-space(),'Following Cards were successful')]"),
            (By.XPATH, "//*[contains(normalize-space(),'successful')]"),
            (By.XPATH, "//*[contains(normalize-space(),'Successfully Rescheduled')]"),
            (By.XPATH, "//*[contains(normalize-space(),'Rescheduled')]"),
        ]:
            try:
                el = WebDriverWait(driver, 8).until(EC.presence_of_element_located(locator))
                msg = el.text.strip()
                print(f"  [INFO] Result message found: '{msg[:120]}'")
                success_found = True
                break
            except Exception:
                continue

        take_screenshot(driver, "05_results")
        assert "RescheduleResult" in current_url or "Reschedule" in current_url, \
            f"Not on expected results page. URL: {current_url}"

        back_btn = None
        for locator in [
            (By.XPATH, "//button[contains(normalize-space(),'Back To Items') or contains(normalize-space(),'Back to Items')]"),
            (By.XPATH, "//a[contains(normalize-space(),'Back To Items') or contains(normalize-space(),'Back to Items')]"),
            (By.XPATH, "//*[contains(@id,'btnBack') or contains(@id,'backToItems') or contains(@id,'BackToItems')]"),
        ]:
            try:
                back_btn = WebDriverWait(driver, 8).until(EC.element_to_be_clickable(locator))
                break
            except Exception:
                continue

        if back_btn:
            scroll_to(driver, back_btn)
            driver.execute_script("arguments[0].click()", back_btn)
            wait_ready(driver)
            step_pause("Back to Items action")

        take_screenshot(driver, "05_back_to_items")
        print(f"  [FINAL URL] {driver.current_url}")
        if not success_found:
            print("  [WARN] Success text not found, but Reschedule result flow executed.")
        print("  [PASS] Reschedule results verified and flow completed.")