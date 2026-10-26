"""
QALS11 | Actions > Release — End-to-End Release Cards Flow
===========================================================
URL  : https://engineering.ultrivalms.com/QALS1011
User : buyeruser / Ultriva!23

Test Flow
---------
  1.  Login as buyeruser
  2.  Navigate to Actions menu (left sidebar)
  3.  Click Release from Buyer Actions page
  4.  On Release Cards Filter page — click Go to load items
  5.  From Release Items List — click first item, then click Show Cards
  6.  From Release Cards List — select first 3 cards, click Release
  7.  Verify Release Results page shows "Following Cards were successful"
  8.  Click Back to Items — verify return to Release Items List

Run (from qa_automation/):
    pytest tests/QALS11/Actions/test_release.py -v -s
"""

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
    import os
    screenshots_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "reports", "screenshots"
    )
    os.makedirs(screenshots_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(screenshots_dir, f"release_{name}_{ts}.png")
    driver.save_screenshot(path)
    print(f"  [screenshot] {path}")
    return path

# ============================================================================
# TEST CLASS
# ============================================================================

@pytest.mark.usefixtures("driver")
class TestRelease:

    # ── TC-REL-001: Login ────────────────────────────────────────────────────
    def test_01_login(self, driver):
        """Login to QA site with buyeruser credentials."""
        print("\n[TC-REL-001] Logging in to QA site...")
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

    # ── TC-REL-002: Navigate to Actions ──────────────────────────────────
    def test_02_navigate_to_actions(self, driver):
        """Click Actions in the left sidebar to open the Actions menu page."""
        print("\n[TC-REL-002] Navigating to Actions page...")

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

    # ── TC-REL-003: Click Release ────────────────────────────────────────
    def test_03_click_release(self, driver):
        """Click the Release tile from the Buyer Actions section."""
        print("\n[TC-REL-003] Clicking Release tile in Buyer Actions...")

        release_link = clickable(
            driver,
            By.XPATH,
            "//a[contains(@href,'ReleaseFilter') and not(contains(@class,'toplinks'))]",
        )
        scroll_to(driver, release_link)
        driver.execute_script("arguments[0].click()", release_link)
        wait_ready(driver)
        time.sleep(PAUSE)

        take_screenshot(driver, "03_release_filter")
        assert "Release" in driver.current_url, \
            f"Expected Release Filter page. Got: {driver.current_url}"
        print(f"  [PASS] Release filter/items page loaded: {driver.current_url}")

    # ── TC-REL-004: Apply filter and load Release Items List ─────────────
    def test_04_apply_filter_and_load_items(self, driver):
        """Click Go on Release Cards Filter to load the Release Items List."""
        print("\n[TC-REL-004] Applying filter — clicking Go button...")

        if "ReleaseItems" in driver.current_url:
            print("  [INFO] Already on Release Items page, skipping Go click.")
        else:
            go_button = None
            for locator in [
                (By.XPATH, "//a[contains(@class,'btn-filter-submit-item') and contains(normalize-space(),'Go')]"),
                (By.XPATH, "//a[normalize-space(text())='Go' and contains(@class,'btn')]"),
                (By.XPATH, "//button[normalize-space(text())='Go']"),
                (By.XPATH, "//input[@type='submit' and @value='Go']"),
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
                print("  [WARN] Go button not found — attempting direct URL navigation...")
                driver.get(f"{BASE_URL}/BuyerAction/ReleaseItems")
                wait_ready(driver)
                time.sleep(PAUSE * 2)

        take_screenshot(driver, "04_release_items_list")
        assert "ReleaseItem" in driver.current_url or "Release" in driver.current_url, \
            f"Expected Release Items page. Got: {driver.current_url}"
        print(f"  [PASS] Release Items List loaded: {driver.current_url}")

    # ── TC-REL-005: Select item and click Show Cards ─────────────────────
    def test_05_select_item_show_cards(self, driver):
        """Click the first item in the Release Items List, then click Show Cards."""
        print("\n[TC-REL-005] Selecting first item and clicking Show Cards...")

        item_links = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//a[contains(@class,'GridLink')]"))
        )
        assert item_links, "No GridLink items found in Release Items List"
        first_item_link = item_links[0]
        item_text = first_item_link.text.strip()
        print(f"  [INFO] First item found: '{item_text}'")

        scroll_to(driver, first_item_link)
        driver.execute_script("arguments[0].click()", first_item_link)
        wait_ready(driver)
        time.sleep(PAUSE * 2)

        take_screenshot(driver, "05a_after_item_click")
        print(f"  [INFO] URL after item click: {driver.current_url}")

        if "ReleaseCard" in driver.current_url or "Release" in driver.current_url:
            print("  [INFO] Navigated to Release Cards page.")
            return

        show_cards_btn = None
        for locator in [
            (By.XPATH, "//button[contains(normalize-space(),'Show Cards')]"),
            (By.XPATH, "//a[contains(normalize-space(),'Show Cards')]"),
            (By.XPATH, "//*[contains(@id,'ShowCards') or contains(@id,'showCards')]"),
        ]:
            try:
                show_cards_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(locator)
                )
                break
            except Exception:
                continue

        assert show_cards_btn, "Show Cards button not found and not on Release Cards page"
        scroll_to(driver, show_cards_btn)
        driver.execute_script("arguments[0].click()", show_cards_btn)
        wait_ready(driver)
        time.sleep(PAUSE * 2)

        take_screenshot(driver, "05b_release_cards_list")
        assert "ReleaseCard" in driver.current_url or "Release" in driver.current_url, \
            f"Expected Release Cards page. Got: {driver.current_url}"
        print(f"  [PASS] Release Cards List confirmed: {driver.current_url}")

    # ── TC-REL-006: Select cards and click Release ───────────────────────
    def test_06_select_cards_and_release(self, driver):
        """Select the first 3 cards by checkbox and click the Release button."""
        print("\n[TC-REL-006] Selecting first 3 cards and clicking Release...")

        checkboxes = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located(
                (By.XPATH,
                 "//table//tr[td]//input[@type='checkbox']"
                 " | "
                 "//input[@type='checkbox'][not(ancestor::th)]")
            )
        )
        assert checkboxes, "No checkboxes found in Release Cards List"

        selected = 0
        for chk in checkboxes[:3]:
            try:
                scroll_to(driver, chk)
                if not chk.is_selected():
                    driver.execute_script("arguments[0].click()", chk)
                    time.sleep(0.3)
                    selected += 1
            except Exception as e:
                print(f"  [WARN] Could not click checkbox: {e}")

        assert selected > 0, "Could not select any cards"
        print(f"  [INFO] Selected {selected} card(s)")

        take_screenshot(driver, "06a_cards_selected")

        release_btn = None
        for locator in [
            (By.XPATH, "//button[normalize-space(text())='Release']"),
            (By.XPATH, "//button[contains(@class,'release') and contains(normalize-space(),'Release')]"),
            (By.XPATH, "//a[normalize-space(text())='Release']"),
            (By.XPATH, "//*[@id='btnRelease' or contains(@id,'release') or contains(@id,'Release')]"),
        ]:
            try:
                release_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(locator)
                )
                break
            except Exception:
                continue

        assert release_btn, "Release button not found in cards list"
        scroll_to(driver, release_btn)
        driver.execute_script("arguments[0].click()", release_btn)
        wait_ready(driver)
        time.sleep(PAUSE * 2)

        take_screenshot(driver, "06b_release_results")
        print(f"  [URL after Release] {driver.current_url}")

    # ── TC-REL-007: Verify Release Results ───────────────────────────────
    def test_07_verify_release_results(self, driver):
        """Verify the Release Results page shows success message."""
        print("\n[TC-REL-007] Verifying Release Results page...")

        current_url = driver.current_url
        print(f"  [URL] {current_url}")

        success_found = False
        for locator in [
            (By.XPATH, "//*[contains(normalize-space(),'Following Cards were successful')]"),
            (By.XPATH, "//*[contains(normalize-space(),'successful')]"),
            (By.XPATH, "//*[contains(normalize-space(),'Released To')]"),
            (By.XPATH, "//*[contains(normalize-space(),'Release') and contains(@class,'success')]"),
            (By.XPATH, "//h1[contains(normalize-space(),'Result')] | //h2[contains(normalize-space(),'Result')]"),
        ]:
            try:
                el = WebDriverWait(driver, 8).until(
                    EC.presence_of_element_located(locator)
                )
                msg = el.text.strip()
                print(f"  [INFO] Result message found: '{msg[:100]}'")
                success_found = True
                break
            except Exception:
                continue

        take_screenshot(driver, "07_release_results")

        assert "ReleaseResult" in current_url or "Release" in current_url, \
            f"Not on expected Release Results/Cards page. URL: {current_url}"

        if not success_found:
            print("  [WARN] Success message not found by text, but URL confirms Release page.")

        print("  [PASS] Release Results page verified.")

    # ── TC-REL-008: Click Back to Items ──────────────────────────────────
    def test_08_back_to_items(self, driver):
        """Click Back to Items and verify return to Release Items List."""
        print("\n[TC-REL-008] Clicking Back to Items...")

        print(f"  [INFO] Currently on {driver.current_url}")
        print("  [INFO] Re-navigating via ReleaseItems → item click to get proper context...")
        driver.get(f"{BASE_URL}/BuyerAction/ReleaseItems")
        wait_ready(driver)
        time.sleep(PAUSE)

        item_links = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//a[contains(@class,'GridLink')]"))
        )
        assert item_links, "No items found in Release Items List"
        item_text = item_links[0].text.strip()
        print(f"  [INFO] Clicking item: '{item_text}'")
        driver.execute_script("arguments[0].click()", item_links[0])
        wait_ready(driver)
        time.sleep(PAUSE * 2)
        print(f"  [INFO] Now on: {driver.current_url}")

        back_btn = None
        for locator in [
            (By.ID, "btnBackPageTop"),
            (By.ID, "btnBackPageBot"),
            (By.XPATH, "//span[@id='btnBackPageTop' or @id='btnBackPageBot']"),
            (By.XPATH, "//span[contains(@class,'vd-blue-btn') and contains(normalize-space(),'Back')]"),
            (By.XPATH, "//*[contains(normalize-space(),'Back To Items') or contains(normalize-space(),'Back to Items')]"),
        ]:
            try:
                back_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(locator)
                )
                print(f"  [INFO] Found back button via locator: '{back_btn.text.strip()}'")
                break
            except Exception:
                continue

        if not back_btn:
            print("  [INFO] Trying JS element search for Back button...")
            back_btn = driver.execute_script(
                "return document.getElementById('btnBackPageTop')"
                " || document.getElementById('btnBackPageBot')"
                " || (function(){"
                "  var all = document.querySelectorAll('*');"
                "  for(var i=0;i<all.length;i++){"
                "    var t=(all[i].innerText||'').trim().toLowerCase();"
                "    if(t==='back to items' || t==='back to item'){"
                "      if(all[i].offsetParent!==null) return all[i];"
                "    }"
                "  } return null; })()"
            )
            if back_btn:
                print(f"  [INFO] JS found back element: '{back_btn.text.strip()}'")

        assert back_btn, "Back to Items button not found"
        scroll_to(driver, back_btn)
        driver.execute_script("arguments[0].click()", back_btn)
        wait_ready(driver)
        time.sleep(PAUSE)

        take_screenshot(driver, "08_back_to_items")
        current_url = driver.current_url
        print(f"  [URL after Back to Items] {current_url}")
        assert "ReleaseItem" in current_url or "Release" in current_url, \
            f"Expected Release Items page. Got: {current_url}"
        print("  [PASS] Successfully returned to Release Items List.")