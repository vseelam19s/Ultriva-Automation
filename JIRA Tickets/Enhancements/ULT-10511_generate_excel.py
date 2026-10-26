"""
ULT-10511 | Generate Excel report with Test Plan, Test Scenarios, Test Cases
Run: python "JIRA Tickets/Enhancements/ULT-10511_generate_excel.py"
Output: JIRA Tickets/Enhancements/ULT-10511_test_data.xlsx
"""

import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

OUTPUT = os.path.join(os.path.dirname(__file__), "ULT-10511_test_data.xlsx")

# ── Colour palette ─────────────────────────────────────────────────────────
BLUE   = "1F4E79"   # header background
LBLUE  = "BDD7EE"   # sub-header
GREEN  = "E2EFDA"   # pass
RED    = "FCE4D6"   # fail / blocked
YELLOW = "FFF2CC"   # in-progress / medium priority
WHITE  = "FFFFFF"
HIGH   = "FF0000"
MED    = "FF9900"
LOW    = "00B050"

THIN = Border(
    left=Side(style="thin"), right=Side(style="thin"),
    top=Side(style="thin"),  bottom=Side(style="thin"),
)


def hdr(bold=True, color=WHITE, bg=BLUE, size=11, wrap=False, center=False):
    fill = PatternFill("solid", fgColor=bg) if bg else None
    align = Alignment(wrap_text=wrap,
                      horizontal="center" if center else "left",
                      vertical="center")
    return Font(bold=bold, color=color, size=size), fill, align


def write_row(ws, row, values, font, fill, align, border=THIN):
    for col, val in enumerate(values, 1):
        c = ws.cell(row=row, column=col, value=val)
        c.font = font
        if fill:
            c.fill = fill
        c.alignment = align
        c.border = border


def set_col_widths(ws, widths):
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


