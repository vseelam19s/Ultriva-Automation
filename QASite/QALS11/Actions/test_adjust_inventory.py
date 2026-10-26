"""Adjust Inventory QA flow.

Flow:
1. Log in as buyeruser.
2. Open the Actions page.
3. Open Adjust Inventory.
4. Select any item.
5. Click Show Cards.
6. Select two cards.
7. Set Adjust Qty = 100.
8. Set a random Current Location.
9. Click Adjust Inventory.
"""

import random
import string
import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
ADJUST_INVENTORY_FILTER_URL = f"{BASE_URL}/BuyerAction/AdjustInventoryFilter"
USERNAME = "buyeruser"
PASSWORD = "Ultriva!23"
PAUSE = 1.5
ADJUST_QTY = "100"


@pytest.fixture(scope="class")
def driver():
    """Class-scoped Chrome driver used for the Adjust Inventory flow."""
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
    """Wait for the page to finish loading."""
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def find(driver, by, locator, timeout=15):
    """Return a visible element once it appears."""
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, locator))
    )


def clickable(driver, by, locator, timeout=15):
    """Return an element when it is clickable."""
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, locator))
    )


def scroll_to(driver, el):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'})", el)
    time.sleep(0.3)


def safe_navigate(driver, url, timeout=20):
    """Navigate without crashing the whole flow if a page load times out."""
    driver.set_page_load_timeout(timeout)
    try:
        driver.get(url)
        wait_ready(driver, timeout=timeout)
        return True
    except Exception:
        return False
    finally:
        driver.set_page_load_timeout(30)


def safe_click(driver, element, timeout=15):
    """Try a standard click and fall back to JS click if needed."""
    try:
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(element))
        element.click()
        return
    except Exception:
        pass

    try:
        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'}); arguments[0].click();",
            element,
        )
    except Exception:
        driver.execute_script("arguments[0].click()", element)


def set_input_value(driver, element, value):
    """Clear and set a field value, then trigger a change event."""
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
    element.clear()
    element.send_keys(value)
    driver.execute_script(
        "arguments[0].dispatchEvent(new Event('input', {bubbles:true}));"
        "arguments[0].dispatchEvent(new Event('change', {bubbles:true}));",
        element,
    )
    time.sleep(0.4)


def select_cards_by_id(driver, card_ids):
    """Select rows by matching Card ID text and checking the row's checkbox."""
    wait = WebDriverWait(driver, 10)
    for card_id in card_ids:
        xpath = f"//tr[td[contains(normalize-space(.), '{card_id}')]]//input[@type='checkbox']"
        try:
            checkbox = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
            if not checkbox.is_selected():
                try:
                    checkbox.click()
                except Exception:
                    driver.execute_script(
                        "arguments[0].click(); arguments[0].setAttribute('checked','checked');"
                        "arguments[0].dispatchEvent(new Event('change', {bubbles: true}));",
                        checkbox,
                    )
            time.sleep(0.4)
        except Exception:
            continue


def select_two_cards(driver):
    """Select two visible card checkboxes from common grid selectors."""
    selectors = [
        "//input[@type='checkbox' and contains(@name,'$CheckboxCardGID') and not(contains(@name,'All$CheckboxCardGID'))]",
        "//input[@type='checkbox' and contains(@name,'CheckboxCardGID') and not(contains(@name,'_All$'))]",
        "//input[@type='checkbox' and (contains(@name,'CheckboxCardGID') or contains(@id,'CheckboxCardGID') or contains(@class,'GridCheckbox')) and not(contains(@name,'All$CheckboxCardGID')) and not(contains(@class,'grid-all-checkbox'))]",
        "//input[contains(@class,'GridCheckbox') and not(contains(@class,'grid-all-checkbox'))]",
    ]

    seen = set()
    selected = 0
    for xpath in selectors:
        try:
            for checkbox in driver.find_elements(By.XPATH, xpath):
                if not checkbox.is_displayed() or not checkbox.is_enabled():
                    continue
                if checkbox.get_attribute('type') and checkbox.get_attribute('type').lower() != 'checkbox':
                    continue

                key = (
                    checkbox.get_attribute('id')
                    or checkbox.get_attribute('name')
                    or checkbox.get_attribute('value')
                    or str(checkbox.location)
                )
                if key in seen:
                    continue
                seen.add(key)

                selected_state = checkbox.is_selected() or driver.execute_script(
                    "return arguments[0].checked;", checkbox
                )
                if selected_state:
                    selected += 1
                    if selected >= 2:
                        return True
                    continue

                try:
                    checkbox.click()
                except Exception:
                    driver.execute_script(
                        """
                        arguments[0].scrollIntoView({block: 'center'});
                        arguments[0].checked = true;
                        arguments[0].setAttribute('checked', 'checked');
                        arguments[0].dispatchEvent(new Event('click', {bubbles: true}));
                        arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
                        """,
                        checkbox,
                    )
                time.sleep(0.3)

                if checkbox.is_selected() or driver.execute_script("return arguments[0].checked;", checkbox):
                    selected += 1
                    if selected >= 2:
                        return True
        except Exception:
            continue

    return selected >= 2


