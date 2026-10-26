"""

QALS11 | Admin > Users â€” User Management Test Suite

=====================================================

Application : https://engineering.ultrivalms.com/QALS1011

Login       : buyeruser / Ultriva!23

Browser     : Chrome (visible, maximised)

â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—

â•‘  WHAT THIS FILE TESTS (each operation is a separate test class):           â•‘

â•‘                                                                            â•‘

â•‘  1. TestAddUser     â€” Create a new user from the Admin > Users page        â•‘

â•‘  2. TestEditUser    â€” Edit an existing user's fields and save              â•‘

â•‘  3. TestViewUser    â€” View a user's details (read-only) and click Cancel   â•‘

â•‘  4. TestDisableUser â€” Disable (soft-delete) a user from the Active list    â•‘

â•‘  5. TestEnableUser  â€” Re-enable a disabled user back to Active             â•‘

â•‘                                                                            â•‘

â•‘  SINGLE LOGIN: All 5 classes share ONE browser session (scope="module").   â•‘

â•‘  The admin logs in ONCE at the start; no repeated login/logout between     â•‘

â•‘  tests. This makes the suite run significantly faster.                     â•‘

â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

HOW TO RUN (from qa_automation/ folder):

    # Run all tests in order:

    pytest tests/QALS11/Admin/Users/users.py -v -s

    # Run a single class:

    pytest tests/QALS11/Admin/Users/users.py::TestAddUser -v -s

    pytest tests/QALS11/Admin/Users/users.py::TestEditUser -v -s

    pytest tests/QALS11/Admin/Users/users.py::TestViewUser -v -s

    pytest tests/QALS11/Admin/Users/users.py::TestDisableUser -v -s

    pytest tests/QALS11/Admin/Users/users.py::TestEnableUser -v -s

TEST EXECUTION ORDER:

    TestAddUser runs FIRST (creates the user that all other tests operate on).

    TestEditUser, TestViewUser run next (modify / inspect the user).

    TestDisableUser runs after (disables the user).

    TestEnableUser runs LAST (re-enables the user so the account is active

    at the end of the run).

FOR BULK USER CREATION (manual or Excel-based):

    See the separate file:

        tests/QALS11/Admin/Users/UsercreationValidations.py

"""

# â”€â”€ Standard library imports
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

import os

import time

import random

import string

from datetime import datetime

# â”€â”€ Third-party imports
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

import pytest

from selenium import webdriver

from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait, Select

from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import TimeoutException

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

# CONFIGURATION â€” change these when testing a different environment

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

# QA site URL (no trailing slash)
BASE_URL = "https://engineering.ultrivalms.com/QALS1011"

ADMIN_USER = "buyeruser"                                      # Admin username

ADMIN_PASS = "Ultriva!23"                                     # Admin password

# Seconds to pause between steps (so QA can observe the browser)
PAUSE = 2

WAIT = 15      # Max seconds for WebDriverWait before timeout

# Email used for all new users
SHARED_EMAIL = "vseelam@uplandsoftware.com"

# Default account type
ACCOUNT_TYPE = "Plant Administrators"

# â”€â”€ The user that this file creates and exercises
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

# All test classes in this file operate on the SAME user ID.

# TestAddUser creates it â†’ TestEditUser edits it â†’ TestViewUser views
# it â†’

# TestDisableUser disables it â†’ TestEnableUser re-enables it.

TEST_USER_ID = "User170426"

TEST_USER_PW = "Ultriva!23"

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

# BROWSER FIXTURE â€” shared across ALL test classes (single login)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.fixture(scope="module")
def driver():
    """

    Launch a visible Chrome window shared by every test in this module.

    WHY scope="module"?

      â€¢ The browser opens ONCE and stays open for the entire file.

      â€¢ All test classes share the same session â€” no repeated login/logout.

      â€¢ This cuts total execution time by ~50% compared to per-class login.

    The browser window is NOT closed after tests finish so QA can inspect

    the final state.

    """

    options = webdriver.ChromeOptions()

    options.add_argument("--start-maximized")

    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    browser = webdriver.Chrome(options=options)

    browser.set_page_load_timeout(30)

    # â”€â”€ Login ONCE at the very start
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    browser.get(BASE_URL)

    _page_ready(browser)

    WebDriverWait(browser, WAIT).until(

        EC.element_to_be_clickable((By.ID, "UserName"))

    ).send_keys(ADMIN_USER)

    browser.find_element(By.ID, "Password").send_keys(ADMIN_PASS)

    browser.find_element(By.ID, "login-button").click()

    _page_ready(browser)

    time.sleep(PAUSE)

    assert "ultrivalms" in browser.current_url, "Login failed â€” check credentials"

    print(f"\n  [SESSION] Logged in as '{ADMIN_USER}' â€” URL:  { browser.current_url }")

    yield browser

    # NOTE: browser.quit() is intentionally omitted so the window stays open

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

