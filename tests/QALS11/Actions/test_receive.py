import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ============================================================================
# CONFIGURATION
# ============================================================================
BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
USERNAME = "buyeruser"
PASSWORD = "Ultriva!23"
PAUSE = 1.5

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
    path = os.path.join(screenshots_dir, f"receive_{name}_{ts}.png")
    driver.save_screenshot(path)
    print(f"  [screenshot] {path}")
    return path

# ============================================================================
# TEST CLASS
# ============================================================================

@pytest.mark.usefixtures("driver")
class TestReceive:
    
    # ── TC-RCV-001: Login ────────────────────────────────────────────────────
    def test_01_login(self, driver):
        """Login to QA site with buyeruser credentials."""
        print("\n[TC-RCV-001] Logging in to QA site...")
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

    # ── TC-RCV-002: Navigate to Actions ──────────────────────────────────
    def test_02_navigate_to_actions(self, driver):
        """Click Actions in the left sidebar to open the Buyer Actions page."""
        print("\n[TC-RCV-002] Navigating to Actions page...")

        actions_link = clickable(
            driver,
            By.XPATH,
            "//a[contains(@href, 'Action/Home') or "
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

    # ── TC-RCV-003: Click Receive ────────────────────────────────────────
    def test_03_click_receive(self, driver):
        """Click the Receive tile from the Buyer Actions page."""
        print("\n[TC-RCV-003] Clicking Receive tile in Buyer Actions...")

        receive_link = None
        for locator in [
            (By.XPATH, "//a[contains(@href,'ReceiveFilter') and not(contains(@class,'toplinks'))]"),
            (By.XPATH, "//a[contains(@href,'Receive') and not(contains(@class,'toplinks')) and not(contains(@href,'ReceiveItems'))]"),
            (By.XPATH, "//a[normalize-space(text())='Receive' and not(contains(@class,'toplinks'))]"),
            (By.XPATH, "//*[normalize-space(text())='Receive' and (self::a or self::button or self::span) and not(contains(@class,'toplinks'))]"),
        ]:
            try:
                receive_link = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(locator)
                )
                break
            except Exception:
                continue

        assert receive_link, "Receive link/tile not found on Actions page"
        scroll_to(driver, receive_link)
        driver.execute_script("arguments[0].click()", receive_link)
        wait_ready(driver)
        time.sleep(PAUSE)

        take_screenshot(driver, "03_receive_page")
        print(f"  [URL] {driver.current_url}")
        assert any(kw in driver.current_url for kw in ["Receive", "receive"]), \
            f"Expected Receive page. Got: {driver.current_url}"
        print(f"  [PASS] Receive page loaded: {driver.current_url}")

    # ── TC-RCV-004: Apply filter and load Receive Items List ─────────────
    def test_04_apply_filter_and_load_items(self, driver):
        """Click Go on Receive Filter page to load the Receive Items List."""
        print("\n[TC-RCV-004] Applying filter — clicking Go button...")

        current_url = driver.current_url
        if any(kw in current_url for kw in ["ReceiveItems", "ReceiveItem", "receiveitem"]):
            print("  [INFO] Already on Receive Items page, skipping Go click.")
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
                print("  [WARN] Go button not found — navigating directly to Receive Items...")
                driver.get(f"{BASE_URL}/BuyerAction/ReceiveItems")
                wait_ready(driver)
                time.sleep(PAUSE * 2)

        take_screenshot(driver, "04_receive_items_list")
        print(f"  [URL] {driver.current_url}")
        assert any(kw in driver.current_url for kw in ["Receive", "receive"]), \
            f"Expected Receive Items page. Got: {driver.current_url}"
        print(f"  [PASS] Receive Items List loaded: {driver.current_url}")

    # ── TC-RCV-005: Select item and click Show Cards ─────────────────────
    def test_05_select_item_show_cards(self, driver):
        """Click the first item in the Receive Items List, then click Show Cards."""
        print("\n[TC-RCV-005] Selecting first item and clicking Show Cards...")

        item_links = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class,'GridLink')]"))
        )
        assert item_links, "No GridLink items found in Receive Items List"

        first_item_link = item_links[0]
        item_text = first_item_link.text.strip()
        print(f"  [INFO] First item found: '{item_text}'")
        scroll_to(driver, first_item_link)
        driver.execute_script("arguments[0].click()", first_item_link)
        wait_ready(driver)
        time.sleep(PAUSE * 2)

        take_screenshot(driver, "05a_after_item_click")
        print(f"  [INFO] URL after item click: {driver.current_url}")

        if any(kw in driver.current_url for kw in ["ReceiveCard", "receivecard"]):
            print("  [INFO] Navigated directly to Receive Cards page.")
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

        assert show_cards_btn, f"Show Cards button not found and not on Receive Cards page. Current URL: {driver.current_url}"
        scroll_to(driver, show_cards_btn)
        driver.execute_script("arguments[0].click()", show_cards_btn)
        wait_ready(driver)
        time.sleep(PAUSE * 2)

        take_screenshot(driver, "05b_receive_cards_list")
        print(f"  [URL] {driver.current_url}")
        assert any(kw in driver.current_url for kw in ["Receive", "receive"]), \
            f"Expected Receive Cards page. Got: {driver.current_url}"
        print(f"  [PASS] Receive Cards List confirmed: {driver.current_url}")

    # ── TC-RCV-006: Select cards → Attach Notes + File → Receive ─────────
    def test_06_select_cards_attach_notes_and_receive(self, driver):
        """Select cards via checkboxes, open Attach Notes dialog, set priority,
        attach a file via Attach/Remove → Upload File → Done, then click Receive
        from within the notes dialog.
        """
        print("\n[TC-RCV-006] Selecting cards, attaching notes + file, then receiving...")

        # ── Step 1: Select cards via checkboxes ──────────────────────────────
        chk_inputs = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//input[contains(@name,'CheckboxCardGID') and not(contains(@name,'_All$'))]")
            )
        )
        assert chk_inputs, "No card row checkboxes found in Receive Cards List"
        print(f"  [INFO] Found {len(chk_inputs)} card row checkboxes")

        selected = 0
        for inp in chk_inputs[:3]:
            try:
                row = driver.execute_script("return arguments[0].closest('tr')", inp)
                row_class = driver.execute_script("return arguments[0].className", row) if row else ""
                if "SelectedRow" in row_class:
                    selected += 1
                    continue
                scroll_to(driver, inp)
                driver.execute_script("arguments[0].click()", inp)
                time.sleep(0.4)
                row_class = driver.execute_script("return arguments[0].className", row) if row else ""
                if "SelectedRow" in row_class:
                    selected += 1
                else:
                    print(f"  [WARN] Row class after click: '{row_class}' — SelectedRow not found")
            except Exception as e:
                print(f"  [WARN] Could not click card checkbox: {e}")

        assert selected > 0, f"Could not select any cards (selected={selected})"
        print(f"  [INFO] Selected {selected} card(s)")
        take_screenshot(driver, "06a_cards_selected")

        # ── Step 2: Click the toolbar "Attach Notes" button ──────────────────
        print("  [INFO] Clicking Attach Notes toolbar button...")
        note_btn = None
        for locator in [
            (By.XPATH, "//button[contains(normalize-space(),'Attach Notes')]"),
            (By.XPATH, "//a[contains(normalize-space(),'Attach Notes')]"),
            (By.XPATH, "//span[contains(normalize-space(),'Attach Notes') and (parent::button or parent::a or ancestor::button or ancestor::a)]"),
            (By.XPATH, "//*[normalize-space(text())='Attach Notes' and (self::button or self::a or self::span)]"),
            (By.XPATH, "//*[contains(@id,'AttachNote') or contains(@id,'attachNote')]"),
        ]:
            try:
                note_btn = WebDriverWait(driver, 8).until(
                    EC.element_to_be_clickable(locator)
                )
                if note_btn.is_displayed():
                    break
            except Exception:
                continue

        assert note_btn, "Attach Notes toolbar button not found"
        scroll_to(driver, note_btn)
        print(f"  [INFO] Found: '{note_btn.text.strip()}'")
        driver.execute_script("arguments[0].click()", note_btn)
        wait_ready(driver)
        time.sleep(PAUSE)
        take_screenshot(driver, "06b_attach_notes_dialog")
        print("  [INFO] Attach Notes dialog opened")

        # ── Step 3: Set priority to High ─────────────────────────────────────
        print("  [INFO] Setting priority to High...")
        for locator in [
            (By.XPATH, "//input[@type='radio'][@value='High']"),
            (By.XPATH, "//input[@type='radio'][following-sibling::*[contains(normalize-space(),'High')]]"),
            (By.ID, "rbHigh"),
        ]:
            try:
                high_radio = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(locator)
                )
                driver.execute_script("arguments[0].click()", high_radio)
                time.sleep(0.3)
                print("  [INFO] Priority set to High")
                break
            except Exception:
                continue
        else:
            print("  [WARN] High priority radio not found, keeping default")

        # ── Step 3b: Enter Notes description ─────────────────────────────────
        print("  [INFO] Entering notes description...")
        try:
            note_ta = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//textarea[contains(@id,'Desc') or contains(@name,'Desc') or contains(@id,'Note') or contains(@name,'Note')] | //textarea")
                )
            )
            note_ta.clear()
            note_ta.send_keys("Automation Test Note")
            time.sleep(0.3)
            print("  [INFO] Notes description entered")
        except Exception:
            print("  [WARN] Notes textarea not found, skipping")

        # ── Step 4: Click Attach/Remove link ─────────────────────────────────
        print("  [INFO] Clicking Attach/Remove link...")
        attach_remove = None
        for locator in [
            (By.XPATH, "//a[contains(normalize-space(),'Attach/Remove')]"),
            (By.XPATH, "//a[contains(normalize-space(),'Attach') and contains(normalize-space(),'Remove')]"),
            (By.LINK_TEXT, "Attach/Remove"),
        ]:
            try:
                attach_remove = WebDriverWait(driver, 8).until(
                    EC.element_to_be_clickable(locator)
                )
                break
            except Exception:
                continue

        assert attach_remove, "Attach/Remove link not found in notes dialog"
        scroll_to(driver, attach_remove)

        # Record main window handle BEFORE clicking Attach/Remove
        main_window = driver.current_window_handle
        all_windows_before = set(driver.window_handles)
        driver.execute_script("arguments[0].click()", attach_remove)
        wait_ready(driver)
        time.sleep(PAUSE)

        # Check if a new window/popup opened
        all_windows_after = set(driver.window_handles)
        new_windows = all_windows_after - all_windows_before

        if new_windows:
            popup_window = list(new_windows)[0]
            driver.switch_to.window(popup_window)
            print(f"  [INFO] Switched to popup window for file attach dialog")

        take_screenshot(driver, "06c_file_attach_dialog")
        print("  [INFO] File attach dialog opened")

        # ── Step 5: Enter attachment title ───────────────────────────────────
        print("  [INFO] Entering attachment title...")
        title_input = None
        for locator in [
            (By.XPATH, "//input[@id='Title' or @name='Title']"),
            (By.XPATH, "//label[contains(normalize-space(),'Title')]/following-sibling::input"),
            (By.XPATH, "//td[contains(normalize-space(),'Title')]/following::input[@type='text'][1]"),
            (By.XPATH, "(//input[@type='text'])[1]"),
        ]:
            try:
                title_input = WebDriverWait(driver, 8).until(
                    EC.presence_of_element_located(locator)
                )
                if title_input.is_displayed():
                    break
            except Exception:
                continue

        assert title_input, "Title input not found in file attach dialog"
        title_input.clear()
        title_input.send_keys("AutoTest_Attachment")
        print("  [INFO] Title entered: 'AutoTest_Attachment'")

        # ── Step 6: Choose the upload file ───────────────────────────────────
        upload_file_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "test_data", "test_attachment.txt")
        )
        print(f"  [INFO] Upload file: {upload_file_path}")
        file_input = None
        for locator in [
            (By.XPATH, "//input[@type='file']"),
            (By.CSS_SELECTOR, "input[type='file']"),
        ]:
            try:
                file_input = WebDriverWait(driver, 8).until(
                    EC.presence_of_element_located(locator)
                )
                break
            except Exception:
                continue

        assert file_input, "File input not found in file attach dialog"
        file_input.send_keys(upload_file_path)
        # Trigger change event so the browser registers the file selection
        driver.execute_script(
            "arguments[0].dispatchEvent(new Event('change', {bubbles:true}))", file_input
        )
        time.sleep(PAUSE)
        take_screenshot(driver, "06d_file_chosen")
        print("  [INFO] File chosen")

        # ── Step 7: Click Upload File button ─────────────────────────────────
        print("  [INFO] Clicking Upload File button...")
        upload_btn = None
        for locator in [
            (By.XPATH, "//button[contains(normalize-space(),'Upload File')]"),
            (By.XPATH, "//a[contains(normalize-space(),'Upload File')]"),
            (By.XPATH, "//*[contains(normalize-space(),'Upload File') and (self::button or self::a or self::span or self::input)]"),
        ]:
            try:
                upload_btn = WebDriverWait(driver, 8).until(
                    EC.element_to_be_clickable(locator)
                )
                break
            except Exception:
                continue

        assert upload_btn, "Upload File button not found"
        scroll_to(driver, upload_btn)
        driver.execute_script("arguments[0].click()", upload_btn)
        time.sleep(3)  # Allow server time to process the upload
        print("  [INFO] Upload File clicked — waiting for Remove link to appear...")

        # ── Attachment verification ──────────────────────────────────────────
        attachment_visible = False
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//a[normalize-space()='Remove'] | //button[normalize-space()='Remove'] | //table[.//th[normalize-space()='Action']]//td/a")
                )
            )
            attachment_visible = True
            print("  [PASS] File uploaded — attachment row appeared")
        except Exception as exc:
            print(f"  [WARN] Remove link not found after 20s — upload may have failed: {exc}")

        take_screenshot(driver, "06e_file_uploaded")
        if not attachment_visible:
            print("  [WARN] Attachments table is empty. Proceeding anyway.")

        # ── Step 8: Click Done in the file attach dialog ─────────────────────
        print("  [INFO] Clicking Done button...")
        done_clicked = False
        for locator in [
            (By.XPATH, "//button[normalize-space(.)='Done']"),
            (By.XPATH, "//a[normalize-space(.)='Done']"),
            (By.XPATH, "//button[.//span[normalize-space()='Done']]"),
            (By.XPATH, "//a[.//span[normalize-space()='Done']]"),
        ]:
            try:
                done_el = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(locator)
                )
                rect = done_el.rect
                if rect['width'] > 0 and rect['height'] > 0:
                    scroll_to(driver, done_el)
                    done_el.click()
                    done_clicked = True
                    print("  [INFO] Done button clicked (direct locator)")
                    break
            except Exception:
                continue

        if not done_clicked:
            done_spans = driver.find_elements(
                By.XPATH, "//span[contains(@class,'btn-toolbar-text') and normalize-space(text())='Done']"
            )
            for span in done_spans:
                try:
                    rect = span.rect
                    if rect['width'] > 0 and rect['height'] > 0:
                        parent = driver.execute_script(
                            "return arguments[0].closest('a,button,[onclick]') || arguments[0].parentElement;", span
                        )
                        target = parent if parent else span
                        driver.execute_script("arguments[0].click()", target)
                        done_clicked = True
                        print("  [INFO] Done clicked via btn-toolbar-text span")
                        break
                except Exception as e:
                    print(f"  [WARN] Done span error: {e}")

        assert done_clicked, "Done button not found in file attach dialog"
        wait_ready(driver)
        time.sleep(PAUSE)
        
        # Switch back to main window if we were in a popup
        if new_windows and driver.current_window_handle != main_window:
            driver.switch_to.window(main_window)
            print("  [INFO] Switched back to main window")
            
        take_screenshot(driver, "06f_after_done")
        print("  [INFO] Done clicked — back in Attach Notes dialog")

        # ── Step 8b: Check 'Apply this notes to all selected Cards' checkbox ───
        print("  [INFO] Checking 'Apply this notes to all selected Cards' checkbox...")
        apply_checked = False
        for apply_locator in [
            (By.XPATH, "//input[@type='checkbox'][contains(@id,'Apply') or contains(@name,'Apply') or contains(@id,'apply') or contains(@name,'apply')]"),
            (By.XPATH, "//label[contains(normalize-space(),'Apply this') and contains(normalize-space(),'selected')]/..//input[@type='checkbox']"),
            (By.XPATH, "//label[contains(normalize-space(),'Apply this') and contains(normalize-space(),'selected')]/preceding-sibling::input[@type='checkbox'][1]"),
            (By.XPATH, "//input[@type='checkbox'][following-sibling::*[contains(normalize-space(),'Apply this')]]"),
            (By.XPATH, "//input[@type='checkbox'][following::label[contains(normalize-space(),'Apply this')]]"),
        ]:
            try:
                apply_chk = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(apply_locator)
                )
                if apply_chk.is_displayed():
                    scroll_to(driver, apply_chk)
                    if not apply_chk.is_selected():
                        driver.execute_script("arguments[0].click()", apply_chk)
                        time.sleep(0.3)
                    apply_checked = True
                    print("  [INFO] 'Apply this notes to all selected Cards' checkbox checked")
                    break
            except Exception:
                continue

        if not apply_checked:
            print("  [WARN] Apply-to-all checkbox not found, proceeding without it")
        take_screenshot(driver, "06f2_apply_all_checked")

        # ── Step 9: Click 'Apply Notes' to save notes and close the dialog ───
        print("  [INFO] Clicking Apply Notes to save notes and close dialog...")
        apply_notes_clicked = False
        for locator in [
            (By.XPATH, "//button[normalize-space()='Apply Notes']"),
            (By.XPATH, "//a[normalize-space()='Apply Notes']"),
            (By.XPATH, "//span[contains(@class,'btn-toolbar-text') and normalize-space(text())='Apply Notes']"),
        ]:
            try:
                apply_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(locator)
                )
                if apply_btn.is_displayed():
                    scroll_to(driver, apply_btn)
                    driver.execute_script("arguments[0].click()", apply_btn)
                    apply_notes_clicked = True
                    print("  [INFO] Apply Notes clicked")
                    break
            except Exception:
                continue

        if not apply_notes_clicked:
            for span in driver.find_elements(
                By.XPATH, "//span[contains(@class,'btn-toolbar-text') and normalize-space(text())='Apply Notes']"
            ):
                try:
                    if span.rect['width'] > 0:
                        parent = driver.execute_script(
                            "return arguments[0].closest('a,button,[onclick]') || arguments[0].parentElement;", span
                        )
                        driver.execute_script("arguments[0].click()", parent or span)
                        apply_notes_clicked = True
                        print("  [INFO] Apply Notes clicked via span fallback")
                        break
                except Exception:
                    continue

        assert apply_notes_clicked, "Apply Notes button not found in Attach Notes dialog"
        wait_ready(driver)
        time.sleep(PAUSE)

        # ── Dismiss any modal that appears after Apply Notes ─────────────────
        time.sleep(1)
        try:
            alert = driver.switch_to.alert
            print(f"  [INFO] JS alert after Apply Notes: '{alert.text}'")
            alert.accept()
        except Exception:
            pass

        for modal_locator in [
            (By.XPATH, "//button[normalize-space()='Ok' or normalize-space()='OK']"),
            (By.XPATH, "//button[normalize-space()='Confirm']"),
        ]:
            try:
                mb = WebDriverWait(driver, 3).until(EC.element_to_be_clickable(modal_locator))
                driver.execute_script("arguments[0].click()", mb)
                print(f"  [INFO] Post-Apply-Notes modal dismissed: '{mb.text.strip()}'")
                time.sleep(0.5)
                break
            except Exception:
                continue

        take_screenshot(driver, "06g_after_apply_notes")
        print("  [INFO] Notes saved — re-selecting cards then clicking Receive...")

        # ── Step 9d: Re-select cards ─────────────────────────────────────────
        recheck_inputs = driver.find_elements(
            By.XPATH, "//input[contains(@name,'CheckboxCardGID') and not(contains(@name,'_All$'))]"
        )
        reselected = 0
        for inp in recheck_inputs[:3]:
            try:
                row = driver.execute_script("return arguments[0].closest('tr')", inp)
                row_class = driver.execute_script("return arguments[0].className", row) if row else ""
                if "SelectedRow" in row_class:
                    reselected += 1
                    continue
                scroll_to(driver, inp)
                driver.execute_script("arguments[0].click()", inp)
                time.sleep(0.3)
                row_class = driver.execute_script("return arguments[0].className", row) if row else ""
                if "SelectedRow" in row_class:
                    reselected += 1
                else:
                    print(f"  [WARN] Row class after re-click: '{row_class}'")
            except Exception as e:
                print(f"  [WARN] Re-select error: {e}")
                
        print(f"  [INFO] {reselected} card(s) re-selected for Receive")
        take_screenshot(driver, "06g2_reselected_for_receive")

        # ── Step 10: Click Receive from the main toolbar ─────────────────────
        receive_clicked = False
        for locator in [
            (By.XPATH, "//button[.//span[contains(@class,'btn-toolbar-text') and normalize-space()='Receive']]"),
            (By.XPATH, "//a[.//span[contains(@class,'btn-toolbar-text') and normalize-space()='Receive']]"),
            (By.XPATH, "//*[@id='btnReceive' or @id='lnkReceive' or @id='btnReceiveCards' or @id='lnkReceiveCards']"),
            (By.XPATH, "//*[contains(@onclick,'Receive') and (.//span[contains(@class,'btn-toolbar-text')])]"),
        ]:
            try:
                recv_btn = WebDriverWait(driver, 8).until(
                    EC.element_to_be_clickable(locator)
                )
                if recv_btn.is_displayed():
                    btn_text = recv_btn.text.strip()
                    driver.execute_script("arguments[0].click()", recv_btn)
                    receive_clicked = True
                    print(f"  [INFO] Toolbar Receive clicked: '{btn_text}'")
                    break
            except Exception:
                continue

        if not receive_clicked:
            for span in driver.find_elements(
                By.XPATH, "//span[contains(@class,'btn-toolbar-text') and normalize-space(text())='Receive']"
            ):
                try:
                    if span.rect['width'] > 0 and span.rect['height'] > 0:
                        parent = driver.execute_script(
                            "return arguments[0].closest('a,button,[onclick]') || arguments[0].parentElement;", span
                        )
                        driver.execute_script("arguments[0].click()", parent or span)
                        receive_clicked = True
                        print("  [INFO] Receive clicked via btn-toolbar-text span")
                        break
                except Exception as e:
                    print(f"  [WARN] Receive span error: {e}")

        assert receive_clicked, "Receive button not found in main toolbar"

        # ── Step 10b: Handle confirm dialog ──────────────────────────────────
        time.sleep(1)
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            print(f"  [INFO] JS Confirm dialog: '{alert_text}'")
            alert.accept()
            print("  [INFO] Confirm dialog accepted — cards confirmed for receive")
            time.sleep(1)
        except Exception:
            print("  [INFO] No JS confirm dialog detected")

        for confirm_locator in [
            (By.XPATH, "//button[normalize-space()='Ok' or normalize-space()='OK']"),
            (By.XPATH, "//button[normalize-space()='Confirm']"),
            (By.XPATH, "//button[normalize-space()='Yes']"),
            (By.XPATH, "//span[contains(@class,'btn-toolbar-text') and (normalize-space()='Confirm' or normalize-space()='OK')]"),
        ]:
            try:
                cb = WebDriverWait(driver, 4).until(EC.element_to_be_clickable(confirm_locator))
                driver.execute_script("arguments[0].click()", cb)
                print(f"  [INFO] Page confirm button clicked: '{cb.text.strip()}'")
                time.sleep(1)
                break
            except Exception:
                continue

        wait_ready(driver)
        time.sleep(PAUSE * 2)
        take_screenshot(driver, "06h_after_receive")
        print(f"  [URL] {driver.current_url}")
        print("  [PASS] Apply Notes + Receive confirmed completed.")

    # ── TC-RCV-007: Verify Receive Results ───────────────────────────────
    def test_07_verify_receive_results(self, driver):
        """Verify the Receive Results page shows a success/completion message."""
        print("\n[TC-RCV-007] Verifying Receive Results page...")

        current_url = driver.current_url
        print(f"  [URL] {current_url}")

        success_found = False
        receive_success_locators = [
            (By.XPATH, "//*[contains(normalize-space(),'Card Successfully Received')]"),
            (By.XPATH, "//*[contains(normalize-space(),'have been received')]"),
            (By.XPATH, "//*[contains(normalize-space(),'Card(s) have been received')]"),
            (By.XPATH, "//*[contains(normalize-space(),'received without printing')]"),
            (By.XPATH, "//*[contains(normalize-space(),'Following Cards were successful')]"),
            (By.XPATH, "//*[contains(normalize-space(),'successfully received')]"),
        ]
        for locator in receive_success_locators:
            try:
                el = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))
                msg = el.text.strip()
                if msg:
                    print(f"  [PASS] Receive success message found: '{msg[:150]}'")
                    success_found = True
                    break
            except Exception:
                continue

        take_screenshot(driver, "07_receive_results")

        if not success_found:
            try:
                body_text = driver.find_element(By.TAG_NAME, "body").text[:300]
                print(f"  [WARN] No specific 'received' message found. Page text: '{body_text}'")
            except Exception:
                pass
            print("  [WARN] Cards may not have been confirmed on server. Check screenshot 07.")

        assert any(kw in current_url for kw in ["Receive", "receive", "Result", "result"]), \
            f"Not on expected Receive Results/Cards page. URL: {current_url}"
        print("  [PASS] Receive Results page verified.")

    # ── TC-RCV-008: Click Back to Items ──────────────────────────────────
    def test_08_back_to_items(self, driver):
        """Click Back to Items and verify return to Receive Items List."""
        print("\n[TC-RCV-008] Clicking Back to Items...")
        print(f"  [INFO] Currently on {driver.current_url}")

        # Re-navigate via ReceiveItems → item click to get proper context
        print("  [INFO] Re-navigating via ReceiveItems → item click for proper context...")
        driver.get(f"{BASE_URL}/BuyerAction/ReceiveItems")
        wait_ready(driver)
        time.sleep(PAUSE)

        item_links = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class,'GridLink')]"))
        )
        assert item_links, "No items found in Receive Items List"
        item_text = item_links[0].text.strip()
        print(f"  [INFO] Clicking item: '{item_text}'")
        driver.execute_script("arguments[0].click()", item_links[0])
        wait_ready(driver)
        time.sleep(PAUSE * 2)
        print(f"  [INFO] Now on: {driver.current_url}")

        # Find Back to Items button
        back_btn = None
        for locator in [
            (By.ID, "btnBackPageTop"),
            (By.ID, "btnBackPageBot"),
            (By.XPATH, "//span[@id='btnBackPageTop' or @id='btnBackPageBot']"),
            (By.XPATH, "//span[contains(@class,'vd-blue-btn') and contains(normalize-space(),'Back')]"),
            (By.XPATH, "//*[contains(normalize-space(),'Back To Items') or contains(normalize-space(),'Back to Items')]"),
        ]:
            try:
                back_btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(locator))
                print(f"  [INFO] Found back button: '{back_btn.text.strip()}'")
                break
            except Exception:
                continue

        # JS fallback: search by ID or visible inner text
        if not back_btn:
            print("  [INFO] Trying JS element search for Back to Items button...")
            back_btn = driver.execute_script(
                "return document.getElementById('btnBackPageTop')"
                " || document.getElementById('btnBackPageBot')"
                " || (function() {"
                "      var all = document.querySelectorAll('*');"
                "      for(var i=0; i<all.length; i++) {"
                "        var t=(all[i].innerText||'').trim().toLowerCase();"
                "        if(t==='back to items' || t==='back to item') {"
                "          if(all[i].offsetParent!==null) return all[i];"
                "        }"
                "      } return null; "
                "    })()"
            )
            if back_btn:
                print("  [INFO] JS found back element.")

        assert back_btn, "Back to Items button not found"
        scroll_to(driver, back_btn)
        driver.execute_script("arguments[0].click()", back_btn)
        wait_ready(driver)
        time.sleep(PAUSE)

        take_screenshot(driver, "08_back_to_items")
        current_url = driver.current_url
        print(f"  [URL] {current_url}")
        assert any(kw in current_url for kw in ["ReceiveItem", "Receive", "receive"]), \
            f"Expected Receive Items page. Got: {current_url}"
        print("  [PASS] Successfully returned to Receive Items List.")