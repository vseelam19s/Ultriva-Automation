import sys
import os
import time
import random
import string
import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from utils.driver_setup import get_driver
from Admin.UserGroup import login

"""
Container.py – Selenium test cases for Admin > Entities > Container.

Covered Test Cases:
    TC-CON-01: Add a new Container (Add flow)
    TC-CON-02: Edit an existing Container (Edit flow)
    TC-CON-03: View an existing Container and cancel (View flow)

Navigation Path:
    Admin > Entities (left nav) > Container
"""

# Allow imports from the qa_automation root (two levels up from this file)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

@pytest.fixture(scope="class")
def setup_driver():
    driver = get_driver()
    wait = WebDriverWait(driver, 20)
    yield driver, wait
    driver.quit()

# ── Constants ───────────────────────────────────────────────────────────
ADMIN_BASE = "https://engineering.ultrivalms.com/QALS1011"
CONTAINER_LIST_URL = f"{ADMIN_BASE}/Entity/List?tk=$Container&busGID=BSU22ZAQALQG&A~1~ABC&"
CONTAINER_TYPES = ["FS2", "FX4", "test23", "TT1", "TT2"]
VOLUME_UOMS = ["CBM - cubic meters", "CBF - cubic feet"]

# ── Utility functions ───────────────────────────────────────────────────
def random_string(length=5):
    """Return a random uppercase alphanumeric string of the given length."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))

def log(msg):
    """Prefix every log line with module name and a timestamp."""
    print(f"[{time.strftime('%H:%M:%S')}][Container] {msg}")

def _search_name(driver, wait, name):
    """Type name into the Container list 'Find Name' search box."""
    search_selectors = [
        (By.NAME, "Container_FindTextbox"),
        (By.XPATH, "//input[contains(@placeholder,'Find Name')]"),
        (By.XPATH, "//input[contains(@name,'FindTextbox')]"),
    ]
    for by, sel in search_selectors:
        try:
            box = wait.until(EC.visibility_of_element_located((by, sel)))
            wait.until(EC.element_to_be_clickable((by, sel)))
            box.clear()
            box.send_keys(name)
            log(f"Search box filled via: {sel}")
            time.sleep(2)
            return
        except Exception:
            continue

    # Fallback
    try:
        box = driver.find_element(By.NAME, "Container_FindTextbox")
        driver.execute_script(
            "arguments[0].value = arguments[1];"
            "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));",
            box, name,
        )
        log("Search box filled via JS fallback.")
    except Exception as exc:
        log(f"Search box fallback also failed: {exc}")
    time.sleep(2)


class TestContainer:

    def _pick_first_container(self, driver, wait):
        """Return the Name of the first valid data row in the Container grid."""
        action_keywords = [
            "add", "edit", "view", "delete", "sorted", "export", "print",
            "go", "find", "filter", "container name", "container type",
            "total volume", "max allowed",
        ]
        rows = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//table//tr[td]")))
        for row in rows:
            tds = row.find_elements(By.TAG_NAME, "td")
            if not tds:
                continue
            candidate = tds[0].text.strip()
            if not candidate or len(candidate) > 60:
                continue
            low = candidate.lower()
            if any(kw in low for kw in action_keywords):
                continue
            return candidate
        return None

    def _select_option(self, driver, wait, field_name, value):
        """Select value by visible text in the <select> element."""
        from selenium.webdriver.support.ui import Select as SeleniumSelect
        try:
            sel_el = wait.until(EC.presence_of_element_located((By.NAME, field_name)))
            sel = SeleniumSelect(sel_el)
            sel.select_by_visible_text(value)
            log(f"Selected '{value}' in '{field_name}'.")
        except Exception as exc:
            log(f"Could not select '{value}' in '{field_name}': {exc}")
            raise

    # ── TC-CON-01: Add Container ─────────────────────────────────────────
    def test_add_container(self, setup_driver):
        driver, wait = setup_driver
        log("=== TC-CON-01: Add Container ===")

        # Step 1 – Log in and navigate to Container list
        login(driver, wait)
        log("Step 1 – Navigating to Container list…")
        driver.get(CONTAINER_LIST_URL)
        time.sleep(2)

        # Step 2 – Click the '+ Add' toolbar button
        add_btn_xpath = (
            "//span[normalize-space()='+ Add' or normalize-space()='+Add']"
            " | //button[contains(.,'Add') and not(contains(.,'Assigned'))]"
            " | //a[contains(.,'Add') and not(contains(.,'Assigned'))]"
        )
        try:
            add_btn = wait.until(EC.element_to_be_clickable((By.XPATH, add_btn_xpath)))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", add_btn)
            driver.execute_script("arguments[0].click();", add_btn)
            log("Step 2 – Clicked '+ Add' button.")
            time.sleep(2)
        except Exception as exc:
            pytest.fail(f"Step 2 FAILED – Add button not found: {exc}")

        # Step 3 – Generate unique test data and fill the form
        con_name = f"CON_{random_string(4)}"
        con_type = CONTAINER_TYPES[0]
        total_vol = str(random.randint(10, 500))
        max_vol = str(random.randint(1, int(total_vol)))
        vol_uom = VOLUME_UOMS[0]
        log(f"Step 3 – Data: Name='{con_name}', Type='{con_type}', TotalVol='{total_vol}', MaxVol='{max_vol}', UOM='{vol_uom}'")

        try:
            name_field = wait.until(EC.visibility_of_element_located((By.NAME, "CODE$ItemName")))
            name_field.clear()
            name_field.send_keys(con_name)
            log("Step 3 – Filled Container Name.")
        except Exception as exc:
            pytest.fail(f"Step 3 FAILED – Could not fill Name field: {exc}")

        try:
            self._select_option(driver, wait, "CODE$Description", con_type)
            log(f"Step 3 – Selected Container Type: '{con_type}'.")
        except Exception as exc:
            log(f"Step 3 WARNING – Container Type select failed: {exc}")

        try:
            vol_field = driver.find_element(By.NAME, "CODE$DblParam1")
            vol_field.clear()
            vol_field.send_keys(total_vol)
            log(f"Step 3 – Filled Total Volume: '{total_vol}'.")
        except Exception as exc:
            log(f"Step 3 WARNING – Total Volume field not found: {exc}")

        try:
            max_field = driver.find_element(By.NAME, "CODE$DblParam2")
            max_field.clear()
            max_field.send_keys(max_vol)
            log(f"Step 3 – Filled Max Allowed Volume: '{max_vol}'.")
        except Exception as exc:
            log(f"Step 3 WARNING – Max Allowed Volume field not found: {exc}")

        try:
            self._select_option(driver, wait, "CODE$STRPARAM2", vol_uom)
            log(f"Step 3 – Selected Volume UOM: '{vol_uom}'.")
        except Exception as exc:
            log(f"Step 3 WARNING – Volume UOM select failed: {exc}")

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

        # Step 5 – Navigate back to list and verify
        driver.get(CONTAINER_LIST_URL)
        time.sleep(2)
        _search_name(driver, wait, con_name)

        found = driver.find_elements(By.XPATH, f"//td[contains(.,'{con_name}')]")
        assert found, f"Step 5 FAIL – Container '{con_name}' not found after creation."
        log(f"Step 5 PASS – Container '{con_name}' created successfully.")

    # ── TC-CON-02: Edit Container ────────────────────────────────────────
    def test_edit_container(self, setup_driver):
        driver, wait = setup_driver
        log("=== TC-CON-02: Edit Container ===")

        login(driver, wait)
        log("Step 1 – Navigating to Container list…")
        driver.get(CONTAINER_LIST_URL)
        time.sleep(2)

        name = self._pick_first_container(driver, wait)
        if not name:
            pytest.fail("Step 2 FAILED – No valid Container row found in the table.")
        log(f"Step 2 – Selected container Name: '{name}'")

        row_xpath = f"//tr[td[normalize-space()='{name}']]"
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

        new_name = f"CON_{random_string(4)}_ED"
        new_type = CONTAINER_TYPES[1]
        new_vol = str(random.randint(10, 500))
        new_max = str(random.randint(1, int(new_vol)))
        new_uom = VOLUME_UOMS[1]
        log(f"Step 4 – Updating to Name='{new_name}', Type='{new_type}', TotalVol='{new_vol}', MaxVol='{new_max}', UOM='{new_uom}'")

        try:
            name_field = wait.until(EC.visibility_of_element_located((By.NAME, "CODE$ItemName")))
            name_field.clear()
            name_field.send_keys(new_name)
            log("Step 4 – Updated Container Name.")
        except Exception as exc:
            pytest.fail(f"Step 4 FAILED – Could not update Name field: {exc}")

        try:
            self._select_option(driver, wait, "CODE$Description", new_type)
        except Exception as exc:
            log(f"Step 4 WARNING – Container Type update failed: {exc}")

        try:
            vol_field = driver.find_element(By.NAME, "CODE$DblParam1")
            vol_field.clear()
            vol_field.send_keys(new_vol)
        except Exception as exc:
            log(f"Step 4 WARNING – Total Volume update failed: {exc}")

        try:
            max_field = driver.find_element(By.NAME, "CODE$DblParam2")
            max_field.clear()
            max_field.send_keys(new_max)
        except Exception as exc:
            log(f"Step 4 WARNING – Max Allowed Volume update failed: {exc}")

        try:
            self._select_option(driver, wait, "CODE$STRPARAM2", new_uom)
        except Exception as exc:
            log(f"Step 4 WARNING – Volume UOM update failed: {exc}")

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

        driver.get(CONTAINER_LIST_URL)
        time.sleep(2)
        _search_name(driver, wait, new_name)

        found = driver.find_elements(By.XPATH, f"//td[contains(.,'{new_name}')]")
        assert found, f"Step 6 FAIL – Updated container '{new_name}' not found in list."
        log(f"Step 6 PASS – Container updated to '{new_name}' successfully.")

    # ── TC-CON-03: View Container ────────────────────────────────────────
    def test_view_container(self, setup_driver):
        driver, wait = setup_driver
        log("=== TC-CON-03: View Container ===")

        login(driver, wait)
        log("Step 1 – Navigating to Container list…")
        driver.get(CONTAINER_LIST_URL)
        time.sleep(2)

        name = self._pick_first_container(driver, wait)
        if not name:
            pytest.fail("Step 2 FAILED – No valid Container row found in the table.")
        log(f"Step 2 – Using container Name: '{name}'")

        _search_name(driver, wait, name)

        row_xpath = f"//tr[td[normalize-space()='{name}']]"
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

        log("Step 5 – Verifying details page content…")
        try:
            body_text = driver.find_element(By.TAG_NAME, "body").text
            if name in body_text:
                log(f"Step 5 PASS – Container name '{name}' found on details page.")
            else:
                log(f"Step 5 WARNING – Name '{name}' not explicitly visible; continuing to Cancel step.")
        except Exception as exc:
            log(f"Step 5 WARNING – Could not read body text: {exc}")

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
                break
            except Exception:
                continue

        if not cancel_btn:
            log("Step 6 WARNING – Cancel button not found; using browser back.")
            driver.back()
            time.sleep(2)
            return

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", cancel_btn)
        driver.execute_script("arguments[0].click();", cancel_btn)
        log("Step 6 – Clicked Cancel; returned to list.")
        time.sleep(2)
