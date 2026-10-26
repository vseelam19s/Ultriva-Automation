"""
ManageTolerancePercentage.py – Selenium test case for Admin > Manage Tolerance Percentage.

Comment:
    Apply ManageTolerancePercentage to Items

Covered Test Case:
    TC-MTP-01: Set Tolerance Percentage to 50 and click Apply
               (Admin > Manage Tolerance Percentage)

Navigation Path:
    Admin > Manage Tolerance Percentage

Login Credentials:
    Username : buyeruser
    Password : ultriva!23

Each function accepts (driver, wait) and returns True on pass, False on fail.
Run via: run_manage_tolerance_percentage_tests() at the bottom of this file.
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.driver_setup import get_driver
from Admin.UserGroup import login

# ── Constants ────────────────────────────────────────────────────────────────
ADMIN_BASE = "https://engineering.ultrivalms.com/QALS1011"
ADMIN_HOME_URL = f"{ADMIN_BASE}/Admin/Home"

TOLERANCE_PERCENTAGE_VALUE = "50"


# ── Utility helpers ──────────────────────────────────────────────────────────
def log(msg):
    """Prefix every log line with module name and timestamp."""
    print(f"[{time.strftime('%H:%M:%S')}][ManageTolerancePercentage] {msg}")


# ── Test Cases ───────────────────────────────────────────────────────────────

def tc_mtp_01_set_tolerance_percentage(driver, wait):
    """
    TC-MTP-01: Navigate to Admin > Manage Tolerance Percentage,
               enter 50 in the Tolerance Percentage (%) field, and click Apply.
    """
    log("TC-MTP-01 START – Set Tolerance Percentage to 50 and Apply")
    try:
        # Step 1: Navigate to Admin Home
        log("Navigating to Admin Home...")
        driver.get(ADMIN_HOME_URL)
        time.sleep(2)
        log(f"Admin Home loaded. URL: {driver.current_url}")

        # Step 2: Click 'Manage Tolerance Percentage' menu item
        log("Clicking 'Manage Tolerance Percentage' menu link...")
        mtp_link_xpaths = [
            "//a[contains(normalize-space(.), 'Manage Tolerance Percentage')]",
            "//a[contains(@href, 'TolerancePercentage')]",
            "//a[contains(@href, 'Tolerance')]",
        ]
        clicked = False
        for xp in mtp_link_xpaths:
            try:
                link = wait.until(EC.element_to_be_clickable((By.XPATH, xp)))
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", link)
                driver.execute_script("arguments[0].click();", link)
                log(f"Clicked link using xpath: {xp}")
                clicked = True
                time.sleep(2)
                break
            except Exception:
                continue
        if not clicked:
            log("ERROR – 'Manage Tolerance Percentage' link not found in Admin menu.")
            return False
        log(f"Manage Tolerance Percentage page loaded. URL: {driver.current_url}")

        # Step 3: Enter 50 in the Tolerance Percentage (%) input field
        # Field IDs confirmed by page inspection:
        #   MISC$TolerancePercentShip  – Ship tolerance
        #   MISC$TolerancePercentReceive – Receive tolerance (linked when same-tolerance checkbox is on)
        log(f"Entering Tolerance Percentage value: {TOLERANCE_PERCENTAGE_VALUE}")
        input_xpaths = [
            "//input[@id='MISC$TolerancePercentShip']",
            "//input[contains(@id,'TolerancePercent')]",
            "//input[contains(@name,'TolerancePercent')]",
        ]
        entered = False
        for xp in input_xpaths:
            try:
                inp = wait.until(EC.presence_of_element_located((By.XPATH, xp)))
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", inp)
                driver.execute_script("arguments[0].value = '';", inp)
                inp.clear()
                inp.send_keys(TOLERANCE_PERCENTAGE_VALUE)
                driver.execute_script(
                    "arguments[0].dispatchEvent(new Event('change', {bubbles:true}));", inp
                )
                log(f"Entered '{TOLERANCE_PERCENTAGE_VALUE}' using xpath: {xp}")
                entered = True
                break
            except Exception:
                continue
        if not entered:
            log("ERROR – Tolerance Percentage input field not found.")
            return False

        # Step 4: Click the Apply button
        # Confirmed by page inspection: <span class="btn vd-blue-btn btn-toolbar-right-item">Apply</span>
        log("Clicking 'Apply' button...")
        apply_xpaths = [
            "//span[normalize-space()='Apply' and contains(@class,'btn-toolbar-right-item')]",
            "//span[normalize-space()='Apply' and contains(@class,'btn')]",
            "//button[normalize-space()='Apply']",
            "//a[normalize-space()='Apply']",
            "//*[contains(@class,'btn') and normalize-space()='Apply']",
        ]
        applied = False
        for xp in apply_xpaths:
            try:
                btn = wait.until(EC.element_to_be_clickable((By.XPATH, xp)))
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
                driver.execute_script("arguments[0].click();", btn)
                log(f"Apply button clicked using xpath: {xp}")
                applied = True
                time.sleep(2)
                break
            except Exception:
                continue
        if not applied:
            log("ERROR – Apply button not found.")
            return False

        log("TC-MTP-01 PASS – Tolerance Percentage set to 50 and Apply clicked successfully.")
        return True

    except Exception as exc:
        log(f"TC-MTP-01 FAIL – Unexpected error: {exc}")
        return False


# ── Runner ───────────────────────────────────────────────────────────────────

def run_manage_tolerance_percentage_tests():
    """Run all Manage Tolerance Percentage test cases."""
    driver = get_driver()
    wait = WebDriverWait(driver, 20)
    results = {}
    try:
        login(driver, wait)

        results["TC-MTP-01"] = tc_mtp_01_set_tolerance_percentage(driver, wait)

    finally:
        driver.quit()

    print("\n" + "=" * 60)
    print("Manage Tolerance Percentage – Test Results")
    print("=" * 60)
    for tc, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {tc}: {status}")
    print("=" * 60)
    return results


def test_manage_tolerance_percentage_suite():
    """Pytest entry point for legacy script-style tolerance suite."""
    results = run_manage_tolerance_percentage_tests()
    assert results, "No Manage Tolerance Percentage tests executed"
    assert all(results.values()), f"Manage Tolerance Percentage failures: {results}"


if __name__ == "__main__":
    run_manage_tolerance_percentage_tests()

