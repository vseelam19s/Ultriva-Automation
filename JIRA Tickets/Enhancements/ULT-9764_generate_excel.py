"""
ULT-9764 | Generate Excel report with Test Plan, Test Scenarios, Test Cases
Feature : Add Task Name Filter to Service Monitors Screen
Run     : python "JIRA Tickets/Enhancements/ULT-9764_generate_excel.py"
Output  : JIRA Tickets/Enhancements/ULT-9764_test_data.xlsx
"""

import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

OUTPUT = os.path.join(os.path.dirname(__file__), "ULT-9764_test_data.xlsx")

# ── Colour palette ─────────────────────────────────────────────────────────
BLUE   = "1F4E79"   # header background
LBLUE  = "BDD7EE"   # sub-header
GREEN  = "E2EFDA"   # pass / in-scope
RED    = "FCE4D6"   # fail / blocked / out-of-scope
YELLOW = "FFF2CC"   # medium priority / in-progress
WHITE  = "FFFFFF"
LOW_G  = "00B050"   # low priority font color

THIN = Border(
    left=Side(style="thin"), right=Side(style="thin"),
    top=Side(style="thin"),  bottom=Side(style="thin"),
)


def hdr(bold=True, color=WHITE, bg=BLUE, size=11, wrap=False, center=False):
    fill  = PatternFill("solid", fgColor=bg) if bg else None
    align = Alignment(wrap_text=wrap,
                      horizontal="center" if center else "left",
                      vertical="center")
    return Font(bold=bold, color=color, size=size), fill, align


def write_cell(ws, row, col, value, font, fill, align, border=THIN, merge_to=None):
    if merge_to:
        ws.merge_cells(f"{get_column_letter(col)}{row}:{get_column_letter(merge_to)}{row}")
    c = ws.cell(row=row, column=col, value=value)
    c.font      = font
    c.alignment = align
    c.border    = border
    if fill:
        c.fill = fill
    return c


def set_col_widths(ws, widths):
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


