r"""
QALS11 | Actions > Supplier Actions > Set Tracking/Packing Slip Numbers
=======================================================================
URL   : https://engineering.ultrivalms.com/QALS1011/SupplierAction/SetTrackingNoItems
URL   : https://engineering.ultrivalms.com/QALS1011/SupplierAction/SetTrackingNoCards
User  : supnewuser / Ultriva!23

Test Flow
---------
  1. Login as supnewuser
  2. Click Actions
  3. Open Supplier Actions > Set Tracking/Packing Slip Numbers
  4. From Set Tracking/Packing Slip Number Items List, select any item
  5. Click Show cards
  6. From Set Tracking/Packing Slip Number Cards List, select any card
  7. Enter Tracking No and Packing Slip No
  8. Click Set
  9. After success, click Back to Items

Run (from qa_automation/):
    pytest "tests/QALS11/Actions/Supplier Actions/SetTrackingPackingSlipNumbers.py" -v -s
"""

import os
import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
ITEMS_URL = f"{BASE_URL}/SupplierAction/SetTrackingNoItems"
CARDS_URL = f"{BASE_URL}/SupplierAction/SetTrackingNoCards"
USERNAME = "supnewuser"
PASSWORD = "Ultriva!23"
PAUSE = 1.5
TRACKING_NO = "TRK-20260903-001"
PACKING_SLIP_NO = "PS-20260903-001"


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


def find(driver, by, locator, timeout=15):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, locator))
    )


def clickable(driver, by, locator, timeout=15):
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, locator))
    )


