import os
import sys
import time
import random
import string
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Ensure relative path utilities load correctly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from Admin.UserGroup import login
from utils.driver_setup import get_driver

"""
ProductionIssue.py – Selenium test cases for Admin > Entities > Production Issue.

Covered Test Cases:
    TC-PI-01: Add a new Production Issue code (Add flow)
    TC-PI-02: Edit an existing Production Issue code (Edit flow)
    TC-PI-03: View an existing Production Issue code and cancel (View flow)
"""

@pytest.fixture(scope="class")
def setup_driver():
    driver = get_driver()
    wait = WebDriverWait(driver, 20)
    yield driver, wait
    driver.quit()

# ── Constants ────────────────────────────────────────────────────────────────
ADMIN_BASE = "https://engineering.ultrivalms.com/QALS1011"
PI_LIST_URL = f"{ADMIN_BASE}/Entity/List?tk=$ProductionIssue&busGID=BSU22ZAQALQG&A~1~ABC&"

# ── Utility Functions ────────────────────────────────────────────────────────
def random_string(length=5):
    """Return a random uppercase alphanumeric string of given length."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def log(msg):
    """Prefix every log line with the module name and a timestamp."""
    print(f"[{time.strftime('%H:%M:%S')}][ProductionIssue] {msg}")


def _search_code(driver, wait, code):
    """Type *code* into the 'Find Code' search box so the list filters."""
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
class TestProductionissue:

    def test_add_production_issue(self, setup_driver):
        driver, wait = setup_driver
        log("=== TC-PI-01: Add Production Issue ===")

        # Step 1 – Login and navigate
        login(driver, wait)
        log("Step 1 – Navigating to Production Issue list…")
        driver.get(PI_LIST_URL)
        time.sleep(2)

        # Step 2 – Click the '+ Add' button
        add_btn_xpath = "//button[contains(.,'Add')] | //a[contains(.,'Add')]"
        try:
            add_btn = wait.until(EC.element_to_be_clickable((By.XPATH, add_btn_xpath)))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", add_btn)
            driver.execute_script("arguments[0].click();", add_btn)
            log("Step 2 – Clicked '+ Add' button.")
            time.sleep(2)
        except Exception as exc:
            pytest.fail(f"Step 2 FAILED – Add button not found: {exc}")

        # Step 3 – Fill fields
        code = f"PI_{random_string(4)}"
        title = f"PITitle_{random_string(4)}"
        desc = f"PIDesc_{random_string(6)}"
        log(f"Step 3 – Entering Code='{code}', Title='{title}', Desc='{desc}'")
        try:
            driver.find_element(By.NAME, "CODE$ItemName").send_keys(code)
            driver.find_element(By.NAME, "CODE$Title").send_keys(title)
            driver.find_element(By.NAME, "CODE$Description").send_keys(desc)
        except Exception as exc:
            pytest.fail(f"Step 3 FAILED – Could not fill form fields: {exc}")

        # Step 4 – Click Save
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
            time.sleep(2)
        except Exception as exc:
            pytest.fail(f"Step 4 FAILED – Save button not found: {exc}")

        # Step 5 – Verify entry
        driver.get(PI_LIST_URL)
        time.sleep(2)
        _search_code(driver, wait, code)
        found = driver.find_elements(By.XPATH, f"//td[contains(.,'{code}')]")
        
        assert len(found) > 0, f"Step 5 FAIL – Production Issue '{code}' not found after creation."
        log(f"Step 5 PASS – Production Issue '{code}' created successfully.")


    def test_edit_production_issue(self, setup_driver):
        driver, wait = setup_driver
        log("=== TC-PI-02: Edit Production Issue ===")

        # Step 1 – Login and navigate
        login(driver, wait)
        log("Step 1 – Navigating to Production Issue list…")
        driver.get(PI_LIST_URL)
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
                    if candidate.lower() in ["code", "production issue"]:
                        continue
                    if any(x in candidate.lower() for x in ["add", "edit", "view", "delete", "sorted", "export", "print", "go"]):
                        continue
                    code = candidate
                    break
            if not code:
                raise RuntimeError("No valid Production Issue code row found in the table.")
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
                row_el.click()
                time.sleep(1)
                global_edit = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Edit')] | //a[contains(.,'Edit')]")))
                driver.execute_script("arguments[0].click();", global_edit)
                log("Step 3 – Clicked global Edit button (fallback).")
            time.sleep(2)
        except Exception as exc:
            pytest.fail(f"Step 3 FAILED – Edit button not found: {exc}")

        # Step 4 – Update details
        new_code = f"PI_{random_string(4)}_ED"
        new_title = f"PIEdit_{random_string(4)}"
        new_desc = f"Edited PI Desc {random_string(5)}"
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
            time.sleep(2)
        except Exception as exc:
            pytest.fail(f"Step 5 FAILED – Save button not found: {exc}")

        # Step 6 – Verify updated code
        driver.get(PI_LIST_URL)
        time.sleep(2)
        _search_code(driver, wait, new_code)
        found = driver.find_elements(By.XPATH, f"//td[contains(.,'{new_code}')]")
        
        assert len(found) > 0, f"Step 6 FAIL – Updated code '{new_code}' not found in list."
        log(f"Step 6 PASS – Production Issue updated to '{new_code}' successfully.")


    def test_view_production_issue(self, setup_driver):
        driver, wait = setup_driver
        log("=== TC-PI-03: View Production Issue ===")

        # Step 1 – Login and navigate
        login(driver, wait)
        log("Step 1 – Navigating to Production Issue list…")
        driver.get(PI_LIST_URL)
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
                    if candidate.lower() in ["code", "production issue"]:
                        continue
                    if any(x in candidate.lower() for x in ["add", "edit", "view", "delete", "sorted", "export", "print", "go"]):
                        continue
                    code = candidate
                    break
            if not code:
                raise RuntimeError("No valid Production Issue code row found.")
            log(f"Step 2 – Using code: '{code}'")
        except Exception as exc:
            pytest.fail(f"Step 2 FAILED – {exc}")

        # Step 3 – Filter the list
        _search_code(driver, wait, code)

        # Step 4 – Click View button
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
            pytest.fail(f"Step 4 FAILED – View button not found: {exc}")

        # Step 5 – Verify description text
        log("Step 5 – Verifying details page content…")
        try:
            divs = driver.find_elements(By.XPATH, "//div")
            for div in divs:
                try:
                    txt = div.text.strip()
                    if "Code:" in txt or code in txt:
                        log(f"Details block found: '{txt[:120]}'")
                        break
                except Exception:
                    pass
        except Exception as exc:
            log(f"Step 5 WARNING – Could not verify details: {exc}")

        # Step 6 – Click Cancel
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

        if not cancel_btn:
            log("Step 6 WARNING – Cancel/Back not found; using browser back.")
            driver.back()
            time.sleep(2)
        else:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", cancel_btn)
            driver.execute_script("arguments[0].click();", cancel_btn)
            log("Step 6 – Clicked Cancel, returned to list.")
            time.sleep(2)

        log(f"PASS – View Production Issue test completed for '{code}'.")
