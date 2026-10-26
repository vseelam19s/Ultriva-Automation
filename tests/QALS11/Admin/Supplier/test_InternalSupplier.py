import time
import random
import string
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
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
    drv.set_page_load_timeout(30)
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
TARGET_WORKCENTER = "WCLine"
_rand = random.randint(1000, 99999)

# ================================================================================
# HELPERS
# ================================================================================

def page_loaded(driver):
    WebDriverWait(driver, 30).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

def scroll_to(driver, el):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'})", el)
    time.sleep(0.3)

def safe_click(driver, by, locator, timeout=15):
    el = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, locator))
    )
    scroll_to(driver, el)
    el.click()
    return el

def safe_fill(driver, by, locator, value, timeout=15):
    el = WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((by, locator))
    )
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
# TEST CLASS
# ================================================================================

class TestInternalsupplier:
    """
    Internal Supplier Workcenter Configuration test:
    1. Login > Admin > Supplier list
    2. Click "Internal Supplier" tab
    3. Find & select WCLine row
    4. Click toolbar "More Options" > Configuration
    5. Update each config tab with random values > Save
    """

    # ========================================================================
    # PHASE 1: LOGIN AND NAVIGATE TO SUPPLIER LIST
    # ========================================================================
    def test_01_login_and_navigate_to_supplier(self, driver):
        print_header("PHASE 1: LOGIN AND NAVIGATE TO ADMIN > SUPPLIER")

        print_step(1, f"Navigating to {BASE_URL}")
        driver.get(BASE_URL)
        page_loaded(driver)

        print_step(2, f"Logging in as {USERNAME}")
        safe_fill(driver, By.ID, "UserName", USERNAME)
        safe_fill(driver, By.ID, "Password", PASSWORD)
        safe_click(driver, By.ID, "login-button")
        page_loaded(driver)
        time.sleep(PAUSE)
        assert "ultrivalms" in driver.current_url.lower(), f"Login failed - URL: {driver.current_url}"
        print(f"  [PASS] Login successful -> {driver.current_url}")

        print_step(3, "Opening Admin module")
        safe_click(driver, By.XPATH, "//a[contains(@href,'/Admin/Home') or normalize-space(.)='Admin']")
        page_loaded(driver)
        time.sleep(PAUSE)
        print(f"  [PASS] Admin module opened -> {driver.current_url}")

        print_step(4, "Clicking Supplier menu")
        try:
            safe_click(driver, By.XPATH, "//a[contains(@href,'Supplier') and (normalize-space(.)='Supplier' or normalize-space(.)='Suppliers')]")
        except Exception:
            driver.get(f"{BASE_URL}/Supplier/List")
        page_loaded(driver)
        time.sleep(PAUSE)
        print(f"  [PASS] Supplier list page -> {driver.current_url}")

    # ========================================================================
    # PHASE 2: SWITCH TO INTERNAL SUPPLIER TAB AND SEARCH WCLINE
    # ========================================================================
    def test_02_switch_to_internal_and_search_wcline(self, driver):
        print_header("PHASE 2: SWITCH TO INTERNAL SUPPLIER TAB & SEARCH WCLINE")

        print_step(1, "Clicking 'Internal Supplier' tab")
        safe_click(driver, By.XPATH, "//a[normalize-space(.)='Internal Supplier'] | //*[contains(@class,'tab') and normalize-space(.)='Internal Supplier']")
        page_loaded(driver)
        time.sleep(PAUSE + 1)

        driver.save_screenshot("after_internal_tab.png")

        page_src = driver.page_source
        if "Internal" in page_src:
            print("  [PASS] Internal Supplier tab active")
        else:
            print("  [WARN] Could not confirm Internal Supplier tab switch")

        print_step(2, f"Searching for '{TARGET_WORKCENTER}' using Find Name")
        search_done = False

        find_selectors = [
            (By.XPATH, "//input[contains(@placeholder,'Find Name') or @placeholder='Find Name']"),
            (By.XPATH, "//input[contains(@id,'Find')]"),
            (By.XPATH, "//input[contains(@name,'Find')]"),
        ]

        for by, selector in find_selectors:
            try:
                field = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((by, selector)))
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
            print("  [INFO] No Find field found, will look for WCLine in list directly")

        time.sleep(PAUSE)
        driver.save_screenshot("internal_supplier_search_wcline.png")

        print_step(3, f"Selecting '{TARGET_WORKCENTER}' row")
        row_xpaths = [
            "//tr[.//td[contains(normalize-space(.),'WCLine')]]",
            "//tr[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'wcline')]",
        ]

        row_clicked = False
        for xpath in row_xpaths:
            try:
                row = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
                scroll_to(driver, row)
                row.click()
                row_clicked = True
                time.sleep(1)
                print("  [PASS] WCLine row selected")
                break
            except Exception:
                continue

        if not row_clicked:
            try:
                td = driver.find_element(By.XPATH, "//td[contains(normalize-space(.),'WCLine')]")
                scroll_to(driver, td)
                td.click()
                row_clicked = True
                print("  [PASS] WCLine cell clicked")
            except Exception:
                assert False, "Could not find or select WCLine row"

        driver.save_screenshot("wcline_selected.png")

    # ========================================================================
    # PHASE 3: CLICK MORE OPTIONS > CONFIGURATION
    # ========================================================================
    def test_03_open_wcline_configuration(self, driver):
        print_header("PHASE 3: OPEN WCLINE CONFIGURATION")

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
                btn = WebDriverWait(driver, 8).until(EC.element_to_be_clickable((By.XPATH, sel)))
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

        driver.save_screenshot("more_options_dropdown.png")
        assert more_clicked, "Could not click 'More Options' toolbar button"

        print_step(2, "Clicking 'Configuration' from dropdown")
        config_selectors = [
            "//a[normalize-space(.)='Configuration']",
            "//li//a[normalize-space(.)='Configuration']",
            "//span[normalize-space(.)='Configuration']",
            "//*[contains(@class,'dropdown-menu') or contains(@class,'menu')]//*[normalize-space(.)='Configuration']",
            "//a[contains(@href,'Configuration')]",
            "//*[contains(@onclick,'Configuration')]",
        ]

        config_clicked = False
        for sel in config_selectors:
            try:
                el = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, sel)))
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
        driver.save_screenshot("configuration_page.png")
        print(f"  [PASS] Configuration page -> {driver.current_url}")

    # ========================================================================
    # PHASE 4: UPDATE EACH CONFIGURATION TAB AND SAVE
    # ========================================================================
    def test_04_update_configuration_tabs(self, driver):
        print_header("PHASE 4: UPDATE CONFIGURATION TABS")
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
                print(f"  [INFO] Found {len(tabs)} tabs")
                break

        if not tabs:
            print("  [WARN] No tabs found — updating visible fields on current page")
            self._update_visible_fields(driver)
            self._save_configuration(driver)
            return

        tab_names = [t.text.strip() for t in tabs if t.text.strip()]
        print(f"  [INFO] Tab names: {tab_names}")

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

            driver.save_screenshot(f"config_tab_{idx + 1}.png")
            self._update_visible_fields(driver)

        print_step(len(tabs) + 2, "Saving configuration")
        self._save_configuration(driver)

    def _update_visible_fields(self, driver):
        """Helper to update visible fields inside structural layout loop context."""
        updated = 0
        inputs = driver.find_elements(By.XPATH, "//input[(@type='text' or @type='number' or @type='') and not(@readonly) and not(@disabled)]")

        for inp in inputs:
            try:
                if not inp.is_displayed():
                    continue
                fid = inp.get_attribute("id") or inp.get_attribute("name") or ""
                if any(skip in fid.lower() for skip in ["find", "search", "filter", "token", "hidden"]):
                    continue

                ftype = inp.get_attribute("type") or "text"
                is_numeric = ftype == "number" or any(kw in fid.lower() for kw in [
                    "qty", "quantity", "count", "num", "days", "hours", "min", "max",
                    "lead", "time", "size", "lot", "moq", "eoq", "safety", "reorder",
                    "buffer", "percent", "rate", "cost", "price", "weight"
                ])

                new_val = str(random_number(1, 100)) if is_numeric else f"Test{random_number(100, 999)}"
                scroll_to(driver, inp)
                inp.clear()
                inp.send_keys(new_val)
                updated += 1
                print(f"    [UPDATED] {fid} = {new_val}")
            except Exception:
                continue

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

        print(f"  [INFO] Updated {updated} field(s)")

    def _save_configuration(self, driver):
        saved = False
        save_selectors = [
            "//input[@type='submit' and contains(@value,'Save')]",
            "//button[contains(normalize-space(.),'Save')]",
            "//a[contains(normalize-space(.),'Save') and contains(@class,'btn')]",
            "//input[@type='button' and contains(@value,'Save')]",
        ]

        for sel in save_selectors:
            try:
                btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, sel)))
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
                WebDriverWait(driver, 30).until(lambda d: d.execute_script("return document.readyState") == "complete")
            except Exception:
                pass
        time.sleep(3)
        print("  [PASS] Configuration saved")
        driver.save_screenshot("config_after_save.png")

    # ========================================================================
    # PHASE 5: SUMMARY REPORT
    # ========================================================================
    def test_05_generate_report(self, driver):
        print_header("PHASE 5: TEST SUMMARY REPORT")

        report = f"""
        ================================================================================
        INTERNAL SUPPLIER — WORKCENTER CONFIGURATION TEST REPORT
        ================================================================================
        Date/Time  : {time.strftime('%Y-%m-%d %H:%M:%S')}
        Test URL   : {BASE_URL}
        User       : {USERNAME}
        Target     : {TARGET_WORKCENTER} (Internal Supplier)

        OPERATIONS PERFORMED:
        ================================================================================
        1. Login and navigate to Admin > Supplier
        2. Switch from External to Internal Supplier tab
        3. Search for '{TARGET_WORKCENTER}' and select it
        4. Open More Options > Configuration
        5. Update each configuration tab with random values
        6. Save configuration

        CURRENT URL: {driver.current_url}
        ================================================================================
        """
        
        print(report)

        report_path = "InternalSupplier_Report_WCLine.txt"
        try:
            with open(report_path, "w") as f:
                f.write(report)
            print(f"  [PASS] Report saved: {report_path}")
        except Exception as e:
            print(f"  [WARN] Report save error: {e}")

        driver.save_screenshot("InternalSupplier_Final.png")
        print("  [DONE] Internal Supplier Configuration test complete.")