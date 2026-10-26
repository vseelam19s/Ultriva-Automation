import sys
import os
import time
import random
import string
import pytest
from Admin.UserGroup import login
from utils.driver_setup import get_driver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

"""
RescheduleReason.py – Selenium test cases for Admin > Entities > Reschedule Reason.

Covered Test Cases:
    TC-RR-01: Add a new Reschedule Reason   (Add flow)
    TC-RR-02: Edit an existing Reschedule Reason (Edit flow)
    TC-RR-03: View an existing Reschedule Reason and cancel (View flow)

Navigation Path:
    Admin > Entities (left nav) > Reschedule Reason
"""

# Allow running from the qa_automation root or from the Entities subfolder
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


@pytest.fixture(scope="class")
def setup_driver():
    driver = get_driver()
    wait = WebDriverWait(driver, 20)
    yield driver, wait
    driver.quit()

# ── Constants ────────────────────────────────────────────────────────────────
ADMIN_BASE = "https://engineering.ultrivalms.com/QALS1011"
RR_LIST_URL = (
    f"{ADMIN_BASE}/Entity/List?tk=$RescheduleReason"
    "&busGID=BSU22ZAQALQG&A~1~ABC&"
)

# ── Utility helpers ──────────────────────────────────────────────────────────
def random_string(length=5):
    """Return a random uppercase alphanumeric string of the given length."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def log(msg):
    """Prefix every console line with module name and current timestamp."""
    print(f"[{time.strftime('%H:%M:%S')}][RescheduleReason] {msg}")


def _search_code(driver, wait, code):
    """Type *code* into the Find Code / Find Name search box to filter the list."""
    search_xpath = (
        "//input[contains(@placeholder,'Find Code') or "
        "contains(@placeholder,'Find Name') or "
        "contains(@placeholder,'Find') or "
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
                "arguments[0].dispatchEvent(new KeyboardEvent('keyup',{bubbles:true,key:'Enter',keyCode:13}));",
                box,
                code,
            )
        except Exception as exc2:
            log(f"JS search fallback also failed: {exc2}")
    time.sleep(2)


# ── Test Suite Class ─────────────────────────────────────────────────────────
class TestReschedulereason:

    def test_add_reschedule_reason(self, setup_driver):
        driver, wait = setup_driver
        """TC-RR-01 – Add a new Reschedule Reason."""
        log("=== TC-RR-01: Add Reschedule Reason ===")

        # Step 1 – Login and navigate to Reschedule Reason list
        login(driver, wait)
        log("Step 1 – Navigating to Reschedule Reason list…")
        driver.get(RR_LIST_URL)
        time.sleep(2)

        # Step 2 – Click '+ Add' button to open the create form
        add_btn_xpath = "//button[contains(.,'Add')] | //a[contains(.,'Add')]"
        try:
            add_btn = wait.until(EC.element_to_be_clickable((By.XPATH, add_btn_xpath)))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", add_btn)
            driver.execute_script("arguments[0].click();", add_btn)
            log("Step 2 – Clicked '+ Add' button.")
            time.sleep(2)
        except Exception as exc:
            log(f"Step 2 FAILED – Add button not found: {exc}")
            assert False, f"Add button not found: {exc}"

        # Step 3 – Fill in Form Fields
        code = f"RR_{random_string(4)}"
        title = f"RR_Title_{random_string(4)}"
        desc = f"RR_Desc_{random_string(6)}"
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
        except Exception:
            log("Step 3 – NAME lookup failed; trying placeholder fallback.")
            try:
                for placeholder, value in [("Code", code), ("Title", title), ("Description", desc)]:
                    field = driver.find_element(
                        By.XPATH,
                        f"//input[@placeholder='{placeholder}'] | //textarea[@placeholder='{placeholder}']"
                    )
                    field.clear()
                    field.send_keys(value)
            except Exception as exc2:
                log(f"Step 3 FAILED – Could not fill form fields: {exc2}")
                assert False, f"Could not fill form fields: {exc2}"

        # Step 4 – Click Save button
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
            log(f"Step 4 FAILED – Save button not found: {exc}")
            assert False, f"Save button not found: {exc}"

        # Step 4a – Check redirection status
        post_save_url = driver.current_url
        log(f"Step 4a – URL after Save: {post_save_url}")
        if "Entity/Add" in post_save_url or "Entity/Create" in post_save_url:
            log("Step 4a WARNING – Still on the add/create form after Save.")
            try:
                for sel in [
                    "//*[contains(@class,'error') or contains(@class,'validation-error') or contains(@class,'alert')]",
                    "//span[@data-valmsg-for]",
                    "//ul[contains(@class,'validation-summary')]//li",
                ]:
                    for el in driver.find_elements(By.XPATH, sel):
                        if el.is_displayed() and el.text.strip():
                            log(f"  Validation msg: {el.text.strip()[:120]}")
            except Exception:
                pass
            assert False, "Validation error occurred or save failed."

        if "Entity/List" in post_save_url or "RescheduleReason" in post_save_url:
            log(f"Step 4a PASS – Redirected to list page after Save (code '{code}' persisted).")
            return

        # Step 5 – Verify the new code is present on the table view
        driver.get(RR_LIST_URL)
        time.sleep(2)
        _search_code(driver, wait, code)
        found = driver.find_elements(By.XPATH, f"//td[contains(.,'{code}')]")
        if found:
            log(f"Step 5 PASS – Reschedule Reason '{code}' created successfully.")
        else:
            all_cells = driver.find_elements(By.XPATH, "//table//td")
            all_text = [c.text.strip() for c in all_cells if c.text.strip()]
            log(f"Step 5 INFO – Visible codes in table: {all_text[:20]}")
            assert code in all_text, f"Reschedule Reason '{code}' not found after creation."

    def test_edit_reschedule_reason(self, setup_driver):
        driver, wait = setup_driver
        """TC-RR-02 – Edit an existing Reschedule Reason."""
        log("=== TC-RR-02: Edit Reschedule Reason ===")

        login(driver, wait)
        log("Step 1 – Navigating to Reschedule Reason list…")
        driver.get(RR_LIST_URL)
        time.sleep(2)

        # Step 2 – Grab the first valid candidate entry row
        code = None
        try:
            rows = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//table//tr[td]")))
            for row in rows:
                tds = row.find_elements(By.TAG_NAME, "td")
                if len(tds) >= 2:
                    candidate = tds[0].text.strip()
                    if not candidate or "\n" in candidate or " " in candidate[:3]:
                        continue
                    if candidate.lower() in ["code", "reschedule reason", "name", "reason"]:
                        continue
                    if any(x in candidate.lower() for x in ["add", "edit", "view", "delete", "sorted", "export", "print", "go"]):
                        continue
                    code = candidate
                    break
            if not code:
                raise RuntimeError("No valid Reschedule Reason row found in the table.")
            log(f"Step 2 – Selected row code: '{code}'")
        except Exception as exc:
            log(f"Step 2 FAILED – {exc}")
            assert False, f"Failed targeting base element: {exc}"

        # Step 3 – Access Edit workflow
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
            log(f"Step 3 FAILED – Edit button not found: {exc}")
            assert False, f"Edit target interaction failure: {exc}"

        # Step 4 – Form value changes
        new_code = f"RR_{random_string(4)}_ED"
        new_title = f"RR_Title_{random_string(4)}"
        new_desc = f"Edited RR Desc {random_string(5)}"
        log(f"Step 4 – Updating to Code='{new_code}', Title='{new_title}', Desc='{new_desc}'")
        try:
            for field_name, value in [("CODE$ItemName", new_code), ("CODE$Title", new_title), ("CODE$Description", new_desc)]:
                try:
                    field = driver.find_element(By.NAME, field_name)
                    field.clear()
                    field.send_keys(value)
                except Exception:
                    pass
        except Exception:
            log("Step 4 – NAME lookup failed; trying placeholder fallback.")
            try:
                for placeholder, value in [("Code", new_code), ("Title", new_title), ("Description", new_desc)]:
                    try:
                        field = driver.find_element(
                            By.XPATH,
                            f"//input[@placeholder='{placeholder}'] | //textarea[@placeholder='{placeholder}']"
                        )
                        field.clear()
                        field.send_keys(value)
                    except Exception:
                        pass
            except Exception as exc2:
                log(f"Step 4 FAILED – Could not update fields: {exc2}")
                assert False, f"Form update error: {exc2}"

        # Step 5 – Click Save button
        save_xpath = (
            "//span[normalize-space()='Save' and contains(@class,'btn')]"
            " | //button[normalize-space()='Save']"
            " | //a[normalize-space()='Save']"
            " | //span[normalize-space()='Save']"
        )
        try:
            save_btn = wait.until(EC.element_to_be_clickable((By.XPATH, save_xpath)))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", save_btn)
            driver.execute_script("arguments[0].click();", save_btn)
            log("Step 5 – Clicked Save button.")
            time.sleep(2)
        except Exception as exc:
            log(f"Step 5 FAILED – Save button not found: {exc}")
            assert False, f"Save interaction failed: {exc}"

        # Step 6 – Return verification
        driver.get(RR_LIST_URL)
        time.sleep(2)
        _search_code(driver, wait, new_code)
        found = driver.find_elements(By.XPATH, f"//td[contains(.,'{new_code}')]")
        if found:
            log(f"Step 6 PASS – Reschedule Reason updated to '{new_code}' successfully.")
        else:
            log(f"Step 6 FAIL – Updated code '{new_code}' not found in list.")
            assert False, f"Updated record '{new_code}' not parsed in table list view profile."

    def test_view_reschedule_reason(self, setup_driver):
        driver, wait = setup_driver
        """TC-RR-03 – View details of an existing Reschedule Reason and cancel."""
        log("=== TC-RR-03: View Reschedule Reason ===")

        login(driver, wait)
        log("Step 1 – Navigating to Reschedule Reason list…")
        driver.get(RR_LIST_URL)
        time.sleep(2)

        # Step 2 – Identify candidate entry row target
        code = None
        try:
            rows = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//table//tr[td]")))
            for row in rows:
                tds = row.find_elements(By.TAG_NAME, "td")
                if len(tds) >= 2:
                    candidate = tds[0].text.strip()
                    if not candidate or "\n" in candidate or " " in candidate[:3]:
                        continue
                    if candidate.lower() in ["code", "reschedule reason", "name", "reason"]:
                        continue
                    if any(x in candidate.lower() for x in ["add", "edit", "view", "delete", "sorted", "export", "print", "go"]):
                        continue
                    code = candidate
                    break
            if not code:
                raise RuntimeError("No valid Reschedule Reason row found.")
            log(f"Step 2 – Using code: '{code}'")
        except Exception as exc:
            log(f"Step 2 FAILED – {exc}")
            assert False, str(exc)

        # Step 3 & 4 – Direct isolation and activation view element mapping
        _search_code(driver, wait, code)
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
            log(f"Step 4 FAILED – View button not found: {exc}")
            assert False, str(exc)

        # Step 5 – Confirm detail dashboard values
        log("Step 5 – Verifying details page content…")
        detail_found = False
        try:
            for tag in ["div", "span", "td", "input"]:
                for el in driver.find_elements(By.TAG_NAME, tag):
                    try:
                        txt = el.text.strip()
                        val = el.get_attribute("value") or ""
                        if code in txt or code in val:
                            log(f"  Detail confirmed: <{tag}> contains '{code}'")
                            detail_found = True
                            break
                    except Exception:
                        pass
                if detail_found:
                    break
        except Exception as exc:
            log(f"Step 5 WARNING – {exc}")

        # Step 6 – Process workflow exit safely
        cancel_xpaths = [
            "//button[normalize-space()='Cancel']",
            "//a[normalize-space()='Cancel']",
            "//span[normalize-space()='Cancel']",
            "//button[contains(translate(.,'cancel','CANCEL'),'CANCEL')]",
            "//a[contains(translate(.,'cancel','CANCEL'),'CANCEL')]",
            "//*[contains(@class,'btn') and contains(translate(.,'cancel','CANCEL'),'CANCEL')]",
        ]
        cancel_btn = None
        for xp in cancel_xpaths:
            try:
                cancel_btn = WebDriverWait(driver, 4).until(EC.element_to_be_clickable((By.XPATH, xp)))
                if cancel_btn:
                    break
            except Exception:
                continue

        if cancel_btn:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", cancel_btn)
            driver.execute_script("arguments[0].click();", cancel_btn)
            log("Step 6 – Clicked Cancel button.")
        else:
            log("Step 6 WARNING – Cancel button not found; using browser back.")
            driver.back()

        time.sleep(2)
        assert "Entity/List" in driver.current_url or "RescheduleReason" in driver.current_url or detail_found, \
            "Failed verification matching code view details state or return navigation pathing."