# ══════════════════════════════════════════════════════════════════════════════
# Sheet 1 — Test Plan
# ══════════════════════════════════════════════════════════════════════════════
def sheet_test_plan(wb):
    ws = wb.create_sheet("Test Plan")
    ws.sheet_view.showGridLines = False

    # ── Title ──────────────────────────────────────────────────────────────
    ws.merge_cells("A1:F1")
    c = ws["A1"]
    c.value     = "ULT-9764 | Test Plan — Add Task Name Filter to Service Monitors Screen"
    c.font      = Font(bold=True, color=WHITE, size=13)
    c.fill      = PatternFill("solid", fgColor=BLUE)
    c.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 30

    # ── Meta info ──────────────────────────────────────────────────────────
    meta = [
        ("Jira Ticket",   "ULT-9764"),
        ("Summary",       "Add Task Name Filter to Service Monitors Screen"),
        ("Type",          "Technical Debt"),
        ("Status",        "In QA Review"),
        ("Assignee",      "Sherif Hamdy"),
        ("QA Engineer",   "Vijayakumar Seelam"),
        ("QA Site",       "https://engineering.ultrivalms.com/QALS1011"),
        ("Test URL",      "https://engineering.ultrivalms.com/QALS1011/SysAdmin/IntgMonitor"),
        ("Date",          "2026-04-10"),
    ]
    f_lbl, fill_lbl, align_lbl = hdr(bold=True,  color="1F4E79", bg=LBLUE)
    f_val, _,        align_val = hdr(bold=False,  color="000000", bg=None, wrap=True)

    for r, (label, value) in enumerate(meta, 2):
        ws.merge_cells(f"B{r}:F{r}")
        lc = ws.cell(row=r, column=1, value=label)
        lc.font, lc.fill, lc.alignment, lc.border = f_lbl, fill_lbl, align_lbl, THIN
        vc = ws.cell(row=r, column=2, value=value)
        vc.font, vc.alignment, vc.border = f_val, align_val, THIN

    row = len(meta) + 3

    # ── Objective ──────────────────────────────────────────────────────────
    ws.merge_cells(f"A{row}:F{row}")
    c = ws.cell(row=row, column=1,
                value="Objective")
    c.font = Font(bold=True, color=WHITE, size=11)
    c.fill = PatternFill("solid", fgColor=BLUE)
    c.alignment = Alignment(horizontal="center", vertical="center")
    row += 1

    ws.merge_cells(f"A{row}:F{row}")
    obj = ws.cell(row=row, column=1,
                  value=(
                      "Verify that the Task Name text filter on the Integration Monitor → Errors tab "
                      "(Admin > Integration > Integration Monitor) renders correctly, filters records by "
                      "exact and partial task name, works in combination with the Date Range filter, shows "
                      "an appropriate empty state when no records match, and requires the Go button to apply."
                  ))
    obj.font      = Font(size=10)
    obj.alignment = Alignment(wrap_text=True, vertical="center")
    obj.border    = THIN
    ws.row_dimensions[row].height = 45
    row += 2

    # ── Scope ──────────────────────────────────────────────────────────────
    ws.merge_cells(f"A{row}:F{row}")
    c = ws.cell(row=row, column=1, value="Scope")
    c.font = Font(bold=True, color=WHITE, size=11)
    c.fill = PatternFill("solid", fgColor=BLUE)
    c.alignment = Alignment(horizontal="center", vertical="center")
    row += 1

    f_h, fill_h, align_h = hdr(bold=True, color="1F4E79", bg=LBLUE, center=True)
    ws.merge_cells(f"A{row}:C{row}")
    ws.cell(row=row, column=1, value="In Scope").font  = f_h
    ws.cell(row=row, column=1).fill                    = fill_h
    ws.cell(row=row, column=1).alignment               = align_h
    ws.cell(row=row, column=1).border                  = THIN
    ws.merge_cells(f"D{row}:F{row}")
    ws.cell(row=row, column=4, value="Out of Scope").font  = f_h
    ws.cell(row=row, column=4).fill                        = fill_h
    ws.cell(row=row, column=4).alignment                   = align_h
    ws.cell(row=row, column=4).border                      = THIN
    row += 1

    scope = [
        ("Task Name filter field visible on Errors tab",        "Current Status tab"),
        ("Filter by exact task name",                           "Cross-user filter persistence"),
        ("Filter by partial / substring task name",             "Admin task management"),
        ("Case-insensitive matching",                           "Integration Monitor data content"),
        ("Combining Task Name + Date Range filters",            "Other SysAdmin screens"),
        ("Empty / no-match result state",                       "API-level integration validation"),
        ("Clearing Task Name resets results",                   ""),
        ("Pagination accurate when filter is active",           ""),
        ("Go button required (no auto-search on keystroke)",    ""),
        ("Special characters handled gracefully",               ""),
    ]

    for ins, out in scope:
        f_d = Font(size=10)
        ws.merge_cells(f"A{row}:C{row}")
        c = ws.cell(row=row, column=1, value=ins)
        c.font, c.border = f_d, THIN
        c.fill = PatternFill("solid", fgColor=GREEN)
        c.alignment = Alignment(wrap_text=True, vertical="center")
        ws.merge_cells(f"D{row}:F{row}")
        c = ws.cell(row=row, column=4, value=out)
        c.font, c.border = f_d, THIN
        if out:
            c.fill = PatternFill("solid", fgColor=RED)
        c.alignment = Alignment(wrap_text=True, vertical="center")
        row += 1

    row += 1

    # ── Test Phases ────────────────────────────────────────────────────────
    ws.merge_cells(f"A{row}:F{row}")
    c = ws.cell(row=row, column=1, value="Test Phases & Entry / Exit Criteria")
    c.font = Font(bold=True, color=WHITE, size=11)
    c.fill = PatternFill("solid", fgColor=BLUE)
    c.alignment = Alignment(horizontal="center", vertical="center")
    row += 1

    phase_headers = ["Phase", "Description", "Entry Criteria", "Exit Criteria", "Risk", "Priority"]
    for col, h in enumerate(phase_headers, 1):
        c = ws.cell(row=row, column=col, value=h)
        c.font, c.fill, c.alignment, c.border = f_h, fill_h, align_h, THIN
    row += 1

    phases = [
        ("Functional",    "Verify filter shows, filters, and resets correctly",
         "Feature deployed to QALS1011; error records with 'sync' exist",
         "All Critical/High TCs pass; no blocker open",
         "Filter not wired to backend",      "High"),
        ("Case Matching", "Verify case-insensitive search",
         "Functional phase passed",
         "SYNC/sync/Sync return identical counts",
         "Case-sensitive DB collation",      "High"),
        ("Combination",   "Task Name + Date Range work together",
         "Both filters rendered",
         "Combined filter returns intersection of both criteria",
         "Filter AND vs OR logic error",     "High"),
        ("Pagination",    "Verify page count reflects filtered total",
         "Filter returns paged results",
         "Viewing counter updates correctly after filter",
         "Stale total in pagination",        "Medium"),
        ("Security",      "Special chars / XSS in Task Name field",
         "Functional phase passed",
         "No server error; no XSS execution",
         "Input not sanitised",              "Medium"),
    ]
    prio_colors = {"High": RED, "Medium": YELLOW, "Low": GREEN}
    for phase in phases:
        for col, val in enumerate(phase, 1):
            c = ws.cell(row=row, column=col, value=val)
            c.font      = Font(size=10)
            c.border    = THIN
            c.alignment = Alignment(wrap_text=True, vertical="center")
            if col == 6:
                c.fill = PatternFill("solid", fgColor=prio_colors.get(val, WHITE))
        ws.row_dimensions[row].height = 42
        row += 1

    # ── Risk Analysis ──────────────────────────────────────────────────────
    row += 1
    ws.merge_cells(f"A{row}:F{row}")
    c = ws.cell(row=row, column=1, value="Risk Analysis")
    c.font = Font(bold=True, color=WHITE, size=11)
    c.fill = PatternFill("solid", fgColor=BLUE)
    c.alignment = Alignment(horizontal="center", vertical="center")
    row += 1

    risk_headers = ["#", "Risk", "Impact", "Mitigation", "", ""]
    for col, h in enumerate(risk_headers[:4], 1):
        c = ws.cell(row=row, column=col, value=h)
        c.font, c.fill, c.alignment, c.border = f_h, fill_h, align_h, THIN
    ws.merge_cells(f"E{row}:F{row}")
    row += 1

    risks = [
        ("1", "Filter not wired to backend query",
         "Critical — wrong results returned",
         "Verify record count changes when filter applied"),
        ("2", "Case-sensitive matching excludes records",
         "High — usability degraded",
         "Test SYNC/sync/Sync; assert equal counts"),
        ("3", "Pagination resets using unfiltered total",
         "Medium — confusing page count",
         "Check 'Viewing X to Y of Z' before and after filter"),
        ("4", "Special chars cause server 500 error",
         "Low — edge case crash",
         "Test '$' and '<script>' inputs; confirm no 500"),
    ]
    for num, risk, impact, mitigation in risks:
        row_vals = [num, risk, impact, mitigation]
        impact_fill = {"Critical": RED, "High": YELLOW, "Medium": PatternFill("solid", fgColor="D9E1F2"), "Low": None}
        for col, val in enumerate(row_vals, 1):
            c = ws.cell(row=row, column=col, value=val)
            c.font      = Font(size=10)
            c.border    = THIN
            c.alignment = Alignment(wrap_text=True, vertical="center")
            if col == 3:
                key = val.split(" — ")[0].strip()
                fill = impact_fill.get(key)
                if isinstance(fill, str):
                    c.fill = PatternFill("solid", fgColor=fill)
                elif fill:
                    c.fill = fill
        ws.row_dimensions[row].height = 32
        row += 1

    set_col_widths(ws, [5, 30, 28, 35, 10, 10])


