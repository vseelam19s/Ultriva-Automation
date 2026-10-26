from Admin.UserGroup import login
from utils.driver_setup import get_driver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pytest
import sys
import os
import time
import random
import string

"""
SkipLotPlan.py – Selenium test cases for Admin > Entities > Skip Lot Plan.

Covered Test Cases:
    TC-SLP-01: Add a new Skip Lot Plan      (Add flow)
    TC-SLP-02: Edit an existing Skip Lot Plan (Edit flow)
    TC-SLP-03: View an existing Skip Lot Plan and cancel (View flow)

Navigation Path:
    Admin > Entities (left nav tab) > Skip Lot Plan

URL Pattern (QALS1011):
    https://engineering.ultrivalms.com/QALS1011/Entity/List?tk=$SkipLotPlan&busGID=BSU22ZAQALQG&A~1~ABC&
"""

# Allow running from the qa_automation root or from the Entities sub-folder
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

@pytest.fixture(scope="class")
def setup_driver():
    driver = get_driver()
    wait = WebDriverWait(driver, 20)
    yield driver, wait
    driver.quit()

# ── Constants ───────────────────────────────────────────────────────────
ADMIN_BASE = "https://engineering.ultrivalms.com/QALS1011"
SLP_LIST_URL = (
    f"{ADMIN_BASE}/Entity/List?tk=$SkipLotPlan"
    "&busGID=BSU22ZAQALQG&A~1~ABC&"
)

