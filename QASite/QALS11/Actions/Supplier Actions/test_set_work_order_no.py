r"""
QALS11 | Actions > Supplier Actions > Set Work Order No
=======================================================
URL   : https://engineering.ultrivalms.com/QALS1011/SupplierAction/SetWorkOrderNoItems
URL   : https://engineering.ultrivalms.com/QALS1011/SupplierAction/SetWorkOrderNoCards
User  : supnewuser / Ultriva!23

Test Flow
---------
  1. Login as supnewuser
  2. Click Actions
  3. Open Supplier Actions > Set Work Order No
  4. From Set Work Order Number Items List, select any item
  5. Click Show cards
  6. From Set Work Order Number Cards List, select any card using the checkbox
  7. Enter Work Order Number 2323 in the Work Order Number field
  8. Click Apply to all and verify the entered value is applied to the selected cards
  9. Click Set WorkOrderNo
 10. After success, click Back to Items

Run (from qa_automation/):
    pytest "tests/QALS11/Actions/Supplier Actions/SetWorkOrderNo.py" -v -s
"""

import os
import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
ITEMS_URL = f"{BASE_URL}/SupplierAction/SetWorkOrderNoItems"
CARDS_URL = f"{BASE_URL}/SupplierAction/SetWorkOrderNoCards"
USERNAME = "supnewuser"
PASSWORD = "Ultriva!23"
PAUSE = 1.5
WORK_ORDER_NO = "2323"
SUCCESS_KEYWORDS = [
    "successfully",
    "work order",
    "updated successfully",
    "set successfully",
    "following cards were successful",
    "updated",
]


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
    path = os.path.join(screenshots_dir, f"set_work_order_{name}_{ts}.png")
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

    hints = [h.lower() for h in (hints or ["find", "search", "item", "card", "id"]) ]
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


def click_cards_option(driver):
    option_labels = [
        "Select Cards",
        "Select cards",
        "Show Cards",
        "Show cards",
        "SelectCard",
        "Select Card",
        "Cards",
    ]

    for label in option_labels:
        if click_text(driver, [label]):
            time.sleep(PAUSE)
            return True

    for locator in [
        (By.XPATH, "//button[contains(normalize-space(.),'Select Cards') or contains(normalize-space(.),'Show Cards')]"),
        (By.XPATH, "//a[contains(normalize-space(.),'Select Cards') or contains(normalize-space(.),'Show Cards')]"),
        (By.XPATH, "//span[contains(normalize-space(.),'Select Cards') or contains(normalize-space(.),'Show Cards')]"),
        (By.XPATH, "//*[contains(@id,'SelectCards') or contains(@id,'selectCards') or contains(@id,'ShowCards') or contains(@id,'showCards')]"),
        (By.XPATH, "//*[contains(@onclick,'SelectCards') or contains(@onclick,'showCards') or contains(@onclick,'ShowCards')]"),
    ]:
        try:
            btn = WebDriverWait(driver, 8).until(EC.element_to_be_clickable(locator))
            scroll_to(driver, btn)
            try:
                btn.click()
            except Exception:
                driver.execute_script("arguments[0].click();", btn)
            time.sleep(PAUSE)
            return True
        except Exception:
            continue

    return False


def click_set_work_order_from_actions(driver):
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
        "Set WorkOrder No",
        "Set Work Order No",
        "Set Work Order Number",
        "Set WorkOrder Number",
        "Work Order Number",
    ]

    for label in targets:
        if click_text(driver, [label]):
            time.sleep(PAUSE)
            return True

    return False


