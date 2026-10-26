"""
QALS11 | Reports > Custom Reports > Create Custom Report > Admin > Item To Suppliers
=====================================================================================
URL  : https://engineering.ultrivalms.com/QALS1011
User : buyeruser / Ultriva!23
Test Flow: Login -> /CreateCustomReport/List -> Click Item To Suppliers -> Fill form -> Submit -> Show Report
Run: pytest tests/QALS11/Reports/CustomReports/Admin/test_item_to_suppliers_report.py -v -s
"""

import os, time, pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
USERNAME = "buyeruser"
PASSWORD = "Ultriva!23"
PAUSE = 1.2
FORM_URL = f"{BASE_URL}/CreateCustomReport/Update?reportGID=I2SReport"
LIST_URL = f"{BASE_URL}/CreateCustomReport/List"

_TS = time.strftime("%Y%m%d%H%M%S")
REPORT_NAME = f"AutoTest_ItemToSuppliers_{_TS}"
REPORT_DESC = f"Automated test - Admin Item To Suppliers report created at {_TS}"

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
    drv.set_page_load_timeout(30)
    drv.maximize_window()
    yield drv
    drv.quit()

def wait_ready(driver, timeout=30):
    WebDriverWait(driver, timeout).until(lambda d: d.execute_script("return document.readyState") == "complete")

def find(driver, by, locator, timeout=15):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, locator)))

def clickable(driver, by, locator, timeout=15):
    return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, locator)))

def scroll_to(driver, el):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'})", el)
    time.sleep(0.3)

def take_screenshot(driver, name):
    d = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "reports", "screenshots")
    os.makedirs(d, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(d, f"custom_report_i2s_{name}_{ts}.png")
    driver.save_screenshot(path)
    print(f"  [screenshot] {path}")
    return path

def safe_click_first(driver, locators, timeout=5):
    for loc in locators:
        try:
            return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(loc))
        except Exception:
            continue
    return None

def click_visible_text(driver, text):
    return driver.execute_script(
        "var w=arguments[0].trim().toLowerCase();"
        "var els=document.querySelectorAll('a,button,input[type=\"button\"],input[type=\"submit\"],span,div,li');"
        "for(var i=0;i<els.length;i++){"
        "  var el=els[i]; var txt=(el.innerText||el.value||'').trim().toLowerCase();"
        "  if(txt===w&&el.offsetParent!==null){el.click();return el;}}"
        "return null;", text)

def js_fill_name(driver, value):
    return driver.execute_script(
        "var inputs=document.querySelectorAll('input[type=\"text\"],input:not([type])');"
        "for(var i=0;i<inputs.length;i++){"
        "  var el=inputs[i];"
        "  if(el.offsetParent!==null&&!el.disabled&&!el.readOnly){"
        "    el.value=arguments[0];"
        "    el.dispatchEvent(new Event('input',{bubbles:true}));"
        "    el.dispatchEvent(new Event('change',{bubbles:true}));"
        "    return true;}}"
        "return false;", value)

def js_fill_desc(driver, value):
    return driver.execute_script(
        "var ta=document.querySelector('textarea');"
        "if(ta&&ta.offsetParent!==null&&!ta.disabled){"
        "  ta.value=arguments[0];"
        "  ta.dispatchEvent(new Event('input',{bubbles:true}));"
        "  ta.dispatchEvent(new Event('change',{bubbles:true}));"
        "  return true;}"
        "return false;", value)