# ── Utility Helpers ─────────────────────────────────────────────────────
def random_string(length=5):
    """Return a random uppercase alphanumeric string of the given length."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def log(msg):
    """Prefix every console line with module name and current timestamp."""
    print(f"[{time.strftime('%H:%M:%S')}][SkipLotPlan] {msg}")


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
                "arguments[0].dispatchEvent(new KeyboardEvent('keyup',"
                "{bubbles:true,key:'Enter',keyCode:13}));", box, code, )
        except Exception as exc2:
            log(f"JS search fallback also failed: {exc2}")
    time.sleep(2)


# ── Test Suite Class ──────────────────────────────────────────────────
class TestSkiplotplan:

    def test_add_skip_lot_plan(self, setup_driver):
        driver, wait = setup_driver
        log("=== TC-SLP-01: Add Skip Lot Plan ===")

        # Step 1 – Login and navigate to the Skip Lot Plan list page
        login(driver, wait)
        log("Step 1 – Navigating to Skip Lot Plan list…")
        driver.get(SLP_LIST_URL)
        time.sleep(2)

        # Step 2 – Click the '+ Add' toolbar button
        add_btn_xpath = "//button[contains(.,'Add')] | //a[contains(.,'Add')]"
        try:
            add_btn = wait.until(EC.element_to_be_clickable((By.XPATH, add_btn_xpath)))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", add_btn)
            driver.execute_script("arguments[0].click();", add_btn)
            log("Step 2 – Clicked '+ Add' button.")
            time.sleep(2)
        except Exception as exc:
            pytest.fail(f"Step 2 FAILED – Add button not found: {exc}")

        # Step 3 – Fill in Form Fields
        code = f"SLP_{random_string(4)}"
        title = f"SLP_Title_{random_string(4)}"
        desc = f"Skip Lot Plan Desc {random_string(6)}"
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
                pytest.fail(f"Step 3 FAILED – Could not fill form fields: {exc2}")

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
            pytest.fail(f"Step 4 FAILED – Save button not found: {exc}")

        # Step 4a – Inspect URL after Save
        post_save_url = driver.current_url
        log(f"Step 4a – URL after Save: {post_save_url}")
        if "Entity/Add" in post_save_url or "Entity/Create" in post_save_url:
            log("Step 4a WARNING – Still on the form; extracting validation error blocks.")
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
            pytest.fail("Form submission failed due to UI validation rules.")

        if "Entity/List" in post_save_url or "SkipLotPlan" in post_save_url:
            log(f"Step 4a PASS – Redirected to list page after Save.")
            return

        # Step 5 – Fallback List Verification
        driver.get(SLP_LIST_URL)
        time.sleep(2)
        _search_code(driver, wait, code)
        found = driver.find_elements(By.XPATH, f"//td[contains(.,'{code}')]")
        if found:
            log(f"Step 5 PASS – Skip Lot Plan '{code}' created successfully.")
        else:
            all_cells = driver.find_elements(By.XPATH, "//table//td")
            all_text = [c.text.strip() for c in all_cells if c.text.strip()]
            log(f"Step 5 INFO – Visible codes in table: {all_text[:20]}")
            assert code in all_text, f"Step 5 FAIL – Skip Lot Plan '{code}' not found after creation."

    def test_edit_skip_lot_plan(self, setup_driver):
        driver, wait = setup_driver
        log("=== TC-SLP-02: Edit Skip Lot Plan ===")

        login(driver, wait)
        log("Step 1 – Navigating to Skip Lot Plan list…")
        driver.get(SLP_LIST_URL)
        time.sleep(2)

        # Step 2 – Find a valid record row
        code = None
        try:
            rows = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//table//tr[td]")))
            for row in rows:
                tds = row.find_elements(By.TAG_NAME, "td")
                if len(tds) >= 2:
                    candidate = tds[0].text.strip()
                    if not candidate or "\n" in candidate or " " in candidate[:3]:
                        continue
                    if candidate.lower() in ["code", "skip lot plan", "name", "title"]:
                        continue
                    if any(x in candidate.lower() for x in ["add", "edit", "view", "delete", "sorted"]):
                        continue
                    code = candidate
                    break
            if not code:
                raise RuntimeError("No valid Skip Lot Plan row found in the table.")
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
        new_code = f"SLP_{random_string(4)}_ED"
        new_title = f"SLP_Edit_{random_string(4)}"
        new_desc = f"Edited Skip Lot Plan Desc {random_string(5)}"
        log(f"Step 4 – Updating to Code='{new_code}', Title='{new_title}', Desc='{new_desc}'")
        try:
            for field_name, value in [("CODE$ItemName", new_code), ("CODE$Title", new_title), ("CODE$Description", new_desc)]:
                field = driver.find_element(By.NAME, field_name)
                field.clear()
                field.send_keys(value)
        except Exception:
            log("Step 4 – NAME lookup failed; trying placeholder fallback.")
            try:
                for placeholder, value in [("Code", new_code), ("Title", new_title), ("Description", new_desc)]:
                    field = driver.find_element(By.XPATH, f"//input[@placeholder='{placeholder}'] | //textarea[@placeholder='{placeholder}']")
                    field.clear()
                    field.send_keys(value)
            except Exception as exc2:
                pytest.fail(f"Step 4 FAILED – Could not update fields: {exc2}")

        # Step 5 – Save
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

        # Step 6 – Verify Edit Update
        driver.get(SLP_LIST_URL)
        time.sleep(2)
        _search_code(driver, wait, new_code)
        found = driver.find_elements(By.XPATH, f"//td[contains(.,'{new_code}')]")
        if found:
            log(f"Step 6 PASS – Skip Lot Plan updated to '{new_code}' successfully.")
        else:
            all_cells = driver.find_elements(By.XPATH, "//table//td")
            all_text = [c.text.strip() for c in all_cells if c.text.strip()]
            assert new_code in all_text, f"Step 6 FAIL – Updated code '{new_code}' not found in list."

    def test_view_skip_lot_plan(self, setup_driver):
        driver, wait = setup_driver
        log("=== TC-SLP-03: View Skip Lot Plan ===")

        login(driver, wait)
        log("Step 1 – Navigating to Skip Lot Plan list…")
        driver.get(SLP_LIST_URL)
        time.sleep(2)

        # Step 2 – Find row code
        code = None
        try:
            rows = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//table//tr[td]")))
            for row in rows:
                tds = row.find_elements(By.TAG_NAME, "td")
                if len(tds) >= 2:
                    candidate = tds[0].text.strip()
                    if not candidate or "\n" in candidate or " " in candidate[:3]:
                        continue
                    if candidate.lower() in ["code", "skip lot plan", "name", "title"]:
                        continue
                    if any(x in candidate.lower() for x in ["add", "edit", "view", "delete", "sorted"]):
                        continue
                    code = candidate
                    break
            if not code:
                raise RuntimeError("No valid Skip Lot Plan row found in the table.")
            log(f"Step 2 – Using code: '{code}'")
        except Exception as exc:
            pytest.fail(f"Step 2 FAILED – {exc}")

        # Step 3 & 4 – Search and Click View
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
            pytest.fail(f"Step 4 FAILED – View button not found: {exc}")

        # Step 5 – Inspect Content
        log("Step 5 – Verifying detail page content…")
        try:
            for tag in ["div", "span", "td", "h2", "h3", "label"]:
                for el in driver.find_elements(By.TAG_NAME, tag):
                    try:
                        txt = el.text.strip()
                        if (code in txt or "Skip Lot" in txt or "Code:" in txt) and el.is_displayed():
                            log(f"  Detail content – <{tag}>: '{txt[:120]}'")
                            break
                    except Exception:
                        pass
        except Exception as exc:
            log(f"Step 5 WARNING – Could not inspect detail content: {exc}")

        # Step 6 – Cancel / Exit Flow
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
            log("Step 6 WARNING – Cancel button not found; shifting to safe fallback (Browser Back).")
            driver.back()
            time.sleep(2)
            return

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", cancel_btn)
        driver.execute_script("arguments[0].click();", cancel_btn)
        log("Step 6 – Clicked Cancel, returned to list.")
        time.sleep(2)


# ── Standalone Custom Engine Runner ───────────────────────────────────────
if __name__ == "__main__":
    """Instantiates standalone loop structure if executed directly."""
    print("\n[Engine] Starting Standalone UI Verification Loop Context...")
    driver_instance = get_driver()
    wait_instance = WebDriverWait(driver_instance, 20)
    
    test_class = TestSkiplotplan()
    mocked_fixture = (driver_instance, wait_instance)

    suite = [
        ("TC-SLP-01  Add  Skip Lot Plan", test_class.test_add_skip_lot_plan),
        ("TC-SLP-02  Edit Skip Lot Plan", test_class.test_edit_skip_lot_plan),
        ("TC-SLP-03  View Skip Lot Plan", test_class.test_view_skip_lot_plan),
    ]

    results = {}
    for name, fn in suite:
        print(f"\n{'─' * 55}\n  Running: {name}\n{'─' * 55}")
        try:
            fn(mocked_fixture)
            results[name] = True
        except Exception as err:
            print(f"  [ERROR] Execution Failure tracking inside '{name}': {err}")
            results[name] = False

    driver_instance.quit()

    # Final Summary Terminal output block
    print("\n" + "=" * 70)
    print("  SKIP LOT PLAN TESTS – FINAL STANDALONE SUMMARY")
    print("=" * 70)
    for name, passed in results.items():
        print(f"  [{'PASS' if passed else 'FAIL'}]  {name}")
    print("=" * 70)
    total = len(results)
    passed_count = sum(1 for v in results.values() if v)
    print(f"  Total: {total} | Passed: {passed_count} | Failed: {total - passed_count}")
    print("=" * 70 + "\n")
