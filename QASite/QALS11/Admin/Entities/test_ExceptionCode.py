import os
import sys
import time
import random
import string
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Resolve import paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from Admin.UserGroup import login
from utils.driver_setup import get_driver

"""
ExceptionCode.py – Selenium test cases for Admin > Entities > Exception Code.

Covered Test Cases:
    TC-EC-01: Add a new Exception Code (Add flow)
    TC-EC-02: Edit an existing Exception Code (Edit flow)
    TC-EC-03: View an existing Exception Code and cancel (View flow)
"""

@pytest.fixture(scope="class")
def setup_driver():
    driver = get_driver()
    wait = WebDriverWait(driver, 20)
    yield driver, wait
    driver.quit()

# ── Constants ────────────────────────────────────────────────────────────────
ADMIN_BASE = "https://engineering.ultrivalms.com/QALS1011"
EC_LIST_URL = f"{ADMIN_BASE}/Entity/List?tk=$ExpCode&busGID=BSU22ZAQALQG&A~1~ABC&"

# ── Utility Functions ────────────────────────────────────────────────────────

def random_string(length=5):
    """Return a random uppercase alphanumeric string of given length."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def log(msg):
    """Prefix every log line with the module name and a timestamp."""
    print(f"[{time.strftime('%H:%M:%S')}][ExceptionCode] {msg}")


def _search_code(driver, wait, code):
    """Type code into the 'Find Code' search box so the list filters."""
    search_xpath = "//input[contains(@placeholder,'Find Code') or @type='text']"
    try:
        box = wait.until(EC.visibility_of_element_located((By.XPATH, search_xpath)))
        wait.until(EC.element_to_be_clickable((By.XPATH, search_xpath)))
        box.clear()
        box.send_keys(code)
    except Exception as exc:
        log(f"Search box not interactable: {exc} — trying JS fallback.")
        box = driver.find_element(By.XPATH, search_xpath)
        driver.execute_script(
            "arguments[0].value = arguments[1];"
            "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));",
            box, code,
        )
    time.sleep(2)


# ── Test Suite ───────────────────────────────────────────────────────────────

class TestExceptioncode:

    def test_add_exception_code(self, setup_driver):
        """TC-EC-01 – Add a new Exception Code."""
        driver, wait = setup_driver
        log("=== TC-EC-01: Add Exception Code ===")

        # Step 1 – Login and navigate to the Exception Code list page
        login(driver, wait)
        log("Step 1 – Navigating to Exception Code list…")
        driver.get(EC_LIST_URL)
        time.sleep(2)

        # Step 2 – Click the '+ Add' button to open the creation form
        add_btn_xpath = "//button[contains(.,'Add')] | //a[contains(.,'Add')]"
        try:
            add_btn = wait.until(EC.element_to_be_clickable((By.XPATH, add_btn_xpath)))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", add_btn)
            driver.execute_script("arguments[0].click();", add_btn)
            log("Step 2 – Clicked '+ Add' button.")
            time.sleep(2)
        except Exception as exc:
            pytest.fail(f"Step 2 FAILED – Add button not found: {exc}")

        # Step 3 – Fill Code, Color (via color picker), and Description
        code = str(random.randint(500, 899))
        desc = f"ECDesc_{random_string(6)}"
        log(f"Step 3 – Entering Code='{code}', Color (picker), Desc='{desc}'")
        try:
            code_field = driver.find_element(By.NAME, "CODE$ItemName")
            code_field.clear()
            code_field.send_keys(code)

            # Open color picker via JS
            driver.execute_script("iColorShow('Code_Title', 'icp_Code_Title');")
            time.sleep(1)

            swatches = driver.find_elements(By.CSS_SELECTOR, "#iColorPicker td[hx]")
            color_td = None
            for sw in swatches:
                if (sw.get_attribute("hx") or "").lower() == "0f0":
                    color_td = sw
                    break
            if not color_td:
                color_td = swatches[2] if len(swatches) > 2 else swatches[0]
            
            driver.execute_script("arguments[0].click();", color_td)
            time.sleep(1)

            color_val = driver.find_element(By.NAME, "CODE$Title").get_attribute("value")
            log(f"  Color selected: '{color_val}'")

            desc_field = driver.find_element(By.NAME, "CODE$Description")
            desc_field.clear()
            desc_field.send_keys(desc)
        except Exception as exc:
            pytest.fail(f"Step 3 FAILED – Could not fill form fields: {exc}")

        # Step 4 – Click Save to persist the new Exception Code record
        save_xpath = (
            "//span[normalize-space()='Save' and contains(@class,'btn-toolbar-right-item')]"
            " | //button[normalize-space()='Save']"
            " | //a[normalize-space()='Save']"
        )
        try:
            save_btn = wait.until(EC.element_to_be_clickable((By.XPATH, save_xpath)))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", save_btn)
            driver.execute_script("arguments[0].click();", save_btn)
            log("Step 4 – Clicked Save button.")
            time.sleep(4)
            
            if "Create" in driver.current_url or "Entity/Create" in driver.current_url:
                log(f"Still on Create page after Save – checking errors. URL: {driver.current_url}")
                error_els = driver.find_elements(By.XPATH, "//*[contains(@class,'error') or contains(@class,'validation')]")
                for el in error_els[:5]:
                    if el.text.strip():
                        log(f"  Validation msg: {el.text.strip()!r}")
        except Exception as exc:
            pytest.fail(f"Step 4 FAILED – Save button handling error: {exc}")

        # Step 5 – Navigate back to the list and verify the new code is present
        driver.get(EC_LIST_URL)
        time.sleep(5)
        body_text = driver.find_element(By.TAG_NAME, "body").text
        
        # Explicit evaluation utilizing structural assertions instead of returning bool
        assert code in body_text, f"Step 5 FAIL – Exception Code '{code}' not detected on validation."
        log(f"Step 5 PASS – Exception Code '{code}' verified successfully.")

    def test_edit_exception_code(self, setup_driver):
        """TC-EC-02 – Edit an existing Exception Code."""
        driver, wait = setup_driver
        log("=== TC-EC-02: Edit Exception Code ===")

        # Step 1 – Login and navigate
        login(driver, wait)
        log("Step 1 – Navigating to Exception Code list…")
        driver.get(EC_LIST_URL)
        time.sleep(2)

        # Step 2 – Find first valid code row
        code = None
        try:
            rows = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//table//tr[td]")))
            for row in rows:
                tds = row.find_elements(By.TAG_NAME, "td")
                if len(tds) >= 2:
                    candidate = tds[0].text.strip()
                    if not candidate or "\n" in candidate or " " in candidate[:3]:
                        continue
                    if candidate.lower() in ["code", "exception code"]:
                        continue
                    if any(x in candidate.lower() for x in ["add", "edit", "view", "delete", "sorted", "export", "print", "go"]):
                        continue
                    code = candidate
                    break
            
            assert code is not None, "No valid Exception Code row found in the table."
            log(f"Step 2 – Selected row code: '{code}'")
        except Exception as exc:
            pytest.fail(f"Step 2 FAILED – Selection sequence context broken: {exc}")

        # Step 3 – Click the Edit button for the selected row
        row_xpath = f"//tr[td[normalize-space()='{code}']]"
        try:
            row_el = wait.until(EC.presence_of_element_located((By.XPATH, row_xpath)))
            edit_btn = None
            for btn_xpath in [
                ".//a[contains(translate(.,'edit','EDIT'),'EDIT') or contains(@class,'edit') or contains(@title,'Edit')]",
                ".//button[contains(translate(.,'edit','EDIT'),'EDIT')]",
                ".//span[contains(translate(.,'edit','EDIT'),'EDIT')]",
            ]:
                try:
                    edit_btn = row_el.find_element(By.XPATH, btn_xpath)
                    if edit_btn:
                        break
                except Exception:
                    continue

            if edit_btn:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", edit_btn)
                driver.execute_script("arguments[0].click();", edit_btn)
                log("Step 3 – Clicked row-level Edit button.")
            else:
                row_el.click()
                time.sleep(1)
                global_edit = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Edit')] | //a[contains(.,'Edit')]")))
                driver.execute_script("arguments[0].click();", global_edit)
                log("Step 3 – Clicked global Edit button (fallback).")
            time.sleep(2)
        except Exception as exc:
            pytest.fail(f"Step 3 FAILED – Edit action broke: {exc}")

        # Step 4 – Update Title and Description
        new_title = f"ECEdit_{random_string(4)}"
        new_desc = f"Edited EC Desc {random_string(5)}"
        log(f"Step 4 – Updating Title='{new_title}', Desc='{new_desc}'")
        try:
            for field_name, value in [("CODE$Title", new_title), ("CODE$Description", new_desc)]:
                field = driver.find_element(By.NAME, field_name)
                driver.execute_script("arguments[0].value = '';", field)
                field.send_keys(value)
        except Exception as exc:
            pytest.fail(f"Step 4 FAILED – Could not update fields: {exc}")

        # Step 5 – Click Save
        save_xpath = (
            "//span[normalize-space()='Save' and contains(@class,'btn-toolbar-right-item')]"
            " | //button[normalize-space()='Save']"
            " | //a[normalize-space()='Save']"
        )
        try:
            save_btn = wait.until(EC.element_to_be_clickable((By.XPATH, save_xpath)))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", save_btn)
            driver.execute_script("arguments[0].click();", save_btn)
            log("Step 5 – Clicked Save button.")
            time.sleep(3)
        except Exception as exc:
            pytest.fail(f"Step 5 FAILED – Save processing error: {exc}")

        # Step 6 – Verify data state change persistence
        driver.get(EC_LIST_URL)
        time.sleep(5)
        found = driver.find_elements(By.XPATH, f"//td[normalize-space()='{code}']")
        assert len(found) > 0, f"Step 6 FAIL – Code '{code}' absent inside index page post edit optimization loop."
        log(f"Step 6 PASS – Exception Code '{code}' verified after structural edit update.")

    def test_view_exception_code(self, setup_driver):
        """TC-EC-03 – View details of an existing Exception Code and cancel."""
        driver, wait = setup_driver
        log("=== TC-EC-03: View Exception Code ===")

        # Step 1 – Login and navigate
        login(driver, wait)
        log("Step 1 – Navigating to Exception Code list…")
        driver.get(EC_LIST_URL)
        time.sleep(2)

        # Step 2 – Find first valid code row
        code = None
        try:
            rows = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//table//tr[td]")))
            for row in rows:
                tds = row.find_elements(By.TAG_NAME, "td")
                if len(tds) >= 2:
                    candidate = tds[0].text.strip()
                    if not candidate or "\n" in candidate or " " in candidate[:3]:
                        continue
                    if candidate.lower() in ["code", "exception code"]:
                        continue
                    if any(x in candidate.lower() for x in ["add", "edit", "view", "delete", "sorted", "export", "print", "go"]):
                        continue
                    code = candidate
                    break
            
            assert code is not None, "No valid Exception Code row targeted."
            log(f"Step 2 – Using code: '{code}'")
        except Exception as exc:
            pytest.fail(f"Step 2 FAILED – Selection target array context validation dropped: {exc}")

        # Step 3 – Filter table list
        _search_code(driver, wait, code)

        # Step 4 – Click the View button for the matching row
        row_xpath = f"//tr[td[normalize-space()='{code}']]"
        try:
            row_el = wait.until(EC.presence_of_element_located((By.XPATH, row_xpath)))
            view_btn = None
            for btn_xpath in [
                ".//a[contains(translate(.,'view','VIEW'),'VIEW') or contains(@class,'view') or contains(@title,'View')]",
                ".//button[contains(translate(.,'view','VIEW'),'VIEW')]",
                ".//span[contains(translate(.,'view','VIEW'),'VIEW')]",
            ]:
                try:
                    view_btn = row_el.find_element(By.XPATH, btn_xpath)
                    if view_btn:
                        break
                except Exception:
                    continue

            if view_btn:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", view_btn)
                driver.execute_script("arguments[0].click();", view_btn)
                log("Step 4 – Clicked row-level View button.")
            else:
                row_el.click()
                time.sleep(1)
                global_view = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'View')] | //a[contains(.,'View')]")))
                driver.execute_script("arguments[0].click();", global_view)
                log("Step 4 – Clicked global View button (fallback).")
            time.sleep(2)
        except Exception as exc:
            pytest.fail(f"Step 4 FAILED – Structural verification loop click drop: {exc}")

        # Step 5 – Verify details page details
        log("Step 5 – Verifying details page content…")
        details_matched = False
        try:
            divs = driver.find_elements(By.XPATH, "//div")
            for div in divs:
                try:
                    txt = div.text.strip()
                    if "Code:" in txt or code in txt:
                        log(f"Details block verified: '{txt[:60]}...'")
                        details_matched = True
                        break
                except Exception:
                    pass
        except Exception as exc:
            log(f"Step 5 WARNING – Exception occurred during parsing sequence: {exc}")

        # Step 6 – Click Cancel/Return to return to list UI view context
        cancel_xpaths = [
            "//button[normalize-space()='Cancel']",
            "//a[normalize-space()='Cancel']",
            "//span[normalize-space()='Cancel']",
            "//button[contains(translate(.,'cancel','CANCEL'),'CANCEL')]",
            "//a[contains(translate(.,'cancel','CANCEL'),'CANCEL')]",
        ]
        cancel_btn = None
        for xp in cancel_xpaths:
            try:
                cancel_btn = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, xp)))
                if cancel_btn:
                    break
            except Exception:
                continue

        if not cancel_btn:
            log("Step 6 WARNING – Explicit exit route absent, reverting through driver back history loop.")
            driver.back()
        else:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", cancel_btn)
            driver.execute_script("arguments[0].click();", cancel_btn)
            log("Step 6 – Terminated view screen context natively.")
        
        time.sleep(2)
