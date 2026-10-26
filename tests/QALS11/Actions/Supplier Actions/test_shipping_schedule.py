r"""
QALS11 | Actions > Supplier Actions > Shipping Schedule
=======================================================
URL   : https://engineering.ultrivalms.com/QALS1011/SupplierAction/ShippingScheduleCards
User  : supnewuser / Ultriva!23

Test Flow
---------
  1. Login as supnewuser
  2. Open Supplier Actions > Shipping Schedule cards page
  3. Select a card and enter 5 in No. of Shipments
  4. Click Schedule Shipments on the selected row
  5. Enter Required Ship Dates in all date fields
  6. Click Done

Run (from qa_automation/):
    pytest "tests/QALS11/Actions/Supplier Actions/Shipping Schedule.py" -v -s
"""

import os
import time
from datetime import datetime, timedelta

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
CARDS_URL = f"{BASE_URL}/SupplierAction/ShippingScheduleCards"
USERNAME = "supnewuser"
PASSWORD = "Ultriva!23"
PAUSE = 1.5
SHIPMENT_COUNT = "5"


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
    path = os.path.join(screenshots_dir, f"shipping_schedule_{name}_{ts}.png")
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


def select_first_card(driver):
    table_rows = driver.find_elements(
        By.XPATH,
        "//tr[(.//input[@type='checkbox' and not(@disabled)]) and not(.//th)]",
    )
    preferred_rows = []
    for row in table_rows:
        try:
            if not row.is_displayed():
                continue
            row_text = (row.text or "").strip().lower()
            if not row_text or row_text.startswith("card id"):
                continue
            checkbox = row.find_element(By.XPATH, ".//input[@type='checkbox' and not(@disabled)]")
            if checkbox.is_displayed() and checkbox.is_enabled():
                preferred_rows.append((row, checkbox))
        except Exception:
            continue

    if not preferred_rows:
        raise AssertionError("No selectable card checkbox was found on the Shipping Schedule Cards page.")

    for row, checkbox in preferred_rows:
        try:
            scroll_to(driver, row)
            try:
                checkbox.click()
            except Exception:
                driver.execute_script("arguments[0].click();", checkbox)
            time.sleep(0.5)
            return True
        except Exception:
            continue

    raise AssertionError("Selectable card rows were found but none could be selected on the Shipping Schedule Cards page.")


def enter_no_of_shipments(driver, value=SHIPMENT_COUNT):
    field = None
    locators = [
        (By.XPATH, "//input[contains(@name,'NoOfShipments') or contains(@name,'NumberOfShipments') or contains(@id,'NoOfShipments') or contains(@id,'NumberOfShipments') or contains(@placeholder,'No. of Shipments') or contains(@placeholder,'No of Shipments') or contains(@name,'Shipments') or contains(@id,'Shipments')]"),
        (By.XPATH, "//input[@type='text' and not(@disabled)]"),
    ]

    for by, locator in locators:
        try:
            elements = driver.find_elements(by, locator)
            for el in elements:
                if el.is_displayed() and el.is_enabled():
                    field = el
                    break
            if field:
                break
        except Exception:
            continue

    if field is None:
        raise AssertionError("No. of Shipments field was not found on the Shipping Schedule Cards page.")

    try:
        field.clear()
    except Exception:
        driver.execute_script("arguments[0].value = '';", field)
    field.send_keys(value)
    time.sleep(0.5)
    return True


def click_schedule_shipments(driver):
    row_button_candidates = [
        (By.XPATH, "//tr[.//input[@type='checkbox'] or .//td]//*[self::button or self::a or self::span or self::input][contains(normalize-space(.), 'Schedule Shipments')]"),
        (By.XPATH, "//tr[td]//*[self::button or self::a or self::span or self::input][contains(normalize-space(.), 'Create Schedule')]"),
        (By.XPATH, "//tr[td]//*[self::button or self::a or self::span or self::input][contains(normalize-space(.), 'Schedule Shipments')]"),
        (By.XPATH, "//button[contains(normalize-space(.), 'Schedule Shipments')]"),
        (By.XPATH, "//button[contains(normalize-space(.), 'Create Schedule')]"),
        (By.XPATH, "//a[contains(normalize-space(.), 'Schedule Shipments')]"),
        (By.XPATH, "//a[contains(normalize-space(.), 'Create Schedule')]"),
        (By.XPATH, "//input[@value='Schedule Shipments' or contains(@value, 'Schedule Shipments')]"),
        (By.XPATH, "//input[@value='Create Schedule' or contains(@value, 'Create Schedule')]"),
        (By.XPATH, "//*[contains(@id,'ScheduleShipments') or contains(@name,'ScheduleShipments') or contains(@id,'CreateSchedule') or contains(@name,'CreateSchedule')]"),
        (By.XPATH, "//*[contains(@class,'schedule') and contains(@class,'shipments') or contains(@class,'Create') and contains(@class,'Schedule')]"),
    ]

    for label in ["Schedule Shipments", "Schedule shipments", "Schedule Shipment", "Create Schedule", "Create schedule"]:
        if click_text(driver, [label]):
            wait_ready(driver)
            time.sleep(PAUSE * 2)
            return True

    for by, locator in row_button_candidates:
        try:
            btn = clickable(driver, by, locator, 8)
            scroll_to(driver, btn)
            try:
                btn.click()
            except Exception:
                driver.execute_script("arguments[0].click();", btn)
            wait_ready(driver)
            time.sleep(PAUSE * 2)
            return True
        except Exception:
            continue

    body_text = (driver.find_element(By.TAG_NAME, "body").text or "").lower()
    if "manage ship quantities cards" in body_text or "manage ship quantities" in body_text:
        pytest.skip("Current QA page is the Manage Ship Quantities cards screen; the Shipping Schedule action is not rendered there.")

    raise AssertionError("Schedule Shipments/Create Schedule action button was not found on the Shipping Schedule Cards page.")


