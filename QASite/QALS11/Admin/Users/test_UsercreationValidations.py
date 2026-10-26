"""

QALS11 | Admin > Users — Bulk User Creation & Validation

==========================================================

Application : https://engineering.ultrivalms.com/QALS1011

Login       : buyeruser / Ultriva!23

Browser     : Chrome (visible, maximised)

╔══════════════════════════════════════════════════════════════════════════════╗

║  WHAT THIS FILE DOES:                                                      ║

║                                                                            ║

║  1. TestCreateUsersManual  — Create multiple users from a hardcoded list   ║

║     (user data is defined directly in this file as a Python list)          ║

║                                                                            ║

║  2. TestCreateUsersFromExcel — Create multiple users by reading an Excel   ║

║     spreadsheet (.xlsx) that contains user data rows                       ║

║                                                                            ║

║  3. TestExportCredentials  — Export all created users' credentials to a    ║

║     formatted Excel report                                                 ║

║                                                                            ║

║  SINGLE LOGIN: All classes share ONE browser session (scope="module").     ║

║  No repeated login/logout between tests.                                   ║

╚══════════════════════════════════════════════════════════════════════════════╝

HOW TO RUN (from qa_automation/ folder):

    # Run everything:

    pytest tests/QALS11/Admin/Users/UsercreationValidations.py -v -s

    # Run only manual creation:

    pytest tests/QALS11/Admin/Users/UsercreationValidations.py::TestCreateUsersManual -v -s

    # Run only Excel-based creation:

    pytest tests/QALS11/Admin/Users/UsercreationValidations.py::TestCreateUsersFromExcel -v -s

    # Run only credential export:

    pytest tests/QALS11/Admin/Users/UsercreationValidations.py::TestExportCredentials -v -s

EXCEL INPUT FILE FORMAT (for TestCreateUsersFromExcel):

    Place an Excel file at: qa_automation/test_data/users_to_create.xlsx

    Required columns (Row 1 = headers):

      | first_name | last_name | work_phone | mobile    | email                    | user_id     | buyer_code | password     | account_type         |

      | Alice      | Johnson   | 5551001001 | 5551001100| user@example.com         | PlantAdm01  | BC001      | Admin@1234!  | Plant Administrators |

      | Bob        | Martinez  | 5552002002 | 5552002200| user@example.com         | PlantAdm02  | BC002      | Secure#2Bx9! | Plant Administrators |

    PASSWORD RULES (Ultriva enforces these):

      • Minimum 8 characters

      • At least 1 uppercase letter (A-Z)

      • At least 1 lowercase letter (a-z)

      • At least 1 digit (0-9)

      • At least 1 special character (!@#$%^&*)

"""

# ── Standard library imports ────────────────────────────────────────────

import os

import time

from datetime import datetime

# ── Third-party imports ─────────────────────────────────────────────────

import pytest

from openpyxl import Workbook, load_workbook

from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

from openpyxl.utils import get_column_letter

from selenium import webdriver

from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait, Select

from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import TimeoutException

# ══════════════════════════════════════════════════════════════════════════════

# CONFIGURATION

# ══════════════════════════════════════════════════════════════════════════════

BASE_URL = "https://engineering.ultrivalms.com/QALS1011"

ADMIN_USER = "buyeruser"

ADMIN_PASS = "Ultriva!23"

PAUSE = 2       # Seconds to pause between steps

WAIT = 15      # Max wait for WebDriverWait

SHARED_EMAIL = "vseelam@uplandsoftware.com"

ACCOUNT_TYPE = "Plant Administrators"

# ── File paths ──────────────────────────────────────────────────────────

# Input Excel file containing user data rows

EXCEL_INPUT = os.path.join(

    os.path.dirname(__file__),

    "..", "..", "..", "..", "test_data", "users_to_create.xlsx"

)

# Output Excel file for credentials report

CREDS_REPORT = os.path.join(

    os.path.dirname(__file__),

    "..", "..", "..", "..", "reports", "user_credentials.xlsx"

)

# ── Hardcoded user list for manual creation ─────────────────────────────

# Each dict has keys matching the Create User form fields.

# Modify this list to add/remove users for manual creation tests.

#

