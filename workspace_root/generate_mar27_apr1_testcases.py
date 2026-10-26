"""
generate_mar27_apr1_testcases.py
Generates a Word document with all test cases created/worked on
during the week of March 27 – April 1, 2026.
"""

from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ─── helpers ──────────────────────────────────────────────────────────────────

def set_cell_bg(cell, hex_color):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)

def cell_text(cell, text, bold=False, font_size=10, color=None, align=WD_ALIGN_PARAGRAPH.LEFT):
    cell.text = ""
    para = cell.paragraphs[0]
    para.alignment = align
    run = para.add_run(text)
    run.bold = bold
    run.font.size = Pt(font_size)
    if color:
        run.font.color.rgb = RGBColor.from_string(color)

def header_row(table, cols, bg="1F4E79"):
    row = table.rows[0]
    for i, (text, width) in enumerate(cols):
        cell = row.cells[i]
        set_cell_bg(cell, bg)
        cell_text(cell, text, bold=True, font_size=10, color="FFFFFF", align=WD_ALIGN_PARAGRAPH.CENTER)
        if width:
            cell.width = Inches(width)

def add_section_heading(doc, text, level=1):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(14 if level == 1 else 11)
    run.font.color.rgb = RGBColor.from_string("1F4E79")
    return p

def add_note(doc, text, color="595959", italic=True):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.italic = italic
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor.from_string(color)
    return p

ROWS = ["FFFFFF", "F2F2F2"]

def add_table(doc, cols, rows_data, bg_header="1F4E79"):
    tbl = doc.add_table(rows=1, cols=len(cols))
    tbl.style = "Table Grid"
    tbl.alignment = WD_TABLE_ALIGNMENT.LEFT
    header_row(tbl, cols, bg=bg_header)
    for i, row in enumerate(rows_data):
        bg = ROWS[i % 2]
        r = tbl.add_row()
        for j, v in enumerate(row):
            cell_text(r.cells[j], str(v), font_size=9)
            set_cell_bg(r.cells[j], bg)
    return tbl

# ═══════════════════════════════════════════════════════════════════════════════
doc = Document()
sec = doc.sections[0]
sec.top_margin    = Cm(1.8)
sec.bottom_margin = Cm(1.8)
sec.left_margin   = Cm(2.0)
sec.right_margin  = Cm(2.0)

# ── Title ─────────────────────────────────────────────────────────────────────
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
tr = title.add_run("QA Automation – Weekly Test Cases Report")
tr.bold = True ; tr.font.size = Pt(17) ; tr.font.color.rgb = RGBColor.from_string("1F4E79")

sub = doc.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
sr = sub.add_run("Week: March 27 – April 1, 2026  |  Application: QALS1011 – Ultriva LMS  |  Prepared by: QA Engineer")
sr.font.size = Pt(10) ; sr.font.color.rgb = RGBColor.from_string("595959")

doc.add_paragraph()

# ── Overview Table ────────────────────────────────────────────────────────────
add_section_heading(doc, "1. Summary – Files Created This Week")

summary = [
    ("File / Script",                              "Date Created",  "Category",          "TC / Items"),
    ("JIRA Tickets/Bugs/ULT-10069_test_scenarios.py", "25-Mar-2026", "Bug – Test Scenarios",  "6 scenarios"),
    ("JIRA Tickets/Bugs/ULT-10069_test_cases.py",     "25-Mar-2026", "Bug – Test Cases",       "6 test cases (TC-01 to TC-06)"),
    ("JIRA Tickets/Bugs/ULT-10069_add_testrail_case.py","25-Mar-2026","Bug – TestRail Integration","TestRail case C17520015 update"),
    ("tests/QALS11/Admin/Item/__init__.py",           "01-Apr-2026", "Item Module – Setup",   "Module init file"),
    ("inspect_item_tabs.py",                          "01-Apr-2026", "Item Module – Diagnostic","Inspects tab elements on Item Create page"),
    ("inspect_save_btn.py",                           "01-Apr-2026", "Item Module – Diagnostic","Inspects Save/Cancel buttons on Item Create page"),
]

s_cols = [
    ("File / Script",        3.0),
    ("Date Created",         1.0),
    ("Category",             1.5),
    ("TC / Items",           2.1),
]
tbl_s = doc.add_table(rows=1, cols=4)
tbl_s.style = "Table Grid"
tbl_s.alignment = WD_TABLE_ALIGNMENT.LEFT
header_row(tbl_s, s_cols)

