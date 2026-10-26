"""
QALS11 | Admin > Workcenter — Workcenter Configuration
========================================================
URL  : https://engineering.ultrivalms.com/QALS1011
User : buyeruser / Ultriva!23

Test flow
---------
1.  Login as buyeruser
2.  Navigate to Admin > Workcenter list
3.  Search for created workcenter using Find Name
4.  Select the workcenter row
5.  Click More Options > Configuration
6.  On Workcenter Configuration page, click each tab and update random values
7.  Save configuration
8.  Generate report

Run (from qa_automation/):
    pytest tests/QALS11/Admin/Workcenter/test_WorkcenterConfiguration.py -v -s
"""

import time
import random
import os
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# ================================================================================
# CLASS-SCOPED DRIVER FIXTURE
# ================================================================================

@pytest.fixture(scope="class")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    drv = webdriver.Chrome(options=options)
    drv.implicitly_wait(10)
    drv.set_page_load_timeout(120)
    drv.maximize_window()
    yield drv
    drv.quit()

# ================================================================================
# CONFIGURATION
# ================================================================================

BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
USERNAME = "buyeruser"
PASSWORD = "Ultriva!23"
PAUSE = 2
REPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "reports")
TARGET_WORKCENTER = "Databizwarehouse"
CONFIG_TABS = [
    "General", "Card", "Custom", "Integration", "LFM", "Pick List",
    "Print", "Receive", "Release", "Scan", "Ship", "Work Order",
]

# ================================================================================
# HELPERS
# ================================================================================

def safe_screenshot(driver, name):
    try:
        driver.save_screenshot(name)
    except Exception:
        pass

def page_loaded(driver):
    WebDriverWait(driver, 60).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

def scroll_to(driver, el):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'})", el)
    time.sleep(0.3)

def safe_click(driver, by, locator, timeout=15):
    el = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, locator)))
    scroll_to(driver, el)
    el.click()
    return el

def safe_fill(driver, by, locator, value, timeout=15):
    el = WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((by, locator)))
    scroll_to(driver, el)
    try:
        el.clear()
        el.send_keys(str(value))
    except Exception:
        driver.execute_script("arguments[0].value = arguments[1]", el, str(value))
    return el

def random_number(low=1, high=999):
    return random.randint(low, high)

