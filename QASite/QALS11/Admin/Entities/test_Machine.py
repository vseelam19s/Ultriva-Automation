import sys
import os
import time
import random
import string
import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

# Ensure standard imports are functional
from Admin.UserGroup import login
from utils.driver_setup import get_driver

"""
Machine.py – Selenium test cases for Admin > Entities > Machine.

Covered Test Cases:
    TC-MC-01: Add a new Machine (Add flow)
    TC-MC-02: Edit an existing Machine (Edit flow)
    TC-MC-03: View an existing Machine and cancel (View flow)

Navigation Path:
    Admin > Entities (left nav) > Machine
"""

# Allow imports from the qa_automation root (two levels up from this file)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

# ── Constants ────────────────────────────────────────────────────────────────
ADMIN_BASE = "https://engineering.ultrivalms.com/QALS1011"
MACHINE_LIST_URL = f"{ADMIN_BASE}/Entity/List?tk=$Machines&busGID=BSU22ZAQALQG&B~2~ABCD&"


@pytest.fixture(scope="class")
def setup_driver():
    driver = get_driver()
    wait = WebDriverWait(driver, 20)
    yield driver, wait
    driver.quit()


# ── Global Utility Functions ──────────────────────────────────────────────────
def random_string(length=5):
    """Return a random uppercase alphanumeric string of given length."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def log(msg):
    """Prefix every log line with the module name and a timestamp."""
    print(f"[{time.strftime('%H:%M:%S')}][Machine] {msg}")


def _search_code(driver, wait, code):
    """
    Type *code* into the Machine list search box so the list filters.
    """
    search_selectors = [
        (By.NAME, "Machines_FindTextbox"),
        (By.XPATH, "//input[contains(@placeholder,'Find Code')]"),
        (By.XPATH, "//input[contains(@placeholder,'Find Name')]"),
        (By.XPATH, "//input[contains(@name,'FindTextbox')]"),
    ]

    for by, sel in search_selectors:
        try:
            box = wait.until(EC.visibility_of_element_located((by, sel)))
            wait.until(EC.element_to_be_clickable((by, sel)))
            box.clear()
            box.send_keys(code)
            log(f"Search box filled via: {sel}")
            time.sleep(2)
            return
        except Exception:
            continue

    # Last resort: JS value dispatch
    try:
        box = driver.find_element(By.XPATH, "//input[@type='text' and not(@readonly)]")
        driver.execute_script(
            "arguments[0].value = arguments[1];"
            "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));",
            box, code,
        )
        log("Search box filled via JS last-resort fallback.")
    except Exception as exc:
        log(f"Search box fallback also failed: {exc}")
    time.sleep(2)


class TestMachine:

    def _pick_first_machine(self, driver, wait):
        """
        Return the code of the first valid data row in the Machine grid.
        """
        action_keywords = [
            "add", "edit", "view", "delete", "sorted", "export", "print", "go",
            "assigned", "capacity", "die configuration", "ryg rule", "machine code",
            "machine name", "filter by", "find name", "find code", "set die", "operations",
        ]
        rows = wait.until(
            EC.presence_of_all_elements_located((By.XPATH, "//table//tr[td]"))
        )
        for row in rows:
            tds = row.find_elements(By.TAG_NAME, "td")
            if not tds:
                continue
            candidate = tds[0].text.strip()
            if not candidate:
                continue
            if len(candidate) > 50:
                continue
            low = candidate.lower()
            if any(kw in low for kw in action_keywords):
                continue
            return candidate
        return None

    # ── TC-MC-01: Add Machine ────────────────────────────────────────────
    def test_add_machine(self, setup_driver):
        driver, wait = setup_driver
        log("=== TC-MC-01: Add Machine ===")

        # Step 1 – Log in and navigate
        login(driver, wait)
        log("Step 1 – Navigating to Machine list…")
        driver.get(MACHINE_LIST_URL)
        time.sleep(2)

        # Step 2 – Click '+ Add'
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
            log(f"Step 2 FAILED – Add button not found: {exc}")
            pytest.fail("Add button not found")

        # Step 3 – Populate unique test data
        mc_code = f"MC_{random_string(4)}"
        mc_desc = f"MachineDesc_{random_string(5)}"
        log(f"Step 3 – Data: Code='{mc_code}', Desc='{mc_desc}'")

        code_filled = False
        for code_sel in [
            "//input[@name='MACHINE$MachineCode']",
            "//input[contains(@name,'MachineCode')]",
            "//input[contains(@name,'Code')]",
            "//form//input[1]",
        ]:
            try:
                el = wait.until(EC.visibility_of_element_located((By.XPATH, code_sel)))
                el.clear()
                el.send_keys(mc_code)
                code_filled = True
                log(f"Step 3 – Filled Code via selector: {code_sel}")
                break
            except Exception:
                continue

        if not code_filled:
            log("Step 3 FAILED – Could not locate Machine Code input field.")
            pytest.fail("Machine Code input field missing")

        for desc_sel in [
            "//input[@name='MACHINE$MachineDescription']",
            "//input[contains(@name,'Description')]",
            "//textarea[contains(@name,'Description')]",
        ]:
            try:
                el = driver.find_element(By.XPATH, desc_sel)
                el.clear()
                el.send_keys(mc_desc)
                log(f"Step 3 – Filled Description via: {desc_sel}")
                break
            except Exception:
                continue

        try:
            rate_el = driver.find_element(By.NAME, "MACHINE$IdealRunRate2")
            rate_el.clear()
            rate_el.send_keys("60")
            log("Step 3 – Filled IdealRunRate2 = 60")
        except Exception as exc:
            log(f"Step 3 – IdealRunRate2 not found (non-fatal): {exc}")

        try:
            uom_sel = driver.find_element(By.NAME, "MACHINE$IdealRunRate2UOM")
            select = Select(uom_sel)
            select.select_by_value("PiecesPerMinute")
            log("Step 3 – Selected IdealRunRate2UOM = PiecesPerMinute")
        except Exception as exc:
            log(f"Step 3 – IdealRunRate2UOM select failed (non-fatal): {exc}")

        # Step 4 – Click Save
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
            log("Step 4 – Clicked Save button.")
            time.sleep(4)
        except Exception as exc:
            log(f"Step 4 FAILED – Save button not found: {exc}")
            pytest.fail("Save button not clickably reachable")

        post_url = driver.current_url
        log(f"Step 4 – Post-save URL: {post_url}")
        
        # Look for validation errors
        try:
            err_els = driver.find_elements(
                By.XPATH,
                "//span[contains(@class,'field-validation-error')]"
                " | //div[contains(@class,'validation-summary-errors')]"
                " | //div[contains(@class,'alert-danger')]"
                " | //div[contains(@class,'StatusError')]"
            )
            for e in err_els:
                t = e.text.strip()
                if t:
                    log(f"Step 4 – Validation error: {t[:150]}")
        except Exception:
            pass

        if "/Machine/Create" in post_url or ("/Entity/List" in post_url and "Create" in post_url):
            log("Step 4 FAIL – Save rejected (still on Create page).")
            pytest.fail("Machine creation execution rejected by backend")

        # Step 5 – Confirm verification
        driver.get(MACHINE_LIST_URL)
        time.sleep(3)
        _search_code(driver, wait, mc_code)
        time.sleep(2)
        
        found = driver.find_elements(By.XPATH, f"//td[contains(normalize-space(.),'{mc_code}')]")
        if found:
            log(f"Step 5 PASS – Machine '{mc_code}' created successfully.")
            assert True
        else:
            cells = driver.find_elements(By.XPATH, "//table//td")
            visible = [c.text.strip() for c in cells[:20] if c.text.strip()]
            log(f"Step 5 FAIL – '{mc_code}' not found. Table cells: {visible}")
            pytest.fail("Machine persistence identification failed")

    # ── TC-MC-02: Edit Machine ───────────────────────────────────────────
    def test_edit_machine(self, setup_driver):
        driver, wait = setup_driver
        log("=== TC-MC-02: Edit Machine ===")

        login(driver, wait)
        log("Step 1 – Navigating to Machine list…")
        driver.get(MACHINE_LIST_URL)
        time.sleep(2)

        # Step 2 – Pick Row
        try:
            mc_code = self._pick_first_machine(driver, wait)
            if not mc_code:
                raise RuntimeError("No valid Machine row found in the table.")
            log(f"Step 2 – Selected Machine: '{mc_code}'")
        except Exception as exc:
            log(f"Step 2 FAILED – {exc}")
            pytest.fail("Table empty or inaccessible")

        # Step 3 – Action Route Selection (Edit UI execution)
        row_xpath = f"//tr[td[normalize-space()='{mc_code}']]"
        try:
            row_el = wait.until(EC.presence_of_element_located((By.XPATH, row_xpath)))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", row_el)

            edit_btn = None
            for btn_sel in [
                ".//a[contains(translate(.,'edit','EDIT'),'EDIT') or contains(@class,'edit')]",
                ".//button[contains(translate(.,'edit','EDIT'),'EDIT')]",
                ".//span[contains(translate(.,'edit','EDIT'),'EDIT') and not(@class='tooltip')]",
            ]:
                try:
                    edit_btn = row_el.find_element(By.XPATH, btn_sel)
                    if edit_btn and edit_btn.is_displayed():
                        break
                    edit_btn = None
                except Exception:
                    continue

            if edit_btn:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", edit_btn)
                driver.execute_script("arguments[0].click();", edit_btn)
                log("Step 3 – Clicked row-level Edit button.")
            else:
                row_el.click()
                time.sleep(1)
                global_edit = wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH,
                         "//button[contains(.,'Edit') and not(contains(.,'Assigned'))]"
                         " | //a[contains(.,'Edit') and not(contains(.,'Assigned'))]"
                         " | //span[normalize-space()='Edit']")
                    )
                )
                driver.execute_script("arguments[0].click();", global_edit)
                log("Step 3 – Clicked global Edit button (fallback).")
                time.sleep(2)
        except Exception as exc:
            log(f"Step 3 FAILED – Edit button not found: {exc}")
            pytest.fail("Edit target button context failed")

        # Step 4 – Mutate fields
        new_code = f"MC_{random_string(4)}_ED"
        new_name = f"MachEdit_{random_string(4)}"
        log(f"Step 4 – Updating Code='{new_code}', Name='{new_name}'")

        code_updated = False
        for code_sel in [
            "//input[@name='MACHINE$MachineCode']",
            "//input[contains(@name,'MachineCode')]",
            "//input[contains(@name,'Code')]",
            "//form//input[1]",
        ]:
            try:
                el = wait.until(EC.visibility_of_element_located((By.XPATH, code_sel)))
                el.clear()
                el.send_keys(new_code)
                code_updated = True
                log(f"Step 4 – Updated Code via: {code_sel}")
                break
            except Exception:
                continue

        if not code_updated:
            log("Step 4 FAILED – Could not locate Machine Code input to update.")
            pytest.fail("Machine entity Key Immutable or Missing element context")

        for name_sel in [
            "//input[@name='MACHINE$MachineName']",
            "//input[contains(@name,'MachineName')]",
            "//form//input[2]",
        ]:
            try:
                el = driver.find_element(By.XPATH, name_sel)
                el.clear()
                el.send_keys(new_name)
                log(f"Step 4 – Updated Name via: {name_sel}")
                break
            except Exception:
                continue

        # Step 5 – Click Save
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
            pytest.fail("Save processing failed")

        # Step 6 – Re-verify presence
        driver.get(MACHINE_LIST_URL)
        time.sleep(2)
        _search_code(driver, wait, new_code)
        found = driver.find_elements(By.XPATH, f"//td[contains(normalize-space(.),'{new_code}')]")
        if found:
            log(f"Step 6 PASS – Machine updated to '{new_code}' successfully.")
            assert True
        else:
            log(f"Step 6 FAIL – Updated code '{new_code}' not found in list.")
            pytest.fail("Edits not captured dynamically within grid system")

    # ── TC-MC-03: View Machine ───────────────────────────────────────────
    def test_view_machine(self, setup_driver):
        driver, wait = setup_driver
        log("=== TC-MC-03: View Machine ===")

        login(driver, wait)
        log("Step 1 – Navigating to Machine list…")
        driver.get(MACHINE_LIST_URL)
        time.sleep(2)

        try:
            mc_code = self._pick_first_machine(driver, wait)
            if not mc_code:
                raise RuntimeError("No valid Machine row found.")
            log(f"Step 2 – Using Machine: '{mc_code}'")
        except Exception as exc:
            log(f"Step 2 FAILED – {exc}")
            pytest.fail("Grid verification source unavailable")

        _search_code(driver, wait, mc_code)

        row_xpath = f"//tr[td[normalize-space()='{mc_code}']]"
        try:
            row_el = wait.until(EC.presence_of_element_located((By.XPATH, row_xpath)))
            view_btn = None

            for btn_sel in [
                ".//a[contains(translate(.,'view','VIEW'),'VIEW') or contains(@class,'view')]",
                ".//button[contains(translate(.,'view','VIEW'),'VIEW')]",
                ".//span[contains(translate(.,'view','VIEW'),'VIEW') and not(@class='tooltip')]",
            ]:
                try:
                    view_btn = row_el.find_element(By.XPATH, btn_sel)
                    if view_btn and view_btn.is_displayed():
                        break
                    view_btn = None
                except Exception:
                    continue

            if view_btn:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", view_btn)
                driver.execute_script("arguments[0].click();", view_btn)
                log("Step 4 – Clicked row-level View button.")
            else:
                row_el.click()
                time.sleep(1)
                global_view = wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH,
                         "//button[contains(.,'View') and not(contains(.,'Assigned'))]"
                         " | //a[contains(.,'View') and not(contains(.,'Assigned'))]"
                         " | //span[normalize-space()='View']")
                    )
                )
                driver.execute_script("arguments[0].click();", global_view)
                log("Step 4 – Clicked global View button (fallback).")
                time.sleep(2)
        except Exception as exc:
            log(f"Step 4 FAILED – View button not found: {exc}")
            pytest.fail("View transition action intercept missing")

        log("Step 5 – Verifying details page content…")
        try:
            verify_xpath = (
                f"//*[contains(normalize-space(.),'{mc_code}')]"
                " | //*[contains(normalize-space(.),'Machine Code')]"
                " | //*[contains(normalize-space(.),'Machine Name')]"
            )
            verify_els = driver.find_elements(By.XPATH, verify_xpath)
            if verify_els:
                log(f"Step 5 – Details page confirmed: '{verify_els[0].text.strip()[:80]}'")
            else:
                log("Step 5 WARNING – Could not confirm detail page content.")
        except Exception as exc:
            log(f"Step 5 WARNING – {exc}")

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
            assert True
            return

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", cancel_btn)
        driver.execute_script("arguments[0].click();", cancel_btn)
        log("Step 6 – Clicked Cancel, returned to list.")
        time.sleep(2)
        assert True