# ══════════════════════════════════════════════════════════════════════════════
# Sheet 2 — Test Scenarios
# ══════════════════════════════════════════════════════════════════════════════
def sheet_scenarios(wb):
    ws = wb.create_sheet("Test Scenarios")
    ws.sheet_view.showGridLines = False

    ws.merge_cells("A1:F1")
    c = ws["A1"]
    c.value     = "ULT-9764 | Test Scenarios — Add Task Name Filter to Service Monitors Screen"
    c.font      = Font(bold=True, color=WHITE, size=13)
    c.fill      = PatternFill("solid", fgColor=BLUE)
    c.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 28

    headers = ["Scenario ID", "Title", "Pre-condition", "Test Steps", "Expected Result", "Priority"]
    f_h, fill_h, align_h = hdr(bold=True, color="1F4E79", bg=LBLUE, center=True)
    for col, h in enumerate(headers, 1):
        c = ws.cell(row=2, column=col, value=h)
        c.font, c.fill, c.alignment, c.border = f_h, fill_h, align_h, THIN

    SCENARIOS = [
        ("TS-01", "Task Name filter field is visible on the Errors tab",
         "User logged in as admin; Errors tab is active.",
         "1. Navigate to Admin > Integration > Integration Monitor.\n"
         "2. Click the 'Errors' tab.\n"
         "3. Inspect the filter bar.",
         "A 'Task Name' text input and 'Go' button are visible beside the Date Range filter.",
         "Critical"),
        ("TS-02", "Valid exact task name returns only matching records",
         "At least one error record exists with a known task name.",
         "1. Navigate to Integration Monitor → Errors tab.\n"
         "2. Enter exact task name (e.g., 'SVC.$batchjob_BSU22ZAQALG') in Task Name field.\n"
         "3. Click Go.\n"
         "4. Inspect Name column of every row returned.",
         "All rows show the exact task name. Count is ≤ unfiltered total.",
         "Critical"),
        ("TS-03", "Partial / substring task name filters correctly",
         "Error records containing 'sync' in their task name exist.",
         "1. Navigate to Integration Monitor → Errors tab.\n"
         "2. Enter 'sync' in the Task Name field.\n"
         "3. Click Go.\n"
         "4. Review Name column of returned rows.",
         "Every row has 'sync' in its Name. Records without 'sync' are excluded.",
         "Critical"),
        ("TS-04", "Non-existent task name shows empty / no-results state",
         "User is on the Errors tab.",
         "1. Enter 'DOESNOTEXIST_XYZ_999' in Task Name.\n"
         "2. Click Go.\n"
         "3. Observe the results area.",
         "No data rows shown. 'No records found' message appears. No app error.",
         "High"),
        ("TS-05", "Task Name filter is case-insensitive",
         "Error records containing 'sync' exist.",
         "1. Enter 'SYNC', click Go. Note count.\n"
         "2. Clear, enter 'sync', click Go. Note count.\n"
         "3. Clear, enter 'Sync', click Go. Note count.",
         "Result count and records are identical for SYNC, sync, and Sync.",
         "High"),
        ("TS-06", "Clearing Task Name resets grid to all records for selected date range",
         "Filter was previously set to 'sync'.",
         "1. Clear Task Name field completely.\n"
         "2. Click Go.\n"
         "3. Observe total record count in 'Viewing X to Y of Z'.",
         "All error records within the selected Date Range are shown (matches baseline).",
         "High"),
        ("TS-07", "Task Name filter combined with Date Range narrows results correctly",
         "User is on Errors tab with default date range set.",
         "1. Select 'Past 7 Days' from Date Range dropdown.\n"
         "2. Enter 'sync' in Task Name.\n"
         "3. Click Go.\n"
         "4. Verify each row's Date and Name.",
         "Returned records match BOTH date range and task name. Others excluded.",
         "High"),
        ("TS-08", "Pagination reflects filtered total, not full dataset",
         "Filter 'sync' returns fewer records than unfiltered set.",
         "1. Enter 'sync', click Go.\n"
         "2. Read 'Viewing 1 to 200 of N | Page 1 of P'.\n"
         "3. Clear filter, click Go. Re-read counter.",
         "N (filtered) < unfiltered total. Page count P is from filtered N.",
         "Medium"),
        ("TS-09", "Go button required to trigger filter (no auto-search on keystroke)",
         "User is on Errors tab.",
         "1. Note current result count.\n"
         "2. Type 'sync' in Task Name but do NOT click Go.\n"
         "3. Wait 5 seconds.\n"
         "4. Observe the grid.",
         "Grid does not update. Results unchanged until Go is clicked.",
         "Medium"),
        ("TS-10", "Special characters in Task Name handled gracefully",
         "User is on Errors tab.",
         "1. Enter '$' in Task Name, click Go.\n"
         "2. Enter '<script>alert(1)</script>' in Task Name, click Go.\n"
         "3. Observe results and error messages.",
         "No server 500 error. No XSS execution. Results or empty state shown.",
         "Low"),
    ]

    prio_colors = {"Critical": "FF0000", "High": RED, "Medium": YELLOW, "Low": GREEN}

    for r, row_data in enumerate(SCENARIOS, 3):
        for col, val in enumerate(row_data, 1):
            c = ws.cell(row=r, column=col, value=val)
            c.font      = Font(size=10)
            c.border    = THIN
            c.alignment = Alignment(wrap_text=True, vertical="center")
            if col == 6:
                fgcolor = prio_colors.get(val, WHITE)
                font_color = WHITE if val == "Critical" else "000000"
                c.fill = PatternFill("solid", fgColor=fgcolor)
                c.font = Font(size=10, bold=(val == "Critical"), color=font_color)
        ws.row_dimensions[r].height = 70

    set_col_widths(ws, [12, 32, 28, 42, 38, 10])


