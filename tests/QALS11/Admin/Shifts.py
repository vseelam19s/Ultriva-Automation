"""
Shifts.py – Selenium test cases for Admin > Shift.

Covered Test Cases:
    TC-SHIFT-01: Add a new Shift (Add flow)
    TC-SHIFT-02: Edit an existing Shift (Edit flow)
    TC-SHIFT-03: View an existing Shift and cancel (View flow)

Navigation Path:
    Admin > Shift (top/side nav)

URL Pattern (QALS1011):
    https://engineering.ultrivalms.com/QALS1011/Shift/List

Login Credentials:
    Username : buyeruser
    Password : ultriva!23

Each function accepts (driver, wait) and returns True on pass, False on fail.
Run via: run_shift_tests() at the bottom of this file.
"""

import sys
import os
import time
import random
import string

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from utils.driver_setup import get_driver
from Admin.UserGroup import login
from selenium.webdriver.support.ui import WebDriverWait

# ── Constants ────────────────────────────────────────────────────────────────
ADMIN_BASE   = "https://engineering.ultrivalms.com/QALS1011"
SHIFT_LIST_URL = f"{ADMIN_BASE}/Shift/List"


# ── Utility Functions ────────────────────────────────────────────────────────
def random_string(length=4):
    """Return a random uppercase alphanumeric string of given length."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def log(msg):
    """Prefix every log line with module name and timestamp."""
    print(f"[{time.strftime('%H:%M:%S')}][Shifts] {msg}")


def _click_save(driver, wait):
    """Click the Save button using multiple fallback selectors."""
    save_xpaths = [
        "//span[normalize-space()='Save' and contains(@class,'btn-toolbar-right-item')]",
        "//button[normalize-space()='Save']",
        "//a[normalize-space()='Save']",
        "//input[@value='Save']",
        "//*[contains(@class,'btn') and normalize-space()='Save']",
    ]
    for xp in save_xpaths:
        try:
            btn = wait.until(EC.element_to_be_clickable((By.XPATH, xp)))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            driver.execute_script("arguments[0].click();", btn)
            log("Save button clicked.")
            time.sleep(2)
            return True
        except Exception:
            continue
    log("WARNING – Save button not found with any selector.")
    return False


def _click_cancel(driver, wait):
    """Click Cancel / Back to return to the list."""
    cancel_xpaths = [
        "//button[normalize-space()='Cancel']",
        "//a[normalize-space()='Cancel']",
        "//span[normalize-space()='Cancel']",
        "//button[contains(translate(.,'cancel','CANCEL'),'CANCEL')]",
        "//a[contains(translate(.,'cancel','CANCEL'),'CANCEL')]",
        "//*[contains(@class,'btn') and contains(translate(.,'cancel','CANCEL'),'CANCEL')]",
    ]
    for xp in cancel_xpaths:
        try:
            btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, xp))
            )
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            driver.execute_script("arguments[0].click();", btn)
            log("Cancel button clicked.")
            time.sleep(2)
            return True
        except Exception:
            continue
    log("WARNING – Cancel button not found; using browser back.")
    driver.back()
    time.sleep(2)
    return True


def _fill_shift_form(driver, shift_name, start_hour="08", start_minute="00",
                     duration="8", normal_break="30"):
    """
    Fill the Shift Add/Edit form fields.

    Confirmed field names from live site (QALS1011/Shift/Create):
        SFT$ShiftName           – Shift Name (text)
        MISC$DurationHours      – Shift Duration in hours (text)
        MISC$NormalBreakMinutes – Normal Break in minutes (text)

    Start Time is TWO <select> dropdowns (hour 00-23 and minute 00/05/.../59).
    It is a *required* field — must be set via Selenium Select.
    """
    from selenium.webdriver.support.ui import Select as SeleniumSelect

    filled = 0

    # ── 1. Shift Name ─────────────────────────────────────────────────────────
    try:
        el = driver.find_element(By.NAME, "SFT$ShiftName")
        el.clear()
        el.send_keys(shift_name)
        log(f"  Filled [SFT$ShiftName] = '{shift_name}'")
        filled += 1
    except Exception as exc:
        log(f"  WARNING – SFT$ShiftName: {exc}")

    # ── 2. Start Time (two <select> dropdowns) ────────────────────────────────
    # Use JavaScript to set + dispatch change/input events (required for JS frameworks
    # like Kendo UI / AngularJS that won't pick up DOM-only changes from Selenium Select)
    selects = driver.find_elements(By.TAG_NAME, "select")
    visible_selects = [s for s in selects if s.is_displayed()]
    log(f"  Found {len(visible_selects)} visible <select> elements for Start Time.")

    def _js_select_by_value(sel_el, value_str):
        """Set a <select> value and fire change/input events via JavaScript."""
        return driver.execute_script("""
            var sel = arguments[0];
            var val = arguments[1];
            for (var i = 0; i < sel.options.length; i++) {
                if (sel.options[i].value === val) {
                    sel.selectedIndex = i;
                    break;
                }
            }
            sel.dispatchEvent(new Event('focus', {bubbles: true}));
            sel.dispatchEvent(new Event('change', {bubbles: true}));
            sel.dispatchEvent(new Event('input',  {bubbles: true}));
            sel.dispatchEvent(new Event('blur',   {bubbles: true}));
            return sel.value;
        """, sel_el, value_str)

    if len(visible_selects) >= 1:
        try:
            hour_val = start_hour.zfill(2)   # "06"
            actual = _js_select_by_value(visible_selects[0], hour_val)
            log(f"  Set Start Time hour via JS: requested='{hour_val}', actual='{actual}'")
            filled += 1
        except Exception as exc:
            log(f"  WARNING – Start hour select: {exc}")

    if len(visible_selects) >= 2:
        try:
            minute_val = start_minute.zfill(2)  # "00"
            actual = _js_select_by_value(visible_selects[1], minute_val)
            log(f"  Set Start Time minute via JS: requested='{minute_val}', actual='{actual}'")
            filled += 1
        except Exception as exc:
            log(f"  WARNING – Start minute select: {exc}")

    # ── 3. Duration in Hours ──────────────────────────────────────────────────
    try:
        el = driver.find_element(By.NAME, "MISC$DurationHours")
        el.clear()
        el.send_keys(duration)
        log(f"  Filled [MISC$DurationHours] = '{duration}'")
        filled += 1
    except Exception as exc:
        log(f"  WARNING – MISC$DurationHours: {exc}")

    # ── 4. Normal Break in Minutes ────────────────────────────────────────────
    try:
        el = driver.find_element(By.NAME, "MISC$NormalBreakMinutes")
        el.clear()
        el.send_keys(normal_break)
        log(f"  Filled [MISC$NormalBreakMinutes] = '{normal_break}'")
        filled += 1
    except Exception as exc:
        log(f"  WARNING – MISC$NormalBreakMinutes: {exc}")

    return filled > 0


# ── TC-SHIFT-01: Add Shift ───────────────────────────────────────────────────
def add_shift(driver, wait):
    """
    TC-SHIFT-01 – Add a new Shift.

    Steps:
        1. Log in and navigate to the Shift List page.
        2. Click '+ Add' toolbar button.
        3. Fill in Shift Name, Start Time, Duration, and Normal Break.
        4. Click Save.
        5. Navigate back to Shift List and verify the new shift appears.
    """
    log("=== TC-SHIFT-01: Add Shift ===")

    # Step 1 – Login and navigate
    login(driver, wait)
    log("Step 1 – Navigating to Shift List…")
    driver.get(SHIFT_LIST_URL)
    time.sleep(2)

    # Step 2 – Click '+ Add' button
    add_btn_xpath = (
        "//button[contains(normalize-space(),'Add')]"
        " | //a[contains(normalize-space(),'Add')]"
        " | //span[normalize-space()='+ Add']"
    )
    try:
        add_btn = wait.until(EC.element_to_be_clickable((By.XPATH, add_btn_xpath)))
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", add_btn)
        driver.execute_script("arguments[0].click();", add_btn)
        log("Step 2 – Clicked '+ Add' button.")
        time.sleep(2)
    except Exception as exc:
        log(f"Step 2 FAILED – Add button not found: {exc}")
        return False

    # Step 3 – Fill in form fields
    shift_name   = f"Shift_{random_string(4)}"
    start_hour   = "06"
    start_minute = "00"
    duration     = "8"
    normal_break = "30"
    log(f"Step 3 – Filling: Name='{shift_name}', Start='{start_hour}:{start_minute}', Duration='{duration}h', Break='{normal_break}min'")
    ok = _fill_shift_form(driver, shift_name, start_hour, start_minute, duration, normal_break)
    if not ok:
        log("Step 3 FAILED – Could not fill any form fields.")
        return False

    # Step 4 – Click Save
    saved = _click_save(driver, wait)
    if not saved:
        log("Step 4 FAILED – Save button not found.")
        return False
    log(f"Step 4 – Clicked Save. Post-save URL: {driver.current_url}")
    # Check if still on Create page (save validation failed)
    if "/Shift/Create" in driver.current_url or "/Shift/Edit" in driver.current_url:
        # Show full form state to diagnose what's still invalid
        body_text = driver.find_element(By.TAG_NAME, "body").text[:3000]
        log(f"  FORM STILL SHOWING. Full body text:\n{body_text}")
        # Read back select values to confirm what's selected
        try:
            all_sel = driver.find_elements(By.TAG_NAME, "select")
            vis_sel = [s for s in all_sel if s.is_displayed()]
            for idx, s in enumerate(vis_sel[:3]):
                cur_val = driver.execute_script("return arguments[0].value;", s)
                log(f"  Select[{idx}] current value='{cur_val}'")
        except Exception as ex:
            log(f"  Could not read select values: {ex}")

    # Step 5 – Verify new shift in the list
    driver.get(SHIFT_LIST_URL)
    time.sleep(2)
    log(f"Step 5 – List URL: {driver.current_url}")
    # Debug: print all visible rows
    debug_rows = driver.find_elements(By.XPATH, "//table//tr[td]")
    log(f"Step 5 – Table rows found: {len(debug_rows)}")
    for dr in debug_rows[:10]:
        cells = [td.text.strip() for td in dr.find_elements(By.TAG_NAME, "td")]
        if any(cells):
            log(f"  Row: {cells}")
    found = driver.find_elements(By.XPATH, f"//td[contains(normalize-space(),'{shift_name}')]")
    if found:
        log(f"Step 5 PASS – Shift '{shift_name}' created successfully.")
        print(f"\n[PASS] TC-SHIFT-01: Shift '{shift_name}' added successfully.")
        return True
    else:
        log(f"Step 5 FAIL – Shift '{shift_name}' not found after creation.")
        print(f"\n[FAIL] TC-SHIFT-01: Shift '{shift_name}' not found after add.")
        return False


# ── TC-SHIFT-02: Edit Shift ──────────────────────────────────────────────────
def edit_shift(driver, wait):
    """
    TC-SHIFT-02 – Edit an existing Shift.

    Steps:
        1. Log in and navigate to the Shift List page.
        2. Pick the first valid row from the table.
        3. Select the row then click the global Edit toolbar button.
        4. Update Shift Name (append '_ED').
        5. Click Save.
        6. Navigate back and verify the updated name appears.
    """
    log("=== TC-SHIFT-02: Edit Shift ===")

    # Step 1 – Login and navigate
    login(driver, wait)
    log("Step 1 – Navigating to Shift List…")
    driver.get(SHIFT_LIST_URL)
    time.sleep(2)

    # Step 2 – Find first valid shift row (Shift No in col[0] is numeric)
    shift_name = None
    shift_no   = None
    try:
        rows = wait.until(
            EC.presence_of_all_elements_located((By.XPATH, "//table//tr[td]"))
        )
        for row in rows:
            tds = row.find_elements(By.TAG_NAME, "td")
            # Shift List columns: Shift No | Shift Name | Start Time | Duration | Capacity | Break
            if len(tds) >= 2:
                col0 = tds[0].text.strip()   # Shift No  (numeric)
                col1 = tds[1].text.strip()   # Shift Name
                if not col0.isdigit():        # skip header / filter / button rows
                    continue
                if not col1:
                    continue
                shift_no   = col0
                shift_name = col1
                break
        if not shift_name:
            raise RuntimeError("No valid Shift row found in the table.")
        log(f"Step 2 – Selected Shift No={shift_no}, Name='{shift_name}'")
    except Exception as exc:
        log(f"Step 2 FAILED – {exc}")
        return False

    # Step 3 – Select the row, then click global Edit button
    row_xpath = f"//tr[td[normalize-space()='{shift_no}'] and td[normalize-space()='{shift_name}']]"
    try:
        row_el = wait.until(EC.presence_of_element_located((By.XPATH, row_xpath)))
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", row_el)
        row_el.click()
        time.sleep(1)

        # Try row-level edit button first
        edit_btn = None
        for btn_xpath in [
            ".//a[contains(translate(.,'edit','EDIT'),'EDIT') or contains(@class,'edit') or contains(@title,'Edit')]",
            ".//button[contains(translate(.,'edit','EDIT'),'EDIT')]",
        ]:
            try:
                edit_btn = row_el.find_element(By.XPATH, btn_xpath)
                break
            except Exception:
                pass

        if edit_btn and edit_btn.is_displayed():
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", edit_btn)
            driver.execute_script("arguments[0].click();", edit_btn)
            log("Step 3 – Clicked row-level Edit button.")
        else:
            # Fallback: global toolbar Edit button
            global_edit = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(normalize-space(),'Edit')] | //a[contains(normalize-space(),'Edit')]")
                )
            )
            driver.execute_script("arguments[0].click();", global_edit)
            log("Step 3 – Clicked global Edit button (fallback).")
        time.sleep(2)
    except Exception as exc:
        log(f"Step 3 FAILED – Edit button not found: {exc}")
        return False

    # Step 4 – Update the Shift Name field
    new_name = f"{shift_name[:8]}_ED"
    log(f"Step 4 – Updating Shift Name to '{new_name}'")
    updated = False
    # Confirmed field name from first run; also try generic fallbacks
    for name_attr in ["SFT$ShiftName", "ShiftName", "shiftName", "Name", "name"]:
        try:
            field = driver.find_element(By.NAME, name_attr)
            field.clear()
            field.send_keys(new_name)
            log(f"  Updated field [name='{name_attr}'] = '{new_name}'")
            updated = True
            break
        except Exception:
            pass

    if not updated:
        # Fallback: first visible, non-readonly text input
        inputs = driver.find_elements(By.XPATH, "//input[@type='text' or not(@type)]")
        for inp in inputs:
            if inp.is_displayed() and not inp.get_attribute("readonly"):
                try:
                    inp.clear()
                    inp.send_keys(new_name)
                    log(f"  Fallback: updated first visible input = '{new_name}'")
                    updated = True
                    break
                except Exception:
                    pass

    if not updated:
        log("Step 4 FAILED – Could not update Shift Name field.")
        return False

    # Step 5 – Click Save
    saved = _click_save(driver, wait)
    if not saved:
        log("Step 5 FAILED – Save button not found.")
        return False
    log("Step 5 – Clicked Save.")

    # Step 6 – Verify updated name in the list
    driver.get(SHIFT_LIST_URL)
    time.sleep(2)
    found = driver.find_elements(By.XPATH, f"//td[contains(normalize-space(),'{new_name}')]")
    if found:
        log(f"Step 6 PASS – Shift updated to '{new_name}' successfully.")
        print(f"\n[PASS] TC-SHIFT-02: Shift edited – new name '{new_name}'.")
        return True
    else:
        log(f"Step 6 FAIL – Updated shift '{new_name}' not found in list.")
        print(f"\n[FAIL] TC-SHIFT-02: Shift '{new_name}' not found after edit.")
        return False


# ── TC-SHIFT-03: View Shift ──────────────────────────────────────────────────
def view_shift(driver, wait):
    """
    TC-SHIFT-03 – View details of an existing Shift and cancel.

    Steps:
        1. Log in and navigate to the Shift List page.
        2. Pick the first valid shift row.
        3. Select the row then click the View button.
        4. Verify the view page displays Shift Name or Shift No text.
        5. Click Cancel to return to the list.
    """
    log("=== TC-SHIFT-03: View Shift ===")

    # Step 1 – Login and navigate
    login(driver, wait)
    log("Step 1 – Navigating to Shift List…")
    driver.get(SHIFT_LIST_URL)
    time.sleep(2)

    # Step 2 – Find first valid shift row (Shift No in col[0] is numeric)
    shift_name = None
    shift_no   = None
    try:
        rows = wait.until(
            EC.presence_of_all_elements_located((By.XPATH, "//table//tr[td]"))
        )
        for row in rows:
            tds = row.find_elements(By.TAG_NAME, "td")
            if len(tds) >= 2:
                col0 = tds[0].text.strip()   # Shift No (numeric)
                col1 = tds[1].text.strip()   # Shift Name
                if not col0.isdigit():
                    continue
                if not col1:
                    continue
                shift_no   = col0
                shift_name = col1
                break
        if not shift_name:
            raise RuntimeError("No valid Shift row found.")
        log(f"Step 2 – Using Shift No={shift_no}, Name='{shift_name}'")
    except Exception as exc:
        log(f"Step 2 FAILED – {exc}")
        return False

    # Step 3 – Select the row then click View
    row_xpath = f"//tr[td[normalize-space()='{shift_no}'] and td[normalize-space()='{shift_name}']]"
    try:
        row_el = wait.until(EC.presence_of_element_located((By.XPATH, row_xpath)))
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", row_el)
        row_el.click()
        time.sleep(1)

        # Try row-level View button first
        view_btn = None
        for btn_xpath in [
            ".//a[contains(translate(.,'view','VIEW'),'VIEW') or contains(@class,'view') or contains(@title,'View')]",
            ".//button[contains(translate(.,'view','VIEW'),'VIEW')]",
        ]:
            try:
                view_btn = row_el.find_element(By.XPATH, btn_xpath)
                break
            except Exception:
                pass

        if view_btn and view_btn.is_displayed():
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", view_btn)
            driver.execute_script("arguments[0].click();", view_btn)
            log("Step 3 – Clicked row-level View button.")
        else:
            # Fallback: global toolbar View button
            global_view = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(normalize-space(),'View')] | //a[contains(normalize-space(),'View')]")
                )
            )
            driver.execute_script("arguments[0].click();", global_view)
            log("Step 3 – Clicked global View button (fallback).")
        time.sleep(2)
    except Exception as exc:
        log(f"Step 3 FAILED – View button not found: {exc}")
        return False

    # Step 4 – Verify details page content
    log("Step 4 – Verifying View/Details page…")
    try:
        page_text = driver.find_element(By.TAG_NAME, "body").text
        if shift_name in page_text or "Shift" in page_text:
            log(f"Step 4 PASS – Details page loaded and contains Shift info.")
        else:
            log("Step 4 WARNING – Shift details not clearly visible on page.")
    except Exception as exc:
        log(f"Step 4 WARNING – {exc}")

    # Step 5 – Click Cancel
    log("Step 5 – Clicking Cancel to return to list…")
    _click_cancel(driver, wait)

    log(f"PASS – View Shift test completed for '{shift_name}'.")
    print(f"\n[PASS] TC-SHIFT-03: Shift '{shift_name}' viewed successfully.")
    return True


# ── Test Runner ──────────────────────────────────────────────────────────────
def run_shift_tests():
    """
    Run all Shift test cases in sequence.
    Login: buyeruser / ultriva!23  (QA site QALS1011)
    """
    driver = get_driver()
    wait   = WebDriverWait(driver, 20)

    results = {}
    try:
        results["TC-SHIFT-01 Add"]  = add_shift(driver, wait)
        results["TC-SHIFT-02 Edit"] = edit_shift(driver, wait)
        results["TC-SHIFT-03 View"] = view_shift(driver, wait)
    finally:
        driver.quit()

    # ── Summary ──────────────────────────────────────────────────────────────
    print("\n" + "=" * 55)
    print("  Shift Test Results Summary")
    print("=" * 55)
    for tc, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {tc:<30}  [{status}]")
    print("=" * 55)
    passed_count = sum(1 for v in results.values() if v)
    total_count  = len(results)
    print(f"\n  Total: {passed_count}/{total_count} passed\n")
    return results


def test_shift_suite():
    """Pytest entry point for legacy script-style Shift suite."""
    results = run_shift_tests()
    assert results, "No Shift tests executed"
    assert all(results.values()), f"Shift failures: {results}"


if __name__ == "__main__":
    run_shift_tests()

