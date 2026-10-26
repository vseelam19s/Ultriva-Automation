"""Ship Cards QA flow.

This script automates the Supplier Actions -> Ship flow in the QA environment and
keeps the sequence intentionally small and explicit:
1) login
2) open Actions
3) open Ship Cards page
4) select a random card
5) pause briefly without triggering the Ship action

The comments below are meant to make each step readable without changing the
behavior of the flow when the Ship action should not be clicked.
"""

import os
import random
import time

import pytest
from selenium import webdriver
from selenium.common.exceptions import NoSuchWindowException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
CARDS_URL = f"{BASE_URL}/SupplierAction/ShipCards"
USERNAME = "supnewuser"
PASSWORD = "Ultriva!23"
PAUSE = 1.5


@pytest.fixture(scope="session")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    drv = webdriver.Chrome(options=options)
    drv.implicitly_wait(10)
    drv.set_page_load_timeout(40)
    drv.maximize_window()
    yield drv
    drv.quit()


def wait_ready(driver, timeout=30):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
    except (NoSuchWindowException, WebDriverException):
        return False
    return True


def find(driver, by, locator, timeout=15):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, locator))
    )


def clickable(driver, by, locator, timeout=15):
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, locator))
    )


def js_click(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    time.sleep(0.2)
    try:
        element.click()
    except Exception:
        driver.execute_script("arguments[0].click();", element)


def take_screenshot(driver, name):
    screenshots_dir = os.path.join(os.path.dirname(__file__), "screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(screenshots_dir, f"ship_cards_{name}_{ts}.png")
    try:
        driver.save_screenshot(path)
        print(f"  [screenshot] {path}")
        return path
    except (NoSuchWindowException, WebDriverException):
        print(f"  [info] Browser window closed before screenshot for {name}; treating as expected post-submit closure.")
        return None


def click_text(driver, labels):
    for label in labels:
        locators = [
            (
                By.XPATH,
                f"//*[self::a or self::button or self::input or self::span or self::div][normalize-space(.)='{label}' or normalize-space(@value)='{label}']",
            ),
            (
                By.XPATH,
                f"//*[self::a or self::button or self::input or self::span or self::div][contains(normalize-space(.), '{label}') or contains(normalize-space(@value), '{label}')]",
            ),
        ]
        for by, locator in locators:
            try:
                elements = driver.find_elements(by, locator)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        js_click(driver, element)
                        return True
            except Exception:
                continue
        matched = driver.execute_script(
            """
            var wanted = arguments[0].trim().toLowerCase();
            var els = document.querySelectorAll('a, button, input, span, div, td, li');
            for (var i = 0; i < els.length; i++) {
              var txt = (els[i].innerText || els[i].value || '').replace(/\\s+/g, ' ').trim().toLowerCase();
              var visible = !!(els[i].offsetParent !== null && (els[i].offsetWidth > 0 || els[i].offsetHeight > 0 || els[i].getClientRects().length > 0));
              if ((txt === wanted || txt.indexOf(wanted) !== -1) && visible && !els[i].disabled) {
                try { els[i].click(); } catch (e) { els[i].dispatchEvent(new MouseEvent('click', {bubbles: true})); }
                return true;
              }
            }
            return false;
            """,
            label,
        )
        if matched:
            return True
    return False


def handle_confirmation(driver):
    try:
        WebDriverWait(driver, 3).until(EC.alert_is_present())
        driver.switch_to.alert.accept()
        return True
    except Exception:
        pass

    for label in ["OK", "Yes", "Confirm", "Continue", "Ship", "Submit", "Save", "Done"]:
        try:
            button = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        f"//*[contains(@class,'modal') or contains(@class,'dialog') or contains(@role,'dialog') or contains(@class,'ui-dialog')]//*[self::button or self::a or self::input][normalize-space(.)='{label}' or normalize-space(@value)='{label}']",
                    )
                )
            )
            js_click(driver, button)
            return True
        except Exception:
            continue
    return False


def is_checkbox_selected(driver, checkbox):
    try:
        if checkbox.is_selected():
            return True
    except Exception:
        pass
    try:
        return bool(driver.execute_script("return arguments[0].checked;", checkbox))
    except Exception:
        return False


def select_random_card(driver):
    row_checkboxes = WebDriverWait(driver, 20).until(
        lambda d: [
            cb for cb in d.find_elements(By.CSS_SELECTOR, "tr[gid] input.GridCheckbox")
            if cb.is_displayed() and cb.is_enabled()
        ]
    )

    for cb in row_checkboxes:
        if is_checkbox_selected(driver, cb):
            js_click(driver, cb)

    chosen = random.choice(row_checkboxes)
    js_click(driver, chosen)
    time.sleep(0.5)
    assert is_checkbox_selected(driver, chosen), "The randomly chosen card could not be selected."

    card_id = chosen.get_attribute("value")
    print(f"[INFO] Randomly selected card: {card_id}")
    return card_id