# ══════════════════════════════════════════════════════════════════════════════
# Sheet 3 — Test Cases
# ══════════════════════════════════════════════════════════════════════════════
def sheet_test_cases(wb):
    ws = wb.create_sheet("Test Cases")
    ws.sheet_view.showGridLines = False

    ws.merge_cells("A1:H1")
    c = ws["A1"]
    c.value     = "ULT-9764 | Test Cases — Add Task Name Filter to Service Monitors Screen"
    c.font      = Font(bold=True, color=WHITE, size=13)
    c.fill      = PatternFill("solid", fgColor=BLUE)
    c.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 28

    headers = ["TC ID", "Scenario Ref", "Test Case Title",
               "Pre-condition", "Test Steps", "Expected Result", "Priority", "Status"]
    f_h, fill_h, align_h = hdr(bold=True, color="1F4E79", bg=LBLUE, center=True)
    for col, h in enumerate(headers, 1):
        c = ws.cell(row=2, column=col, value=h)
        c.font, c.fill, c.alignment, c.border = f_h, fill_h, align_h, THIN

    TEST_CASES = [
        ("TC-01", "TS-01",
         "Task Name input and Go button visible on Errors tab",
         "User is logged in as Application $ Administrator; Errors tab active.",
         "1. Navigate to Admin > Integration > Integration Monitor.\n"
         "2. Click 'Errors' tab.\n"
         "3. Inspect filter bar for Task Name input and Go button.",
         "'Task Name' text input and 'Go' button are both visible and enabled.",
         "Critical", "Not Run"),

        ("TC-02", "TS-03",
         "Partial name 'sync' returns only matching records",
         "Error records with 'sync' in task name exist for the selected date range.",
         "1. Open Errors tab.\n"
         "2. Enter 'sync' in Task Name field.\n"
         "3. Click Go.\n"
         "4. Check Name column of every row returned.",
         "All Name cells contain 'sync'. Record count ≤ unfiltered total.",
         "Critical", "Not Run"),

        ("TC-03", "TS-02",
         "Exact task name returns only records for that task",
         "At least one error record exists with a known task name.",
         "1. Load unfiltered results; note first task name in Name column.\n"
         "2. Enter that exact name in Task Name field.\n"
         "3. Click Go.\n"
         "4. Inspect all returned Name cells.",
         "Every row in results matches the entered task name exactly.",
         "Critical", "Not Run"),

        ("TC-04", "TS-04",
         "Non-existent task name shows empty state without error",
         "User is on Errors tab.",
         "1. Enter 'DOESNOTEXIST_XYZ_999' in Task Name.\n"
         "2. Click Go.\n"
         "3. Observe results grid and page source.",
         "Zero data rows shown; 'No records' message visible; no HTTP 500 error.",
         "High", "Not Run"),

        ("TC-05", "TS-05",
         "Filter is case-insensitive — SYNC / sync / Sync return same count",
         "Error records containing 'sync' exist.",
         "1. Enter 'SYNC', click Go. Record row count.\n"
         "2. Clear, enter 'sync', click Go. Record row count.\n"
         "3. Clear, enter 'Sync', click Go. Record row count.",
         "Row count identical for all three variants.",
         "High", "Not Run"),

        ("TC-06", "TS-06",
         "Clearing Task Name and clicking Go restores all records",
         "Filter 'sync' was previously applied.",
         "1. Record row count with no filter (baseline).\n"
         "2. Apply filter 'sync'; verify it reduces count.\n"
         "3. Clear Task Name field; click Go.\n"
         "4. Compare restored count with baseline.",
         "Row count after clearing equals baseline unfiltered count.",
         "High", "Not Run"),

        ("TC-07", "TS-07",
         "Task Name + Date Range combination filters correctly",
         "User is on Errors tab; Date Range dropdown is functional.",
         "1. Apply Task Name 'sync' only; note count A.\n"
         "2. Select 'Past 7 Days' from Date Range.\n"
         "3. Apply Task Name 'sync'; note count B.\n"
         "4. Verify each row satisfies both filters.",
         "Count B ≤ Count A. Every row date is within Past 7 Days and Name contains 'sync'.",
         "High", "Not Run"),

        ("TC-08", "TS-08",
         "Pagination 'Viewing X to Y of Z' reflects filtered total",
         "Filtered set (sync) is smaller than unfiltered set.",
         "1. Apply no filter; note pagination text (total = T_all).\n"
         "2. Apply filter 'sync'; note pagination text (total = T_filtered).",
         "T_filtered < T_all (unless all records happen to match). "
         "Page count re-calculated from T_filtered.",
         "Medium", "Not Run"),

        ("TC-09", "TS-09",
         "Grid does not auto-filter — Go button click required",
         "User is on Errors tab with results loaded.",
         "1. Note current row count.\n"
         "2. Type 'sync' in Task Name but do NOT click Go.\n"
         "3. Wait 3–5 seconds.\n"
         "4. Check row count.",
         "Row count unchanged. Grid only updates after Go is clicked.",
         "Medium", "Not Run"),

        ("TC-10", "TS-10",
         "Special characters do not cause server errors or XSS",
         "User is on Errors tab.",
         "1. Enter '$' in Task Name; click Go; check for 500 errors.\n"
         "2. Enter '<script>alert(1)</script>'; click Go; check page source.\n"
         "3. Enter \"'; DROP TABLE--\"; click Go.",
         "No HTTP 500 error. No XSS alert executes. Page remains functional.",
         "Low", "Not Run"),
    ]

    status_colors  = {"Not Run": WHITE, "Pass": GREEN,  "Fail": RED,    "Blocked": YELLOW}
    prio_colors    = {"Critical": "FF0000", "High": RED, "Medium": YELLOW, "Low": GREEN}
    prio_font_clr  = {"Critical": WHITE,  "High": "000000", "Medium": "000000", "Low": "000000"}

    for r, row_data in enumerate(TEST_CASES, 3):
        for col, val in enumerate(row_data, 1):
            c = ws.cell(row=r, column=col, value=val)
            c.font      = Font(size=10)
            c.border    = THIN
            c.alignment = Alignment(wrap_text=True, vertical="center")
            if col == 7:
                fgc = prio_colors.get(val, WHITE)
                fc  = prio_font_clr.get(val, "000000")
                c.fill = PatternFill("solid", fgColor=fgc)
                c.font = Font(size=10, bold=(val == "Critical"), color=fc)
            if col == 8:
                c.fill = PatternFill("solid", fgColor=status_colors.get(val, WHITE))
        ws.row_dimensions[r].height = 75

    set_col_widths(ws, [8, 12, 30, 28, 50, 38, 10, 12])