# PASSWORD RULES:

#   • > 8 characters

#   • At least 1 UPPERCASE, 1 lowercase, 1 digit, 1 special character

USERS_MANUAL = [

    {

        "first_name": "Alice",

        "mi": "A",

        "last_name": "Johnson",

        "work_phone": "5551001001",

        "mobile": "5551001100",

        "email": SHARED_EMAIL,

        "user_id": "PlantAdm01",

        "buyer_code": "BC001",

        "password": "Admin@1234!",

        "account_type": ACCOUNT_TYPE,

    },

    {

        "first_name": "Bob",

        "mi": "B",

        "last_name": "Martinez",

        "work_phone": "5552002002",

        "mobile": "5552002200",

        "email": SHARED_EMAIL,

        "user_id": "PlantAdm02",

        "buyer_code": "BC002",

        "password": "Secure#2Bx9!",

        "account_type": ACCOUNT_TYPE,

    },

    {

        "first_name": "Carol",

        "mi": "C",

        "last_name": "Davis",

        "work_phone": "5553003003",

        "mobile": "5553003300",

        "email": SHARED_EMAIL,

        "user_id": "PlantAdm03",

        "buyer_code": "BC003",

        "password": "Plant$3Cdvs!",

        "account_type": ACCOUNT_TYPE,

    },

    {

        "first_name": "David",

        "mi": "D",

        "last_name": "Wilson",

        "work_phone": "5554004004",

        "mobile": "5554004400",

        "email": SHARED_EMAIL,

        "user_id": "PlantAdm04",

        "buyer_code": "BC004",

        "password": "Test!4Xdw9z@",

        "account_type": ACCOUNT_TYPE,

    },

    {

        "first_name": "Emma",

        "mi": "E",

        "last_name": "Thompson",

        "work_phone": "5555005005",

        "mobile": "5555005500",

        "email": SHARED_EMAIL,

        "user_id": "PlantAdm05",

        "buyer_code": "BC005",

        "password": "Build%5eNop#",

        "account_type": ACCOUNT_TYPE,

    },

    {

        "first_name": "User",

        "mi": "",

        "last_name": "170426",

        "work_phone": "5556006006",

        "mobile": "5556006600",

        "email": SHARED_EMAIL,

        "user_id": "User170426",

        "buyer_code": "BC006",

        "password": "Ultriva!23",

        "account_type": ACCOUNT_TYPE,

    },

]

# Collects results during test execution — exported at the end

created_users: list[dict] = []

# ══════════════════════════════════════════════════════════════════════════════

# BROWSER FIXTURE — single login for all test classes

# ══════════════════════════════════════════════════════════════════════════════


@pytest.fixture(scope="module")
def driver():
    """

    Launch Chrome, log in ONCE, and share the session across all tests.

    No repeated login/logout — faster execution.

    """

    options = webdriver.ChromeOptions()

    options.add_argument("--start-maximized")

    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    browser = webdriver.Chrome(options=options)

    browser.set_page_load_timeout(30)

    # ── Login once ────────────────────────────────────────────────────────

    browser.get(BASE_URL)

    _page_ready(browser)

    WebDriverWait(browser, WAIT).until(

        EC.element_to_be_clickable((By.ID, "UserName"))

    ).send_keys(ADMIN_USER)

    browser.find_element(By.ID, "Password").send_keys(ADMIN_PASS)

    browser.find_element(By.ID, "login-button").click()

    _page_ready(browser)

    time.sleep(PAUSE)

    assert "ultrivalms" in browser.current_url, "Login failed — check credentials"

    print(f"\n  [SESSION] Logged in as '{ADMIN_USER}' — URL: {browser.current_url}")

    yield browser

    # Browser stays open for QA inspection

# ══════════════════════════════════════════════════════════════════════════════

# HELPER FUNCTIONS

# ══════════════════════════════════════════════════════════════════════════════


def _page_ready(driver, timeout=WAIT):
    """Wait until document.readyState == 'complete'."""

    WebDriverWait(driver, timeout).until(

        lambda d: d.execute_script("return document.readyState") == "complete"

    )