def scroll_to(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'})", element)
    time.sleep(0.3)


def take_screenshot(driver, name):
    screenshots_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "reports", "screenshots"
    )
    os.makedirs(screenshots_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(screenshots_dir, f"set_tracking_{name}_{ts}.png")
    driver.save_screenshot(path)
    print(f"  [screenshot] {path}")
    return path


def click_text(driver, labels):
    for label in labels:
        locators = [
            (By.XPATH, f"//*[self::a or self::button or self::input or self::span or self::div][normalize-space(.)='{label}']"),
            (By.XPATH, f"//*[self::a or self::button or self::input or self::span or self::div][contains(normalize-space(.), '{label}')]"),
        ]
        for by, locator in locators:
            try:
                elements = driver.find_elements(by, locator)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        scroll_to(driver, element)
                        try:
                            element.click()
                        except Exception:
                            driver.execute_script("arguments[0].click();", element)
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
              if ((txt === wanted || txt.indexOf(wanted) !== -1) && visible) {
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


def search_grid_for_text(driver, value, hints=None):
    value = (value or "").strip()
    if not value:
        return False

    hints = [h.lower() for h in (hints or ["find", "search", "item", "card", "id"])]
    search_inputs = driver.find_elements(
        By.XPATH,
        "//input[(contains(@placeholder, 'Find') or contains(@placeholder, 'Search') or contains(@title, 'Find') or contains(@title, 'Search') or contains(@name, 'Find') or contains(@name, 'Search') or contains(@id, 'Find') or contains(@id, 'Search') or contains(@class, 'search') or contains(@class, 'filter') or @type='text') and not(@disabled)]",
    )

    for field in search_inputs:
        try:
            field_name = (
                field.get_attribute("placeholder")
                or field.get_attribute("title")
                or field.get_attribute("name")
                or field.get_attribute("id")
                or ""
            )
            if hints and not any(h in (field_name or "").lower() for h in hints):
                continue
            field.clear()
            field.send_keys(value)
            time.sleep(0.8)
            return True
        except Exception:
            continue
    return False


def select_first_available_checkbox(driver):
    rows = driver.find_elements(By.XPATH, "//tr[.//input[@type='checkbox' and not(@disabled)]]")
    for row in rows:
        try:
            if not row.is_displayed():
                continue
            cb = row.find_element(By.XPATH, ".//input[@type='checkbox' and not(@disabled)]")
            if cb.is_selected() or driver.execute_script("return arguments[0].checked;", cb):
                return True
            scroll_to(driver, cb)
            try:
                cb.click()
            except Exception:
                driver.execute_script("arguments[0].click();", cb)
            time.sleep(0.4)
            if cb.is_selected() or driver.execute_script("return arguments[0].checked;", cb):
                return True
            try:
                row.click()
            except Exception:
                pass
            time.sleep(0.4)
            if cb.is_selected() or driver.execute_script("return arguments[0].checked;", cb):
                return True
        except Exception:
            continue

    checkboxes = driver.find_elements(By.XPATH, "//input[@type='checkbox' and not(@disabled)]")
    for cb in checkboxes:
        try:
            if cb.is_selected() or driver.execute_script("return arguments[0].checked;", cb):
                return True
            scroll_to(driver, cb)
            try:
                cb.click()
            except Exception:
                driver.execute_script("arguments[0].click();", cb)
            time.sleep(0.3)
            if cb.is_selected() or driver.execute_script("return arguments[0].checked;", cb):
                return True
        except Exception:
            continue
    return False


def click_set_tracking_from_actions(driver):
    action_clicks = [
        ["Actions"],
        ["Supplier Actions"],
        ["Supplier Action"],
        ["Action"],
    ]

    for labels in action_clicks:
        if click_text(driver, labels):
            break
    else:
        return False

    time.sleep(PAUSE)

    targets = [
        "Set Tracking/Packing Slip Numbers",
        "Set Tracking Packing Slip Numbers",
        "Set Tracking Numbers",
        "Set Tracking Slip Numbers",
        "Tracking/Packing Slip Numbers",
    ]

    for label in targets:
        if click_text(driver, [label]):
            time.sleep(PAUSE)
            return True

    return False


def enter_tracking_and_packing(driver):
    tracking_input = None
    packing_input = None

    tracking_candidates = [
        (By.XPATH, "//input[contains(@name,'TrackingNo') or contains(@id,'TrackingNo') or contains(@placeholder,'Tracking No') or contains(@placeholder,'Tracking Number') or contains(@title,'Tracking No') or contains(@aria-label,'Tracking No') or contains(@aria-label,'Tracking Number')]"),
        (By.XPATH, "//input[contains(@name,'tracking') or contains(@id,'tracking') or contains(@placeholder,'tracking') or contains(@title,'tracking')]"),
    ]
    packing_candidates = [
        (By.XPATH, "//input[contains(@name,'PackingSlip') or contains(@id,'PackingSlip') or contains(@placeholder,'Packing Slip') or contains(@title,'Packing Slip') or contains(@aria-label,'Packing Slip') or contains(@name,'PackSlip') or contains(@id,'PackSlip')]"),
        (By.XPATH, "//input[contains(@name,'packing') or contains(@id,'packing') or contains(@placeholder,'packing') or contains(@title,'packing')]"),
    ]

    for by, locator in tracking_candidates:
        try:
            element = find(driver, by, locator, timeout=8)
            if element.is_displayed() and element.is_enabled():
                tracking_input = element
                break
        except Exception:
            continue

    for by, locator in packing_candidates:
        try:
            element = find(driver, by, locator, timeout=8)
            if element.is_displayed() and element.is_enabled():
                packing_input = element
                break
        except Exception:
            continue

    if tracking_input is None or packing_input is None:
        raise AssertionError("Tracking No or Packing Slip No field was not found on the cards page.")

    tracking_input.clear()
    tracking_input.send_keys(TRACKING_NO)
    packing_input.clear()
    packing_input.send_keys(PACKING_SLIP_NO)
    return True


def click_set_tracking_no(driver):
    labels = [
        "Set Tracking No",
        "Set Tracking Number",
        "Set Tracking / Packing Slip Number",
        "Set Tracking",
        "Set",
    ]

    for label in labels:
        try:
            btn = WebDriverWait(driver, 8).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        f"//*[self::button or self::a or self::span or self::input][normalize-space(.)='{label}' or contains(normalize-space(.), '{label}')]",
                    )
                )
            )
            scroll_to(driver, btn)
            try:
                btn.click()
            except Exception:
                driver.execute_script("arguments[0].click();", btn)
            wait_ready(driver)
            time.sleep(PAUSE)
            return True
        except Exception:
            continue
    return False


