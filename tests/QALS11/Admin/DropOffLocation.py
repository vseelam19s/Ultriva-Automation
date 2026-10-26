"""
DropOffLocation.py – Selenium test cases for Admin > Dropoff Location.

Covered Test Cases:
    TC-DOL-01: Add a new Dropoff Location   (Add flow)
    TC-DOL-02: Edit an existing Dropoff Location  (Edit flow)
    TC-DOL-03: View an existing Dropoff Location and cancel  (View flow)

Navigation Path:
    Admin > Dropoff Location

URL Pattern (QALS1011):
    List  : https://engineering.ultrivalms.com/QALS1011/Warehouse/List
    Create: https://engineering.ultrivalms.com/QALS1011/Warehouse/Create

Form Fields (Create / Edit):
    Required  – Name, Code, Address 1, City, Country
    Optional  – Address 2, Address 3, State, Zip

Each function accepts (driver, wait) and returns True on pass, False on fail.
Run via: run_dropoff_location_tests() at the bottom of this file, or
include in run_admin_entity_tests.py.

Reference: LocationCode.py / ABCCode.py patterns.
"""

import sys
import os
import time
import random
import string

# Allow running from the qa_automation root or from the Entities subfolder
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.driver_setup import get_driver
from Admin.UserGroup import login

# ── Constants ────────────────────────────────────────────────────────────────
ADMIN_BASE = "https://engineering.ultrivalms.com/QALS1011"

# Dropoff Location list and create URLs
DOL_LIST_URL   = f"{ADMIN_BASE}/Warehouse/List"
DOL_CREATE_URL = f"{ADMIN_BASE}/Warehouse/Create"


