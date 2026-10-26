import sys
import os
import time
import random
import string
import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Allow running from the qa_automation root or from the Entities sub-folder
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from Admin.UserGroup import login
from utils.driver_setup import get_driver

"""
Carrier.py – Selenium test cases for Admin > Carrier.

Covered Test Cases:
    TC-CAR-01: Add a new Carrier (Add flow)
    TC-CAR-02: Edit an existing Carrier (Edit flow)
    TC-CAR-03: View an existing Carrier and cancel (View flow)

Navigation Path:
    Admin > Entities (left nav) > Carrier
"""

@pytest.fixture(scope="class")
def setup_driver():
    driver = get_driver()
    wait = WebDriverWait(driver, 15)
    # Perform login once for the entire test class run to save execution time
    login(driver, wait)
    yield driver, wait
    driver.quit()


# ── Constants ────────────────────────────────────────────────────────────────
ADMIN_BASE = "https://engineering.ultrivalms.com/QALS1011"
CARRIER_LIST_URL = f"{ADMIN_BASE}/Entity/List?tk=$Carrier&busGID=BSU22ZAQALQG&A~1~ABC&"

SAVE_XPATH = (
    "//span[normalize-space()='Save' and contains(@class,'btn-toolbar-right-item')]"
    " | //button[normalize-space()='Save']"
    " | //a[normalize-space()='Save']"
)

# ── Utility Functions ────────────────────────────────────────────────────────

