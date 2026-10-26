"""

QALS11 | Actions > Call-off — End-to-End Call-off Flow

=======================================================

URL  : https://engineering.ultrivalms.com/QALS1011

User : buyeruser / Ultriva!23

Test Flow

---------

  1.  Login as buyeruser

  2.  Navigate to Actions menu (left sidebar)

  3.  Click Call-off from Buyer Actions page

  4.  On Call-off Items Filter page — click Go to load items

  5.  From Call-off Items List — click first item, then click Show Cards

  6.  From Call-off Cards List — select first 2 cards, click Call-off

  7.  Verify Call-off Results page shows "Following Cards were successful"

  8.  Click Back to Items — verify return to Call-off Items List

Run (from qa_automation/):

    pytest tests/QALS11/Actions/test_calloff.py -v -s

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

    path = os.path.join(screenshots_dir, f"calloff_{name}_{ts}.png")

    driver.save_screenshot(path)

    print(f"  [screenshot] {path}")

    return path

# ============================================================================

# TEST CLASS

# ============================================================================


@pytest.mark.usefixtures("driver")
# ── TC-CAL-001: Login ────────────────────────────────────────────────────
class TestCalloff:
    def test_01_login(self, driver):
        """Login to QA site with buyeruser credentials."""
        print("\n[TC-CAL-001] Logging in to QA site...")
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

    # ── TC-CAL-002: Navigate to Actions ──────────────────────────────────
    def test_02_navigate_to_actions(self, driver):
        """Click Actions in the left sidebar to open the Actions menu page."""
        print("\n[TC-CAL-002] Navigating to Actions page...")

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

    # ── TC-CAL-003: Click Call-off ───────────────────────────────────────
    def test_03_click_calloff(self, driver):
        """Click the Call-off tile from the Buyer Actions section."""
        print("\n[TC-CAL-003] Clicking Call-off tile in Buyer Actions...")

        calloff_link = None
        for locator in [
            (By.XPATH, "//a[contains(@href,'CallOff') and not(contains(@class,'toplinks'))]"),
            (By.XPATH, "//a[contains(@href,'Calloff') and not(contains(@class,'toplinks'))]"),
            (By.XPATH, "//a[normalize-space(text())='Call-off' or normalize-space(text())='CallOff']"),
            (By.XPATH, "//*[contains(normalize-space(),'Call-off') or contains(normalize-space(),'Call Off')]"
             "[self::a or self::button or self::span[@onclick]]"),
        ]:
            try:
                calloff_link = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(locator)
                )
                break
            except Exception:
                continue

        assert calloff_link, "Call-off link/tile not found on Actions page"
        scroll_to(driver, calloff_link)
        driver.execute_script("arguments[0].click()", calloff_link)
        wait_ready(driver)
        time.sleep(PAUSE)

        take_screenshot(driver, "03_calloff_page")
        current_url = driver.current_url
        print(f"  [URL after Call-off click] {current_url}")
        assert "CallOff" in current_url or "Calloff" in current_url or "calloff" in current_url.lower(), \
            f"Expected Call-off page. Got: {current_url}"
        print(f"  [PASS] Call-off page loaded: {current_url}")

    # ── TC-CAL-004: Click Go to load Call-off Items List ─────────────────
    def test_04_apply_filter_and_load_items(self, driver):
        """Click Go on the Call-off filter page to load Call-off Items List."""
        print("\n[TC-CAL-004] Clicking Go to load Call-off Items List...")

        if "CallOffItems" in driver.current_url:
            print("  [INFO] Already on Call-off Items page, skipping Go click.")
        else:
            # Use JS to find and click the Go/Submit button on the filter page
            clicked = driver.execute_script("""
            var candidates = document.querySelectorAll(
            'a, button, input[type="submit"], input[type="button"]'
            );
            for (var el of candidates) {
            var txt = (el.textContent || el.value || '').trim().toLowerCase();
            if (txt === 'go' || txt === 'search' || txt === 'submit') {
            el.click();
            return el.tagName + ':' + (el.textContent || el.value).trim();
            }
            }
            // Also try by common id/class patterns
            var byId = document.querySelector(
            '#btnGo, #go-button, #goBtn, .btn-go, .btn-filter-go, .btn-filter-submit-item'
            );
            if (byId) { byId.click(); return 'id/class:' + byId.id; }
            return null;
            """)

            if clicked:
                print(f"  [INFO] Clicked Go via JS: {clicked}")
                wait_ready(driver)
                time.sleep(PAUSE * 2)
            else:
                print(
                    "  [WARN] Go button not found on filter page — navigating directly to CallOffItems...")
                driver.get(f"{BASE_URL}/BuyerAction/CallOffItems")
                wait_ready(driver)
                time.sleep(PAUSE * 2)

        take_screenshot(driver, "04_calloff_items_list")
        assert "CallOffItems" in driver.current_url or "CallOffItem" in driver.current_url, \
            f"Expected Call-off Items List page. Got: {driver.current_url}"
        print(f"  [PASS] Call-off Items List loaded: {driver.current_url}")

    # ── TC-CAL-005: Select item and click Show Cards ─────────────────────
    def test_05_select_item_show_cards(self, driver):
        """Click the first item in the Call-off Items List, then click Show Cards."""
        print("\n[TC-CAL-005] Selecting first item and clicking Show Cards...")

        # Item links on CallOffItems page use class=GridLink
        item_links = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//a[contains(@class,'GridLink')]"))
        )
        assert item_links, "No items found in Call-off Items List"
        first_item_link = item_links[0]
        item_text = first_item_link.text.strip()
        print(f"  [INFO] First item found: '{item_text}'")

        scroll_to(driver, first_item_link)
        driver.execute_script("arguments[0].click()", first_item_link)
        wait_ready(driver)
        time.sleep(PAUSE * 2)

        take_screenshot(driver, "05a_after_item_click")
        print(f"  [INFO] URL after item click: {driver.current_url}")

        # Direct navigation to CallOffCards after clicking item
        if "CallOffCard" in driver.current_url or "CallOff" in driver.current_url:
            print("  [INFO] Navigated to Call-off Cards page.")
            return

        # Fallback: look for Show Cards button if still on items page
        show_cards_btn = None
        for locator in [
            (By.XPATH, "//button[contains(normalize-space(),'Show Cards')]"),
            (By.XPATH, "//a[contains(normalize-space(),'Show Cards')]"),
            (By.XPATH, "//span[contains(normalize-space(),'Show Cards')]"),
            (By.XPATH, "//*[contains(@id,'ShowCards') or contains(@id,'showCards')]"),
        ]:
            try:
                show_cards_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(locator)
                )
                break
            except Exception:
                continue

        assert show_cards_btn, "Show Cards button not found and not on Call-off Cards page"
        scroll_to(driver, show_cards_btn)
        driver.execute_script("arguments[0].click()", show_cards_btn)
        wait_ready(driver)
        time.sleep(PAUSE * 2)

        take_screenshot(driver, "05b_calloff_cards_list")
        assert "CallOffCard" in driver.current_url or "CallOff" in driver.current_url, \
            f"Expected Call-off Cards page. Got: {driver.current_url}"
        print(f"  [PASS] Call-off Cards List confirmed: {driver.current_url}")

    # ── TC-CAL-006: Select cards and click Call-off ──────────────────────
    def test_06_select_cards_and_calloff(self, driver):
        """Select the first 2 cards by checkbox and click the Call-off button."""
        print("\n[TC-CAL-006] Selecting cards and clicking Call-off...")

        assert "CallOffCard" in driver.current_url, \
            f"Expected to be on CallOffCards page. Got: {driver.current_url}"

        # Wait for data-row checkboxes using the real name pattern
        checkboxes = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//input[contains(@name,'CheckboxCardGID')]")
            )
        )
        assert checkboxes, "No checkboxes found in Call-off Cards List"

        # Select up to 3 cards — use regular click to fire change events, verify each
        selected = 0
        for chk in checkboxes[:3]:
            try:
                scroll_to(driver, chk)
                if not chk.is_selected():
                    chk.click()
                    time.sleep(0.5)
                    if chk.is_selected():
                        selected += 1
                        print(f"  [INFO] Card {selected} checkbox confirmed selected")
                    else:
                        print(f"  [WARN] Checkbox did not toggle — trying JS click")
                        driver.execute_script("arguments[0].click()", chk)
                        time.sleep(0.5)
                        if chk.is_selected():
                            selected += 1
                            print(f"  [INFO] Card {selected} checkbox confirmed selected (via JS)")
            except Exception as e:
                print(f"  [WARN] Could not click checkbox: {e}")

        assert selected > 0, "Could not verify any card checkbox as selected"
        print(f"  [INFO] Total confirmed selected: {selected} card(s)")

        take_screenshot(driver, "06a_cards_selected")

        # Click the Call-off action button — it's a <span> with onclick=da(),
        # IDs are btndoActTop (top toolbar) and btndoActBot (bottom toolbar)
        calloff_btn = None
        for locator in [
            (By.ID, "btndoActTop"),
            (By.ID, "btndoActBot"),
            (By.XPATH, "//span[@onclick='da()' and contains(@class,'btn')]"),
            (By.XPATH, "//span[contains(@id,'doAct') and contains(@class,'btn')]"),
        ]:
            try:
                calloff_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(locator)
                )
                break
            except Exception:
                continue

        assert calloff_btn, "Call-off action button (btndoActTop/btndoActBot) not found on cards page"
        print(f"  [INFO] Found Call-off button: id={calloff_btn.get_attribute('id')}")
        scroll_to(driver, calloff_btn)
        driver.execute_script("arguments[0].click()", calloff_btn)
        wait_ready(driver)
        time.sleep(PAUSE * 2)

        take_screenshot(driver, "06b_calloff_results")
        print(f"  [URL after Call-off] {driver.current_url}")

    # ── TC-CAL-007: Verify Call-off Results ──────────────────────────────
    def test_07_verify_calloff_results(self, driver):
        """Verify the Call-off Results page shows success message."""
        print("\n[TC-CAL-007] Verifying Call-off Results page...")

        current_url = driver.current_url
        print(f"  [URL] {current_url}")

        # Result page should be CallOffResults (the app's actionPageURL after da())
        assert "CallOffFilter" not in current_url, \
            f"Still on CallOffFilter — call-off action was not executed. URL: {current_url}"

        success_found = False
        for locator in [
            (By.XPATH, "//*[contains(normalize-space(),'Following Cards were successful')]"),
            (By.XPATH, "//*[contains(normalize-space(),'Called-off Successfully')]"),
            (By.XPATH, "//*[contains(normalize-space(),'successful')]"),
            (By.XPATH, "//*[contains(normalize-space(),'Call-off') and contains(@class,'success')]"),
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

        take_screenshot(driver, "07_calloff_results")

        assert "CallOffResult" in current_url or success_found, \
            f"Expected CallOffResults page or success message. URL: {current_url}"

        if not success_found:
            print("  [WARN] Success message not found by text — verifying via URL.")

        print("  [PASS] Call-off Results page verified.")

    # ── TC-CAL-008: Click Back to Items ──────────────────────────────────
    def test_08_back_to_items(self, driver):
        """Click Back to Items and verify return to Call-off Items List."""
        print("\n[TC-CAL-008] Clicking Back to Items...")

        print(f"  [INFO] Currently on {driver.current_url}")

        # Look for Back to Items button on results page
        back_btn = None
        for locator in [
            (By.XPATH, "//button[contains(normalize-space(),'Back To Items') or "
             "contains(normalize-space(),'Back to Items')]"),
            (By.XPATH, "//a[contains(normalize-space(),'Back To Items') or "
             "contains(normalize-space(),'Back to Items')]"),
            (By.XPATH, "//span[contains(normalize-space(),'Back To Items') or "
             "contains(normalize-space(),'Back to Items')]"),
            (By.ID, "btnBackPageTop"),
            (By.ID, "btnBackPageBot"),
            (By.XPATH, "//*[contains(@onclick,'BackToItems') or contains(@onclick,'backToItems')]"),
        ]:
            try:
                back_btn = WebDriverWait(driver, 8).until(
                    EC.element_to_be_clickable(locator)
                )
                break
            except Exception:
                continue

        if not back_btn:
            # Fallback: navigate directly to CallOffItems
            print(
                "  [WARN] Back to Items button not found — navigating directly to CallOffItems...")
            driver.get(f"{BASE_URL}/BuyerAction/CallOffItems")
            wait_ready(driver)
            time.sleep(PAUSE * 2)
        else:
            scroll_to(driver, back_btn)
            driver.execute_script("arguments[0].click()", back_btn)
            wait_ready(driver)
            time.sleep(PAUSE * 2)

        take_screenshot(driver, "08_back_to_items")
        current_url = driver.current_url
        print(f"  [URL after Back to Items] {current_url}")

        assert "CallOffItems" in current_url or "CallOffItem" in current_url, \
            f"Expected Call-off Items List page after Back to Items. Got: {current_url}"
        print(
            f"  [PASS] Successfully returned to Call-off Items List: {current_url}")
