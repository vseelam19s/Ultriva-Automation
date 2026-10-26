r"""
QALS11 | Actions > Supplier Actions > Add Notes
===============================================
URL   : https://engineering.ultrivalms.com/QALS1011/SupplierAction/AddNotesItems
URL   : https://engineering.ultrivalms.com/QALS1011/SupplierAction/AddNotesCards
User  : supnewuser / Ultriva!23

Business flow covered by this script
-----------------------------------
  1. Log in as supnewuser
  2. Open Supplier Actions > Add Notes Items
  3. Select an item and click Show Cards
  4. Select one or more cards
  5. Click Attach Notes
  6. Choose a note from the dropdown
  7. Check "Apply this notes and priority to all selected Cards"
  8. Click Apply Notes
  9. Click Submit
 10. Click Back to Items and return to the item list

Run (from qa_automation/):
    pytest "tests/QALS11/Actions/Supplier Actions/test_add_notes.py" -v -s

This file is organized as a step-by-step Selenium flow so each major action is
validated as its own test case. That makes it easier to see which part of the
workflow failed during a run.
"""

import os
import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
ITEMS_URL = f"{BASE_URL}/SupplierAction/AddNotesItems"
CARDS_URL = f"{BASE_URL}/SupplierAction/AddNotesCards"
USERNAME = "supnewuser"
PASSWORD = "Ultriva!23"
PAUSE = 1.5


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
    path = os.path.join(screenshots_dir, f"supplier_add_notes_{name}_{ts}.png")
    driver.save_screenshot(path)
    print(f"  [screenshot] {path}")
    return path


def click_text(driver, labels):
    for label in labels:
        locators = [
            (By.XPATH, f"//*[self::a or self::button or self::input or self::span or self::div][normalize-space(.)='{label}']"),
            (By.XPATH, f"//*[self::a or self::button or self::input or self::span or self::div][contains(normalize-space(.), '{label}')]"),
            (By.XPATH, f"//*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{label.lower()}')]"),
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
              var text = (els[i].innerText || els[i].value || '').replace(/\\s+/g, ' ').trim().toLowerCase();
              var visible = !!(els[i].offsetParent !== null && (els[i].offsetWidth > 0 || els[i].offsetHeight > 0 || els[i].getClientRects().length > 0));
              if ((text === wanted || text.indexOf(wanted) !== -1) && visible) {
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


def ensure_attachment_file(file_name="sample_attachment.txt"):
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), file_name))
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("Sample test attachment file content.\n")
    return file_path


