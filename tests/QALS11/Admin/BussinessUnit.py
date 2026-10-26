"""
BussinessUnit.py – Selenium test case for Admin > Business Unit.

Covered Test Case:
    TC-BU-01: Update Business Unit Configuration (Edit Plant TCEK-Ram > change
              Address fields > Save)

Comment:
    Update business configuration — verifies that the Edit Plant form for the
    TCEK-Ram business unit can be opened, address fields updated with new
    random values, and saved successfully.

Navigation Path:
    Admin > Business Unit (Plant List)
    Edit Plant TCEK-Ram

URL Pattern (QALS1011):
    List : https://engineering.ultrivalms.com/QALS1011/Plant/List
    Edit : https://engineering.ultrivalms.com/QALS1011/Plant/UpdateFromMyAccount?GID=<GID>

Form Fields (Edit Plant – Address Information):
    Required – Address 1, City, Country
    Optional – Address 2, Address 3, State, Zip

Each function accepts (driver, wait) and returns True on pass, False on fail.
Run via: run_bussiness_unit_tests() at the bottom of this file.

Reference: DropOffLocation.py / LocationCode.py patterns.
"""

import sys
import os
import time
import random
import string

# Allow running from the qa_automation root or from the admin subfolder
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.driver_setup import get_driver
from Admin.UserGroup import login

# ── Constants ────────────────────────────────────────────────────────────────
ADMIN_BASE   = "https://engineering.ultrivalms.com/QALS1011"
BU_LIST_URL  = f"{ADMIN_BASE}/Plant/List"

# The target business unit name to edit
TARGET_BU_NAME = "TCEK-Ram"

# Direct Edit URL for TCEK-Ram (GID is fixed for this plant record)
# buyeruser is not authorized to view Plant/List, but can access this edit URL
BU_EDIT_URL = f"{ADMIN_BASE}/Plant/UpdateFromMyAccount?GID=BSU22ZAQALQG"


