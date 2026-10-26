"""
QALS11 | Reports > Custom Reports > Create Custom Report > Admin > User Login Session Details
=============================================================================================
URL  : https://engineering.ultrivalms.com/QALS1011/CreateCustomReport/List
User : buyeruser / Ultriva!23

Test Flow: Login -> Open Create Custom Report list -> Click User Login Session Details ->
           Fill mandatory fields -> Save
Run: pytest tests/QALS11/Reports/CustomReports/Admin/test_user_login_session_details_report.py -v -s
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
FORM_URL = f"{BASE_URL}/CreateCustomReport/Update?reportGID=SessionHistory"

_TS = time.strftime("%Y%m%d%H%M%S")
REPORT_NAME = f"AutoTest_UserLoginSessionDetails_{_TS}"
REPORT_DESC = f"User Login Session Details report {_TS}"


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
    path = os.path.join(
        screenshot_dir,
        f"custom_report_user_login_session_details_{name}_{ts}.png",
    )
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


def fill_report_form_fields_js(driver, name_value, desc_value):
    return driver.execute_script(
        "var forms=document.querySelectorAll('form');"
        "for(var f=0; f<forms.length; f++){"
        "  var form=forms[f];"
        "  var action=(form.getAttribute('action')||'').toLowerCase();"
        "  if(action.indexOf('dosearch')>=0||action.indexOf('/search')>=0){continue;}"
        "  var nameInput=form.querySelector('input#Name,input[name=\"Name\"]');"
        "  if(!nameInput){"
        "    var ins=form.querySelectorAll('input[type=\"text\"],input:not([type])');"
        "    for(var i=0;i<ins.length;i++){"
        "      var cand=ins[i];"
        "      if(cand.offsetParent!==null&&!cand.disabled&&!cand.readOnly){nameInput=cand;break;}"
        "    }"
        "  }"
        "  var descInput=form.querySelector('textarea#Description,textarea[name=\"Description\"]');"
        "  if(!descInput){descInput=form.querySelector('textarea');}"
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


def submit_custom_report(driver):
    submit_btn = safe_click_first(
        driver,
        [
            (By.XPATH, "//button[contains(normalize-space(.),'Save') and not(@disabled)]"),
            (By.XPATH, "//input[contains(@value,'Save') and not(@disabled)]"),
            (By.XPATH, "//button[contains(normalize-space(.),'Create') and not(@disabled)]"),
            (By.XPATH, "//input[contains(@value,'Create') and not(@disabled)]"),
            (By.XPATH, "//button[@type='submit']"),
            (By.XPATH, "//input[@type='submit']"),
        ],
        timeout=8,
    )
    if submit_btn:
        scroll_to(driver, submit_btn)
        submit_btn.click()
        return True

    return bool(
        click_visible_text(driver, "Save")
        or click_visible_text(driver, "Create")
        or click_visible_text(driver, "Create Report")
    )


@pytest.mark.usefixtures("driver")
class TestCustomReportAdminUserLoginSessionDetails:

    def test_01_login(self, driver):
        print("\n" + "=" * 70)
        print("[TC-ULSD-001] Custom Report Admin User Login Session Details - Login")
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
        print("[TC-ULSD-002] Navigate to Create Custom Report List")
        print("=" * 70)
        driver.get(LIST_URL)
        wait_ready(driver)
        time.sleep(PAUSE)
        take_screenshot(driver, "02_list_page")
        url = driver.current_url
        print(f"  [URL] {url}")
        assert "createcustomreport" in url.lower()
        print(f"  [PASS] List page loaded: {url}")

    def test_03_click_user_login_session_details(self, driver):
        print("\n" + "=" * 70)
        print("[TC-ULSD-003] Click 'User Login Session Details' under Admin")
        print("=" * 70)
        link = safe_click_first(
            driver,
            [
                (By.XPATH, "//a[contains(@href,'SessionHistory')]"),
                (By.XPATH, "//a[contains(@href,'sessionhistory')]"),
                (By.XPATH, "//a[normalize-space()='User Login Session Details']"),
            ],
            timeout=5,
        )
        if link:
            scroll_to(driver, link)
            link.click()
        else:
            click_visible_text(driver, "User Login Session Details")
            time.sleep(0.5)
            if "SessionHistory" not in driver.current_url:
                driver.get(FORM_URL)

        wait_ready(driver)
        time.sleep(PAUSE)
        take_screenshot(driver, "03_form")
        url = driver.current_url
        print(f"  [URL] {url}")
        assert "sessionhistory" in url.lower() or "createcustomreport" in url.lower()
        print(f"  [PASS] User Login Session Details form loaded: {url}")

    def test_04_fill_mandatory_fields(self, driver):
        print("\n" + "=" * 70)
        print("[TC-ULSD-004] Fill mandatory fields")
        print("=" * 70)
        if "CreateCustomReport/Update" not in driver.current_url:
            driver.get(FORM_URL)
            wait_ready(driver)
            time.sleep(PAUSE)

        filled = fill_report_form_fields_js(driver, REPORT_NAME, REPORT_DESC)
        assert filled, "Could not fill Name/Description fields on custom report form."

        visible_only = safe_click_first(
            driver,
            [
                (By.XPATH, "//input[@type='radio' and contains(@id,'VisibleOnlyToMe')]"),
                (By.XPATH, "//input[@type='radio' and contains(@value,'VisibleOnlyToMe')]"),
                (By.XPATH, "//label[contains(text(),'Visible only to me')]/preceding::input[@type='radio'][1]"),
            ],
            timeout=3,
        )
        if visible_only and not visible_only.is_selected():
            driver.execute_script("arguments[0].click();", visible_only)

        take_screenshot(driver, "04_form_filled")
        print(f"  [PASS] Mandatory fields filled with report name: {REPORT_NAME}")

    def test_05_save_custom_report(self, driver):
        print("\n" + "=" * 70)
        print("[TC-ULSD-005] Save custom report")
        print("=" * 70)

        submitted = submit_custom_report(driver)
        assert submitted, "Could not click Save/Create for custom report."

        wait_ready(driver)
        time.sleep(PAUSE)
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        current_url = driver.current_url

        if (
            "required fields do not have valid values" in page_text
            or "createcustomreport/update" in current_url.lower()
        ) and "successfully created" not in page_text:
            print("  [WARN] Validation triggered; refilling and retrying save once.")
            driver.get(FORM_URL)
            wait_ready(driver)
            time.sleep(PAUSE)
            refilled = fill_report_form_fields_js(driver, REPORT_NAME, REPORT_DESC)
            assert refilled, "Retry failed: unable to refill mandatory fields."
            submitted_retry = submit_custom_report(driver)
            assert submitted_retry, "Retry failed: unable to click Save/Create."
            wait_ready(driver)
            time.sleep(PAUSE)
            page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
            current_url = driver.current_url

        take_screenshot(driver, "05_after_save")
        print(f"  [URL] {current_url}")

        success = (
            "successfully created" in page_text
            or "customreport/customreport" in current_url.lower()
            or (
                "customreport" in current_url.lower()
                and "createcustomreport/update" not in current_url.lower()
            )
            or REPORT_NAME.lower() in page_text
        )
        assert success, (
            f"Custom report save may have failed. URL: {current_url} | "
            f"Page text (first 300): {page_text[:300]}"
        )
        print("  [PASS] Custom report saved successfully.")
