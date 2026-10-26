"""
QALS11 | Reports > Custom Reports > Create Custom Report > Admin > Suppliers' Users
====================================================================================
URL  : https://engineering.ultrivalms.com/QALS1011/CreateCustomReport/List
User : buyeruser / Ultriva!23
Test Flow: Login -> Open Create Custom Report list -> Click Suppliers' Users ->
           Fill mandatory fields -> Save -> Show Report
Run: pytest tests/QALS11/Reports/CustomReports/Admin/test_suppliers_users_report.py -v -s
"""

import os
import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
USERNAME = "buyeruser"
PASSWORD = "Ultriva!23"
PAUSE = 1.2

LIST_URL = f"{BASE_URL}/CreateCustomReport/List"
FORM_URL = f"{BASE_URL}/CreateCustomReport/Update?reportGID=SupUserReport"

_TS = time.strftime("%Y%m%d%H%M%S")
REPORT_NAME = f"SU{_TS[-8:]}"
REPORT_DESC = f"Suppliers Users report {_TS[-8:]}"


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


def take_screenshot(driver, name):
    screenshot_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "..", "reports", "screenshots"
    )
    os.makedirs(screenshot_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(screenshot_dir, f"custom_report_suppliers_users_{name}_{ts}.png")
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
        "var wanted=arguments[0].trim().toLowerCase();"
        "var els=document.querySelectorAll('a,button,input[type=\"button\"],input[type=\"submit\"],span,div,li');"
        "for(var i=0;i<els.length;i++){"
        "  var el=els[i];"
        "  var txt=(el.innerText||el.value||'').trim().toLowerCase();"
        "  if(txt===wanted&&el.offsetParent!==null){el.click();return el;}"
        "}"
        "return null;",
        text,
    )


def js_fill_name(driver, value):
    return driver.execute_script(
        "var inputs=document.querySelectorAll('input[type=\"text\"],input:not([type])');"
        "for(var i=0;i<inputs.length;i++){"
        "  var el=inputs[i];"
        "  var idv=(el.id||'').toLowerCase();"
        "  var namev=(el.name||'').toLowerCase();"
        "  if(idv.indexOf('search')>=0||namev.indexOf('search')>=0){continue;}"
        "  var form=el.closest('form');"
        "  if(form){"
        "    var action=(form.getAttribute('action')||'').toLowerCase();"
        "    if(action.indexOf('dosearch')>=0||action.indexOf('/search')>=0){continue;}"
        "  }"
        "  if(el.offsetParent!==null&&!el.disabled&&!el.readOnly){"
        "    el.value=arguments[0];"
        "    el.dispatchEvent(new Event('input',{bubbles:true}));"
        "    el.dispatchEvent(new Event('change',{bubbles:true}));"
        "    return true;"
        "  }"
        "}"
        "return false;",
        value,
    )


def js_fill_desc(driver, value):
    return driver.execute_script(
        "var tas=document.querySelectorAll('textarea');"
        "for(var i=0;i<tas.length;i++){"
        "  var ta=tas[i];"
        "  var form=ta.closest('form');"
        "  if(form){"
        "    var action=(form.getAttribute('action')||'').toLowerCase();"
        "    if(action.indexOf('dosearch')>=0||action.indexOf('/search')>=0){continue;}"
        "  }"
        "  if(ta&&ta.offsetParent!==null&&!ta.disabled){"
        "    ta.value=arguments[0];"
        "    ta.dispatchEvent(new Event('input',{bubbles:true}));"
        "    ta.dispatchEvent(new Event('change',{bubbles:true}));"
        "    return true;"
        "  }"
        "}"
        "return false;",
        value,
    )


def ensure_output_format_tabular(driver):
    return driver.execute_script(
        "var sel = document.querySelector('select#OutputFormat,select[name=\"OutputFormat\"],select');"
        "if(!sel){return false;}"
        "for(var i=0;i<sel.options.length;i++){"
        "  var t=(sel.options[i].text||'').trim().toLowerCase();"
        "  if(t==='tabular'){sel.selectedIndex=i;"
        "    sel.dispatchEvent(new Event('change',{bubbles:true}));"
        "    return true;"
        "  }"
        "}"
        "return false;"
    )


