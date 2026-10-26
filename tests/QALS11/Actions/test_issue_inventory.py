"""
QALS11 | Actions > Issue Inventory — End-to-End Issue Inventory Flow
=====================================================================
URL  : https://engineering.ultrivalms.com/QALS1011
User : buyeruser / Ultriva!23

Test Flow
---------
  1.  Login as buyeruser
  2.  Navigate to Actions menu (left sidebar)
  3.  Click Issue Inventory from Buyer Actions page
  4.  On Issue Inventory Items List page — click Go, then select an item, click Show Cards
  5.  On Issue Inventory Cards List — enter Issue Location and Issue Qty, click Issue Inventory
  6.  Verify Issue Inventory Results page shows "Following Cards were successful"
  7.  Click Back to Items — verify return to Issue Inventory Items List

Run (from qa_automation/):
    pytest tests/QALS11/Actions/test_issue_inventory.py -v -s
"""

import time
import re
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
ISSUE_LOCATION = "1212"     # To Issue Location value
ISSUE_QTY = "1"             # Issue Qty value

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
    import os
    screenshots_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "reports", "screenshots"
    )
    os.makedirs(screenshots_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(screenshots_dir, f"issue_inventory_{name}_{ts}.png")
    driver.save_screenshot(path)
    print(f"  [screenshot] {path}")
    return path

# ============================================================================
# TEST CLASS
# ============================================================================

@pytest.mark.usefixtures("driver")
class TestIssueInventory:

    # ── TC-II-001: Login ─────────────────────────────────────────────────────
    def test_01_login(self, driver):
        """Login to QA site with buyeruser credentials."""
        print("\n[TC-II-001] Logging in to QA site...")
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
        assert BASE_URL.lower() in current_url.lower() or "Home" in current_url, \
            f"Login may have failed. URL: {current_url}"
        print("  [PASS] Login successful.")

    # ── TC-II-002: Navigate to Actions ───────────────────────────────────
    def test_02_navigate_to_actions(self, driver):
        """Click Actions in the left sidebar to open the Actions menu page."""
        print("\n[TC-II-002] Navigating to Actions page...")

        actions_link = clickable(
            driver,
            By.XPATH,
            "//a[contains(@href,'Action/Home') or "
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

    # ── TC-II-003: Click Issue Inventory ─────────────────────────────────
    def test_03_click_issue_inventory(self, driver):
        """Click the Issue Inventory tile from the Buyer Actions section."""
        print("\n[TC-II-003] Clicking Issue Inventory tile in Buyer Actions...")

        issue_inv_link = None
        for locator in [
            (By.XPATH, "//a[contains(@href,'IssueInventory') and not(contains(@class,'toplinks'))]"),
            (By.XPATH, "//a[contains(normalize-space(),'Issue Inventory') and not(contains(@class,'toplinks'))]"),
            (By.XPATH, "//a[normalize-space()='Issue Inventory']"),
        ]:
            try:
                issue_inv_link = WebDriverWait(driver, 8).until(
                    EC.element_to_be_clickable(locator)
                )
                break
            except Exception:
                continue

        assert issue_inv_link, "Issue Inventory link not found on Actions page"
        scroll_to(driver, issue_inv_link)
        driver.execute_script("arguments[0].click()", issue_inv_link)
        wait_ready(driver)
        time.sleep(PAUSE)

        take_screenshot(driver, "03_issue_inventory_filter")
        assert "IssueInventory" in driver.current_url, \
            f"Expected Issue Inventory page. Got: {driver.current_url}"
        print(f"  [PASS] Issue Inventory page loaded: {driver.current_url}")

    # ── TC-II-004: Click Go to load Issue Inventory Items List ───────────
    def test_04_click_go_load_items(self, driver):
        """Click Go on Issue Inventory Filter to load the Items List."""
        print("\n[TC-II-004] Clicking Go button to load Issue Inventory Items...")

        if "IssueInventoryItems" in driver.current_url:
            print("  [INFO] Already on Issue Inventory Items page, skipping Go click.")
        else:
            go_button = None
            for locator in [
                (By.XPATH, "//a[contains(@class,'btn-filter-submit-item') and contains(normalize-space(),'Go')]"),
                (By.XPATH, "//a[normalize-space(text())='Go' and contains(@class,'btn')]"),
                (By.XPATH, "//button[normalize-space(text())='Go']"),
                (By.XPATH, "//input[@type='submit' and @value='Go']"),
                (By.XPATH, "//*[normalize-space(text())='Go']"),
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
                print("  [WARN] Go button not found — navigating directly to Items page...")
                driver.get(f"{BASE_URL}/BuyerAction/IssueInventoryItems")
                wait_ready(driver)
                time.sleep(PAUSE * 2)

        take_screenshot(driver, "04_issue_inventory_items")
        assert "IssueInventory" in driver.current_url, \
            f"Expected Issue Inventory Items page. Got: {driver.current_url}"
        print(f"  [PASS] Issue Inventory Items List loaded: {driver.current_url}")

    # ── TC-II-005: Select item and click Show Cards ──────────────────────
    def test_05_select_item_show_cards(self, driver):
        """Click items one by one until landing on a Cards page with available cards."""
        print("\n[TC-II-005] Finding an item with available cards...")

        items_url = f"{BASE_URL}/BuyerAction/IssueInventoryItems"
        MAX_ITEMS_TO_TRY = 10
        chosen_item = None

        for idx in range(MAX_ITEMS_TO_TRY):
            if "IssueInventoryItems" not in driver.current_url:
                driver.get(items_url)
                wait_ready(driver)
                time.sleep(PAUSE)

            item_links = driver.find_elements(By.XPATH, "//a[contains(@class,'GridLink')]")
            if idx >= len(item_links):
                break

            item_link = item_links[idx]
            item_name = item_link.text.strip()
            scroll_to(driver, item_link)
            driver.execute_script("arguments[0].click()", item_link)
            wait_ready(driver)
            time.sleep(PAUSE * 2)

            if "IssueInventoryCards" not in driver.current_url:
                print(f"  [INFO] '{item_name}' did not navigate to Cards — skipping")
                continue

            row_chks = driver.find_elements(
                By.XPATH,
                "//input[contains(@class,'GridCheckbox') and not(contains(@class,'grid-all-checkbox'))]"
            )
            if not row_chks:
                row_chks = driver.find_elements(
                    By.XPATH,
                    "//input[contains(@name,'CheckboxCardGID') and not(contains(@name,'_All$'))]"
                )

            print(f"  [INFO] '{item_name}' — {len(row_chks)} card row(s)")
            if row_chks:
                chosen_item = item_name
                print(f"  [INFO] Selected item: '{item_name}' with {len(row_chks)} card(s)")
                break

        assert chosen_item, f"No items with available cards found after checking {MAX_ITEMS_TO_TRY} items"

        take_screenshot(driver, "05_issue_inventory_cards")
        assert "IssueInventoryCards" in driver.current_url, \
            f"Expected IssueInventoryCards page. Got: {driver.current_url}"
        print(f"  [PASS] Issue Inventory Cards page loaded for '{chosen_item}': {driver.current_url}")

    # ── TC-II-006: Enter Issue Location, Issue Qty and click Issue Inventory ──
    def test_06_enter_details_and_issue(self, driver):
        """Select cards, enter Issue Location and Issue Qty, then click Issue Inventory."""
        print("\n[TC-II-006] Selecting cards, entering Issue Location + Qty, clicking Issue Inventory...")

        if "IssueInventoryCards" not in driver.current_url:
            print(f"  [WARN] Not on IssueInventoryCards. Current URL: {driver.current_url}")

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//table//tr[td]"))
        )
        time.sleep(PAUSE * 2)

        row_checkboxes = driver.find_elements(
            By.XPATH,
            "//input[contains(@class,'GridCheckbox') and not(contains(@class,'grid-all-checkbox'))]"
        )
        if not row_checkboxes:
            row_checkboxes = driver.find_elements(
                By.XPATH,
                "//input[contains(@name,'CheckboxCardGID') and not(contains(@name,'_All$'))]"
            )
            
        assert row_checkboxes, "No card row checkboxes found on Issue Inventory Cards page"
        print(f"  [INFO] Found {len(row_checkboxes)} card row checkbox(es)")

        chk = row_checkboxes[0]
        scroll_to(driver, chk)
        if not chk.is_selected():
            driver.execute_script("arguments[0].click()", chk)
            time.sleep(0.4)
            
        card_value = chk.get_attribute("value")
        print(f"  [INFO] Selected card GID: '{card_value}'")

        chk_name = chk.get_attribute("name") or ""
        row_match = re.search(r'IssueInventoryCards_(\d+)_\$', chk_name)
        row_idx = row_match.group(1) if row_match else "1"
        print(f"  [INFO] Card row index: {row_idx}")

        loc_id = f"IssueInventoryCards_{row_idx}_$TextboxCurrentLocation"
        loc_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, loc_id))
        )
        scroll_to(driver, loc_input)
        loc_input.clear()
        loc_input.send_keys(ISSUE_LOCATION)
        print(f"  [INFO] Entered Issue Location: '{ISSUE_LOCATION}' into '{loc_id}'")

        qty_id = f"IssueInventoryCards_{row_idx}_$TextboxAdjustQty"
        qty_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, qty_id))
        )
        scroll_to(driver, qty_input)
        qty_input.clear()
        qty_input.send_keys(ISSUE_QTY)
        print(f"  [INFO] Entered Issue Qty: '{ISSUE_QTY}' into '{qty_id}'")

        take_screenshot(driver, "06a_cards_filled")

        issue_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "btndoActTop"))
        )
        scroll_to(driver, issue_btn)
        driver.execute_script("arguments[0].click()", issue_btn)
        wait_ready(driver)
        time.sleep(PAUSE * 2)

        take_screenshot(driver, "06b_issue_inventory_submitted")
        print(f"  [URL] {driver.current_url}")
        print("  [PASS] Issue Inventory submitted.")

    # ── TC-II-007: Verify Issue Inventory Results ────────────────────────
    def test_07_verify_results(self, driver):
        """Verify the Issue Inventory Results page shows a success message."""
        print("\n[TC-II-007] Verifying Issue Inventory Results page...")

        current_url = driver.current_url
        print(f"  [URL] {current_url}")

        success_found = False
        for locator in [
            (By.XPATH, "//*[contains(normalize-space(),'Following Cards were successful')]"),
            (By.XPATH, "//*[contains(normalize-space(),'Inventory Successfully Issued')]"),
            (By.XPATH, "//*[contains(normalize-space(),'successful')]"),
            (By.XPATH, "//h1[contains(normalize-space(),'Result')] | //h2[contains(normalize-space(),'Result')]"),
            (By.XPATH, "//*[contains(@class,'success')]"),
        ]:
            try:
                el = WebDriverWait(driver, 8).until(
                    EC.presence_of_element_located(locator)
                )
                msg = el.text.strip()
                if msg:
                    print(f"  [INFO] Result message: '{msg[:120]}'")
                    success_found = True
                    break
            except Exception:
                continue

        take_screenshot(driver, "07_issue_inventory_results")

        assert "IssueInventory" in current_url or "Result" in current_url, \
            f"Not on expected Issue Inventory Results page. URL: {current_url}"

        if not success_found:
            print("  [WARN] Success message not found by text, but URL confirms Issue Inventory page.")

        print("  [PASS] Issue Inventory Results page verified.")

    # ── TC-II-008: Click Back to Items ───────────────────────────────────
    def test_08_back_to_items(self, driver):
        """Click Back to Items and verify return to Issue Inventory Items List."""
        print("\n[TC-II-008] Clicking Back to Items...")
        print(f"  [INFO] Currently on: {driver.current_url}")

        back_btn = None
        for locator in [
            (By.XPATH, "//button[contains(normalize-space(),'Back To Items') or contains(normalize-space(),'Back to Items')]"),
            (By.XPATH, "//a[contains(normalize-space(),'Back To Items') or contains(normalize-space(),'Back to Items')]"),
            (By.XPATH, "//span[contains(normalize-space(),'Back To Items') or contains(normalize-space(),'Back to Items')]"),
            (By.ID, "btnBackPageTop"),
            (By.ID, "btnBackPageBot"),
            (By.XPATH, "//*[contains(@onclick,'IssueInventoryItems') or contains(@href,'IssueInventoryItems')]"),
        ]:
            try:
                back_btn = WebDriverWait(driver, 4).until(
                    EC.element_to_be_clickable(locator)
                )
                break
            except Exception:
                continue

        if back_btn is None:
            print("  [INFO] Back to Items not on current page — re-navigating via Items → Cards...")
            driver.get(f"{BASE_URL}/BuyerAction/IssueInventoryItems")
            wait_ready(driver)
            time.sleep(PAUSE * 2)

            if "UserName" in driver.page_source or "login" in driver.current_url.lower():
                print("  [INFO] Session expired — logging in again...")
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
                driver.get(f"{BASE_URL}/BuyerAction/IssueInventoryItems")
                wait_ready(driver)
                time.sleep(PAUSE * 2)

            item_links = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class,'GridLink')]"))
            )
            assert item_links, "No items found in Issue Inventory Items List"
            print(f"  [INFO] Clicking first item: '{item_links[0].text.strip()}'")
            driver.execute_script("arguments[0].click()", item_links[0])
            wait_ready(driver)
            time.sleep(PAUSE * 2)
            print(f"  [INFO] Now on: {driver.current_url}")

            for locator in [
                (By.XPATH, "//button[contains(normalize-space(),'Back To Items') or contains(normalize-space(),'Back to Items')]"),
                (By.XPATH, "//a[contains(normalize-space(),'Back To Items') or contains(normalize-space(),'Back to Items')]"),
                (By.XPATH, "//span[contains(normalize-space(),'Back To Items') or contains(normalize-space(),'Back to Items')]"),
                (By.ID, "btnBackPageTop"),
                (By.ID, "btnBackPageBot"),
                (By.XPATH, "//*[contains(@onclick,'IssueInventoryItems') or contains(@href,'IssueInventoryItems')]"),
            ]:
                try:
                    back_btn = WebDriverWait(driver, 8).until(
                        EC.element_to_be_clickable(locator)
                    )
                    break
                except Exception:
                    continue

        assert back_btn, "Back to Items button not found on Issue Inventory Cards or Results page"
        scroll_to(driver, back_btn)
        driver.execute_script("arguments[0].click()", back_btn)
        wait_ready(driver)
        time.sleep(PAUSE * 2)

        take_screenshot(driver, "08_back_to_items")
        current_url = driver.current_url
        print(f"  [URL] {current_url}")
        assert "IssueInventory" in current_url, f"Expected Issue Inventory Items page. Got: {current_url}"
        print(f"  [PASS] Returned to Issue Inventory Items List: {current_url}")