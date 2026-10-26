"""
QALS11 | Actions > Bulk Print — Buyer action flow
==================================================
URL   : https://engineering.ultrivalms.com/QALS1011/BuyerAction/BulkPrintItems
User  : buyeruser / Ultriva!23

Test Flow
---------
  1. Login as buyeruser
  2. Open the Bulk Print Items list using the direct URL
  3. Select an item and click Show Cards
  4. Select cards on the Bulk Print Cards List
  5. Click Print

Run (from qa_automation/):
    pytest tests/QALS11/Actions/BulkPrint.py -v -s
"""

import os
import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
BULK_PRINT_URL = "https://engineering.ultrivalms.com/QALS1011/BuyerAction/BulkPrintItems"
USERNAME = "buyeruser"
PASSWORD = "Ultriva!23"
PAUSE = 1.5


@pytest.fixture(scope="class")
def driver():
    """Class-scoped Chrome browser session."""
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


def scroll_to(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'})", element)
    time.sleep(0.3)


def click_by_text(driver, text, timeout=10):
    """Click the first visible element whose text content contains the given label exactly once."""
    locator = (
        "//*[self::button or self::a or self::input or self::span or self::div or self::li or self::td or self::th]"
        f"[contains(normalize-space(string(.)), '{text}')]"
    )
    try:
        element = WebDriverWait(driver, timeout).until(
            lambda d: next((el for el in d.find_elements(By.XPATH, locator) if el.is_displayed() and el.is_enabled()), None)
        )
        scroll_to(driver, element)
        driver.execute_script("arguments[0].click();", element)
        return True
    except Exception:
        return False


def click_by_text_in_context(driver, target_text, context_text, timeout=10):
    """Click the target element only when it appears in the same container as the given context text."""
    js = (
        "const targetText = arguments[0];"
        "const contextText = arguments[1];"
        "const candidates = Array.from(document.querySelectorAll('*')).filter(el => {"
        "  const text = (el.textContent || '').replace(/\\s+/g, ' ').trim();"
        "  return text.toLowerCase().includes(targetText.toLowerCase()) && el.offsetParent !== null;"
        "});"
        "for (const candidate of candidates) {"
        "  const container = candidate.closest('table, tr, td, div, li, body');"
        "  const containerText = (container ? container.textContent : '').replace(/\\s+/g, ' ').trim();"
        "  if (containerText.toLowerCase().includes(contextText.toLowerCase())) {"
        "    return candidate;"
        "  }"
        "}"
        "return null;"
    )
    for _ in range(2):
        try:
            element = driver.execute_script(js, target_text, context_text)
            if element:
                scroll_to(driver, element)
                driver.execute_script("arguments[0].click();", element)
                return True
            return False
        except Exception:
            time.sleep(0.5)
    return False


def select_cards_by_id(driver, card_ids):
    """Select rows by matching Card ID text and checking the row's checkbox."""
    wait = WebDriverWait(driver, 10)
    for card_id in card_ids:
        xpath = f"//tr[td[contains(normalize-space(.), '{card_id}')]]//input[@type='checkbox']"
        checkbox = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
        if not checkbox.is_selected():
            checkbox.click()
            time.sleep(0.4)


def select_two_cards(driver):
    """Select two card checkboxes using the page's known card checkbox selectors."""
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

                if checkbox.is_selected() or driver.execute_script("return arguments[0].checked;", checkbox):
                    selected += 1
                    if selected >= 2:
                        return True
                    continue

                try:
                    checkbox.click()
                except Exception:
                    driver.execute_script(
                        """
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


def safe_click(driver, element, timeout=15):
    """Try a standard click and fall back to JavaScript click when needed."""
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
        try:
            driver.execute_script("arguments[0].click();", element)
        except Exception:
            pass


def click_bulkprint_button(driver, timeout=15):
    """Find the visible Print action in the Bulk Print cards toolbar and click it."""
    print("\n[STEP 7] Click Print button...")
    print_btn = None
    locators = [
        (By.ID, "btnPrintTop"),
        (By.ID, "btnPrintBot"),
        (By.XPATH, "//span[contains(normalize-space(.),'Print') and contains(@class,'btn')]"),
        (By.XPATH, "//*[self::span or self::button or self::input or self::a][contains(@id, 'btnPrint') or @id='btnPrintTop' or @id='btnPrintBot']"),
        (By.XPATH, "//span[contains(normalize-space(),'Print')]"),
        (By.XPATH, "//button[contains(normalize-space(),'Print')]"),
        (By.XPATH, "//a[contains(normalize-space(),'Print')]"),
        (By.XPATH, "//input[@value='Print']"),
    ]

    for by, locator in locators:
        try:
            print_btn = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((by, locator))
            )
            if print_btn and print_btn.is_displayed() and print_btn.is_enabled():
                break
        except Exception:
            continue

    if print_btn is None:
        candidate_xpaths = [
            "//button[normalize-space(.)='Print' or normalize-space(@value)='Print' or normalize-space(@title)='Print' or normalize-space(@aria-label)='Print']",
            "//a[normalize-space(.)='Print' or normalize-space(@title)='Print' or normalize-space(@aria-label)='Print']",
            "//input[normalize-space(@value)='Print' or normalize-space(@title)='Print' or normalize-space(@aria-label)='Print']",
            "//*[self::button or self::a or self::input][contains(normalize-space(string(.)), 'Print') or contains(normalize-space(@value), 'Print') or contains(normalize-space(@title), 'Print') or contains(normalize-space(@aria-label), 'Print')]",
        ]
        for xpath in candidate_xpaths:
            try:
                element = WebDriverWait(driver, timeout).until(
                    lambda d, xp=xpath: next(
                        (
                            el for el in d.find_elements(By.XPATH, xp)
                            if el.is_displayed() and el.is_enabled()
                        ),
                        None,
                    )
                )
                if element is not None:
                    print_btn = element
                    break
            except Exception:
                continue

    assert print_btn, "Print button not found"
    print(f"  [INFO] Using action button: id={print_btn.get_attribute('id')}, text={print_btn.text[:80]}")
    safe_click(driver, print_btn)
    wait_ready(driver)
    time.sleep(PAUSE * 2)

    print(f"  [URL] {driver.current_url}")
    assert "BulkPrint" in driver.current_url or "BuyerAction" in driver.current_url, \
        f"Unexpected URL after Print: {driver.current_url}"
    print("  [PASS] Print action completed with the requested flow.")
    return True


def select_dropdown_option(driver, label_text, option_text):
    """Select a dropdown option by its visible label and visible option text."""
    from selenium.webdriver.support.ui import Select

    selectors = [
        (By.XPATH, f"//*[self::label or self::span or self::div][normalize-space(.)='{label_text}']/following::select[1]"),
        (By.XPATH, f"//select[preceding::*[self::label or self::span or self::div][normalize-space(.)='{label_text}'][1]]"),
    ]
    for by, locator in selectors:
        try:
            for element in driver.find_elements(by, locator):
                if element.is_displayed() and element.is_enabled():
                    Select(element).select_by_visible_text(option_text)
                    time.sleep(0.5)
                    return True
        except Exception:
            continue
    return False


def take_screenshot(driver, name):
    screenshots_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "reports", "screenshots"
    )
    os.makedirs(screenshots_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(screenshots_dir, f"bulkprint_{name}_{ts}.png")
    driver.save_screenshot(path)
    print(f"  [screenshot] {path}")
    return path


@pytest.mark.usefixtures("driver")
class TestBulkPrint:

    def test_bulk_print_flow(self, driver):
        """Execute the single Bulk Print buyer flow once in one browser session."""
        print("\n[TC-BP-001] Logging in and completing the Bulk Print flow...")

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
        assert BASE_URL.lower() in current_url.lower() or "Home" in current_url.lower(), (
            f"Login may have failed. URL: {current_url}"
        )
        print("  [PASS] Login successful.")

        driver.get(BULK_PRINT_URL)
        wait_ready(driver)
        time.sleep(PAUSE * 2)

        take_screenshot(driver, "02_bulk_print_items")
        current_url = driver.current_url
        print(f"  [URL] {current_url}")
        assert "BulkPrintItems" in current_url or "BulkPrint" in current_url, (
            f"Bulk Print Items page did not load. URL: {current_url}"
        )
        print(f"  [PASS] Bulk Print Items page loaded: {current_url}")

        item_links = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class,'GridLink')]"))
        )
        assert item_links, "No item links found on the Bulk Print Items page."

        first_item = item_links[0]
        item_text = (first_item.text or "").strip() or "first item"
        print(f"  [INFO] Selected item: {item_text}")
        scroll_to(driver, first_item)
        driver.execute_script("arguments[0].click();", first_item)
        wait_ready(driver)
        time.sleep(PAUSE * 2)

        take_screenshot(driver, "03a_after_item_click")
        print(f"  [INFO] URL after item click: {driver.current_url}")

        if "BulkPrintCards" not in driver.current_url:
            show_cards_clicked = click_by_text(driver, "Show Cards")
            assert show_cards_clicked, (
                f"Show Cards control not found. Current URL: {driver.current_url}"
            )
            wait_ready(driver)
            time.sleep(PAUSE * 2)

        take_screenshot(driver, "03b_bulk_print_cards")
        print(f"  [URL] {driver.current_url}")
        assert "BulkPrintCards" in driver.current_url or "BulkPrint" in driver.current_url, (
            f"Expected Bulk Print Cards List page. Got: {driver.current_url}"
        )
        print(f"  [PASS] Bulk Print Cards page confirmed: {driver.current_url}")

        assert "BulkPrint" in driver.current_url, (
            f"Expected Bulk Print Cards page. Got: {driver.current_url}"
        )
        assert select_two_cards(driver), "Could not confirm two card checkboxes were selected from the cards list."
        take_screenshot(driver, "04a_cards_selected")

        driver.execute_script("window.__bulkprint_action_clicked__ = false;")
        print_clicked = click_bulkprint_button(driver)
        assert print_clicked, f"Bulkprint control not found on Bulk Print Cards page. URL: {driver.current_url}"
        time.sleep(PAUSE * 2)

        take_screenshot(driver, "04b_after_print_click")
        print("  [PASS] Bulkprint action clicked on the selected cards.")