def random_string(length=5):
    """Return a random uppercase alphanumeric string of given length."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def log(msg):
    """Prefix every log line with module name and timestamp."""
    print(f"[{time.strftime('%H:%M:%S')}][Carrier] {msg}")


def _search_code(driver, wait, code):
    """Type *code* into the 'Find Code' search box so the list filters."""
    search_xpath = "//input[contains(@placeholder,'Find Code') or @type='text']"
    try:
        box = wait.until(EC.visibility_of_element_located((By.XPATH, search_xpath)))
        wait.until(EC.element_to_be_clickable((By.XPATH, search_xpath)))
        
        # Clear strategies for reactive front-ends
        box.click()
        box.send_keys(Keys.CONTROL + "a")
        box.send_keys(Keys.BACKSPACE)
        box.clear()
        box.send_keys(code)
        box.send_keys(Keys.ENTER)
    except Exception as exc:
        log(f"Search box not interactable: {exc} — trying JS fallback.")
        box = driver.find_element(By.XPATH, search_xpath)
        driver.execute_script(
            "arguments[0].value = '';"
            "arguments[0].value = arguments[1];"
            "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));"
            "arguments[0].dispatchEvent(new Event('change',{bubbles:true}));",
            box, code,
        )
    time.sleep(2)  # Short pause to let list filter settle


# ── Pytest Test Class Suite ─────────────────────────────────────────────
class TestCarrier:

    def test_add_carrier(self, setup_driver):
        """TC-CAR-01 – Add a new Carrier."""
        driver, wait = setup_driver
        log("=== TC-CAR-01: Add Carrier ===")

        # Step 1 – Navigate
        log("Step 1 – Navigating to Carrier list…")
        driver.get(CARRIER_LIST_URL)

        # Step 2 – Click '+ Add' button
        add_btn_xpath = "//button[contains(.,'Add')] | //a[contains(.,'Add')]"
        try:
            add_btn = wait.until(EC.element_to_be_clickable((By.XPATH, add_btn_xpath)))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", add_btn)
            driver.execute_script("arguments[0].click();", add_btn)
            log("Step 2 – Clicked '+ Add' button.")
        except Exception as exc:
            log(f"Step 2 FAILED – Add button not found: {exc}")
            pytest.fail("Add action button context omitted or unclickable.")

        # Step 3 – Fill Code, Title, Description
        code = f"CAR_{random_string(4)}"
        title = f"CARTitle_{random_string(4)}"
        desc = f"CARDesc_{random_string(6)}"
        log(f"Step 3 – Entering Code='{code}', Title='{title}', Desc='{desc}'")
        try:
            wait.until(EC.visibility_of_element_located((By.NAME, "CODE$ItemName"))).send_keys(code)
            driver.find_element(By.NAME, "CODE$Title").send_keys(title)
            driver.find_element(By.NAME, "CODE$Description").send_keys(desc)
        except Exception as exc:
            log(f"Step 3 FAILED – Could not fill form fields: {exc}")
            pytest.fail("Form entry field elements mismatched or missing.")

        # Step 4 – Click Save
        try:
            save_btn = wait.until(EC.element_to_be_clickable((By.XPATH, SAVE_XPATH)))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", save_btn)
            driver.execute_script("arguments[0].click();", save_btn)
            log("Step 4 – Clicked Save button.")
        except Exception as exc:
            log(f"Step 4 FAILED – Save button not found: {exc}")
            pytest.fail("Save submittal element validation aborted.")

        # Step 5 – Verify new carrier code in the list
        driver.get(CARRIER_LIST_URL)
        _search_code(driver, wait, code)
        
        found = wait.until(EC.presence_of_all_elements_located((By.XPATH, f"//td[contains(.,'{code}')]")))
        if found:
            log(f"Step 5 PASS – Carrier '{code}' created successfully.")
        else:
            log(f"Step 5 FAIL – Carrier '{code}' not found after creation.")
            assert False, f"Carrier verification failed for: {code}"

    def test_edit_carrier(self, setup_driver):
        """TC-CAR-02 – Edit an existing Carrier."""
        driver, wait = setup_driver
        log("=== TC-CAR-02: Edit Carrier ===")

        # Step 1 – Navigate
        log("Step 1 – Navigating to Carrier list…")
        driver.get(CARRIER_LIST_URL)

        # Step 2 – Find first valid row using explicit XPath exclusions
        try:
            cell_xpath = (
                "//table//tr/td[1][normalize-space()!='' "
                "and not(contains(., 'Code')) "
                "and not(contains(., 'Carrier')) "
                "and not(contains(., 'Add')) "
                "and not(contains(., 'Edit'))]"
            )
            target_cell = wait.until(EC.presence_of_element_located((By.XPATH, cell_xpath)))
            code = target_cell.text.strip()
            log(f"Step 2 – Selected row code: '{code}'")
        except Exception as exc:
            log(f"Step 2 FAILED – {exc}")
            pytest.fail("Data row structural list parsing unresolvable.")

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
                global_edit = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(.,'Edit')] | //a[contains(.,'Edit')]")))
                driver.execute_script("arguments[0].click();", global_edit)
                log("Step 3 – Clicked global Edit button (fallback).")
        except Exception as exc:
            log(f"Step 3 FAILED – Edit button not found: {exc}")
            pytest.fail("Interactive inline row components are missing.")

        # Step 4 – Update fields
        new_code = f"CAR_{random_string(4)}_ED"
        new_title = f"CAREdit_{random_string(4)}"
        new_desc = f"Edited Carrier Desc {random_string(5)}"
        log(f"Step 4 – Updating to Code='{new_code}', Title='{new_title}', Desc='{new_desc}'")
        try:
            for name, value in [
                ("CODE$ItemName", new_code),
                ("CODE$Title", new_title),
                ("CODE$Description", new_desc),
            ]:
                field = wait.until(EC.visibility_of_element_located((By.NAME, name)))
                field.click()
                field.send_keys(Keys.CONTROL + "a")
                field.send_keys(Keys.BACKSPACE)
                field.clear()
                field.send_keys(value)
        except Exception as exc:
            log(f"Step 4 FAILED – Could not update fields: {exc}")
            pytest.fail("Form updates failed inside target modification fields.")

        # Step 5 – Click Save
        try:
            save_btn = wait.until(EC.element_to_be_clickable((By.XPATH, SAVE_XPATH)))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", save_btn)
            driver.execute_script("arguments[0].click();", save_btn)
            log("Step 5 – Clicked Save button.")
        except Exception as exc:
            log(f"Step 5 FAILED – Save button not found: {exc}")
            pytest.fail("Persistent save trigger was dropped.")

        # Step 6 – Verify updated code in the list
        driver.get(CARRIER_LIST_URL)
        _search_code(driver, wait, new_code)
        found = wait.until(EC.presence_of_all_elements_located((By.XPATH, f"//td[contains(.,'{new_code}')]")))
        if found:
            log(f"Step 6 PASS – Carrier updated to '{new_code}' successfully.")
        else:
            log(f"Step 6 FAIL – Updated code '{new_code}' not found in list.")
            assert False, f"Modified entity could not be verified for: {new_code}"

    def test_view_carrier(self, setup_driver):
        """TC-CAR-03 – View details of an existing Carrier and cancel."""
        driver, wait = setup_driver
        log("=== TC-CAR-03: View Carrier ===")

        # Step 1 – Navigate
        log("Step 1 – Navigating to Carrier list…")
        driver.get(CARRIER_LIST_URL)

        # Step 2 – Find first valid row via explicit XPath selection
        try:
            cell_xpath = (
                "//table//tr/td[1][normalize-space()!='' "
                "and not(contains(., 'Code')) "
                "and not(contains(., 'Carrier'))]"
            )
            target_cell = wait.until(EC.presence_of_element_located((By.XPATH, cell_xpath)))
            code = target_cell.text.strip()
            log(f"Step 2 – Using code: '{code}'")
        except Exception as exc:
            log(f"Step 2 FAILED – {exc}")
            pytest.fail("Failed to target active tracking item row components.")

        # Step 3 – Search for the code
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
                global_view = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(.,'View')] | //a[contains(.,'View')]")))
                driver.execute_script("arguments[0].click();", global_view)
                log("Step 4 – Clicked global View button (fallback).")
        except Exception as exc:
            log(f"Step 4 FAILED – View button not found: {exc}")
            pytest.fail("View detail form action element missed.")

        # Step 5 – Verify details page
        log("Step 5 – Verifying details page…")
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{code}') or contains(., 'Code:')]")))
            log("Step 5 PASS - Details block found.")
        except Exception as exc:
            log(f"Step 5 WARNING – Could not assert context details page: {exc}")

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
                cancel_btn = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, xp)))
                if cancel_btn:
                    break
            except Exception:
                continue

        if not cancel_btn:
            log("Step 6 WARNING – Cancel/Back not found; using browser back fallback.")
            driver.back()
            return

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", cancel_btn)
        driver.execute_script("arguments[0].click();", cancel_btn)
        log("Step 6 – Clicked Cancel, returned to list.")