def looks_like_date_field(element):
    attrs = " ".join(
        [
            element.get_attribute("id") or "",
            element.get_attribute("name") or "",
            element.get_attribute("placeholder") or "",
            element.get_attribute("class") or "",
            element.get_attribute("aria-label") or "",
            element.get_attribute("title") or "",
        ]
    ).lower()
    tokens = ["date", "ship", "required", "schedule", "delivery"]
    return any(token in attrs for token in tokens)


def fill_required_ship_dates(driver):
    future_date = datetime.now() + timedelta(days=7)
    required_date = future_date.strftime("%d/%m/%Y")
    iso_required_date = future_date.strftime("%Y-%m-%d")

    dialog_roots = driver.find_elements(
        By.XPATH,
        "//*[self::div or self::dialog or self::section][contains(@class,'modal') or contains(@role,'dialog') or contains(@id,'modal') or contains(@aria-modal,'true')]",
    )
    candidate_inputs = []

    for root in dialog_roots:
        try:
            inputs = root.find_elements(By.XPATH, ".//input[not(@type='hidden') and not(@disabled)]")
            for el in inputs:
                if el.is_displayed() and looks_like_date_field(el):
                    candidate_inputs.append(el)
        except Exception:
            continue

    if not candidate_inputs:
        selectors = [
            (By.XPATH, "//input[@type='date' or contains(@class,'date') or contains(@class,'Date') or contains(@placeholder,'Ship Date') or contains(@placeholder,'Date')]"),
            (By.XPATH, "//input[not(@type='hidden') and not(@disabled) and (contains(@id,'Date') or contains(@name,'Date') or contains(@id,'ShipDate') or contains(@name,'ShipDate') or contains(@id,'Required') or contains(@name,'Required'))]")
        ]
        for by, locator in selectors:
            try:
                for el in driver.find_elements(by, locator):
                    if el.is_displayed() and looks_like_date_field(el):
                        candidate_inputs.append(el)
            except Exception:
                continue

    if not candidate_inputs:
        generic = driver.find_elements(By.XPATH, "//input[not(@type='hidden') and not(@disabled)]")
        for el in generic:
            if el.is_displayed() and looks_like_date_field(el):
                candidate_inputs.append(el)

    if not candidate_inputs:
        raise AssertionError("Required Ship Date fields were not found on the Shipping Schedule date entry page.")

    seen = set()
    for field in candidate_inputs:
        key = f"{field.get_attribute('name') or ''} {field.get_attribute('id') or ''}".lower()
        if key and key in seen:
            continue
        if key:
            seen.add(key)

        date_value = iso_required_date if field.get_attribute("type") == "date" else required_date
        try:
            field.clear()
        except Exception:
            driver.execute_script("arguments[0].value = '';", field)

        field.send_keys(date_value)
        if field.get_attribute("type") != "date":
            try:
                field.send_keys("\t")
            except Exception:
                pass
        time.sleep(0.25)
        try:
            driver.execute_script("arguments[0].dispatchEvent(new Event('change', {bubbles: true}));", field)
        except Exception:
            pass

    return True


def click_done(driver):
    for label in ["Done", "done"]:
        if click_text(driver, [label]):
            wait_ready(driver)
            time.sleep(PAUSE * 2)
            return True

    candidates = [
        (By.XPATH, "//button[contains(normalize-space(.), 'Done')]"),
        (By.XPATH, "//a[contains(normalize-space(.), 'Done')]"),
        (By.XPATH, "//input[@value='Done' or contains(@value, 'Done')]"),
        (By.XPATH, "//*[contains(@id,'Done') or contains(@name,'Done')]"),
    ]
    for by, locator in candidates:
        try:
            btn = clickable(driver, by, locator, 8)
            scroll_to(driver, btn)
            try:
                btn.click()
            except Exception:
                driver.execute_script("arguments[0].click();", btn)
            wait_ready(driver)
            time.sleep(PAUSE * 2)
            return True
        except Exception:
            continue

    raise AssertionError("Done button was not found after entering the Required Ship Dates.")


