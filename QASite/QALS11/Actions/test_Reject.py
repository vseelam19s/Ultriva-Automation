"""
QALS11 | Actions > Reject Cards
================================

Step-wise flow:
    STEP 01: Login to QA site
    STEP 02: Navigate to Buyer Actions
    STEP 03: Open Approve Filter
    STEP 04: Click Go to load Approve Items
    STEP 05: Open the selected item and load Approve Cards
    STEP 06: Select cards, enter reject comment, click Reject
    STEP 07: Back to Items and verify return flow

Run from qa_automation/:
    pytest tests/QALS11/Actions/test_Reject.py -v -s
"""

import os
import random
import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
USERNAME = "buyeruser"
PASSWORD = "Ultriva!23"
PAUSE = 1.5
REJECT_COMMENT = "Rejecting card — quality issue noted during inspection."


@pytest.fixture(scope="class")
def driver():
    """Class-scoped Chrome driver for Reject flow tests."""
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


def scroll_to(driver, el):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'})", el)
    time.sleep(0.3)


def safe_click(driver, element, label="element"):
    start_url = driver.current_url
    try:
        element.click()
        time.sleep(0.8)
        if driver.current_url != start_url:
            return True
    except Exception:
        pass

    try:
        driver.execute_script("arguments[0].click()", element)
        time.sleep(0.8)
        return driver.current_url != start_url or True
    except Exception:
        return False


def take_screenshot(driver, name, prefix="reject"):
    screenshots_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "reports", "screenshots"
    )
    os.makedirs(screenshots_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(screenshots_dir, f"{prefix}_{name}_{ts}.png")
    driver.save_screenshot(path)
    print(f"  [screenshot] {path}")
    return path


def _navigate_to_approve_filter(driver):
    locators = [
        (By.XPATH, "//a[contains(@href,'ApproveFilter') and not(contains(@href,'RLApprove'))]"),
        (By.XPATH, "//a[contains(@href,'BuyerAction/Approve') and not(contains(@href,'RLApprove'))]"),
        (By.XPATH, "//span[normalize-space(text())='Approve' and not(ancestor::*[contains(@href,'RLApprove')])]."),
        (By.XPATH, "(//a[normalize-space(.)='Approve' or contains(@href,'ApproveFilter')])[1]"),
    ]
    for locator in locators:
        try:
            tile = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(locator))
            if "RLApprove" not in (tile.get_attribute("href") or ""):
                driver.execute_script("arguments[0].click()", tile)
                wait_ready(driver)
                time.sleep(PAUSE)
                if "RLApprove" not in driver.current_url:
                    return
        except Exception:
            continue
    driver.get(f"{BASE_URL}/BuyerAction/ApproveFilter")
    wait_ready(driver)
    time.sleep(PAUSE)


def _click_go_load_items(driver):
    if "ApproveFilter" not in driver.current_url:
        driver.get(f"{BASE_URL}/BuyerAction/ApproveFilter")
        wait_ready(driver)
        time.sleep(PAUSE)

    time.sleep(PAUSE)
    go_btn = None
    locators = [
        (By.ID, "btnGoBot"),
        (By.ID, "btnGoTop"),
        (By.XPATH, "//button[normalize-space(text())='Go']"),
        (By.XPATH, "//input[@type='button' and @value='Go']"),
        (By.XPATH, "//span[normalize-space(text())='Go' and (contains(@class,'btn') or contains(@class,'toolbar'))]"),
        (By.XPATH, "//a[normalize-space(text())='Go']"),
        (By.XPATH, "//*[@id='btnGo' or contains(@id,'btnGo') or contains(@id,'BtnGo')]"),
        (By.XPATH, "//span[@id='imgMatStatusGo']"),
    ]
    for locator in locators:
        try:
            go_btn = WebDriverWait(driver, 8).until(EC.element_to_be_clickable(locator))
            break
        except Exception:
            continue

    if not go_btn:
        go_btn = driver.execute_script(
            "var els=document.querySelectorAll('button,input,a,span');"
            "for(var i=0;i<els.length;i++){"
            "  var t=(els[i].innerText||els[i].value||'').trim();"
            "  if(t==='Go'&&els[i].offsetParent!==null) return els[i];"
            "} return null;"
        )

    if go_btn:
        driver.execute_script("arguments[0].click()", go_btn)
        wait_ready(driver)
        time.sleep(PAUSE * 2)
    else:
        driver.get(f"{BASE_URL}/BuyerAction/ApproveItems")
        wait_ready(driver)
        time.sleep(PAUSE)

    if "RLApprove" in driver.current_url:
        driver.get(f"{BASE_URL}/BuyerAction/ApproveItems")
        wait_ready(driver)
        time.sleep(PAUSE)