# ══════════════════════════════════════════════════════════════════════════════
# Sheet 1 — Test Plan
# ══════════════════════════════════════════════════════════════════════════════
def sheet_test_plan(wb):
    ws = wb.create_sheet("Test Plan")
    ws.sheet_view.showGridLines = False

    # Title
    ws.merge_cells("A1:E1")
    c = ws["A1"]
    c.value = "ULT-10511 | Test Plan — Export All Scheduled Jobs Report"
    c.font  = Font(bold=True, color=WHITE, size=13)
    c.fill  = PatternFill("solid", fgColor=BLUE)
    c.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 28

    # Meta rows
    meta = [
        ("Jira Ticket",   "ULT-10511"),
        ("Summary",       "Customer Needs a report of all the Scheduled Jobs"),
        ("Type",          "Enhancement / Customer Request"),
        ("Status",        "QA Approved"),
        ("Assignee",      "Sherif Hamdy"),
        ("QA Engineer",   "Vijayakumar Seelam"),
        ("Date",          "2026-03-19"),
    ]
    f_lbl, fill_lbl, align_lbl = hdr(bold=True,  color="1F4E79", bg=LBLUE, wrap=False)
    f_val, fill_val, align_val = hdr(bold=False,  color="000000", bg=None,  wrap=True)

    for r, (label, value) in enumerate(meta, 2):
        ws.merge_cells(f"B{r}:E{r}")
        lc = ws.cell(row=r, column=1, value=label)
        lc.font, lc.fill, lc.alignment, lc.border = f_lbl, fill_lbl, align_lbl, THIN
        vc = ws.cell(row=r, column=2, value=value)
        vc.font, vc.alignment, vc.border = f_val, align_val, THIN

    # Blank separator
    row = len(meta) + 3

    # Scope table
    ws.merge_cells(f"A{row}:E{row}")
    c = ws.cell(row=row, column=1, value="Scope")
    c.font = Font(bold=True, color=WHITE, size=11)
    c.fill = PatternFill("solid", fgColor=BLUE)
    c.alignment = Alignment(horizontal="center", vertical="center")
    row += 1

    scope_headers = ["#", "In Scope", "Out of Scope"]
    f_h, fill_h, align_h = hdr(bold=True, color="1F4E79", bg=LBLUE, center=True)
    ws.cell(row=row, column=1, value=scope_headers[0]).font = f_h
    ws.merge_cells(f"B{row}:C{row}")
    ws.cell(row=row, column=2, value=scope_headers[1]).font = f_h
    ws.merge_cells(f"D{row}:E{row}")
    ws.cell(row=row, column=4, value=scope_headers[2]).font = f_h
    for col in [1, 2, 4]:
        ws.cell(row=row, column=col).fill = fill_h
        ws.cell(row=row, column=col).alignment = align_h
        ws.cell(row=row, column=col).border = THIN
    row += 1

    scope = [
        ("Export all scheduled jobs (no date filter)", "Modifying existing per-day export"),
        ("Format match with existing export template",  "UI redesign"),
        ("Background/scheduled report execution",       "Real-time streaming export"),
        ("Download link / notification when ready",     "Email delivery of report"),
        ("Empty-state handling (no jobs scheduled)",    ""),
    ]
    for i, (ins, out) in enumerate(scope, 1):
        f_d = Font(size=10)
        fill_d = PatternFill("solid", fgColor=GREEN) if ins  else None
        fill_o = PatternFill("solid", fgColor=RED)   if out  else None
        ws.cell(row=row, column=1, value=i).font = f_d
        ws.cell(row=row, column=1).border = THIN
        ws.merge_cells(f"B{row}:C{row}")
        c = ws.cell(row=row, column=2, value=ins)
        c.font, c.border = f_d, THIN
        if fill_d: c.fill = fill_d
        ws.merge_cells(f"D{row}:E{row}")
        c = ws.cell(row=row, column=4, value=out)
        c.font, c.border = f_d, THIN
        if fill_o: c.fill = fill_o
        row += 1

    row += 1

    # Test Phases table
    ws.merge_cells(f"A{row}:E{row}")
    c = ws.cell(row=row, column=1, value="Test Phases & Entry/Exit Criteria")
    c.font = Font(bold=True, color=WHITE, size=11)
    c.fill = PatternFill("solid", fgColor=BLUE)
    c.alignment = Alignment(horizontal="center", vertical="center")
    row += 1

    phase_headers = ["Phase", "Description", "Entry Criteria", "Exit Criteria", "Priority"]
    for col, h in enumerate(phase_headers, 1):
        c = ws.cell(row=row, column=col, value=h)
        c.font, c.fill, c.alignment, c.border = f_h, fill_h, align_h, THIN
    row += 1

    phases = [
        ("Functional",   "Verify all positive/negative scenarios",
         "Feature deployed to QA; test data with 3+ scheduled jobs",
         "All High priority tests pass; no blockers open", "High"),
        ("Format Check", "Compare exported file vs reference template",
         "Export feature working",
         "Headers and data match reference exactly", "High"),
        ("Performance",  "Large dataset background job completes within SLA",
         "1000+ job records loaded",
         "Export completes without timeout/error", "Medium"),
        ("Security",     "Access control on export endpoint",
         "Auth module tested",
         "Unauthorised access returns 403", "High"),
    ]
    priority_colors = {"High": RED, "Medium": YELLOW, "Low": GREEN}
    for phase in phases:
        for col, val in enumerate(phase, 1):
            c = ws.cell(row=row, column=col, value=val)
            c.font = Font(size=10)
            c.border = THIN
            c.alignment = Alignment(wrap_text=True, vertical="center")
            if col == 5:
                c.fill = PatternFill("solid", fgColor=priority_colors.get(val, WHITE))
        ws.row_dimensions[row].height = 40
        row += 1

    set_col_widths(ws, [5, 28, 30, 30, 12])