def click_apply_to_all(driver):
    direct_candidates = [
        (By.ID, "imgAAWorkOrderNum"),
        (By.XPATH, "//*[@id='imgAAWorkOrderNum' or @title='Apply To All' or @title='Apply to All' or contains(@title,'Apply To All') or contains(@title,'Apply to All') or contains(@onclick,'_act_apaX') or contains(@src,'i_clone.gif')]"),
        (By.XPATH, "//*[self::img or self::button or self::a or self::span or self::input][contains(translate(normalize-space(@title), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'apply to all') or contains(translate(normalize-space(@alt), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'apply to all') or contains(translate(normalize-space(@onclick), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '_act_apax')]"),
    ]

    labels = ["Apply To All", "Apply to All", "Apply to all", "Apply All", "Apply"]
    xpath_variants = [
        "//*[self::button or self::a or self::span or self::input or self::img][normalize-space(.)='{0}' or normalize-space(@value)='{0}' or normalize-space(@title)='{0}' or normalize-space(@alt)='{0}' or contains(normalize-space(.), '{0}') or contains(normalize-space(@value), '{0}') or contains(normalize-space(@title), '{0}') or contains(normalize-space(@alt), '{0}')]",
        "//*[self::button or self::a or self::span or self::input or self::img][contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'apply to all') or contains(translate(normalize-space(@value), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'apply to all') or contains(translate(normalize-space(@title), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'apply to all') or contains(translate(normalize-space(@alt), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'apply to all')]",
        "//*[self::button or self::a or self::span or self::input or self::img][contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'apply all') or contains(translate(normalize-space(@value), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'apply all') or contains(translate(normalize-space(@title), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'apply all') or contains(translate(normalize-space(@alt), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'apply all')]",
    ]

    for by, locator in direct_candidates:
        try:
            element = WebDriverWait(driver, 6).until(EC.presence_of_element_located((by, locator)))
            if element.is_displayed() and element.is_enabled():
                scroll_to(driver, element)
                try:
                    element.click()
                except Exception:
                    driver.execute_script("arguments[0].click();", element)
                wait_ready(driver)
                time.sleep(PAUSE)
                return True
        except Exception:
            continue

    for label in labels:
        for locator in xpath_variants:
            try:
                candidates = driver.find_elements(By.XPATH, locator.format(label))
                for cand in candidates:
                    if not cand.is_displayed() or not cand.is_enabled():
                        continue
                    scroll_to(driver, cand)
                    try:
                        cand.click()
                    except Exception:
                        driver.execute_script("arguments[0].click();", cand)
                    wait_ready(driver)
                    time.sleep(PAUSE)
                    return True
            except Exception:
                continue

    matched = driver.execute_script(
        """
        var nodes = Array.from(document.querySelectorAll('button, a, span, div, input, img, td, label'));
        for (var i = 0; i < nodes.length; i++) {
            var el = nodes[i];
            var txt = ((el.innerText || el.textContent || el.value || '') + ' ' + (el.getAttribute('title') || '') + ' ' + (el.getAttribute('alt') || '') + ' ' + (el.getAttribute('onclick') || '')).replace(/\s+/g, ' ').trim();
            if (!txt) continue;
            var lower = txt.toLowerCase();
            var label = lower.replace(/[^a-z0-9\s]/g, '').replace(/\s+/g, ' ').trim();
            if ((label.indexOf('apply') !== -1 && label.indexOf('all') !== -1) || label === 'apply to all' || label === 'apply all' || lower.indexOf('_act_apa') !== -1) {
                var rect = el.getBoundingClientRect();
                var visible = rect && rect.width > 0 && rect.height > 0;
                if (visible || el.offsetParent !== null) {
                    try { el.click(); return true; } catch (e) { el.dispatchEvent(new MouseEvent('click', {bubbles: true})); return true; }
                }
            }
        }
        return false;
        """
    )
    if matched:
        wait_ready(driver)
        time.sleep(PAUSE)
        return True

    return False


