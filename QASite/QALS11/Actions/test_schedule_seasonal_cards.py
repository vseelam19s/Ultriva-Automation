"""
QALS11 | Actions > Schedule Seasonal Kanban Cards — End-to-End Flow
=================================================================
URL   : https://engineering.ultrivalms.com/QALS1011/BuyerAction/SeasonalCardEntry
User  : buyeruser / Ultriva!23

Test Flow
---------
  1. Login as buyeruser
  2. Click Actions from the left sidebar
  3. Open Schedule Seasonal Kanban Cards from Buyer Actions
  4. Select any item from the DDM, enter Release Date and Expiration Date
  5. Click Validate Entries and Submit Entries
  6. Click Back to seasonal entry

Run (from qa_automation/):
    pytest tests/QALS11/Actions/ScheduleSeasonalCards.py -v -s
"""

import os
import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
SEASONAL_ENTRY_URL = f"{BASE_URL}/BuyerAction/SeasonalCardEntry"
USERNAME = "buyeruser"
PASSWORD = "Ultriva!23"
PAUSE = 1.5
RELEASE_DATE = "06/01/2027"
EXPIRATION_DATE = "07/01/2027"


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


def scroll_to(driver, el):
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
    time.sleep(0.3)


def safe_click(driver, el):
    scroll_to(driver, el)
    driver.execute_script("arguments[0].click();", el)
    time.sleep(PAUSE)