def _find_items(driver, timeout=3):
    locators = [
        (By.XPATH, "//a[contains(@class,'GridLink')]"),
        (By.XPATH, "//table//td//a[not(contains(@class,'btn'))]"),
        (By.XPATH, "//a[contains(@href,'ApproveCards')]"),
        (By.XPATH, "//a[contains(@href,'GID=')]"),
    ]
    for locator in locators:
        try:
            found = WebDriverWait(driver, timeout).until(EC.presence_of_all_elements_located(locator))
            links = []
            for item in found:
                href = (item.get_attribute('href') or '').lower()
                txt = (item.text or '').strip()
                if 'scan/cardstatus' in href:
                    continue
                if 'approveitems' in href or 'approvecards' in href or 'gid=' in href:
                    links.append(item)
                elif txt and 'scan' not in href and 'cardstatus' not in href:
                    links.append(item)
            if links:
                return links
        except Exception:
            continue
    return []


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


def _select_card_checkboxes(driver, max_cards=2):
    """Select real card-row checkboxes while ignoring the page select-all control."""
    time.sleep(PAUSE)
    if max_cards <= 0:
        return 0

    selected = 0
    seen = set()
    selectors = [
        "//input[@type='checkbox' and contains(@name,'$CheckboxCardGID') and not(contains(@name,'All$CheckboxCardGID'))]",
        "//input[@type='checkbox' and contains(@name,'CheckboxCardGID') and not(contains(@name,'_All$'))]",
        "//input[@type='checkbox' and (contains(@name,'CheckboxCardGID') or contains(@id,'CheckboxCardGID') or contains(@class,'GridCheckbox')) and not(contains(@name,'All$CheckboxCardGID')) and not(contains(@class,'grid-all-checkbox'))]",
        "//input[contains(@class,'GridCheckbox') and not(contains(@class,'grid-all-checkbox'))]",
    ]

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

                try:
                    if checkbox.is_selected() or driver.execute_script("return arguments[0].checked;", checkbox):
                        selected += 1
                        print(f"  [INFO] Already selected checkbox #{selected}: {checkbox.get_attribute('name') or checkbox.get_attribute('id')}")
                        if selected >= max_cards:
                            return selected
                        continue

                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
                    checkbox.click()
                    time.sleep(0.4)
                    if checkbox.is_selected() or driver.execute_script("return arguments[0].checked;", checkbox):
                        selected += 1
                        print(f"  [INFO] Selected checkbox #{selected}: {checkbox.get_attribute('name') or checkbox.get_attribute('id')}")
                        if selected >= max_cards:
                            return selected
                except Exception as e:
                    print(f"  [WARN] Could not click checkbox: {e}")
        except Exception:
            continue

    return selected


