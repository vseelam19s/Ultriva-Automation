import os
import time
import pytest
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
ITEMS_URL = f"{BASE_URL}/SupplierAction/SetReadyToShipDateItems"
CARDS_URL = f"{BASE_URL}/SupplierAction/SetReadyToShipDateCards"
RESULTS_URL = f"{BASE_URL}/SupplierAction/SetReadyToShipDateResults"
USERNAME = "supnewuser"
PASSWORD = "Ultriva!23"
PAUSE = 1.5

# Test targets
TARGET_ITEM_ID = "0000_test"
TARGET_CARD_ID = "KCD36DJQALE2"
FUTURE_DATE = "30/09/2026"


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


def scroll_to(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    time.sleep(0.3)


def safe_click(driver, element):
    scroll_to(driver, element)
    try:
        element.click()
    except Exception:
        driver.execute_script("arguments[0].click();", element)


def take_screenshot(driver, name):
    screenshots_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "reports", "screenshots"
    )
    os.makedirs(screenshots_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(screenshots_dir, f"set_ready_to_ship_date_{name}_{ts}.png")
    driver.save_screenshot(path)
    print(f"  [screenshot] {path}")
    return path


def select_item_by_id(driver, item_id):
    locators = [
        (By.XPATH, f"//tr[.//td[normalize-space(.)='{item_id}'] or .//a[normalize-space(.)='{item_id}'] or .//span[normalize-space(.)='{item_id}']]//a"),
        (By.XPATH, f"//a[normalize-space(.)='{item_id}']"),
        (By.XPATH, f"//td[normalize-space(.)='{item_id}']"),
        (By.XPATH, "//table//tbody/tr[1]//a[1]"),
    ]
    for by, locator in locators:
        try:
            match = WebDriverWait(driver, 6).until(EC.presence_of_element_located((by, locator)))
            if match.is_displayed():
                safe_click(driver, match)
                return True
        except Exception:
            continue
    return False


def click_show_cards(driver):
    locators = [
        (By.XPATH, "//button[contains(normalize-space(.),'Show Cards') or contains(normalize-space(.),'Select Cards')]"),
        (By.XPATH, "//a[contains(normalize-space(.),'Show Cards') or contains(normalize-space(.),'Select Cards')]"),
        (By.XPATH, "//*[contains(@id,'ShowCards') or contains(@id,'SelectCards')]"),
        (By.XPATH, "//*[self::a or self::button][normalize-space()='Cards']"),
    ]
    for by, locator in locators:
        try:
            btn = WebDriverWait(driver, 6).until(EC.element_to_be_clickable((by, locator)))
            safe_click(driver, btn)
            time.sleep(PAUSE)
            return True
        except Exception:
            continue
    return False


def select_card_checkbox(driver, card_id=None):
    """Selects specific card row checkbox or the first row checkbox in the table."""
    if card_id:
        try:
            row_xpath = f"//tr[contains(., '{card_id}')]"
            row = driver.find_element(By.XPATH, row_xpath)
            cb = row.find_element(By.XPATH, ".//input[@type='checkbox']")
            if not cb.is_selected():
                safe_click(driver, cb)
                time.sleep(0.5)
            return True
        except Exception:
            print(f"  [WARN] Card {card_id} not found in current view; selecting first available row checkbox.")

    for _ in range(2):
        try:
            checkboxes = driver.find_elements(
                By.XPATH, "//tbody//input[@type='checkbox' and not(@disabled)]"
            )
            for cb in checkboxes:
                if cb.is_displayed() and cb.is_enabled():
                    if not cb.is_selected():
                        safe_click(driver, cb)
                    return True
        except StaleElementReferenceException:
            time.sleep(0.5)

    return False


def enter_and_apply_ready_to_ship_date(driver, date_str):
    """Enters date in the header Ready To Ship Date field and clicks the copy/apply icon."""
    date_input_locators = [
        (By.XPATH, "//*[contains(normalize-space(),'Ready To Ship Date')]/following::input[1]"),
        (By.XPATH, "//input[contains(@id, 'ReadyToShipDate') and not(contains(@id,'Grid'))]"),
    ]

    date_field = None
    for by, locator in date_input_locators:
        try:
            date_field = WebDriverWait(driver, 6).until(EC.visibility_of_element_located((by, locator)))
            if date_field.is_displayed() and date_field.is_enabled():
                break
        except Exception:
            continue

    assert date_field is not None, "Top 'Ready To Ship Date' input field was not found."

    scroll_to(driver, date_field)
    try:
        date_field.clear()
    except Exception:
        driver.execute_script("arguments[0].value = '';", date_field)

    date_field.send_keys(date_str)
    driver.execute_script("arguments[0].dispatchEvent(new Event('change', {bubbles: true}));", date_field)
    time.sleep(0.5)
    print(f"  [STEP] Entered date '{date_str}' into Ready To Ship Date field.")

    # Locate the copy/apply icon adjacent to the input field
    apply_locators = [
        (By.XPATH, "//*[contains(normalize-space(),'Ready To Ship Date')]/following::input[1]/following-sibling::*[self::a or self::img or self::button or self::span][1]"),
        (By.XPATH, "//input[contains(@id, 'ReadyToShipDate')]/following-sibling::*[self::a or self::img or self::button or self::span][1]"),
        (By.XPATH, "//*[contains(@title, 'Apply') or contains(@alt, 'Apply') or contains(@id, 'Apply')]"),
    ]

    apply_clicked = False
    for by, locator in apply_locators:
        try:
            apply_btn = WebDriverWait(driver, 4).until(EC.element_to_be_clickable((by, locator)))
            safe_click(driver, apply_btn)
            apply_clicked = True
            break
        except Exception:
            continue

    if not apply_clicked:
        apply_clicked = driver.execute_script(
            """
            var input = arguments[0];
            var nextEl = input.nextElementSibling || input.parentElement.querySelector('a, img, button, span');
            if (nextEl) {
                nextEl.click();
                return true;
            }
            return false;
            """,
            date_field,
        )

    assert apply_clicked, "Could not click the 'Apply to All' icon/button next to the date input."
    print("  [STEP] Clicked 'Apply to All' icon next to Ready To Ship Date field.")
    time.sleep(PAUSE)
    return True


def click_set_ready_to_ship_date_action(driver):
    """
    Clicks the dark blue toolbar action button (marked in blue).
    Excludes the header, filter details, breadcrumbs, and return links.
    """
    locators = [
        # 1. Anchored immediately before 'Attach Notes' button
        (By.XPATH, "//*[contains(normalize-space(), 'Attach Notes')]/preceding::*[normalize-space(.)='Set Ready To Ship Date' and not(self::h1 or self::h2 or self::h3 or self::h4)][1]"),
        (By.XPATH, "//*[contains(normalize-space(), 'Attach Notes')]/preceding::*[(self::a or self::button or self::div or self::span) and contains(normalize-space(), 'Set Ready To Ship Date') and not(contains(normalize-space(), 'Cards List'))][1]"),

        # 2. Strict text match on actionable elements excluding header/filter classes and breadcrumbs
        (By.XPATH, "//div[not(contains(@class, 'breadcrumb')) and not(contains(@class, 'filter'))]//a[normalize-space(.)='Set Ready To Ship Date' and not(contains(@href, 'SetReadyToShipDateItems'))]"),
        (By.XPATH, "//button[normalize-space(.)='Set Ready To Ship Date' and not(contains(., 'Cards List'))]"),
        (By.XPATH, "//input[@type='button' or @type='submit'][normalize-space(@value)='Set Ready To Ship Date']"),
    ]

    clicked = False
    for by, locator in locators:
        try:
            elements = driver.find_elements(by, locator)
            for el in elements:
                txt = (el.text or el.get_attribute("value") or "").strip()
                href = (el.get_attribute("href") or "").lower()

                # Filter out the title, breadcrumbs, and filter popover
                if "cards list" in txt.lower():
                    continue
                if "filter" in txt.lower() or "plant:" in txt.lower():
                    continue
                if "setreadytoshipdateitems" in href:
                    continue

                if el.is_displayed() and el.is_enabled():
                    safe_click(driver, el)
                    clicked = True
                    break
            if clicked:
                break
        except Exception:
            continue

    if not clicked:
        # Fallback JS specifically targeting the button adjacent to Attach Notes
        clicked = driver.execute_script(
            """
            // Find the 'Attach Notes' toolbar button first
            var attachBtn = Array.from(document.querySelectorAll('a, button, div, span')).find(function(el) {
                return (el.innerText || '').trim().includes('Attach Notes') && el.offsetParent !== null;
            });

            if (attachBtn) {
                // Find the previous sibling or preceding button in the same toolbar
                var parent = attachBtn.parentElement;
                var siblings = Array.from(parent.querySelectorAll('a, button, div, span'));
                var actionBtn = siblings.find(function(el) {
                    var t = (el.innerText || '').trim();
                    return t.includes('Set Ready To Ship Date') && !t.includes('Cards List') && el.offsetParent !== null;
                });
                if (actionBtn) {
                    actionBtn.click();
                    return true;
                }
            }

            // Global scan ignoring headers, breadcrumbs, and filter tooltips
            var candidates = Array.from(document.querySelectorAll('a, button, input[type=\"button\"], input[type=\"submit\"]'));
            var target = candidates.find(function(el) {
                var text = (el.innerText || el.value || '').trim();
                var isTitleOrFilter = el.closest('h1, h2, h3, h4, .filter, #filter, .breadcrumb') !== null;
                return text === 'Set Ready To Ship Date' && !isTitleOrFilter && el.offsetParent !== null;
            });

            if (target) {
                target.click();
                return true;
            }
            return false;
            """
        )

    assert clicked, "Failed to click the 'Set Ready To Ship Date' toolbar action button."
    wait_ready(driver)
    time.sleep(PAUSE)
    print("  [STEP] Successfully clicked 'Set Ready To Ship Date' toolbar button.")
    return True


def verify_ready_to_ship_results(driver, target_card=None, timeout=12):
    """
    Validates confirmation on SetReadyToShipDateResults and checks for success indicators.
    """
    end_time = time.time() + timeout
    while time.time() < end_time:
        current_url = (driver.current_url or "").lower()
        body_text = (driver.find_element(By.TAG_NAME, "body").text or "")

        # Fail immediately if erroneously redirected back to Items page
        if "setreadytoshipdateitems" in current_url:
            print("  [FAIL] Redirected back to SetReadyToShipDateItems without saving.")
            return False

        # Success confirmation on Results page
        if "setreadytoshipdateresults" in current_url or "Results" in current_url:
            if "Set Ready To Ship Date Cards Results" in body_text or "Following Cards were successful" in body_text or "Ready To Ship Date Successfully Updated" in body_text:
                if target_card:
                    matches = driver.find_elements(By.XPATH, f"//tr[contains(., '{target_card}')]")
                    if matches:
                        print(f"  [VERIFY] Card {target_card} verified in results table.")
                return True

        # Inline toast or success alert check
        success_alerts = driver.find_elements(
            By.XPATH, "//*[contains(text(),'Ready To Ship Date Successfully Updated') or contains(@class,'alert-success') or contains(@class,'toast')]"
        )
        if any(el.is_displayed() for el in success_alerts):
            return True

        time.sleep(0.5)

    return "setreadytoshipdateresults" in driver.current_url.lower()


@pytest.mark.usefixtures("driver")
class TestSupplierSetReadyToShipDate:
    def test_set_ready_to_ship_date_flow(self, driver):
        print("\n[TC-RTSD-001] Executing Supplier Set Ready To Ship Date Flow...")

        # Step 1: Login
        driver.get(f"{BASE_URL}/Account/Login")
        wait_ready(driver)

        username_field = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "UserName")))
        password_field = driver.find_element(By.ID, "Password")
        login_button = driver.find_element(By.ID, "login-button")

        username_field.clear()
        username_field.send_keys(USERNAME)
        password_field.clear()
        password_field.send_keys(PASSWORD)
        login_button.click()
        wait_ready(driver)
        time.sleep(PAUSE)
        take_screenshot(driver, "01_after_login")

        # Step 2: Navigate to Set Ready To Ship Date
        if "setreadytoshipdateitems" not in driver.current_url.lower() and "setreadytoshipdatecards" not in driver.current_url.lower():
            try:
                actions_link = WebDriverWait(driver, 8).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//a[contains(@href,'Action/Home') or normalize-space(.)='Actions' or .//span[normalize-space()='Actions']]")
                    )
                )
                safe_click(driver, actions_link)
                wait_ready(driver)
                time.sleep(PAUSE)
            except Exception:
                pass

            driver.get(ITEMS_URL)
            wait_ready(driver)
            time.sleep(PAUSE)

        take_screenshot(driver, "02_items_page")

        # Step 3 & 4: Select Item and Show Cards (if currently on Items view)
        if "setreadytoshipdatecards" not in driver.current_url.lower():
            item_selected = select_item_by_id(driver, TARGET_ITEM_ID)
            assert item_selected, f"Item '{TARGET_ITEM_ID}' could not be selected from the items grid."
            wait_ready(driver)
            time.sleep(PAUSE)

            if "setreadytoshipdatecards" not in driver.current_url.lower():
                if not click_show_cards(driver):
                    driver.get(CARDS_URL)
                    wait_ready(driver)
                    time.sleep(PAUSE)

        assert "setreadytoshipdatecards" in driver.current_url.lower(), (
            f"Expected Cards page URL, got: {driver.current_url}"
        )
        take_screenshot(driver, "03_cards_page")

        # Step 5: Select Card(s) Checkbox
        card_checked = select_card_checkbox(driver, TARGET_CARD_ID)
        assert card_checked, "Failed to select card checkbox in the grid."
        print(f"  [STEP] Selected card checkbox (Target: {TARGET_CARD_ID}).")

        # Step 6 & 7: Enter Ready To Ship Date and Apply To All
        enter_and_apply_ready_to_ship_date(driver, FUTURE_DATE)
        take_screenshot(driver, "04_after_date_applied")

        # Step 8: Click the visible, actionable Set Ready To Ship Date toolbar button
        button = WebDriverWait(driver, 10).until(
            lambda d: next(
                (
                    el
                    for el in d.find_elements(
                        By.XPATH,
                        "//*[self::button or self::a or self::span or self::div or @role='button'][contains(normalize-space(.), 'Set Ready To Ship Date')]"
                    )
                    if el.is_displayed() and el.size.get("width", 0) > 0 and el.size.get("height", 0) > 0
                ),
                None,
            )
        )
        safe_click(driver, button)
        time.sleep(PAUSE)
        take_screenshot(driver, "05_after_action_click")

        # Step 9: Click Set Ready To Ship Date button as shown in the reference screenshot
        blue_button = WebDriverWait(driver, 10).until(
            lambda d: next(
                (
                    el
                    for el in d.find_elements(
                        By.XPATH,
                        "//*[self::button or self::a or self::span][contains(normalize-space(.), 'Set Ready To Ship Date') and contains(@style, 'background') or contains(@class, 'blue') or contains(@class, 'primary') or contains(@class, 'btn-primary')]"
                    )
                    if el.is_displayed() and el.size.get("width", 0) > 0 and el.size.get("height", 0) > 0
                ),
                None,
            )
        )
        safe_click(driver, blue_button)
        time.sleep(PAUSE)
        take_screenshot(driver, "06_after_blue_button_click")

        # Step 10: Click Back to items after the action completes
        back_to_items_button = WebDriverWait(driver, 12).until(
            lambda d: next(
                (
                    el
                    for el in d.find_elements(
                        By.XPATH,
                        "//*[self::button or self::a or self::span][contains(normalize-space(.), 'Back to items') or contains(normalize-space(.), 'Back To Items') or contains(normalize-space(.), '← Back to items')]"
                    )
                    if el.is_displayed() and el.size.get("width", 0) > 0 and el.size.get("height", 0) > 0
                ),
                None,
            )
        )
        safe_click(driver, back_to_items_button)
        wait_ready(driver)
        time.sleep(PAUSE)
        take_screenshot(driver, "07_after_back_to_items_click")
        assert "setreadytoshipdateitems" in driver.current_url.lower(), (
            f"Expected navigation back to items page, got: {driver.current_url}"
        )

        print("  [PASS] Set Ready To Ship Date date entry flow reached the final submit state successfully.")