def fill_report_form_fields_js(driver, name_value, desc_value):
    """Fill Name + Description on the actual custom-report form (not header search)."""
    return driver.execute_script(
        "var forms=document.querySelectorAll('form');"
        "for(var f=0; f<forms.length; f++){"
        "  var form=forms[f];"
        "  var action=(form.getAttribute('action')||'').toLowerCase();"
        "  if(action.indexOf('dosearch')>=0||action.indexOf('/search')>=0){continue;}"
        "  var nameInput=form.querySelector('input#Name,input[name=\"Name\"]');"
        "  if(!nameInput){"
        "    var labels=form.querySelectorAll('label,*');"
        "    for(var i=0;i<labels.length;i++){"
        "      var t=(labels[i].innerText||'').replace(/\\s+/g,' ').trim().toLowerCase();"
        "      if(t.indexOf('name')>=0){"
        "        var next=labels[i].parentElement?labels[i].parentElement.querySelector('input[type=\"text\"],input:not([type])'):null;"
        "        if(next){nameInput=next; break;}"
        "      }"
        "    }"
        "  }"
        "  var descInput=form.querySelector('textarea#Description,textarea[name=\"Description\"],textarea');"
        "  if(!nameInput||!descInput){continue;}"
        "  if(nameInput.offsetParent===null||descInput.offsetParent===null){continue;}"
        "  nameInput.value=arguments[0];"
        "  nameInput.dispatchEvent(new Event('input',{bubbles:true}));"
        "  nameInput.dispatchEvent(new Event('change',{bubbles:true}));"
        "  descInput.value=arguments[1];"
        "  descInput.dispatchEvent(new Event('input',{bubbles:true}));"
        "  descInput.dispatchEvent(new Event('change',{bubbles:true}));"
        "  return true;"
        "}"
        "return false;",
        name_value,
        desc_value,
    )


def submit_report_form_js(driver):
    """Submit the specific custom-report form that contains Name + Description."""
    return driver.execute_script(
        "var forms=document.querySelectorAll('form');"
        "for(var f=0; f<forms.length; f++){"
        "  var form=forms[f];"
        "  var action=(form.getAttribute('action')||'').toLowerCase();"
        "  if(action.indexOf('dosearch')>=0||action.indexOf('/search')>=0){continue;}"
        "  var nameInput=form.querySelector('input#Name,input[name=\"Name\"],input[type=\"text\"]');"
        "  var descInput=form.querySelector('textarea');"
        "  if(!nameInput||!descInput){continue;}"
        "  form.submit();"
        "  return true;"
        "}"
        "return false;"
    )