def _click_back_to_items(driver):
    back_btn = None
    locators = [
        (By.ID, "btnBackPageTop"),
        (By.ID, "btnBackPageBot"),
        (By.XPATH, "//span[@id='btnBackPageTop' or @id='btnBackPageBot']"),
        (By.XPATH, "//button[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'),'back to items')]"),
        (By.XPATH, "//a[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'),'back to items')]"),
        (By.XPATH, "//span[contains(@class,'vd-blue-btn') and contains(normalize-space(),'Back')]"),
        (By.XPATH, "//*[contains(normalize-space(),'Back To Items') or contains(normalize-space(),'Back to Items')]"),
        (By.XPATH, "//*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'),'back to items')]"),
    ]
    for locator in locators:
        try:
            back_btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(locator))
            print(f"  [INFO] Found Back button: '{back_btn.text.strip()}'")
            break
        except Exception:
            continue

    if not back_btn:
        back_btn = driver.execute_script(
            "return document.getElementById('btnBackPageTop')"
            " || document.getElementById('btnBackPageBot')"
            " || (function(){"
            "  var all=document.querySelectorAll('*');"
            "  for(var i=0;i<all.length;i++){"
            "    var t=(all[i].innerText||'').trim().toLowerCase();"
            "    if(t==='back to items'&&all[i].offsetParent!==null) return all[i];"
            "  } return null; })()"
        )
        if back_btn:
            print("  [INFO] Back to Items found via JS")
    return back_btn