def is_real_ship_action(element):
    try:
        tag = (element.tag_name or "").lower()
        text = " ".join((element.text or element.get_attribute("innerText") or "").split()).strip()
        value = (element.get_attribute("value") or "").strip()
        combined = (text or value).lower()
        ancestors = element.find_elements(
            By.XPATH,
            "./ancestor::*[contains(@class, 'menu') or contains(@class, 'nav') or contains(@class, 'dropdown') or contains(@class, 'breadcrumb') or contains(@role, 'menu')]",
        )
    except Exception:
        return False

    if not combined:
        return False
    if any(token in combined for token in ["consolidator", "consol ship", "ship date", "ship to", "ship cards"]):
        return False
    if ancestors:
        return False
    if "ship" not in combined:
        return False
    return tag in {"button", "input", "span", "a"}


def click_ship_button(driver):
    ship_ids = ["btndoActTop", "btndoActBot"]
    for ship_id in ship_ids:
        try:
            button = driver.find_element(By.ID, ship_id)
            if button.is_displayed() and button.is_enabled():
                js_click(driver, button)
                wait_ready(driver)
                time.sleep(PAUSE * 2)
                handle_confirmation(driver)
                return True
        except Exception:
            continue

    locators = [
        (By.XPATH, "//*[@id='btndoActTop' or @id='btndoActBot']"),
        (
            By.XPATH,
            "//*[self::span or self::button or self::input or self::a][normalize-space(.)='Ship' and (contains(@id, 'doAct') or contains(@id, 'btndoAct') or contains(@class, 'vd-blue-btn') or contains(@class, 'btn-toolbar')) and not(ancestor::*[contains(@class, 'breadcrumb') or contains(@role, 'menu') or contains(@class, 'dropdown') or contains(@class, 'nav')])]",
        ),
        (
            By.XPATH,
            "//*[self::span or self::button or self::input or self::a][normalize-space(.)='Ship' and (contains(@class, 'vd-blue-btn') or @id='btndoActTop' or @id='btndoActBot') and not(ancestor::*[contains(@class, 'breadcrumb') or contains(@role, 'menu') or contains(@class, 'dropdown') or contains(@class, 'nav')])]",
        ),
        (
            By.XPATH,
            "//*[self::span or self::button or self::input or self::a][contains(normalize-space(.), 'Ship') and not(contains(normalize-space(.), 'Consolidator')) and not(contains(normalize-space(.), 'Ship Date')) and not(contains(normalize-space(.), 'Ship To')) and not(ancestor::*[contains(@class, 'breadcrumb') or contains(@role, 'menu') or contains(@class, 'dropdown') or contains(@class, 'nav')])]",
        ),
    ]
    for by, locator in locators:
        try:
            buttons = driver.find_elements(by, locator)
            for button in buttons:
                if not button.is_displayed() or not button.is_enabled():
                    continue
                if not is_real_ship_action(button):
                    continue
                js_click(driver, button)
                wait_ready(driver)
                time.sleep(PAUSE * 2)
                handle_confirmation(driver)
                return True
        except Exception:
            continue

    raise AssertionError("Ship button not found on Ship Cards page.")


def test_ship_cards_flow(driver):
    # Step 1: Open the QA login page and authenticate the supplier user.
    print("\n[STEP 1] Log in to QA site with supnewuser / Ultriva!23")
    driver.get(f"{BASE_URL}/Account/Login")
    wait_ready(driver)

    username_field = find(driver, By.ID, "UserName")
    password_field = find(driver, By.ID, "Password")
    login_button = clickable(driver, By.ID, "login-button")

    # Fill in the login form and submit it.
    username_field.clear()
    username_field.send_keys(USERNAME)
    password_field.clear()
    password_field.send_keys(PASSWORD)
    js_click(driver, login_button)
    wait_ready(driver)
    time.sleep(PAUSE)
    take_screenshot(driver, "01_after_login")

    assert "home" in driver.current_url.lower() or BASE_URL.lower() in driver.current_url.lower(), (
        f"Login may have failed. URL: {driver.current_url}"
    )

    # Step 2: Open the Actions menu from the supplier landing page.
    print("\n[STEP 2] Click Actions")
    actions_menu = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'Actions')] | //span[contains(., 'Actions')]"))
    )
    js_click(driver, actions_menu)
    time.sleep(PAUSE)

    # Step 3: Select the Ship option from Supplier Actions.
    print("\n[STEP 3] From Supplier Actions, click Ship")
    ship_menu_item = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(@href, 'SupplierAction/ShipCards') or normalize-space(.)='Ship']")
        )
    )
    js_click(driver, ship_menu_item)
    wait_ready(driver)
    time.sleep(PAUSE * 2)
    assert "shipcards" in driver.current_url.lower(), (
        f"Expected Ship Cards page, but current URL is {driver.current_url}"
    )
    take_screenshot(driver, "02_cards_page")

    # Step 4: Select a random card without triggering the Ship action.
    print("\n[STEP 4] From Ship cards list, select a random card")
    select_random_card(driver)
    take_screenshot(driver, "03_card_selected")
    print("\n[WAIT] Pausing briefly after card selection without clicking Ship.")
    time.sleep(PAUSE * 4)

    # Step 5: Intentionally stop after selection; do not click Ship.
    print("\n[STEP 5] Avoid Ship action click")
    take_screenshot(driver, "04_ship_card_selected_no_click")

    print("\n[PASS] Ship Cards flow completed after selecting the card without clicking Ship.")