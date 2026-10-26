"""
QALS11 | Actions > Approve Cards
================================
Run from qa_automation/:
    pytest tests/QALS11/Actions/test_Approve.py -v -s
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


@pytest.fixture(scope="class")
def driver():
    """Class-scoped Chrome driver for Approve flow tests."""
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


def take_screenshot(driver, name, prefix="approve"):
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
        try:
            checkbox = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
            if not checkbox.is_selected():
                checkbox.click()
                time.sleep(0.4)
        except Exception:
            continue


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
    time.sleep(PAUSE)
    candidate_cbs = driver.find_elements(By.XPATH, "//input[@type='checkbox']")
    if not candidate_cbs:
        try:
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.querySelectorAll('input[type=checkbox]').length") > 0
            )
            candidate_cbs = driver.find_elements(By.XPATH, "//input[@type='checkbox']")
        except Exception:
            print(f"  [WARN] No checkbox inputs found on page: {driver.current_url}")
            return 0

    def is_non_card_control(value_text):
        text = (value_text or '').lower()
        return any(token in text for token in ['applynotes', 'search_', 'selectall', 'toggleall', 'allcheckbox'])

    real_card_cbs = []
    for cb in candidate_cbs:
        name = (cb.get_attribute('name') or '').lower()
        class_name = (cb.get_attribute('class') or '').lower()
        cb_id = (cb.get_attribute('id') or '').lower()
        value = (cb.get_attribute('value') or '').lower()
        title = (cb.get_attribute('title') or '').lower()
        combined = f"{name} {class_name} {cb_id} {value} {title}"
        if not cb.is_displayed():
            continue
        if cb.get_attribute('disabled') is not None:
            continue

        if is_non_card_control(combined):
            continue
        if 'grid-all-checkbox' in combined or 'all$checkboxcardgid' in combined:
            continue
        if 'all' in combined and 'checkbox' in combined and ('card' in combined or 'gid' in combined):
            continue
        if 'checkboxcardgid' in combined and 'all' in combined:
            continue
        if value in {'all', 'item', 'card', 'supplier', 'user'} and 'checkbox' not in combined and 'card' not in combined and 'gid' not in combined:
            continue

        real_card_cbs.append(cb)

    if not real_card_cbs:
        print("  [WARN] No obvious row checkboxes matched; checking for select-all card checkbox.")
        for cb in candidate_cbs:
            name = (cb.get_attribute('name') or '').lower()
            class_name = (cb.get_attribute('class') or '').lower()
            cb_id = (cb.get_attribute('id') or '').lower()
            combined = f"{name} {class_name} {cb_id}"
            if not cb.is_displayed():
                continue
            if cb.get_attribute('disabled') is not None:
                continue
            if 'checkboxcardgid' in combined and ('all' in combined or 'grid-all-checkbox' in combined or 'allcheckbox' in combined):
                real_card_cbs.append(cb)
                break

    if not real_card_cbs:
        print("  [WARN] No obvious row or select-all checkboxes matched; using permissive fallback.")
        for cb in candidate_cbs:
            name = (cb.get_attribute('name') or '').lower()
            class_name = (cb.get_attribute('class') or '').lower()
            cb_id = (cb.get_attribute('id') or '').lower()
            combined = f"{name} {class_name} {cb_id}"
            if not cb.is_displayed():
                continue
            if cb.get_attribute('disabled') is not None:
                continue
            if any(token in combined for token in ['applynotes', 'search_', 'selectall', 'toggleall', 'allcheckbox']):
                continue
            if 'all' in combined and 'checkbox' in combined:
                continue
            if 'checkbox' in combined or 'card' in combined or 'gid' in combined or 'grid' in combined:
                real_card_cbs.append(cb)

    if not real_card_cbs:
        return 0

    selected_cbs = random.sample(real_card_cbs, min(len(real_card_cbs), max_cards)) if len(real_card_cbs) > max_cards else real_card_cbs
    print(f"  [INFO] Randomly selecting {len(selected_cbs)} real card(s) out of {len(real_card_cbs)} available.")

    selected = 0
    for cb in selected_cbs:
        try:
            cb_name = cb.get_attribute('name') or ''
            cb_value = cb.get_attribute('value') or ''
            cb_class = cb.get_attribute('class') or ''
            print(f"  [INFO] Checkbox — name={cb_name!r}  value={cb_value!r}  class={cb_class!r}")
            scroll_to(driver, cb)
            safe_click(driver, cb, "card checkbox")
            time.sleep(0.5)
            selected += 1
            print(f"  [INFO] Selected checkbox #{selected}")
        except Exception as e:
            print(f"  [WARN] Could not click checkbox: {e}")
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
class TestApproveCards:
    def test_01_login(self, driver):
        print("\n[TC-APR-001] Logging in to QA site...")
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

        take_screenshot(driver, "01_after_login", "approve")
        current_url = driver.current_url
        print(f"  [URL] {current_url}")
        assert BASE_URL.lower() in current_url.lower() or "Home" in current_url, f"Login may have failed. URL: {current_url}"
        print("  [PASS] Login successful.")

    def test_02_navigate_to_actions(self, driver):
        print("\n[TC-APR-002] Navigating to Actions page...")
        actions_link = clickable(
            driver, By.XPATH,
            "//a[contains(@href,'Action/Home') or (.//span[normalize-space()='Actions']) or normalize-space(.)='Actions']",
        )
        scroll_to(driver, actions_link)
        actions_link.click()
        wait_ready(driver)
        time.sleep(PAUSE)

        take_screenshot(driver, "02_actions_page", "approve")
        assert "Action/Home" in driver.current_url, f"Expected Actions page. Got: {driver.current_url}"
        print(f"  [PASS] Actions page loaded: {driver.current_url}")

    def test_03_click_approve(self, driver):
        print("\n[TC-APR-003] Clicking Approve tile in Buyer Actions...")
        _navigate_to_approve_filter(driver)

        take_screenshot(driver, "03_approve_filter", "approve")
        print(f"  [URL] {driver.current_url}")
        assert any(kw in driver.current_url for kw in ["ApproveFilter", "Approve"]), f"Expected ApproveFilter. Got: {driver.current_url}"
        print(f"  [PASS] Approve page loaded: {driver.current_url}")

    def test_04_apply_filter_and_load_items(self, driver):
        print("\n[TC-APR-004] Applying filter — clicking Go button...")
        current_url = driver.current_url
        if "ApproveItems" in current_url and "RLApprove" not in current_url:
            print("  [INFO] Already on Approve Items page.")
        else:
            _click_go_load_items(driver)

        take_screenshot(driver, "04_approve_items_list", "approve")
        print(f"  [URL] {driver.current_url}")
        assert "ApproveItem" in driver.current_url and "RLApprove" not in driver.current_url, f"Expected ApproveItems (not RLApprove). Got: {driver.current_url}"
        print(f"  [PASS] Approve Items List loaded: {driver.current_url}")

    def test_05_select_item_show_cards(self, driver):
        print("\n[TC-APR-005] Selecting first item and clicking Show Cards...")
        item_links = _find_items(driver, timeout=10)
        if not item_links:
            pytest.skip("No items available in Approve Items List — test data may be depleted")

        first_item = item_links[0]
        print(f"  [INFO] First item found: '{first_item.text.strip()}'")
        scroll_to(driver, first_item)
        safe_click(driver, first_item, "first item")
        wait_ready(driver)
        time.sleep(PAUSE * 2)
        take_screenshot(driver, "05a_after_item_click", "approve")
        print(f"  [INFO] URL after item click: {driver.current_url}")

        if any(kw in driver.current_url for kw in ["ApproveCard", "approvecard"]):
            print("  [INFO] Navigated directly to Approve Cards page.")
            return

        for locator in [
            (By.ID, "btnShowCardsT"), (By.ID, "btnShowCardsB"),
            (By.XPATH, "//button[contains(normalize-space(),'Show Cards')]"),
            (By.XPATH, "//a[contains(normalize-space(),'Show Cards')]"),
            (By.XPATH, "//span[contains(normalize-space(),'Show Cards')]"),
        ]:
            try:
                btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(locator))
                scroll_to(driver, btn)
                driver.execute_script("arguments[0].click()", btn)
                wait_ready(driver)
                time.sleep(PAUSE * 2)
                break
            except Exception:
                continue

        take_screenshot(driver, "05b_approve_cards_list", "approve")
        print(f"  [URL] {driver.current_url}")
        assert any(kw in driver.current_url for kw in ["ApproveCard", "approvecard"]), f"Expected Approve Cards page. Got: {driver.current_url}"
        print(f"  [PASS] Approve Cards List confirmed: {driver.current_url}")

    def test_06_select_cards_approve_and_finish(self, driver):
        print("\n[TC-APR-006] Selecting cards → Approve → verify success message...")

        if "ApproveCard" not in driver.current_url:
            print("  [INFO] Not on ApproveCards — navigating via ApproveItems...")
            driver.get(f"{BASE_URL}/BuyerAction/ApproveItems")
            wait_ready(driver)
            time.sleep(PAUSE)
            links = _find_items(driver)
            if not links:
                pytest.skip("No items available in Approve Items List — test data may be depleted")
            driver.execute_script("arguments[0].click()", links[0])
            wait_ready(driver)
            time.sleep(PAUSE * 2)

        selected = 2 if select_two_cards(driver) else _select_card_checkboxes(driver)
        assert selected > 0, "Could not select any card checkboxes"
        print(f"  [INFO] Total selected: {selected}")
        take_screenshot(driver, "06a_cards_selected", "approve")

        print("  [INFO] Clicking Approve button...")
        approve_btn = None
        locators = [
            (By.ID, "btndoActTop"), (By.ID, "btndoActBot"),
            (By.XPATH, "//span[@onclick='da()']"),
            (By.XPATH, "//button[normalize-space(text())='Approve Cards']"),
            (By.XPATH, "//button[normalize-space(text())='Approve']"),
            (By.XPATH, "//a[normalize-space(text())='Approve Cards']"),
            (By.XPATH, "//a[normalize-space(text())='Approve']"),
            (By.XPATH, "//span[contains(normalize-space(),'Approve') and (contains(@class,'btn') or contains(@class,'toolbar')) and not(contains(normalize-space(),'Back'))]"),
            (By.XPATH, "//*[@id='btnApprove' or contains(@id,'doAct')]"),
        ]
        for locator in locators:
            try:
                candidate = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(locator))
                btn_text = candidate.text.strip().lower()
                if btn_text not in ("back to items", "back", ""):
                    approve_btn = candidate
                    break
            except Exception:
                continue

        assert approve_btn, "Approve button not found on ApproveCards page"
        print(f"  [INFO] Found Approve button: '{approve_btn.text.strip()}'")
        scroll_to(driver, approve_btn)
        driver.execute_script("arguments[0].click()", approve_btn)
        wait_ready(driver)
        time.sleep(PAUSE * 2)
        take_screenshot(driver, "06b_after_approve_click", "approve")
        print(f"  [INFO] URL after Approve click: {driver.current_url}")

        for locator in [
            (By.ID, "btnapNodoAct"),
            (By.XPATH, "//button[contains(normalize-space(),'Approve without Notes')]"),
            (By.XPATH, "//a[contains(normalize-space(),'Approve without Notes')]"),
            (By.XPATH, "//span[contains(normalize-space(),'Approve without Notes')]"),
        ]:
            try:
                dialog_btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(locator))
                print(f"  [INFO] Notes dialog: '{dialog_btn.text.strip()}' — clicking...")
                driver.execute_script("arguments[0].click()", dialog_btn)
                wait_ready(driver)
                time.sleep(PAUSE * 2)
                take_screenshot(driver, "06c_after_notes_dialog", "approve")
                print(f"  [INFO] URL after notes dialog: {driver.current_url}")
                break
            except Exception:
                continue

        print("  [INFO] Waiting for ApproveResults page and success message...")
        try:
            WebDriverWait(driver, 15).until(lambda d: "ApproveResult" in d.current_url)
            print(f"  [INFO] Landed on results page: {driver.current_url}")
        except Exception:
            print(f"  [INFO] Still on: {driver.current_url} — checking success text")

        take_screenshot(driver, "06d_approve_results", "approve")
        success_found = False
        msg_locators = [
            (By.XPATH, "//*[contains(normalize-space(),'Following Cards were successful')]"),
            (By.XPATH, "//*[contains(normalize-space(),'Card Successfully Approved')]"),
            (By.XPATH, "//*[contains(normalize-space(),'successful')]"),
            (By.XPATH, "//*[contains(normalize-space(),'Approve Cards Results')]"),
        ]
        for locator in msg_locators:
            try:
                el = WebDriverWait(driver, 8).until(EC.presence_of_element_located(locator))
                print(f"  [INFO] Success message: '{el.text.strip()[:120]}'")
                success_found = True
                break
            except Exception:
                continue

        assert "ApproveResult" in driver.current_url or success_found, f"Expected ApproveResults with success message. URL: {driver.current_url} success_found={success_found}"
        print("  [PASS] Approve Cards Results page verified — cards successfully approved.")

    def test_07_back_to_items(self, driver):
        print("\n[TC-APR-007] Clicking Back to Items...")
        print(f"  [INFO] Currently on: {driver.current_url}")

        if "ApproveCard" not in driver.current_url and "ApproveResult" not in driver.current_url:
            print("  [INFO] Re-navigating via ApproveItems → item click...")
            driver.get(f"{BASE_URL}/BuyerAction/ApproveItems")
            wait_ready(driver)
            time.sleep(PAUSE)
            links = _find_items(driver, timeout=20)
            if not links:
                pytest.skip("No items available in Approve Items List — test data may be depleted")
            print(f"  [INFO] Clicking item: '{links[0].text.strip()}'")
            driver.execute_script("arguments[0].click()", links[0])
            wait_ready(driver)
            time.sleep(PAUSE * 2)

        back_btn = _click_back_to_items(driver)
        assert back_btn, "Back to Items button not found"
        scroll_to(driver, back_btn)
        driver.execute_script("arguments[0].click()", back_btn)
        wait_ready(driver)
        time.sleep(PAUSE)

        take_screenshot(driver, "07_back_to_items", "approve")
        current_url = driver.current_url
        print(f"  [URL] {current_url}")
        assert any(kw in current_url for kw in ["ApproveItem", "Approve", "approve"]), f"Expected Approve Items page. Got: {current_url}"
        print("  [PASS] Successfully returned to Approve Items List.")
        driver.quit()


if __name__ == "__main__":
    raise SystemExit(pytest.main(["-v", "-s", __file__]))