# ══════════════════════════════════════════════════════════════════════════════
# Sheet 4 — Short-Form Summary (from screenshot)
# ══════════════════════════════════════════════════════════════════════════════
def sheet_summary(wb):
    ws = wb.create_sheet("Short-Form Summary")
    ws.sheet_view.showGridLines = False

    ws.merge_cells("A1:E1")
    c = ws["A1"]
    c.value     = "ULT-9764 | Short-Form Test Cases (from Integration Monitor Screenshot)"
    c.font      = Font(bold=True, color=WHITE, size=13)
    c.fill      = PatternFill("solid", fgColor=BLUE)
    c.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 28

    headers = ["TC", "Description", "Steps (Short)", "Expected", "Status"]
    f_h, fill_h, align_h = hdr(bold=True, color="1F4E79", bg=LBLUE, center=True)
    for col, h in enumerate(headers, 1):
        c = ws.cell(row=2, column=col, value=h)
        c.font, c.fill, c.alignment, c.border = f_h, fill_h, align_h, THIN

    SHORT_CASES = [
        ("TC-01", "Filter field visible",
         "Open Errors tab",
         "'Task Name' input and 'Go' button are visible",
         "Not Run"),
        ("TC-02", "Filter by partial name 'sync'",
         "Enter 'sync' → click Go",
         "Only records with 'sync' in Name column shown",
         "Not Run"),
        ("TC-03", "Filter by exact task name",
         "Paste full task name → click Go",
         "Only that task's records shown",
         "Not Run"),
        ("TC-04", "No match — non-existent name",
         "Enter 'DOESNOTEXIST_XYZ_999' → click Go",
         "Empty grid or 'No records' message; no error",
         "Not Run"),
        ("TC-05", "Case-insensitive filtering",
         "Enter 'SYNC' → click Go",
         "Same records as 'sync' search",
         "Not Run"),
        ("TC-06", "Clear filter → restore all records",
         "Clear Task Name field → click Go",
         "Full unfiltered record set for selected date range returned",
         "Not Run"),
        ("TC-07", "Combined filters: date range + task name",
         "Set date range 'Past 7 Days' + Task Name 'sync' → click Go",
         "Records satisfy BOTH date and name criteria",
         "Not Run"),
        ("TC-08", "Pagination with filter active",
         "Filter 'sync' → check page count",
         "Page count reflects filtered total, not all records",
         "Not Run"),
        ("TC-09", "Go button required (no auto-search)",
         "Type name; do NOT click Go; wait 5 s",
         "Grid unchanged until Go is clicked",
         "Not Run"),
        ("TC-10", "Special chars in Task Name",
         "Enter '$' → Go; enter '<script>' → Go",
         "No server error; no XSS execution",
         "Not Run"),
    ]

    status_colors = {"Not Run": WHITE, "Pass": GREEN, "Fail": RED, "Blocked": YELLOW}

    for r, row_data in enumerate(SHORT_CASES, 3):
        for col, val in enumerate(row_data, 1):
            c = ws.cell(row=r, column=col, value=val)
            c.font      = Font(size=10)
            c.border    = THIN
            c.alignment = Alignment(wrap_text=True, vertical="center")
            if col == 5:
                c.fill = PatternFill("solid", fgColor=status_colors.get(val, WHITE))
        ws.row_dimensions[r].height = 38

    set_col_widths(ws, [8, 28, 30, 38, 12])


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════
def main():
    wb = Workbook()
    wb.remove(wb.active)   # remove default sheet

    sheet_test_plan(wb)
    sheet_scenarios(wb)
    sheet_test_cases(wb)
    sheet_summary(wb)

    wb.save(OUTPUT)
    print(f"Excel saved → {OUTPUT}")


if __name__ == "__main__":
    main()
