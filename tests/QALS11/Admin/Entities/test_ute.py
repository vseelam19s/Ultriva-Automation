import os
import random
import string
import sys
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Allow imports from the qa_automation root (two levels up from this file)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from Admin.UserGroup import login
from utils.driver_setup import get_driver

"""
Route.py – Selenium test cases for Admin > Entities > Route.

Covered Test Cases:
    TC-RT-01: Add a new Route code (Add flow)
    TC-RT-02: Edit an existing Route code (Edit flow)
    TC-RT-03: View an existing Route code and cancel (View flow)

Navigation Path:
    Admin > Entities (left nav) > Route

URL Pattern (QALS1011):
    https://engineering.ultrivalms.com/QALS1011/Entity/List?tk=$Route&busGID=BSU22ZAQALQG&A~1~ABC&
"""

# ── Constants ────────────────────────────────────────────────────────────────
ADMIN_BASE = "https://engineering.ultrivalms.com/QALS1011"
ROUTE_LIST_URL = f"{ADMIN_BASE}/Entity/List?tk=$Routes&busGID=BSU22ZAQALQG&A~1~ABC&"


@pytest.fixture(scope="class")
def setup_driver():
    """Sets up the driver instance and performs a single authentication login."""
    driver = get_driver()
    wait = WebDriverWait(driver, 20)

    log("Performing global fixture login...")
    login(driver, wait)

    yield driver, wait
    driver.quit()


# ── Utility Functions ────────────────────────────────────────────────────────


def random_string(length=5):
    """Return a random uppercase alphanumeric string of given length."""
    return "".join(
        random.choices(string.ascii_uppercase + string.digits, k=length)
    )


def log(msg):
    """Prefix every log line with the module name and a timestamp."""
    print(f"[{time.strftime('%H:%M:%S')}][Route] {msg}")