# ── Utility helpers ──────────────────────────────────────────────────────────
def random_string(length=5):
    """Return a random uppercase alphanumeric string of the given length."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def log(msg):
    """Prefix every console line with module name and current timestamp."""
    print(f"[{time.strftime('%H:%M:%S')}][BussinessUnit] {msg}")


# ── TC-BU-01: Update Business Unit Configuration ─────────────────────────────
def update_bussiness_unit(driver, wait):
    """
    TC-BU-01 – Update Business Unit Configuration.

    Comment: Update business configuration

    Test Steps:
        1. Log in as 'buyeruser' / 'ultriva!23' and navigate directly to the
           Edit Plant page for TCEK-Ram (Plant/UpdateFromMyAccount?GID=…).
           Note: buyeruser cannot view Plant/List but can access the edit form.
        2. Verify the Edit Plant page loaded for the correct business unit
           (TCEK-Ram).
        3. In the 'Address Information' section, clear and update:
               Address 1 (ADR$Street1)   – new random address
               City      (ADR$City)      – new random city
               Country   (ADR$Country)   – keep as 'India'
        4. Click Save.
        5. Verify no validation errors appear after save (page stays or
           redirects without an error alert).

    Expected Result:
        The Edit Plant page for TCEK-Ram saves successfully without any
        validation error or exception.
    """
    log("=== TC-BU-01: Update Business Unit Configuration ===")

    # ── Step 1 – Login and navigate directly to Edit Plant TCEK-Ram ──────────
    login(driver, wait)
    log("Step 1 – Navigating to Edit Plant TCEK-Ram…")
    driver.get(BU_EDIT_URL)
    time.sleep(3)

    # ── Step 2 – Verify we are on the correct edit page ───────────────────────
    log("Step 2 – Verifying Edit Plant page for TCEK-Ram…")
    try:
        # The BUS$Name field should contain 'TCEK-Ram'
        bu_name_field = wait.until(
            EC.presence_of_element_located((By.NAME, "BUS$Name"))
        )
        bu_name_value = bu_name_field.get_attribute("value")
        log(f"Step 2 – BUS$Name value = '{bu_name_value}'")
        if TARGET_BU_NAME not in bu_name_value:
            log(f"Step 2 FAIL – Expected '{TARGET_BU_NAME}' in BUS$Name, got '{bu_name_value}'")
            return False
        log(f"Step 2 PASS – Edit Plant page is for '{bu_name_value}'.")
    except Exception as exc:
        log(f"Step 2 FAILED – Could not verify edit page: {exc}")
        return False

    # ── Step 3 – Update Address Information fields ─────────────────────────────
    # Confirmed field names from page inspection:
    #   ADR$Street1  – Address 1 (required)
    #   ADR$City     – City (required)
    #   ADR$Country  – Country (required)
    unique_suffix = random_string(4)
    new_address1  = f"{random.randint(100, 9999)} Test Ave {unique_suffix}"
    new_city      = f"City_{unique_suffix}"
    new_country   = "India"   # Keep country as India (required; preserve valid value)

    log(
        f"Step 3 – Updating Address: Street1='{new_address1}', "
        f"City='{new_city}', Country='{new_country}'"
    )
    try:
        # Address 1 – ADR$Street1
        addr1_field = wait.until(EC.presence_of_element_located((By.NAME, "ADR$Street1")))
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", addr1_field)
        addr1_field.clear()
        addr1_field.send_keys(new_address1)
        log(f"Step 3 – ADR$Street1 set to '{new_address1}'.")

        # City – ADR$City
        city_field = driver.find_element(By.NAME, "ADR$City")
        city_field.clear()
        city_field.send_keys(new_city)
        log(f"Step 3 – ADR$City set to '{new_city}'.")

        # Country – ADR$Country (keep as India to avoid validation error)
        country_field = driver.find_element(By.NAME, "ADR$Country")
        country_field.clear()
        country_field.send_keys(new_country)
        log(f"Step 3 – ADR$Country set to '{new_country}'.")

        log("Step 3 PASS – Address Information fields updated.")
    except Exception as exc:
        log(f"Step 3 FAILED – Could not update address fields: {exc}")
        return False

    time.sleep(1)

    # ── Step 4 – Click Save (submit the Edit Plant form) ──────────────────────
    # The Edit Plant page uses a POST form (action=UpdateFromMyAccount).
    # There is no standard <button type="submit">. The form is submitted via
    # the toolbar button 'PlantProfile_tbrCrop' (the Save/Update action) or,
    # as a fallback, via JavaScript form.submit().
    log("Step 4 – Clicking Save (PlantProfile_tbrCrop)…")
    try:
        save_btn = wait.until(EC.element_to_be_clickable(
            (By.ID, "PlantProfile_tbrCrop")
        ))
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", save_btn)
        driver.execute_script("arguments[0].click();", save_btn)
        log("Step 4 – Clicked PlantProfile_tbrCrop (Save).")
        time.sleep(3)
    except Exception:
        log("Step 4 – PlantProfile_tbrCrop not found; falling back to JS form.submit()…")
        try:
            driver.execute_script(
                "var form = document.querySelector('form[action*=\"UpdateFromMyAccount\"]');"
                "if (form) { form.submit(); }"
            )
            log("Step 4 – Submitted form via JavaScript.")
            time.sleep(3)
        except Exception as exc:
            log(f"Step 4 FAILED – Could not submit form: {exc}")
            return False

    # ── Step 5 – Verify save succeeded (no validation errors) ─────────────────
    log("Step 5 – Verifying save result…")
    try:
        current_url = driver.current_url
        log(f"Step 5 – Current URL after save: {current_url}")

        # Check for visible error messages
        error_elems = driver.find_elements(
            By.XPATH,
            "//*[contains(@class,'error') or contains(@class,'alert-danger') or "
            "contains(@class,'validation-summary-errors')]"
        )
        visible_errors = [
            e.text.strip() for e in error_elems
            if e.text.strip() and e.is_displayed()
        ]
        if visible_errors:
            log(f"Step 5 FAIL – Validation errors: {visible_errors}")
            print(f"\n[FAIL] TC-BU-01: Save returned errors: {visible_errors}")
            return False

        # After a successful save the page either:
        #   a) Redirects away from the edit URL (success), or
        #   b) Stays on the edit URL but shows no errors (also success)
        # Confirm BUS$Name is still TCEK-Ram if we're still on the edit page
        if "UpdateFromMyAccount" in current_url:
            bu_name_inputs = driver.find_elements(By.NAME, "BUS$Name")
            if bu_name_inputs:
                val = bu_name_inputs[0].get_attribute("value")
                log(f"Step 5 – Still on edit page; BUS$Name='{val}'.")
                if TARGET_BU_NAME not in val:
                    log("Step 5 FAIL – Unexpected BUS$Name after save.")
                    print(f"\n[FAIL] TC-BU-01: Unexpected state after save.")
                    return False

        log("Step 5 PASS – No validation errors found after save.")
        print(
            f"\n[PASS] TC-BU-01: Business Unit '{TARGET_BU_NAME}' "
            "configuration updated successfully."
        )
        return True
    except Exception as exc:
        log(f"Step 5 FAILED – {exc}")
        print(f"\n[FAIL] TC-BU-01: Could not verify save result: {exc}")
        return False


# ── Test Runner ───────────────────────────────────────────────────────────────
def run_bussiness_unit_tests():
    """
    Entry point: instantiate WebDriver, run TC-BU-01, print a summary table,
    and quit the browser.

    Comment: Update business configuration

    Usage:
        python admin/BussinessUnit.py   (from qa_automation/)
        or
        python -m admin.BussinessUnit
    """
    driver = get_driver()
    wait   = WebDriverWait(driver, 25)

    results = {}

    # TC-BU-01: Update Business Unit Configuration
    # Comment: Update business configuration
    try:
        results["TC-BU-01  Update Business Unit Configuration"] = (
            update_bussiness_unit(driver, wait)
        )
    except Exception as exc:
        log(f"TC-BU-01 raised exception: {exc}")
        results["TC-BU-01  Update Business Unit Configuration"] = False

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  BUSINESS UNIT TEST RESULTS")
    print("=" * 60)
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}]  {name}")
    print("=" * 60)
    total        = len(results)
    passed_count = sum(1 for v in results.values() if v)
    print(f"  Total: {total} | Passed: {passed_count} | Failed: {total - passed_count}")
    print("=" * 60 + "\n")

    driver.quit()
    return results


def test_bussiness_unit_suite():
    """Pytest entry point for legacy script-style Business Unit suite."""
    results = run_bussiness_unit_tests()
    assert results, "No Business Unit tests executed"
    assert all(results.values()), f"Business Unit failures: {results}"


# ── Script Entry ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    run_bussiness_unit_tests()