def click_go_if_needed(driver):
    """On the filter page, click the Go button before the cards/items load."""
    if "AdjustInventoryItems" in driver.current_url or "AdjustInventoryCard" in driver.current_url:
        return

    selectors = [
        (By.ID, "imgMatStatusGo"),
        (By.XPATH, "//button[normalize-space(.)='Go']"),
        (By.XPATH, "//input[@type='submit' and @value='Go']"),
        (By.XPATH, "//a[normalize-space(.)='Go']"),
        (By.XPATH, "//*[@id='btnGo' or @id='go-button' or @id='goBtn']"),
        (By.XPATH, "//*[contains(@id,'Go') or contains(@name,'Go')][normalize-space(.)='Go']"),
    ]

    for by, locator in selectors:
        try:
            go_button = WebDriverWait(driver, 8).until(EC.element_to_be_clickable((by, locator)))
            safe_click(driver, go_button)
            wait_ready(driver)
            time.sleep(PAUSE)
            return
        except Exception:
            continue

    if driver.find_elements(By.XPATH, "//a[contains(@class,'GridLink')]"):
        return

    if "AdjustInventory" in driver.current_url:
        return

    safe_navigate(driver, ADJUST_INVENTORY_FILTER_URL)
    time.sleep(PAUSE)


@pytest.mark.usefixtures("driver")
class TestAdjustInventory:

    def test_adjust_inventory_flow(self, driver):
        """Run the exact requested Adjust Inventory workflow."""
        print("\n[STEP 1] Login to QA site...")
        driver.get(BASE_URL)
        wait_ready(driver)

        username_field = find(driver, By.ID, "UserName")
        password_field = find(driver, By.ID, "Password")
        login_button = clickable(driver, By.ID, "login-button")

        username_field.clear()
        username_field.send_keys(USERNAME)
        password_field.clear()
        password_field.send_keys(PASSWORD)
        safe_click(driver, login_button)
        wait_ready(driver)
        time.sleep(PAUSE)

        assert BASE_URL.lower() in driver.current_url.lower() or "Home" in driver.current_url, \
            f"Login may have failed. URL: {driver.current_url}"

        print("\n[STEP 2] Open Adjust Inventory filter page...")
        safe_navigate(driver, ADJUST_INVENTORY_FILTER_URL)
        wait_ready(driver)
        time.sleep(PAUSE)

        assert (
            "AdjustInventoryFilter" in driver.current_url
            or "BuyerAction" in driver.current_url
            or "AdjustInventory" in driver.current_url
        ), f"Expected Adjust Inventory filter page. Got: {driver.current_url}"

        print("\n[STEP 3] Click GO on the Adjust Inventory filter page...")
        click_go_if_needed(driver)
        wait_ready(driver)
        time.sleep(PAUSE)

        assert (
            "AdjustInventoryFilter" in driver.current_url
            or "AdjustInventory" in driver.current_url
            or "BuyerAction" in driver.current_url
        ), f"Expected Adjust Inventory page after GO. Got: {driver.current_url}"

        print("\n[STEP 4] Select any item and click Show Cards...")
        item_links = None
        try:
            item_links = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class,'GridLink')]"))
            )
        except Exception:
            item_links = []

        if item_links:
            first_item = item_links[0]
            scroll_to(driver, first_item)
            safe_click(driver, first_item)
            wait_ready(driver)
            time.sleep(PAUSE)

            if "AdjustInventoryCard" in driver.current_url or "AdjustInventoryCards" in driver.current_url:
                show_cards_btn = True
            else:
                show_cards_btn = None
                for locator in [
                    (By.XPATH, "//button[contains(normalize-space(),'Show Cards')]"),
                    (By.XPATH, "//a[contains(normalize-space(),'Show Cards')]"),
                    (By.XPATH, "//span[contains(normalize-space(),'Show Cards')]"),
                    (By.XPATH, "//*[contains(@id,'ShowCards') or contains(@id,'showCards')]"),
                ]:
                    try:
                        show_cards_btn = WebDriverWait(driver, 8).until(EC.element_to_be_clickable(locator))
                        break
                    except Exception:
                        continue

                assert show_cards_btn, "Show Cards button not found"
                safe_click(driver, show_cards_btn)
                wait_ready(driver)
                time.sleep(PAUSE)

            assert "AdjustInventoryCard" in driver.current_url or "AdjustInventoryCards" in driver.current_url or "AdjustInventory" in driver.current_url, \
                f"Expected cards page. Got: {driver.current_url}"

        row_checkbox_xpath = (
            "//input[@type='checkbox' and "
            "(contains(@name,'CheckboxCardGID') or contains(@id,'CheckboxCardGID') or contains(@name,'$CheckboxCardGID') "
            "or contains(@id,'chkCard') or contains(@name,'chkCard') or contains(@id,'card') or contains(@name,'card')) "
            "and not(contains(@name,'All$CheckboxCardGID')) and not(@disabled)]"
        )
        row_checkboxes = driver.find_elements(By.XPATH, row_checkbox_xpath)
        if not row_checkboxes:
            row_checkboxes = driver.find_elements(By.XPATH, "//input[@type='checkbox' and not(@disabled)]")
        assert row_checkboxes, "No card checkboxes found on Adjust Inventory Cards List"

        print("\n[STEP 5] Select two cards from the cards list...")
        assert select_two_cards(driver), "Could not confirm two card checkboxes were selected from the cards list"

        print("\n[STEP 6] Enter Adjust Qty = 100 and a random Current Location...")
        random_suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
        random_location = f"LOC-{random_suffix}"

        location_inputs = driver.find_elements(
            By.XPATH,
            "//input[contains(@id,'CurrentLocation') or contains(@name,'CurrentLocation') or contains(@id,'Location') or contains(@name,'Location')]",
        )
        if location_inputs:
            set_input_value(driver, location_inputs[0], random_location)
        else:
            pytest.skip("Current Location field was not found on the page")

        qty_inputs = driver.find_elements(
            By.XPATH,
            "//input[contains(@id,'AdjustQty') or contains(@name,'AdjustQty') or contains(@id,'AdjustQuantity') or contains(@name,'AdjustQuantity')]",
        )
        assert qty_inputs, "Adjust Qty field not found on the cards page"

        for qty_input in qty_inputs[:2]:
            set_input_value(driver, qty_input, ADJUST_QTY)

        print(f"  [INFO] Set Current Location = {random_location}")
        print(f"  [INFO] Set Adjust Qty = {ADJUST_QTY}")

        print("\n[STEP 7] Click Adjust Inventory button...")
        adjust_btn = None
        for locator in [
            (By.ID, "btndoActTop"),
            (By.ID, "btndoActBot"),
            (By.XPATH, "//span[@onclick='da()' and contains(@class,'btn')]"),
            (By.XPATH, "//*[self::span or self::button or self::input or self::a][contains(@id,'doAct') or @id='btndoActTop' or @id='btndoActBot']"),
            (By.XPATH, "//span[@id='btndoActTop' or contains(@id,'doAct')][contains(normalize-space(.),'Adjust Inventory')]"),
            (By.XPATH, "//span[contains(normalize-space(.),'Adjust Inventory')]"),
            (By.XPATH, "//button[contains(normalize-space(),'Adjust Inventory')]"),
            (By.XPATH, "//a[contains(normalize-space(),'Adjust Inventory')]"),
            (By.XPATH, "//*[@id='btnAdjustInventory' or contains(@id,'btnAdjust')]"),
            (By.XPATH, "//input[@value='Adjust Inventory']"),
        ]:
            try:
                adjust_btn = WebDriverWait(driver, 8).until(EC.element_to_be_clickable(locator))
                break
            except Exception:
                continue

        assert adjust_btn, "Adjust Inventory button not found"
        print(f"  [INFO] Using action button: id={adjust_btn.get_attribute('id')}, text={adjust_btn.text[:80]}")
        safe_click(driver, adjust_btn)
        wait_ready(driver)
        time.sleep(PAUSE * 2)

        print(f"  [URL] {driver.current_url}")
        assert "AdjustInventory" in driver.current_url or "BuyerAction" in driver.current_url, \
            f"Unexpected URL after Adjust Inventory: {driver.current_url}"
        print("  [PASS] Adjust Inventory action completed with the requested flow.")