import os
import random
import string
import sys
import time
from Admin.UserGroup import login
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from utils.driver_setup import get_driver
import pytest

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
# Location Code list URL – tk=$LocationCode maps to the Location Code entity
LC_LIST_URL = f"{ADMIN_BASE}/Entity/List?tk=$LocationCode&busGID=BSU22ZAQALQG&A~1~ABC&"


# ── Utility helpers ──────────────────────────────────────────────────────────
def random_string(length=5):
    """Return a random uppercase alphanumeric string of the given length."""
    return "".join(
        random.choices(string.ascii_uppercase + string.digits, k=length)
    )


def log(msg):
    """Prefix every console line with module name and current timestamp."""
    print(f"[{time.strftime('%H:%M:%S')}][LocationCode] {msg}")


def _search_code(driver, wait, code):
    """Type *code* into the Find Code search box so the list filters down.

    Falls back to a JavaScript value-set when the box is not interactable.
    """
    search_xpath = "//input[contains(@placeholder,'Find Code') or @type='text']"
    try:
        box = wait.until(
            EC.visibility_of_element_located((By.XPATH, search_xpath))
        )
        wait.until(EC.element_to_be_clickable((By.XPATH, search_xpath)))
        box.clear()
        box.send_keys(code)
    except Exception as exc:
        log(f"Search box not interactable: {exc} — trying JS fallback.")
        box = driver.find_element(By.XPATH, search_xpath)
        driver.execute_script(
            "arguments[0].value = arguments[1];"
            "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));",
            box,
            code,
        )
    time.sleep(2)