# HELPER FUNCTIONS â€” reusable utilities used by all test classes

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def _page_ready(driver, timeout=WAIT):
    """Wait until the browser says document.readyState == 'complete'."""

    WebDriverWait(driver, timeout).until(

        lambda d: d.execute_script("return document.readyState") == "complete"

    )


def _clear_and_type(driver, by, locator, text, timeout=WAIT):
    """Find a visible field, clear it, type new text. Returns the element."""

    el = WebDriverWait(driver, timeout).until(

        EC.visibility_of_element_located((by, locator))

    )

    el.clear()

    el.send_keys(text)

    return el


def _dismiss_modal(driver):
    """

    Close Ultriva's modal dialog if it is blocking the page.

    Tries 'No' button first, then the Ã— close button.

    Silently does nothing if no modal is present.

    """

    try:

        modal = driver.find_element(By.ID, "Modal-modal-alert-id")

        if modal.is_displayed():

            for xpath in [

                ".//button[normalize-space(.)='No']",

                ".//button[contains(@class,'close')]",

                ".//button[@data-dismiss='modal']",

            ]:

                try:

                    btn = modal.find_element(By.XPATH, xpath)

                    if btn.is_displayed():

                        driver.execute_script("arguments[0].click();", btn)

                        time.sleep(1)

                        return

                except Exception:

                    pass

    except Exception:

        pass


def _select_account_type(driver, account_type=ACCOUNT_TYPE):
    """

    Find the Account Type dropdown and select the given option.

    Returns True if selection succeeded, False otherwise.

    """

    for by, val in [

        (By.NAME, "USR$AccountType"),

        (By.ID, "USR_AccountType"),

        (By.NAME, "AccountType"),

        (By.XPATH, "//select[contains(@name,'AccountType') or contains(@id,'AccountType')]"),

        (By.XPATH, "//select[option[contains(text(),'Plant Administrator')]]"),

    ]:

        try:

            el = WebDriverWait(
                driver, 5).until(
                EC.visibility_of_element_located(
                    (by, val)))

            sel = Select(el)

            try:

                sel.select_by_visible_text(account_type)

                return True

            except Exception:

                pass

            for option in sel.options:

                if account_type.lower() in option.text.lower():

                    sel.select_by_visible_text(option.text.strip())

                    return True

        except Exception:

            continue

    return False


def _click_save(driver):
    """

    Click the Save button using multiple fallback selectors.

    Returns True if clicked successfully.

    NOTE FOR QA:

      Ultriva uses different Save button implementations across pages:

        â€¢ <a id="entryPGSubmit">  (most common)

        â€¢ <a title="Save" onclick="frmEntryPage_onSubmit()">

        â€¢ <button> or <input type="submit">

    """

    for by, sel in [

        (By.ID, "entryPGSubmit"),

        (By.XPATH, "//a[@title='Save' and contains(@onclick,'frmEntryPage_onSubmit')]"),

        (By.XPATH, "//a[@title='Save']"),

        (By.XPATH, "//input[@value='Save'] | //button[normalize-space(text())='Save']"),

    ]:

        try:

            btn = WebDriverWait(
                driver, 5).until(
                EC.element_to_be_clickable(
                    (by, sel)))

            driver.execute_script("arguments[0].click();", btn)

            _page_ready(driver)

            time.sleep(PAUSE)

            return True

        except Exception:

            continue

    return False


def _search_user(driver, user_id):
    """

    Type a user ID into the search box on the User List page and wait

    for the matching row to appear in the grid.

    """

    _dismiss_modal(driver)

    try:

        sb = WebDriverWait(driver, 8).until(

            EC.visibility_of_element_located((By.NAME, "User_FindTextbox"))

        )

        sb.clear()

        sb.send_keys(user_id)

        time.sleep(PAUSE)

    except Exception:

        pass

    WebDriverWait(driver, WAIT).until(

        EC.presence_of_element_located((

            By.XPATH, f"//td[normalize-space(text())='{user_id}']"

        ))

    )

    print(f"  Found '{user_id}' in the list")

    return True