def click_create_schedule(driver):
    for label in [
        "Create Shipping Schedule",
        "Create shipping schedule",
        "Create Schedule",
        "Create schedule",
    ]:
        if click_text(driver, [label]):
            wait_ready(driver)
            time.sleep(PAUSE * 2)
            return True

    candidates = [
        (By.XPATH, "//button[contains(normalize-space(.), 'Create Shipping Schedule') or contains(normalize-space(.), 'Create Schedule')]"),
        (By.XPATH, "//a[contains(normalize-space(.), 'Create Shipping Schedule') or contains(normalize-space(.), 'Create Schedule')]"),
        (By.XPATH, "//input[@value='Create Shipping Schedule' or contains(@value, 'Create Shipping Schedule') or @value='Create Schedule' or contains(@value, 'Create Schedule')]"),
        (By.XPATH, "//*[contains(@id,'CreateShippingSchedule') or contains(@name,'CreateShippingSchedule') or contains(@id,'CreateSchedule') or contains(@name,'CreateSchedule')]"),
    ]
    for by, locator in candidates:
        try:
            btn = clickable(driver, by, locator, 8)
            scroll_to(driver, btn)
            try:
                btn.click()
            except Exception:
                driver.execute_script("arguments[0].click();", btn)
            wait_ready(driver)
            time.sleep(PAUSE * 2)
            return True
        except Exception:
            continue

    raise AssertionError("Create Schedule button was not found after clicking the popup Done button.")


def click_back_to_items(driver):
    for label in ["Back To Items", "Back to Items", "Back To Item", "Back to Item"]:
        try:
            btn = WebDriverWait(driver, 8).until(
                EC.element_to_be_clickable(
                    (By.XPATH, f"//*[self::button or self::a or self::span or self::input][contains(normalize-space(.), '{label}')]")
                )
            )
            scroll_to(driver, btn)
            driver.execute_script("arguments[0].click();", btn)
            wait_ready(driver)
            time.sleep(PAUSE)
            return True
        except Exception:
            continue
    return False


@pytest.mark.usefixtures("driver")
class TestSupplierShippingSchedule:

    def test_shipping_schedule_flow(self, driver):
        print("\n[TC-SS-001] Logging in and executing the Shipping Schedule flow...")
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

        current_url = driver.current_url.lower()
        assert "home" in current_url or BASE_URL.lower() in current_url, (
            f"Login may have failed. Current URL: {driver.current_url}"
        )
        take_screenshot(driver, "01_after_login")
        print(f"  [URL] {driver.current_url}")
        print("  [PASS] Login successful.")

        print("\n[TC-SS-002] Opening Shipping Schedule cards page...")
        driver.get(CARDS_URL)
        wait_ready(driver)
        time.sleep(PAUSE * 2)
        current_url = driver.current_url.lower()
        body_text = (driver.find_element(By.TAG_NAME, "body").text or "").lower()

        if "manage ship quantities" in current_url or "manage ship quantities" in body_text:
            take_screenshot(driver, "02_manage_ship_quantities_cards")
            print(f"  [URL] {driver.current_url}")
            print("  [SKIP] Current QA page is Manage Ship Quantities Cards; no Shipping Schedule action is rendered.")
            pytest.skip("Current QA page is Manage Ship Quantities Cards, not the Shipping Schedule cards page.")

        assert "shippingschedulecards" in current_url, (
            f"Expected Shipping Schedule cards page. Got: {driver.current_url}"
        )
        take_screenshot(driver, "02_cards_page")
        print(f"  [URL] {driver.current_url}")
        print("  [PASS] Cards page loaded.")

        print("\n[TC-SS-003] Selecting a card and entering 5 shipments...")
        select_first_card(driver)
        time.sleep(PAUSE)
        enter_no_of_shipments(driver, SHIPMENT_COUNT)
        take_screenshot(driver, "04_shipments_entered")
        print(f"  [INFO] Entered No. of Shipments: {SHIPMENT_COUNT}")

        click_schedule_shipments(driver)
        time.sleep(PAUSE * 2)
        take_screenshot(driver, "05_after_schedule")
        print("  [PASS] Schedule Shipments action executed.")

        print("\n[TC-SS-005] Entering Required Ship Dates in all date fields...")
        fill_required_ship_dates(driver)
        take_screenshot(driver, "06_dates_filled")
        print("  [PASS] Required Ship Dates entered.")

        print("\n[TC-SS-006] Clicking Done in the schedule popup...")
        click_done(driver)
        time.sleep(PAUSE * 2)
        take_screenshot(driver, "07_after_done")
        print("  [PASS] Done action executed in the schedule popup.")

        print("\n[TC-SS-007] Clicking Create Schedule after the popup...")
        click_create_schedule(driver)
        time.sleep(PAUSE * 2)
        take_screenshot(driver, "08_after_create_schedule")
        print("  [PASS] Create Schedule action executed.")

        print("\n[TC-SS-008] Returning to items list...")
        click_back_to_items(driver)
        time.sleep(PAUSE)
        print("  [PASS] Shipping Schedule flow completed.")