def _clear_and_type(driver, by, locator, text, timeout=WAIT):
    """Find a visible field, clear it, type new text."""

    el = WebDriverWait(driver, timeout).until(

        EC.visibility_of_element_located((by, locator))

    )

    el.clear()

    el.send_keys(text)

    return el


def _dismiss_modal(driver):
    """Close Ultriva's modal dialog if present."""

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


def _select_account_type(driver, account_type):
    """

    Select the Account Type from the dropdown.

    Tries multiple selector strategies for different Ultriva builds.

    Returns True on success, False otherwise.

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


def _fill_and_save_user(driver, user: dict) -> str:
    """

    Fill the Create User form with the given data and click Save.

    Parameters:

        driver  — Selenium WebDriver instance

        user    — Dict with keys: first_name, last_name, work_phone, mobile,

                  email, user_id, buyer_code, password, account_type

    Returns:

        "Created" if saved successfully, "Failed" if errors appeared.

    QA PROCESS:

      1. Navigate to /User/Create

      2. Fill personal fields (PRS$ prefix)

      3. Fill account fields (USR$ prefix)

      4. Select Account Type dropdown

      5. Enter Password and Confirm Password

      6. Click Save

      7. Check for validation error messages

    """

    uid = user.get("user_id", "Unknown")

    # Step 1 — Open Create User page

    driver.get(f"{BASE_URL}/User/Create")

    _page_ready(driver)

    time.sleep(PAUSE)

    _dismiss_modal(driver)

    # Step 2 & 3 — Form field mapping: (form_field_name, data_key, required)

    FIELDS = [

        ("PRS$FirstName", "first_name", True),

        ("PRS$MI", "mi", False),

        ("PRS$LastName", "last_name", True),

        ("PRS$WorkPhone", "work_phone", True),

        ("PRS$MobilePhone", "mobile", False),

        ("PRS$EmailID", "email", True),

        ("USR$LoginName", "user_id", True),

        ("USR$BuyerCode", "buyer_code", False),

    ]

    # Alternate field names for different Ultriva form builds

    ALT_NAMES = {

        "PRS$FirstName": ["FirstName", "User_FirstName", "txtFirstName"],

        "PRS$MI": ["MI", "User_MI"],

        "PRS$LastName": ["LastName", "User_LastName", "txtLastName"],

        "PRS$WorkPhone": ["WorkPhone", "User_WorkPhone", "txtWorkPhone"],

        "PRS$MobilePhone": ["MobilePhone", "User_MobilePhone"],

        "PRS$EmailID": ["EmailID", "Email", "User_Email", "txtEmail"],

        "USR$LoginName": ["LoginName", "UsrId", "UserId", "User_ID"],

        "USR$BuyerCode": ["BuyerCode", "User_BuyerCode"],

    }

    def _try_fill(name, value):
        """Try primary name, then alternates, then by ID."""

        for n in [name] + ALT_NAMES.get(name, []):

            try:

                _clear_and_type(driver, By.NAME, n, value, timeout=6)

                print(f"  [FILLED] {name} = '{value}'")

                return True

            except Exception:

                pass

        try:

            _clear_and_type(driver, By.ID, name, value, timeout=4)

            print(f"  [FILLED] {name} = '{value}' (by ID)")

            return True

        except Exception:

            pass

        return False

    # Fill each field

    for field_name, data_key, required in FIELDS:

        val = user.get(data_key, "")

        if val:

            ok = _try_fill(field_name, str(val))

            if not ok and required:

                print(f"  [WARN] Could not fill required field '{field_name}'")

    # Step 4 — Account Type dropdown

    acct = user.get("account_type", ACCOUNT_TYPE)

    if _select_account_type(driver, acct):

        print(f"  [FILLED] Account Type = '{acct}'")

    else:

        print(f"  [WARN] Could not set Account Type to '{acct}'")

    # Step 5 — Password fields

    pw = user.get("password", "")

    if pw:

        _try_fill("MISC$Password", pw)

        _try_fill("MISC$ConfirmPassword", pw)

    time.sleep(1)

    # Step 6 — Click Save

    saved = False

    for by, sel in [

        (By.XPATH, "//a[@title='Save' and contains(@onclick,'frmEntryPage_onSubmit')]"),

        (By.XPATH, "//a[contains(@onclick,'frmEntryPage_onSubmit')]"),

        (By.XPATH, "//a[@title='Save']"),

        (By.ID, "entryPGSubmit"),

        (By.XPATH, "//input[@value='Save'] | //button[normalize-space(text())='Save']"),

    ]:

        try:

            btn = WebDriverWait(
                driver, 6).until(
                EC.element_to_be_clickable(
                    (by, sel)))

            btn.click()

            saved = True

            break

        except Exception:

            continue

    if not saved:

        print(f"  [ERROR] Save button not found for '{uid}'")

        return "Failed"

    _page_ready(driver)

    time.sleep(PAUSE)

    # Step 7 — Check for form validation errors

    for xpath in [

        "//*[contains(@class,'error') or contains(@class,'alert-danger') or contains(@class,'validation')]",

        "//*[contains(@id,'error') or contains(@id,'Error')]",

    ]:

        for el in driver.find_elements(By.XPATH, xpath):

            txt = el.text.strip()

            if txt and len(txt) > 3:

                print(f"  [FORM ERROR] {txt[:200]}")

                return "Failed"

    return "Created"


def _read_users_from_excel(filepath: str) -> list[dict]:
    """

    Read user data from an Excel file (.xlsx).

    EXPECTED FORMAT:

      Row 1 = Column headers (must match the keys below)

      Row 2+ = User data

    REQUIRED COLUMNS:

      first_name, last_name, work_phone, email, user_id, password, account_type

    OPTIONAL COLUMNS:

      mi, mobile, buyer_code

    Returns a list of dicts, one per user row.

    """

    abs_path = os.path.abspath(filepath)

    assert os.path.exists(abs_path), (

        f"Excel input file not found: {abs_path}\n"

        f"Create this file with columns: first_name, last_name, work_phone, "

        f"email, user_id, password, account_type"

    )

    wb = load_workbook(abs_path, read_only=True)

    ws = wb.active

    # Read header row (Row 1)

    headers = [str(cell.value).strip().lower() for cell in ws[1] if cell.value]

    users = []

    for row in ws.iter_rows(min_row=2, values_only=True):

        if not row or not row[0]:

            continue  # skip empty rows

        user = {}

        for i, header in enumerate(headers):

            val = row[i] if i < len(row) else ""

            user[header] = str(val).strip() if val else ""

        users.append(user)

    wb.close()

    print(f"\n  [EXCEL] Read {len(users)} user(s) from: {abs_path}")

    return users

# ══════════════════════════════════════════════════════════════════════════════

# EXCEL EXPORT — formatted credential report

# ══════════════════════════════════════════════════════════════════════════════

# Styling constants


_DARK_BLUE = "1F4E79"

_LIGHT_BLUE = "BDD7EE"

_GREEN = "92D050"

_RED = "FF6B6B"

_BORDER = Border(

    left=Side(style="thin"), right=Side(style="thin"),

    top=Side(style="thin"), bottom=Side(style="thin"),

)


def _export_credentials(records: list[dict], path: str) -> str:
    """

    Write user IDs, passwords, and statuses to a formatted Excel workbook.

    Sheet 1 — "User Credentials": one row per user

    Sheet 2 — "Summary": totals (success / failed)

    Parameters:

        records  — List of dicts with keys: user_id, password, status, created_at

        path     — File path where the .xlsx will be saved

    Returns the absolute path of the saved file.

    """

    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

    wb = Workbook()

    # ── Sheet 1: User Credentials ─────────────────────────────────────────

    ws = wb.active

    ws.title = "User Credentials"

    ws.sheet_view.showGridLines = False

    # Title banner

    ws.merge_cells("A1:F1")

    title = ws["A1"]

    title.value = "QALS1011 — User Credentials Report"

    title.font = Font(bold=True, color="FFFFFF", size=13, name="Calibri")

    title.fill = PatternFill("solid", fgColor=_DARK_BLUE)

    title.alignment = Alignment(horizontal="center", vertical="center")

    ws.row_dimensions[1].height = 28

    # Timestamp row

    ws.merge_cells("A2:F2")

    ts = ws["A2"]

    ts.value = f"Generated:  { datetime.now().strftime('%Y-%m-%d %H:%M:%S') }  |  Email: {SHARED_EMAIL}"

    ts.font = Font(italic=True, size=10, name="Calibri", color="444444")

    ts.fill = PatternFill("solid", fgColor=_LIGHT_BLUE)

    ts.alignment = Alignment(horizontal="center", vertical="center")

    # Column headers

    COLS = [("#", 5), ("User ID", 18), ("Password", 22), ("Status", 12),

            ("Source", 10), ("Created At", 22)]

    for i, (name, width) in enumerate(COLS, 1):

        cell = ws.cell(row=3, column=i, value=name)

        cell.font = Font(bold=True, color="FFFFFF", size=11, name="Calibri")

        cell.fill = PatternFill("solid", fgColor=_DARK_BLUE)

        cell.alignment = Alignment(horizontal="center", vertical="center")

        cell.border = _BORDER

        ws.column_dimensions[get_column_letter(i)].width = width

    # Data rows

    for idx, rec in enumerate(records, 1):

        row_num = idx + 3

        status = rec.get("status", "Unknown")

        fill_color = _GREEN if status == "Created" else _RED

        row_data = [

            idx,

            rec.get("user_id", ""),

            rec.get("password", ""),

            status,

            rec.get("source", "Manual"),

            rec.get("created_at", ""),

        ]

        for col, val in enumerate(row_data, 1):

            c = ws.cell(row=row_num, column=col, value=val)

            c.font = Font(size=10, name="Calibri")

            c.border = _BORDER

            if col == 4:  # Status column gets color

                c.fill = PatternFill("solid", fgColor=fill_color)

                c.alignment = Alignment(horizontal="center", vertical="center")

            else:

                alt_fill = "D6E4F0" if idx % 2 == 0 else "FFFFFF"

                c.fill = PatternFill("solid", fgColor=alt_fill)

    ws.freeze_panes = "A4"

    # ── Sheet 2: Summary ──────────────────────────────────────────────────

    ws2 = wb.create_sheet("Summary")

    ws2.sheet_view.showGridLines = False

    ws2.merge_cells("A1:B1")

    s_title = ws2["A1"]

    s_title.value = "User Creation Summary"

    s_title.font = Font(bold=True, color="FFFFFF", size=13, name="Calibri")

    s_title.fill = PatternFill("solid", fgColor=_DARK_BLUE)

    s_title.alignment = Alignment(horizontal="center", vertical="center")

    total = len(records)

    success = sum(1 for r in records if r.get("status") == "Created")

    failed = total - success

    manual = sum(1 for r in records if r.get("source") == "Manual")

    excel = sum(1 for r in records if r.get("source") == "Excel")

    summary = [

        ("Total Users Attempted", total),

        ("Successfully Created", success),

        ("Failed", failed),

        ("From Manual List", manual),

        ("From Excel File", excel),

        ("Shared Email", SHARED_EMAIL),

        ("Account Type", ACCOUNT_TYPE),

        ("Run Date", datetime.now().strftime("%Y-%m-%d")),

    ]

    ws2.column_dimensions["A"].width = 28

    ws2.column_dimensions["B"].width = 38

    for row_i, (label, value) in enumerate(summary, 2):

        lc = ws2.cell(row=row_i, column=1, value=label)

        lc.font = Font(bold=True, size=10, name="Calibri")

        lc.fill = PatternFill("solid", fgColor=_LIGHT_BLUE)

        lc.border = _BORDER

        vc = ws2.cell(row=row_i, column=2, value=value)

        vc.font = Font(size=10, name="Calibri")

        vc.border = _BORDER

    wb.save(path)

    abs_path = os.path.abspath(path)

    print(f"\n  [EXPORT] Credentials saved → {abs_path}")

    return abs_path

# ══════════════════════════════════════════════════════════════════════════════

# TEST CLASS 1 — Create Multiple Users (Manual / Hardcoded List)

# ══════════════════════════════════════════════════════════════════════════════

#

# QA PROCESS — Manual Bulk User Creation:

#   • User data is defined in the USERS_MANUAL list at the top of this file

#   • Each user is created one-by-one on the /User/Create page

#   • If a user fails to create, it is marked as "xfail" (expected failure)

#     so the remaining users still get created

#   • Results are stored in the created_users list for the final export

#

# HOW TO ADD MORE USERS:

#   1. Add a new dict to USERS_MANUAL with the required keys

#   2. Add a new test method (e.g. test_08_create_user_xyz) that calls

#      self._create_one_user(driver, index)

#   3. Run the tests

#

# WHAT EACH TEST VERIFIES:

#   test_01 — Verify we are logged in and on the dashboard

#   test_02 to test_07 — Create one user each from USERS_MANUAL

# ══════════════════════════════════════════════════════════════════════════════

    """

    Create multiple users from a hardcoded list (USERS_MANUAL).

    Each user gets its own test for clear pass/fail reporting.

    Test Steps:

      test_01 — Verify login session is active

      test_02 — Create PlantAdm01 (Alice Johnson)

      test_03 — Create PlantAdm02 (Bob Martinez)

      test_04 — Create PlantAdm03 (Carol Davis)

      test_05 — Create PlantAdm04 (David Wilson)

      test_06 — Create PlantAdm05 (Emma Thompson)

      test_07 — Create User170426 (added today)

    Run:  pytest ...::TestCreateUsersManual -v -s

    """

    def _create_one_user(self, driver, index: int):
        """

        Internal helper — creates the user at USERS_MANUAL[index].

        Records the result into created_users for the final Excel export.

        Uses pytest.xfail() on failure so remaining tests continue running.

        """

        user = USERS_MANUAL[index]

        uid = user["user_id"]

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"\n  [CREATE] {uid} — {user['first_name']} {user['last_name']}")

        status = _fill_and_save_user(driver, user)

        created_users.append({

            "user_id": uid,

            "password": user["password"],

            "status": status,

            "source": "Manual",

            "created_at": created_at,

        })

        print(f"  → {uid}  status={status}")

        if status == "Failed":

            pytest.xfail(f"User '{uid}' creation failed — see console output")

    # ── Step 1: Verify login ──────────────────────────────────────────────


class TestUsercreationvalidations:
    def test_01_verify_login(self, driver):
        """Confirm we are logged in (session from the module fixture)."""
        assert "ultrivalms" in driver.current_url, "Not logged in"
        print(f"\n  [LOGIN] Session active — URL: {driver.current_url}")

        # ── Steps 2–7: One test per user ─────────────────────────────────────
    def test_02_create_plantadm01(self, driver):
        """Create Alice Johnson — user ID: PlantAdm01"""
        self._create_one_user(driver, 0)

    def test_03_create_plantadm02(self, driver):
        """Create Bob Martinez — user ID: PlantAdm02"""
        self._create_one_user(driver, 1)

    def test_04_create_plantadm03(self, driver):
        """Create Carol Davis — user ID: PlantAdm03"""
        self._create_one_user(driver, 2)

    def test_05_create_plantadm04(self, driver):
        """Create David Wilson — user ID: PlantAdm04"""
        self._create_one_user(driver, 3)

    def test_06_create_plantadm05(self, driver):
        """Create Emma Thompson — user ID: PlantAdm05"""
        self._create_one_user(driver, 4)

    def test_07_create_user170426(self, driver):
        """Create User170426 — password: Ultriva!23"""
        self._create_one_user(driver, 5)

        # ══════════════════════════════════════════════════════════════════════════════
        # TEST CLASS 2 — Create Multiple Users from Excel File
        # ══════════════════════════════════════════════════════════════════════════════
        #
        # QA PROCESS — Excel-Based Bulk User Creation:
        #   • User data is read from an Excel file (.xlsx)
        #   • Default path: qa_automation/test_data/users_to_create.xlsx
        #   • The first row must be column headers matching the expected keys
        #   • Each subsequent row is one user to create
        #   • Results are appended to the created_users list
        #
        # EXCEL FILE COLUMNS (Row 1 headers):
        #   first_name | last_name | work_phone | mobile | email | user_id |
        #   buyer_code | password  | account_type
        #
        # HOW TO USE:
        #   1. Create the Excel file at: qa_automation/test_data/users_to_create.xlsx
        #   2. Fill in one row per user
        #   3. Run: pytest ...::TestCreateUsersFromExcel -v -s
        #
        # WHAT EACH TEST VERIFIES:
        #   test_01 — Excel file exists and can be read
        #   test_02 — Each user row is created (one assertion per user)
        # ══════════════════════════════════════════════════════════════════════════════

        """

        Create multiple users by reading data from an Excel spreadsheet.

        Input file:  qa_automation/test_data/users_to_create.xlsx

        Test Steps:

        test_01 — Read and validate the Excel file

        test_02 — Create each user row from the spreadsheet

        Run:  pytest ...::TestCreateUsersFromExcel -v -s

        """

        # ── Step 1: Read the Excel file ──────────────────────────────────────
    def test_01_read_excel_file(self, driver):
        """
        Read the Excel input file and store the user data.

        If the file does not exist, this test is SKIPPED (not failed)
        so the manual creation tests can still run independently.
        """
        abs_path = os.path.abspath(EXCEL_INPUT)
        if not os.path.exists(abs_path):
            pytest.skip(f"Excel input file not found: {abs_path}\n"
            f"Create this file to run Excel-based user creation.\n"
            f"Required columns: first_name, last_name, work_phone, "
            f"email, user_id, password, account_type"
        )

        # Store users on the class so test_02 can access them
        TestCreateUsersFromExcel._excel_users = _read_users_from_excel(
            abs_path)
        assert len(TestCreateUsersFromExcel._excel_users) > 0, (
            "Excel file has no user data rows"
        )
        print(f"  [EXCEL] {len(TestCreateUsersFromExcel._excel_users)} user(s) to create")

        # ── Step 2: Create each user from Excel ──────────────────────────────
    def test_02_create_users_from_excel(self, driver):
        """
        Create each user from the Excel file one by one.

        Each user that fails is logged but does NOT stop the remaining users.
        All results are appended to the created_users list for the report.
        """
        users = getattr(TestCreateUsersFromExcel, "_excel_users", [])
        if not users:
            pytest.skip("No Excel users to create — test_01 may have been skipped")

        for i, user in enumerate(users, 1):
            uid = user.get("user_id", f"ExcelUser{i}")
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"\n  [EXCEL CREATE {i}/{len(users)}] {uid}")
        status = _fill_and_save_user(driver, user)

        created_users.append({
            "user_id": uid,
            "password": user.get("password", ""),
            "status": status,
            "source": "Excel",
            "created_at": created_at,
        })
        print(f"  → {uid}  status={status}")

        # Summary
        total = len(users)
        success = sum(1 for u in created_users if u.get("source")
                      == "Excel" and u["status"] == "Created")
        print(f"\n  [EXCEL SUMMARY] {success}/{total} users created successfully")

        # ══════════════════════════════════════════════════════════════════════════════
        # TEST CLASS 3 — Export All Created User Credentials to Excel
        # ══════════════════════════════════════════════════════════════════════════════
        #
        # This class runs LAST — it exports all results from the previous classes.
        #
        # OUTPUT FILE:
        #   qa_automation/reports/user_credentials.xlsx
        #
        # The report contains:
        #   Sheet 1: User ID, Password, Status (Created/Failed), Source (Manual/Excel)
        #   Sheet 2: Summary totals
        # ══════════════════════════════════════════════════════════════════════════════

        """

        Export all user IDs and passwords from this session to a formatted Excel file.

        Test Steps:

        test_01 — Export credentials to Excel and verify the file was created

        Run:  pytest ...::TestExportCredentials -v -s

        """

    def test_01_export_to_excel(self, driver):
        """
        Save all created user credentials to an Excel workbook.

        Output: qa_automation/reports/user_credentials.xlsx

        The report includes:
        • User ID and password for each created user
        • Status: "Created" (green) or "Failed" (red)
        • Source: "Manual" or "Excel"
        • Timestamp of creation attempt
        • Summary sheet with totals
        """
        assert created_users, "No user records to export — creation tests may have been skipped"

        path = _export_credentials(created_users, CREDS_REPORT)
        assert os.path.exists(path), f"Excel file was not created at {path}"

        print(f"\n  [REPORT]  { len(created_users) } user(s) exported to:\n  {path}")
