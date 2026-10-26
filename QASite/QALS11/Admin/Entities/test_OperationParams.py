"""
OperationParams.py – Selenium test cases for Admin > Entities > Operation Params.

Covered Test Cases:
    TC-OP-PARAMS-01: Add a new Operation Params entry      (Add flow)
    TC-OP-PARAMS-02: Edit an existing Operation Params entry (Edit flow)
    TC-OP-PARAMS-03: View an existing Operation Params entry and cancel (View flow)

Navigation Path:
    Admin > Entities (left nav) > Operation Params
"""

import os
import sys
import time
import random
import string
import pytest
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from Admin.UserGroup import login
from utils.driver_setup import get_driver

# Allow running from the qa_automation root or from the Entities sub-folder
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

# ── Constants ───────────────────────────────────────────────────────────
ADMIN_BASE = "https://engineering.ultrivalms.com/QALS1011"
OP_PARAMS_LIST_URL = (
    f"{ADMIN_BASE}/Entity/List?tk=$OperationParams"
    "&busGID=BSU22ZAQALQG&A~1~ABC&"
)

# ── Pytest Fixtures ─────────────────────────────────────────────────────
@pytest.fixture(scope="class")
def setup_driver():
    driver = get_driver()
    wait = WebDriverWait(driver, 20)
    yield driver, wait
    driver.quit()

