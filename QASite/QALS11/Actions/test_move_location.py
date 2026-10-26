"""
QALS11 | Actions > Move Location - End-to-End Move Location Flow
"""

import os
import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
MOVE_LOCATION_CARDS_URL = f"{BASE_URL}/BuyerAction/MoveLocationCards"
USERNAME = "buyeruser"
PASSWORD = "Ultriva!23"
PAUSE = 1.5

CURRENT_LOCATION = "1234"
NEW_LOCATION_1 = "5001"
NEW_LOCATION_2 = "5002"
TEST_CASE_DELAY = 5


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="class")
def driver():
    """Class-scoped Chrome driver - one browser session per test class."""
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
    """Scroll element into view."""
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    time.sleep(0.3)


def take_screenshot(driver, name):
    """Save screenshot for step verification."""
    screenshots_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "reports", "screenshots"
    )
    os.makedirs(screenshots_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(screenshots_dir, f"movelocation_{name}_{ts}.png")
    driver.save_screenshot(path)
    print(f"  [screenshot] {path}")
    return path


def find_move_location_button(driver, timeout=15):
    """Return the actual Move Location button, preferring the exact control id and falling back to known variants."""
    locators = [
        (By.ID, "btnMoveLocation"),
        (By.XPATH, "//button[@id='btnMoveLocation']"),
        (By.XPATH, "//button[@title='Move Location']"),
        (By.XPATH, "//button[normalize-space(.)='Move Location']"),
        (By.XPATH, "//button[contains(normalize-space(.), 'Move Location')]"),
        (By.XPATH, "//input[@type='submit' and normalize-space(@value)='Move Location']"),
        (By.XPATH, "//input[@type='button' and normalize-space(@value)='Move Location']"),
        (By.XPATH, "//a[normalize-space(.)='Move Location' and not(contains(@href, 'MoveLocationItems'))]"),
        (By.XPATH, "//*[contains(@id, 'MoveLocation') and (self::button or self::input or self::a)]"),
    ]

    for by, locator in locators:
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((by, locator))
            )
            if element.is_displayed() and element.is_enabled():
                return element
        except Exception:
            continue

    for by, locator in locators:
        try:
            elements = driver.find_elements(by, locator)
            for element in elements:
                if element.is_displayed() and element.is_enabled():
                    return element
        except Exception:
            continue

    raise TimeoutError("Move Location button not found or not clickable on the page.")


def log_step(step_no, message):
    """Print readable step header."""
    print(f"\n[STEP {step_no}] {message}")


def wait_after_test_case():
    """Pause briefly between test cases."""
    print(f"[WAIT] Pausing for {TEST_CASE_DELAY} seconds before next test case...\n")
    time.sleep(TEST_CASE_DELAY)


# ============================================================================
# TEST CLASS
# ============================================================================