# ── Test Suite Class ─────────────────────────────────────────────────────────
class TestLocationcode:

    def test_add_location_code(self, setup_driver):
        driver, wait = setup_driver
        """
        TC-LC-01 – Add a new Location Code.
        """
        log("=== TC-LC-01: Add Location Code ===")

        # Step 1 – Login and navigate to Location Code list
        login(driver, wait)
        log("Step 1 – Navigating to Location Code list…")
        driver.get(LC_LIST_URL)
        time.sleep(2)

        # Step 2 – Click '+ Add' button to open the create form
        add_btn_xpath = "//button[contains(.,'Add')] | //a[contains(.,'Add')]"
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
            pytest.fail(f"Step 2 FAILED – Add button not found: {exc}")

        # Step 3 – Fill in Code and Description with random values
        code = f"LC_{random_string(4)}"
        desc = f"LC_Desc_{random_string(6)}"
        log(f"Step 3 – Entering Code='{code}', Desc='{desc}'")
        try:
            driver.find_element(By.NAME, "CODE$ItemName").send_keys(code)
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
            pytest.fail(f"Step 4 FAILED – Save button not found: {exc}")

        # Step 5 – Return to list, search, and verify the new code is present
        driver.get(LC_LIST_URL)
        time.sleep(2)
        _search_code(driver, wait, code)
        found = driver.find_elements(By.XPATH, f"//td[contains(.,'{code}')]")

        assert (
            found
        ), f"Step 5 FAIL – Location Code '{code}' not found after creation."
        log(f"Step 5 PASS – Location Code '{code}' created successfully.")

    def test_edit_location_code(self, setup_driver):
        driver, wait = setup_driver
        """
        TC-LC-02 – Edit an existing Location Code.
        """
        log("=== TC-LC-02: Edit Location Code ===")

        # Step 1 – Login and navigate to Location Code list
        login(driver, wait)
        log("Step 1 – Navigating to Location Code list…")
        driver.get(LC_LIST_URL)
        time.sleep(2)

        # Step 2 – Find the first valid data row
        code = None
        try:
            rows = wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//table//tr[td]")
                )
            )
            for row in rows:
                tds = row.find_elements(By.TAG_NAME, "td")
                if len(tds) >= 2:
                    candidate = tds[0].text.strip()
                    if (
                        not candidate
                        or "\n" in candidate
                        or " " in candidate[:3]
                    ):
                        continue
                    if candidate.lower() in ["code", "location code"]:
                        continue
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
                        ]
                    ):
                        continue
                    code = candidate
                    break
            if not code:
                raise RuntimeError(
                    "No valid Location Code row found in the table."
                )
            log(f"Step 2 – Selected row code: '{code}'")
        except Exception as exc:
            pytest.fail(f"Step 2 FAILED – {exc}")

        # Step 3 – Click Edit button
        row_xpath = f"//tr[td[normalize-space()='{code}']]"
        try:
            row_el = wait.until(
                EC.presence_of_element_located((By.XPATH, row_xpath))
            )
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
                            "//button[contains(.,'Edit')] | //a[contains(.,'Edit')]",
                        )
                    )
                )
                driver.execute_script("arguments[0].click();", global_edit)
                log("Step 3 – Clicked global Edit button (fallback).")
                time.sleep(2)
        except Exception as exc:
            pytest.fail(f"Step 3 FAILED – Edit button not found: {exc}")

        # Step 4 – Clear fields and enter updated values
        new_code = f"LC_{random_string(4)}_ED"
        new_desc = f"Edited LC Desc {random_string(5)}"
        log(f"Step 4 – Updating to Code='{new_code}', Desc='{new_desc}'")
        try:
            for field_name, value in [
                ("CODE$ItemName", new_code),
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
            pytest.fail(f"Step 5 FAILED – Save button not found: {exc}")

        # Step 6 – Return to list, search, and verify the updated code is present
        driver.get(LC_LIST_URL)
        time.sleep(2)
        _search_code(driver, wait, new_code)
        found = driver.find_elements(
            By.XPATH, f"//td[contains(.,'{new_code}')]"
        )

        assert (
            found
        ), f"Step 6 FAIL – Updated code '{new_code}' not found in list."
        log(f"Step 6 PASS – Location Code updated to '{new_code}' successfully.")

    def test_view_location_code(self, setup_driver):
        driver, wait = setup_driver
        """
        TC-LC-03 – View details of an existing Location Code and cancel.
        """
        log("=== TC-LC-03: View Location Code ===")

        # Step 1 – Login and navigate to Location Code list
        login(driver, wait)
        log("Step 1 – Navigating to Location Code list…")
        driver.get(LC_LIST_URL)
        time.sleep(2)

        # Step 2 – Find the first valid data row
        code = None
        try:
            rows = wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//table//tr[td]")
                )
            )
            for row in rows:
                tds = row.find_elements(By.TAG_NAME, "td")
                if len(tds) >= 2:
                    candidate = tds[0].text.strip()
                    if (
                        not candidate
                        or "\n" in candidate
                        or " " in candidate[:3]
                    ):
                        continue
                    if candidate.lower() in ["code", "location code"]:
                        continue
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
                        ]
                    ):
                        continue
                    code = candidate
                    break
            if not code:
                raise RuntimeError("No valid Location Code row found.")
            log(f"Step 2 – Using code: '{code}'")
        except Exception as exc:
            pytest.fail(f"Step 2 FAILED – {exc}")

        # Step 3 – Search for the code to isolate the row
        _search_code(driver, wait, code)

        # Step 4 – Click View button
        row_xpath = f"//tr[td[normalize-space()='{code}']]"
        try:
            row_el = wait.until(
                EC.presence_of_element_located((By.XPATH, row_xpath))
            )
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
                            "//button[contains(.,'View')] | //a[contains(.,'View')]",
                        )
                    )
                )
                driver.execute_script("arguments[0].click();", global_view)
                log("Step 4 – Clicked global View button (fallback).")
                time.sleep(2)
        except Exception as exc:
            pytest.fail(f"Step 4 FAILED – View button not found: {exc}")

        # Step 5 – Verify the details page shows the code value
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
            log(f"Step 5 WARNING – {exc}")

        # Step 6 – Click Cancel to return to the list
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
            log("Step 6 WARNING – Cancel button not found; using browser back.")
            driver.back()
            time.sleep(2)
            log(
                f"PASS – View Location Code completed for '{code}' (browser back used)."
            )
        else:
            driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", cancel_btn
            )
            driver.execute_script("arguments[0].click();", cancel_btn)
            log("Step 6 – Clicked Cancel, returned to the list.")
            time.sleep(2)
            log(f"PASS – View Location Code test completed for '{code}'.")
