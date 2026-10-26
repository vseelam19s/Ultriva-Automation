"""
QALS11 | Actions > Supplier Actions > Reschedule
==============================================
1. Login as supnewuser
2. Click Actions
3. Open Supplier Actions > Reschedule Request
4. Select any item from the list
5. Click Show Cards
6. Select any two cards using the row checkboxes
7. Enter New Reqd Ship Date as 21/10/2026
8. Select Reschedule Reason as Reason 1
9. Click Reschedule button
"""

import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
USERNAME = "supnewuser"
PASSWORD = "Ultriva!23"
PAUSE = 1.5
STEP_DELAY_SECONDS = 10


def wait_for_step(step_name):
    print(f"[STEP {step_name}] Waiting {STEP_DELAY_SECONDS}s before continuing...")
    time.sleep(STEP_DELAY_SECONDS)


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


def js_click(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    try:
        element.click()
    except Exception:
        driver.execute_script("arguments[0].click();", element)


def click_text(driver, labels):
    for label in labels:
        locators = [
            (By.XPATH, f"//*[self::a or self::button or self::input or self::span or self::div or self::td or self::li][normalize-space(.)='{label}']"),
            (By.XPATH, f"//*[self::a or self::button or self::input or self::span or self::div or self::td or self::li][contains(normalize-space(.), '{label}')]"),
            (By.XPATH, f"//*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{label.lower()}')]"),
            (By.XPATH, f"//button[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{label.lower()}')]"),
            (By.XPATH, f"//a[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{label.lower()}')]"),
        ]
        for by, locator in locators:
            try:
                for element in driver.find_elements(by, locator):
                    if element.is_displayed() and element.is_enabled():
                        try:
                            element.click()
                        except Exception:
                            driver.execute_script("arguments[0].click();", element)
                        return True
            except Exception:
                continue

        try:
            matched = driver.execute_script(
                """
                var wanted = arguments[0].trim().toLowerCase();
                var nodes = document.querySelectorAll('a, button, input, span, div, td, li');
                for (var i = 0; i < nodes.length; i++) {
                    var txt = (nodes[i].innerText || nodes[i].value || '').replace(/\s+/g, ' ').trim().toLowerCase();
                    var visible = !!(nodes[i].offsetParent !== null || nodes[i].getClientRects().length > 0);
                    if (visible && (txt === wanted || txt.indexOf(wanted) !== -1)) {
                        try { nodes[i].click(); } catch (e) { nodes[i].dispatchEvent(new MouseEvent('click', {bubbles: true})); }
                        return true;
                    }
                }
                return false;
                """,
                label,
            )
            if matched:
                return True
        except Exception:
            continue
    return False


def select_two_cards(driver):
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


def fill_reschedule_form(driver, date_value="21/10/2026", reason_value="Reason 1"):
    selected_prefixes = set()
    for checkbox in driver.find_elements(By.XPATH, "//input[contains(@name,'$CheckboxCardGID') and not(contains(@name,'All$CheckboxCardGID'))]"):
        try:
            if not checkbox.is_displayed() or not checkbox.is_enabled():
                continue
            if checkbox.is_selected() or driver.execute_script("return arguments[0].checked;", checkbox):
                name = checkbox.get_attribute("name") or ""
                if "$CheckboxCardGID" in name:
                    selected_prefixes.add(name.replace("$CheckboxCardGID", ""))
        except Exception:
            continue

    assert selected_prefixes, "No selected cards were found to update the reschedule date and reason."

    for prefix in sorted(selected_prefixes):
        date_input = driver.find_elements(By.XPATH, f"//input[@name='{prefix}$TextboxReqShipDate']")
        reason_select = driver.find_elements(By.XPATH, f"//select[@name='{prefix}$RescheduleReason']")

        if date_input:
            date_input = date_input[0]
            try:
                driver.execute_script(
                    """
                    arguments[0].value = arguments[1];
                    arguments[0].dispatchEvent(new Event('input', {bubbles: true}));
                    arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
                    """,
                    date_input,
                    date_value,
                )
            except Exception:
                try:
                    date_input.clear()
                    date_input.send_keys(date_value)
                except Exception:
                    pass

        if reason_select:
            reason_select = reason_select[0]
            try:
                select = Select(reason_select)
                select.select_by_visible_text(reason_value)
            except Exception:
                for option in reason_select.find_elements(By.TAG_NAME, 'option'):
                    if option.text.strip() == reason_value:
                        try:
                            option.click()
                            break
                        except Exception:
                            driver.execute_script("arguments[0].selected = true; arguments[0].dispatchEvent(new Event('change', {bubbles: true}));", option)


def select_item_and_show_cards(driver):
    driver.get(f"{BASE_URL}/SupplierAction/SupplierRescheduleCards")
    wait_ready(driver)
    time.sleep(PAUSE)

    item_links = driver.find_elements(By.XPATH, "//a[contains(@class,'GridLink')]")
    if item_links:
        selected_item = item_links[0]
        print(f"[INFO] Selected item: {selected_item.text.strip()}")
        js_click(driver, selected_item)
        wait_ready(driver)
        time.sleep(PAUSE)

    if "supplierreschedulecards" not in driver.current_url.lower():
        show_cards = None
        for locator in [
            (By.XPATH, "//button[contains(normalize-space(),'Show Cards')]"),
            (By.XPATH, "//a[contains(normalize-space(),'Show Cards')]"),
            (By.XPATH, "//span[contains(normalize-space(),'Show Cards')]"),
            (By.XPATH, "//*[contains(@id,'ShowCards') or contains(@id,'showCards')]"),
        ]:
            try:
                show_cards = WebDriverWait(driver, 8).until(EC.element_to_be_clickable(locator))
                break
            except Exception:
                continue

        assert show_cards, "Show Cards button not found after selecting the item."
        js_click(driver, show_cards)
        wait_ready(driver)
        time.sleep(PAUSE)

    assert "supplierreschedulecards" in driver.current_url.lower(), (
        f"Expected to land on Supplier Reschedule Cards page. Current URL: {driver.current_url}"
    )


def click_reschedule_button(driver):
    locator = (By.XPATH, "//span[contains(@class,'btn') and normalize-space(.)='Reschedule']")
    WebDriverWait(driver, 15).until(
        lambda d: any(e.is_displayed() for e in d.find_elements(*locator))
    )
    button = next(e for e in driver.find_elements(*locator) if e.is_displayed())
    js_click(driver, button)
    WebDriverWait(driver, 30).until(EC.url_contains("SupplierRescheduleResults"))
    wait_ready(driver)


@pytest.mark.usefixtures("driver")
class TestSupplierReshchedule:
    def test_reshchedule_flow(self, driver):
        print("\n[TC-RESH-001] Logging in and executing the Supplier Reschedule flow...")

        print("[STEP 1] Open login page.")
        driver.get(f"{BASE_URL}/Account/Login")
        wait_ready(driver)
        wait_for_step("1")

        print("[STEP 2] Enter username and password, then login.")
        username_field = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "UserName")))
        password_field = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "Password")))
        login_button = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, "login-button")))

        username_field.clear()
        username_field.send_keys(USERNAME)
        password_field.clear()
        password_field.send_keys(PASSWORD)
        login_button.click()
        wait_ready(driver)
        wait_for_step("2")

        print("[STEP 3] Select an item and click Show Cards.")
        select_item_and_show_cards(driver)
        wait_for_step("3")

        assert "supplierreschedulecards" in driver.current_url.lower(), (
            f"Reschedule Cards page did not open after selecting the item. URL: {driver.current_url}"
        )

        print("[STEP 4] Select two cards from the list.")
        assert select_two_cards(driver), "Could not select two cards from the Reschedule Request Cards list."
        wait_for_step("4")

        print("[STEP 5] Fill the reschedule date and reason for selected cards.")
        fill_reschedule_form(driver, "21/10/2026", "Reason 1")
        wait_for_step("5")

        print("[STEP 6] Click Reschedule on the Reschedule Request Cards List.")
        click_reschedule_button(driver)
        body_text = driver.find_element(By.TAG_NAME, "body").text
        assert "Reschedule Request Cards Results" in body_text, body_text
        assert "Following Cards were successful" in body_text, body_text
        assert body_text.count("Ultriva Usser will be notified of the requested change") == 2, body_text
        print("[STEP PASS] Both cards were rescheduled successfully.")