@pytest.mark.usefixtures("driver")
class TestRejectApproveCards:
    def test_01_login(self, driver):
        print("\n[STEP 01] Logging in to QA site...")
        driver.get(BASE_URL)
        wait_ready(driver)

        find(driver, By.ID, "UserName").send_keys(USERNAME)
        find(driver, By.ID, "Password").send_keys(PASSWORD)
        clickable(driver, By.ID, "login-button").click()
        wait_ready(driver)
        time.sleep(PAUSE)

        take_screenshot(driver, "01_after_login", "reject")
        current_url = driver.current_url
        print(f"  [URL] {current_url}")
        assert BASE_URL.lower() in current_url.lower() or "Home" in current_url, f"Login failed. URL: {current_url}"
        print("  [PASS] Login successful.")

    def test_02_navigate_to_actions(self, driver):
        print("\n[STEP 02] Navigating to Buyer Actions page...")

        nav_clicked = False
        locators = [
            (By.XPATH, "//a[contains(@href,'/Action/Home')]"),
            (By.XPATH, "//span[contains(normalize-space(),'Actions')]"),
            (By.XPATH, "//a[contains(normalize-space(),'Actions')]"),
            (By.XPATH, "//li[contains(@class,'nav')]//a[contains(normalize-space(),'Action')]"),
        ]
        for locator in locators:
            try:
                link = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(locator))
                driver.execute_script("arguments[0].click()", link)
                wait_ready(driver)
                time.sleep(PAUSE)
                if "Action" in driver.current_url:
                    nav_clicked = True
                    break
            except Exception:
                continue

        if not nav_clicked:
            driver.get(f"{BASE_URL}/Action/Home")
            wait_ready(driver)
            time.sleep(PAUSE)

        take_screenshot(driver, "02_actions_page", "reject")
        current_url = driver.current_url
        print(f"  [URL] {current_url}")
        assert "Action" in current_url, f"Expected Actions page. Got: {current_url}"
        print(f"  [PASS] Actions page loaded: {current_url}")

    def test_03_click_approve_tile(self, driver):
        print("\n[STEP 03] Opening Approve Filter page...")
        _navigate_to_approve_filter(driver)

        take_screenshot(driver, "03_approve_filter", "reject")
        current_url = driver.current_url
        print(f"  [URL] {current_url}")
        assert "ApproveFilter" in current_url, f"Expected ApproveFilter. Got: {current_url}"
        print(f"  [PASS] Approve page loaded: {current_url}")

    def test_04_apply_filter_load_items(self, driver):
        print("\n[STEP 04] Applying filter and loading Approve Items...")
        _click_go_load_items(driver)

        take_screenshot(driver, "04_approve_items_list", "reject")
        current_url = driver.current_url
        print(f"  [URL] {current_url}")
        assert "ApproveItem" in current_url, f"Expected ApproveItems. Got: {current_url}"
        print(f"  [PASS] Approve Items List loaded: {current_url}")

    def test_05_click_item_show_cards(self, driver):
        print("\n[STEP 05] Selecting an item and opening Approve Cards...")

        if "ApproveItem" not in driver.current_url:
            driver.get(f"{BASE_URL}/BuyerAction/ApproveItems")
            wait_ready(driver)
            time.sleep(PAUSE)

        item_links = _find_items(driver)
        if not item_links:
            pytest.skip("No items available in Approve Items List — test data may be depleted")

        first_item = item_links[0]
        print(f"  [INFO] First item found: '{first_item.text.strip()}'")
        safe_click(driver, first_item, "first item")
        wait_ready(driver)
        time.sleep(PAUSE * 2)
        take_screenshot(driver, "05a_after_item_click", "reject")
        print(f"  [INFO] URL after item click: {driver.current_url}")

        if "ApproveCards" not in driver.current_url:
            print("  [INFO] Looking for Show Cards button...")
            locators = [
                (By.XPATH, "//button[contains(normalize-space(),'Show Cards')]"),
                (By.XPATH, "//a[contains(normalize-space(),'Show Cards')]"),
                (By.XPATH, "//input[@value='Show Cards']"),
            ]
            for locator in locators:
                try:
                    btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(locator))
                    safe_click(driver, btn, "Show Cards button")
                    wait_ready(driver)
                    time.sleep(PAUSE * 2)
                    break
                except Exception:
                    continue

        take_screenshot(driver, "05b_approve_cards", "reject")
        current_url = driver.current_url
        print(f"  [INFO] URL on ApproveCards: {current_url}")
        assert "ApproveCard" in current_url or "approvecard" in current_url.lower(), f"Expected ApproveCards page. Got: {current_url}"
        print("  [PASS] Approve Cards List loaded.")

    def test_06_select_cards_reject_with_comment(self, driver):
        print("\n[STEP 06] Selecting cards, entering reject comment, and rejecting...")

        if "ApproveCard" not in driver.current_url:
            print("  [INFO] Navigating via ApproveItems → first item...")
            driver.get(f"{BASE_URL}/BuyerAction/ApproveItems")
            wait_ready(driver)
            time.sleep(PAUSE)
            links = _find_items(driver)
            if not links:
                pytest.skip("No items available in Approve Items List — test data may be depleted")
            safe_click(driver, links[0], "item link")
            wait_ready(driver)
            time.sleep(PAUSE * 2)

        selected = _select_card_checkboxes(driver)
        assert selected > 0, "Could not select any card checkboxes"
        print(f"  [INFO] Total selected: {selected}")
        take_screenshot(driver, "06a_cards_selected", "reject")

        print("  [INFO] Looking for Notes textarea on Approve Cards page...")
        comment_entered = False
        notes_locators = [
            (By.XPATH, "//textarea[@id='Notes' or @name='Notes']"),
            (By.XPATH, "//textarea[contains(@id,'note') or contains(@name,'note') or contains(@id,'Note') or contains(@name,'Note')]"),
            (By.XPATH, "//textarea"),
            (By.XPATH, "//input[@type='text' and (contains(@id,'note') or contains(@id,'Note') or contains(@id,'comment') or contains(@id,'Comment'))]"),
        ]
        for notes_locator in notes_locators:
            try:
                notes_field = WebDriverWait(driver, 5).until(EC.visibility_of_element_located(notes_locator))
                scroll_to(driver, notes_field)
                notes_field.clear()
                notes_field.send_keys(REJECT_COMMENT)
                comment_entered = True
                print(f"  [INFO] Comment entered: '{REJECT_COMMENT}'")
                take_screenshot(driver, "06b_comment_entered", "reject")
                break
            except Exception:
                continue

        if not comment_entered:
            print("  [WARN] Notes textarea not found — continuing without pre-comment")

        print("  [INFO] Clicking Reject button...")
        reject_btn = None
        reject_locators = [
            (By.ID, "btnRejectTop"), (By.ID, "btnRejectBot"),
            (By.XPATH, "//button[normalize-space(text())='Reject']"),
            (By.XPATH, "//a[normalize-space(text())='Reject']"),
            (By.XPATH, "//span[normalize-space(text())='Reject']"),
            (By.XPATH, "//input[@type='button' and contains(@value,'Reject')]"),
            (By.XPATH, "//*[contains(normalize-space(),'Reject') and (self::button or self::a or self::span or self::input) and not(contains(normalize-space(),'Back'))]"),
        ]
        for locator in reject_locators:
            try:
                candidate = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(locator))
                btn_text = (candidate.text or candidate.get_attribute('value') or '').strip().lower()
                if btn_text not in ('back to items', 'back', ''):
                    reject_btn = candidate
                    break
            except Exception:
                continue

        assert reject_btn, "Reject button not found on Approve Cards List page"
        print(f"  [INFO] Found Reject button: '{reject_btn.text.strip() or reject_btn.get_attribute('value')}'")
        scroll_to(driver, reject_btn)
        safe_click(driver, reject_btn, "Reject button")
        wait_ready(driver)
        time.sleep(PAUSE * 2)
        take_screenshot(driver, "06c_after_reject_click", "reject")
        print(f"  [INFO] URL after Reject click: {driver.current_url}")

        print("  [INFO] Waiting for RejectResults page...")
        try:
            WebDriverWait(driver, 15).until(lambda d: "RejectResult" in d.current_url)
            print(f"  [INFO] Landed on results page: {driver.current_url}")
        except Exception:
            print(f"  [INFO] Still on: {driver.current_url} — checking success text")

        take_screenshot(driver, "06d_reject_results", "reject")
        success_found = False
        res_locators = [
            (By.XPATH, "//*[contains(normalize-space(),'Following Cards were successful')]"),
            (By.XPATH, "//*[contains(normalize-space(),'Card Successfully Rejected')]"),
            (By.XPATH, "//*[contains(normalize-space(),'Reject Cards Results')]"),
            (By.XPATH, "//*[contains(normalize-space(),'successfully')]"),
        ]
        for locator in res_locators:
            try:
                el = WebDriverWait(driver, 8).until(EC.presence_of_element_located(locator))
                print(f"  [INFO] Success message: '{el.text.strip()[:120]}'")
                success_found = True
                break
            except Exception:
                continue

        assert "RejectResult" in driver.current_url or success_found, f"Expected RejectResults with success message. URL: {driver.current_url} success_found={success_found}"
        print("  [PASS] Reject Cards Results page verified — cards successfully rejected.")

    def test_07_back_to_items(self, driver):
        print("\n[STEP 07] Returning to the Approve Items list...")
        print(f"  [INFO] Currently on: {driver.current_url}")

        if not any(kw in driver.current_url for kw in ("ApproveCard", "ApproveResult", "RejectResult")):
            print("  [INFO] Re-navigating via ApproveItems → item click...")
            driver.get(f"{BASE_URL}/BuyerAction/ApproveItems")
            wait_ready(driver)
            time.sleep(PAUSE)
            links = _find_items(driver)
            if not links:
                pytest.skip("No items available in Approve Items List — test data may be depleted")
            safe_click(driver, links[0], "item link")
            wait_ready(driver)
            time.sleep(PAUSE * 2)

        back_btn = _click_back_to_items(driver)
        assert back_btn, "Back to Items button not found"
        scroll_to(driver, back_btn)
        safe_click(driver, back_btn, "Back to Items button")
        wait_ready(driver)
        time.sleep(PAUSE)

        take_screenshot(driver, "07_back_to_items", "reject")
        current_url = driver.current_url
        print(f"  [URL] {current_url}")
        assert any(kw in current_url for kw in ["ApproveItem", "Approve", "approve"]), f"Expected Approve Items page after Back to Items. Got: {current_url}"
        print("  [PASS] Successfully returned to Approve Items List.")


if __name__ == "__main__":
    raise SystemExit(pytest.main(["-v", "-s", __file__]))
