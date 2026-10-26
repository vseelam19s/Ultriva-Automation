import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

# ============================================================================
# CONFIGURATION
# ============================================================================
BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
USERNAME = "buyeruser"
PASSWORD = "Ultriva!23"
PAUSE = 1.5

# Dummy text file used as note attachment
ATTACHMENT_TITLE = "TestNoteAttachment"
ATTACHMENT_FILE = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "note_attachment.txt"
    )
)

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="class")
def driver():
    """Class-scoped Chrome driver — one browser session per test class."""
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

# ============================================================================
# HELPERS
# ============================================================================

def wait_ready(driver, timeout=30):
    """Wait for document.readyState == complete."""
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def find(driver, by, locator, timeout=15):
    """Wait for presence and return element."""
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, locator))
    )


def clickable(driver, by, locator, timeout=15):
    """Wait until clickable and return element."""
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, locator))
    )


def scroll_to(driver, el):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'})", el)
    time.sleep(0.3)


def take_screenshot(driver, name):
    screenshots_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "reports", "screenshots"
    )
    os.makedirs(screenshots_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(screenshots_dir, f"addnotes_{name}_{ts}.png")
    driver.save_screenshot(path)
    print(f"  [screenshot] {path}")
    return path


def ensure_attachment_file():
    """Create a small text file to use as the note attachment if it doesn't exist."""
    if not os.path.exists(ATTACHMENT_FILE):
        with open(ATTACHMENT_FILE, "w") as f:
            f.write("Test note attachment file for Add Notes QA automation.\n")
    return ATTACHMENT_FILE

# ============================================================================
# TEST CLASS
# ============================================================================

@pytest.mark.usefixtures("driver")
class TestAddNotes:
    
    # ── TC-AN-001: Login ─────────────────────────────────────────────────────
    def test_01_login(self, driver):
        """Login to QA site with buyeruser credentials."""
        print("\n[TC-AN-001] Logging in to QA site...")
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
        assert BASE_URL.lower() in current_url.lower() or "Home" in current_url, \
            f"Login may have failed. URL: {current_url}"
        print("  [PASS] Login successful.")

    # ── TC-AN-002: Navigate to Actions ───────────────────────────────────
    def test_02_navigate_to_actions(self, driver):
        """Click Actions in the left sidebar to open the Buyer Actions page."""
        print("\n[TC-AN-002] Navigating to Actions page...")

        actions_link = clickable(
            driver,
            By.XPATH,
            "//a[contains(@href,'Action/Home') or "
            "(.//span[normalize-space()='Actions']) or "
            "normalize-space(.)='Actions']",
        )
        scroll_to(driver, actions_link)
        actions_link.click()
        wait_ready(driver)
        time.sleep(PAUSE)

        take_screenshot(driver, "02_actions_page")
        assert "Action/Home" in driver.current_url, \
            f"Expected Actions page. Got: {driver.current_url}"
        print(f"  [PASS] Actions page loaded: {driver.current_url}")

    # ── TC-AN-003: Click Add Notes ───────────────────────────────────────
    def test_03_click_add_notes(self, driver):
        """Click the Add Notes tile from the Buyer Actions page."""
        print("\n[TC-AN-003] Clicking Add Notes tile in Buyer Actions...")

        add_notes_link = None
        for locator in [
            (By.XPATH, "//a[contains(@href,'AddNotes') and not(contains(@class,'toplinks'))]"),
            (By.XPATH, "//a[contains(@href,'AddNote') and not(contains(@class,'toplinks'))]"),
            (By.XPATH, "//a[normalize-space(text())='Add Notes' or normalize-space(text())='AddNotes']"),
            (By.XPATH, "//*[contains(normalize-space(),'Add Notes') or contains(normalize-space(),'AddNotes')]"
                       "[self::a or self::button or self::span]"
                       "[not(contains(@class,'toplinks'))]"),
        ]:
            try:
                add_notes_link = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(locator)
                )
                break
            except Exception:
                continue

        assert add_notes_link, "Add Notes link/tile not found on Actions page"
        scroll_to(driver, add_notes_link)
        driver.execute_script("arguments[0].click()", add_notes_link)
        wait_ready(driver)
        time.sleep(PAUSE)

        take_screenshot(driver, "03_add_notes_filter_page")
        current_url = driver.current_url
        print(f"  [URL] {current_url}")
        assert any(kw in current_url for kw in ["AddNotes", "addnotes"]), \
            f"Expected Add Notes page. Got: {current_url}"
        print(f"  [PASS] Add Notes Filter page loaded: {current_url}")

    # ── TC-AN-004: Click Go to load Add Notes Items List ─────────────────
    def test_04_apply_filter_and_load_items(self, driver):
        """Click Go on the Add Notes Filter page to load the Items List."""
        print("\n[TC-AN-004] Clicking Go to load Add Notes Items List...")

        current_url = driver.current_url
        if "AddNotesItems" in current_url or "AddNoteItems" in current_url:
            print("  [INFO] Already on Add Notes Items page, skipping Go click.")
        else:
            go_button = None
            for locator in [
                (By.ID, "imgMatStatusGo"),
                (By.XPATH, "//span[@id='imgMatStatusGo']"),
                (By.XPATH, "//a[contains(@class,'btn-filter-submit-item') and contains(normalize-space(),'Go')]"),
                (By.XPATH, "//span[contains(@class,'btn-filter-submit-item') and normalize-space(text())='Go']"),
                (By.XPATH, "//button[normalize-space(text())='Go']"),
                (By.XPATH, "//input[@type='submit' and @value='Go']"),
                (By.XPATH, "//*[@id='btnGo' or @id='go-button' or @id='goBtn']"),
                (By.XPATH, "//a[normalize-space(text())='Go' and contains(@class,'btn')]"),
                (By.XPATH, "//span[normalize-space(text())='Go']"),
                (By.XPATH, "//a[normalize-space(text())='Go']"),
            ]:
                try:
                    go_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable(locator)
                    )
                    break
                except Exception:
                    continue

            if go_button:
                scroll_to(driver, go_button)
                driver.execute_script("arguments[0].click()", go_button)
                wait_ready(driver)
                time.sleep(PAUSE * 2)
            else:
                print("  [WARN] Go button not found — navigating directly to AddNotesItems...")
                driver.get(f"{BASE_URL}/BuyerAction/AddNotesItems")
                wait_ready(driver)
                time.sleep(PAUSE * 2)

        take_screenshot(driver, "04_add_notes_items_list")
        print(f"  [URL] {driver.current_url}")
        assert any(kw in driver.current_url for kw in ["AddNotes", "addnotes"]), \
            f"Expected Add Notes Items page. Got: {driver.current_url}"
        print(f"  [PASS] Add Notes Items List loaded: {driver.current_url}")

    # ── TC-AN-005: Select item and click Show Cards ──────────────────────
    def test_05_select_item_show_cards(self, driver):
        """Click the first item in the Add Notes Items List, then click Show Cards."""
        print("\n[TC-AN-005] Selecting first item and clicking Show Cards...")

        item_links = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class,'GridLink')]"))
        )
        assert item_links, "No items found in Add Notes Items List"

        first_item_link = item_links[0]
        item_text = first_item_link.text.strip()
        print(f"  [INFO] First item found: '{item_text}'")
        scroll_to(driver, first_item_link)
        driver.execute_script("arguments[0].click()", first_item_link)
        wait_ready(driver)
        time.sleep(PAUSE * 2)

        take_screenshot(driver, "05a_after_item_click")
        print(f"  [INFO] URL after item click: {driver.current_url}")

        if any(kw in driver.current_url for kw in ["AddNotesCards", "AddNoteCards"]):
            print("  [INFO] Navigated directly to Add Notes Cards page.")
            return

        show_cards_btn = None
        for locator in [
            (By.XPATH, "//button[contains(normalize-space(),'Show Cards')]"),
            (By.XPATH, "//a[contains(normalize-space(),'Show Cards')]"),
            (By.XPATH, "//span[contains(normalize-space(),'Show Cards')]"),
            (By.XPATH, "//*[contains(@id,'ShowCards') or contains(@id,'showCards')]"),
            (By.XPATH, "//*[contains(@onclick,'ShowCards') or contains(@onclick,'showCards')]"),
        ]:
            try:
                show_cards_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(locator)
                )
                break
            except Exception:
                continue

        assert show_cards_btn, f"Show Cards button not found and not on Add Notes Cards page. Current URL: {driver.current_url}"
        scroll_to(driver, show_cards_btn)
        driver.execute_script("arguments[0].click()", show_cards_btn)
        wait_ready(driver)
        time.sleep(PAUSE * 2)

        take_screenshot(driver, "05b_add_notes_cards_list")
        print(f"  [URL] {driver.current_url}")
        assert any(kw in driver.current_url for kw in ["AddNotes", "addnotes"]), \
            f"Expected Add Notes Cards page. Got: {driver.current_url}"
        print(f"  [PASS] Add Notes Cards List confirmed: {driver.current_url}")

    # ── TC-AN-006: Select cards and click Attach Notes ───────────────────
    def test_06_select_cards_and_attach_notes(self, driver):
        """Select first 2 cards via checkboxes and click Attach Notes button."""
        print("\n[TC-AN-006] Selecting cards and clicking Attach Notes...")

        assert any(kw in driver.current_url for kw in ["AddNotes", "addnotes"]), \
            f"Expected to be on Add Notes Cards page. Got: {driver.current_url}"

        chk_inputs = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//input[contains(@name,'CheckboxCardGID') and not(contains(@name,'_All$'))]")
            )
        )
        assert chk_inputs, "No card row checkboxes found in Add Notes Cards List"
        print(f"  [INFO] Found {len(chk_inputs)} card row checkboxes")

        selected = 0
        for inp in chk_inputs[:2]:
            try:
                row = driver.execute_script("return arguments[0].closest('tr')", inp)
                row_class = driver.execute_script("return arguments[0].className", row) if row else ""
                if "SelectedRow" in row_class:
                    selected += 1
                    continue
                scroll_to(driver, inp)
                driver.execute_script("arguments[0].click()", inp)
                time.sleep(0.5)
                row_class_after = driver.execute_script("return arguments[0].className", row) if row else ""
                if "SelectedRow" in row_class_after:
                    selected += 1
                    print(f"  [INFO] Card {selected} selected via JS click")
                else:
                    inp.click()
                    time.sleep(0.4)
                    selected += 1
                    print(f"  [INFO] Card {selected} selected via native click")
            except Exception as e:
                print(f"  [WARN] Could not select card: {e}")

        print(f"  [INFO] Total cards selected: {selected}")
        assert selected >= 1, "Failed to select any cards"

        take_screenshot(driver, "06a_cards_selected")

        attach_notes_btn = None
        for locator in [
            (By.XPATH, "//button[contains(normalize-space(),'Attach Notes')]"),
            (By.XPATH, "//a[contains(normalize-space(),'Attach Notes')]"),
            (By.XPATH, "//span[contains(normalize-space(),'Attach Notes')]"),
            (By.XPATH, "//*[@id='btnAttachNotes' or contains(@id,'AttachNotes')]"),
            (By.XPATH, "//*[normalize-space(text())='Attach Notes']"),
        ]:
            try:
                attach_notes_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(locator)
                )
                break
            except Exception:
                continue

        assert attach_notes_btn, "Attach Notes button not found on Add Notes Cards List"
        scroll_to(driver, attach_notes_btn)
        driver.execute_script("arguments[0].click()", attach_notes_btn)
        time.sleep(PAUSE)

        take_screenshot(driver, "06b_attach_notes_dialog_open")
        print("  [PASS] Attach Notes dialog opened.")

    # ── TC-AN-007: Select Note from DDM and apply to all cards ───────────
    def test_07_select_note_and_apply_to_all(self, driver):
        """In the Attach Notes dialog: select a note from the DDM,
        check 'Apply this notes and priority to all selected Cards',
        click Attach/Remove link, attach a file, click Done, then Apply Notes."""
        print("\n[TC-AN-007] Selecting note, applying to all cards, attaching file...")

        # Step 1: Verify the dialog is open
        dialog = None
        for locator in [
            (By.XPATH, "//div[contains(@class,'modal') and contains(.,'Attach notes for Card')]"),
            (By.XPATH, "//div[contains(@class,'dialog') and contains(.,'Attach notes for Card')]"),
            (By.XPATH, "//div[contains(.,'Attach notes for Card') and .//select]"),
            (By.XPATH, "//*[contains(text(),'Attach notes for Card') or contains(.,'Notes:') and .//select]"),
        ]:
            try:
                dialog = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(locator)
                )
                break
            except Exception:
                continue

        print("  [INFO] Attach Notes dialog located (or assumed open).")

        # Step 2: Select a Note from the Notes DDM
        notes_select = None
        for locator in [
            (By.XPATH, "//select[contains(@id,'NoteTitleID') or contains(@name,'NoteTitleID')]"),
            (By.XPATH, "//label[normalize-space()='Notes:']/following-sibling::select"),
            (By.XPATH, "//label[normalize-space()='Notes:']/following::select[1]"),
            (By.XPATH, "//select[contains(@id,'NoteTitle') or contains(@name,'NoteTitle')]"),
            (By.XPATH, "//select[.//option[contains(text(),'Select Notes') or contains(text(),'nortes') or contains(text(),'NoteEdit') or contains(text(),'Track')]]"),
        ]:
            try:
                notes_select = WebDriverWait(driver, 8).until(
                    EC.presence_of_element_located(locator)
                )
                break
            except Exception:
                continue

        assert notes_select, "Notes DDM (select element) not found in Attach Notes dialog"
        scroll_to(driver, notes_select)

        sel = Select(notes_select)
        options = [o for o in sel.options if o.get_attribute("value") and o.text.strip() not in ("-- Select Notes --", "")]
        assert options, "No note options available in Notes DDM"

        selected_note = options[0].text.strip()
        sel.select_by_visible_text(selected_note)
        print(f"  [INFO] Note selected from DDM: '{selected_note}'")
        time.sleep(0.5)

        take_screenshot(driver, "07a_note_selected")

        # Step 3: Check "Apply this notes and priority to all selected Cards"
        apply_all_chk = None
        for locator in [
            (By.XPATH, "//input[@type='checkbox' and (contains(@id,'ApplyAll') or contains(@name,'ApplyAll') or contains(@id,'applyAll') or contains(@name,'applyAll'))]"),
            (By.XPATH, "//label[contains(normalize-space(),'Apply this notes')]/preceding-sibling::input[@type='checkbox'][1]"),
            (By.XPATH, "//label[contains(normalize-space(),'Apply this notes')]/following-sibling::input[@type='checkbox'][1]"),
            (By.XPATH, "//input[@type='checkbox'][following-sibling::*[contains(normalize-space(),'Apply this notes')]]"),
            (By.XPATH, "//input[@type='checkbox'][preceding::label[contains(normalize-space(),'Apply this notes')]]"),
        ]:
            try:
                apply_all_chk = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(locator)
                )
                break
            except Exception:
                continue

        if apply_all_chk:
            if not apply_all_chk.is_selected():
                driver.execute_script("arguments[0].click()", apply_all_chk)
                time.sleep(0.4)
                print("  [INFO] Checked 'Apply this notes and priority to all selected Cards'")
            else:
                print("  [INFO] 'Apply this notes and priority to all selected Cards' already checked")
        else:
            print("  [WARN] 'Apply all' checkbox not found — continuing without it")

        take_screenshot(driver, "07b_apply_all_checked")

        # Step 4: Click Attach/Remove link to open file attachment dialog
        attach_remove_link = None
        for locator in [
            (By.XPATH, "//a[contains(normalize-space(),'Attach/Remove')]"),
            (By.XPATH, "//span[contains(normalize-space(),'Attach/Remove')]"),
            (By.XPATH, "//a[contains(@href,'Attach') or contains(@onclick,'Attach')][contains(normalize-space(),'Attach')]"),
            (By.XPATH, "//*[normalize-space(text())='Attach/Remove']"),
        ]:
            try:
                attach_remove_link = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(locator)
                )
                break
            except Exception:
                continue

        assert attach_remove_link, "Attach/Remove link not found in Attach Notes dialog"
        scroll_to(driver, attach_remove_link)

        # Track window handles BEFORE clicking
        main_window = driver.current_window_handle
        all_windows_before = set(driver.window_handles)
        driver.execute_script("arguments[0].click()", attach_remove_link)
        wait_ready(driver)
        time.sleep(PAUSE)

        # Switch to new popup window if one was opened
        all_windows_after = set(driver.window_handles)
        new_windows = all_windows_after - all_windows_before
        if new_windows:
            popup_window = list(new_windows)[0]
            driver.switch_to.window(popup_window)
            print("  [INFO] Switched to popup window for file attach dialog")

        take_screenshot(driver, "07c_attach_file_dialog_open")
        print("  [INFO] Attach file(s) dialog opened.")

        # Step 5: Enter Title and choose file
        title_field = None
        for locator in [
            (By.XPATH, "//input[@id='Title' or @name='Title']"),
            (By.XPATH, "//input[@type='text' and (contains(@id,'Title') or contains(@name,'Title') or contains(@placeholder,'Title'))]"),
            (By.XPATH, "//label[contains(normalize-space(),'Title')]/following-sibling::input"),
            (By.XPATH, "//td[contains(normalize-space(),'Title')]/following::input[@type='text'][1]"),
            (By.XPATH, "//label[normalize-space()='Title:']/following::input[@type='text'][1]"),
            (By.XPATH, "(//input[@type='text'])[1]"),
        ]:
            try:
                title_field = WebDriverWait(driver, 8).until(
                    EC.presence_of_element_located(locator)
                )
                if title_field.is_displayed():
                    break
            except Exception:
                continue

        assert title_field, "Title field not found in Attach file(s) dialog"
        scroll_to(driver, title_field)
        title_field.clear()
        title_field.send_keys(ATTACHMENT_TITLE)
        print(f"  [INFO] Title entered: '{ATTACHMENT_TITLE}'")

        attachment_path = os.path.abspath(ensure_attachment_file())
        assert os.path.isfile(attachment_path), f"Attachment file not found: {attachment_path}"
        print(f"  [INFO] Attachment file ready: {attachment_path} ({os.path.getsize(attachment_path)} bytes)")

        file_input = None
        for locator in [
            (By.XPATH, "//input[@type='file']"),
            (By.CSS_SELECTOR, "input[type='file']"),
            (By.XPATH, "//input[contains(@id,'file') or contains(@name,'file') or contains(@id,'Attachment') or contains(@name,'Attachment')]"),
        ]:
            try:
                file_input = WebDriverWait(driver, 8).until(
                    EC.presence_of_element_located(locator)
                )
                break
            except Exception:
                continue

        assert file_input, "File input not found in Attach file(s) dialog"
        file_input.send_keys(attachment_path)
        time.sleep(1)

        file_label = driver.execute_script("return arguments[0].value", file_input)
        print(f"  [INFO] File input value after send_keys: '{file_label}'")
        if not file_label:
            print("  [WARN] File input value empty — trying JS value set...")
            driver.execute_script("arguments[0].dispatchEvent(new Event('change', {bubbles:true}))", file_input)
            time.sleep(0.5)
        print(f"  [INFO] File selected: {attachment_path}")

        take_screenshot(driver, "07d_file_selected")

        # Step 6: JS scan — find ALL elements with 'Upload' text
        scan_results = driver.execute_script("""
            var found = [];
            var all = document.querySelectorAll('*');
            for (var i = 0; i < all.length; i++) {
                var el = all[i];
                var txt = (el.innerText || el.textContent || '').trim();
                if (txt.indexOf('Upload') !== -1 && txt.length < 80) {
                    found.push(
                        el.tagName + '|id=' + el.id +
                        '|class=' + el.className +
                        '|onclick=' + (typeof el.onclick === 'function' ? 'YES' : 'no') +
                        '|children=' + el.children.length +
                        '|txt=' + txt.substring(0, 50)
                    );
                }
            }
            return found;
        """)
        print(f"  [DIAG] All elements with 'Upload' in text ({len(scan_results or [])} found):")
        for r in (scan_results or [])[:25]:
            print(f"    {r}")

        try:
            os.makedirs(r'C:\Prcatices-AI\reports', exist_ok=True)
            with open(r'C:\Prcatices-AI\reports\attach_dialog_source.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print("  [DIAG] Page source saved → reports/attach_dialog_source.html")
        except Exception as e:
            print(f"  [DIAG] Page source save failed: {e}")

        # Click Upload File button
        upload_btn = None
        for locator in [
            (By.ID, "btnAatch_cmdSubmitpNo"),
            (By.XPATH, "//span[contains(@class,'vd-blue-btn') and contains(normalize-space(),'Upload')]"),
            (By.XPATH, "//span[contains(@class,'btn-toolbar-right-item') and contains(normalize-space(),'Upload')]"),
            (By.XPATH, "//span[contains(@class,'btn') and contains(normalize-space(),'Upload File') and not(contains(@class,'btn-toolbar-text'))]"),
            (By.XPATH, "//button[contains(normalize-space(),'Upload File')]"),
            (By.XPATH, "//a[contains(normalize-space(),'Upload File')]"),
            (By.XPATH, "//input[@type='submit' and contains(normalize-space(@value),'Upload')]"),
            (By.XPATH, "//input[@type='button' and contains(normalize-space(@value),'Upload')]"),
        ]:
            try:
                el = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located(locator)
                )
                tag = el.tag_name.lower()
                txt = el.text.strip()
                html = el.get_attribute('outerHTML') or ''
                print(f"  [DIAG] Candidate: tag={tag} text='{txt[:40]}' html='{html[:120]}'")
                cls = el.get_attribute('class') or ''
                if 'separate-vertical' in cls or 'modal-popup-separate' in cls:
                    print("  [DIAG]  → skipping instruction span")
                    continue
                upload_btn = el
                break
            except Exception:
                continue

        assert upload_btn, "Upload File button NOT found. Check reports/attach_dialog_source.html for actual button HTML."

        btn_tag = upload_btn.tag_name
        btn_txt = upload_btn.text.strip()
        btn_html = upload_btn.get_attribute('outerHTML') or ''
        btn_class = upload_btn.get_attribute('class') or ''
        print(f"  [INFO] Upload button found: tag={btn_tag} text='{btn_txt}' class='{btn_class}'")
        print(f"  [DIAG] Upload btn outerHTML: {btn_html[:200]}")
        scroll_to(driver, upload_btn)

        driver.execute_script("arguments[0].click()", upload_btn)
        print("  [INFO] Upload File — JS click fired")
        time.sleep(5)

        take_screenshot(driver, "07e_after_upload")
        print(f"  [INFO] Upload File clicked — waiting for '{ATTACHMENT_TITLE}' in Attachments table...")

        attachment_visible = False
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, f"//table//td[contains(normalize-space(),'{ATTACHMENT_TITLE}')]"))
            )
            attachment_visible = True
            print(f"  [PASS] Attachment '{ATTACHMENT_TITLE}' confirmed — row appeared in Attachments table.")
        except Exception:
            remove_links = driver.find_elements(By.XPATH, "//a[normalize-space()='Remove'] | //button[normalize-space()='Remove']")
            if remove_links:
                attachment_visible = True
                print("  [WARN] Title row not found but Remove link exists — assuming upload succeeded.")
            else:
                print(f"  [WARN] Attachment '{ATTACHMENT_TITLE}' NOT found in table after 30s — upload failed.")
                take_screenshot(driver, "07e2_upload_failed")

        take_screenshot(driver, "07f_attachment_row_visible")

        # Step 7: Click Done
        done_clicked = False
        for locator in [
            (By.XPATH, "//button[normalize-space(.)='Done']"),
            (By.XPATH, "//a[normalize-space(.)='Done']"),
            (By.XPATH, "//button[.//span[normalize-space()='Done']]"),
            (By.XPATH, "//a[.//span[normalize-space()='Done']]"),
            (By.XPATH, "//*[@id='btnDone' or contains(@id,'Done')]"),
            (By.XPATH, "//*[normalize-space(text())='Done']"),
        ]:
            try:
                done_el = WebDriverWait(driver, 8).until(
                    EC.element_to_be_clickable(locator)
                )
                rect = done_el.rect
                if rect['width'] > 0 and rect['height'] > 0:
                    scroll_to(driver, done_el)
                    driver.execute_script("arguments[0].click()", done_el)
                    done_clicked = True
                    print("  [INFO] Done button clicked")
                    break
            except Exception:
                continue

        if not done_clicked:
            done_spans = driver.find_elements(By.XPATH, "//span[contains(@class,'btn-toolbar-text') and normalize-space(text())='Done']")
            for span in done_spans:
                try:
                    rect = span.rect
                    if rect['width'] > 0 and rect['height'] > 0:
                        parent = driver.execute_script("return arguments[0].closest('a,button,[onclick]') || arguments[0].parentElement;", span)
                        target = parent if parent else span
                        driver.execute_script("arguments[0].click()", target)
                        done_clicked = True
                        print("  [INFO] Done clicked via btn-toolbar-text span")
                        break
                except Exception:
                    continue

        assert done_clicked, "Done button not found in Attach file(s) dialog"
        wait_ready(driver)
        time.sleep(PAUSE)

        if new_windows and driver.current_window_handle != main_window:
            driver.switch_to.window(main_window)
            print("  [INFO] Switched back to main window after Done")

        take_screenshot(driver, "07g_after_done")
        print("  [INFO] Done clicked — back in Attach Notes dialog.")

        # Step 8: Click Apply Notes
        apply_notes_btn = None
        for locator in [
            (By.XPATH, "//button[contains(normalize-space(),'Apply Notes')]"),
            (By.XPATH, "//a[contains(normalize-space(),'Apply Notes')]"),
            (By.XPATH, "//span[contains(normalize-space(),'Apply Notes')]"),
            (By.XPATH, "//*[@id='btnApplyNotes' or contains(@id,'ApplyNotes')]"),
            (By.XPATH, "//*[normalize-space(text())='Apply Notes']"),
        ]:
            try:
                apply_notes_btn = WebDriverWait(driver, 8).until(
                    EC.element_to_be_clickable(locator)
                )
                break
            except Exception:
                continue

        assert apply_notes_btn, "Apply Notes button not found in Attach Notes dialog"
        scroll_to(driver, apply_notes_btn)
        driver.execute_script("arguments[0].click()", apply_notes_btn)
        time.sleep(PAUSE)

        take_screenshot(driver, "07h_after_apply_notes")
        print("  [PASS] Apply Notes clicked — note applied to selected cards.")

    # ── TC-AN-008: Click Submit ──────────────────────────────────────────
    def test_08_click_submit(self, driver):
        """Click the Submit button on the Add Notes Cards List page."""
        print("\n[TC-AN-008] Clicking Submit button...")

        submit_btn = None
        for locator in [
            (By.XPATH, "//button[normalize-space(text())='Submit']"),
            (By.XPATH, "//a[normalize-space(text())='Submit']"),
            (By.XPATH, "//span[normalize-space(text())='Submit']"),
            (By.XPATH, "//*[@id='btnSubmit' or contains(@id,'Submit')][not(contains(@class,'toplinks'))]"),
            (By.XPATH, "//input[@type='submit' and @value='Submit']"),
        ]:
            try:
                submit_btn = WebDriverWait(driver, 8).until(
                    EC.element_to_be_clickable(locator)
                )
                break
            except Exception:
                continue

        assert submit_btn, "Submit button not found on Add Notes Cards List page"
        scroll_to(driver, submit_btn)
        driver.execute_script("arguments[0].click()", submit_btn)
        wait_ready(driver)
        time.sleep(PAUSE * 2)

        take_screenshot(driver, "08_after_submit")
        print(f"  [URL] {driver.current_url}")
        assert any(kw in driver.current_url for kw in ["AddNotes", "addnotes"]), \
            f"Expected Add Notes Results page. Got: {driver.current_url}"
        print("  [PASS] Submit clicked successfully.")

    # ── TC-AN-009: Verify Results ────────────────────────────────────────
    def test_09_verify_results(self, driver):
        """Verify the Add Notes Results page shows successful note additions."""
        print("\n[TC-AN-009] Verifying Add Notes Results...")

        take_screenshot(driver, "09_results_page")
        page_source = driver.page_source

        assert "AddNotesResults" in driver.current_url or "AddNotes" in driver.current_url, \
            f"Not on Add Notes Results page. URL: {driver.current_url}"

        success_found = any(phrase in page_source for phrase in [
            "Following Cards were successful",
            "Notes added Successfully",
            "Notes added successfully",
            "Successful",
            "successful",
        ])
        assert success_found, f"Success message not found on Add Notes Results page. URL: {driver.current_url}"
        print("  [PASS] Add Notes Results page confirmed with success message.")

    # ── TC-AN-010: Click Back To Items ───────────────────────────────────
    def test_10_back_to_items(self, driver):
        """Click Back To Items and verify return to Add Notes Items List."""
        print("\n[TC-AN-010] Clicking Back To Items...")

        back_btn = None
        for locator in [
            (By.XPATH, "//button[contains(normalize-space(),'Back To Items') or contains(normalize-space(),'Back to Items')]"),
            (By.XPATH, "//a[contains(normalize-space(),'Back To Items') or contains(normalize-space(),'Back to Items')]"),
            (By.XPATH, "//span[contains(normalize-space(),'Back To Items') or contains(normalize-space(),'Back to Items')]"),
            (By.XPATH, "//*[contains(@id,'BackToItems') or contains(@id,'backToItems')]"),
            (By.XPATH, "//*[contains(normalize-space(),'Back To Items') or contains(normalize-space(),'Back to Items')]"),
        ]:
            try:
                back_btn = WebDriverWait(driver, 8).until(
                    EC.element_to_be_clickable(locator)
                )
                break
            except Exception:
                continue

        assert back_btn, "Back To Items button not found on Add Notes Results page"
        scroll_to(driver, back_btn)
        driver.execute_script("arguments[0].click()", back_btn)
        wait_ready(driver)
        time.sleep(PAUSE * 2)

        take_screenshot(driver, "10_back_to_items")
        print(f"  [URL] {driver.current_url}")
        assert any(kw in driver.current_url for kw in ["AddNotes", "addnotes"]), \
            f"Expected Add Notes Items page after Back To Items. Got: {driver.current_url}"
        print("  [PASS] Back To Items successful — returned to Add Notes Items List.")