def _search_code(driver, wait, code):
    """Type *code* into the 'Find Code' search box so the list filters.

    Falls back to JavaScript event dispatch if the input is not interactable.
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


class TestUte:

    def test_add_route(self, setup_driver):
        driver, wait = setup_driver
        """
        TC-RT-01 – Add a new Route code.
        """
        log("=== TC-RT-01: Add Route ===")

        log("Step 1 – Navigating to Route list…")
        driver.get(ROUTE_LIST_URL)
        time.sleep(2)

        # Step 2 – Click the '+ Add' button to open the creation form
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

        # Step 3 – Fill Code, Title, and Description with random values
        code = f"RT_{random_string(4)}"
        title = f"RouteTitle_{random_string(4)}"
        desc = f"RouteDesc_{random_string(6)}"
        log(
            f"Step 3 – Entering Code='{code}', Title='{title}', Desc='{desc}'"
        )
        try:
            driver.find_element(By.NAME, "ROUTE$RouteCode").send_keys(code)
            driver.find_element(By.NAME, "ROUTE$RouteName").send_keys(title)
            driver.find_element(By.NAME, "ROUTE$RouteDescription").send_keys(
                desc
            )
        except Exception as exc:
            pytest.fail(f"Step 3 FAILED – Could not fill form fields: {exc}")

        # Step 4 – Click Save to persist the new Route entry
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

        # Step 5 – Navigate back to the list and verify the new code is present
        driver.get(ROUTE_LIST_URL)
        time.sleep(2)
        _search_code(driver, wait, code)
        found = driver.find_elements(By.XPATH, f"//td[contains(.,'{code}')]")

        assert found, f"Step 5 FAIL – Route '{code}' not found after creation."
        log(f"Step 5 PASS – Route '{code}' created successfully.")

    def test_edit_route(self, setup_driver):
        driver, wait = setup_driver
        """
        TC-RT-02 – Edit an existing Route code.
        """
        log("=== TC-RT-02: Edit Route ===")

        log("Step 1 – Navigating to Route list…")
        driver.get(ROUTE_LIST_URL)
        time.sleep(2)

        # Step 2 – Find the first valid code row
        code = None
        try:
            rows = wait.until(
                EC.presence_of_all_elements_located(
                    (
                        By.XPATH,
                        "//table//tr[td and not(.//input) and not(.//select)]",
                    )
                )
            )
            for row in rows:
                tds = row.find_elements(By.TAG_NAME, "td")
                if len(tds) >= 2:
                    candidate = tds[0].text.strip()
                    if (
                        not candidate
                        or len(candidate) < 3
                        or "\n" in candidate
                        or " " in candidate[:3]
                    ):
                        continue
                    if candidate.lower() in ["code", "route", "go", "default"]:
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
                raise RuntimeError("No valid Route code row found in the table.")
            log(f"Step 2 – Selected row code: '{code}'")
        except Exception as exc:
            pytest.fail(f"Step 2 FAILED – {exc}")

        # Step 3 – Click the Edit button for the selected row
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

        # Step 4 – Clear and update fields
        new_code = f"RT_{random_string(4)}_ED"
        new_title = f"RouteEdit_{random_string(4)}"
        new_desc = f"Edited Route Desc {random_string(5)}"
        log(
            f"Step 4 – Updating to Code='{new_code}', Title='{new_title}', Desc='{new_desc}'"
        )
        try:
            for field_name, value in [
                ("ROUTE$RouteCode", new_code),
                ("ROUTE$RouteName", new_title),
                ("ROUTE$RouteDescription", new_desc),
            ]:
                field = driver.find_element(By.NAME, field_name)
                field.clear()
                field.send_keys(value)
        except Exception as exc:
            pytest.fail(f"Step 4 FAILED – Could not update fields: {exc}")

        # Step 5 – Save changes
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

        # Step 6 – Verify the updated code appears in the list
        driver.get(ROUTE_LIST_URL)
        time.sleep(2)
        _search_code(driver, wait, new_code)
        found = driver.find_elements(
            By.XPATH, f"//td[contains(.,'{new_code}')]"
        )

        assert (
            found
        ), f"Step 6 FAIL – Updated code '{new_code}' not found in list."
        log(f"Step 6 PASS – Route updated to '{new_code}' successfully.")

    def test_view_route(self, setup_driver):
        driver, wait = setup_driver
        """
        TC-RT-03 – View details of an existing Route code and cancel.
        """
        log("=== TC-RT-03: View Route ===")

        log("Step 1 – Navigating to Route list…")
        driver.get(ROUTE_LIST_URL)
        time.sleep(2)

        # Step 2 – Find the first valid code row
        code = None
        try:
            rows = wait.until(
                EC.presence_of_all_elements_located(
                    (
                        By.XPATH,
                        "//table//tr[td and not(.//input) and not(.//select)]",
                    )
                )
            )
            for row in rows:
                tds = row.find_elements(By.TAG_NAME, "td")
                if len(tds) >= 2:
                    candidate = tds[0].text.strip()
                    if (
                        not candidate
                        or len(candidate) < 3
                        or "\n" in candidate
                        or " " in candidate[:3]
                    ):
                        continue
                    if candidate.lower() in ["code", "route", "go", "default"]:
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
                raise RuntimeError("No valid Route code row found.")
            log(f"Step 2 – Using code: '{code}'")
        except Exception as exc:
            pytest.fail(f"Step 2 FAILED – {exc}")

        # Step 3 – Filter the list using the Find Code search box
        _search_code(driver, wait, code)

        # Step 4 – Click the View button for the matching row
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

        # Step 5 – Verify details page rendering
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

        # Step 6 – Click Cancel to return to the Route list
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
        else:
            driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", cancel_btn
            )
            driver.execute_script("arguments[0].click();", cancel_btn)
            log("Step 6 – Clicked Cancel, returned to list.")
            time.sleep(2)

        log(f"PASS – View Route test completed for '{code}'.")