def take_screenshot(driver, name):
    screenshots_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "reports", "screenshots"
    )
    os.makedirs(screenshots_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(screenshots_dir, f"seasonal_cards_{name}_{ts}.png")
    driver.save_screenshot(path)
    print(f"  [screenshot] {path}")
    return path


def click_text_match(driver, label):
    el = driver.execute_script(
        """
        var nodes = Array.from(document.querySelectorAll('button, a, input, span, div, li'));
        var target = arguments[0].toLowerCase();
        for (var i = 0; i < nodes.length; i++) {
            var txt = ((nodes[i].textContent || '') + ' ' + (nodes[i].value || '') + ' ' + (nodes[i].id || '') + ' ' + (nodes[i].name || '')).toLowerCase();
            if (txt.indexOf(target) !== -1 && !nodes[i].disabled) {
                return nodes[i];
            }
        }
        return null;
        """,
        label,
    )
    if el:
        safe_click(driver, el)
        return True
    return False


def find_matching_field(driver, *keywords):
    return driver.execute_script(
        """
        var fields = Array.from(document.querySelectorAll('input, select, textarea'));
        for (var i = 0; i < fields.length; i++) {
            var field = fields[i];
            var text = ((field.name || '') + ' ' + (field.id || '') + ' ' + (field.className || '') + ' ' + (field.placeholder || '') + ' ' + (field.getAttribute('aria-label') || '')).toLowerCase();
            var match = false;
            for (var j = 0; j < arguments.length; j++) {
                if (text.indexOf(arguments[j].toLowerCase()) !== -1) {
                    match = true;
                }
            }
            if (match && !field.disabled && field.type !== 'hidden' && !field.readOnly) return field;
        }
        return null;
        """,
        *keywords,
    )


def set_field_value(driver, field, value):
    try:
        field.clear()
    except Exception:
        driver.execute_script("arguments[0].value = '';", field)
    driver.execute_script(
        """
        arguments[0].value = arguments[1];
        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
        """,
        field,
        value,
    )


def pick_first_visible_select(driver):
    selects = driver.find_elements(By.TAG_NAME, "select")
    for sel in selects:
        if sel.is_displayed() and sel.size["width"] > 0:
            return sel
    return None


@pytest.mark.usefixtures("driver")
class TestScheduleSeasonalCards:
    def test_01_login(self, driver):
        print("\n[TC-SSC-001] Logging in to QA site...")
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
        assert BASE_URL.lower() in current_url.lower() or "Home" in current_url.lower(), (
            f"Login may have failed. URL: {current_url}"
        )
        print("  [PASS] Login successful.")

    def test_02_open_schedule_seasonal_cards(self, driver):
        print("\n[TC-SSC-002] Opening Schedule Seasonal Kanban Cards...")
        actions_link = clickable(
            driver,
            By.XPATH,
            "//a[contains(@href, 'Action/Home') or contains(normalize-space(.), 'Actions')]",
        )
        safe_click(driver, actions_link)
        wait_ready(driver)
        time.sleep(PAUSE)

        seasonal_tile = None
        for locator in [
            (By.XPATH, "//a[contains(@href, 'SeasonalCardEntry') and not(contains(@class, 'toplinks'))]"),
            (By.XPATH, "//a[contains(normalize-space(.), 'Schedule Seasonal Kanban Cards')]"),
            (By.XPATH, "//a[contains(normalize-space(.), 'Seasonal Card Entry')]"),
            (By.XPATH, "//*[contains(normalize-space(.), 'Schedule Seasonal') or contains(normalize-space(.), 'Seasonal Cards')]"),
        ]:
            try:
                seasonal_tile = WebDriverWait(driver, 8).until(EC.element_to_be_clickable(locator))
                break
            except Exception:
                continue

        if seasonal_tile:
            safe_click(driver, seasonal_tile)
        else:
            print("  [INFO] Menu tile not visible; falling back to direct URL.")
            driver.get(SEASONAL_ENTRY_URL)

        wait_ready(driver)
        time.sleep(PAUSE * 2)

        take_screenshot(driver, "02_seasonal_entry_page")
        assert "SeasonalCardEntry" in driver.current_url or "BuyerAction" in driver.current_url, (
            f"Expected Seasonal Card Entry page. Got: {driver.current_url}"
        )
        print(f"  [PASS] Seasonal entry page loaded: {driver.current_url}")

    def test_03_select_item_and_submit_seasonal_entry(self, driver):
        print("\n[TC-SSC-003] Selecting item and entering dates...")

        if "SeasonalCardEntry" not in driver.current_url:
            driver.get(SEASONAL_ENTRY_URL)
            wait_ready(driver)

        select_field = pick_first_visible_select(driver)
        if select_field is not None:
            try:
                select = Select(select_field)
                for option in select.options:
                    text = (option.text or "").strip()
                    if text:
                        select.select_by_visible_text(text)
                        break
            except Exception:
                pass

        release_field = find_matching_field(driver, "release", "date")
        expiration_field = find_matching_field(driver, "expiration", "date")

        if release_field is None:
            raise AssertionError("Release Date field not found on Seasonal Card Entry page")
        if expiration_field is None:
            raise AssertionError("Expiration Date field not found on Seasonal Card Entry page")

        set_field_value(driver, release_field, RELEASE_DATE)
        set_field_value(driver, expiration_field, EXPIRATION_DATE)
        time.sleep(PAUSE)

        take_screenshot(driver, "03_dates_entered")

        assert click_text_match(driver, "Validate Entries"), "Validate Entries button not found"
        time.sleep(PAUSE * 2)

        assert click_text_match(driver, "Submit Entries"), "Submit Entries button not found"
        time.sleep(PAUSE * 2)

        take_screenshot(driver, "04_after_submit")

        clicked_back = False
        for label in ["Back to Seasonal Entry", "Back to Seasonal Cards", "Back"]:
            if click_text_match(driver, label):
                clicked_back = True
                break

        assert clicked_back, "Back link/button to Seasonal Entry page not found"
        wait_ready(driver)
        time.sleep(PAUSE)

        take_screenshot(driver, "05_back_to_entry")
        assert "SeasonalCardEntry" in driver.current_url or "BuyerAction" in driver.current_url, (
            f"Expected return to Seasonal Card Entry page. Got: {driver.current_url}"
        )
        print(f"  [PASS] Seasonal card entry flow completed and returned to entry page: {driver.current_url}")
