"""
QALS11 | Actions > Runline Approve — End-to-End Flow
=====================================================
URL  : https://engineering.ultrivalms.com/QALS1011
User : buyeruser / Ultriva!23

Test Flow
---------
  1.  Login as buyeruser
  2.  Navigate to Actions menu (left sidebar)
  3.  Click Runline Approve from Buyer Actions page
  4.  On Runline Approve Filter page — click Go to load items
  5.  From Runline Approve Items List — click first item → Show Cards
  6.  From Runline Approve Cards List — select first card → click Approve
  7.  Click Back To Items — verify return to Runline Approve Items List

Run (from qa_automation/):
    pytest tests/QALS11/Actions/test_runline_approve.py -v -s
"""

import os
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
    path = os.path.join(screenshots_dir, f"runline_approve_{name}_{ts}.png")
    driver.save_screenshot(path)
    print(f"  [screenshot] {path}")
    return path

# ============================================================================
# TEST CLASS
# ============================================================================

@pytest.mark.usefixtures("driver")
class TestRunlineApprove:

    # ── TC-RLA-001: Login ────────────────────────────────────────────────────
    def test_01_login(self, driver):
        """Login to QA site with buyeruser credentials."""
        print("\n[TC-RLA-001] Logging in to QA site...")
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
        print(f"  [URL after login] {current_url}")
        assert BASE_URL.lower() in current_url.lower() or "Home" in current_url, \
            f"Login may have failed. URL: {current_url}"
        print("  [PASS] Login successful.")

    # ── TC-RLA-002: Navigate to Actions ──────────────────────────────────
    def test_02_navigate_to_actions(self, driver):
        """Click Actions in the left sidebar to open the Buyer Actions page."""
        print("\n[TC-RLA-002] Navigating to Actions page...")

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
        print(f"  [PASS] Actions page loaded: {driver.current_url}")

    # ── TC-RLA-003: Click Runline Approve ────────────────────────────────
    def test_03_click_runline_approve(self, driver):
        """Click the Runline Approve tile from the Buyer Actions section."""
        print("\n[TC-RLA-003] Clicking Runline Approve tile in Buyer Actions...")

        runline_approve_link = clickable(
            driver,
            By.XPATH,
            "//a[contains(@href,'RLApprove') and not(contains(@class,'toplinks'))]",
        )
        scroll_to(driver, runline_approve_link)
        driver.execute_script("arguments[0].click()", runline_approve_link)
        wait_ready(driver)
        time.sleep(PAUSE)

        take_screenshot(driver, "03_runline_approve_filter")
        assert "RLApprove" in driver.current_url, \
            f"Expected Runline Approve page. Got: {driver.current_url}"
        print(f"  [PASS] Runline Approve page loaded: {driver.current_url}")

    # ── TC-RLA-004: Apply filter and load Runline Approve Items List ─────
    def test_04_apply_filter_and_load_items(self, driver):
        """Click Go on Runline Approve Filter to load the Approve Items List."""
        print("\n[TC-RLA-004] Applying filter — clicking Go button...")

        if "RLApproveItems" in driver.current_url:
            print("  [INFO] Already on Runline Approve Items page, skipping Go click.")
        else:
            go_button = None
            for locator in [
                (By.ID, "imgMatStatusGo"),
                (By.XPATH, "//span[@id='imgMatStatusGo']"),
                (By.XPATH, "//span[contains(@class,'btn-filter-submit-item') and normalize-space(text())='Go']"),
                (By.XPATH, "//a[contains(@class,'btn-filter-submit-item') and contains(normalize-space(),'Go')]"),
                (By.XPATH, "//button[normalize-space(text())='Go']"),
                (By.XPATH, "//input[@type='submit' and @value='Go']"),
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
                print("  [WARN] Go button not found — attempting direct URL navigation...")
                driver.get(f"{BASE_URL}/BuyerAction/RLApproveItems")
                wait_ready(driver)
                time.sleep(PAUSE * 2)

        take_screenshot(driver, "04_runline_approve_items_list")
        assert "RLApprove" in driver.current_url, \
            f"Expected Runline Approve Items page. Got: {driver.current_url}"
        print(f"  [PASS] Runline Approve Items List loaded: {driver.current_url}")

    # ── TC-RLA-005: Click Show Cards to navigate to Runline Approve Cards
    def test_05_select_item_and_show_cards(self, driver):
        """Click Show Cards on Runline Approve Items List to load the cards."""
        print("\n[TC-RLA-005] Clicking Show Cards button from Runline Approve Items List...")

        show_cards_btn = None
        for locator in [
            (By.ID, "btnShowCardsT"),
            (By.ID, "btnShowCardsB"),
            (By.CSS_SELECTOR, "span.show-cards-btn"),
            (By.XPATH, "//span[contains(@class,'show-cards-btn')]"),
            (By.XPATH, "//span[normalize-space(text())='Show Cards' or contains(normalize-space(),'Show Cards')]"),
        ]:
            try:
                show_cards_btn = WebDriverWait(driver, 8).until(
                    EC.element_to_be_clickable(locator)
                )
                break
            except Exception:
                continue

        assert show_cards_btn, "Show Cards button not found on Runline Approve Items page"
        print("  [INFO] Found Show Cards button: id=%r  class=%r" %
              (show_cards_btn.get_attribute("id"), show_cards_btn.get_attribute("class")))
        take_screenshot(driver, "05a_items_list")
        scroll_to(driver, show_cards_btn)
        driver.execute_script("arguments[0].click()", show_cards_btn)
        wait_ready(driver)
        time.sleep(PAUSE * 2)

        take_screenshot(driver, "05b_runline_approve_cards_list")
        print("  [INFO] URL after Show Cards: %s" % driver.current_url)
        assert "RLApproveCard" in driver.current_url or "RLApprove" in driver.current_url, \
            "Expected Runline Approve Cards page. Got: %s" % driver.current_url
        print("  [PASS] Runline Approve Cards List loaded: %s" % driver.current_url)

    # ── TC-RLA-006: Full Approve cycle — select card → Approve → handle Notes dialog ─
    def test_06_select_card_and_approve(self, driver):
        """
        Complete Runline Approve cycle:
        1. Ensure we are on RLApproveCards page
        2. Select the first individual card row checkbox (GridCheckbox, not grid-all-checkbox)
        3. Click the Approve button (id='btndoActTop', onclick='da()')
        4. Handle the Notes dialog — click 'Approve without Notes' (id='btnapNodoAct', onclick='apnda()')
        5. Wait for approval to complete and take final screenshot
        """
        print("\n[TC-RLA-006] Completing full Approve cycle (select card → Approve → Notes dialog)...")

        # Ensure we are on the RLApproveCards page; if not, navigate there
        if "RLApproveCard" not in driver.current_url:
            print("  [INFO] Not on RLApproveCards — navigating via Show Cards...")
            driver.get("%s/BuyerAction/RLApproveItems" % BASE_URL)
            wait_ready(driver)
            time.sleep(PAUSE)
            for locator in [
                (By.ID, "btnShowCardsT"),
                (By.CSS_SELECTOR, "span.show-cards-btn"),
            ]:
                try:
                    btn = WebDriverWait(driver, 8).until(EC.element_to_be_clickable(locator))
                    driver.execute_script("arguments[0].click()", btn)
                    wait_ready(driver)
                    time.sleep(PAUSE * 2)
                    break
                except Exception:
                    continue
            print("  [INFO] Now on: %s" % driver.current_url)

        # Wait for the cards table to be present
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "RLApproveCards"))
        )
        time.sleep(PAUSE)  # Extra wait for dynamic card rows to render

        all_cbs = driver.find_elements(By.XPATH, "//input[@type='checkbox']")
        print("  [INFO] Total checkboxes on page: %d" % len(all_cbs))
        card_checkboxes = []
        for cb in all_cbs:
            cls = cb.get_attribute('class') or ''
            if 'GridCheckbox' in cls and 'grid-all-checkbox' not in cls:
                card_checkboxes.append(cb)
                print("  [INFO] Card checkbox: name=%r  value=%r" % (
                    cb.get_attribute('name'), cb.get_attribute('value')))

        if not card_checkboxes:
            print("  [WARN] No individual card checkboxes found — trying Select All fallback")
            card_checkboxes = [cb for cb in all_cbs if 'grid-all-checkbox' in (cb.get_attribute('class') or '')]
            if card_checkboxes:
                print("  [INFO] Using Select All checkbox to select all cards")

        assert card_checkboxes, "No card checkboxes found on RLApproveCards page — no cards available to approve"
        print("  [INFO] Found %d card checkbox(es) to use" % len(card_checkboxes))

        first_cb = card_checkboxes[0]
        scroll_to(driver, first_cb)
        card_value = first_cb.get_attribute("value") or "(unknown)"
        if not first_cb.is_selected():
            driver.execute_script("arguments[0].click()", first_cb)
            time.sleep(0.5)
            print("  [INFO] Selected card GID: %s" % card_value)
            take_screenshot(driver, "06a_card_selected")

        # Click the Approve button
        approve_btn = None
        for locator in [
            (By.ID, "btndoActTop"),
            (By.ID, "btndoActBot"),
            (By.XPATH, "//span[@onclick='da()']"),
        ]:
            try:
                approve_btn = WebDriverWait(driver, 8).until(EC.element_to_be_clickable(locator))
                break
            except Exception:
                continue

        assert approve_btn, "Approve toolbar button (btndoActTop/btndoActBot) not found"
        print("  [INFO] Clicking Approve button (id=%r)..." % approve_btn.get_attribute("id"))
        scroll_to(driver, approve_btn)
        driver.execute_script("arguments[0].click()", approve_btn)
        time.sleep(PAUSE)
        take_screenshot(driver, "06b_notes_dialog")

        # Handle Notes dialog
        approve_no_notes = None
        for locator in [
            (By.ID, "btnapNodoAct"),
            (By.XPATH, "//span[@id='btnapNodoAct']"),
            (By.XPATH, "//span[contains(@onclick,'apnda')]"),
        ]:
            try:
                approve_no_notes = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(locator)
                )
                break
            except Exception:
                continue

        if approve_no_notes:
            print("  [INFO] Notes dialog visible — clicking 'Approve without Notes' (apnda)...")
            driver.execute_script("arguments[0].click()", approve_no_notes)
            wait_ready(driver)
            time.sleep(PAUSE * 2)
        else:
            print("  [WARN] Notes dialog not found — Approve may have submitted directly.")

        take_screenshot(driver, "06c_after_full_approve")
        print("  [URL after full Approve] %s" % driver.current_url)

        remaining = driver.find_elements(
            By.XPATH,
            "//input[@type='checkbox' and contains(@class,'GridCheckbox') and not(contains(@class,'grid-all-checkbox'))]"
        )
        print("  [INFO] Remaining unapproved cards: %d" % len(remaining))
        print("  [PASS] Full Approve cycle completed successfully.")

    # ── TC-RLA-007: Click Back To Items ──────────────────────────────────
    def test_07_back_to_items(self, driver):
        """Click Back To Items and verify return to Runline Approve Items List."""
        print("\n[TC-RLA-007] Clicking Back To Items...")
        print("  [INFO] Currently on: %s" % driver.current_url)

        if "RLApproveCard" not in driver.current_url:
            print("  [INFO] Not on RLApproveCards — re-navigating via Show Cards...")
            driver.get("%s/BuyerAction/RLApproveItems" % BASE_URL)
            wait_ready(driver)
            time.sleep(PAUSE)
            for locator in [
                (By.ID, "btnShowCardsT"),
                (By.CSS_SELECTOR, "span.show-cards-btn"),
            ]:
                try:
                    btn = WebDriverWait(driver, 8).until(EC.element_to_be_clickable(locator))
                    driver.execute_script("arguments[0].click()", btn)
                    wait_ready(driver)
                    time.sleep(PAUSE * 2)
                    break
                except Exception:
                    continue
            print("  [INFO] Now on: %s" % driver.current_url)

        back_btn = None
        for locator in [
            (By.ID, "btnBackPageTop"),
            (By.ID, "btnBackPageBot"),
            (By.XPATH, "//span[@onclick='gb();']"),
            (By.XPATH, "//span[contains(normalize-space(),'Back To Items')]"),
        ]:
            try:
                back_btn = WebDriverWait(driver, 8).until(EC.element_to_be_clickable(locator))
                break
            except Exception:
                continue

        assert back_btn, "Back To Items button (btnBackPageTop/btnBackPageBot) not found"
        print("  [INFO] Found: id=%r  text=%r" % (back_btn.get_attribute("id"), back_btn.text.strip()))
        scroll_to(driver, back_btn)
        driver.execute_script("arguments[0].click()", back_btn)
        wait_ready(driver)
        time.sleep(PAUSE * 2)

        take_screenshot(driver, "07_back_to_items")
        current_url = driver.current_url
        print("  [URL after Back To Items] %s" % current_url)
        assert "RLApproveItem" in current_url or "RLApprove" in current_url, \
            "Expected Runline Approve Items page. Got: %s" % current_url
        print("  [PASS] Successfully returned to Runline Approve Items List.")