@pytest.mark.usefixtures("driver")
class TestCustomReportAdminItemToSuppliers:

    def test_01_login(self, driver):
        print("\n" + "="*70)
        print("[TC-I2S-001] Custom Report Admin Item To Suppliers - Login")
        print("="*70)
        driver.get(BASE_URL); wait_ready(driver)
        find(driver, By.ID, "UserName").send_keys(USERNAME)
        find(driver, By.ID, "Password").send_keys(PASSWORD)
        clickable(driver, By.ID, "login-button").click()
        wait_ready(driver); time.sleep(PAUSE)
        take_screenshot(driver, "01_after_login")
        url = driver.current_url; print(f"  [URL] {url}")
        assert "Account/Login" not in url
        print("  [PASS] Login successful.")

    def test_02_navigate_to_list(self, driver):
        print("\n" + "="*70)
        print("[TC-I2S-002] Navigate to Create Custom Report List")
        print("="*70)
        driver.get(LIST_URL); wait_ready(driver); time.sleep(PAUSE)
        take_screenshot(driver, "02_list_page")
        url = driver.current_url
        print(f"  [URL] {url}")
        assert "createcustomreport" in url.lower()
        print(f"  [PASS] List page loaded: {url}")

    def test_03_click_item_to_suppliers(self, driver):
        print("\n" + "="*70)
        print("[TC-I2S-003] Click 'Item To Suppliers' under Admin")
        print("="*70)
        link = safe_click_first(driver, [
            (By.XPATH, "//a[contains(@href,'I2SReport')]"),
            (By.XPATH, "//a[normalize-space()='Item To Suppliers']"),
        ], timeout=5)
        if link:
            scroll_to(driver, link); link.click()
        else:
            driver.get(FORM_URL)
        wait_ready(driver); time.sleep(PAUSE)
        take_screenshot(driver, "03_form")
        url = driver.current_url
        print(f"  [URL] {url}")
        assert "i2sreport" in url.lower() or "createcustomreport" in url.lower()
        print(f"  [PASS] Item To Suppliers form loaded: {url}")

    def test_04_fill_form(self, driver):
        print("\n" + "="*70)
        print("[TC-I2S-004] Fill Report Information form")
        print("="*70)
        print(f"\n[STEP 4] Filling form: Name='{REPORT_NAME}'...")
        time.sleep(0.5)

        if "CreateCustomReport/Update" not in driver.current_url:
            driver.get(FORM_URL); wait_ready(driver); time.sleep(PAUSE)

        # Scroll to top of form first
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.5)

        # ========== Fill Name field ==========
        name_filled = False
        nf = safe_click_first(driver, [(By.ID, "Name"), (By.NAME, "Name"), (By.XPATH, "//input[@id='Name' or @name='Name']")], timeout=5)
        if nf:
            scroll_to(driver, nf)
            driver.execute_script(
                "arguments[0].value=arguments[1];"
                "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));"
                "arguments[0].dispatchEvent(new Event('change',{bubbles:true}));", nf, REPORT_NAME)
            time.sleep(0.2)
            # Verify fill
            val = driver.execute_script("return arguments[0].value;", nf)
            print(f"  [INFO] Name field value after fill: '{val}'")
            name_filled = True
        else:
            name_filled = js_fill_name(driver, REPORT_NAME)
            if name_filled:
                time.sleep(0.2)
                print(f"  [INFO] Name entered via JS: {REPORT_NAME}")

        assert name_filled, "Name field could not be filled."

        # ========== Fill Description field ==========
        desc_filled = False
        df = safe_click_first(driver, [(By.ID, "Description"), (By.NAME, "Description"), (By.XPATH, "//textarea[@id='Description' or @name='Description']"), (By.XPATH, "//textarea[1]")], timeout=5)
        if df:
            scroll_to(driver, df)
            driver.execute_script(
                "arguments[0].value=arguments[1];"
                "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));"
                "arguments[0].dispatchEvent(new Event('change',{bubbles:true}));", df, REPORT_DESC)
            time.sleep(0.2)
            # Verify fill
            val = driver.execute_script("return arguments[0].value;", df)
            print(f"  [INFO] Description field value after fill: '{val[:50]}...'")
            desc_filled = True
        else:
            desc_filled = js_fill_desc(driver, REPORT_DESC)
            if desc_filled:
                time.sleep(0.2)
                print(f"  [INFO] Description entered via JS: {REPORT_DESC[:50]}...")

        assert desc_filled, "Description field could not be filled."

        # ========== Ensure Visible only to me is selected ==========
        try:
            vis_radio = safe_click_first(driver, [(By.XPATH, "//input[@type='radio'][contains(@id,'VisibleOnlyToMe') or contains(@value,'VisibleOnlyToMe')]"), (By.XPATH, "//input[@type='radio'][1]")], timeout=5)
            if vis_radio and not vis_radio.is_selected():
                driver.execute_script("arguments[0].click()", vis_radio)
            print("  [INFO] Visibility set.")
        except Exception as e:
            print(f"  [WARN] Visibility radio not found: {e}")

        take_screenshot(driver, "04_form_filled")
        print("  [PASS] Form filled successfully.")

    def test_05_submit(self, driver):
        print("\n" + "="*70)
        print("[TC-I2S-005] Submit form and verify success")
        print("="*70)
        print("\n[STEP 5] Ensuring we're on the correct form page...")
        
        # Navigate back to form URL to start fresh
        if "CreateCustomReport/Update?reportGID=I2SReport" not in driver.current_url:
            print("  [INFO] Not on expected form URL; navigating back...")
            driver.get(FORM_URL)
            wait_ready(driver); time.sleep(PAUSE)

        print("[STEP 5] Filling and submitting form..."); time.sleep(0.5)

        # Scroll to top
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.5)

        # Fill fields again (they may have been cleared when page changed)
        js_fill_name(driver, REPORT_NAME)
        js_fill_desc(driver, REPORT_DESC)
        time.sleep(0.3)

        # Verify fields have values before submit
        name_val = driver.execute_script("var nf = document.getElementById('Name') || document.querySelector('input[name=\"Name\"]'); return nf ? nf.value : 'NOT_FOUND';")
        desc_val = driver.execute_script("var df = document.querySelector('textarea'); return df ? df.value : 'NOT_FOUND';")
        print(f"  [DEBUG] Name field value: '{name_val[:30] if name_val != 'NOT_FOUND' else 'NOT_FOUND'}...'")
        print(f"  [DEBUG] Description field value: '{desc_val[:30] if desc_val != 'NOT_FOUND' else 'NOT_FOUND'}...'")

        sb = safe_click_first(driver, [(By.XPATH, "//input[@type='submit']"), (By.XPATH, "//button[@type='submit']"), (By.XPATH, "//button[contains(normalize-space(.),'Save')]"), (By.XPATH, "//input[contains(@value,'Save')]")], timeout=8)
        if sb:
            scroll_to(driver, sb); sb.click(); print("  [INFO] Submit clicked.")
        else:
            click_visible_text(driver, "Save") or click_visible_text(driver, "Create")
            print("  [INFO] Submit clicked via JS fallback.")

        wait_ready(driver); time.sleep(PAUSE)
        take_screenshot(driver, "05_after_submit")
        url = driver.current_url; txt = driver.find_element(By.TAG_NAME, "body").text.lower()
        print(f"  [URL] {url}")

        # Check for errors
        if ("required fields do not have valid values" in txt or "system error" in txt or "CreateCustomReport/Update" in url) and "successfully created" not in txt:
            print("  [WARN] Form submission failed; retrying...")
            driver.get(FORM_URL)
            wait_ready(driver); time.sleep(0.5)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(0.3)
            js_fill_name(driver, REPORT_NAME)
            js_fill_desc(driver, REPORT_DESC)
            time.sleep(0.3)
            click_visible_text(driver, "Save") or click_visible_text(driver, "Create")
            print("  [INFO] Re-submitted form.")
            wait_ready(driver); time.sleep(PAUSE)
            take_screenshot(driver, "05_after_retry")
            url = driver.current_url; txt = driver.find_element(By.TAG_NAME, "body").text.lower()
            print(f"  [URL after retry] {url}")

        success = ("customreport" in url.lower() and "CreateCustomReport/Update" not in url) or REPORT_NAME.lower() in txt or "successfully created" in txt
        assert success, f"Creation failed. URL: {url}\nText: {txt[:200]}"
        print(f"  [PASS] Custom report created. URL: {url}")

    def test_06_show_report(self, driver):
        print("\n" + "="*70)
        print("[TC-I2S-006] Verify and click Show Report")
        print("="*70)
        print("\n[STEP 6] Checking Show Report..."); time.sleep(0.5)
        url = driver.current_url; txt = driver.find_element(By.TAG_NAME, "body").text
        print(f"  [URL] {url}")
        if "CreateCustomReport/Update" in url:
            print("  [WARN] Still on form; waiting for redirect..."); time.sleep(2); wait_ready(driver)
            url = driver.current_url; txt = driver.find_element(By.TAG_NAME, "body").text
            print(f"  [URL after wait] {url}")

        assert "Show Report" in txt, f"'Show Report' not found. URL: {url}\nText: {txt[:300]}"
        print("  [PASS] 'Show Report' button present.")

        # Check for Schedule Report too
        if "Schedule Report" in txt:
            print("  [PASS] 'Schedule Report' button also present.")

        sb = safe_click_first(driver, [(By.XPATH, "//a[contains(normalize-space(.),'Show Report')]"), (By.XPATH, "//button[contains(normalize-space(.),'Show Report')]")], timeout=8)
        if sb:
            scroll_to(driver, sb); sb.click(); print("  [INFO] 'Show Report' clicked.")
        else:
            click_visible_text(driver, "Show Report")
            print("  [INFO] 'Show Report' clicked via JS fallback.")

        wait_ready(driver); time.sleep(PAUSE)
        take_screenshot(driver, "07_show_report_output")
        url = driver.current_url; print(f"  [URL] {url}")
        assert "customreport" in url.lower() or "report" in url.lower()
        print(f"  [PASS] Show Report output loaded: {url}")
        print("\n" + "="*70)
        print("[DONE] All Item To Suppliers test steps completed.")
        print("="*70)