def js_click(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    driver.execute_script("arguments[0].click();", element)


def ensure_logged_in(driver):
    current_url = driver.current_url.lower()
    if "login" in current_url or "account" in current_url or driver.current_url == "data:,":
        driver.get(f"{BASE_URL}/Account/Login")
        wait_ready(driver)
        username = find(driver, By.ID, "UserName")
        password = find(driver, By.ID, "Password")
        login_btn = clickable(driver, By.ID, "login-button")

        username.clear()
        username.send_keys(USERNAME)
        password.clear()
        password.send_keys(PASSWORD)
        login_btn.click()
        wait_ready(driver)
        time.sleep(PAUSE)


def step_banner(step_no, title):
    print(f"\n[STEP {step_no}] {title}")


def assert_url_contains(driver, expected_tokens, description):
    current_url = driver.current_url.lower()
    if not any(token in current_url for token in expected_tokens):
        raise AssertionError(f"{description}. Current URL: {driver.current_url}")


def step_01_login(driver):
    step_banner(1, "Log in as the supplier user")
    ensure_logged_in(driver)
    assert_url_contains(driver, ["home", BASE_URL.lower()], "Login did not land on the expected landing page")


def select_item_and_show_cards(driver):
    driver.get(ITEMS_URL)
    wait_ready(driver)
    time.sleep(PAUSE)

    item_links = driver.find_elements(By.XPATH, "//a[contains(@class,'GridLink')]")
    assert item_links, "No items found in Add Notes Items List"

    selected_item = item_links[0]
    print(f"  [INFO] Selected item: {selected_item.text.strip()}")
    scroll_to(driver, selected_item)
    try:
        selected_item.click()
    except Exception:
        js_click(driver, selected_item)
    wait_ready(driver)
    time.sleep(PAUSE)

    if not ("addnotescards" in driver.current_url.lower() or "addnotecards" in driver.current_url.lower()):
        show_cards = None
        for locator in [
            (By.XPATH, "//button[contains(normalize-space(),'Show Cards')]"),
            (By.XPATH, "//a[contains(normalize-space(),'Show Cards')]"),
            (By.XPATH, "//span[contains(normalize-space(),'Show Cards')]"),
            (By.XPATH, "//*[contains(@id,'ShowCards') or contains(@id,'showCards')]"),
        ]:
            try:
                show_cards = clickable(driver, locator[0], locator[1], 5)
                break
            except Exception:
                continue

        if show_cards:
            js_click(driver, show_cards)
            wait_ready(driver)
            time.sleep(PAUSE)

    assert "addnotes" in driver.current_url.lower(), f"Expected Add Notes Cards page. Got: {driver.current_url}"


def select_cards(driver, count=2):
    card_checkboxes = driver.find_elements(
        By.XPATH,
        "//input[contains(@name,'CheckboxCardGID') and not(contains(@name,'_All$'))]"
    )
    assert card_checkboxes, "No card row checkboxes found on Add Notes Cards page"

    selected_count = 0
    for checkbox in card_checkboxes[:count]:
        try:
            scroll_to(driver, checkbox)
            if not checkbox.is_selected():
                try:
                    checkbox.click()
                except Exception:
                    js_click(driver, checkbox)
            selected_count += 1
            time.sleep(0.3)
        except Exception:
            continue

    assert selected_count >= 1, "Failed to select at least one card"
    print(f"  [INFO] Selected {selected_count} card(s)")


def open_attach_notes_dialog(driver):
    attach_notes = None
    for locator in [
        (By.XPATH, "//button[contains(normalize-space(),'Attach Notes')]"),
        (By.XPATH, "//a[contains(normalize-space(),'Attach Notes')]"),
        (By.XPATH, "//span[contains(normalize-space(),'Attach Notes')]"),
        (By.XPATH, "//*[@id='btnAttachNotes' or contains(@id,'AttachNotes')]"),
    ]:
        try:
            attach_notes = clickable(driver, locator[0], locator[1], 5)
            break
        except Exception:
            continue

    assert attach_notes, "Attach Notes button not found on Add Notes Cards page"
    js_click(driver, attach_notes)
    time.sleep(PAUSE)


def choose_note_and_apply_to_all(driver):
    note_select = None
    for locator in [
        (By.XPATH, "//select[contains(@id,'NoteTitleID') or contains(@name,'NoteTitleID')]"),
        (By.XPATH, "//select[contains(@id,'NoteTitle') or contains(@name,'NoteTitle')]"),
        (By.XPATH, "//label[normalize-space()='Notes:']/following-sibling::select"),
        (By.XPATH, "//label[normalize-space()='Notes:']/following::select[1]"),
        (By.XPATH, "//select"),
    ]:
        try:
            note_select = find(driver, locator[0], locator[1], 8)
            if note_select.tag_name.lower() == "select":
                options = note_select.find_elements(By.TAG_NAME, "option")
                if len(options) > 1:
                    break
                note_select = None
        except Exception:
            continue

    if note_select is None:
        for sel in driver.find_elements(By.TAG_NAME, "select"):
            opts = sel.find_elements(By.TAG_NAME, "option")
            if len(opts) > 1:
                note_select = sel
                break

    assert note_select, "Notes dropdown not found in Attach Notes dialog"
    select = Select(note_select)
    note_options = [
        opt for opt in select.options
        if opt.get_attribute("value") and opt.text.strip() not in ("-- Select Notes --", "")
    ]
    if not note_options:
        note_options = [opt for opt in select.options if opt.text.strip() not in ("-- Select Notes --", "")]
    assert note_options, "No note options available in the dropdown"

    selected_note = note_options[0].text.strip()
    select.select_by_visible_text(selected_note)
    print(f"  [INFO] Selected note: {selected_note}")

    apply_all = None
    for locator in [
        (By.XPATH, "//input[@type='checkbox' and (contains(@id,'ApplyAll') or contains(@name,'ApplyAll') or contains(@id,'applyAll') or contains(@name,'applyAll'))]"),
        (By.XPATH, "//label[contains(normalize-space(),'Apply this notes')]/preceding-sibling::input[@type='checkbox'][1]"),
        (By.XPATH, "//label[contains(normalize-space(),'Apply this notes')]/following-sibling::input[@type='checkbox'][1]"),
        (By.XPATH, "//*[contains(normalize-space(.), 'Apply this notes')]/preceding-sibling::input[@type='checkbox'][1]"),
        (By.XPATH, "//*[contains(normalize-space(.), 'Apply this notes')]/following-sibling::input[@type='checkbox'][1]"),
        (By.XPATH, "//input[@type='checkbox']"),
    ]:
        try:
            candidate = find(driver, locator[0], locator[1], 8)
            if candidate.is_displayed() and candidate.is_enabled():
                apply_all = candidate
                break
        except Exception:
            continue

    if apply_all:
        if not apply_all.is_selected():
            try:
                apply_all.click()
            except Exception:
                js_click(driver, apply_all)
            print("  [INFO] Checked 'Apply this notes and priority to all selected Cards'")
        else:
            print("  [INFO] Checkbox already checked")
    else:
        print("  [WARN] 'Apply this notes and priority to all selected Cards' checkbox not found")

    apply_notes = None
    for locator in [
        (By.XPATH, "//button[contains(normalize-space(),'Apply Notes')]"),
        (By.XPATH, "//a[contains(normalize-space(),'Apply Notes')]"),
        (By.XPATH, "//span[contains(normalize-space(),'Apply Notes')]"),
        (By.XPATH, "//*[@id='btnApplyNotes' or contains(@id,'ApplyNotes')]"),
        (By.XPATH, "//*[contains(normalize-space(.), 'Apply Notes')]"),
    ]:
        try:
            apply_notes = clickable(driver, locator[0], locator[1], 5)
            break
        except Exception:
            continue

    assert apply_notes, "Apply Notes button not found in Attach Notes dialog"
    js_click(driver, apply_notes)
    time.sleep(PAUSE)


def submit_and_return_to_items(driver):
    submit_btn = None
    for locator in [
        (By.XPATH, "//button[normalize-space(text())='Submit']"),
        (By.XPATH, "//a[normalize-space(text())='Submit']"),
        (By.XPATH, "//span[normalize-space(text())='Submit']"),
        (By.XPATH, "//*[@id='btnSubmit' or contains(@id,'Submit')]"),
        (By.XPATH, "//input[@type='submit' and @value='Submit']"),
        (By.XPATH, "//*[contains(normalize-space(.), 'Submit')]"),
    ]:
        try:
            submit_btn = clickable(driver, locator[0], locator[1], 6)
            break
        except Exception:
            continue

    assert submit_btn, "Submit button not found on Cards page"
    js_click(driver, submit_btn)
    wait_ready(driver)
    time.sleep(PAUSE)

    back_to_items = click_text(driver, ["Back To Items", "Back to Items"])
    assert back_to_items, "Back To Items button not found"
    wait_ready(driver)
    time.sleep(PAUSE)
    assert "addnotesitems" in driver.current_url.lower() or "addnoteitems" in driver.current_url.lower(), (
        f"Expected to return to Add Notes Items page. Current URL: {driver.current_url}"
    )


@pytest.mark.usefixtures("driver")
class TestSupplierAddNotes:

    def test_01_add_notes_with_notes_only(self, driver):
        """Case 1: Apply Note dropdown value only without file attachment."""
        print("\n=== [TEST 1] Add Notes (Notes Only) ===")

        step_01_login(driver)
        step_banner(2, "Open Add Notes Items and select cards")
        select_item_and_show_cards(driver)
        select_cards(driver, count=2)

        step_banner(3, "Open Attach Notes dialog and apply the selected note")
        open_attach_notes_dialog(driver)
        choose_note_and_apply_to_all(driver)
        take_screenshot(driver, "01_applied_notes_only")

        step_banner(4, "Submit the action and return to the item list")
        submit_and_return_to_items(driver)
        take_screenshot(driver, "01_completed_notes_only")
        print("  [PASS] Completed Add Notes (Notes Only) successfully.")

    def test_02_add_notes_with_notes_and_attachment(self, driver):
        """Case 2: Upload attachment file, choose note, and submit in the same browser."""
        print("\n=== [TEST 2] Add Notes (Notes + Attachment) ===")

        step_01_login(driver)
        step_banner(2, "Open Add Notes Items and select cards")
        select_item_and_show_cards(driver)
        select_cards(driver, count=2)

        step_banner(3, "Open Attach Notes dialog and attach a file")
        open_attach_notes_dialog(driver)

        attach_remove = None
        for locator in [
            (By.XPATH, "//a[contains(normalize-space(.), 'Attach/Remove')]"),
            (By.XPATH, "//a[contains(normalize-space(.), 'Attach Remove')]"),
            (By.XPATH, "//*[contains(normalize-space(.), 'Attach/Remove')]"),
        ]:
            try:
                attach_remove = clickable(driver, locator[0], locator[1], 5)
                break
            except Exception:
                continue

        assert attach_remove, "Attach/Remove link not found in Attach Notes popup"
        js_click(driver, attach_remove)
        time.sleep(PAUSE)

        title_input = None
        for locator in [
            (By.XPATH, "//div[contains(@id,'Attach') or contains(@id,'dlg')]//input[contains(@id,'Title') or contains(@name,'Title')]"),
            (By.XPATH, "//label[contains(normalize-space(.),'Title')]/following::input[1]"),
            (By.XPATH, "//label[contains(normalize-space(.),'Title')]/following::textarea[1]"),
            (By.XPATH, "//*[@id='Title' or @name='Title']"),
            (By.ID, "Title"),
            (By.NAME, "Title"),
        ]:
            try:
                elem = find(driver, locator[0], locator[1], 5)
                if elem.is_displayed():
                    title_input = elem
                    break
            except Exception:
                continue

        if not title_input:
            candidates = driver.find_elements(By.XPATH, "//input[not(@type='hidden') and not(@type='file')] | //textarea")
            for elem in candidates:
                try:
                    if elem.is_displayed() and elem.is_enabled():
                        title_input = elem
                        break
                except Exception:
                    continue

        assert title_input, "Title field not found in Attach Files dialog"
        title_input.clear()
        title_input.send_keys("Automated Test Attachment")

        test_file_path = ensure_attachment_file()
        file_input = None
        for locator in [
            (By.XPATH, "//input[@type='file']"),
            (By.CSS_SELECTOR, "input[type='file']"),
            (By.XPATH, "//input[contains(@id,'File') or contains(@name,'File') or contains(@id,'Upload') or contains(@name,'Upload')]"),
        ]:
            try:
                file_input = find(driver, locator[0], locator[1], 8)
                break
            except Exception:
                continue

        if file_input is None:
            file_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
            if file_inputs:
                file_input = file_inputs[0]

        assert file_input, "File input not found in Attach Files dialog"
        file_input.send_keys(test_file_path)
        time.sleep(0.5)
        print(f"  [INFO] Attached file: {test_file_path}")

        upload_clicked = False
        upload_candidates = [
            (By.XPATH, "//button[contains(normalize-space(),'Upload File')]"),
            (By.XPATH, "//input[@type='button' or @type='submit'][contains(@value,'Upload File')]"),
            (By.XPATH, "//a[contains(normalize-space(),'Upload File')]"),
            (By.XPATH, "//*[contains(normalize-space(.), 'Upload File') and not(self::p)]"),
        ]

        for by, loc in upload_candidates:
            elements = driver.find_elements(by, loc)
            for el in elements:
                if el.is_displayed() and el.is_enabled():
                    try:
                        js_click(driver, el)
                        upload_clicked = True
                        break
                    except Exception:
                        continue
            if upload_clicked:
                break

        if not upload_clicked:
            upload_clicked = driver.execute_script(
                """
                var buttons = document.querySelectorAll('button, input[type="button"], input[type="submit"], a');
                for (var i = 0; i < buttons.length; i++) {
                    var text = (buttons[i].innerText || buttons[i].value || '').toLowerCase();
                    if (text.indexOf('upload file') !== -1 && buttons[i].offsetParent !== null) {
                        buttons[i].click();
                        return true;
                    }
                }
                return false;
                """
            )

        assert upload_clicked, "Failed to click the 'Upload File' button in Attach Files dialog"
        print("  [INFO] Upload File clicked successfully.")
        time.sleep(PAUSE * 2)

        done_btn = None
        for locator in [
            (By.XPATH, "//button[contains(normalize-space(),'Done')]"),
            (By.XPATH, "//a[contains(normalize-space(),'Done')]"),
            (By.XPATH, "//span[contains(normalize-space(),'Done')]"),
            (By.XPATH, "//*[contains(normalize-space(.), 'Done') and not(self::p)]"),
        ]:
            try:
                candidate = clickable(driver, locator[0], locator[1], 5)
                if candidate.is_displayed():
                    done_btn = candidate
                    break
            except Exception:
                continue

        assert done_btn, "Done button not found in Attach Files dialog"
        js_click(driver, done_btn)
        time.sleep(PAUSE)

        step_banner(4, "Select the note and submit the final update")
        choose_note_and_apply_to_all(driver)
        take_screenshot(driver, "02_applied_notes_with_attachment")
        submit_and_return_to_items(driver)
        take_screenshot(driver, "02_completed_notes_with_attachment")
        print("  [PASS] Completed Add Notes (Notes + Attachment) successfully.")