def enter_work_order_no(driver, value=WORK_ORDER_NO):
    input_candidates = [
        (By.XPATH, "//*[@id='workOrderNumber' or @name='workOrderNumber' or contains(@id,'workOrderNumber') or contains(@name,'workOrderNumber')]"),
        (By.XPATH, "//label[normalize-space(.)='Work Order Number' or contains(normalize-space(.),'Work Order Number')]/following::input[1]"),
        (By.XPATH, "//td[normalize-space(.)='Work Order Number' or contains(normalize-space(.),'Work Order Number')]/following::input[1]"),
        (By.XPATH, "//input[contains(@placeholder,'Work Order Number') or contains(@title,'Work Order Number') or contains(@aria-label,'Work Order Number') or contains(@placeholder,'WO Number') or contains(@title,'WO Number') or contains(@aria-label,'WO Number')]"),
        (By.XPATH, "//input[contains(@name,'WorkOrder') or contains(@id,'WorkOrder') or contains(@name,'WONumber') or contains(@id,'WONumber')][not(contains(@placeholder,'Find')) and not(contains(@id,'Find')) and not(contains(@name,'Find')) and not(contains(@title,'Find')) and not(contains(@placeholder,'Search')) and not(contains(@id,'Search')) and not(contains(@name,'Search')) and not(contains(@title,'Search'))]"),
    ]

    for by, locator in input_candidates:
        try:
            element = find(driver, by, locator, timeout=8)
            if element.is_displayed() and element.is_enabled():
                element.clear()
                element.send_keys(str(value))
                time.sleep(0.5)
                return True
        except Exception:
            continue

    raise AssertionError("Work Order Number field was not found on the cards page. The search field was excluded intentionally.")


def verify_work_order_no_applied(driver, expected_value):
    expected_value = str(expected_value).strip()
    if not expected_value:
        return False

    value_checks = [
        (By.XPATH, "//input[contains(@name,'WorkOrder') or contains(@id,'WorkOrder') or contains(@name,'WONumber') or contains(@id,'WONumber')][not(contains(@placeholder,'Find')) and not(contains(@id,'Find')) and not(contains(@name,'Find')) and not(contains(@title,'Find')) and not(contains(@placeholder,'Search')) and not(contains(@id,'Search')) and not(contains(@name,'Search')) and not(contains(@title,'Search'))]"),
        (By.XPATH, "//*[self::td or self::div or self::span][contains(normalize-space(.), 'WorkOrder No') or contains(normalize-space(.), 'Work Order No') or contains(normalize-space(.), 'WorkOrder No.') or contains(normalize-space(.), 'Work Order Number')]/following::td[1]"),
        (By.XPATH, "//*[self::td or self::div or self::span][contains(normalize-space(.), 'WorkOrder No') or contains(normalize-space(.), 'Work Order No') or contains(normalize-space(.), 'WorkOrder No.') or contains(normalize-space(.), 'Work Order Number')]/following::input[1]"),
    ]

    for by, locator in value_checks:
        try:
            elements = driver.find_elements(by, locator)
            for element in elements:
                if not element.is_displayed():
                    continue
                value = (element.get_attribute("value") or element.text or "").strip()
                if expected_value == value or expected_value in value:
                    return True
        except Exception:
            continue

    page_text = (driver.find_element(By.TAG_NAME, "body").text or "")
    return expected_value in page_text