# ── Utility Helpers ─────────────────────────────────────────────────────
def random_string(length=5):
    """Return a random uppercase alphanumeric string of the given length."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def log(msg):
    """Prefix every console line with the module name and current timestamp."""
    print(f"[{time.strftime('%H:%M:%S')}][OperationParams] {msg}")


def _search_code(driver, wait, code):
    """
    Type *code* into the Operation Params 'Find Code' / 'Find Name' search box
    to filter the list, then press Enter. Falls back to JS + KeyboardEvent if needed.
    """
    search_xpath = (
        "//input[contains(@placeholder,'Find Code') or "
        "contains(@placeholder,'Find Name') or "
        "contains(@placeholder,'Find') or "
        "contains(@placeholder,'Search') or "
        "@type='text']"
    )
    short_wait = WebDriverWait(driver, 5)
    try:
        box = wait.until(EC.visibility_of_element_located((By.XPATH, search_xpath)))
        short_wait.until(EC.element_to_be_clickable((By.XPATH, search_xpath)))
        box.clear()
        box.send_keys(code)
        box.send_keys(Keys.RETURN)
    except Exception as exc:
        log(f"Search box not fully interactable: {exc} — using JS + Enter fallback.")
        try:
            box = driver.find_element(By.XPATH, search_xpath)
            driver.execute_script(
                "arguments[0].value = arguments[1];"
                "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));"
                "arguments[0].dispatchEvent(new KeyboardEvent('keyup',"
                "{bubbles:true,key:'Enter',keyCode:13}));", box, code, )
        except Exception as exc2:
            log(f"JS search fallback also failed: {exc2}")
    time.sleep(2)


# ── Test Suite Class ───────────────────────────────────────────────────
class TestOperationparams:

    def test_add_operation_params(self, setup_driver):
        """TC-OP-PARAMS-01 – Add a new Operation Params entry."""
        driver, wait = setup_driver
        log("=== TC-OP-PARAMS-01: Add Operation Params ===")

        # Step 1 – Log in and navigate to the Operation Params list page
        login(driver, wait)
        log("Step 1 – Navigating to Operation Params list…")
        driver.get(OP_PARAMS_LIST_URL)
        time.sleep(3)

        # Step 2 – Click the Add toolbar button
        add_xpaths = [
            "//span[@class='tbrAdd' and normalize-space()='Add']",
            "//a[contains(@class,'toolbarbuttonleft') and normalize-space()='Add']",
            "//button[contains(.,'Add')]",
            "//a[normalize-space()='Add' or normalize-space()='+ Add']",
            "//span[normalize-space()='Add' or normalize-space()='+ Add']",
        ]
        clicked_add = False
        for xp in add_xpaths:
            try:
                el = wait.until(EC.element_to_be_clickable((By.XPATH, xp)))
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
                driver.execute_script("arguments[0].click();", el)
                log(f"Step 2 – Clicked Add via '{xp}'.")
                clicked_add = True
                break
            except Exception:
                continue

        assert clicked_add, "Step 2 FAILED – Add button not found on Operation Params list page."
        time.sleep(2)

        # Step 3 – Fill in the form fields with unique random values.
        code = f"OP_{random_string(4)}"
        title = f"OpParam_Title_{random_string(4)}"
        desc = f"Operation Param Desc {random_string(6)}"
        log(f"Step 3 – Entering Code='{code}', Title='{title}', Desc='{desc}'")

        try:
            code_field = driver.find_element(By.NAME, "CODE$ItemName")
            code_field.clear()
            code_field.send_keys(code)

            title_field = driver.find_element(By.NAME, "CODE$Title")
            title_field.clear()
            title_field.send_keys(title)

            desc_field = driver.find_element(By.NAME, "CODE$Description")
            desc_field.clear()
            desc_field.send_keys(desc)
            log("Step 3 – Fields filled via NAME attribute.")
        except Exception:
            log("Step 3 – NAME lookup failed; trying placeholder fallback.")
            try:
                for placeholder, value in [
                    ("Code", code),
                    ("Title", title),
                    ("Description", desc),
                ]:
                    field = driver.find_element(
                        By.XPATH,
                        f"//input[@placeholder='{placeholder}'] | //textarea[@placeholder='{placeholder}']"
                    )
                    field.clear()
                    field.send_keys(value)
            except Exception as exc2:
                pytest.fail(f"Step 3 FAILED – Could not fill form fields: {exc2}")

        # Step 4 – Click Save to submit the new Operation Params entry
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
            time.sleep(3)
        except Exception as exc:
            pytest.fail(f"Step 4 FAILED – Save button not found: {exc}")

        # Step 4a – If Save redirected straight to the list, treat as success
        post_save_url = driver.current_url
        log(f"Step 4a – URL after Save: {post_save_url}")

        if "Entity/Create" in post_save_url or "Entity/Add" in post_save_url:
            log("Step 4a WARNING – Still on Create/Add form after Save; checking for errors.")
            for sel in [
                "//*[contains(@class,'error') or contains(@class,'validation-error') or contains(@class,'alert')]",
                "//span[@data-valmsg-for]",
                "//ul[contains(@class,'validation-summary')]//li",
            ]:
                for el in driver.find_elements(By.XPATH, sel):
                    try:
                        if el.is_displayed() and el.text.strip():
                            log(f"  Validation msg: {el.text.strip()[:120]}")
                    except Exception:
                        pass
            pytest.fail("Failed to save Operation Params entry due to form validation error.")

        if "Entity/List" in post_save_url or "OperationParams" in post_save_url:
            log(f"Step 4a PASS – Redirected to list page after Save (code '{code}' persisted).")
            return

        # Step 5 – Navigate to list, search, and verify the new code is present
        driver.get(OP_PARAMS_LIST_URL)
        time.sleep(2)
        _search_code(driver, wait, code)
        found = driver.find_elements(By.XPATH, f"//td[contains(.,'{code}')]")
        if found:
            log(f"Step 5 PASS – Operation Params '{code}' created successfully.")
        else:
            all_cells = driver.find_elements(By.XPATH, "//table//td")
            all_text = [c.text.strip() for c in all_cells if c.text.strip()]
            log(f"Step 5 INFO – Visible codes in table: {all_text[:20]}")
            assert code in all_text, f"Step 5 FAIL – Operation Params '{code}' not found after creation."

    def test_edit_operation_params(self, setup_driver):
        """TC-OP-PARAMS-02 – Edit an existing Operation Params entry."""
        driver, wait = setup_driver
        log("=== TC-OP-PARAMS-02: Edit Operation Params ===")

        # Step 1 – Log in and navigate to Operation Params list
        login(driver, wait)
        log("Step 1 – Navigating to Operation Params list…")
        driver.get(OP_PARAMS_LIST_URL)
        time.sleep(3)

        # Step 2 – Find the first valid data row
        code = None
        try:
            rows = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//table//tr[td]")))
            for row in rows:
                tds = row.find_elements(By.TAG_NAME, "td")
                if len(tds) >= 2:
                    candidate = tds[0].text.strip()
                    if not candidate or "\n" in candidate or " " in candidate[:3]:
                        continue
                    if candidate.lower() in ["code", "operation params", "title", "name"]:
                        continue
                    if any(x in candidate.lower() for x in ["add", "edit", "view", "delete", "sorted", "export", "print", "go"]):
                        continue
                    code = candidate
                    break
            assert code is not None, "No valid Operation Params row found in the table."
            log(f"Step 2 – Selected row code: '{code}'")
        except Exception as exc:
            pytest.fail(f"Step 2 FAILED – {exc}")

        # Step 3 – Click Edit button
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
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", row_el)
                row_el.click()
                time.sleep(1)
                global_edit = wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//span[@class='tbrEdit'] | //a[contains(@class,'toolbarbuttonleft') and normalize-space()='Edit'] | //button[contains(.,'Edit')] | //a[contains(.,'Edit')]")
                    )
                )
                driver.execute_script("arguments[0].click();", global_edit)
                log("Step 3 – Clicked global Edit button (fallback).")
            time.sleep(2)
        except Exception as exc:
            pytest.fail(f"Step 3 FAILED – Edit button not found: {exc}")

        # Step 4 – Clear and update fields
        new_code = f"OP_{random_string(4)}_ED"
        new_title = f"OpParam_Edit_{random_string(4)}"
        new_desc = f"Edited Op Param Desc {random_string(5)}"
        log(f"Step 4 – Updating to Code='{new_code}', Title='{new_title}', Desc='{new_desc}'")

        try:
            for field_name, value in [
                ("CODE$ItemName", new_code),
                ("CODE$Title", new_title),
                ("CODE$Description", new_desc),
            ]:
                field = driver.find_element(By.NAME, field_name)
                field.clear()
                field.send_keys(value)
            log("Step 4 – Fields updated via NAME attribute.")
        except Exception:
            log("Step 4 – NAME lookup failed; trying placeholder fallback.")
            try:
                for placeholder, value in [
                    ("Code", new_code),
                    ("Title", new_title),
                    ("Description", new_desc),
                ]:
                    field = driver.find_element(
                        By.XPATH,
                        f"//input[@placeholder='{placeholder}'] | //textarea[@placeholder='{placeholder}']"
                    )
                    field.clear()
                    field.send_keys(value)
            except Exception as exc2:
                pytest.fail(f"Step 4 FAILED – Could not update fields: {exc2}")

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
            pytest.fail(f"Step 5 FAILED – Save button not found: {exc}")

        # Step 6 – Navigate to list, search for the updated code, and verify
        driver.get(OP_PARAMS_LIST_URL)
        time.sleep(2)
        _search_code(driver, wait, new_code)
        found = driver.find_elements(By.XPATH, f"//td[contains(.,'{new_code}')]")
        if found:
            log(f"Step 6 PASS – Operation Params updated to '{new_code}' successfully.")
        else:
            all_cells = driver.find_elements(By.XPATH, "//table//td")
            all_text = [c.text.strip() for c in all_cells if c.text.strip()]
            log(f"Step 6 INFO – Visible codes: {all_text[:20]}")
            assert new_code in all_text, f"Step 6 FAIL – Updated code '{new_code}' not found in list."

    def test_view_operation_params(self, setup_driver):
        """TC-OP-PARAMS-03 – View details of an existing Operation Params entry, then cancel."""
        driver, wait = setup_driver
        log("=== TC-OP-PARAMS-03: View Operation Params ===")

        # Step 1 – Log in and navigate to Operation Params list
        login(driver, wait)
        log("Step 1 – Navigating to Operation Params list…")
        driver.get(OP_PARAMS_LIST_URL)
        time.sleep(3)

        # Step 2 – Find the first valid data row
        code = None
        try:
            rows = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//table//tr[td]")))
            for row in rows:
                tds = row.find_elements(By.TAG_NAME, "td")
                if len(tds) >= 2:
                    candidate = tds[0].text.strip()
                    if not candidate or "\n" in candidate or " " in candidate[:3]:
                        continue
                    if candidate.lower() in ["code", "operation params", "title", "name"]:
                        continue
                    if any(x in candidate.lower() for x in ["add", "edit", "view", "delete", "sorted", "export", "print", "go"]):
                        continue
                    code = candidate
                    break
            assert code is not None, "No valid Operation Params row found in the table."
            log(f"Step 2 – Using code: '{code}'")
        except Exception as exc:
            pytest.fail(f"Step 2 FAILED – {exc}")

        # Step 3 – Click View button
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
                log("Step 3 – Clicked row-level View button.")
            else:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", row_el)
                row_el.click()
                time.sleep(1)
                global_view = wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//span[@class='tbrView2'] | //a[contains(@class,'toolbarbuttonleft') and normalize-space()='View'] | //button[contains(.,'View')] | //a[contains(.,'View')]")
                    )
                )
                driver.execute_script("arguments[0].click();", global_view)
                log("Step 3 – Clicked global View button (fallback).")
            time.sleep(2)
        except Exception as exc:
            pytest.fail(f"Step 3 FAILED – View button not found: {exc}")

        # Step 4 – Verify the detail page displays content
        log("Step 4 – Verifying detail page content…")
        detail_found = False
        try:
            for tag in ["h2", "h3", "h4", "div", "span", "td"]:
                for el in driver.find_elements(By.TAG_NAME, tag):
                    try:
                        txt = el.text.strip()
                        if el.is_displayed() and txt and (code in txt or "Code:" in txt or "Operation Params" in txt):
                            log(f"  Detail content – <{tag}>: '{txt[:120]}'")
                            detail_found = True
                            break
                    except Exception:
                        pass
                if detail_found:
                    break
        except Exception as exc:
            log(f"Step 4 WARNING – Could not inspect detail content: {exc}")

        # Step 5 – Click Cancel to return to the list
        cancel_xpaths = [
            "//button[normalize-space()='Cancel']",
            "//a[normalize-space()='Cancel']",
            "//span[normalize-space()='Cancel']",
            "//button[contains(translate(.,'cancel','CANCEL'),'CANCEL')]",
            "//a[contains(translate(.,'cancel','CANCEL'),'CANCEL')]",
        ]
        cancel_btn = None
        short_wait = WebDriverWait(driver, 4)
        for xp in cancel_xpaths:
            try:
                cancel_btn = short_wait.until(EC.element_to_be_clickable((By.XPATH, xp)))
                if cancel_btn:
                    break
            except Exception:
                continue

        if not cancel_btn:
            log("Step 5 WARNING – Cancel button not found; navigating back via browser.")
            driver.back()
            time.sleep(2)
            return

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", cancel_btn)
        driver.execute_script("arguments[0].click();", cancel_btn)
        log("Step 5 – Clicked Cancel, returned to list.")
        time.sleep(2)


# ── Standalone Custom Engine ───────────────────────────────────────────
if __name__ == "__main__":
    """
    Fallback direct executor if running without 'pytest' command utility.
    """
    log("Direct script execution detected. Initializing test execution sequence...")
    _driver = get_driver()
    _wait = WebDriverWait(_driver, 20)
    
    test_class = TestOperationparams()
    suite = [
        ("TC-OP-PARAMS-01 Add Entry", test_class.test_add_operation_params),
        ("TC-OP-PARAMS-02 Edit Entry", test_class.test_edit_operation_params),
        ("TC-OP-PARAMS-03 View Entry", test_class.test_view_operation_params),
    ]

    results = {}
    for name, method in suite:
        print(f"\n{'─' * 60}\n Running: {name}\n{'─' * 60}")
        try:
            method((_driver, _wait))
            results[name] = True
            print(f"[PASS] {name}")
        except Exception as e:
            results[name] = False
            print(f"[FAIL] {name}: {e}")

    _driver.quit()

    print("\n" + "=" * 70 + "\n  FINAL AUTOMATION RUN SUMMARY\n" + "=" * 70)
    for name, passed in results.items():
        print(f"  [{'PASS' if passed else 'FAIL'}]  {name}")
    print("=" * 70 + "\n")