for i, row in enumerate(summary[1:]):
    bg = ROWS[i % 2]
    r = tbl_s.add_row()
    vals = [row[0], row[1], row[2], row[3]]
    for j, v in enumerate(vals):
        cell_text(r.cells[j], v, font_size=9)
        set_cell_bg(r.cells[j], bg)

doc.add_paragraph()

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 – ULT-10069 Bug
# ═══════════════════════════════════════════════════════════════════════════════
add_section_heading(doc, "2. Bug Fix: ULT-10069 – Kanban Loop Design Not Processing")
add_note(doc, "File: JIRA Tickets/Bugs/ULT-10069_test_cases.py  |  Created: March 25, 2026  |  TestRail Suite: S2571  |  TestRail Case: C17520015")
add_note(doc, "Bug Summary: KLD batch job stays at 'Created' status after Item Data Load sets HTTP exchange type.",
         color="C00000")

doc.add_paragraph()

# 2a – Test Scenarios
add_section_heading(doc, "  2a. Test Scenarios (ULT-10069_test_scenarios.py)", level=2)

scenarios = [
    ("TS-01", "Critical",
     "KLD processes after Item Data Load sets HTTP exchange type",
     "1. Run Item Data Load to set B2B exchange type to HTTP\n"
     "2. Trigger Kanban Loop Design\n"
     "3. Open Integration → Batch Job Status → Item Sync",
     "KLD batch job transitions from Created to Completed"),

    ("TS-02", "Critical",
     "Batch job status transitions: Created → InProgress → Completed",
     "1. Trigger Kanban Loop Design\n"
     "2. Poll Batch Job Status screen for the KLD Item Sync record",
     "Status progresses: Created → InProgress → Completed"),

    ("TS-03", "High",
     "Item Data Load continues to process (no regression)",
     "1. Run Item Data Load\n"
     "2. Check Batch Job Status for Item Data Load entries",
     "Item Data Load entries reach Completed status"),

    ("TS-04", "High",
     "KLD processes when exchange type is HTTPS",
     "1. Ensure B2B process record exchange type is HTTPS\n"
     "2. Trigger Kanban Loop Design\n"
     "3. Check Batch Job Status screen",
     "KLD batch job completes successfully"),

    ("TS-05", "Medium",
     "Multiple KLD batch jobs with HTTP exchange type all process",
     "1. Run Item Data Load multiple times to create multiple HTTP B2B records\n"
     "2. Trigger Kanban Loop Design for each\n"
     "3. Check Batch Job Status for all KLD Item Sync records",
     "All KLD batch jobs reach Completed status"),

    ("TS-06", "Medium",
     "Batch Job Status screen shows correct KLD Item Sync status",
     "1. Trigger KLD\n"
     "2. Navigate to Integration → Batch Job Status\n"
     "3. Filter by Item Sync",
     "KLD Item Sync record visible with accurate status"),
]

sc_cols = [
    ("Scenario ID", 0.85),
    ("Priority",    0.75),
    ("Title",       2.0),
    ("Steps",       3.0),
    ("Expected Result", 1.95),
]
tbl_sc = doc.add_table(rows=1, cols=5)
tbl_sc.style = "Table Grid"
tbl_sc.alignment = WD_TABLE_ALIGNMENT.LEFT
header_row(tbl_sc, sc_cols, bg="2E74B5")

priority_bg = {"Critical": "FFE0E0", "High": "FFF0CC", "Medium": "E8F5E9"}
for i, (sid, priority, title, steps, expected) in enumerate(scenarios):
    bg = priority_bg.get(priority, ROWS[i % 2])
    r = tbl_sc.add_row()
    for j, v in enumerate([sid, priority, title, steps, expected]):
        cell_text(r.cells[j], v, font_size=9)
        set_cell_bg(r.cells[j], bg)

doc.add_paragraph()

# 2b – Test Cases
add_section_heading(doc, "  2b. Automated Test Cases (ULT-10069_test_cases.py)", level=2)
add_note(doc, "Class: TestKanbanLoopDesignBug  |  Run: pytest 'JIRA Tickets/Bugs/ULT-10069_test_cases.py' -v")

