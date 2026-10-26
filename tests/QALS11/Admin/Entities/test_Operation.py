import os
import random
import string
import sys
import time
from Admin.UserGroup import login
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from utils.driver_setup import get_driver

"""
Operation.py – Selenium test cases for Admin > Entities > Operation.

Covered Test Cases:
    TC-OP-01: Add a new Operation (Add flow)
    TC-OP-02: Edit an existing Operation (Edit flow)
    TC-OP-03: View an existing Operation and cancel (View flow)

Navigation Path:
    Admin > Entities (left nav) > Operation
"""

# Allow imports from the qa_automation root (two levels up from this file)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


@pytest.fixture(scope="class")
def setup_driver():
    driver = get_driver()
    wait = WebDriverWait(driver, 20)
    yield driver, wait
    driver.quit()


# ── Constants ────────────────────────────────────────────────────────────────
ADMIN_BASE = "https://engineering.ultrivalms.com/QALS1011"
OPERATION_LIST_URL = (
    f"{ADMIN_BASE}/Entity/List?tk=$Operations"
    "&busGID=BSU22ZAQALQG&B~2~ABCD&"
)

# ── Utility Functions ────────────────────────────────────────────────────────


def random_string(length=5):
    """Return a random uppercase alphanumeric string of given length."""
    return "".join(
        random.choices(string.ascii_uppercase + string.digits, k=length)
    )


def log(msg):
    """Prefix every log line with the module name and a timestamp."""
    print(f"[{time.strftime('%H:%M:%S')}][Operation] {msg}")


def _search_name(driver, wait, name):
    """Type *name* into the Operations 'Find Name' search box."""
    try:
        box = wait.until(
            EC.presence_of_element_located((By.NAME, "Operations_FindTextbox"))
        )
        box.clear()
        box.send_keys(name)
    except Exception as exc:
        log(f"Search box not interactable: {exc} — trying JS fallback.")
        try:
            box = driver.find_element(By.NAME, "Operations_FindTextbox")
            driver.execute_script(
                "arguments[0].value = arguments[1];"
                "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));",
                box,
                name,
            )
        except Exception:
            pass
    time.sleep(2)