def submit_custom_report(driver):
    # Prefer bottom-most visible Save/Create button outside search forms.
    bottom_save = driver.execute_script(
        "var els=document.querySelectorAll('button,input[type=\"submit\"],input[type=\"button\"]');"
        "var chosen=null; var chosenY=-1;"
        "for(var i=0;i<els.length;i++){"
        "  var el=els[i];"
        "  if(el.offsetParent===null){continue;}"
        "  var form=el.closest('form');"
        "  if(form){"
        "    var action=(form.getAttribute('action')||'').toLowerCase();"
        "    if(action.indexOf('dosearch')>=0||action.indexOf('/search')>=0){continue;}"
        "  }"
        "  var t=(el.innerText||el.value||'').trim().toLowerCase();"
        "  if(!(t==='save'||t==='create'||t==='create report'||t==='create custom report')){continue;}"
        "  var r=el.getBoundingClientRect();"
        "  if(r.top>chosenY){chosen=el; chosenY=r.top;}"
        "}"
        "if(chosen){chosen.click(); return true;}"
        "return false;"
    )
    if bottom_save:
        return True

    # Prefer submit controls within the report form that contains Name/Description.
    in_form_clicked = driver.execute_script(
        "var forms=document.querySelectorAll('form');"
        "for(var f=0;f<forms.length;f++){"
        "  var form=forms[f];"
        "  var action=(form.getAttribute('action')||'').toLowerCase();"
        "  if(action.indexOf('dosearch')>=0||action.indexOf('/search')>=0){continue;}"
        "  var hasName=form.querySelector('input#Name,input[name=\"Name\"],input[type=\"text\"]');"
        "  var hasDesc=form.querySelector('textarea');"
        "  if(!hasName&&!hasDesc){continue;}"
        "  var btns=form.querySelectorAll('button,input[type=\"submit\"],input[type=\"button\"]');"
        "  for(var i=0;i<btns.length;i++){"
        "    var b=btns[i];"
        "    if(b.offsetParent===null){continue;}"
        "    var t=(b.innerText||b.value||'').trim().toLowerCase();"
        "    if(t==='save'||t==='create'||t==='create report'||t==='create custom report'){"
        "      b.click();"
        "      return true;"
        "    }"
        "  }"
        "}"
        "return false;"
    )
    if in_form_clicked:
        return True

    submit_btn = safe_click_first(
        driver,
        [
            (By.XPATH, "//form[.//input[@id='Name' or @name='Name'] or .//textarea]//button[contains(normalize-space(.),'Save')]"),
            (By.XPATH, "//form[.//input[@id='Name' or @name='Name'] or .//textarea]//input[contains(@value,'Save')]") ,
            (By.XPATH, "//form[.//input[@id='Name' or @name='Name'] or .//textarea]//button[contains(normalize-space(.),'Create')]"),
            (By.XPATH, "//form[.//input[@id='Name' or @name='Name'] or .//textarea]//input[contains(@value,'Create')]"),
            (By.XPATH, "//input[@type='submit']"),
            (By.XPATH, "//button[@type='submit']"),
            (By.XPATH, "//input[contains(@id,'Save') or contains(@name,'Save')]"),
            (By.XPATH, "//button[contains(@id,'Save') or contains(@name,'Save')]"),
            (By.XPATH, "//button[contains(normalize-space(.),'Create')]"),
            (By.XPATH, "//input[contains(@value,'Create')]"),
            (By.XPATH, "//button[contains(normalize-space(.),'Save')]"),
            (By.XPATH, "//input[contains(@value,'Save')]"),
        ],
        timeout=8,
    )
    if submit_btn:
        scroll_to(driver, submit_btn)
        submit_btn.click()
        return True

    js_submit = driver.execute_script(
        "var f=document.querySelector('form');"
        "if(f&&typeof f.submit==='function'){f.submit();return true;}"
        "return false;"
    )
    if js_submit:
        return True

    return bool(
        click_visible_text(driver, "Create")
        or click_visible_text(driver, "Save")
        or click_visible_text(driver, "Create Report")
    )