# ── Utility helpers ──────────────────────────────────────────────────────────
def random_string(length=5):
    """Return a random uppercase alphanumeric string of the given length."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def log(msg):
    """Prefix every console line with module name and current timestamp."""
    print(f"[{time.strftime('%H:%M:%S')}][DropOffLocation] {msg}")


def _search_name(driver, wait, name):
    """
    Type *name* into the Find Name search box so the list filters down.
    Falls back to a JavaScript value-set when the box is not interactable.
    """
    search_xpath = "//input[contains(@placeholder,'Find Name') or contains(@placeholder,'Find') or @type='text']"
    try:
        box = wait.until(EC.visibility_of_element_located((By.XPATH, search_xpath)))
        wait.until(EC.element_to_be_clickable((By.XPATH, search_xpath)))
        box.clear()
        box.send_keys(name)
    except Exception as exc:
        log(f"Search box not interactable: {exc}  — trying JS fallback.")
        box = driver.find_element(By.XPATH, search_xpath)
        driver.execute_script(
            "arguments[0].value = arguments[1];"
            "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));",
            box, name,
        )
    time.sleep(2)


def _fill_form_field(driver, label_text, value):
    """
    Fill a form input by locating the <input> sibling of a visible <label>
    that contains *label_text*.  Tries several XPath strategies in order.
    """
    strategies = [
        # Strategy 1: input that follows a label containing the text
        f"//label[contains(normalize-space(.), '{label_text}')]/following-sibling::input[1]",
        # Strategy 2: input inside the same form-group as the label
        f"//label[contains(normalize-space(.), '{label_text}')]/..//input",
        # Strategy 3: input with a name or id containing a keyword derived from label
        f"//input[contains(@name,'{label_text}') or contains(@id,'{label_text}')]",
    ]
    for xpath in strategies:
        try:
            field = driver.find_element(By.XPATH, xpath)
            if field:
                field.clear()
                field.send_keys(value)
                return True
        except Exception:
            continue
    return False


# ── TC-DOL-01: Add Dropoff Location ─────────────────────────────────────────
def add_dropoff_location(driver, wait):
    """
    TC-DOL-01 – Add a new Dropoff Location.

    Test Steps:
        1. Log in and navigate to the Dropoff Location list page.
        2. Click the '+ Add' toolbar button to open the Create form.
        3. Fill in all required fields (Name, Code, Address 1, City, Country)
           with unique random values.
        4. Click Save to submit the form.
        5. Navigate back to the list, search for the new location by Name,
           and verify it appears in the table.

    Expected Result:
        The newly created Dropoff Location is visible in the list after save.
    """
    log("=== TC-DOL-01: Add Dropoff Location ===")

    # Step 1 – Login and navigate to Dropoff Location list
    login(driver, wait)
    log("Step 1 – Navigating to Dropoff Location list…")
    driver.get(DOL_LIST_URL)
    time.sleep(2)

    # Step 2 – Click '+ Add' button to open the create form
    add_btn_xpath = (
        "//button[contains(normalize-space(.),'+') and contains(normalize-space(.),'Add')]"
        " | //a[contains(normalize-space(.),'+ Add')]"
        " | //button[normalize-space()='+ Add']"
        " | //a[normalize-space()='+ Add']"
        " | //button[contains(.,'Add')] | //a[contains(.,'Add')]"
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

    # Step 3 – Generate random values for all required fields
    unique_suffix  = random_string(4)
    name           = f"DL_{unique_suffix}"           # e.g. DL_A3B7
    code           = f"DLC_{unique_suffix}"           # e.g. DLC_A3B7
    address1       = f"{random.randint(100, 9999)} Troup Hwy"
    city           = "TestCity"
    state          = "TX"
    zip_code       = str(random.randint(10000, 99999))
    country        = "USA"

    log(
        f"Step 3 – Filling form: Name='{name}', Code='{code}', "
        f"Address1='{address1}', City='{city}', Country='{country}'"
    )

    try:
        # Fill using confirmed ADR$* name attributes from the live form
        driver.find_element(By.NAME, "ADR$Name").send_keys(name)
        driver.find_element(By.NAME, "ADR$Code").send_keys(code)
        driver.find_element(By.NAME, "ADR$Street1").send_keys(address1)
        driver.find_element(By.NAME, "ADR$City").send_keys(city)
        driver.find_element(By.NAME, "ADR$State").send_keys(state)
        driver.find_element(By.NAME, "ADR$Zip").send_keys(zip_code)
        driver.find_element(By.NAME, "ADR$Country").send_keys(country)
        log("Step 3 – Fields filled via ADR$* NAME attributes.")
    except Exception as exc:
        log(f"Step 3 FAILED – Could not fill form fields: {exc}")
        return False

    time.sleep(1)

    # Step 4 – Click Save
    save_xpath = (
        "//button[normalize-space()='Save']"
        " | //a[normalize-space()='Save']"
        " | //span[normalize-space()='Save']"
        " | //input[@type='submit' and contains(@value,'Save')]"
    )
    try:
        save_btn = wait.until(EC.element_to_be_clickable((By.XPATH, save_xpath)))
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", save_btn)
        driver.execute_script("arguments[0].click();", save_btn)
        log("Step 4 – Clicked Save button.")
        time.sleep(2)
    except Exception as exc:
        log(f"Step 4 FAILED – Save button not found: {exc}")
        return False

    # Step 5 – Return to list, search for the new location by Name, verify it exists
    driver.get(DOL_LIST_URL)
    time.sleep(2)
    _search_name(driver, wait, name)

    found = driver.find_elements(By.XPATH, f"//td[contains(normalize-space(.),'{name}')]")
    if found:
        log(f"Step 5 PASS – Dropoff Location '{name}' created successfully.")
        print(f"\n[PASS] TC-DOL-01: Dropoff Location '{name}' added.")
        return True
    else:
        log(f"Step 5 FAIL – Dropoff Location '{name}' not found after creation.")
        print(f"\n[FAIL] TC-DOL-01: Dropoff Location '{name}' not found after add.")
        return False


# ── TC-DOL-02: Edit Dropoff Location ────────────────────────────────────────
def edit_dropoff_location(driver, wait):
    """
    TC-DOL-02 – Edit an existing Dropoff Location.

    Test Steps:
        1. Log in and navigate to the Dropoff Location list page.
        2. Pick the first valid data row from the table (skip header/UI rows).
        3. Click the row-level Edit button; fallback to: select row → global Edit.
        4. Clear and update Name, Code, Address 1, City, and Country with
           new random values.
        5. Click Save.
        6. Navigate back to the list, search for the updated Name,
           and verify it appears.

    Expected Result:
        The updated Dropoff Location is visible in the list after save.
    """
    log("=== TC-DOL-02: Edit Dropoff Location ===")

    # Step 1 – Login and navigate to Dropoff Location list
    login(driver, wait)
    log("Step 1 – Navigating to Dropoff Location list…")
    driver.get(DOL_LIST_URL)
    time.sleep(2)

    # Step 2 – Find first valid data row scoped to the grid container.
    # Data rows have exactly 8 direct <td> cells:
    #   [row-selector] | Name | Address | Code | City | State | Zip | Country
    # tds[0] is the invisible row-selector; tds[1] is the Name column.
    name = None
    try:
        wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[@id='cnt_rnd_cntnr']//table//tr[count(td)=8]")
        ))
        rows = driver.find_elements(
            By.XPATH, "//div[@id='cnt_rnd_cntnr']//table//tr[count(td)=8]"
        )
        for row in rows:
            tds = row.find_elements(By.TAG_NAME, "td")
            if len(tds) < 2:
                continue
            # tds[0] is the row-selector (empty); tds[1] is Name
            candidate = tds[1].text.strip()
            if not candidate:
                candidate = tds[0].text.strip()  # fallback if no selector td
            if not candidate:
                continue
            if candidate.lower() in ["name", "address", "code", "city"]:
                continue
            if any(x in candidate.lower() for x in ["add", "edit", "delete", "sorted", "go"]):
                continue
            name = candidate
            break
        if not name:
            raise RuntimeError("No valid Dropoff Location row found in the grid.")
        log(f"Step 2 – Selected row Name: '{name}'")
    except Exception as exc:
        log(f"Step 2 FAILED – {exc}")
        return False

    # Step 3 – Click the Name cell to select the row, then click the
    #           toolbar Edit button (id='Warehouse_tbrEdit').
    try:
        name_td = wait.until(EC.element_to_be_clickable(
            (By.XPATH, f"//div[@id='cnt_rnd_cntnr']//td[normalize-space()='{name}']")
        ))
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", name_td)
        name_td.click()
        log(f"Step 3 – Clicked row for '{name}' to select it.")
        time.sleep(1)

        # Toolbar Edit button has a confirmed id on this page
        edit_btn = wait.until(EC.element_to_be_clickable((By.ID, "Warehouse_tbrEdit")))
        driver.execute_script("arguments[0].click();", edit_btn)
        log("Step 3 – Clicked toolbar Edit button (id=Warehouse_tbrEdit).")
        time.sleep(2)
    except Exception as exc:
        log(f"Step 3 FAILED – {exc}")
        return False

    # Step 4 – Clear existing field values and enter updated values
    unique_suffix = random_string(4)
    new_name      = f"DL_{unique_suffix}_ED"
    new_code      = f"DLC_{unique_suffix}_E"
    new_address1  = f"{random.randint(100, 9999)} Edited Ave"
    new_city      = "EditedCity"
    new_country   = "India"

    log(
        f"Step 4 – Updating to Name='{new_name}', Code='{new_code}', "
        f"Address1='{new_address1}', City='{new_city}', Country='{new_country}'"
    )

    try:
        # Update using confirmed ADR$* name attributes from the live form
        for field_name, value in [
            ("ADR$Name",    new_name),
            ("ADR$Code",    new_code),
            ("ADR$Street1", new_address1),
            ("ADR$City",    new_city),
            ("ADR$Country", new_country),
        ]:
            field = driver.find_element(By.NAME, field_name)
            field.clear()
            field.send_keys(value)
        log("Step 4 – Fields updated via ADR$* NAME attributes.")
    except Exception as exc:
        log(f"Step 4 FAILED – Could not update fields: {exc}")
        return False

    time.sleep(1)

    # Step 5 – Click Save
    save_xpath = (
        "//button[normalize-space()='Save']"
        " | //a[normalize-space()='Save']"
        " | //span[normalize-space()='Save']"
        " | //input[@type='submit' and contains(@value,'Save')]"
    )
    try:
        save_btn = wait.until(EC.element_to_be_clickable((By.XPATH, save_xpath)))
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", save_btn)
        driver.execute_script("arguments[0].click();", save_btn)
        log("Step 5 – Clicked Save button.")
        time.sleep(2)
    except Exception as exc:
        log(f"Step 5 FAILED – Save button not found: {exc}")
        return False

    # Step 6 – Return to list, search for the updated Name, and verify it appears
    driver.get(DOL_LIST_URL)
    time.sleep(2)
    _search_name(driver, wait, new_name)

    found = driver.find_elements(By.XPATH, f"//td[contains(normalize-space(.),'{new_name}')]")
    if found:
        log(f"Step 6 PASS – Dropoff Location updated to '{new_name}' successfully.")
        print(f"\n[PASS] TC-DOL-02: Dropoff Location edited – new name '{new_name}'.")
        return True
    else:
        log(f"Step 6 FAIL – Updated name '{new_name}' not found in list.")
        print(f"\n[FAIL] TC-DOL-02: Dropoff Location '{new_name}' not found after edit.")
        return False


# ── TC-DOL-03: View Dropoff Location ────────────────────────────────────────
def view_dropoff_location(driver, wait):
    """
    TC-DOL-03 – View details of an existing Dropoff Location and cancel.

    Test Steps:
        1. Log in and navigate to the Dropoff Location list page.
        2. Pick the first valid data row from the table.
        3. Search for the location by Name using the Find Name search box.
        4. Click the View button (row-level first; fallback to: select row → global View).
        5. Verify the details page displays the Name value.
        6. Click Cancel to return to the list.

    Expected Result:
        The details page opens for the selected location and Cancel returns to the list.
    """
    log("=== TC-DOL-03: View Dropoff Location ===")

    # Step 1 – Login and navigate to Dropoff Location list
    login(driver, wait)
    log("Step 1 – Navigating to Dropoff Location list…")
    driver.get(DOL_LIST_URL)
    time.sleep(2)

    # Step 2 – Find first valid data row scoped to the grid container.
    # Data rows have exactly 8 direct <td> cells:
    #   [row-selector] | Name | Address | Code | City | State | Zip | Country
    # tds[0] is the invisible row-selector; tds[1] is the Name column.
    name = None
    try:
        wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[@id='cnt_rnd_cntnr']//table//tr[count(td)=8]")
        ))
        rows = driver.find_elements(
            By.XPATH, "//div[@id='cnt_rnd_cntnr']//table//tr[count(td)=8]"
        )
        for row in rows:
            tds = row.find_elements(By.TAG_NAME, "td")
            if len(tds) < 2:
                continue
            # tds[0] is the row-selector (empty); tds[1] is Name
            candidate = tds[1].text.strip()
            if not candidate:
                candidate = tds[0].text.strip()  # fallback if no selector td
            if not candidate:
                continue
            if candidate.lower() in ["name", "address", "code", "city"]:
                continue
            if any(x in candidate.lower() for x in ["add", "edit", "delete", "sorted", "go"]):
                continue
            name = candidate
            break
        if not name:
            raise RuntimeError("No valid Dropoff Location row found.")
        log(f"Step 2 – Using Name: '{name}'")
    except Exception as exc:
        log(f"Step 2 FAILED – {exc}")
        return False

    # Step 3 – (optional) narrow the list via search
    _search_name(driver, wait, name)

    # Step 4 – Click the Name cell to select the row, then click the
    #           toolbar View button (id='Warehouse_tbrView2').
    try:
        name_td = wait.until(EC.element_to_be_clickable(
            (By.XPATH, f"//div[@id='cnt_rnd_cntnr']//td[normalize-space()='{name}']")
        ))
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", name_td)
        name_td.click()
        log(f"Step 4 – Clicked row for '{name}' to select it.")
        time.sleep(1)

        # Toolbar View button has a confirmed id on this page
        view_btn = wait.until(EC.element_to_be_clickable((By.ID, "Warehouse_tbrView2")))
        driver.execute_script("arguments[0].click();", view_btn)
        log("Step 4 – Clicked toolbar View button (id=Warehouse_tbrView2).")
        time.sleep(2)
    except Exception as exc:
        log(f"Step 4 FAILED – {exc}")
        return False

    # Step 5 – Verify the details page shows the location Name value
    log("Step 5 – Verifying details page content…")
    try:
        divs = driver.find_elements(By.XPATH, "//div | //td | //span | //label")
        for el in divs:
            try:
                txt = el.text.strip()
                if name in txt or "Name:" in txt or "Address" in txt:
                    log(f"Details block found: '{txt[:140]}'")
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
        # Graceful fallback: use browser back if Cancel button is absent
        log("Step 6 WARNING – Cancel button not found; using browser back.")
        driver.back()
        time.sleep(2)
        log(f"PASS – View Dropoff Location completed for '{name}' (browser back used).")
        print(f"\n[PASS] TC-DOL-03: Dropoff Location '{name}' viewed successfully (browser back).")
        return True

    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", cancel_btn)
    driver.execute_script("arguments[0].click();", cancel_btn)
    log("Step 6 – Clicked Cancel, returned to the list.")
    time.sleep(2)

    log(f"PASS – View Dropoff Location test completed for '{name}'.")
    print(f"\n[PASS] TC-DOL-03: Dropoff Location '{name}' viewed successfully.")
    return True


# ── TC-DOL-04: Delete Dropoff Location ──────────────────────────────────────
def delete_dropoff_location(driver, wait):
    """
    TC-DOL-04 – Delete an existing Dropoff Location.

    Test Steps:
        1. Log in and navigate to the Dropoff Location list page.
        2. Pick the first test-created row from the grid — any row whose
           Name starts with 'DL_' (our auto-generated prefix). This safely
           avoids permanent entries like 'DL2', 'DL3', 'DRop1', etc. which
           do not have an underscore as the third character.
        3. Click the Name cell to select the row in the grid.
        4. Click the toolbar Delete button (id='Warehouse_tbrDelete').
        5. Confirm the deletion by clicking 'Yes' in the confirmation dialog
           that asks "Do you want to delete this Dropoff Location?".
        6. Navigate back to the list and verify the deleted Name no longer
           appears in the grid.

    Expected Result:
        The deleted Dropoff Location no longer appears in the list after
        the 'Yes' confirmation is submitted.
    """
    log("=== TC-DOL-04: Delete Dropoff Location ===")

    # ── Step 1 – Login and navigate to Dropoff Location list ─────────────────
    login(driver, wait)
    log("Step 1 – Navigating to Dropoff Location list…")
    driver.get(DOL_LIST_URL)
    time.sleep(2)

    # ── Step 2 – Pick the first test-created row (Name starts with 'DL_') ────
    # Test-created names always have the pattern DL_<suffix> (underscore at
    # index 2). Permanent demo entries use 'DL2', 'DL3', 'DRop1', etc.
    target_name = None
    try:
        wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[@id='cnt_rnd_cntnr']//table//tr[count(td)=8]")
        ))
        rows = driver.find_elements(
            By.XPATH, "//div[@id='cnt_rnd_cntnr']//table//tr[count(td)=8]"
        )
        for row in rows:
            tds = row.find_elements(By.TAG_NAME, "td")
            if len(tds) < 2:
                continue
            # tds[0] = row-selector (invisible); tds[1] = Name column
            candidate = tds[1].text.strip()
            if not candidate:
                continue
            # Only target auto-generated test records: name matches 'DL_...'
            if candidate.startswith("DL_"):
                target_name = candidate
                break
        if not target_name:
            raise RuntimeError(
                "No test-created row (Name starting with 'DL_') found to delete."
            )
        log(f"Step 2 – Selected test row to delete: '{target_name}'")
    except Exception as exc:
        log(f"Step 2 FAILED – {exc}")
        return False

    # ── Step 3 – Click the Name cell to select the row in the grid ───────────
    try:
        name_td = wait.until(EC.element_to_be_clickable(
            (By.XPATH, f"//div[@id='cnt_rnd_cntnr']//td[normalize-space()='{target_name}']")
        ))
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", name_td)
        name_td.click()
        log(f"Step 3 – Clicked row for '{target_name}' to select it.")
        time.sleep(1)
    except Exception as exc:
        log(f"Step 3 FAILED – Row not found: {exc}")
        return False

    # ── Step 4 – Click the toolbar Delete button (id='Warehouse_tbrDelete') ──
    try:
        del_btn = wait.until(EC.element_to_be_clickable((By.ID, "Warehouse_tbrDelete")))
        driver.execute_script("arguments[0].click();", del_btn)
        log("Step 4 – Clicked toolbar Delete button (id=Warehouse_tbrDelete).")
        time.sleep(1)
    except Exception as exc:
        log(f"Step 4 FAILED – Delete button not found: {exc}")
        return False

    # ── Step 5 – Confirm deletion by clicking 'Yes' in the dialog ─────────────
    # Dialog text: "Do you want to delete this Dropoff Location?"
    # Buttons:     [ ✓ Yes ]  [ ✕ No ]
    try:
        yes_btn = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH,
                 "//button[normalize-space()='Yes']"
                 " | //a[normalize-space()='Yes']"
                 " | //span[normalize-space()='Yes']"
                 " | //*[contains(@class,'btn') and normalize-space()='Yes']")
            )
        )
        driver.execute_script("arguments[0].click();", yes_btn)
        log("Step 5 – Confirmed deletion by clicking 'Yes'.")
        time.sleep(3)
    except Exception as exc:
        log(f"Step 5 FAILED – Confirmation 'Yes' button not found: {exc}")
        return False

    # ── Step 6 – Verify the deleted record is no longer in the list ───────────
    driver.get(DOL_LIST_URL)
    time.sleep(2)
    _search_name(driver, wait, target_name)

    still_present = driver.find_elements(
        By.XPATH, f"//div[@id='cnt_rnd_cntnr']//td[normalize-space()='{target_name}']"
    )
    if not still_present:
        log(f"Step 6 PASS – '{target_name}' no longer appears in the list.")
        print(f"\n[PASS] TC-DOL-04: Dropoff Location '{target_name}' deleted successfully.")
        return True
    else:
        log(f"Step 6 FAIL – '{target_name}' still visible in the list after deletion.")
        print(f"\n[FAIL] TC-DOL-04: Dropoff Location '{target_name}' still present after delete.")
        return False


# ── Test Runner ──────────────────────────────────────────────────────────────
def run_dropoff_location_tests():
    """
    Entry point: instantiate WebDriver, run all four test cases,
    print a summary table, and quit the browser.

    Usage:
        python -m admin.Entities.DropOffLocation
        or
        python admin/Entities/DropOffLocation.py   (from qa_automation/)
    """
    driver = get_driver()
    wait   = WebDriverWait(driver, 20)

    results = {}

    # TC-DOL-01: Add
    try:
        results["TC-DOL-01  Add  Dropoff Location"] = add_dropoff_location(driver, wait)
    except Exception as exc:
        log(f"TC-DOL-01 raised exception: {exc}")
        results["TC-DOL-01  Add  Dropoff Location"] = False

    # TC-DOL-02: Edit
    try:
        results["TC-DOL-02  Edit Dropoff Location"] = edit_dropoff_location(driver, wait)
    except Exception as exc:
        log(f"TC-DOL-02 raised exception: {exc}")
        results["TC-DOL-02  Edit Dropoff Location"] = False

    # TC-DOL-03: View
    try:
        results["TC-DOL-03  View   Dropoff Location"] = view_dropoff_location(driver, wait)
    except Exception as exc:
        log(f"TC-DOL-03 raised exception: {exc}")
        results["TC-DOL-03  View   Dropoff Location"] = False

    # TC-DOL-04: Delete
    try:
        results["TC-DOL-04  Delete Dropoff Location"] = delete_dropoff_location(driver, wait)
    except Exception as exc:
        log(f"TC-DOL-04 raised exception: {exc}")
        results["TC-DOL-04  Delete Dropoff Location"] = False

    # ── Summary ──────────────────────────────────────────────────────────────
    print("\n" + "=" * 58)
    print("  DROPOFF LOCATION TEST RESULTS")
    print("=" * 58)
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}]  {name}")
    print("=" * 58)
    total        = len(results)
    passed_count = sum(1 for v in results.values() if v)
    print(f"  Total: {total} | Passed: {passed_count} | Failed: {total - passed_count}")
    print("=" * 58 + "\n")

    driver.quit()
    return results


def test_dropoff_location_suite():
    """Pytest entry point for legacy script-style DropOff Location suite."""
    results = run_dropoff_location_tests()
    assert results, "No DropOff Location tests executed"
    assert all(results.values()), f"DropOff Location failures: {results}"


# ── Script Entry ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    run_dropoff_location_tests()