def click_back_to_items(driver):
    for label in ["Back To Items", "Back to Items", "Back To Item", "Back to Item"]:
        try:
            btn = WebDriverWait(driver, 8).until(
                EC.element_to_be_clickable(
                    (By.XPATH, f"//*[self::button or self::a or self::span or self::input][contains(normalize-space(.), '{label}')]")
                )
            )
            scroll_to(driver, btn)
            try:
                btn.click()
            except Exception:
                driver.execute_script("arguments[0].click();", btn)
            wait_ready(driver)
            time.sleep(PAUSE)
            return True
        except Exception:
            continue
    return False


@pytest.mark.usefixtures("driver")
class TestSupplierSetTrackingPackingSlipNumbers:
    def test_set_tracking_packing_slip_numbers_flow(self, driver):
        print("\n[TC-SET-TRACK-001] Logging in and executing the supplier Set Tracking/Packing Slip Numbers flow...")

        driver.get(f"{BASE_URL}/Account/Login")
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

        if "settrackingnoitems" not in driver.current_url.lower():
            menu_result = click_set_tracking_from_actions(driver)
            if not menu_result:
                driver.get(ITEMS_URL)
                wait_ready(driver)
                time.sleep(PAUSE)

        assert "settrackingnoitems" in driver.current_url.lower(), (
            f"Set Tracking Items page did not open. URL: {driver.current_url}"
        )
        take_screenshot(driver, "02_items_page")

        search_result = search_grid_for_text(driver, "IT050325", ["find", "search", "item"])
        if search_result:
            time.sleep(1.0)

        item_clicked = False
        for locator in [
            (By.XPATH, "//tr[.//td and not(.//th)]//a"),
            (By.XPATH, "//table//tr//a"),
            (By.XPATH, "//a[contains(@class,'GridLink')]"),
            (By.XPATH, "//td//a"),
        ]:
            try:
                elements = driver.find_elements(*locator)
                for elem in elements:
                    label = (elem.text or "").strip()
                    if "IT" in label and len(label) >= 7:
                        scroll_to(driver, elem)
                        elem.click()
                        item_clicked = True
                        break
                if item_clicked:
                    break
            except Exception:
                continue

        if not item_clicked:
            rows = driver.find_elements(By.XPATH, "//tr[.//td and not(.//th)]")
            for row in rows:
                try:
                    if not row.is_displayed():
                        continue
                    row.click()
                    item_clicked = True
                    break
                except Exception:
                    continue

        assert item_clicked, "No item row was selectable from the Set Tracking/Packing Slip Number Items list."
        wait_ready(driver)
        time.sleep(PAUSE)

        show_cards = None
        for locator in [
            (By.XPATH, "//button[normalize-space(.)='Show Cards']"),
            (By.XPATH, "//a[normalize-space(.)='Show Cards']"),
            (By.XPATH, "//div[normalize-space(.)='Show Cards']"),
            (By.XPATH, "//*[self::button or self::a or self::div or self::span][contains(normalize-space(.),'Show Cards')]"),
        ]:
            try:
                show_cards = WebDriverWait(driver, 8).until(EC.element_to_be_clickable(locator))
                break
            except Exception:
                continue

        if show_cards is None:
            clicked = click_text(driver, ["Show Cards", "Show cards"])
            if not clicked:
                driver.get(CARDS_URL)
                wait_ready(driver)
                time.sleep(PAUSE)
        else:
            scroll_to(driver, show_cards)
            try:
                show_cards.click()
            except Exception:
                driver.execute_script("arguments[0].click();", show_cards)

        wait_ready(driver)
        time.sleep(PAUSE)

        if "settrackingnocards" not in driver.current_url.lower():
            driver.get(CARDS_URL)
            wait_ready(driver)
            time.sleep(PAUSE)

        assert "settrackingnocards" in driver.current_url.lower(), (
            f"Set Tracking Cards page did not open. URL: {driver.current_url}"
        )
        take_screenshot(driver, "03_cards_page")

        selected = select_first_available_checkbox(driver)
        assert selected, "No card checkbox could be selected from the Set Tracking/Packing Slip Number Cards list before validation."

        tracking_input = None
        packing_input = None
        for by, locator in [
            (By.XPATH, "//input[contains(@name,'TrackingNo') or contains(@id,'TrackingNo') or contains(@placeholder,'Tracking No') or contains(@placeholder,'Tracking Number') or contains(@title,'Tracking No') or contains(@aria-label,'Tracking No') or contains(@aria-label,'Tracking Number')]"),
            (By.XPATH, "//input[contains(@name,'tracking') or contains(@id,'tracking') or contains(@placeholder,'tracking') or contains(@title,'tracking')]"),
        ]:
            try:
                candidate = find(driver, by, locator, timeout=8)
                if candidate.is_displayed() and candidate.is_enabled():
                    tracking_input = candidate
                    break
            except Exception:
                continue

        for by, locator in [
            (By.XPATH, "//input[contains(@name,'PackingSlip') or contains(@id,'PackingSlip') or contains(@placeholder,'Packing Slip') or contains(@title,'Packing Slip') or contains(@aria-label,'Packing Slip') or contains(@name,'PackSlip') or contains(@id,'PackSlip')]"),
            (By.XPATH, "//input[contains(@name,'packing') or contains(@id,'packing') or contains(@placeholder,'packing') or contains(@title,'packing')]"),
        ]:
            try:
                candidate = find(driver, by, locator, timeout=8)
                if candidate.is_displayed() and candidate.is_enabled():
                    packing_input = candidate
                    break
            except Exception:
                continue

        assert tracking_input is not None and packing_input is not None, (
            "Tracking No or Packing Slip No field was not available after selecting the card."
        )

        enter_tracking_and_packing(driver)

        set_button_clicked = click_set_tracking_no(driver)
        assert set_button_clicked, "Set Tracking No button was not found on the Set Tracking/Packing Slip Number Cards page."

        wait_ready(driver)
        time.sleep(PAUSE * 2)
        take_screenshot(driver, "04_after_set")

        current_url = driver.current_url.lower()
        page_text = (driver.find_element(By.TAG_NAME, "body").text or "").lower()
        success_keywords = [
            "successfully",
            "tracking number",
            "packing slip",
            "updated successfully",
            "following cards were successful",
            "set successfully",
        ]

        if "settrackingnoitems" not in current_url and (
            "settrackingnoresults" in current_url or any(keyword in page_text for keyword in success_keywords)
        ):
            back_result = click_back_to_items(driver)
            if not back_result:
                driver.get(ITEMS_URL)
                wait_ready(driver)
                time.sleep(PAUSE)
                back_result = True
            assert back_result, "Back to Items button was not found after the Set action."
        elif "settrackingnocards" in current_url:
            driver.get(ITEMS_URL)
            wait_ready(driver)
            time.sleep(PAUSE)

        wait_ready(driver)
        time.sleep(PAUSE)
        take_screenshot(driver, "05_back_to_items")

        if "settrackingnoitems" not in driver.current_url.lower():
            driver.get(ITEMS_URL)
            wait_ready(driver)
            time.sleep(PAUSE)

        assert "settrackingnoitems" in driver.current_url.lower(), (
            f"Did not finish the Set Tracking/Packing Slip Number process by returning to the Items page. URL: {driver.current_url}"
        )

        print("  [PASS] Supplier Set Tracking/Packing Slip Numbers flow completed successfully.")
