"""
=============================================================================
  testrail_manager.py  –  UltrivaQAMilestone all-in-one manager
=============================================================================
Run from qa_automation/:
    python "Practise on test rail/UltrivaQAMilestone/testrail_manager.py" <command>

Available commands
------------------
  create_milestone            Create a new milestone
  create_plan                 Create a test plan and assign it to a milestone
  add_all_suites              Delete all plan entries then add every project
                              suite as one flat entry (include_all=True)
  remove_suites               Remove specific suite entries from a plan
  update_suite_cases          Replace case list for one suite entry in the plan
  copy_plan_entries           Copy all entries from a reference plan into
                              the target plan (no duplicates)
  list_plan                   Print a summary of all current plan entries

  ── EXCEL-DRIVEN AUTOMATION (no manual code editing needed) ──
  excel_setup                 Create testrail_config.xlsx template.
                              QA fills in the 4 sheets, then runs excel_run.
  excel_run                   Read testrail_config.xlsx and run full automation:
                                · Step 1 – Create Milestone  (if ID blank)
                                · Step 2 – Create Test Plan  (if ID blank)
                                · Step 3 – Add all Suite entries
                                · Step 4 – Submit pass/fail results
                              IDs are written back to the Excel after creation.

Excel Sheets
------------
  Config      Milestone Name, Plan Name, IDs (auto-filled after run)
  Suites      Suite Name + Action (include / exclude)
  TestCases   Suite Name + specific Case IDs to pin (blank = include all)
  Results     Suite Name + Test ID + Result (pass / fail)

Examples
--------
  python "Practise on test rail/UltrivaQAMilestone/testrail_manager.py" excel_setup
  python "Practise on test rail/UltrivaQAMilestone/testrail_manager.py" excel_run
  python "Practise on test rail/UltrivaQAMilestone/testrail_manager.py" list_plan
  python "Practise on test rail/UltrivaQAMilestone/testrail_manager.py" create_milestone
  python "Practise on test rail/UltrivaQAMilestone/testrail_manager.py" add_all_suites
  python "Practise on test rail/UltrivaQAMilestone/testrail_manager.py" remove_suites
  python "Practise on test rail/UltrivaQAMilestone/testrail_manager.py" copy_plan_entries
=============================================================================
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from config.config import TESTRAIL_PROJECT_ID, TESTRAIL_API_KEY
from utils.testrail_client import TestRailClient

# =============================================================================
#  ── USER CONFIGURATION  (edit these values before running) ──────────────────
# =============================================================================

# ── Milestone ─────────────────────────────────────────────────────────────────
MILESTONE_NAME = "UltrivaAutomation"
MILESTONE_ID   = 2640          # M2640 – set after running create_milestone

# ── Test Plan ─────────────────────────────────────────────────────────────────
PLAN_NAME      = "UltrivaAutomation"
PLAN_ID        = 81033          # P81033 – set after running create_plan

# ── Reference plan (used by copy_plan_entries) ────────────────────────────────
REF_PLAN_ID    = 79859          # P79859 – source plan to copy entries from

# ── Suites to EXCLUDE when running remove_suites ─────────────────────────────
SUITES_TO_REMOVE = {
    "Cross Site Scripting",
    "Security",
    # add more suite names here as needed
}

# ── Suite to update when running update_suite_cases ──────────────────────────
UPDATE_SUITE_NAME = "Actions"   # entry name in the plan to update
UPDATE_CASE_IDS   = []          # list of case IDs to set; [] = include_all=True

# ── TestRail result status IDs ────────────────────────────────────────────────
PASSED = 1
FAILED = 5

# =============================================================================
#  ── EXCEL INTEGRATION CONFIG ─────────────────────────────────────────────────
#  Excel file lives in the same folder as this script.
#  QA fills in the file once; excel_run does the rest automatically.
# =============================================================================

# Path to the Excel config file (same directory as this script)
EXCEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "testrail_config.xlsx")

# Sheet names – must match the workbook exactly
SHEET_CONFIG     = "Config"      # Milestone & Plan names/IDs
SHEET_SUITES     = "Suites"      # include / exclude per suite
SHEET_TESTCASES  = "TestCases"   # pin specific case IDs to a suite
SHEET_RESULTS    = "Results"     # which test IDs to mark as FAILED

# =============================================================================
#  ── HELPERS ──────────────────────────────────────────────────────────────────
# =============================================================================

def _connect():
    """Validate API key and return a connected TestRailClient."""
    if not TESTRAIL_API_KEY:
        print("[ERROR] TESTRAIL_API_KEY not set in environment."); sys.exit(1)
    return TestRailClient()


def _get_plan(tr, plan_id):
    """Fetch plan detail and return (plan_dict, entries_list)."""
    plan    = tr._client.plans.get_plan(plan_id=plan_id)
    entries = plan.get("entries", [])
    return plan, entries


def _run_case_ids(tr, run_id):
    """Return list of case IDs for a given run."""
    raw   = tr._client.tests.get_tests(run_id=run_id)
    tests = raw.get("tests", raw) if isinstance(raw, dict) else raw
    return [t["case_id"] for t in tests]


def _suite_cases(tr, suite_id):
    """
    Return all case IDs in a suite, handling pagination.
    TestRail API returns max 250 cases per request.
    """
    all_ids, offset = [], 0
    while True:
        raw   = tr._client.cases.get_cases(
                    project_id=TESTRAIL_PROJECT_ID, suite_id=suite_id, offset=offset)
        cases = raw.get("cases", raw) if isinstance(raw, dict) else raw
        ids   = [c["id"] for c in cases]
        all_ids += ids
        if len(ids) < 250:     # last page
            break
        offset += len(ids)
    return all_ids


# =============================================================================
#  ── COMMAND: list_plan ───────────────────────────────────────────────────────
# =============================================================================

def list_plan():
    """
    Print a clear summary of every entry currently in the plan.
    Shows: Run ID, Suite ID, entry name, case count.
    """
    tr = _connect()
    _, entries = _get_plan(tr, PLAN_ID)

    print(f"\n{'='*70}")
    print(f"  Plan P{PLAN_ID}  '{PLAN_NAME}'  ({len(entries)} entries)")
    print(f"{'='*70}")
    for e in entries:
        runs = e.get("runs", [])
        rid  = runs[0]["id"] if runs else "?"
        cc   = runs[0].get("case_count", "?") if runs else "?"
        print(f"  R{rid:<7}  S{e.get('suite_id'):<6}  cases={cc:<6}  '{e['name']}'")
    print(f"{'='*70}\n")


# =============================================================================
#  ── COMMAND: create_milestone ────────────────────────────────────────────────
# =============================================================================

def create_milestone():
    """
    Create a new milestone with MILESTONE_NAME in the project.
    After running, copy the printed M<id> into MILESTONE_ID above.
    """
    tr = _connect()
    ms = tr._client.milestones.add_milestone(
             project_id=TESTRAIL_PROJECT_ID, name=MILESTONE_NAME)
    print(f"[OK] Milestone M{ms['id']}  '{ms['name']}'")
    print(f"     → update MILESTONE_ID = {ms['id']} in this file")


# =============================================================================
#  ── COMMAND: create_plan ─────────────────────────────────────────────────────
# =============================================================================

def create_plan():
    """
    Create PLAN_NAME and assign it to MILESTONE_ID.
    Creates an empty plan; run add_all_suites afterwards to populate it.
    After running, copy the printed P<id> into PLAN_ID above.
    """
    if not MILESTONE_ID:
        print("[ERROR] Set MILESTONE_ID in this file first."); sys.exit(1)

    tr   = _connect()
    plan = tr._client.plans.add_plan(
               project_id=TESTRAIL_PROJECT_ID,
               name=PLAN_NAME,
               milestone_id=MILESTONE_ID)
    print(f"[OK] Plan P{plan['id']}  '{plan['name']}'  milestone=M{MILESTONE_ID}")
    print(f"     → update PLAN_ID = {plan['id']} in this file")


# =============================================================================
#  ── COMMAND: add_all_suites ──────────────────────────────────────────────────
# =============================================================================

def add_all_suites():
    """
    Rebuild the plan from scratch:
      1. Delete every existing entry in PLAN_ID
      2. For every suite in the project that has cases, add ONE flat entry
         with include_all=True (entry name = suite name)

    This mirrors the reference strategy in AuomationPractiseQA (P81301).
    Suites listed in SUITES_TO_REMOVE are automatically skipped.
    """
    tr = _connect()

    # ── Step 1: Remove all existing entries ──────────────────────────────────
    _, entries = _get_plan(tr, PLAN_ID)
    print(f"Deleting {len(entries)} existing entries from P{PLAN_ID} ...")
    for e in entries:
        try:
            tr._client.plans.delete_plan_entry(plan_id=PLAN_ID, entry_id=e["id"])
            runs = e.get("runs", [])
            rid  = runs[0]["id"] if runs else "?"
            print(f"  [DEL] R{rid}  '{e['name']}'")
        except Exception as ex:
            print(f"  [ERR] '{e['name']}': {ex}")

    # ── Step 2: Load all suites in the project ────────────────────────────────
    raw    = tr._client.suites.get_suites(project_id=TESTRAIL_PROJECT_ID)
    suites = raw.get("suites", raw) if isinstance(raw, dict) else raw
    print(f"\nFound {len(suites)} suites in project {TESTRAIL_PROJECT_ID}")
    print(f"Suites to skip: {SUITES_TO_REMOVE}\n")

    # ── Step 3: Add one entry per suite ──────────────────────────────────────
    added = skipped = 0
    for suite in suites:
        sid, name = suite["id"], suite["name"]

        # Skip suites listed in SUITES_TO_REMOVE
        if name in SUITES_TO_REMOVE:
            print(f"  [skip] S{sid}  '{name}'  – in exclusion list")
            skipped += 1
            continue

        # Skip suites with no test cases
        case_ids = _suite_cases(tr, sid)
        if not case_ids:
            print(f"  [skip] S{sid}  '{name}'  – no cases")
            skipped += 1
            continue

        # Add one flat entry covering all cases in the suite
        entry = tr._client.plans.add_plan_entry(
            plan_id     = PLAN_ID,
            suite_id    = sid,
            name        = name,
            include_all = True,
        )
        runs = entry.get("runs", [])
        rid  = runs[0]["id"] if runs else "?"
        cc   = runs[0].get("case_count", len(case_ids)) if runs else len(case_ids)
        print(f"  [ADD] R{rid}  S{sid}  '{name}'  case_count={cc}")
        added += 1

    print(f"\n[Done] {added} entries added, {skipped} skipped → P{PLAN_ID}")


# =============================================================================
#  ── COMMAND: remove_suites ───────────────────────────────────────────────────
# =============================================================================

def remove_suites():
    """
    Remove specific suite entries (by name) from the plan.
    Names are controlled by SUITES_TO_REMOVE above.
    """
    tr = _connect()
    _, entries = _get_plan(tr, PLAN_ID)

    removed = 0
    for e in entries:
        if e["name"] in SUITES_TO_REMOVE:
            tr._client.plans.delete_plan_entry(plan_id=PLAN_ID, entry_id=e["id"])
            runs = e.get("runs", [])
            rid  = runs[0]["id"] if runs else "?"
            print(f"  [DEL] R{rid}  '{e['name']}'")
            removed += 1

    if removed == 0:
        print(f"  No matching entries found for: {SUITES_TO_REMOVE}")
    print(f"\n[Done] {removed} entries removed from P{PLAN_ID}")


# =============================================================================
#  ── COMMAND: update_suite_cases ──────────────────────────────────────────────
# =============================================================================

def update_suite_cases():
    """
    Update the case selection for one entry in the plan.

    - UPDATE_SUITE_NAME  : entry name to target
    - UPDATE_CASE_IDS    : list of specific case IDs to assign
                           (empty list → switches to include_all=True)
    """
    tr = _connect()
    _, entries = _get_plan(tr, PLAN_ID)

    target = next((e for e in entries if e["name"] == UPDATE_SUITE_NAME), None)
    if not target:
        print(f"[ERROR] Entry '{UPDATE_SUITE_NAME}' not found in P{PLAN_ID}")
        list_plan()
        sys.exit(1)

    if UPDATE_CASE_IDS:
        # Update to a specific set of cases
        tr._client.plans.update_plan_entry(
            plan_id     = PLAN_ID,
            entry_id    = target["id"],
            include_all = False,
            case_ids    = UPDATE_CASE_IDS,
        )
        print(f"[OK] '{UPDATE_SUITE_NAME}' → {len(UPDATE_CASE_IDS)} specific cases")
    else:
        # Switch back to include_all (all cases in the suite)
        tr._client.plans.update_plan_entry(
            plan_id     = PLAN_ID,
            entry_id    = target["id"],
            include_all = True,
        )
        print(f"[OK] '{UPDATE_SUITE_NAME}' → include_all=True (all cases in suite)")


# =============================================================================
#  ── COMMAND: copy_plan_entries ───────────────────────────────────────────────
# =============================================================================

def copy_plan_entries():
    """
    Copy all entries from REF_PLAN_ID into PLAN_ID.
    - Reads the exact case IDs from each run in the reference plan
    - Skips entries whose name already exists in the target plan
    - Skips reference entries that have no cases
    """
    tr = _connect()

    # Load reference plan
    ref_plan, ref_entries = _get_plan(tr, REF_PLAN_ID)
    print(f"Reference plan: P{REF_PLAN_ID}  '{ref_plan.get('name','')}'"
          f"  ({len(ref_entries)} entries)")

    # Load target plan – build set of existing entry names to avoid duplicates
    _, tgt_entries = _get_plan(tr, PLAN_ID)
    existing_names  = {e["name"] for e in tgt_entries}

    added = skipped = 0
    for e in ref_entries:
        name     = e["name"]
        suite_id = e["suite_id"]
        runs     = e.get("runs", [])

        # Skip if already present in target plan
        if name in existing_names:
            print(f"  [skip] '{name}'  – already in plan")
            skipped += 1
            continue

        # Collect case IDs from the reference run
        case_ids = []
        for r in runs:
            case_ids += _run_case_ids(tr, r["id"])
        case_ids = list(dict.fromkeys(case_ids))   # deduplicate, keep order

        if not case_ids:
            print(f"  [skip] '{name}'  – no cases in reference run")
            skipped += 1
            continue

        # Add the entry to the target plan with exact same case IDs
        new_entry = tr._client.plans.add_plan_entry(
            plan_id     = PLAN_ID,
            suite_id    = suite_id,
            name        = name,
            include_all = False,
            case_ids    = case_ids,
        )
        for r in new_entry.get("runs", []):
            print(f"  [ADD] R{r['id']}  S{suite_id}  '{name}'"
                  f"  case_count={r.get('case_count', len(case_ids))}")
        added += 1

    print(f"\n[Done] {added} entries copied, {skipped} skipped → P{PLAN_ID}")


# =============================================================================
#  ── COMMAND: excel_setup ─────────────────────────────────────────────────────
# =============================================================================

def excel_setup():
    """
    Create testrail_config.xlsx in the same folder as this script.

    The workbook has 4 sheets that QA fills in before running excel_run:
      Config      – Milestone Name, Plan Name, IDs (auto-filled on first run)
      Suites      – Suite Name + Action (include / exclude)
      TestCases   – Suite Name + specific Case IDs (blank = include all)
      Results     – Suite Name + Test ID + Result (pass / fail)

    After filling in the file run:
        python "Practise on test rail/UltrivaQAMilestone/testrail_manager.py" excel_run
    """
    try:
        import openpyxl
        from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
    except ImportError:
        print("[ERROR] openpyxl not installed.  Run: pip install openpyxl")
        sys.exit(1)

    if os.path.exists(EXCEL_PATH):
        print(f"[WARN] File already exists – delete it first if you want a fresh template:")
        print(f"       {EXCEL_PATH}")
        return

    wb = openpyxl.Workbook()

    # ── Style helpers ──────────────────────────────────────────────────────────
    HDR_FILL  = PatternFill("solid", fgColor="1F4E79")   # dark blue header
    HDR_FONT  = Font(bold=True, color="FFFFFF", size=11)
    LBL_FILL  = PatternFill("solid", fgColor="D9E1F2")   # light blue label
    LBL_FONT  = Font(bold=True, size=11)
    NOTE_FONT = Font(italic=True, color="595959", size=10)
    CENTER    = Alignment(horizontal="center", vertical="center", wrap_text=True)
    WRAP      = Alignment(vertical="center", wrap_text=True)
    thin      = Side(border_style="thin", color="BFBFBF")
    BORDER    = Border(left=thin, right=thin, top=thin, bottom=thin)

    def _hdr(ws, row, values, widths):
        """Write a formatted header row and set column widths."""
        for col, val in enumerate(values, 1):
            c = ws.cell(row=row, column=col, value=val)
            c.fill, c.font, c.alignment, c.border = HDR_FILL, HDR_FONT, CENTER, BORDER
        for col, w in enumerate(widths, 1):
            ws.column_dimensions[chr(64 + col)].width = w

    def _row(ws, row_num, values):
        """Write a plain data row with border."""
        for col, val in enumerate(values, 1):
            c = ws.cell(row=row_num, column=col, value=val)
            c.alignment, c.border = WRAP, BORDER

    def _note(ws, row_num, text, merge_to):
        """Write an italicised instruction note spanning columns A to merge_to."""
        c = ws.cell(row=row_num, column=1, value=text)
        c.font, c.alignment = NOTE_FONT, WRAP
        ws.merge_cells(f"A{row_num}:{chr(64+merge_to)}{row_num}")
        ws.row_dimensions[row_num].height = 44

    # ── Sheet 1: Config ────────────────────────────────────────────────────────
    ws1 = wb.active
    ws1.title = SHEET_CONFIG
    _note(ws1, 1,
          "Fill in Milestone Name and Plan Name before running excel_run. "
          "Milestone ID and Plan ID are AUTO-FILLED after the first run – do not edit them manually.",
          3)
    _hdr(ws1, 2, ["Setting", "Value", "Description / Instructions"], [28, 22, 60])
    ws1.row_dimensions[2].height = 26

    config_data = [
        ("Milestone Name", "UltrivaAutomation",
         "Name for the new TestRail milestone"),
        ("Plan Name",      "UltrivaAutomation",
         "Name for the test plan (usually same as milestone)"),
        ("Milestone ID",   "",
         "AUTO-FILLED by excel_run after milestone is created. Leave blank to create a new one."),
        ("Plan ID",        "",
         "AUTO-FILLED by excel_run after plan is created. Leave blank to create a new one."),
        ("Reference Plan ID", "79859",
         "(Optional) ID of an existing plan to copy entries from. Leave blank to skip."),
    ]
    for i, (key, val, desc) in enumerate(config_data, start=3):
        ws1.row_dimensions[i].height = 26
        k = ws1.cell(row=i, column=1, value=key)
        k.fill, k.font, k.alignment, k.border = LBL_FILL, LBL_FONT, WRAP, BORDER
        v = ws1.cell(row=i, column=2, value=val)
        v.alignment, v.border = WRAP, BORDER
        d = ws1.cell(row=i, column=3, value=desc)
        d.font, d.alignment, d.border = NOTE_FONT, WRAP, BORDER

    # ── Sheet 2: Suites ────────────────────────────────────────────────────────
    ws2 = wb.create_sheet(SHEET_SUITES)
    _note(ws2, 1,
          "List suites here to control inclusion.  Action must be 'include' or 'exclude'. "
          "Suites NOT listed here are automatically INCLUDED with all cases.",
          3)
    _hdr(ws2, 2, ["Suite Name", "Action (include / exclude)", "Notes"], [42, 28, 42])

    suite_defaults = [
        ("Cross Site Scripting", "exclude", "Skipped – not needed for automation"),
        ("Security",             "exclude", "Skipped – not needed for automation"),
        ("Admin",                "include", "All cases OR specific IDs in TestCases sheet"),
        ("Actions",              "include", "All cases in Actions suite"),
    ]
    for i, row_data in enumerate(suite_defaults, start=3):
        _row(ws2, i, list(row_data))
        ws2.row_dimensions[i].height = 22

    # ── Sheet 3: TestCases ─────────────────────────────────────────────────────
    ws3 = wb.create_sheet(SHEET_TESTCASES)
    _note(ws3, 1,
          "Pin specific Case IDs to a suite entry. "
          "Use comma-separated IDs with or without the 'C' prefix (e.g. C5157814,5157815). "
          "Leave the Case IDs column blank to include ALL cases in that suite.",
          3)
    _hdr(ws3, 2, ["Suite Name", "Case IDs (comma-separated, C-prefix optional)", "Notes"],
         [42, 48, 42])

    tc_defaults = [
        ("Admin",   "C5157814",
         "Pin only this case from Admin suite"),
        ("Actions", "",
         "Blank = include all cases in Actions suite"),
    ]
    for i, row_data in enumerate(tc_defaults, start=3):
        _row(ws3, i, list(row_data))
        ws3.row_dimensions[i].height = 22

    # ── Sheet 4: Results ───────────────────────────────────────────────────────
    ws4 = wb.create_sheet(SHEET_RESULTS)
    _note(ws4, 1,
          "Enter tests to mark as FAILED. All other tests in the same run are marked PASSED. "
          "Suite Name must match the plan entry name exactly. "
          "Test ID uses the T-prefix (e.g. T41146589). "
          "Leave Suite Name blank to fail that Test ID across ALL runs.",
          4)
    _hdr(ws4, 2,
         ["Suite Name (must match plan entry)", "Test ID (T-prefix)",
          "Result (pass / fail)", "Notes"],
         [44, 22, 22, 44])

    result_defaults = [
        ("System Configuration Parameters settings", "T41146589", "fail",
         "Test SHOW_FORECAST_PLANNED_ORDERS_FOR_SUPPLIERS-True"),
        ("System Configuration Parameters settings", "T41146590", "fail",
         "Test SHOW_FORECAST_PLANNED_ORDERS_FOR_SUPPLIERS-False"),
    ]
    for i, row_data in enumerate(result_defaults, start=3):
        _row(ws4, i, list(row_data))
        ws4.row_dimensions[i].height = 22

    wb.save(EXCEL_PATH)
    print(f"[OK] Excel template created:")
    print(f"     {EXCEL_PATH}")
    print()
    print("  Next steps for QA:")
    print("  1. Open testrail_config.xlsx")
    print("  2. Config sheet   – verify Milestone Name and Plan Name")
    print("  3. Suites sheet   – mark suites to include or exclude")
    print("  4. TestCases sheet – pin specific Case IDs (or leave blank for all)")
    print("  5. Results sheet  – list Test IDs to mark as FAILED")
    print("  6. Save and close the file")
    print("  7. Run:  python \"Practise on test rail/UltrivaQAMilestone/testrail_manager.py\" excel_run")


# =============================================================================
#  ── COMMAND: excel_run ───────────────────────────────────────────────────────
# =============================================================================

def excel_run():
    """
    Read testrail_config.xlsx and execute the full TestRail automation in 4 steps:

      Step 1 – Create Milestone   (skipped if Milestone ID already exists in Excel)
      Step 2 – Create Test Plan   (skipped if Plan ID already exists in Excel)
      Step 3 – Add Suite Entries  (uses Suites + TestCases sheets to decide
                                   which suites to add and which case IDs to pin)
      Step 4 – Submit Results     (uses Results sheet to mark tests pass/fail;
                                   all tests not listed default to PASSED)

    Milestone ID and Plan ID are written back to the Excel file after creation
    so that re-running excel_run reuses the same milestone and plan.
    """
    try:
        import openpyxl
    except ImportError:
        print("[ERROR] openpyxl not installed.  Run: pip install openpyxl")
        sys.exit(1)

    if not os.path.exists(EXCEL_PATH):
        print(f"[ERROR] Excel file not found: {EXCEL_PATH}")
        print("        Run 'excel_setup' first to create the template file.")
        sys.exit(1)

    # ── Pre-flight: warn if Excel file is currently open/locked ──────────────
    try:
        import msvcrt
        with open(EXCEL_PATH, "r+b"):
            pass  # file is free to write
    except (IOError, PermissionError):
        print(f"[ERROR] Cannot open '{EXCEL_PATH}' for writing.")
        print("        Close the file in Excel first, then re-run excel_run.")
        sys.exit(1)

    wb = openpyxl.load_workbook(EXCEL_PATH)

    # ── Read Config sheet ──────────────────────────────────────────────────────
    ws_cfg = wb[SHEET_CONFIG]
    cfg = {}
    for row in ws_cfg.iter_rows(min_row=2, values_only=True):
        if row[0]:  # Key column must not be empty
            cfg[str(row[0]).strip()] = str(row[1]).strip() if row[1] is not None else ""

    ms_name = cfg.get("Milestone Name", "").strip()
    pn_name = cfg.get("Plan Name", "").strip()
    ms_id   = int(cfg["Milestone ID"]) if cfg.get("Milestone ID") else None
    pn_id   = int(cfg["Plan ID"])      if cfg.get("Plan ID")      else None
    ref_pid = int(cfg["Reference Plan ID"]) if cfg.get("Reference Plan ID") else None

    if not ms_name or not pn_name:
        print("[ERROR] 'Milestone Name' and 'Plan Name' must be set in the Config sheet.")
        sys.exit(1)

    # ── Read Suites sheet ──────────────────────────────────────────────────────
    # Build a set of suite names that QA marked as 'exclude'
    ws_suites = wb[SHEET_SUITES]
    excel_excluded = set()
    for row in ws_suites.iter_rows(min_row=3, values_only=True):
        suite_name = str(row[0]).strip() if row[0] else ""
        action     = str(row[1]).strip().lower() if row[1] else "include"
        if suite_name and action == "exclude":
            excel_excluded.add(suite_name)

    # ── Read TestCases sheet ───────────────────────────────────────────────────
    # Build {suite_name: [case_id, ...]};
    # empty list means include_all=True for that suite
    ws_tc = wb[SHEET_TESTCASES]
    pinned = {}   # {suite_name: [case_id, ...]} – empty list = include_all
    for row in ws_tc.iter_rows(min_row=3, values_only=True):
        suite_name = str(row[0]).strip() if row[0] else ""
        ids_raw    = str(row[1]).strip() if row[1] else ""
        if suite_name:
            if ids_raw:
                # Parse comma-separated IDs; strip optional 'C' prefix
                case_ids = [
                    int(x.strip().lstrip("Cc"))
                    for x in ids_raw.split(",")
                    if x.strip()
                ]
                pinned[suite_name] = case_ids
            else:
                # Blank = include all cases in this suite
                pinned[suite_name] = []

    # ── Read Results sheet ─────────────────────────────────────────────────────
    # Build:
    #   fail_by_suite: {suite_name: set(test_ids)} – fail specific tests per run
    #   fail_global  : set(test_ids)               – fail these in every run
    ws_res = wb[SHEET_RESULTS]
    fail_by_suite = {}   # {suite_name: set(int test_id)}
    fail_global   = set()
    for row in ws_res.iter_rows(min_row=3, values_only=True):
        suite_name = str(row[0]).strip() if row[0] else ""
        test_id_raw = str(row[1]).strip() if row[1] else ""
        result      = str(row[2]).strip().lower() if row[2] else "pass"
        if not test_id_raw:
            continue
        tid = int(test_id_raw.lstrip("Tt"))
        if result == "fail":
            if suite_name:
                fail_by_suite.setdefault(suite_name, set()).add(tid)
            else:
                fail_global.add(tid)  # no suite = apply to ALL runs

    # ── Print automation plan to console ──────────────────────────────────────
    tr = _connect()
    print(f"\n{'='*65}")
    print(f"  EXCEL AUTOMATION RUN")
    print(f"  Milestone : '{ms_name}'")
    print(f"  Plan      : '{pn_name}'")
    print(f"  Excluded  : {excel_excluded or '(none)'}")
    print(f"  Pinned    : {list(pinned.keys()) or '(none – all suites use include_all)'}")
    print(f"  Fails     : suite-specific={list(fail_by_suite.keys())}  global={fail_global}")
    print(f"{'='*65}\n")

    # ── Step 1: Create Milestone ───────────────────────────────────────────────
    if not ms_id:
        print(f"[Step 1] Creating milestone '{ms_name}' ...")
        ms   = tr._client.milestones.add_milestone(
                   project_id=TESTRAIL_PROJECT_ID, name=ms_name)
        ms_id = ms["id"]
        print(f"         Milestone M{ms_id} created")
        # Write Milestone ID back to the Excel Config sheet
        for row in ws_cfg.iter_rows(min_row=2):
            if row[0].value == "Milestone ID":
                row[1].value = ms_id
                break
        try:
            wb.save(EXCEL_PATH)
            print(f"         Milestone ID {ms_id} saved to Excel")
        except (IOError, PermissionError):
            print(f"         [WARN] Could not save to Excel (file open?). "
                  f"Manually enter Milestone ID = {ms_id} in Config sheet.")
    else:
        print(f"[Step 1] Skipped – using existing milestone M{ms_id} (from Excel)")

    # ── Step 2: Create Test Plan ───────────────────────────────────────────────
    if not pn_id:
        print(f"\n[Step 2] Creating plan '{pn_name}' under M{ms_id} ...")
        plan  = tr._client.plans.add_plan(
                    project_id   = TESTRAIL_PROJECT_ID,
                    name         = pn_name,
                    milestone_id = ms_id)
        pn_id = plan["id"]
        print(f"         Plan P{pn_id} created")
        # Write Plan ID back to the Excel Config sheet
        for row in ws_cfg.iter_rows(min_row=2):
            if row[0].value == "Plan ID":
                row[1].value = pn_id
                break
        try:
            wb.save(EXCEL_PATH)
            print(f"         Plan ID {pn_id} saved to Excel")
        except (IOError, PermissionError):
            print(f"         [WARN] Could not save to Excel (file open?). "
                  f"Manually enter Plan ID = {pn_id} in Config sheet.")
    else:
        print(f"\n[Step 2] Skipped – using existing plan P{pn_id} (from Excel)")

    # ── Step 3: Add Suite Entries ──────────────────────────────────────────────
    print(f"\n[Step 3] Building suite entries in P{pn_id} ...")

    # 3a: Remove all current entries (start clean)
    _, existing_entries = _get_plan(tr, pn_id)
    if existing_entries:
        print(f"         Deleting {len(existing_entries)} existing entries first ...")
        for e in existing_entries:
            try:
                tr._client.plans.delete_plan_entry(plan_id=pn_id, entry_id=e["id"])
            except Exception:
                pass

    # 3b: Load all suites in the project
    raw    = tr._client.suites.get_suites(project_id=TESTRAIL_PROJECT_ID)
    suites = raw.get("suites", raw) if isinstance(raw, dict) else raw
    print(f"         {len(suites)} suites found in project {TESTRAIL_PROJECT_ID}")

    # 3c: Add one entry per suite; track run IDs for Step 4
    # suite_run_map: {suite_name: run_id} – used to submit results in Step 4
    suite_run_map = {}
    added = skipped = 0

    for suite in suites:
        sid, name = suite["id"], suite["name"]

        # Skip suites the QA marked as 'exclude' in the Suites sheet
        if name in excel_excluded:
            print(f"         [skip] '{name}'  – excluded in Suites sheet")
            skipped += 1
            continue

        # Determine whether to pin specific cases or include all
        if name in pinned and pinned[name]:
            # QA listed specific case IDs in the TestCases sheet
            include_all = False
            use_ids     = pinned[name]
            case_label  = f"{len(use_ids)} pinned case(s)"
        else:
            # Default: include all cases in the suite
            # Verify the suite is not empty before adding
            all_ids = _suite_cases(tr, sid)
            if not all_ids:
                print(f"         [skip] '{name}'  – suite has no test cases")
                skipped += 1
                continue
            include_all = True
            use_ids     = None
            case_label  = f"include_all ({len(all_ids)} cases)"

        # Add the plan entry
        kwargs = dict(plan_id=pn_id, suite_id=sid, name=name, include_all=include_all)
        if not include_all:
            kwargs["case_ids"] = use_ids
        entry = tr._client.plans.add_plan_entry(**kwargs)

        runs = entry.get("runs", [])
        rid  = runs[0]["id"] if runs else None
        cc   = runs[0].get("case_count", "?") if runs else "?"
        if rid:
            suite_run_map[name] = rid
        print(f"         [ADD] R{rid}  S{sid}  '{name}'  cases={cc}")
        added += 1

    print(f"         [Done] {added} suite entries added, {skipped} skipped")

    # ── Step 4: Submit Pass/Fail Results ──────────────────────────────────────
    print(f"\n[Step 4] Submitting pass/fail results to {len(suite_run_map)} runs ...")
    if not fail_by_suite and not fail_global:
        print("         (Results sheet has no FAIL rows – all tests will be PASSED)")

    total_p = total_f = 0
    for suite_name, run_id in suite_run_map.items():
        # Combine global fails + suite-specific fails for this run
        fail_ids = fail_global | fail_by_suite.get(suite_name, set())

        raw   = tr._client.tests.get_tests(run_id=run_id)
        tests = raw.get("tests", raw) if isinstance(raw, dict) else raw
        if not tests:
            print(f"         [skip] R{run_id} '{suite_name}' – no tests found")
            continue

        # Build results list: fail if test ID in fail_ids, else pass
        results = [
            {"test_id": t["id"],
             "status_id": FAILED if t["id"] in fail_ids else PASSED}
            for t in tests
        ]
        tr._client.results.add_results(run_id=run_id, results=results)

        p = sum(1 for r in results if r["status_id"] == PASSED)
        f = sum(1 for r in results if r["status_id"] == FAILED)
        total_p += p
        total_f += f
        failed_ids = [r["test_id"] for r in results if r["status_id"] == FAILED]
        print(f"         R{run_id:<7}  '{suite_name}'  passed={p}  failed={f}"
              + (f"  → fail T-IDs: {failed_ids}" if f else ""))

    print(f"\n{'='*65}")
    print(f"  EXCEL RUN COMPLETE")
    print(f"  Milestone M{ms_id}  |  Plan P{pn_id}")
    print(f"  Suite entries added : {added}")
    print(f"  Total tests PASSED  : {total_p}")
    print(f"  Total tests FAILED  : {total_f}")
    print(f"{'='*65}\n")


# =============================================================================
#  ── ENTRY POINT ──────────────────────────────────────────────────────────────
# =============================================================================

COMMANDS = {
    "list_plan":          list_plan,
    "create_milestone":   create_milestone,
    "create_plan":        create_plan,
    "add_all_suites":     add_all_suites,
    "remove_suites":      remove_suites,
    "update_suite_cases": update_suite_cases,
    "copy_plan_entries":  copy_plan_entries,
    "excel_setup":        excel_setup,
    "excel_run":          excel_run,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__)
        print("Available commands:")
        for cmd in COMMANDS:
            print(f"  {cmd}")
        sys.exit(0)

    COMMANDS[sys.argv[1]]()