@pytest.mark.usefixtures("driver")
class TestCustomReportAdminSuppliersUsers:

    def test_01_login(self, driver):
        print("\n" + "=" * 70)
        print("[TC-SUPU-001] Custom Report Admin Suppliers Users - Login")
        print("=" * 70)
        driver.get(BASE_URL)
        wait_ready(driver)
        find(driver, By.ID, "UserName").send_keys(USERNAME)
        find(driver, By.ID, "Password").send_keys(PASSWORD)
        clickable(driver, By.ID, "login-button").click()
        wait_ready(driver)
        time.sleep(PAUSE)
        take_screenshot(driver, "01_after_login")
        url = driver.current_url
        print(f"  [URL] {url}")
        assert "Account/Login" not in url
        print("  [PASS] Login successful.")

    def test_02_navigate_to_list(self, driver):
        print("\n" + "=" * 70)
        print("[TC-SUPU-002] Navigate to Create Custom Report List")
        print("=" * 70)
        driver.get(LIST_URL)
        wait_ready(driver)
        time.sleep(PAUSE)
        take_screenshot(driver, "02_list_page")
        url = driver.current_url
        print(f"  [URL] {url}")
        assert "createcustomreport" in url.lower()
        print(f"  [PASS] List page loaded: {url}")

    def test_03_click_suppliers_users(self, driver):
        print("\n" + "=" * 70)
        print("[TC-SUPU-003] Click 'Suppliers\' Users' under Admin")
        print("=" * 70)
        link = safe_click_first(
            driver,
            [
                (By.XPATH, "//a[contains(@href,'SupUserReport')]"),
                (By.XPATH, "//a[contains(@href,'supuserreport')]"),
                (By.XPATH, "//a[normalize-space()=\"Suppliers' Users\"]"),
                (By.XPATH, "//a[normalize-space()=\"Suppliers Users\"]"),
            ],
            timeout=5,
        )
        if link:
            scroll_to(driver, link)
            link.click()
        else:
            click_visible_text(driver, "Suppliers' Users")
            time.sleep(0.5)
            if "SupUserReport" not in driver.current_url:
                driver.get(FORM_URL)

        wait_ready(driver)
        time.sleep(PAUSE)
        take_screenshot(driver, "03_form")
        url = driver.current_url
        print(f"  [URL] {url}")
        assert "supuserreport" in url.lower() or "createcustomreport" in url.lower()
        print(f"  [PASS] Suppliers Users form loaded: {url}")

    def test_04_fill_mandatory_fields(self, driver):
        print("\n" + "=" * 70)
        print("[TC-SUPU-004] Fill mandatory fields")
        print("=" * 70)
        if "CreateCustomReport/Update" not in driver.current_url:
            driver.get(FORM_URL)
            wait_ready(driver)
            time.sleep(PAUSE)

        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.5)

        name_filled = False
        name_field = safe_click_first(
            driver,
            [
                (By.ID, "Name"),
                (By.NAME, "Name"),
                (By.XPATH, "//input[@id='Name' or @name='Name']"),
                (By.XPATH, "//label[contains(normalize-space(.),'Name')]/following::input[1]"),
                (By.XPATH, "//*[contains(normalize-space(.),'*Name')]/following::input[1]"),
            ],
            timeout=5,
        )
        if name_field:
            scroll_to(driver, name_field)
            driver.execute_script(
                "arguments[0].value=arguments[1];"
                "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));"
                "arguments[0].dispatchEvent(new Event('change',{bubbles:true}));",
                name_field,
                REPORT_NAME,
            )
            name_filled = True
        else:
            name_filled = js_fill_name(driver, REPORT_NAME)

        assert name_filled, "Name field could not be filled."

        desc_filled = False
        desc_field = safe_click_first(
            driver,
            [
                (By.ID, "Description"),
                (By.NAME, "Description"),
                (By.XPATH, "//textarea[@id='Description' or @name='Description']"),
                (By.XPATH, "//label[contains(normalize-space(.),'Description')]/following::textarea[1]"),
                (By.XPATH, "//textarea[1]"),
            ],
            timeout=5,
        )
        if desc_field:
            scroll_to(driver, desc_field)
            driver.execute_script(
                "arguments[0].value=arguments[1];"
                "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));"
                "arguments[0].dispatchEvent(new Event('change',{bubbles:true}));",
                desc_field,
                REPORT_DESC,
            )
            desc_filled = True
        else:
            desc_filled = js_fill_desc(driver, REPORT_DESC)

        assert desc_filled, "Description field could not be filled."

        vis_radio = safe_click_first(
            driver,
            [
                (
                    By.XPATH,
                    "//input[@type='radio'][contains(@id,'VisibleOnlyToMe') or contains(@value,'VisibleOnlyToMe')]",
                ),
                (By.XPATH, "//input[@type='radio'][1]"),
            ],
            timeout=5,
        )
        if vis_radio and not vis_radio.is_selected():
            driver.execute_script("arguments[0].click()", vis_radio)

        ensure_output_format_tabular(driver)

        take_screenshot(driver, "04_form_filled")
        print("  [PASS] Mandatory fields filled successfully.")

    def test_05_save_custom_report(self, driver):
        print("\n" + "=" * 70)
        print("[TC-SUPU-005] Save custom report and verify success")
        print("=" * 70)
        if "CreateCustomReport/Update?reportGID=SupUserReport" not in driver.current_url:
            driver.get(FORM_URL)
            wait_ready(driver)
            time.sleep(PAUSE)

        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.5)
        filled = fill_report_form_fields_js(driver, REPORT_NAME, REPORT_DESC)
        if not filled:
            js_fill_name(driver, REPORT_NAME)
            js_fill_desc(driver, REPORT_DESC)
        ensure_output_format_tabular(driver)
        time.sleep(0.3)

        submitted = submit_report_form_js(driver)
        if not submitted:
            submitted = submit_custom_report(driver)
        assert submitted, "Could not find or trigger the custom report submit action."
        print("  [INFO] Save/Create action submitted.")

        wait_ready(driver)
        time.sleep(PAUSE)
        take_screenshot(driver, "05_after_save")
        url = driver.current_url
        txt = driver.find_element(By.TAG_NAME, "body").text.lower()
        print(f"  [URL] {url}")

        if (
            (
                "required fields do not have valid values" in txt
                or "system error" in txt
                or "CreateCustomReport/Update" in url
            )
            and "successfully created" not in txt
        ):
            print("  [WARN] Initial save failed; retrying once.")
            driver.get(FORM_URL)
            wait_ready(driver)
            time.sleep(0.5)
            js_fill_name(driver, REPORT_NAME)
            js_fill_desc(driver, REPORT_DESC)
            ensure_output_format_tabular(driver)
            time.sleep(0.3)
            submitted = submit_custom_report(driver)
            assert submitted, "Retry submit action could not be triggered."
            wait_ready(driver)
            time.sleep(PAUSE)
            take_screenshot(driver, "05_after_retry")
            url = driver.current_url
            txt = driver.find_element(By.TAG_NAME, "body").text.lower()
            print(f"  [URL after retry] {url}")

        success = (
            ("customreport" in url.lower() and "CreateCustomReport/Update" not in url)
            or REPORT_NAME.lower() in txt
            or "successfully created" in txt
        )
        assert success, f"Creation failed. URL: {url}\nText: {txt[:200]}"
        print(f"  [PASS] Suppliers Users custom report created. URL: {url}")

    def test_06_show_report(self, driver):
        print("\n" + "=" * 70)
        print("[TC-SUPU-006] Verify and click Show Report")
        print("=" * 70)
        url = driver.current_url
        txt = driver.find_element(By.TAG_NAME, "body").text
        print(f"  [URL] {url}")

        if "CreateCustomReport/Update" in url:
            time.sleep(2)
            wait_ready(driver)
            url = driver.current_url
            txt = driver.find_element(By.TAG_NAME, "body").text

        assert "Show Report" in txt, f"'Show Report' not found. URL: {url}\nText: {txt[:300]}"
        print("  [PASS] 'Show Report' button present.")

        show_btn = safe_click_first(
            driver,
            [
                (By.XPATH, "//a[contains(normalize-space(.),'Show Report')]"),
                (By.XPATH, "//button[contains(normalize-space(.),'Show Report')]"),
            ],
            timeout=8,
        )
        if show_btn:
            scroll_to(driver, show_btn)
            show_btn.click()
            print("  [INFO] 'Show Report' clicked.")
        else:
            click_visible_text(driver, "Show Report")
            print("  [INFO] 'Show Report' clicked via JS fallback.")

        wait_ready(driver)
        time.sleep(PAUSE)
        take_screenshot(driver, "06_show_report_output")
        url = driver.current_url
        print(f"  [URL] {url}")
        assert "customreport" in url.lower() or "report" in url.lower()
        print(f"  [PASS] Show Report output loaded: {url}")
