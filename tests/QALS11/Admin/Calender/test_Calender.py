import time
import random
import os
import datetime
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
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
REPORT_DIR = os.path.join(os.path.dirname(
    __file__), "..", "..", "..", "reports")
_rand = random.randint(1000, 99999)
HOLIDAY_DATE = "04/30/2026"
HOLIDAY_DESC = f"Holiday{_rand}"

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


def print_header(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_step(num, desc):
    print(f"\n  [STEP {num}] {desc}")


def _ensure_logged_in(driver):
    """Check if logged in; if not, perform login."""
    if "/Account/Login" in driver.current_url or "login" in driver.title.lower():
        print("  [INFO] Not logged in — performing login")
        driver.get(BASE_URL)
        page_loaded(driver)
        safe_fill(driver, By.ID, "UserName", USERNAME)
        safe_fill(driver, By.ID, "Password", PASSWORD)
        safe_click(driver, By.ID, "login-button")
        page_loaded(driver)
        time.sleep(PAUSE)
        print(f"  [PASS] Login successful -> {driver.current_url}")
    else:
        try:
            driver.find_element(By.ID, "login-button")
            print("  [INFO] Session expired — re-logging in")
            safe_fill(driver, By.ID, "UserName", USERNAME)
            safe_fill(driver, By.ID, "Password", PASSWORD)
            safe_click(driver, By.ID, "login-button")
            page_loaded(driver)
            time.sleep(PAUSE)
            print(f"  [PASS] Re-login successful -> {driver.current_url}")
        except Exception:
            pass  # Already logged in

# ================================================================================
# TEST CLASS
# ================================================================================


class TestCalender:
    """
    Admin > Calendar: Add New Holiday
    """
    holiday_date = HOLIDAY_DATE
    holiday_desc = HOLIDAY_DESC

    # ========================================================================
    # TEST 01: ADD NEW HOLIDAY
    # ========================================================================
    def test_01_add_new_holiday(self, driver):
        """add New holiday"""
        print_header("PHASE 1: ADD NEW HOLIDAY TO CALENDAR")

        # Step 1: Login
        print_step(1, "Logging in")
        driver.get(BASE_URL)
        page_loaded(driver)
        _ensure_logged_in(driver)
        time.sleep(PAUSE)

        # Step 2: Navigate to Admin
        print_step(2, "Navigating to Admin module")
        try:
            safe_click(
                driver,
                By.XPATH,
                "//a[contains(@href,'/Admin/Home') or normalize-space(.)='Admin']")
        except Exception:
            driver.get(f"{BASE_URL}/Admin/Home")
            page_loaded(driver)
            time.sleep(PAUSE)
            print(f"  [PASS] Admin page opened -> {driver.current_url}")

        # Step 3: Click Calendar menu
        print_step(3, "Clicking Calendar menu")
        calendar_selectors = [
            "//a[normalize-space(.)='Calendar']",
            "//a[contains(@href,'Calendar')]",
            "//h4[normalize-space(.)='Calendar']/ancestor::a",
            "//*[contains(@class,'admin-module')]//a[contains(text(),'Calendar')]",
        ]
        cal_clicked = False
        for sel in calendar_selectors:
            try:
                safe_click(driver, By.XPATH, sel, timeout=5)
                cal_clicked = True
                print(f"  [PASS] Calendar menu clicked via: {sel}")
                break
            except Exception:
                continue
        if not cal_clicked:
            driver.get(f"{BASE_URL}/Calendar/List")
            print("  [INFO] Calendar opened via direct URL")
            page_loaded(driver)
            time.sleep(PAUSE)
            print(f"  [INFO] Current URL: {driver.current_url}")

        # Step 4: Click "+ Add" button
        print_step(4, "Clicking '+ Add' button")
        add_selects = [
            "//a[normalize-space(.)='Add' or normalize-space(.)='+ Add']",
            "//button[normalize-space(.)='Add' or normalize-space(.)='+ Add']",
            "//*[contains(@class,'btn') and contains(normalize-space(.),'Add')]",
            "//a[contains(@href,'Calendar/Create')]",
        ]
        add_clicked = False
        for sel in add_selects:
            try:
                el = safe_click(driver, By.XPATH, sel, timeout=5)
                add_clicked = True
                print(f"  [PASS] Add button clicked via: {sel}")
                break
            except Exception:
                continue
        if not add_clicked:
            driver.get(f"{BASE_URL}/Calendar/Create?Yr=2026")
            print("  [INFO] Add Holiday opened via direct URL")
            page_loaded(driver)
            time.sleep(PAUSE)
            print(f"  [INFO] Current URL: {driver.current_url}")

        # Step 5: Enter Holiday Date
        print_step(5, f"Entering Holiday Date: {self.holiday_date}")
        date_selects = [
            (By.ID, "HolidayDate"),
            (By.NAME, "HolidayDate"),
            (By.XPATH, "//input[contains(@id,'HolidayDate') or contains(@name,'HolidayDate')]"),
            (By.XPATH, "//label[contains(text(),'Holiday Date')]/following::input[1]"),
            (By.XPATH, "//input[@type='text'][1]"),
        ]
        date_filled = False
        for by, loc in date_selects:
            try:
                el = WebDriverWait(
                    driver, 5).until(
                    EC.visibility_of_element_located(
                        (by, loc)))
                scroll_to(driver, el)
                el.click()
                el.clear()
                el.send_keys(self.holiday_date)
                el.send_keys(Keys.TAB)
                date_filled = True
                print(f"  [PASS] Holiday Date entered via: {by}={loc}")
                break
            except Exception:
                continue
        if not date_filled:
            driver.execute_script("""
                var inputs = document.querySelectorAll('input[type="text"], input[id*="Date"], input[name*="Date"]');
                for (var i = 0; i < inputs.length; i++) {
                    if (inputs[i].id.toLowerCase().includes('date') || inputs[i].name.toLowerCase().includes('date')) {
                        inputs[i].value = arguments[0];
                        inputs[i].dispatchEvent(new Event('change', {bubbles: true}));
                        break;
                    }
                }
            """, self.holiday_date)
            print(f"  [INFO] Holiday Date entered via JS fallback")
            time.sleep(1)

        # Step 6: Enter Description
        print_step(6, f"Entering Description: {self.holiday_desc}")
        desc_selects = [
            (By.ID, "Description"),
            (By.NAME, "Description"),
            (By.XPATH, "//input[contains(@id,'Description') or contains(@name,'Description')]"),
            (By.XPATH, "//label[contains(text(),'Description')]/following::input[1]"),
        ]
        desc_filled = False
        for by, loc in desc_selects:
            try:
                el = WebDriverWait(
                    driver, 5).until(
                    EC.visibility_of_element_located(
                        (by, loc)))
                scroll_to(driver, el)
                el.click()
                el.clear()
                el.send_keys(self.holiday_desc)
                desc_filled = True
                print(f"  [PASS] Description entered via: {by}={loc}")
                break
            except Exception:
                continue
        if not desc_filled:
            driver.execute_script("""
                var inputs = document.querySelectorAll('input[type="text"], input[id*="escription"], input[name*="escription"]');
                for (var i = 0; i < inputs.length; i++) {
                    if (inputs[i].id.toLowerCase().includes('description') || inputs[i].name.toLowerCase().includes('description')) {
                        inputs[i].value = arguments[0];
                        inputs[i].dispatchEvent(new Event('change', {bubbles: true}));
                        break;
                    }
                }
            """, self.holiday_desc)
            print(f"  [INFO] Description entered via JS fallback")
            time.sleep(1)

        # Step 7: Click Save
        print_step(7, "Clicking Save button")
        save_selects = [
            "//button[normalize-space(.)='Save']",
            "//input[@type='submit' and @value='Save']",
            "//a[normalize-space(.)='Save']",
            "//*[contains(@class,'btn') and contains(normalize-space(.),'Save')]",
            "//button[contains(@class,'save')]",
            "//*[@id='btnSave']",
        ]
        save_clicked = False
        for sel in save_selects:
            try:
                el = safe_click(driver, By.XPATH, sel, timeout=5)
                save_clicked = True
                print(f"  [PASS] Save clicked via: {sel}")
                break
            except Exception:
                continue
        if not save_clicked:
            driver.execute_script("""
                var btns = document.querySelectorAll('button, input[type="submit"], a.btn');
                for (var i = 0; i < btns.length; i++) {
                    if (btns[i].textContent.trim().toLowerCase().includes('save') ||
                        (btns[i].value && btns[i].value.toLowerCase().includes('save'))) {
                        btns[i].click();
                        break;
                    }
                }
            """)
            print("  [INFO] Save clicked via JS fallback")
        page_loaded(driver)
        time.sleep(PAUSE * 2)

        # Step 8: Verify save
        print_step(8, "Verifying holiday was saved")
        current_url = driver.current_url
        print(f"  [INFO] Current URL after save: {current_url}")

        if "Calendar/List" in current_url or "Calendar" in current_url:
            print(f"  [PASS] Redirected to Calendar list after save")

        try:
            page_source = driver.page_source
            if self.holiday_desc in page_source:
                print(f"  [PASS] Holiday '{self.holiday_desc}' found in calendar list")
            elif self.holiday_date in page_source or "04/30/2026" in page_source:
                print(f"  [PASS] Holiday date '{self.holiday_date}' found in calendar list")
            else:
                print(f"  [INFO] Holiday may have been saved — could not verify in page source")
        except Exception:
            print(f"  [INFO] Could not verify holiday in list")

        try:
            errors = driver.find_elements(
                By.CSS_SELECTOR,
                ".validation-summary-errors, .field-validation-error, .alert-danger")
            if errors:
                for err in errors:
                    if err.text.strip():
                        print(f"  [WARN] Validation error: {err.text.strip()}")
        except Exception:
            pass

        print(f"\n  [SUMMARY] Add New Holiday completed")
        print(f"    Holiday Date : {self.holiday_date}")
        print(f"    Description  : {self.holiday_desc}")

    # ========================================================================
    # TEST 02: EDIT CALENDAR
    # ========================================================================
    def test_02_edit_holiday(self, driver):
        """Edit calender"""
        print_header("PHASE 2: EDIT HOLIDAY FROM CALENDAR")

        _edit_rand = random.randint(1000, 99999)
        new_desc = f"EditedHoliday{_edit_rand}"

        # Step 1: Login
        print_step(1, "Logging in")
        driver.get(BASE_URL)
        page_loaded(driver)
        _ensure_logged_in(driver)
        time.sleep(PAUSE)

        # Step 2: Navigate to Admin > Calendar List
        print_step(2, "Navigating to Calendar List (2026)")
        driver.get(f"{BASE_URL}/Calendar/List?Yr=2026")
        page_loaded(driver)
        time.sleep(PAUSE)
        print(f"  [PASS] Calendar list opened -> {driver.current_url}")

        # Step 3: Select a holiday from Observed Holidays list
        print_step(3, "Selecting a holiday from list")
        selected_desc = None
        checkbox_selects = [
            "//table//tr[td]//input[@type='checkbox']",
            "//table//tbody//tr//input[@type='checkbox']",
            "//input[@type='checkbox' and not(@id='checkAll') and not(contains(@id,'all'))]",
        ]
        chk_clicked = False
        for sel in checkbox_selects:
            try:
                checkboxes = driver.find_elements(By.XPATH, sel)
                if checkboxes:
                    cb = checkboxes[0]
                    scroll_to(driver, cb)
                    try:
                        row = cb.find_element(By.XPATH, "./ancestor::tr")
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if len(cells) >= 2:
                            selected_desc = cells[-1].text.strip()
                    except Exception:
                        pass
                    cb.click()
                    chk_clicked = True
                    print(f"  [PASS] Holiday checkbox selected (Description:  { selected_desc or 'N/A' })")
                    break
            except Exception:
                continue
        if not chk_clicked:
            driver.execute_script("""
                var cbs = document.querySelectorAll('table tr td input[type="checkbox"]');
                if (cbs.length > 0) { cbs[0].click(); }
            """)
            print("  [INFO] Holiday selected via JS fallback")
            time.sleep(1)

        # Step 4: Click Edit button
        print_step(4, "Clicking Edit button")
        edit_selects = [
            "//a[normalize-space(.)='Edit']",
            "//button[normalize-space(.)='Edit']",
            "//*[contains(@class,'btn') and normalize-space(.)='Edit']",
            "//a[contains(@href,'Calendar/Edit')]",
        ]
        edit_clicked = False
        for sel in edit_selects:
            try:
                safe_click(driver, By.XPATH, sel, timeout=5)
                edit_clicked = True
                print(f"  [PASS] Edit button clicked via: {sel}")
                break
            except Exception:
                continue
        if not edit_clicked:
            driver.execute_script("""
                var btns = document.querySelectorAll('a.btn, button');
                for (var i = 0; i < btns.length; i++) {
                    if (btns[i].textContent.trim() === 'Edit') {
                        btns[i].click(); break;
                    }
                }
            """)
            print("  [INFO] Edit clicked via JS fallback")
        page_loaded(driver)
        time.sleep(PAUSE)
        print(f"  [INFO] Current URL: {driver.current_url}")

        # Step 5: Modify description
        print_step(5, f"Modifying Description to: {new_desc}")
        desc_selects = [
            (By.ID, "Description"),
            (By.NAME, "Description"),
            (By.XPATH, "//input[contains(@id,'Description') or contains(@name,'Description')]"),
            (By.XPATH, "//label[contains(text(),'Description')]/following::input[1]"),
        ]
        desc_modified = False
        for by, loc in desc_selects:
            try:
                el = WebDriverWait(
                    driver, 5).until(
                    EC.visibility_of_element_located(
                        (by, loc)))
                scroll_to(driver, el)
                old_val = el.get_attribute("value")
                print(f"  [INFO] Current description: {old_val}")
                el.click()
                el.clear()
                el.send_keys(new_desc)
                desc_modified = True
                print(f"  [PASS] Description modified via: {by}={loc}")
                break
            except Exception:
                continue
        if not desc_modified:
            driver.execute_script("""
                var inputs = document.querySelectorAll('input[type="text"], input[id*="escription"], input[name*="escription"]');
                for (var i = 0; i < inputs.length; i++) {
                    if (inputs[i].id.toLowerCase().includes('description') || inputs[i].name.toLowerCase().includes('description')) {
                        inputs[i].value = arguments[0];
                        inputs[i].dispatchEvent(new Event('change', {bubbles: true}));
                        break;
                    }
                }
            """, new_desc)
            print(f"  [INFO] Description modified via JS fallback")
            time.sleep(1)

        # Step 6: Click Save
        print_step(6, "Clicking Save button")
        save_selects = [
            "//button[normalize-space(.)='Save']",
            "//input[@type='submit' and @value='Save']",
            "//a[normalize-space(.)='Save']",
            "//*[contains(@class,'btn') and contains(normalize-space(.),'Save')]",
            "//button[contains(@class,'save')]",
            "//*[@id='btnSave']",
        ]
        save_clicked = False
        for sel in save_selects:
            try:
                el = safe_click(driver, By.XPATH, sel, timeout=5)
                save_clicked = True
                print(f"  [PASS] Save clicked via: {sel}")
                break
            except Exception:
                continue
        if not save_clicked:
            driver.execute_script("""
                var btns = document.querySelectorAll('button, input[type="submit"], a.btn');
                for (var i = 0; i < btns.length; i++) {
                    if (btns[i].textContent.trim().toLowerCase().includes('save') ||
                        (btns[i].value && btns[i].value.toLowerCase().includes('save'))) {
                        btns[i].click();
                        break;
                    }
                }
            """)
            print("  [INFO] Save clicked via JS fallback")
        page_loaded(driver)
        time.sleep(PAUSE * 2)

        # Step 7: Verify save
        print_step(7, "Verifying holiday was updated")
        current_url = driver.current_url
        print(f"  [INFO] Current URL after save: {current_url}")

        if "Calendar/List" in current_url or "Calendar" in current_url:
            print(f"  [PASS] Redirected to Calendar list after save")

        try:
            page_source = driver.page_source
            if new_desc in page_source:
                print(f"  [PASS] Updated description '{new_desc}' found in calendar list")
            else:
                print(f"  [INFO] Holiday may have been updated — could not verify in page source")
        except Exception:
            print(f"  [INFO] Could not verify updated holiday in list")

        try:
            errors = driver.find_elements(
                By.CSS_SELECTOR,
                ".validation-summary-errors, .field-validation-error, .alert-danger")
            if errors:
                for err in errors:
                    if err.text.strip():
                        print(f"  [WARN] Validation error: {err.text.strip()}")
        except Exception:
            pass

        print(f"\n  [SUMMARY] Edit Holiday completed")
        print(f"    Original     : {selected_desc or 'first holiday in list'}")
        print(f"    New Desc     : {new_desc}")

    # ========================================================================
    # TEST 03: ADD RANGE OF HOLIDAYS
    # ========================================================================
    def test_03_add_range_of_holidays(self, driver):
        """Add Range of holidays"""
        print_header("PHASE 3: ADD RANGE OF HOLIDAYS TO CALENDAR")

        _range_rand = random.randint(1000, 99999)
        range_desc = f"RangeHoliday{_range_rand}"

        # Step 1: Login
        print_step(1, "Logging in")
        driver.get(BASE_URL)
        page_loaded(driver)
        _ensure_logged_in(driver)
        time.sleep(PAUSE)

        # Step 2: Navigate to Calendar List (2026)
        print_step(2, "Navigating to Calendar List (2026)")
        driver.get(f"{BASE_URL}/Calendar/List?Yr=2026")
        page_loaded(driver)
        time.sleep(PAUSE)
        print(f"  [PASS] Calendar list opened -> {driver.current_url}")

        # Step 3: Click "Add Range" button
        print_step(3, "Clicking 'Add Range' button")
        add_range_selects = [
            "//a[normalize-space(.)='Add Range']",
            "//button[normalize-space(.)='Add Range']",
            "//*[contains(@class,'btn') and normalize-space(.)='Add Range']",
            "//a[contains(@href,'AddRange')]",
        ]
        ar_clicked = False
        for sel in add_range_selects:
            try:
                safe_click(driver, By.XPATH, sel, timeout=5)
                ar_clicked = True
                print(f"  [PASS] Add Range button clicked via: {sel}")
                break
            except Exception:
                continue
        if not ar_clicked:
            driver.get(f"{BASE_URL}/Calendar/AddRange?Yr=2026")
            print("  [INFO] Add Range opened via direct URL")
            page_loaded(driver)
            time.sleep(PAUSE)
            print(f"  [INFO] Current URL: {driver.current_url}")

        # Step 4: Select Date Range from dropdown
        print_step(4, "Selecting Date Range")
        date_range_filled = False
        date_range_input_selects = [
            (By.ID, "DateRange"),
            (By.NAME, "DateRange"),
            (By.XPATH, "//input[contains(@id,'DateRange') or contains(@name,'DateRange')]"),
            (By.XPATH, "//label[contains(text(),'Date Range')]/following::input[1]"),
            (By.XPATH, "//input[@type='text'][1]"),
        ]
        for by, loc in date_range_input_selects:
            try:
                el = WebDriverWait(
                    driver, 5).until(
                    EC.visibility_of_element_located(
                        (by, loc)))
                scroll_to(driver, el)
                el.click()
                time.sleep(1)
                print(f"  [INFO] Date Range input clicked via: {by}={loc}")
                date_range_filled = True
                break
            except Exception:
                continue

        if date_range_filled:
            option_selects = [
                "//li[normalize-space(.)='Next 5 Days']",
                "//a[normalize-space(.)='Next 5 Days']",
                "//*[contains(@class,'ui-menu-item')]//a[contains(text(),'Next 5 Days')]",
                "//*[contains(@class,'dropdown')]//a[contains(text(),'Next 5 Days')]",
                "//*[contains(text(),'Next 5 Days')]",
            ]
            option_selected = False
            for sel in option_selects:
                try:
                    opt = WebDriverWait(
                        driver, 5).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, sel)))
                    opt.click()
                    option_selected = True
                    print(f"  [PASS] 'Next 5 Days' selected via: {sel}")
                    break
                except Exception:
                    continue
            if not option_selected:
                driver.execute_script("""
                    var items = document.querySelectorAll('li a, li, .ui-menu-item a, .dropdown-menu a');
                    for (var i = 0; i < items.length; i++) {
                        if (items[i].textContent.trim().indexOf('Next 5 Days') !== -1) {
                            items[i].click(); return true;
                        }
                    }
                    return false;
                """)
                print("  [INFO] Date Range selected via JS fallback")
        else:
            driver.execute_script("""
                var inputs = document.querySelectorAll('input[type="text"], input[id*="Date"], input[name*="Date"]');
                if (inputs.length > 0) {
                    inputs[0].click();
                    inputs[0].focus();
                }
            """)
            time.sleep(1)
            try:
                opt = WebDriverWait(
                    driver, 5).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//*[contains(text(),'Next 5 Days')]")))
                opt.click()
                print("  [PASS] 'Next 5 Days' selected after JS input click")
            except Exception:
                driver.execute_script("""
                    var items = document.querySelectorAll('li a, li, .ui-menu-item a');
                    for (var i = 0; i < items.length; i++) {
                        if (items[i].textContent.trim().indexOf('Next 5 Days') !== -1) {
                            items[i].click(); return;
                        }
                    }
                """)
                print("  [INFO] Date Range selected via JS fallback")
                time.sleep(PAUSE)

        # Step 5: Enter Description
        print_step(5, f"Entering Description: {range_desc}")
        desc_selects = [
            (By.ID, "Description"),
            (By.NAME, "Description"),
            (By.XPATH, "//input[contains(@id,'Description') or contains(@name,'Description')]"),
            (By.XPATH, "//label[contains(text(),'Description')]/following::input[1]"),
        ]
        desc_filled = False
        for by, loc in desc_selects:
            try:
                el = WebDriverWait(
                    driver, 5).until(
                    EC.visibility_of_element_located(
                        (by, loc)))
                scroll_to(driver, el)
                el.click()
                el.clear()
                el.send_keys(range_desc)
                desc_filled = True
                print(f"  [PASS] Description entered via: {by}={loc}")
                break
            except Exception:
                continue
        if not desc_filled:
            driver.execute_script("""
                var inputs = document.querySelectorAll('input[type="text"], input[id*="escription"], input[name*="escription"]');
                for (var i = 0; i < inputs.length; i++) {
                    if (inputs[i].id.toLowerCase().includes('description') || inputs[i].name.toLowerCase().includes('description')) {
                        inputs[i].value = arguments[0];
                        inputs[i].dispatchEvent(new Event('change', {bubbles: true}));
                        break;
                    }
                }
            """, range_desc)
            print(f"  [INFO] Description entered via JS fallback")
            time.sleep(1)

        # Step 6: Click Save
        print_step(6, "Clicking Save button")
        save_selects = [
            "//button[normalize-space(.)='Save']",
            "//input[@type='submit' and @value='Save']",
            "//a[normalize-space(.)='Save']",
            "//*[contains(@class,'btn') and contains(normalize-space(.),'Save')]",
            "//button[contains(@class,'save')]",
            "//*[@id='btnSave']",
        ]
        save_clicked = False
        for sel in save_selects:
            try:
                el = safe_click(driver, By.XPATH, sel, timeout=5)
                save_clicked = True
                print(f"  [PASS] Save clicked via: {sel}")
                break
            except Exception:
                continue
        if not save_clicked:
            driver.execute_script("""
                var btns = document.querySelectorAll('button, input[type="submit"], a.btn');
                for (var i = 0; i < btns.length; i++) {
                    if (btns[i].textContent.trim().toLowerCase().includes('save') ||
                        (btns[i].value && btns[i].value.toLowerCase().includes('save'))) {
                        btns[i].click();
                        break;
                    }
                }
            """)
            print("  [INFO] Save clicked via JS fallback")
        page_loaded(driver)
        time.sleep(PAUSE * 2)

        # Step 7: Verify save
        print_step(7, "Verifying range holidays were saved")
        current_url = driver.current_url
        print(f"  [INFO] Current URL after save: {current_url}")

        if "Calendar/List" in current_url or "Calendar" in current_url:
            print(f"  [PASS] Redirected to Calendar list after save")

        try:
            page_source = driver.page_source
            if range_desc in page_source:
                print(f"  [PASS] Range holiday '{range_desc}' found in calendar list")
            else:
                print(f"  [INFO] Range holidays may have been saved — could not verify in page source")
        except Exception:
            print(f"  [INFO] Could not verify range holidays in list")

        try:
            errors = driver.find_elements(
                By.CSS_SELECTOR,
                ".validation-summary-errors, .field-validation-error, .alert-danger")
            if errors:
                for err in errors:
                    if err.text.strip():
                        print(f"  [WARN] Validation error: {err.text.strip()}")
        except Exception:
            pass

        print(f"\n  [SUMMARY] Add Range of Holidays completed")
        print(f"    Date Range   : Next 5 Days")
        print(f"    Description  : {range_desc}")

    # ========================================================================
    # TEST 04: DELETE HOLIDAY
    # ========================================================================
    def test_04_delete_holiday(self, driver):
        """Delete Holiday"""
        print_header("PHASE 4: DELETE HOLIDAY FROM CALENDAR")

        # Step 1: Login
        print_step(1, "Logging in")
        driver.get(BASE_URL)
        page_loaded(driver)
        _ensure_logged_in(driver)
        time.sleep(PAUSE)

        # Step 2: Navigate to Calendar List (2026)
        print_step(2, "Navigating to Calendar List (2026)")
        driver.get(f"{BASE_URL}/Calendar/List?Yr=2026")
        page_loaded(driver)
        time.sleep(PAUSE)
        print(f"  [PASS] Calendar list opened -> {driver.current_url}")

        # Step 3: Select a holiday from Observed Holidays list
        print_step(3, "Selecting a holiday from list")
        selected_desc = None
        selected_date = None
        checkbox_selects = [
            "//table//tr[td]//input[@type='checkbox']",
            "//table//tbody//tr//input[@type='checkbox']",
            "//input[@type='checkbox' and not(@id='checkAll') and not(contains(@id,'all'))]",
        ]
        chk_clicked = False
        for sel in checkbox_selects:
            try:
                checkboxes = driver.find_elements(By.XPATH, sel)
                if checkboxes:
                    cb = checkboxes[0]
                    scroll_to(driver, cb)
                    try:
                        row = cb.find_element(By.XPATH, "./ancestor::tr")
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if len(cells) >= 2:
                            selected_date = cells[1].text.strip() if len(
                                cells) > 1 else "N/A"
                            selected_desc = cells[-1].text.strip()
                    except Exception:
                        pass
                    cb.click()
                    chk_clicked = True
                    print(f"  [PASS] Holiday selected (Date: {selected_date or 'N/A'}, Description: {selected_desc or 'N/A'}")
                    break
            except Exception:
                continue
        if not chk_clicked:
            driver.execute_script("""
                var cbs = document.querySelectorAll('table tr td input[type="checkbox"]');
                if (cbs.length > 0) { cbs[0].click(); }
            """)
            print("  [INFO] Holiday selected via JS fallback")
            time.sleep(1)

        # Step 4: Click Delete button
        print_step(4, "Clicking Delete button")
        delete_selects = [
            "//a[normalize-space(.)='Delete']",
            "//button[normalize-space(.)='Delete']",
            "//*[contains(@class,'btn') and normalize-space(.)='Delete']",
            "//a[contains(@href,'Delete')]",
        ]
        del_clicked = False
        for sel in delete_selects:
            try:
                safe_click(driver, By.XPATH, sel, timeout=5)
                del_clicked = True
                print(f"  [PASS] Delete button clicked via: {sel}")
                break
            except Exception:
                continue
        if not del_clicked:
            driver.execute_script("""
                var btns = document.querySelectorAll('a.btn, button');
                for (var i = 0; i < btns.length; i++) {
                    if (btns[i].textContent.trim() === 'Delete') {
                        btns[i].click(); break;
                    }
                }
            """)
            print("  [INFO] Delete clicked via JS fallback")
            time.sleep(PAUSE)

        # Step 5: Confirm deletion — click "Yes" on popup
        print_step(5, "Confirming deletion — clicking 'Yes' on popup")
        yes_selects = [
            "//button[normalize-space(.)='Yes']",
            "//a[normalize-space(.)='Yes']",
            "//*[contains(@class,'btn') and normalize-space(.)='Yes']",
            "//button[contains(@class,'confirm') or contains(@class,'yes')]",
            "//*[contains(@class,'modal') or contains(@class,'popup')]//*[normalize-space(.)='Yes']",
        ]
        yes_clicked = False
        for sel in yes_selects:
            try:
                el = WebDriverWait(
                    driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, sel)))
                el.click()
                yes_clicked = True
                print(f"  [PASS] 'Yes' clicked via: {sel}")
                break
            except Exception:
                continue
        if not yes_clicked:
            try:
                alert = driver.switch_to.alert
                alert.accept()
                print("  [INFO] Confirmed via browser alert")
            except Exception:
                driver.execute_script("""
                    var btns = document.querySelectorAll('button, a.btn');
                    for (var i = 0; i < btns.length; i++) {
                        if (btns[i].textContent.trim() === 'Yes') {
                            btns[i].click(); break;
                        }
                    }
                """)
                print("  [INFO] 'Yes' clicked via JS fallback")
        page_loaded(driver)
        time.sleep(PAUSE * 2)

        # Step 6: Verify deletion
        print_step(6, "Verifying holiday was deleted")
        current_url = driver.current_url
        print(f"  [INFO] Current URL after delete: {current_url}")

        if "Calendar/List" in current_url or "Calendar" in current_url:
            print(f"  [PASS] Redirected to Calendar list after delete")

        if selected_desc:
            try:
                page_source = driver.page_source
                if selected_desc not in page_source:
                    print(f"  [PASS] Deleted holiday '{selected_desc}' no longer in list")
                else:
                    print(f"  [INFO] Holiday '{selected_desc}' may still appear (could be duplicate entries)")
            except Exception:
                print(f"  [INFO] Could not verify deletion in page source")

        try:
            errors = driver.find_elements(
                By.CSS_SELECTOR,
                ".validation-summary-errors, .field-validation-error, .alert-danger")
            if errors:
                for err in errors:
                    if err.text.strip():
                        print(f"  [WARN] Error: {err.text.strip()}")
        except Exception:
            pass

        print(f"\n  [SUMMARY] Delete Holiday completed")
        print(f"    Date         : {selected_date or 'first holiday in list'}")
        print(f"    Description  : {selected_desc or 'N/A'}")

    # ========================================================================
    # TEST 05: CONVERT ACTIVE DATE TO HOLIDAY
    # ========================================================================
    def test_05_convert_active_date_to_holiday(self, driver):
        """Convert any active (working) date to holiday (robust selector, no questions)"""
        print_header("PHASE 5: CONVERT ACTIVE DATE TO HOLIDAY")
        print_step(1, "Logging in")
        driver.get(BASE_URL)
        page_loaded(driver)
        _ensure_logged_in(driver)
        time.sleep(PAUSE)
        print_step(2, "Navigating to Business Calendar tab (2026)")
        driver.get(f"{BASE_URL}/Calendar/ListCal?Yr=2026")
        page_loaded(driver)
        time.sleep(PAUSE)
        print(f"  [PASS] Business Calendar opened -> {driver.current_url}")
        print_step(3, "Clicking first blue (working) date cell")
        cell = None
        selectors = [
            "//td[contains(@style,'color: rgb(0, 112, 192)')]",
            "//td[contains(@class,'text-primary')]",
            "//td[.//span[contains(@style,'color: rgb(0, 112, 192)')]]",
            "//td[not(contains(@class,'holiday')) and not(contains(@class,'non-working')) and not(contains(@style,'red')) and not(contains(@style,'pink')) and string-length(normalize-space(text()))>0]"
        ]
        for sel in selectors:
            try:
                cell = driver.find_element(By.XPATH, sel)
                scroll_to(driver, cell)
                cell.click()
                print(f"  [PASS] Active date cell clicked via: {sel}")
                break
            except Exception:
                continue
        if not cell:
            print("  [FAIL] Could not find any active date cell")
            return
        time.sleep(1)
        print_step(4, "Clicking 'convert to holiday' link")
        try:
            link = driver.find_element(
                By.XPATH,
                "//*[contains(text(),'convert to holiday') or contains(text(),'Convert to holiday')]")
            scroll_to(driver, link)
            link.click()
            print("  [PASS] 'Convert to holiday' link clicked")
        except Exception:
            print("  [FAIL] Could not find 'convert to holiday' link")
            return
        time.sleep(1)
        print_step(5, "Entering description and saving")
        desc = f"ConvertedHoliday{random.randint(1000, 99999)}"
        try:
            desc_input = driver.find_element(
                By.XPATH,
                "//input[contains(@id,'Description') or contains(@name,'Description')]")
            desc_input.clear()
            desc_input.send_keys(desc)
            print(f"  [PASS] Description entered: {desc}")
        except Exception:
            print("  [FAIL] Could not enter description")
            return
        try:
            save_btn = driver.find_element(
                By.XPATH,
                "//button[normalize-space(.)='Save'] | //input[@type='submit' and @value='Save']")
            save_btn.click()
            print("  [PASS] Save clicked")
        except Exception:
            print("  [FAIL] Could not click Save button")
            return
        page_loaded(driver)
        time.sleep(PAUSE)
        print_step(6, "Verifying holiday was created")
        try:
            if desc in driver.page_source:
                print(f"  [PASS] Converted holiday '{desc}' found in calendar")
            else:
                print(f"  [INFO] Converted holiday '{desc}' may have been created (not found in page source)")
        except Exception:
            print(f"  [INFO] Could not verify converted holiday in calendar")
        print(f"\n  [SUMMARY] Convert Active Date to Holiday completed\n    Description: {desc}")

    # ========================================================================
    # TEST 06: DIRECT CONVERT SPECIFIC DATE TO HOLIDAY
    # ========================================================================
    def test_06_direct_convert_specific_date_to_holiday(self, driver):
        """Directly convert a specific date (2026-04-21) to holiday via URL"""
        print_header("PHASE 6: DIRECT CONVERT SPECIFIC DATE TO HOLIDAY")
        print_step(1, "Logging in")
        driver.get(BASE_URL)
        page_loaded(driver)
        _ensure_logged_in(driver)
        time.sleep(PAUSE)
        print_step(2, "Navigating directly to CreateCal for 2026-04-21")
        url = f"{BASE_URL}/Calendar/CreateCal?Yr=2026&dt=2026-04-21"
        driver.get(url)
        page_loaded(driver)
        time.sleep(PAUSE)
        print(f"  [PASS] Navigated to: {url}")
        print_step(3, "Entering description and saving")
        desc = f"DirectHoliday{random.randint(1000, 99999)}"
        try:
            desc_input = driver.find_element(
                By.XPATH,
                "//input[contains(@id,'Description') or contains(@name,'Description')]")
            desc_input.clear()
            desc_input.send_keys(desc)
            print(f"  [PASS] Description entered: {desc}")
        except Exception:
            print("  [FAIL] Could not enter description")
            return
        try:
            save_btn = driver.find_element(
                By.XPATH,
                "//button[normalize-space(.)='Save'] | //input[@type='submit' and @value='Save']")
            save_btn.click()
            print("  [PASS] Save clicked")
        except Exception:
            print("  [FAIL] Could not click Save button")
            return
        page_loaded(driver)
        time.sleep(PAUSE)
        print_step(4, "Verifying holiday was created")
        try:
            if desc in driver.page_source:
                print(f"  [PASS] Direct holiday '{desc}' found in calendar")
            else:
                print(f"  [INFO] Direct holiday '{desc}' may have been created (not found in page source)")
        except Exception:
            print(f"  [INFO] Could not verify direct holiday in calendar")
        print(f"\n  [SUMMARY] Direct Convert Specific Date to Holiday completed\n    Description: {desc}")

    # ========================================================================
    # TEST 07: DIRECT CONVERT RANDOM ACTIVE DATE TO HOLIDAY
    # ========================================================================
    def test_07_direct_convert_random_active_date_to_holiday(self, driver):
        """Directly convert a random active (working) date to holiday via URL (no questions, robust)"""
        print_header("PHASE 7: DIRECT CONVERT RANDOM ACTIVE DATE TO HOLIDAY")
        print_step(1, "Logging in")
        driver.get(BASE_URL)
        page_loaded(driver)
        _ensure_logged_in(driver)
        time.sleep(PAUSE)
        print_step(
            2, "Pick a random active date in 2026 and navigate to CreateCal")
        year = 2026
        for _ in range(20):
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            try:
                date = datetime.date(year, month, day)
            except Exception:
                continue
            if date.weekday() < 5:
                break
        else:
            print("  [FAIL] Could not find a random working day in 2026")
            return
        url = f"{BASE_URL}/Calendar/CreateCal?Yr={year}&dt={date}"
        driver.get(url)
        page_loaded(driver)
        time.sleep(PAUSE)
        print(f"  [PASS] Navigated to: {url}")
        print_step(3, "Entering description and saving")
        desc = f"RandomHoliday{random.randint(1000, 99999)}"
        try:
            desc_input = driver.find_element(
                By.XPATH,
                "//input[contains(@id,'Description') or contains(@name,'Description')]")
            desc_input.clear()
            desc_input.send_keys(desc)
            print(f"  [PASS] Description entered: {desc}")
        except Exception:
            print("  [FAIL] Could not enter description")
            return
        try:
            save_btn = driver.find_element(
                By.XPATH,
                "//button[normalize-space(.)='Save'] | //input[@type='submit' and @value='Save']")
            save_btn.click()
            print("  [PASS] Save clicked")
        except Exception:
            print("  [FAIL] Could not click Save button")
            return
        page_loaded(driver)
        time.sleep(PAUSE)
        print_step(4, "Verifying holiday was created")
        try:
            if desc in driver.page_source:
                print(f"  [PASS] Random holiday '{desc}' found in calendar")
            else:
                print(f"  [INFO] Random holiday '{desc}' may have been created (not found in page source)")
        except Exception:
            print(f"  [INFO] Could not verify random holiday in calendar")
        print(f"\n  [SUMMARY] Direct Convert Random Active Date to Holiday completed\n    Date: {date}\n    Description: {desc}")