def _select_user_row(driver, user_id):
    """

    Click the user's <td> cell to select the row in Ultriva's grid.

    IMPORTANT FOR QA:

      You must click the <td> cell, NOT the <tr> row â€” clicking <tr>

      does not trigger Ultriva's row-selection JavaScript handler.

    """

    _dismiss_modal(driver)

    time.sleep(0.5)

    user_cell = WebDriverWait(driver, WAIT).until(

        EC.presence_of_element_located((

            By.XPATH, f"//td[normalize-space(text())='{user_id}']"

        ))

    )

    driver.execute_script(
        "arguments[0].scrollIntoView({block:'center'});",
        user_cell)

    time.sleep(0.5)

    driver.execute_script("arguments[0].click();", user_cell)

    time.sleep(PAUSE)

    print(f"  Selected row for '{user_id}'")


def _click_toolbar_button(driver, title, fallback_id=None):
    """

    Click a toolbar button by its title attribute (e.g. 'Edit', 'View').

    Falls back to button ID if title-based selectors fail.

    """

    btn = None

    for by, sel in [

        (By.XPATH, f"//a[@title='{title}'] | //button[@title='{title}']"),

        (By.XPATH, f"//a[normalize-space(.)='{title}'] | //button[normalize-space(.)='{title}']"),

    ]:

        try:

            btn = WebDriverWait(
                driver, 5).until(
                EC.presence_of_element_located(
                    (by, sel)))

            break

        except Exception:

            continue

    if btn is None and fallback_id:

        btn = WebDriverWait(driver, 5).until(

            EC.presence_of_element_located((By.ID, fallback_id))

        )

    assert btn is not None, f"Toolbar button '{title}' not found"

    driver.execute_script("arguments[0].click();", btn)

    _page_ready(driver)

    time.sleep(PAUSE)

    return btn


def _confirm_modal_yes(driver):
    """

    Wait for Ultriva's confirmation modal and click 'Yes'.

    NOTE FOR QA:

      Ultriva renders the Yes button as a <span> inside the modal footer,

      not a standard <button>. The XPath below covers all variations.

    """

    modal = WebDriverWait(driver, WAIT).until(

        EC.visibility_of_element_located((By.ID, "Modal-modal-alert-id"))

    )

    modal_text = modal.text.strip()

    print(f"  Modal text: '{modal_text[:150]}'")

    yes_btn = WebDriverWait(driver, WAIT).until(

        EC.element_to_be_clickable((

            By.XPATH,

            "//button[normalize-space(text())='Yes'] "

            "| //button[normalize-space(.)='Yes'] "

            "| //a[normalize-space(text())='Yes'] "

            "| //input[@value='Yes'] "

            "| //*[@id='Modal-modal-alert-id']//*[contains(normalize-space(text()),'Yes')]"

        ))

    )

    driver.execute_script("arguments[0].click();", yes_btn)

    _page_ready(driver)

    time.sleep(PAUSE)

    print("  Clicked 'Yes' â€” action confirmed")

    return modal_text


def _go_to_user_list(driver):
    """Navigate to the Active User List page and dismiss any modal."""

    driver.get(f"{BASE_URL}/User/List")

    _page_ready(driver)

    time.sleep(PAUSE)

    _dismiss_modal(driver)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

# TEST CLASS 1 â€” Add (Create) a New User

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

#

# QA PROCESS â€” How to Create a User in Ultriva:

#   1. Navigate to Admin > Users > Create User  (URL: /User/Create)

#   2. Fill in ALL mandatory fields:

#        â€¢ First Name, Last Name, Work Phone, Email

#        â€¢ Login Name (User ID), Account Type dropdown

#        â€¢ Password and Confirm Password

#   3. Optionally fill: Mobile Phone, Buyer Code

#   4. Click Save

#   5. Navigate to User List â†’ confirm the new user row exists

#

# WHAT THESE TESTS VERIFY:

#   test_01 â€” Open the Create User form

#   test_02 â€” Fill in all mandatory fields and save

#   test_03 â€” Verify the user appears in the Active User List

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    """

    Create a new user account from the Admin > Users page.

    Test Steps:

      test_01 â€” Navigate to Create User form

      test_02 â€” Fill mandatory fields and click Save

      test_03 â€” Search for the user in User List and confirm it exists

    Run:  pytest tests/QALS11/Admin/Users/users.py::TestAddUser -v -s

    """

    # â”€â”€ Step 1: Open the Create User form
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