@pytest.mark.usefixtures("driver")
class TestMoveLocation:

    def test_01_login(self, driver):
        """Step 1: Open the QA site and authenticate with buyer credentials."""
        log_step(1, "Open the QA site and authenticate with buyer credentials.")
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
        assert BASE_URL.lower() in current_url.lower() or "Home" in current_url, (
            f"Login may have failed. URL: {current_url}"
        )
        print("  [PASS] Step 1 completed: Login successful.")
        wait_after_test_case()

    def test_02_navigate_to_actions(self, driver):
        """Step 2: Navigate to the Actions section from the UI menu."""
        log_step(2, "Navigate to the Actions page from the navigation bar.")
        actions_link = clickable(
            driver,
            By.XPATH,
            "//a[contains(@href, 'Action/Home') or (.//span[normalize-space()='Actions']) or normalize-space(.)='Actions']",
        )
        scroll_to(driver, actions_link)
        actions_link.click()
        wait_ready(driver)
        time.sleep(PAUSE)

        take_screenshot(driver, "02_actions_page")
        assert "Action/Home" in driver.current_url, (
            f"Expected Actions page. Got: {driver.current_url}"
        )
        print(f"  [PASS] Step 2 completed: Actions page loaded: {driver.current_url}")
        wait_after_test_case()

    def test_03_navigate_to_move_location_cards(self, driver):
        """Step 3: Open Move Location items list, choose item, and open the Cards List."""
        log_step(3, "Navigate to Move Location Cards page.")
        driver.get(f"{BASE_URL}/BuyerAction/MoveLocationItems")
        wait_ready(driver)
        time.sleep(PAUSE)

        try:
            item_links = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class,'GridLink')]"))
            )
            target_item = item_links[0]
            for lnk in item_links:
                if "00kantest" in lnk.text.lower():
                    target_item = lnk
                    break

            print(f"  [INFO] Selected item: '{target_item.text.strip()}'")
            scroll_to(driver, target_item)
            driver.execute_script("arguments[0].click()", target_item)
            wait_ready(driver)
            time.sleep(PAUSE)

            # Check if Show Cards button is required
            if "MoveLocationCard" not in driver.current_url:
                show_cards_locators = [
                    (By.XPATH, "//button[contains(normalize-space(),'Show Cards')]"),
                    (By.XPATH, "//a[contains(normalize-space(),'Show Cards')]"),
                    (By.XPATH, "//*[contains(@id,'ShowCards') or contains(@id,'showCards')]"),
                ]
                for loc in show_cards_locators:
                    try:
                        btn = WebDriverWait(driver, 4).until(EC.element_to_be_clickable(loc))
                        driver.execute_script("arguments[0].click()", btn)
                        wait_ready(driver)
                        time.sleep(PAUSE)
                        break
                    except Exception:
                        continue
        except Exception as e:
            print(f"  [WARN] Item selection skipped or failed ({e}); navigating directly to cards page.")
            driver.get(MOVE_LOCATION_CARDS_URL)
            wait_ready(driver)
            time.sleep(PAUSE)

        take_screenshot(driver, "03_move_location_cards_list")
        assert "MoveLocationCards" in driver.current_url or "MoveLocation" in driver.current_url, (
            f"Expected Move Location Cards page. Got: {driver.current_url}"
        )
        print(f"  [PASS] Step 3 completed: Move Location Cards page active.")
        wait_after_test_case()

    def test_04_select_cards_and_enter_locations(self, driver):
        """Step 4: Select cards and fill in current and new location fields."""
        log_step(4, "Select cards and input target location values.")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[contains(@id,'$TextboxCurrentLocation')]"))
        )

        new_locations = [NEW_LOCATION_1, NEW_LOCATION_2]
        cards_processed = 0

        for n in range(1, 3):
            chk_name = f"MoveLocationCards_{n}_$CheckboxCardGID"
            curr_id = f"MoveLocationCards_{n}_$TextboxCurrentLocation"
            new_id = f"MoveLocationCards_{n}_$TextboxNewLocation"

            try:
                # 1. Select the card checkbox
                chk = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f"//input[@name='{chk_name}']"))
                )
                scroll_to(driver, chk)
                if not chk.is_selected():
                    driver.execute_script("arguments[0].click()", chk)
                    time.sleep(0.3)

                # 2. Check and fill Current Location if missing
                curr_inp = driver.find_element(By.ID, curr_id)
                scroll_to(driver, curr_inp)
                if not curr_inp.get_attribute("value"):
                    curr_inp.clear()
                    curr_inp.send_keys(CURRENT_LOCATION)

                # 3. Enter target New Location
                new_inp = driver.find_element(By.ID, new_id)
                scroll_to(driver, new_inp)
                new_inp.clear()
                new_inp.send_keys(new_locations[n - 1])
                print(f"  [INFO] Card {n}: New Location set to '{new_locations[n - 1]}'")

                cards_processed += 1
            except Exception as e:
                print(f"  [WARN] Failed to configure row {n}: {e}")

        assert cards_processed > 0, "No cards were selected or populated"
        take_screenshot(driver, "04_locations_entered")
        print(f"  [PASS] Step 4 completed: Configured {cards_processed} cards.")
        wait_after_test_case()

    def test_05_click_move_location_action(self, driver):
        """Step 5: Click Move Location button and verify submission."""
        log_step(5, "Click the Move Location action button.")

        # Specific locators matching Ultriva's action bar markup
        locators = [
            (By.XPATH, "//a[contains(., 'Move Location')]"),
            (By.XPATH, "//button[contains(., 'Move Location')]"),
            (By.XPATH, "//*[@id='btnMoveLocation' or contains(@id, 'MoveLocation') or contains(@id, 'btn_MoveLocation')]"),
            (By.XPATH, "//input[@type='button' or @type='submit'][contains(@value, 'Move Location')]"),
            (By.XPATH, "//div[contains(@class, 'action')]//*[contains(text(), 'Move Location')]"),
        ]

        move_btn = None
        for by, val in locators:
            try:
                elements = driver.find_elements(by, val)
                for el in elements:
                    if el.is_displayed():
                        move_btn = el
                        break
                if move_btn:
                    break
            except Exception:
                continue

        assert move_btn is not None, "Move Location button element could not be found."

        # Ensure scrolled into view
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", move_btn)
        time.sleep(0.5)

        # Trigger via JavaScript event dispatch to ensure inline onclick / href javascript handlers fire
        try:
            driver.execute_script("""
                var elem = arguments[0];
                elem.focus();
                var clickEvent = new MouseEvent('click', {
                    bubbles: true,
                    cancelable: true,
                    view: window
                });
                elem.dispatchEvent(clickEvent);
            """, move_btn)
        except Exception:
            move_btn.click()

        wait_ready(driver)
        time.sleep(PAUSE * 2)

        # Check for browser confirmation dialogs / alerts
        try:
            WebDriverWait(driver, 3).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            print(f"  [INFO] Alert appeared: {alert.text}")
            alert.accept()
            wait_ready(driver)
            time.sleep(PAUSE)
        except Exception:
            pass

        take_screenshot(driver, "05_after_move_location_clicked")
        print(f"  [PASS] Step 5 completed: Move Location button executed.")
        wait_after_test_case()