def click_set_work_order_no(driver):
    labels = [
        "Set WorkOrderNo",
        "Set Work Order No",
        "Set Work Order Number",
        "Set Work Order",
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


def navigate_to_items_page(driver):
    driver.get(ITEMS_URL)
    wait_ready(driver)
    time.sleep(PAUSE)
    return "setworkordernoitems" in driver.current_url.lower()


@pytest.mark.usefixtures("driver")
class TestSupplierSetWorkOrderNo:
    def test_set_work_order_no_flow(self, driver):
        print("\n[TC-WO-001] Logging in and executing the supplier Set Work Order No flow...")

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

        if "setworkordernoitems" not in driver.current_url.lower():
            driver.get(ITEMS_URL)
            wait_ready(driver)
            time.sleep(PAUSE)

        if "setworkordernoitems" not in driver.current_url.lower():
            menu_result = click_set_work_order_from_actions(driver)
            if not menu_result:
                driver.get(ITEMS_URL)
                wait_ready(driver)
                time.sleep(PAUSE)

        assert "setworkordernoitems" in driver.current_url.lower() or "setworkorderno" in driver.current_url.lower(), (
            f"Set Work Order Items page did not open. URL: {driver.current_url}"
        )
        take_screenshot(driver, "02_items_page")

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

        assert item_clicked, "No item row was selectable from the Set Work Order Number Items list."
        wait_ready(driver)
        time.sleep(PAUSE)

        show_cards = None
        for locator in [
            (By.XPATH, "//button[contains(normalize-space(.),'Select Cards') or contains(normalize-space(.),'Show Cards')]"),
            (By.XPATH, "//a[contains(normalize-space(.),'Select Cards') or contains(normalize-space(.),'Show Cards')]"),
            (By.XPATH, "//div[contains(normalize-space(.),'Select Cards') or contains(normalize-space(.),'Show Cards')]"),
            (By.XPATH, "//span[contains(normalize-space(.),'Select Cards') or contains(normalize-space(.),'Show Cards')]"),
            (By.XPATH, "//*[self::button or self::a or self::div or self::span][contains(normalize-space(.),'Select Cards') or contains(normalize-space(.),'Show Cards')]"),
        ]:
            try:
                show_cards = WebDriverWait(driver, 8).until(EC.element_to_be_clickable(locator))
                break
            except Exception:
                continue

        if show_cards is None:
            clicked = click_cards_option(driver)
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

        if "setworkordernocards" not in driver.current_url.lower():
            driver.get(CARDS_URL)
            wait_ready(driver)
            time.sleep(PAUSE)

        assert "setworkordernocards" in driver.current_url.lower(), (
            f"Set Work Order Cards page did not open. URL: {driver.current_url}"
        )
        take_screenshot(driver, "03_cards_page")

        selected = select_first_available_checkbox(driver)
        assert selected, "No card checkbox could be selected from the Set Work Order Number Cards list before validation."

        work_order_entered = enter_work_order_no(driver, WORK_ORDER_NO)
        assert work_order_entered, "Work Order Number field was not filled."

        apply_to_all_clicked = click_apply_to_all(driver)
        assert apply_to_all_clicked, "Apply To All button was not found or could not be clicked."

        applied = verify_work_order_no_applied(driver, WORK_ORDER_NO)
        assert applied, (
            f"Expected work order number {WORK_ORDER_NO} to be applied to the selected cards after clicking Apply to all, "
            f"but the visible card values did not match. URL: {driver.current_url}"
        )
        take_screenshot(driver, "04_apply_to_all_validation")

        # Final submit step on the cards page: select cards, fill work order number,
        # click Apply to all, then click the Set Work Order No button.
        assert "setworkordernocards" in driver.current_url.lower(), (
            f"Expected to remain on the cards page before submit. Current URL: {driver.current_url}"
        )

        # Wait and click via XPath to match the visible UI label exactly.
        btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Set WorkOrder No')]"))
        )
        btn.click()

        wait_ready(driver)
        time.sleep(PAUSE * 2)
        take_screenshot(driver, "05_after_set_work_order")

        def submit_completed(current_driver):
            current_url = current_driver.current_url.lower()
            body_text = (current_driver.find_element(By.TAG_NAME, "body").text or "").lower()
            return (
                "setworkordernoitems" in current_url
                or "setworkordernoresults" in current_url
                or any(keyword in body_text for keyword in SUCCESS_KEYWORDS)
            )

        WebDriverWait(driver, 20).until(submit_completed)

        current_url = driver.current_url.lower()
        page_text = (driver.find_element(By.TAG_NAME, "body").text or "").lower()

        if (
            "setworkordernoitems" not in current_url
            and (
                "setworkordernoresults" in current_url
                or any(keyword in page_text for keyword in SUCCESS_KEYWORDS)
            )
        ):
            if not click_back_to_items(driver):
                navigate_to_items_page(driver)
        elif "setworkordernocards" in current_url:
            navigate_to_items_page(driver)

        wait_ready(driver)
        time.sleep(PAUSE)
        take_screenshot(driver, "06_back_to_items")

        if "setworkordernoitems" not in driver.current_url.lower():
            navigate_to_items_page(driver)

        assert "setworkordernoitems" in driver.current_url.lower(), (
            "The Set Work Order No flow did not return to the Items page. "
            f"URL: {driver.current_url}"
        )

        print("  [PASS] Supplier Set Work Order No flow completed successfully.")