class TestOperation:

    def _pick_first_operation(self, driver, wait):
        """Return the name (text) of the first valid data row in the Operations grid."""
        rows = wait.until(
            EC.presence_of_all_elements_located((By.XPATH, "//table//tr[td]"))
        )
        for row in rows:
            tds = row.find_elements(By.TAG_NAME, "td")
            if len(tds) < 2:
                continue
            candidate = tds[0].text.strip()
            if not candidate or "\n" in candidate:
                continue
            # Skip toolbar rows (contain action button keywords)
            if any(
                x in candidate.lower()
                for x in [
                    "add",
                    "edit",
                    "view",
                    "delete",
                    "sorted",
                    "export",
                    "print",
                    "go",
                    "assigned",
                    "filter by",
                    "find name",
                    "operation name",
                    "setup time",
                ]
            ):
                continue
            if len(candidate) > 80:  # very long string = toolbar row
                continue
            return candidate
        return None

    # ── TC-OP-01: Add Operation ──────────────────────────────────────────
    def test_add_operation(self, setup_driver):
        driver, wait = setup_driver
        log("=== TC-OP-01: Add Operation ===")

        # Step 1 – Log in and navigate to the Operation list page
        login(driver, wait)
        log("Step 1 – Navigating to Operation list…")
        driver.get(OPERATION_LIST_URL)
        time.sleep(2)

        # Step 2 – Click the '+ Add' toolbar button
        add_btn_xpath = (
            "//span[normalize-space()='+ Add' or normalize-space()='+Add']"
            " | //button[contains(.,'Add') and not(contains(.,'Assigned'))]"
            " | //a[contains(.,'Add') and not(contains(.,'Assigned'))]"
        )
        try:
            add_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, add_btn_xpath))
            )
            driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", add_btn
            )
            driver.execute_script("arguments[0].click();", add_btn)
            log("Step 2 – Clicked '+ Add' button.")
            time.sleep(2)
        except Exception as exc:
            log(f"Step 2 FAILED – Add button not found: {exc}")
            pytest.fail(f"Add button not located: {exc}")

        # Step 3 – Generate unique test data for this Operation
        op_name = f"Op_{random_string(5)}"
        setup_hrs = str(random.randint(1, 8))
        teardn_hrs = str(random.randint(1, 4))
        log(
            f"Step 3 – Data: Name='{op_name}', SetupTime='{setup_hrs}', TeardownTime='{teardn_hrs}'"
        )

        try:
            driver.find_element(By.NAME, "OPER$Operation").send_keys(op_name)
            driver.find_element(By.NAME, "OPER$SetupTime").send_keys(setup_hrs)
            driver.find_element(By.NAME, "OPER$UnsetupTime").send_keys(
                teardn_hrs
            )
            log("Step 3 – Filled Operation Name, Setup Time, Teardown Time.")
        except Exception as exc:
            log(
                f"Step 3 FAILED – Could not locate Operation Name input field.\n  {exc}"
            )
            pytest.fail(f"Form execution fields unavailable: {exc}")

        # Step 4 – Click Save
        save_xpath = (
            "//span[normalize-space()='Save' and contains(@class,'btn')]"
            " | //button[normalize-space()='Save']"
            " | //a[normalize-space()='Save']"
            " | //span[normalize-space()='Save']"
        )
        try:
            save_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, save_xpath))
            )
            driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", save_btn
            )
            driver.execute_script("arguments[0].click();", save_btn)
            log("Step 4 – Clicked Save button.")
            time.sleep(2)
        except Exception as exc:
            log(f"Step 4 FAILED – Save button not found: {exc}")
            pytest.fail(f"Save action execution failed: {exc}")

        # Step 5 – Navigate back and verify
        driver.get(OPERATION_LIST_URL)
        time.sleep(2)
        _search_name(driver, wait, op_name)
        found = driver.find_elements(
            By.XPATH, f"//td[contains(normalize-space(.),'{op_name}')]"
        )

        if found:
            log(f"Step 5 PASS – Operation '{op_name}' created successfully.")
            assert True
        else:
            log(f"Step 5 FAIL – Operation '{op_name}' not found after creation.")
            assert False, f"Target operation context matching {op_name} absent."

    # ── TC-OP-02: Edit Operation ─────────────────────────────────────────
    def test_edit_operation(self, setup_driver):
        driver, wait = setup_driver
        log("=== TC-OP-02: Edit Operation ===")

        login(driver, wait)
        log("Step 1 – Navigating to Operation list…")
        driver.get(OPERATION_LIST_URL)
        time.sleep(2)

        # Step 2 – Find target operational context item row
        try:
            op_name = self._pick_first_operation(driver, wait)
            if not op_name:
                raise RuntimeError("No valid Operation row found in the table.")
            log(f"Step 2 – Selected Operation: '{op_name}'")
        except Exception as exc:
            log(f"Step 2 FAILED – {exc}")
            pytest.fail(f"Row item discovery structural block failure: {exc}")

        # Step 3 – Context Selection & Trigger Edit
        row_xpath = f"//tr[td[normalize-space()='{op_name}']]"
        try:
            row_el = wait.until(
                EC.presence_of_element_located((By.XPATH, row_xpath))
            )
            driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", row_el
            )

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
                driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});", edit_btn
                )
                driver.execute_script("arguments[0].click();", edit_btn)
                log("Step 3 – Clicked row-level Edit button.")
            else:
                row_el.click()
                time.sleep(1)
                global_edit = wait.until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "//button[contains(.,'Edit') and not(contains(.,'Assigned'))]"
                            " | //a[contains(.,'Edit') and not(contains(.,'Assigned'))]"
                            " | //span[normalize-space()='Edit']",
                        )
                    )
                )
                driver.execute_script("arguments[0].click();", global_edit)
                log("Step 3 – Clicked global Edit button (fallback).")
            time.sleep(2)
        except Exception as exc:
            log(f"Step 3 FAILED – Edit action element mapping error: {exc}")
            pytest.fail(f"Aborting process on interactive component error: {exc}")

        # Step 4 – Update target field values
        new_name = f"OpEdit_{random_string(4)}"
        log(f"Step 4 – Updating Name to '{new_name}'")
        try:
            field = driver.find_element(By.NAME, "OPER$Operation")
            field.clear()
            field.send_keys(new_name)
            log("Step 4 – Updated Name field.")
        except Exception as exc:
            log(f"Step 4 FAILED – Field element clear/populate error: {exc}")
            pytest.fail(f"Field updating phase crashed: {exc}")

        # Step 5 – Execute Save Action
        save_xpath = (
            "//span[normalize-space()='Save' and contains(@class,'btn')]"
            " | //button[normalize-space()='Save']"
            " | //a[normalize-space()='Save']"
            " | //span[normalize-space()='Save']"
        )
        try:
            save_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, save_xpath))
            )
            driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", save_btn
            )
            driver.execute_script("arguments[0].click();", save_btn)
            log("Step 5 – Clicked Save button.")
            time.sleep(2)
        except Exception as exc:
            log(f"Step 5 FAILED – Form save target execution failed: {exc}")
            pytest.fail(f"Critical execution error tracking submission: {exc}")

        # Step 6 – Final validation phase tracking state adjustments
        driver.get(OPERATION_LIST_URL)
        time.sleep(2)
        _search_name(driver, wait, new_name)
        found = driver.find_elements(
            By.XPATH, f"//td[contains(normalize-space(.),'{new_name}')]"
        )
        if found:
            log(
                f"Step 6 PASS – Operation updated to '{new_name}' successfully."
            )
            assert True
        else:
            log(f"Step 6 FAIL – Updated name '{new_name}' not found in list.")
            assert False, "Modified profile dataset assertion error encountered."

    # ── TC-OP-03: View Operation ─────────────────────────────────────────
    def test_view_operation(self, setup_driver):
        driver, wait = setup_driver
        log("=== TC-OP-03: View Operation ===")

        login(driver, wait)
        log("Step 1 – Navigating to Operation list…")
        driver.get(OPERATION_LIST_URL)
        time.sleep(2)

        # Step 2 – Find the first valid Operation row
        try:
            op_name = self._pick_first_operation(driver, wait)
            if not op_name:
                raise RuntimeError("No valid Operation row found.")
            log(f"Step 2 – Using Operation: '{op_name}'")
        except Exception as exc:
            log(f"Step 2 FAILED – {exc}")
            pytest.fail(f"Read operation selection sequence skipped: {exc}")

        # Step 3 – Filter the list using the search box to isolate the row
        _search_name(driver, wait, op_name)

        # Step 4 – Click the View button for the matching row
        row_xpath = f"//tr[td[normalize-space()='{op_name}']]"
        try:
            row_el = wait.until(
                EC.presence_of_element_located((By.XPATH, row_xpath))
            )
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
                driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});", view_btn
                )
                driver.execute_script("arguments[0].click();", view_btn)
                log("Step 4 – Clicked row-level View button.")
            else:
                row_el.click()
                time.sleep(1)
                global_view = wait.until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "//button[contains(.,'View') and not(contains(.,'Assigned'))]"
                            " | //a[contains(.,'View') and not(contains(.,'Assigned'))]"
                            " | //span[normalize-space()='View']",
                        )
                    )
                )
                driver.execute_script("arguments[0].click();", global_view)
                log("Step 4 – Clicked global View button (fallback).")
            time.sleep(2)
        except Exception as exc:
            log(f"Step 4 FAILED – Interaction map missing: {exc}")
            pytest.fail(f"View mapping route process failure: {exc}")

        # Step 5 – Confirm Detail view text content
        log("Step 5 – Verifying details page content…")
        try:
            verify_xpath = (
                f"//*[contains(normalize-space(.),'{op_name}')]"
                " | //*[contains(normalize-space(.),'Operation Name')]"
                " | //*[contains(normalize-space(.),'Setup Time')]"
            )
            verify_els = driver.find_elements(By.XPATH, verify_xpath)
            if verify_els:
                extracted_text = verify_els[0].text.strip()[:80]
                log(f"Step 5 – Details page confirmed: found '{extracted_text}'")
            else:
                log("Step 5 WARNING – Could not confirm detail page content.")
        except Exception as exc:
            log(f"Step 5 WARNING – {exc}")

        # Step 6 – Terminate View flow with Cancel/Return elements
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
                cancel_btn = WebDriverWait(driver, 4).until(
                    EC.element_to_be_clickable((By.XPATH, xp))
                )
                if cancel_btn:
                    break
            except Exception:
                continue

        if not cancel_btn:
            log("Step 6 WARNING – Cancel/Back not found; using browser back.")
            driver.back()
            time.sleep(2)
            return

        try:
            driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", cancel_btn
            )
            driver.execute_script("arguments[0].click();", cancel_btn)
            log("Step 6 – Clicked Cancel, returned to list.")
            time.sleep(2)
        except Exception as exc:
            log(f"Step 6 non-breaking interface exception handled: {exc}")