# ══════════════════════════════════════════════════════════════════════════════
# Sheet 2 — Test Scenarios
# ══════════════════════════════════════════════════════════════════════════════
def sheet_scenarios(wb):
    ws = wb.create_sheet("Test Scenarios")
    ws.sheet_view.showGridLines = False

    ws.merge_cells("A1:F1")
    c = ws["A1"]
    c.value = "ULT-10511 | Test Scenarios — Export All Scheduled Jobs Report"
    c.font  = Font(bold=True, color=WHITE, size=13)
    c.fill  = PatternFill("solid", fgColor=BLUE)
    c.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 28

    headers = ["Scenario ID", "Title", "Pre-condition", "Test Steps", "Expected Result", "Priority"]
    f_h, fill_h, align_h = hdr(bold=True, color="1F4E79", bg=LBLUE, center=True)
    for col, h in enumerate(headers, 1):
        c = ws.cell(row=2, column=col, value=h)
        c.font, c.fill, c.alignment, c.border = f_h, fill_h, align_h, THIN

    SCENARIOS = [
        ("TS-01", "Export all scheduled jobs",
         "User logged in with export permission",
         "1. Navigate to Scheduled Jobs page\n2. Click 'Export All'\n3. Verify trigger",
         "Report generation starts successfully", "High"),
        ("TS-02", "Report format matches reference template",
         "Export triggered",
         "1. Open downloaded file\n2. Compare headers with reference template",
         "Headers and row format match reference exactly", "High"),
        ("TS-03", "Report runs as background job (no timeout)",
         "Large dataset in system",
         "1. Trigger export\n2. Confirm UI stays responsive\n3. Wait for completion",
         "Report completes in background; UI stays responsive", "High"),
        ("TS-04", "Report includes all scheduled jobs across all dates",
         "Multiple scheduled jobs across different dates",
         "1. Note total job count\n2. Trigger export\n3. Compare row count",
         "Row count matches total scheduled jobs in system", "High"),
        ("TS-05", "Column headers and data alignment are correct",
         "Export file available",
         "1. Open file\n2. Validate each column header\n3. Check data mapping",
         "All columns correctly labelled; data is aligned", "Medium"),
        ("TS-06", "Downloaded file is accessible after job completes",
         "Background job finished",
         "1. Click download link\n2. Open file",
         "File downloads and opens successfully", "Medium"),
        ("TS-07", "Empty state — no scheduled jobs",
         "No scheduled jobs in system",
         "1. Trigger export",
         "Empty file generated; no error shown", "Medium"),
        ("TS-08", "Large dataset export completes without error",
         "1000+ scheduled job records",
         "1. Trigger export\n2. Wait for completion\n3. Verify file",
         "Export succeeds with all records present", "Medium"),
        ("TS-09", "Unauthorised user cannot trigger export",
         "User without export permission logged in",
         "1. Navigate to export page\n2. Attempt to trigger export",
         "Access denied; appropriate error message displayed", "High"),
        ("TS-10", "Export is idempotent",
         "Scheduled jobs data unchanged",
         "1. Run export\n2. Run export again\n3. Compare files",
         "Both files contain identical data", "Low"),
    ]

    priority_colors = {"High": RED, "Medium": YELLOW, "Low": PatternFill("solid", fgColor=LOW)}

    for r, row_data in enumerate(SCENARIOS, 3):
        for col, val in enumerate(row_data, 1):
            c = ws.cell(row=r, column=col, value=val)
            c.font = Font(size=10)
            c.border = THIN
            c.alignment = Alignment(wrap_text=True, vertical="center")
            if col == 6:
                pc = priority_colors.get(val)
                if isinstance(pc, str):
                    c.fill = PatternFill("solid", fgColor=pc)
                elif pc:
                    c.fill = pc
        ws.row_dimensions[r].height = 55

    set_col_widths(ws, [12, 30, 28, 40, 35, 10])