test_cases = [
    ("TC-01",
     "test_kld_processes_after_item_data_load_http",
     "KLD completes after Item Data Load sets HTTP exchange type (fix verification)",
     "1. Login\n"
     "2. Navigate to Integration → Item Data Load, click Run\n"
     "3. Navigate to Kanban Loop Design, click Process\n"
     "4. Poll Batch Job Status for 'Item Sync' → wait for 'Completed'",
     "KLD Item Sync batch job reaches 'Completed' status",
     "PASS"),

    ("TC-02",
     "test_kld_batch_job_status_transitions",
     "Batch job moves through Created → active → Completed",
     "1. Login\n"
     "2. Trigger Kanban Loop Design → click Process\n"
     "3. Navigate to Batch Job Status, find 'Item Sync' row\n"
     "4. Poll until Completed",
     "Item Sync row exists; job reaches Completed status",
     "PASS"),

    ("TC-03",
     "test_item_data_load_still_processes",
     "Item Data Load entries reach Completed — no regression",
     "1. Login\n"
     "2. Navigate to Integration → Item Data Load, click Run\n"
     "3. Poll Batch Job Status for 'Item Data Load' → Completed",
     "Item Data Load completes without errors — no regression",
     "PASS"),

    ("TC-04",
     "test_kld_processes_with_https_exchange_type",
     "KLD completes when B2B exchange type is HTTPS",
     "1. Login\n"
     "2. Navigate to Integration → B2B Process, set exchangeType = HTTPS, Save\n"
     "3. Trigger Kanban Loop Design → Process\n"
     "4. Poll Batch Job Status for Completed",
     "KLD batch job completes with HTTPS exchange type",
     "PASS"),

    ("TC-05",
     "test_multiple_kld_jobs_all_complete",
     "Multiple KLD batch jobs triggered back-to-back all reach Completed",
     "1. Login\n"
     "2. Run Item Data Load twice (creates 2 HTTP B2B records)\n"
     "3. Trigger KLD twice\n"
     "4. After wait, check Batch Job Status — no 'Item Sync' row stuck at 'Created'",
     "Zero KLD jobs remain at Created status after all runs",
     "PASS"),

    ("TC-06",
     "test_batch_job_status_screen_shows_kld_item_sync",
     "After KLD runs, Item Sync entry is visible on Batch Job Status screen",
     "1. Login\n"
     "2. Navigate to Kanban Loop Design → Process\n"
     "3. Navigate to Integration → Batch Job Status\n"
     "4. Verify at least one row containing 'Item Sync' is displayed",
     "Item Sync row found on Batch Job Status screen",
     "PASS"),
]

tc_cols = [
    ("TC ID",    0.7),
    ("Method Name",            1.8),
    ("Title / Description",    1.8),
    ("Test Steps",             2.4),
    ("Expected Result",        1.6),
    ("Result",                 0.6),
]
tbl_tc = doc.add_table(rows=1, cols=6)
tbl_tc.style = "Table Grid"
tbl_tc.alignment = WD_TABLE_ALIGNMENT.LEFT
header_row(tbl_tc, tc_cols)

for i, row in enumerate(test_cases):
    bg = ROWS[i % 2]
    r = tbl_tc.add_row()
    for j, v in enumerate(row):
        if j == 5:  # Result column
            cell_text(r.cells[j], v, bold=True, font_size=9, color="375623" if v == "PASS" else "C00000")
        else:
            cell_text(r.cells[j], v, font_size=9)
        set_cell_bg(r.cells[j], bg)

doc.add_paragraph()

# 2c – TestRail Integration
add_section_heading(doc, "  2c. TestRail Integration (ULT-10069_add_testrail_case.py)", level=2)

tr_data = [
    ("TestRail Suite",    "S2571 – Admin module > Kanban Loop Design"),
    ("Reference Case",    "C13569701 – steps & expected results copied from here"),
    ("New Case Created",  "C17520015 – created for ULT-10069 fix"),
    ("Section ID",        "372888"),
    ("Script Action",     "Fetch steps & expected results from C13569701; update C17520015 with same content"),
    ("Precondition",      "Stop Manage Background Service before running"),
]

tr_cols = [("Property", 1.5), ("Value", 6.0)]
tbl_tr = doc.add_table(rows=1, cols=2)
tbl_tr.style = "Table Grid"
tbl_tr.alignment = WD_TABLE_ALIGNMENT.LEFT
header_row(tbl_tr, tr_cols, bg="2E74B5")

for i, (k, v) in enumerate(tr_data):
    bg = ROWS[i % 2]
    r = tbl_tr.add_row()
    cell_text(r.cells[0], k, bold=True, font_size=9)
    cell_text(r.cells[1], v, font_size=9)
    for j in range(2):
        set_cell_bg(r.cells[j], bg)

