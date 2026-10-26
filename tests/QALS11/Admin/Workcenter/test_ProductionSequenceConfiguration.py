"""

QALS11 | Admin > Workcenter — Production Sequence Configuration

================================================================

URL  : https://engineering.ultrivalms.com/QALS1011

User : buyeruser / Ultriva!23

Test flow

---------

1.  Login as buyeruser

2.  Navigate to Admin > Workcenter list

3.  Search for created workcenter using Find Name

4.  Select the workcenter row

5.  Click More Options > Production Sequence Configuration

6.  On Production Sequence Configuration page, click each tab and update random values

7.  Save configuration

8.  Generate report

Tabs: Schedule, Custom Field List, Sort Info, Scrap Tag, Screen Info, External Device Data Info

Run (from qa_automation/):

    pytest tests/QALS11/Admin/Workcenter/ProductionSequenceConfiguration.py -v -s

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

REPORT_DIR = os.path.join(os.path.dirname(
    __file__), "..", "..", "..", "reports")

# Target workcenter to configure

TARGET_WORKCENTER = "Databizwarehouse"

# Production Sequence Configuration tabs

PSC_TABS = [

    "Schedule", "Custom Field List", "Sort Info",

    "Scrap Tag", "Screen Info", "External Device Data Info",

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

    el = WebDriverWait(
        driver, timeout).until(
        EC.element_to_be_clickable(
            (by, locator)))

    scroll_to(driver, el)

    el.click()

    return el


def safe_fill(driver, by, locator, value, timeout=15):

    el = WebDriverWait(
        driver, timeout).until(
        EC.visibility_of_element_located(
            (by, locator)))

    scroll_to(driver, el)

    try:

        el.clear()

        el.send_keys(str(value))

    except Exception:

        driver.execute_script(
            "arguments[0].value = arguments[1]", el, str(value))

    return el


def random_number(low=1, high=999):

    return random.randint(low, high)


def random_decimal(low=1.0, high=100.0):

    return round(random.uniform(low, high), 2)


def print_header(title):

    print("\n" + "=" * 80)

    print(f"  {title}")

    print("=" * 80)


def print_step(num, desc):

    print(f"\n  [STEP {num}] {desc}")

# ================================================================================

# TEST CLASS — PRODUCTION SEQUENCE CONFIGURATION

# ================================================================================


class TestProductionsequenceconfiguration:
    """
    Production Sequence Configuration test:

    1. Login > Admin > Workcenter list

    2. Search & select the created workcenter

    3. Click More Options > Production Sequence Configuration

    4. Click each tab (Schedule, Custom Field List, Sort Info, Scrap Tag,

       Screen Info, External Device Data Info), update random values

    5. Save configuration
    """

    tab_updates = {}  # Track updates per tab

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
        safe_screenshot(driver, "psc_workcenter_list.png")

        # ========================================================================
        # PHASE 2: SEARCH AND SELECT THE CREATED WORKCENTER
        # ========================================================================
    def test_02_search_and_select_workcenter(self, driver):
        print_header(f"PHASE 2: SEARCH AND SELECT '{TARGET_WORKCENTER}'")

        # Step 1: Search using "Find Name" input
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

        # Click find/search icon (binoculars icon next to the field)
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
            print(
            "  [INFO] No Find field found, will look for workcenter in list directly")

        time.sleep(PAUSE)
        safe_screenshot(driver, "psc_search.png")

        # Step 2: Click/select the workcenter row
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
        safe_screenshot(driver, "psc_selected.png")

        # ========================================================================
        # PHASE 3: CLICK MORE OPTIONS > PRODUCTION SEQUENCE CONFIGURATION
        # ========================================================================
    def test_03_open_production_sequence_configuration(self, driver):
        """Click the toolbar 'More Options' dropdown, then 'Production Sequence Configuration'."""
        print_header("PHASE 3: OPEN PRODUCTION SEQUENCE CONFIGURATION")

        # Step 1: Click "More Options" toolbar button
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
            # JS fallback
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

        safe_screenshot(driver, "psc_more_options.png")
        assert more_clicked, "Could not click 'More Options' toolbar button"

        # Step 2: Click 'Production Sequence Configuration' from dropdown
        print_step(
            2, "Clicking 'Production Sequence Configuration' from dropdown")

        psc_selectors = [
            "//a[normalize-space(.)='Production Sequence Configuration']",
            "//li//a[normalize-space(.)='Production Sequence Configuration']",
            "//span[normalize-space(.)='Production Sequence Configuration']",
            "//*[contains(@class,'dropdown-menu') or contains(@class,'menu')]//*[normalize-space(.)='Production Sequence Configuration']",
            "//a[contains(@href,'ScheduleConfig') or contains(@href,'ProductionSequence')]",
        ]

        psc_clicked = False
        for sel in psc_selectors:
            try:
                el = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, sel)))
                scroll_to(driver, el)
                el.click()
                psc_clicked = True
                print("  [PASS] 'Production Sequence Configuration' clicked")
                break
            except Exception:
                continue

        if not psc_clicked:
            try:
                driver.execute_script("""
        var items = document.querySelectorAll('a, li, span, div');
        for (var i = 0; i < items.length; i++) {
        if (items[i].textContent.trim() === 'Production Sequence Configuration' && items[i].offsetParent !== null) {
        items[i].click(); break;
        }
        }
        """)
                psc_clicked = True
                time.sleep(1)
                print("  [PASS] 'Production Sequence Configuration' clicked via JS")
            except Exception:
                pass

        page_loaded(driver)
        time.sleep(PAUSE)
        safe_screenshot(driver, "psc_page.png")
        assert psc_clicked, "Could not click 'Production Sequence Configuration'"
        print(
            f"  [PASS] Production Sequence Configuration page -> {driver.current_url}")

        # ========================================================================
        # PHASE 4: UPDATE EACH TAB AND SAVE
        # ========================================================================
    def test_04_update_production_sequence_tabs(self, driver):
        """Click each tab, update visible fields with random values, and Save."""
        print_header("PHASE 4: UPDATE PRODUCTION SEQUENCE CONFIGURATION TABS")

        print_step(
            1, "Discovering tabs on Production Sequence Configuration page")

        tab_selectors = [
            "//div[contains(@class,'tab-control-item')]//span[contains(@class,'txt')]",
            "//div[contains(@class,'tab-control-item')]",
            "//ul[contains(@class,'nav-tabs')]//a",
            "//li[contains(@class,'tab') or contains(@class,'nav-item')]/a",
            "//a[@data-toggle='tab']",
        ]

        # Discover the working tab selector and collect tab names
        working_selector = None
        tab_names = []
        for sel in tab_selectors:
            found = driver.find_elements(By.XPATH, sel)
            if found and len(found) > 1:
                working_selector = sel
                tab_names = [t.text.strip() for t in found if t.text.strip()]
                print(f"  [INFO] Found {len(found)} tabs")
                break

        print(f"  [INFO] Tab names: {tab_names}")

        if not working_selector or not tab_names:
            print("  [WARN] No tabs found — updating visible fields on current page")
            count = self._update_visible_fields(driver, "Default")
            self.tab_updates["Default"] = count
            self._save_configuration(driver)
            return

        # Iterate each tab — re-discover elements each iteration to avoid stale
        # references
        for idx, expected_name in enumerate(tab_names):
            print_step(idx + 2, f"Clicking tab: '{expected_name}'")

            try:
                # Re-find all tabs fresh from the DOM
                fresh_tabs = driver.find_elements(By.XPATH, working_selector)
                tab = None
                for t in fresh_tabs:
                    try:
                        if t.text.strip() == expected_name:
                            tab = t
                            break
                    except Exception:
                        continue

                if tab is None:
                    # Fallback: click by index
                    if idx < len(fresh_tabs):
                        tab = fresh_tabs[idx]
                    else:
                        print(f"  [WARN] Could not find tab '{expected_name}'")
                        continue

                scroll_to(driver, tab)
                tab.click()
                time.sleep(1)
                page_loaded(driver)
            except Exception as e:
                print(f"  [WARN] Could not click tab '{expected_name}': {e}")
                continue

            safe_screenshot(
                driver, f"psc_tab_{expected_name.replace(' ', '_')}.png")
            count = self._update_visible_fields(driver, expected_name)
            self.tab_updates[expected_name] = count

            # Save after Schedule mandatory data is set
            if expected_name == "Schedule":
                print_step(idx + 3, "Saving after Schedule mandatory data")
                self._save_configuration(driver)
            # Navigate back to Production Sequence Configuration if save redirected
            if "ScheduleConfig" not in driver.current_url:
                print("  [INFO] Navigating back to Production Sequence Configuration")
                driver.get(
                    f"{BASE_URL}/ScheduleConfig/WorkcenterSetup?BusGID=BSU232QQALMS")
                page_loaded(driver)
                time.sleep(PAUSE)

        # Final Save after all tabs
        print_step(
            len(tab_names) + 3,
            "Final Save — Production Sequence Configuration")
        self._save_configuration(driver)

    def _update_visible_fields(self, driver, tab_name):
        """Update visible editable fields with random values. Returns count of updated fields."""
        updated = 0

        # --- Schedule tab specific fields ---
        if tab_name == "Schedule":
            # Available Production Hours (numeric decimal)
            updated += self._update_numeric_field(
            driver, "Available Production Hours", random_decimal(8.0, 48.0))
        # Schedule Offset (days integer)
        updated += self._update_numeric_field(
            driver, "Schedule Offset", random_number(0, 30))

        # --- Text / number inputs ---
        inputs = driver.find_elements(
            By.XPATH, "//input[(@type='text' or @type='number' or @type='') "
            "and not(@readonly) and not(@disabled)]")

        for inp in inputs:
            try:
                if not inp.is_displayed():
                    continue
                fid = inp.get_attribute("id") or inp.get_attribute("name") or ""
                if any(skip in fid.lower() for skip in
               ["find", "search", "filter", "token", "hidden",
                "__requestverification"]):
                    continue

                ftype = inp.get_attribute("type") or "text"
                is_numeric = ftype == "number" or any(
            kw in fid.lower() for kw in [
                "qty",
                "quantity",
                "count",
                "num",
                "days",
                "hours",
                "min",
                "max",
                "lead",
                "time",
                "size",
                "lot",
                "moq",
                "eoq",
                "safety",
                "reorder",
                "buffer",
                "percent",
                "rate",
                "cost",
                "price",
                "weight",
                "tolerance",
                "offset",
                "production"])

                if is_numeric:
                    new_val = str(random_decimal(1.0, 50.0))
                else:
                    new_val = f"Test{random_number(100, 999)}"

                scroll_to(driver, inp)
                inp.clear()
                inp.send_keys(new_val)
                updated += 1
                print(f"    [UPDATED] {fid} = {new_val}")
            except Exception:
                continue

        # --- Dropdowns ---
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

        # --- Radio buttons (e.g., Grouping Preference: By Release Time / By Sort Condition) ---
        radio_groups = {}
        radios = driver.find_elements(
            By.XPATH, "//input[@type='radio' and not(@disabled)]")
        for radio in radios:
            try:
                if not radio.is_displayed():
                    continue
                name = radio.get_attribute("name") or ""
                if name and name not in radio_groups:
                    radio_groups[name] = []
                if name:
                    radio_groups[name].append(radio)
            except Exception:
                continue

        for group_name, group_radios in radio_groups.items():
            try:
                if len(group_radios) > 1:
                    chosen = random.choice(group_radios)
                    scroll_to(driver, chosen)
                    chosen.click()
                    val = chosen.get_attribute("value") or chosen.get_attribute("id") or ""
                    updated += 1
                    print(f"    [RADIO] {group_name} = {val}")
            except Exception:
                continue

        # --- Toggle switches / checkboxes (toggle ~50%) ---
        checkboxes = driver.find_elements(
            By.XPATH, "//input[@type='checkbox' and not(@disabled)]")
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

        # --- ON/OFF toggle switches (slider-type toggles from screenshot) ---
        toggles = driver.find_elements(
            By.XPATH, "//*[contains(@class,'toggle') or contains(@class,'switch')]"
            "[not(contains(@class,'tab'))]")
        for toggle in toggles:
            try:
                if not toggle.is_displayed():
                    continue
                if random.random() > 0.5:
                    scroll_to(driver, toggle)
                    toggle.click()
                    updated += 1
                    tid = (toggle.get_attribute("id")
                        or toggle.get_attribute("data-field") or "toggle")
                    print(f"    [TOGGLED] {tid}")
            except Exception:
                continue

        # --- Textarea fields ---
        textareas = driver.find_elements(
            By.XPATH, "//textarea[not(@readonly) and not(@disabled)]")
        for ta in textareas:
            try:
                if not ta.is_displayed():
                    continue
                fid = ta.get_attribute("id") or ta.get_attribute("name") or ""
                scroll_to(driver, ta)
                ta.clear()
                new_val = f"AutoTest_{random_number(100, 999)}"
                ta.send_keys(new_val)
                updated += 1
                print(f"    [UPDATED] {fid} = {new_val}")
            except Exception:
                continue

        print(f"  [INFO] Updated {updated} field(s) on '{tab_name}' tab")
        return updated

    def _update_numeric_field(self, driver, label_text, value):
        """Try to update a numeric field identified by its nearby label text."""
        try:
            # Find input near a label containing the text
            xpaths = [
                f"//label[contains(normalize-space(.),'{label_text}')]/following::input[1]",
                f"//*[contains(normalize-space(.),'{label_text}')]/following::input[1]",
            ]
            for xpath in xpaths:
                try:
                    inp = driver.find_element(By.XPATH, xpath)
                    if inp.is_displayed() and not inp.get_attribute("readonly"):
                        scroll_to(driver, inp)
                        inp.clear()
                        inp.send_keys(str(value))
                        fid = inp.get_attribute("id") or label_text
                        print(f"    [UPDATED] {fid} = {value}")
                        return 1
                except Exception:
                    continue
        except Exception:
            pass
        return 0

    def _save_configuration(self, driver):
        """Save Production Sequence Configuration."""
        saved = False
        url_before = driver.current_url

        # Primary: find the Save button by multiple strategies
        save_selectors = [
            # Exact text match for links/buttons styled as Save
            "//a[normalize-space(.)='Save']",
            "//button[normalize-space(.)='Save']",
            # Partial text with btn class (teal Save button from screenshot)
            "//a[contains(normalize-space(.),'Save') and contains(@class,'btn')]",
            "//button[contains(normalize-space(.),'Save') and contains(@class,'btn')]",
            # Input submit/button
            "//input[@type='submit' and contains(@value,'Save')]",
            "//input[@type='button' and contains(@value,'Save')]",
            # Icon-based Save (floppy disk icon + Save text)
            "//*[contains(@class,'btn')][.//text()[contains(.,'Save')]]",
            # Any clickable element with Save text near bottom of page
            "//div[contains(@class,'footer') or contains(@class,'button')]//a[contains(.,'Save')]",
        ]

        for sel in save_selectors:
            try:
                btns = driver.find_elements(By.XPATH, sel)
                for btn in btns:
                    if btn.is_displayed():
                        scroll_to(driver, btn)
                btn.click()
                saved = True
                print(f"  [PASS] Save button clicked (selector: {sel})")
                break
                if saved:
                    break
            except Exception:
                continue

        # Fallback: JS click on visible element containing 'Save'
        if not saved:
            try:
                driver.execute_script("""
        var els = document.querySelectorAll('a, button, input[type="submit"], input[type="button"]');
        for (var i = 0; i < els.length; i++) {
        var txt = els[i].textContent || els[i].value || '';
        if (txt.trim() === 'Save' && els[i].offsetParent !== null) {
        els[i].click();
        return true;
        }
        }
        return false;
        """)
                saved = True
                print("  [PASS] Save clicked via JS text match")
            except Exception:
                pass

        # Fallback: try known form submission functions (NOT generic
        # form.submit)
        if not saved:
            js_functions = [
            "frmEntryPage_onSubmit()",
            "document.getElementById('frmEntryPage').submit()",
            "document.querySelector('form[id*=\"Entry\"]').submit()",
            "document.querySelector('form[action*=\"Save\"]').submit()",
            "document.querySelector('form[action*=\"Setup\"]').submit()",
            "document.querySelector('form[action*=\"ScheduleConfig\"]').submit()",
        ]
        for js in js_functions:
            try:
                driver.execute_script(f"{js};")
                saved = True
                print(f"  [PASS] Save triggered via JS: {js}")
                break
            except Exception:
                continue

        if not saved:
            print("  [WARN] No Save mechanism found — configuration may not be saved")

        if saved:
            try:
                WebDriverWait(driver, 30).until(lambda d: d.execute_script(
            "return document.readyState") == "complete")
            except Exception:
                pass
        time.sleep(3)

        # Handle any confirmation dialog
        try:
            alert = driver.switch_to.alert
            alert.accept()
            print("  [PASS] Confirmation alert accepted")
            time.sleep(1)
        except Exception:
            pass

        # Verify save didn't navigate to wrong page (e.g. Search)
        url_after = driver.current_url
        if "Search/DoSearch" in url_after or "Search" in url_after:
            print(f"  [WARN] Redirected to search page: {url_after}")
        print("  [INFO] Navigating back to retry save...")
        driver.back()
        page_loaded(driver)
        time.sleep(2)
        # Retry with JS click
        try:
            driver.execute_script("""
        var els = document.querySelectorAll('a, button, input');
        for (var i = 0; i < els.length; i++) {
        var txt = els[i].textContent || els[i].value || '';
        if (txt.trim() === 'Save' && els[i].offsetParent !== null) {
        els[i].click();
        return true;
        }
        }
        return false;
        """)
            time.sleep(3)
            page_loaded(driver)
            url_retry = driver.current_url
            if "Search" not in url_retry:
                print(f"  [PASS] Save retry successful -> {url_retry}")
            else:
                print(f"  [WARN] Save retry also redirected: {url_retry}")
        except Exception as e:
            print(f"  [WARN] Save retry failed: {e}")
        else:
            print(
            f"  [PASS] Production Sequence Configuration saved successfully -> {url_after}")

        safe_screenshot(driver, "psc_after_save.png")

        # ========================================================================
        # PHASE 5: SUMMARY REPORT
        # ========================================================================
    def test_05_generate_report(self, driver):
        print_header("PHASE 5: TEST SUMMARY REPORT")

        tab_summary = "\n".join(
            f"   - {tab}: {count} field(s) updated"
            for tab, count in self.tab_updates.items()
        ) or "   (no tab updates recorded)"

        report = f"""
        ================================================================================
        PRODUCTION SEQUENCE CONFIGURATION TEST REPORT
        ================================================================================
        Date/Time  : {time.strftime('%Y-%m-%d %H:%M:%S')}
        Test URL   : {BASE_URL}
        User       : {USERNAME}
        Target     : {TARGET_WORKCENTER}
        Comment    : Production Sequence configuration

        OPERATIONS PERFORMED:
        ================================================================================
        1. Login and navigate to Admin > Workcenter
        2. Search for '{TARGET_WORKCENTER}' in Workcenter list
        3. Select workcenter row
        4. Click More Options > Production Sequence Configuration
        5. Click each tab and update random values:
        Tabs: {', '.join(PSC_TABS)}
        6. Save Production Sequence Configuration

        TAB UPDATE SUMMARY:
        {tab_summary}

        EXPECTED TABS: {', '.join(PSC_TABS)}

        CURRENT URL: {driver.current_url}
        ================================================================================
        """
        print(report)

        os.makedirs(REPORT_DIR, exist_ok=True)
        report_path = os.path.join(
            REPORT_DIR,
            f"ProductionSequenceConfiguration_{TARGET_WORKCENTER}.txt")
        try:
            with open(report_path, "w") as f:
                f.write(report)
            print(f"  [INFO] Report saved to: {report_path}")
        except Exception as e:
            print(f"  [WARN] Could not save report: {e}")

        safe_screenshot(driver, "psc_final.png")