# ══════════════════════════════════════════════════════════════════════════════
# Sheet 3 — Test Cases
# ══════════════════════════════════════════════════════════════════════════════
def sheet_test_cases(wb):
    ws = wb.create_sheet("Test Cases")
    ws.sheet_view.showGridLines = False

    ws.merge_cells("A1:H1")
    c = ws["A1"]
    c.value = "ULT-10511 | Test Cases — Export All Scheduled Jobs Report"
    c.font  = Font(bold=True, color=WHITE, size=13)
    c.fill  = PatternFill("solid", fgColor=BLUE)
    c.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 28

    headers = ["TC ID", "Scenario Ref", "Test Case Title",
               "Pre-condition", "Test Steps", "Expected Result", "Priority", "Status"]
    f_h, fill_h, align_h = hdr(bold=True, color="1F4E79", bg=LBLUE, center=True)
    for col, h in enumerate(headers, 1):
        c = ws.cell(row=2, column=col, value=h)
        c.font, c.fill, c.alignment, c.border = f_h, fill_h, align_h, THIN

    TEST_CASES = [
        ("TC-01", "TS-01", "Export All button visible to authorised user",
         "User logged in with export permission",
         "1. Log in as authorised user\n2. Navigate to Scheduled Jobs page\n3. Check for 'Export All' button",
         "'Export All' button is visible and enabled", "High", "Not Run"),
        ("TC-02", "TS-01", "Clicking Export All triggers background job",
         "User on Scheduled Jobs page",
         "1. Click 'Export All'\n2. Check for confirmation message",
         "Confirmation 'report is being generated' displayed", "High", "Not Run"),
        ("TC-03", "TS-02", "Exported file has correct column headers",
         "Export triggered and completed",
         "1. Download exported file\n2. Open file\n3. Verify column headers",
         "Headers match: Job Number, Part Number, Description, Quantity, Due Date, Remaining Hours",
         "High", "Not Run"),
        ("TC-04", "TS-04", "Export row count matches total scheduled jobs",
         "Scheduled jobs exist in system",
         "1. Note total job count in UI\n2. Trigger export\n3. Open file\n4. Count rows",
         "File row count equals total scheduled jobs count", "High", "Not Run"),
        ("TC-05", "TS-07", "Empty state — export with no scheduled jobs",
         "No scheduled jobs in system",
         "1. Navigate to Scheduled Jobs page\n2. Click 'Export All'",
         "File with headers only generated; no error message", "Medium", "Not Run"),
        ("TC-06", "TS-09", "Unauthorised user is blocked from export",
         "Read-only user logged in",
         "1. Log in as read-only user\n2. Navigate to export endpoint",
         "HTTP 403 or 'Access Denied' message shown", "High", "Not Run"),
        ("TC-07", "TS-03", "UI remains responsive during background export",
         "Export triggered",
         "1. Trigger export\n2. Click navigation link while export runs",
         "Navigation link is enabled; page does not freeze", "High", "Not Run"),
        ("TC-08", "TS-10", "Export produces identical results on repeated runs",
         "Scheduled job data unchanged between runs",
         "1. Run export\n2. Record status\n3. Run export again\n4. Compare statuses",
         "Both runs show status 'Completed' or 'Ready'", "Low", "Not Run"),
    ]

    status_colors = {"Not Run": WHITE, "Pass": GREEN, "Fail": RED, "Blocked": YELLOW}
    priority_colors = {"High": RED, "Medium": YELLOW, "Low": LOW}

    for r, row_data in enumerate(TEST_CASES, 3):
        for col, val in enumerate(row_data, 1):
            c = ws.cell(row=r, column=col, value=val)
            c.font = Font(size=10)
            c.border = THIN
            c.alignment = Alignment(wrap_text=True, vertical="center")
            if col == 7:
                c.fill = PatternFill("solid", fgColor=priority_colors.get(val, WHITE))
            if col == 8:
                c.fill = PatternFill("solid", fgColor=status_colors.get(val, WHITE))
        ws.row_dimensions[r].height = 65

    set_col_widths(ws, [8, 12, 30, 28, 42, 35, 10, 12])


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════
def main():
    wb = Workbook()
    wb.remove(wb.active)          # remove default empty sheet

    sheet_test_plan(wb)
    sheet_scenarios(wb)
    sheet_test_cases(wb)

    wb.save(OUTPUT)
    print(f"Excel saved → {OUTPUT}")


if __name__ == "__main__":
    main()