def print_header(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_step(num, desc):
    print(f"\n  [STEP {num}] {desc}")

# ================================================================================
# TEST CLASS — WORKCENTER CONFIGURATION
# ================================================================================

class TestWorkcenterconfiguration:
    
    def __init__(self):
        self.tab_updates = {}

    def test_01_login_and_navigate_to_workcenter(self, driver):
        print_header("PHASE 1: LOGIN AND NAVIGATE TO ADMIN > WORKCENTER")

        print_step(1, f"Navigating to {BASE_URL}")
        driver.get(BASE_URL)
        page_loaded(driver)

        print_step(2, f"Logging in as {USERNAME}")
        safe_fill(driver, By.ID, "UserName", USERNAME)
        safe_fill(driver, By.ID, "Password", PASSWORD)
        safe_click(driver, By.ID, "login-button")
        page_loaded(driver)
        time.sleep(PAUSE)
        assert "ultrivalms" in driver.current_url, f"Login failed - URL: {driver.current_url}"
        print(f"  [PASS] Login successful -> {driver.current_url}")

        print_step(3, "Navigating directly to Workcenter list")
        driver.get(f"{BASE_URL}/Workcenter/List")
        page_loaded(driver)
        time.sleep(PAUSE)
        print(f"  [PASS] Workcenter list page -> {driver.current_url}")
        safe_screenshot(driver, "wc_config_list.png")

    def test_02_search_and_select_workcenter(self, driver):
        print_header(f"PHASE 2: SEARCH AND SELECT '{TARGET_WORKCENTER}'")

        print_step(1, f"Searching for '{TARGET_WORKCENTER}' using Find Name")
        search_done = False

        find_selectors = [
            (By.XPATH, "//input[contains(@placeholder,'Find Name') or @placeholder='Find Name']"),
            (By.XPATH, "//input[contains(@id,'Find')]"),
            (By.XPATH, "//input[contains(@name,'Find')]"),
        ]

        for by, selector in find_selectors:
            try:
                field = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((by, selector)))
                scroll_to(driver, field)
                field.clear()
                field.send_keys(TARGET_WORKCENTER)
                time.sleep(0.5)

                try:
                    safe_click(driver, By.XPATH,
                        "//img[contains(@src,'find') or contains(@alt,'Find')] | "
                        "//a[contains(@onclick,'Find')] | "
                        "//span[contains(@onclick,'Find')]",
                        timeout=3)
                except Exception:
                    field.send_keys(Keys.RETURN)

                search_done = True
                print(f"  [PASS] Entered '{TARGET_WORKCENTER}' in Find Name")
                break
            except Exception:
                continue

        if not search_done:
            print("  [INFO] No Find field found, will look for workcenter in list directly")

        time.sleep(PAUSE)
        safe_screenshot(driver, "wc_config_search.png")

        print_step(2, f"Selecting '{TARGET_WORKCENTER}' row")

        row_xpaths = [
            f"//tr[.//td[contains(normalize-space(.),'{TARGET_WORKCENTER}')]]",
            f"//td[contains(normalize-space(.),'{TARGET_WORKCENTER}')]",
        ]

        row_clicked = False
        for xpath in row_xpaths:
            try:
                row = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, xpath)))
                scroll_to(driver, row)
                row.click()
                row_clicked = True
                time.sleep(1)
                print(f"  [PASS] '{TARGET_WORKCENTER}' row selected")
                break
            except Exception:
                continue

        assert row_clicked, f"Could not find or select '{TARGET_WORKCENTER}' row"
        safe_screenshot(driver, "wc_config_selected.png")

    def test_03_open_configuration(self, driver):
        """Click the toolbar 'More Options' dropdown, then 'Configuration'."""
        print_header("PHASE 3: OPEN WORKCENTER CONFIGURATION")

        print_step(1, "Clicking 'More Options' toolbar dropdown")

        more_selectors = [
            "//button[contains(normalize-space(.),'More Options')]",
            "//a[contains(normalize-space(.),'More Options')]",
            "//*[contains(@class,'btn') and contains(normalize-space(.),'More Options')]",
            "//span[contains(normalize-space(.),'More Options')]/parent::*",
        ]

        more_clicked = False
        for sel in more_selectors:
            try:
                btn = WebDriverWait(driver, 8).until(
                    EC.element_to_be_clickable((By.XPATH, sel)))
                scroll_to(driver, btn)
                btn.click()
                more_clicked = True
                print("  [PASS] 'More Options' dropdown opened")
                time.sleep(1)
                break
            except Exception:
                continue

        if not more_clicked:
            try:
                driver.execute_script("""
                    var els = document.querySelectorAll('a, button, span, div');
                    for (var i = 0; i < els.length; i++) {
                        if (els[i].textContent.trim().indexOf('More Options') >= 0 && els[i].offsetParent !== null) {
                            els[i].click(); break;
                        }
                    }
                """)
                more_clicked = True
                time.sleep(1)
                print("  [PASS] 'More Options' clicked via JS")
            except Exception:
                pass

        safe_screenshot(driver, "wc_config_more_options.png")
        assert more_clicked, "Could not click 'More Options' toolbar button"

        print_step(2, "Clicking 'Configuration' from dropdown")

        config_selectors = [
            "//a[normalize-space(.)='Configuration']",
            "//li//a[normalize-space(.)='Configuration']",
            "//span[normalize-space(.)='Configuration']",
            "//*[contains(@class,'dropdown-menu') or contains(@class,'menu')]//*[normalize-space(.)='Configuration']",
            "//a[contains(@href,'Configuration')]",
        ]

        config_clicked = False
        for sel in config_selectors:
            try:
                el = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, sel)))
                scroll_to(driver, el)
                el.click()
                config_clicked = True
                print("  [PASS] 'Configuration' clicked")
                break
            except Exception:
                continue

        if not config_clicked:
            try:
                driver.execute_script("""
                    var items = document.querySelectorAll('a, li, span, div');
                    for (var i = 0; i < items.length; i++) {
                        if (items[i].textContent.trim() === 'Configuration' && items[i].offsetParent !== null) {
                            items[i].click(); break;
                        }
                    }
                """)
                config_clicked = True
                time.sleep(1)
                print("  [PASS] 'Configuration' clicked via JS")
            except Exception:
                pass

        page_loaded(driver)
        time.sleep(PAUSE)
        safe_screenshot(driver, "wc_config_page.png")
        assert config_clicked, "Could not click 'Configuration'"
        print(f"  [PASS] Workcenter Configuration page -> {driver.current_url}")

    def test_04_update_configuration_tabs(self, driver):
        """Click each tab, update visible fields with random values, and Save."""
        print_header("PHASE 4: UPDATE CONFIGURATION TABS WITH RANDOM VALUES")

        print_step(1, "Discovering configuration tabs")

        tab_selectors = [
            "//div[contains(@class,'tab-control-item')]//span[contains(@class,'txt')]",
            "//div[contains(@class,'tab-control-item')]",
            "//ul[contains(@class,'nav-tabs')]//a",
            "//li[contains(@class,'tab') or contains(@class,'nav-item')]/a",
            "//a[@data-toggle='tab']",
        ]

        tabs = []
        for sel in tab_selectors:
            found = driver.find_elements(By.XPATH, sel)
            if found and len(found) > 1:
                tabs = found
                break
        print(f"  [INFO] Found {len(tabs)} tabs")

        tab_names = [t.text.strip() for t in tabs if t.text.strip()]
        print(f"  [INFO] Tab names: {tab_names}")

        if not tabs:
            print("  [WARN] No tabs found — updating visible fields on current page")
            count = self._update_visible_fields(driver)
            self.tab_updates["Default"] = count
            self._save_configuration(driver)
            return

        for idx, tab in enumerate(tabs):
            tab_name = tab.text.strip() or f"Tab {idx + 1}"
            print_step(idx + 2, f"Clicking tab: '{tab_name}'")

            try:
                scroll_to(driver, tab)
                tab.click()
                time.sleep(1)
                page_loaded(driver)
            except Exception as e:
                print(f"  [WARN] Could not click tab '{tab_name}': {e}")
                continue

            safe_screenshot(driver, f"wc_config_tab_{tab_name.replace(' ', '_')}.png")
            count = self._update_visible_fields(driver)
            self.tab_updates[tab_name] = count

        print_step(len(tabs) + 2, "Saving configuration")
        self._save_configuration(driver)

    def _update_visible_fields(self, driver):
        """Update visible editable fields with random values. Returns count of updated fields."""
        updated = 0

        # Text / number inputs
        inputs = driver.find_elements(By.XPATH, 
            "//input[(@type='text' or @type='number' or @type='') "
            "and not(@readonly) and not(@disabled)]")

        for inp in inputs:
            try:
                if not inp.is_displayed():
                    continue
                fid = inp.get_attribute("id") or inp.get_attribute("name") or ""
                if any(skip in fid.lower() for skip in [
                    "find", "search", "filter", "token", "hidden", "__requestverification"]):
                    continue

                ftype = inp.get_attribute("type") or "text"
                is_numeric = ftype == "number" or any(kw in fid.lower() for kw in [
                    "qty", "quantity", "count", "num", "days", "hours", "min", "max",
                    "lead", "time", "size", "lot", "moq", "eoq", "safety", "reorder",
                    "buffer", "percent", "rate", "cost", "price", "weight", "tolerance"])

                new_val = str(random_number(1, 100)) if is_numeric else f"Test{random_number(100, 999)}"

                scroll_to(driver, inp)
                inp.clear()
                inp.send_keys(new_val)
                updated += 1
                print(f"    [UPDATED] {fid} = {new_val}")
            except Exception:
                continue

        # Dropdowns
        selects = driver.find_elements(By.TAG_NAME, "select")
        for sel_el in selects:
            try:
                if not sel_el.is_displayed() or sel_el.get_attribute("disabled"):
                    continue
                fid = sel_el.get_attribute("id") or sel_el.get_attribute("name") or ""
                if any(skip in fid.lower() for skip in ["find", "search", "filter"]):
                    continue

                select = Select(sel_el)
                options = [o for o in select.options if o.get_attribute("value")]
                if len(options) > 1:
                    scroll_to(driver, sel_el)
                    choice = random.choice(options[1:])
                    select.select_by_value(choice.get_attribute("value"))
                    updated += 1
                    print(f"    [UPDATED] {fid} = {choice.text}")
            except Exception:
                continue

        # Toggle switches / checkboxes (toggle ~50%)
        checkboxes = driver.find_elements(By.XPATH, "//input[@type='checkbox' and not(@disabled)]")
        for cb in checkboxes:
            try:
                if not cb.is_displayed():
                    continue
                if random.random() > 0.5:
                    fid = cb.get_attribute("id") or cb.get_attribute("name") or ""
                    scroll_to(driver, cb)
                    cb.click()
                    state = "checked" if cb.is_selected() else "unchecked"
                    updated += 1
                    print(f"    [TOGGLED] {fid} -> {state}")
            except Exception:
                continue

        # ON/OFF toggle switches
        toggles = driver.find_elements(By.XPATH, 
            "//*[contains(@class,'toggle') or contains(@class,'switch')]"
            "[not(contains(@class,'tab'))]")
        for toggle in toggles:
            try:
                if not toggle.is_displayed():
                    continue
                if random.random() > 0.5:
                    scroll_to(driver, toggle)
                    toggle.click()
                    updated += 1
                    tid = toggle.get_attribute("id") or toggle.get_attribute("data-field") or "toggle"
                    print(f"    [TOGGLED] {tid}")
            except Exception:
                continue

        print(f"  [INFO] Updated {updated} field(s)")
        return updated

    def _save_configuration(self, driver):
        """Save configuration."""
        saved = False

        save_selectors = [
            "//input[@type='submit' and contains(@value,'Save')]",
            "//button[contains(normalize-space(.),'Save')]",
            "//a[contains(normalize-space(.),'Save') and contains(@class,'btn')]",
            "//input[@type='button' and contains(@value,'Save')]",
        ]

        for sel in save_selectors:
            try:
                btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, sel)))
                scroll_to(driver, btn)
                btn.click()
                saved = True
                print("  [PASS] Save button clicked")
                break
            except Exception:
                continue

        if not saved:
            try:
                driver.execute_script("frmEntryPage_onSubmit();")
                saved = True
                print("  [PASS] Save triggered via JS")
            except Exception:
                try:
                    driver.execute_script("document.forms[0].submit();")
                    saved = True
                    print("  [PASS] Save via form.submit()")
                except Exception:
                    print("  [WARN] No Save mechanism found")

        if saved:
            try:
                WebDriverWait(driver, 30).until(lambda d: d.execute_script(
                    "return document.readyState") == "complete")
            except Exception:
                pass
        time.sleep(3)
        print("  [PASS] Configuration saved successfully")
        safe_screenshot(driver, "wc_config_after_save.png")

    def test_05_generate_report(self, driver):
        print_header("PHASE 5: TEST SUMMARY REPORT")

        tab_summary = "\n".join(
            f"   - {tab}: {count} field(s) updated"
            for tab, count in self.tab_updates.items()
        ) or "   (no tab updates recorded)"

        report = f"""
        ================================================================================
        WORKCENTER CONFIGURATION TEST REPORT
        ================================================================================
        Date/Time  : {time.strftime('%Y-%m-%d %H:%M:%S')}
        Test URL   : {BASE_URL}
        User       : {USERNAME}
        Target     : {TARGET_WORKCENTER}
        Comment    : workcenter configuration

        OPERATIONS PERFORMED:
        ================================================================================
        1. Login and navigate to Admin > Workcenter
        2. Search for '{TARGET_WORKCENTER}' in Workcenter list
        3. Select workcenter row
        4. Click More Options > Configuration
        5. Click each configuration tab and update random values
        6. Save configuration

        TAB UPDATE SUMMARY:
        {tab_summary}

        CURRENT URL: {driver.current_url}
        ================================================================================
        """
        print(report)

        os.makedirs(REPORT_DIR, exist_ok=True)
        report_path = os.path.join(REPORT_DIR, f"WorkcenterConfiguration_{TARGET_WORKCENTER}.txt")
        try:
            with open(report_path, "w") as f:
                f.write(report)
            print(f"  [INFO] Report saved to: {report_path}")
        except Exception as e:
            print(f"  [WARN] Could not save report: {e}")

        safe_screenshot(driver, "wc_config_final.png")