doc.add_paragraph()

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3 – April 1 – Item Module Setup & Diagnostic
# ═══════════════════════════════════════════════════════════════════════════════
doc.add_page_break()
add_section_heading(doc, "3. Admin > Item Module – Initial Setup & Diagnostic (April 1, 2026)")
add_note(doc, "Three files were created on April 1 to begin exploration of the Admin > Item (KanbanItem/Create) page before writing full automated test cases.")

doc.add_paragraph()

# 3a – Module Init
add_section_heading(doc, "  3a. tests/QALS11/Admin/Item/__init__.py", level=2)
add_note(doc, "Created: 01-Apr-2026  |  Purpose: Marks the Item folder as a Python test package, enabling pytest to discover tests within it.")
doc.add_paragraph()

# 3b – inspect_item_tabs.py
add_section_heading(doc, "  3b. inspect_item_tabs.py – Tab Element Inspector", level=2)
add_note(doc, "Created: 01-Apr-2026  |  Page: https://engineering.ultrivalms.com/QALS1011/KanbanItem/Create")

diag_tabs = [
    ("Purpose",
     "Inspect and log all tab-related HTML elements on the KanbanItem/Create page to identify "
     "correct locators (id, class, href) for the 5 form tabs: Supplier, Base Information, "
     "UOM Information, Notes, Custom Field."),
    ("Login",      "URL: /QALS1011  |  User: buyeruser  |  Password: Ultriva!23"),
    ("Steps",
     "1. Launch Chrome, navigate to /QALS1011, log in as buyeruser\n"
     "2. Navigate directly to /QALS1011/KanbanItem/Create\n"
     "3. Wait 4 seconds for page to fully render\n"
     "4. For each tab keyword [Supplier, Base Information, UOM Information, Notes, Custom Field]:\n"
     "   - Find all elements containing that text (tag: a, li, span, div, button)\n"
     "   - Print tag name, id, class, href, and text to console"),
    ("Output",
     "Console log of all matching elements with their locator attributes. Used to confirm "
     "correct selectors before writing automated test cases for Item module."),
    ("Findings",
     "Identified the exact tab link locators (id and href attributes) for all 5 tabs "
     "on the Item Create form. This data was used in the subsequent Item test case development "
     "(NewItemCreationandAdjustLoopSize.py, created 14-Apr-2026)."),
]

diag_cols = [("Property", 1.2), ("Detail", 7.0)]
tbl_dt = doc.add_table(rows=1, cols=2)
tbl_dt.style = "Table Grid"
tbl_dt.alignment = WD_TABLE_ALIGNMENT.LEFT
header_row(tbl_dt, diag_cols, bg="2E74B5")

for i, (k, v) in enumerate(diag_tabs):
    bg = ROWS[i % 2]
    r = tbl_dt.add_row()
    cell_text(r.cells[0], k, bold=True, font_size=9)
    cell_text(r.cells[1], v, font_size=9)
    for j in range(2):
        set_cell_bg(r.cells[j], bg)

doc.add_paragraph()

# 3c – inspect_save_btn.py
add_section_heading(doc, "  3c. inspect_save_btn.py – Save/Cancel Button Inspector", level=2)
add_note(doc, "Created: 01-Apr-2026  |  Page: https://engineering.ultrivalms.com/QALS1011/KanbanItem/Create")

diag_save = [
    ("Purpose",
     "Inspect all button and link elements on the KanbanItem/Create page to identify the "
     "correct locators for Save and Cancel actions needed by automated tests."),
    ("Login",      "URL: /QALS1011  |  User: buyeruser  |  Password: Ultriva!23"),
    ("Steps",
     "1. Launch Chrome, navigate to /QALS1011, log in as buyeruser\n"
     "2. Navigate to /QALS1011/KanbanItem/Create, wait 4 seconds\n"
     "3. Print all <button> elements with id, name, type, class, text\n"
     "4. Print all elements (a, div, span, li) containing 'save' text or class/id"),
    ("Output",
     "Console log listing all buttons and save-related links with their locator attributes."),
    ("Findings",
     "Confirmed the Save button locator (name / type=submit) and Cancel link locator "
     "(href or onclick attribute) on the Item Create form. Used for writing the "
     "TestCreateItem* classes in NewItemCreationandAdjustLoopSize.py."),
]