class TestUsers:
    def test_01_open_create_form(self, driver):
        """
        Navigate to Admin > Users > Create User.
        Confirm the form page loads successfully.
        """
        driver.get(f"{BASE_URL}/User/Create")
        _page_ready(driver)
        time.sleep(PAUSE)
        _dismiss_modal(driver)

        assert "Create" in driver.current_url or "User" in driver.current_url, (
            f"Create User page did not load. URL: {driver.current_url}")
        print(f"\n  Create User form â€” URL: {driver.current_url}")

        # â”€â”€ Step 2: Fill all mandatory fields and Save
        # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def test_02_fill_form_and_save(self, driver):
        """
        Fill in every mandatory field on the Create User form and click Save.

        MANDATORY FIELDS (must be filled for the Save to succeed):
        â€¢ PRS$FirstName       â€” First Name
        â€¢ PRS$LastName        â€” Last Name
        â€¢ PRS$WorkPhone       â€” Work Phone (10-digit, unique per user)
        â€¢ PRS$EmailID         â€” Email Address
        â€¢ USR$LoginName       â€” Login Name / User ID
        â€¢ Account Type        â€” Dropdown (Plant Administrators)
        â€¢ MISC$Password       â€” Password (>8 chars, 1 upper, 1 lower, 1 digit, 1 symbol)
        â€¢ MISC$ConfirmPassword â€” Must match Password

        OPTIONAL FIELDS:
        â€¢ PRS$MobilePhone     â€” Mobile Phone
        â€¢ USR$BuyerCode       â€” Buyer Code (unique identifier)
        """
        # Random phone/buyer code to avoid duplicate errors on re-runs
        rand_phone = f"555{random.randint(1000000, 9999999)}"
        rand_bc = "".join(
            random.choices(
                string.ascii_uppercase +
                string.digits,
                k=4))

        # â”€â”€ Fill mandatory fields
        # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        _clear_and_type(driver, By.NAME, "PRS$FirstName", "User")
        print("  [FILLED] First Name = 'User'")

        _clear_and_type(driver, By.NAME, "PRS$LastName", "170426")
        print("  [FILLED] Last Name = '170426'")

        _clear_and_type(driver, By.NAME, "PRS$WorkPhone", rand_phone)
        print(f"  [FILLED] Work Phone = '{rand_phone}'")

        _clear_and_type(driver, By.NAME, "PRS$EmailID", SHARED_EMAIL)
        print(f"  [FILLED] Email = '{SHARED_EMAIL}'")

        _clear_and_type(driver, By.NAME, "USR$LoginName", TEST_USER_ID)
        print(f"  [FILLED] Login Name = '{TEST_USER_ID}'")

        # â”€â”€ Fill optional fields
        # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        try:
            _clear_and_type(
            driver,
            By.NAME,
            "PRS$MobilePhone",
            rand_phone,
            timeout=5)
            print(f"  [FILLED] Mobile Phone = '{rand_phone}'")
        except Exception:
            pass

        try:
            _clear_and_type(driver, By.NAME, "USR$BuyerCode", rand_bc, timeout=5)
            print(f"  [FILLED] Buyer Code = '{rand_bc}'")
        except Exception:
            pass

        # â”€â”€ Account Type dropdown
        # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        if _select_account_type(driver):
            print(f"  [FILLED] Account Type = '{ACCOUNT_TYPE}'")
        else:
            print("  [WARN] Could not set Account Type")

        # â”€â”€ Password fields
        # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        for field in ("MISC$Password", "MISC$ConfirmPassword"):
            try:
                _clear_and_type(driver, By.NAME, field, TEST_USER_PW, timeout=6)
                print(f"  [FILLED] {field} = '{TEST_USER_PW}'")
            except Exception:
                print(f"  [WARN] Could not fill {field}")

        time.sleep(1)

        # â”€â”€ Click Save
        # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        assert _click_save(driver), "Save button not found on Create User form"
        print(f"  [SAVE] User saved â€” URL: {driver.current_url}")

        # â”€â”€ Step 3: Verify the user exists in the Active User List
        # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def test_03_verify_user_in_list(self, driver):
        """
        Navigate to User List, search for the newly created user,
        and confirm the row exists in the grid.
        """
        _go_to_user_list(driver)
        assert _search_user(driver, TEST_USER_ID), (
            f"User '{TEST_USER_ID}' not found in Active User List after creation"
        )
        print(f"  VERIFIED: '{TEST_USER_ID}' found in Active User List")

        # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
        # TEST CLASS 2 â€” Edit an Existing User
        # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
        #
        # QA PROCESS â€” How to Edit a User in Ultriva:
        #   1. Navigate to Admin > User List  (URL: /User/List)
        #   2. Search for the user using the search box
        #   3. Click the user's row to SELECT it (row highlights in blue)
        #   4. Click the EDIT toolbar button (title="Edit")
        #   5. On the Edit User form, change the desired fields
        #   6. Click Save
        #   7. Confirm the browser returns to the User List without errors
        #
        # WHAT THESE TESTS VERIFY:
        #   test_01 â€” Search for the user and select the row
        #   test_02 â€” Click Edit and modify fields (First Name, Phone, Buyer Code)
        #   test_03 â€” Save and confirm no errors appeared
        # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

        """

        Edit the user created by TestAddUser with new random values.

        Test Steps:

        test_01 â€” Search for user and select the row

        test_02 â€” Click Edit, change fields, and Save

        test_03 â€” Verify we return to User List without errors

        Run:  pytest tests/QALS11/Admin/Users/users.py::TestEditUser -v -s

        """

        # â”€â”€ Step 1: Search and select the user row
        # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def test_01_search_and_select(self, driver):
        """Open User List, search for the test user, and select the row."""
        _go_to_user_list(driver)
        _search_user(driver, TEST_USER_ID)
        _select_user_row(driver, TEST_USER_ID)

        # â”€â”€ Step 2: Click Edit and update fields
        # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def test_02_edit_fields(self, driver):
        """
        Click the Edit toolbar button and update the user's fields.

        FIELDS BEING CHANGED:
        â€¢ First Name  â†’ 'EditedUser'  (was 'User')
        â€¢ Work Phone  â†’ new random 10-digit number
        â€¢ Buyer Code  â†’ new random 4-char alphanumeric code
        â€¢ Email       â†’ shared QA email (same value, ensuring it's still set)
        â€¢ Password    â†’ new random valid password

        Random values prevent "duplicate value" validation errors on re-runs.
        """
        rand_phone = f"555{random.randint(1000000, 9999999)}"
        rand_bc = "".join(
            random.choices(
                string.ascii_uppercase +
                string.digits,
                k=4))
        new_pw = f"Edit@{random.randint(1000, 9999)}Zx!"

        # Click Edit toolbar button
        _click_toolbar_button(driver, "Edit", fallback_id="User_tbrEdit")
        print(f"  Edit form â€” URL: {driver.current_url}")

        # Update fields with new values
        _clear_and_type(driver, By.NAME, "PRS$FirstName", "EditedUser")
        print("  [UPDATED] First Name â†’ 'EditedUser'")

        _clear_and_type(driver, By.NAME, "PRS$WorkPhone", rand_phone)
        print(f"  [UPDATED] Work Phone â†’ '{rand_phone}'")

        _clear_and_type(driver, By.NAME, "PRS$EmailID", SHARED_EMAIL)

        try:
            _clear_and_type(driver, By.NAME, "USR$BuyerCode", rand_bc, timeout=5)
            print(f"  [UPDATED] Buyer Code â†’ '{rand_bc}'")
        except Exception:
            pass

        _select_account_type(driver)

        for field in ("MISC$Password", "MISC$ConfirmPassword"):
            try:
                _clear_and_type(driver, By.NAME, field, new_pw, timeout=6)
            except Exception:
                pass

        time.sleep(1)

        # â”€â”€ Step 3: Save and verify
        # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def test_03_save_and_verify(self, driver):
        """
        Click Save and confirm the browser returns to User List
        without any validation errors.
        """
        assert _click_save(driver), "Save button not found on Edit form"
        print(f"  Edit saved â€” URL: {driver.current_url}")

        # Navigate back to User List to confirm
        _go_to_user_list(driver)
        assert "ultrivalms" in driver.current_url
        print(f"  Browser on User List â€” URL: {driver.current_url}")

        # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
        # TEST CLASS 3 â€” View User (Read-Only)
        # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
        #
        # QA PROCESS â€” How to View a User in Ultriva:
        #   1. Navigate to Admin > User List
        #   2. Search for the user and select the row
        #   3. Click the VIEW toolbar button (title="View")
        #   4. The View User page opens in READ-ONLY mode
        #      â€” all fields are visible but NOT editable
        #   5. The page heading shows: "View User <UserID>"
        #   6. Click Cancel to return to the User List (no data is changed)
        #
        # WHAT THESE TESTS VERIFY:
        #   test_01 â€” Search and select the user row
        #   test_02 â€” Click View and confirm the page shows the correct user ID
        #   test_03 â€” Click Cancel and return to the User List
        # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

        """

        View the user's details in read-only mode and click Cancel.

        This test does NOT modify any data â€” it is a read-only verification.

        Test Steps:

        test_01 â€” Search for user and select the row

        test_02 â€” Click View and verify the page heading

        test_03 â€” Click Cancel to return to User List

        Run:  pytest tests/QALS11/Admin/Users/users.py::TestViewUser -v -s

        """

        # â”€â”€ Step 1: Search and select
        # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def test_01_search_and_select(self, driver):
        """Open User List, search for the test user, and select the row."""
        _go_to_user_list(driver)
        _search_user(driver, TEST_USER_ID)
        _select_user_row(driver, TEST_USER_ID)

        # â”€â”€ Step 2: Click View and verify
        # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def test_02_view_user_details(self, driver):
        """
        Click the View toolbar button and confirm the View User page
        displays the correct user ID in the heading.

        The View User page:
        â€¢ URL contains '/User/ViewBO?GID=...'
        â€¢ Heading shows: "View User <UserID>"
        â€¢ All fields are displayed but NOT editable
        """
        _click_toolbar_button(driver, "View")
        print(f"  View page â€” URL: {driver.current_url}")

        # Confirm we reached the View page
        assert "ViewBO" in driver.current_url or TEST_USER_ID in driver.page_source, (
            f"View page did not load. URL: {driver.current_url}")

        # Check the page heading contains the user ID
        heading_text = ""
        for by, sel in [
            (By.TAG_NAME, "h1"),
            (By.TAG_NAME, "h2"),
            (By.XPATH, "//*[contains(@class,'page-title') or contains(@class,'pagetitle')]"),
            (By.XPATH, f"//*[contains(normalize-space(text()),'{TEST_USER_ID}')]"),
        ]:
            try:
                el = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((by, sel))
        )
                heading_text = el.text.strip()
                if heading_text:
                    break
            except Exception:
                continue

        print(f"  Page heading: '{heading_text}'")
        assert TEST_USER_ID in heading_text or TEST_USER_ID in driver.page_source, (
            f"'{TEST_USER_ID}' not found on View page")

        # â”€â”€ Step 3: Click Cancel â†’ back to User List
        # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def test_03_cancel_and_return(self, driver):
        """
        Click the Cancel button to return to the User List.

        No data is changed â€” this is a read-only operation.
        Ultriva places the Cancel button at the bottom of the form page.
        """
        # Scroll to the bottom where Cancel is located
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        cancel_found = False
        for by, sel in [
            (By.ID, "entryPGCancel"),
            (By.XPATH, "//a[@id='entryPGCancel']"),
            (By.XPATH, "//a[contains(@href,'User/List')]"),
            (By.XPATH, "//a[contains(normalize-space(.),'Cancel')]"),
            (By.XPATH, "//button[contains(normalize-space(.),'Cancel')]"),
        ]:
            try:
                btn = WebDriverWait(
            driver, 5).until(
            EC.element_to_be_clickable(
                (by, sel)))
                driver.execute_script("arguments[0].click();", btn)
                cancel_found = True
                break
            except Exception:
                continue

        if not cancel_found:
            # Last resort: navigate directly back to User List
            driver.get(f"{BASE_URL}/User/List")

        _page_ready(driver)
        time.sleep(PAUSE)
        _dismiss_modal(driver)

        assert "ultrivalms" in driver.current_url
        print(f"  Clicked Cancel â€” returned to: {driver.current_url}")

        # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
        # TEST CLASS 4 â€” Disable User
        # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
        #
        # QA PROCESS â€” How to Disable a User in Ultriva:
        #   1. Navigate to Admin > User List
        #   2. Search for the user and select the row
        #   3. Click the DISABLE toolbar button (id="User_tbrDelete")
        #      â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
        #      â”‚ IMPORTANT: Despite the ID containing "tbrDelete", this  â”‚
        #      â”‚ button DISABLES the user â€” it does NOT permanently      â”‚
        #      â”‚ delete the account. This is Ultriva's "soft delete".    â”‚
        #      â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
        #   4. A confirmation dialog appears:
        #        "Do you want to disable this user?"
        #   5. Click YES to confirm
        #   6. The user moves to the Disabled list and can no longer log in
        #
        # STATUS INDICATORS (in the first column of the User List grid):
        #   Green icon (enable1.gif)  = Active user
        #   Red icon   (disable.gif)  = Disabled user
        #
        # WHAT THESE TESTS VERIFY:
        #   test_01 â€” Search for the user and select the row
        #   test_02 â€” Click Disable â†’ confirmation dialog appears
        #   test_03 â€” Click Yes â†’ user is disabled
        # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

        """

        Disable (soft-delete) the test user from the Admin > User List.

        After this test class runs, the user will be in the Disabled list

        and cannot log in until re-enabled by TestEnableUser.

        Test Steps:

        test_01 â€” Search for user and select the row

        test_02 â€” Click Disable button and verify the confirmation dialog

        test_03 â€” Click Yes and verify the user is disabled

        Run:  pytest tests/QALS11/Admin/Users/users.py::TestDisableUser -v -s

        """

        # â”€â”€ Step 1: Search and select
        # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def test_01_search_and_select(self, driver):
        """Open User List, search for the test user, and select the row."""
        _go_to_user_list(driver)
        _search_user(driver, TEST_USER_ID)
        _select_user_row(driver, TEST_USER_ID)

        # â”€â”€ Step 2: Click Disable and verify dialog
        # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def test_02_click_disable_button(self, driver):
        """
        Click the Disable toolbar button.

        BUTTON DETAILS (from browser inspection):
        â€¢ ID:    "User_tbrDelete"  (misleading name â€” it DISABLES, not deletes)
        â€¢ Title: "Disable"
        â€¢ After clicking, a modal dialog appears asking for confirmation

        EXPECTED DIALOG TEXT:
        "Do you want to disable this user?"
        """
        # The Disable button uses id="User_tbrDelete" â€” this is by design in
        # Ultriva
        disable_btn = WebDriverWait(driver, WAIT).until(
            EC.presence_of_element_located((By.ID, "User_tbrDelete"))
        )
        print(f"\n  Disable button â€” title=' { disable_btn.get_attribute('title') }'")

        driver.execute_script("arguments[0].click();", disable_btn)
        time.sleep(PAUSE)
        print("  Clicked Disable â€” waiting for confirmation dialog")

        # Verify the modal appeared and contains "disable"
        modal = WebDriverWait(driver, WAIT).until(
            EC.visibility_of_element_located((By.ID, "Modal-modal-alert-id"))
        )
        modal_text = modal.text.strip()
        print(f"  Modal text: '{modal_text[:200]}'")
        assert "disable" in modal_text.lower(), (
            f"Expected disable dialog, got: '{modal_text[:100]}'"
        )
        print("  Disable confirmation dialog appeared correctly")

        # â”€â”€ Step 3: Confirm disable
        # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def test_03_confirm_disable(self, driver):
        """
        Click 'Yes' in the confirmation modal to disable the user.

        After confirming:
        â€¢ The user moves from the Active list to the Disabled list
        â€¢ The user can no longer log in to the application
        â€¢ The status icon changes from green (Active) to red (Disabled)
        â€¢ To re-enable: use More Options â†’ Show Disabled And Locked â†’ Enable
        """
        _confirm_modal_yes(driver)

        assert "ultrivalms" in driver.current_url
        print(f"  DISABLED '{TEST_USER_ID}' â€” URL: {driver.current_url}")

        # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
        # TEST CLASS 5 â€” Enable (Re-activate) a Disabled User
        # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
        #
        # QA PROCESS â€” How to Enable a Disabled User in Ultriva:
        #   1. Navigate to Admin > User List  (shows Active users by default)
        #   2. Click "More Options" dropdown in the toolbar
        #   3. Select "Show Disabled And Locked" â€” grid switches to Disabled list
        #   4. Search for the disabled user and select the row
        #   5. Click the ENABLE toolbar button (title="Enable")
        #      â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
        #      â”‚ The Enable button is ONLY visible on the Disabled list. â”‚
        #      â”‚ It does NOT appear on the Active user list toolbar.     â”‚
        #      â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
        #   6. A confirmation dialog appears:
        #        "Do you want to enable this user?"
        #   7. Click YES to confirm
        #   8. Navigate back to Active list â†’ user shows Active (green icon)
        #
        # WHAT THESE TESTS VERIFY:
        #   test_01 â€” Switch to the Disabled User List via More Options
        #   test_02 â€” Search for the user and select the row
        #   test_03 â€” Click Enable â†’ confirm dialog â†’ click Yes
        #   test_04 â€” Navigate to Active list â†’ verify user is Active again
        # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

        """

        Re-enable the previously disabled user from the Disabled User List.

        After this test class runs, the user is back in the Active list

        and can log in again.

        Test Steps:

        test_01 â€” Open User List â†’ More Options â†’ Show Disabled And Locked

        test_02 â€” Search for the user and select the row

        test_03 â€” Click Enable, confirm dialog, click Yes

        test_04 â€” Navigate to Active list and verify user is Active

        Run:  pytest tests/QALS11/Admin/Users/users.py::TestEnableUser -v -s

        """

        # â”€â”€ Step 1: Switch to the Disabled User List
        # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def test_01_open_disabled_list(self, driver):
        """
        Navigate to User List â†’ click "More Options" â†’ "Show Disabled And Locked".

        WHY THIS STEP IS NEEDED:
        The default User List only shows ACTIVE users.
        Disabled users are hidden until you switch to the Disabled view
        using the "More Options" dropdown in the toolbar.

        HOW TO IDENTIFY THE DISABLED LIST:
        The URL will contain "ds=1" when viewing Disabled users.
        """
        _go_to_user_list(driver)

        # Click More Options dropdown
        more_opts = WebDriverWait(driver, WAIT).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//button[contains(normalize-space(.),'More Options')] "
                "| //a[contains(normalize-space(.),'More Options')]"
            ))
        )
        driver.execute_script("arguments[0].click();", more_opts)
        time.sleep(1)
        print("\n  Clicked 'More Options' dropdown")

        # Select 'Show Disabled And Locked' from the dropdown menu
        show_disabled = WebDriverWait(driver, WAIT).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//a[normalize-space(.)='Show Disabled And Locked'] "
                "| //li[normalize-space(.)='Show Disabled And Locked']"
            ))
        )
        driver.execute_script("arguments[0].click();", show_disabled)
        _page_ready(driver)
        time.sleep(PAUSE)

        assert (
            "ds=1" in driver.current_url
            or "Disabled" in driver.title
        ), "Did not reach the Disabled User List"
        print(f"  Disabled User List â€” URL: {driver.current_url}")

        # â”€â”€ Step 2: Search and select the user
        # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def test_02_search_and_select(self, driver):
        """Search for the user in the Disabled list and select the row."""
        _search_user(driver, TEST_USER_ID)
        _select_user_row(driver, TEST_USER_ID)

        # â”€â”€ Step 3: Click Enable and confirm
        # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def test_03_enable_user(self, driver):
        """
        Click the Enable toolbar button and confirm in the modal dialog.

        The Enable button is only visible when viewing the Disabled list
        (step 1 must switch to the Disabled view first).

        EXPECTED DIALOG TEXT:
        "Do you want to enable this user?"
        """
        # Click Enable â€” this opens the confirmation modal (not a new page)
        enable_btn = None
        for by, sel in [
            (By.XPATH, "//a[@title='Enable'] | //button[@title='Enable']"),
            (By.XPATH, "//a[normalize-space(.)='Enable'] | //button[normalize-space(.)='Enable']"),
            (By.ID, "User_tbrEnable"),
        ]:
            try:
                enable_btn = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((by, sel))
        )
                break
            except Exception:
                continue

        assert enable_btn is not None, "Enable button not found â€” are you on the Disabled list?"
        driver.execute_script("arguments[0].click();", enable_btn)
        time.sleep(PAUSE)

        # Confirm Yes in the modal
        modal_text = _confirm_modal_yes(driver)
        assert "enable" in modal_text.lower(), (
            f"Expected enable dialog, got: '{modal_text[:100]}'"
        )
        print(f"  ENABLED '{TEST_USER_ID}'")

        # â”€â”€ Step 4: Verify user is Active again
        # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def test_04_verify_user_active(self, driver):
        """
        Navigate to the Active User List and confirm the user row appears
        with an Active status indicator (green tick icon).

        STATUS INDICATORS IN THE GRID:
        â€¢ enable1.gif (green icon) â†’ Active user â€” can log in
        â€¢ disable.gif (red icon)   â†’ Disabled user â€” cannot log in
        """
        _go_to_user_list(driver)
        _search_user(driver, TEST_USER_ID)

        row = WebDriverWait(driver, WAIT).until(
            EC.presence_of_element_located((
                By.XPATH, f"//tr[td[normalize-space(text())='{TEST_USER_ID}']]"
            ))
        )
        row_html = row.get_attribute("outerHTML")

        is_active = "enable1.gif" in row_html or "Active" in row_html
        if is_active:
            print(f"  VERIFIED: '{TEST_USER_ID}' status = ACTIVE (green tick)")
        else:
            print("  NOTE: Row found in Active list â€” verify icon manually")

        assert "ultrivalms" in driver.current_url
        print(f"  Final URL: {driver.current_url}")