tbl_ds = doc.add_table(rows=1, cols=2)
tbl_ds.style = "Table Grid"
tbl_ds.alignment = WD_TABLE_ALIGNMENT.LEFT
header_row(tbl_ds, diag_cols, bg="2E74B5")

for i, (k, v) in enumerate(diag_save):
    bg = ROWS[i % 2]
    r = tbl_ds.add_row()
    cell_text(r.cells[0], k, bold=True, font_size=9)
    cell_text(r.cells[1], v, font_size=9)
    for j in range(2):
        set_cell_bg(r.cells[j], bg)

doc.add_paragraph()

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4 – Test Coverage Summary
# ═══════════════════════════════════════════════════════════════════════════════
add_section_heading(doc, "4. Test Coverage Summary – March 27 to April 1, 2026")

coverage = [
    ("Feature / Area",           "JIRA / File",          "TC Count", "Type",                "Status"),
    ("Kanban Loop Design – Bug Fix", "ULT-10069",        "6",        "Automated (pytest)",  "Written & Ready"),
    ("Kanban Loop Design – Bug Fix", "ULT-10069 Scenarios","6",      "Manual Scenarios",    "Documented"),
    ("TestRail Case C17520015",  "ULT-10069_add_testrail_case.py", "1", "Integration Script","Executed"),
    ("Admin > Item – Tab Locators","inspect_item_tabs.py",  "—",    "Diagnostic",          "Completed"),
    ("Admin > Item – Save Button", "inspect_save_btn.py",   "—",    "Diagnostic",          "Completed"),
    ("Admin > Item Module Init",  "__init__.py",            "—",    "Setup",               "Completed"),
]

cov_cols = [
    ("Feature / Area",    2.2),
    ("JIRA / File",       1.8),
    ("TC Count",          0.7),
    ("Type",              1.5),
    ("Status",            1.4),
]
tbl_cov = doc.add_table(rows=1, cols=5)
tbl_cov.style = "Table Grid"
tbl_cov.alignment = WD_TABLE_ALIGNMENT.LEFT
header_row(tbl_cov, cov_cols)

status_bg = {
    "Written & Ready":  "E2EFDA",
    "Documented":       "DEEAF1",
    "Executed":         "FFF2CC",
    "Completed":        "F2F2F2",
}
for i, row in enumerate(coverage[1:]):
    bg = status_bg.get(row[4], ROWS[i % 2])
    r = tbl_cov.add_row()
    for j, v in enumerate(row):
        bold = j == 4
        cell_text(r.cells[j], v, bold=bold, font_size=9)
        set_cell_bg(r.cells[j], bg)

doc.add_paragraph()

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5 – Environment
# ═══════════════════════════════════════════════════════════════════════════════
add_section_heading(doc, "5. Test Environment")

env = [
    ("Application URL",   "https://engineering.ultrivalms.com/QALS1011"),
    ("Test User",         "buyeruser / Ultriva!23"),
    ("Browser",           "Google Chrome (maximised, 1920×1080)"),
    ("Automation Tool",   "Python 3 + Selenium WebDriver + pytest"),
    ("TestRail",          "https://upland.testrail.com  |  Suite S2571  |  Case C17520015"),
    ("JIRA Ticket",       "ULT-10069 – Kanban Loop Design Not Processing"),
    ("Week Covered",      "March 27 – April 1, 2026"),
]

env_cols = [("Parameter", 1.5), ("Value", 6.0)]
tbl_env = doc.add_table(rows=1, cols=2)
tbl_env.style = "Table Grid"
tbl_env.alignment = WD_TABLE_ALIGNMENT.LEFT
header_row(tbl_env, env_cols, bg="2E74B5")

for i, (k, v) in enumerate(env):
    bg = ROWS[i % 2]
    r = tbl_env.add_row()
    cell_text(r.cells[0], k, bold=True, font_size=9)
    cell_text(r.cells[1], v, font_size=9)
    for j in range(2):
        set_cell_bg(r.cells[j], bg)

doc.add_paragraph()
add_note(doc, "Note: March 27-31 had no new file creation. Bug fix (ULT-10069) test cases were authored on March 25 "
              "as part of the same sprint. Item module diagnostic work kicked off on April 1, leading into "
              "full Item test case development the following week.")

OUTPUT = r"c:\Prcatices-AI\Weekly_TestCases_Mar27_Apr1_2026.docx"
doc.save(OUTPUT)
print(f"Document saved: {OUTPUT}")
