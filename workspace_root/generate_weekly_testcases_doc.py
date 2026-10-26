"""
generate_weekly_testcases_doc.py
Creates a Word document summarising all test cases created and run this week
(Week of April 28 – May 1, 2026) — for team lead review.
"""

from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

# ─── helpers ──────────────────────────────────────────────────────────────────

def set_cell_bg(cell, hex_color):
    """Fill table cell background with a hex colour (e.g. '1F4E79')."""
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

def add_data_row(table, values, bg=None):
    row = table.add_row()
    for i, val in enumerate(values):
        cell = row.cells[i]
        if bg:
            set_cell_bg(cell, bg)
        cell_text(cell, val, font_size=9)
    return row

def add_section_heading(doc, text, level=1):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(13 if level == 1 else 11)
    run.font.color.rgb = RGBColor.from_string("1F4E79")
    return p

def add_sub_heading(doc, text):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor.from_string("2E74B5")
    return p

def add_note(doc, text):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.italic = True
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor.from_string("595959")
    return p

# ─── document ─────────────────────────────────────────────────────────────────

doc = Document()

# Page margins
section = doc.sections[0]
section.top_margin    = Cm(1.8)
section.bottom_margin = Cm(1.8)
section.left_margin   = Cm(2.0)
section.right_margin  = Cm(2.0)

# ── Title block ───────────────────────────────────────────────────────────────
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
tr = title.add_run("QA Automation – Weekly Test Cases Summary")
tr.bold = True
tr.font.size = Pt(16)
tr.font.color.rgb = RGBColor.from_string("1F4E79")

sub = doc.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
sr = sub.add_run("Week: April 28 – May 1, 2026  |  Application: QALS1011 – Ultriva LMS  |  Prepared by: QA Engineer")
sr.font.size = Pt(10)
sr.font.color.rgb = RGBColor.from_string("595959")

doc.add_paragraph()

# ── Summary table ─────────────────────────────────────────────────────────────
add_section_heading(doc, "1. Summary Overview")

summary_data = [
    ("Module",              "Files / Classes",  "Total Test Cases"),
    ("Admin > Entities",    "19 entity files",  "57 (3 per entity)"),
    ("Admin > Workcenter",  "3 files",          "18"),
    ("Admin > Users",       "2 files",          "8"),
    ("Admin > Supplier",    "1 file",           "1"),
    ("Admin > Calendar",    "1 file",           "4"),
    ("Admin > Item",        "2 files",          "14"),
    ("TOTAL",               "—",                "102"),
]

cols = [("Module", 2.2), ("Files / Classes", 2.0), ("Total Test Cases", 1.8)]
tbl = doc.add_table(rows=1, cols=3)
tbl.style = "Table Grid"
tbl.alignment = WD_TABLE_ALIGNMENT.LEFT
header_row(tbl, cols)

for i, row_data in enumerate(summary_data[1:]):
    bg = "DEEAF1" if row_data[0] == "TOTAL" else None
    bold = row_data[0] == "TOTAL"
    r = tbl.add_row()
    for j, val in enumerate(row_data):
        cell_text(r.cells[j], val, bold=bold, font_size=9)
    if bg:
        for j in range(3):
            set_cell_bg(r.cells[j], bg)

doc.add_paragraph()

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 – Admin > Entities
# ═══════════════════════════════════════════════════════════════════════════════
add_section_heading(doc, "2. Admin > Entities — CRUD Test Cases")
add_note(doc, "Navigation: Admin > Entities (left nav).  Each entity has Add / Edit / View flows.")

ENTITIES = [
    ("ABC Code",          "TC-ABC-01", "TC-ABC-02", "TC-ABC-03"),
    ("Break Reason Code", "TC-BRC-01", "TC-BRC-02", "TC-BRC-03"),
    ("Carrier",           "TC-CAR-01", "TC-CAR-02", "TC-CAR-03"),
    ("Commodity Code",    "TC-CC-01",  "TC-CC-02",  "TC-CC-03"),
    ("Container",         "TC-CON-01", "TC-CON-02", "TC-CON-03"),
    ("Exception Code",    "TC-EC-01",  "TC-EC-02",  "TC-EC-03"),
    ("Location Code",     "TC-LC-01",  "TC-LC-02",  "TC-LC-03"),
    ("Logistics Mode",    "TC-LM-01",  "TC-LM-02",  "TC-LM-03"),
    ("Machine",           "TC-MAC-01", "TC-MAC-02", "TC-MAC-03"),
    ("Notes",             "TC-NOT-01", "TC-NOT-02", "TC-NOT-03"),
    ("Operation",         "TC-OP-01",  "TC-OP-02",  "TC-OP-03"),
    ("Operation Params",  "TC-OPP-01", "TC-OPP-02", "TC-OPP-03"),
    ("Printer",           "TC-PR-01",  "TC-PR-02",  "TC-PR-03"),
    ("Production Issue",  "TC-PI-01",  "TC-PI-02",  "TC-PI-03"),
    ("Reschedule Reason", "TC-RR-01",  "TC-RR-02",  "TC-RR-03"),
    ("Route",             "TC-RT-01",  "TC-RT-02",  "TC-RT-03"),
    ("Scrap Reason",      "TC-SR-01",  "TC-SR-02",  "TC-SR-03"),
    ("Skip Lot Plan",     "TC-SLP-01", "TC-SLP-02", "TC-SLP-03"),
    ("Unit of Measure",   "TC-UOM-01", "TC-UOM-02", "TC-UOM-03"),
]

entity_cols = [
    ("Entity Name",   2.0),
    ("TC ID – Add",   1.5),
    ("TC ID – Edit",  1.5),
    ("TC ID – View",  1.5),
    ("Description",   3.2),
]

tbl2 = doc.add_table(rows=1, cols=5)
tbl2.style = "Table Grid"
tbl2.alignment = WD_TABLE_ALIGNMENT.LEFT
header_row(tbl2, entity_cols)

descriptions = {
    "Add":  "Fill all fields with valid data and save. Verify row appears in list.",
    "Edit": "Select existing record, update fields, save. Verify changes in list.",
    "View": "Open record in read-only mode, verify fields displayed, click Cancel.",
}

row_colors = ["FFFFFF", "F2F2F2"]
for idx, (entity, add_id, edit_id, view_id) in enumerate(ENTITIES):
    bg = row_colors[idx % 2]
    for tc_id, flow in [(add_id, "Add"), (edit_id, "Edit"), (view_id, "View")]:
        r = tbl2.add_row()
        vals = [entity, tc_id, "", "", descriptions[flow]]
        if flow == "Add":
            vals = [entity, add_id, edit_id, view_id, descriptions["Add"]]
            for j, v in enumerate(vals):
                cell_text(r.cells[j], v, font_size=9)
                set_cell_bg(r.cells[j], bg)
            break
        # only first row per entity has entity name; show all 3 IDs inline
    else:
        continue
    # One row per entity (all 3 TCs)
    r = tbl2.rows[-1]

# Re-build the table properly (one row per entity, all 3 TCs in columns)
# Remove all data rows and rebuild
for _ in range(len(tbl2.rows) - 1):
    tbl = tbl2._tbl
    tbl.remove(tbl.findall(qn("w:tr"))[-1])

for idx, (entity, add_id, edit_id, view_id) in enumerate(ENTITIES):
    bg = row_colors[idx % 2]
    r = tbl2.add_row()
    vals = [entity, add_id, edit_id, view_id, "Add / Edit / View – full CRUD coverage"]
    for j, v in enumerate(vals):
        cell_text(r.cells[j], v, font_size=9)
        set_cell_bg(r.cells[j], bg)

doc.add_paragraph()

# ── Detailed steps for one entity (Container as example) ──────────────────────
add_sub_heading(doc, "Detailed Steps (Container — representative example)")

entity_detail = [
    # (TC ID, Title, Steps, Expected Result)
    (
        "TC-CON-01",
        "Add New Container",
        "1. Login → Navigate to Admin > Entities > Container\n"
        "2. Click '+ Add' toolbar button\n"
        "3. Fill: Container Name (random), Container Type (select), "
        "Total Volume, Max Allowed Volume, Volume UOM (select)\n"
        "4. Click Save",
        "New container row appears in the list grid.",
    ),
    (
        "TC-CON-02",
        "Edit Existing Container",
        "1. Login → Navigate to Container list\n"
        "2. Pick the first existing container row\n"
        "3. Click Edit, update Name, Type, Volume fields\n"
        "4. Click Save",
        "Updated container name visible in the list.",
    ),
    (
        "TC-CON-03",
        "View Container (Read-Only)",
        "1. Login → Navigate to Container list\n"
        "2. Pick an existing container row\n"
        "3. Click View – verify all fields are read-only\n"
        "4. Click Cancel (or browser back)",
        "Container details displayed; no changes made; list restored.",
    ),
]

det_cols = [("TC ID", 1.0), ("Test Case Title", 1.6), ("Test Steps", 3.5), ("Expected Result", 2.3)]
tbl3 = doc.add_table(rows=1, cols=4)
tbl3.style = "Table Grid"
header_row(tbl3, det_cols)
for i, (tc_id, title, steps, expected) in enumerate(entity_detail):
    bg = row_colors[i % 2]
    r = tbl3.add_row()
    for j, v in enumerate([tc_id, title, steps, expected]):
        cell_text(r.cells[j], v, font_size=9)
        set_cell_bg(r.cells[j], bg)

doc.add_paragraph()

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3 – Admin > Workcenter
# ═══════════════════════════════════════════════════════════════════════════════
doc.add_page_break()
add_section_heading(doc, "3. Admin > Workcenter — Test Cases")

wc_cases = [
    # (TC ID, File, Title, Steps, Expected)
    ("TC-WC-01", "Workcenter.py",
     "Create New Workcenter",
     "1. Login\n2. Admin > Workcenter > '+ Add'\n"
     "3. Fill Name, Code, Location; select Label = ebizkanban\n4. Save",
     "New workcenter row visible in list."),

    ("TC-WC-02", "Workcenter.py",
     "Edit Workcenter",
     "1. Search for created workcenter\n2. Click Edit\n"
     "3. Update Name, Code, Location\n4. Save",
     "Updated workcenter reflected in list."),

    ("TC-WC-03", "Workcenter.py",
     "Add Workcenter User",
     "1. Select workcenter → More Options > Users > '+ Add'\n"
     "2. Fill User ID, Password, First/Last Name, Email, Phone, Account Type\n3. Save",
     "New user appears in Workcenter User list."),

    ("TC-WC-04", "Workcenter.py",
     "Edit Workcenter User",
     "1. Select user in list → Edit\n"
     "2. Update First Name, Phone, Buyer Code\n3. Save",
     "Updated values visible in user list."),

    ("TC-WC-05", "Workcenter.py",
     "View Workcenter User",
     "1. Select user in list → View\n2. Verify all fields read-only\n3. Click Cancel",
     "User details displayed, no changes saved."),

    ("TC-WC-06", "Workcenter.py",
     "Disable / Enable Workcenter User",
     "1. Select active user → More Options > Disable → Confirm\n"
     "2. Verify status = Disabled\n"
     "3. More Options > Enable → Confirm\n4. Verify status = Active",
     "User status toggles correctly between Active and Disabled."),

    ("TC-WC-07", "Workcenter.py",
     "Add Shipping Rule",
     "1. More Options > Shipping Rules > Add Shipping Rule\n"
     "2. Select rule, fill Release Day and Ship Date links\n3. Apply → Save",
     "Shipping rule saved and visible in rules list."),

    ("TC-WC-08", "Workcenter.py",
     "Add RYG Rule",
     "1. More Options > RYG Rules > Add RYG Rule\n"
     "2. Select rule, fill threshold / value fields\n3. Save",
     "RYG rule saved successfully."),

    ("TC-WC-09", "Workcenter.py",
     "Kanban Formula Verification",
     "1. More Options > Kanban Formula\n"
     "2. Verify expression, functions, and field dropdowns are displayed\n3. Save",
     "Kanban formula page loads; save completes without error."),

    ("TC-WC-10", "Workcenter.py",
     "Add Attachment",
     "1. More Options > Attachment > Add Attachment\n"
     "2. Choose file from Desktop\n3. Upload File(s)",
     "Attachment visible in Attachment list."),

    ("TC-WC-11", "WorkcenterConfiguration.py",
     "Workcenter Configuration (All Tabs)",
     "1. Admin > Workcenter > select WC > More Options > Configuration\n"
     "2. Click each tab (General, Card, Custom, Integration, LFM, Pick List, "
     "Print, Receive, Release, Scan, Ship, Work Order)\n"
     "3. Update random values on each tab\n4. Save",
     "Configuration saved; all 12 tabs updated successfully."),

    ("TC-WC-12", "ProductionSequenceConfiguration.py",
     "Production Sequence Configuration (All Tabs)",
     "1. Admin > Workcenter > select WC > More Options > Production Sequence Configuration\n"
     "2. Click each tab (Schedule, Custom Field List, Sort Info, Scrap Tag, Screen Info, External Device Data Info)\n"
     "3. Update Available Production Hours & Schedule Offset\n4. Save",
     "PSC saved; all 6 tabs updated."),
]

wc_cols = [
    ("TC ID",    0.85),
    ("File",     1.7),
    ("Title",    1.6),
    ("Test Steps", 2.8),
    ("Expected Result", 1.65),
]
tbl4 = doc.add_table(rows=1, cols=5)
tbl4.style = "Table Grid"
header_row(tbl4, wc_cols)
for i, row in enumerate(wc_cases):
    bg = row_colors[i % 2]
    r = tbl4.add_row()
    for j, v in enumerate(row):
        cell_text(r.cells[j], v, font_size=9)
        set_cell_bg(r.cells[j], bg)

doc.add_paragraph()

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4 – Admin > Users
# ═══════════════════════════════════════════════════════════════════════════════
add_section_heading(doc, "4. Admin > Users — Test Cases")

user_cases = [
    ("TC-USR-01", "users.py",
     "Add New User",
     "1. Login → Admin > Users > '+ Add'\n"
     "2. Fill User ID (User170426), Password, First/Last Name, Email, Phone, Account Type\n3. Save",
     "New user row visible in Users list."),

    ("TC-USR-02", "users.py",
     "Edit Existing User",
     "1. Search for User170426\n2. Click Edit\n"
     "3. Update First Name, Phone, Buyer Code\n4. Save",
     "Updated values reflected in user list."),

    ("TC-USR-03", "users.py",
     "View User (Read-Only)",
     "1. Select User170426 → View\n"
     "2. Verify all fields are read-only\n3. Click Cancel",
     "User detail page shows all data; no edits possible."),

    ("TC-USR-04", "users.py",
     "Disable User",
     "1. Select active User170426 → More Options > Disable → Confirm 'Yes'",
     "User status changes to Disabled; no longer in Active list."),

    ("TC-USR-05", "users.py",
     "Enable (Re-activate) User",
     "1. Switch to Disabled list → Select user → More Options > Enable → Confirm 'Yes'",
     "User status returns to Active."),

    ("TC-USR-06", "UsercreationValidations.py",
     "Bulk User Creation (Manual List)",
     "1. Run TestCreateUsersManual\n"
     "2. Creates multiple users from hardcoded Python list\n"
     "3. Verify each user ID appears in Users list",
     "All users from the list created successfully."),

    ("TC-USR-07", "UsercreationValidations.py",
     "Bulk User Creation (Excel-Driven)",
     "1. Prepare users_to_create.xlsx with user data rows\n"
     "2. Run TestCreateUsersFromExcel\n"
     "3. Verify each user created in the application",
     "All Excel rows created as users in the application."),

    ("TC-USR-08", "UsercreationValidations.py",
     "Export User Credentials",
     "1. Run TestExportCredentials after bulk creation\n"
     "2. Generates a formatted Excel report with all user credentials",
     "Excel report created with user ID, password, account type columns."),
]

usr_cols = [
    ("TC ID",    0.85),
    ("File",     1.8),
    ("Title",    1.7),
    ("Test Steps", 2.6),
    ("Expected Result", 1.65),
]
tbl5 = doc.add_table(rows=1, cols=5)
tbl5.style = "Table Grid"
header_row(tbl5, usr_cols)
for i, row in enumerate(user_cases):
    bg = row_colors[i % 2]
    r = tbl5.add_row()
    for j, v in enumerate(row):
        cell_text(r.cells[j], v, font_size=9)
        set_cell_bg(r.cells[j], bg)

doc.add_paragraph()

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5 – Admin > Supplier
# ═══════════════════════════════════════════════════════════════════════════════
add_section_heading(doc, "5. Admin > Supplier — Internal Supplier Configuration")

sup_cases = [
    ("TC-SUP-01", "InternalSupplier.py",
     "Internal Supplier – Workcenter Configuration",
     "1. Login → Admin > Supplier\n"
     "2. Click 'Internal Supplier' tab\n"
     "3. Search 'WCLine' in Find Name\n"
     "4. Select WCLine row → More Options > Configuration\n"
     "5. On Supply Workcenter Configuration: click each tab, update random values\n"
     "6. Save",
     "Configuration saved successfully; all tab values persisted."),
]

sup_cols = [
    ("TC ID",    0.85),
    ("File",     1.8),
    ("Title",    1.6),
    ("Test Steps", 2.85),
    ("Expected Result", 1.55),
]
tbl6 = doc.add_table(rows=1, cols=5)
tbl6.style = "Table Grid"
header_row(tbl6, sup_cols)
for i, row in enumerate(sup_cases):
    bg = row_colors[i % 2]
    r = tbl6.add_row()
    for j, v in enumerate(row):
        cell_text(r.cells[j], v, font_size=9)
        set_cell_bg(r.cells[j], bg)

doc.add_paragraph()

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6 – Admin > Calendar
# ═══════════════════════════════════════════════════════════════════════════════
add_section_heading(doc, "6. Admin > Calendar — Holiday Management")

cal_cases = [
    ("TC-CAL-01", "Calender.py",
     "Add New Holiday",
     "1. Login → Admin > Calendar\n"
     "2. Click '+ Add'\n"
     "3. Enter Holiday Date and Description\n4. Save",
     "New holiday visible in Observed Holidays list."),

    ("TC-CAL-02", "Calender.py",
     "Edit Existing Holiday",
     "1. Navigate to Calendar List (2026)\n"
     "2. Select a holiday → Click Edit\n"
     "3. Modify Description\n4. Save",
     "Updated description reflected in holiday list."),

    ("TC-CAL-03", "Calender.py",
     "Add Range of Holidays",
     "1. Navigate to Calendar List (2026)\n"
     "2. Click 'Add Range' button\n"
     "3. Select Date Range from dropdown, enter Description\n4. Save",
     "Range of holidays added to the Observed Holidays list."),

    ("TC-CAL-04", "Calender.py",
     "Delete Holiday",
     "1. Navigate to Calendar List (2026)\n"
     "2. Select a holiday → Click Delete\n"
     "3. Confirm 'Yes' on the popup",
     "Holiday removed from the Observed Holidays list."),
]

cal_cols = [
    ("TC ID",    0.85),
    ("File",     1.3),
    ("Title",    1.6),
    ("Test Steps", 3.0),
    ("Expected Result", 1.85),
]
tbl7 = doc.add_table(rows=1, cols=5)
tbl7.style = "Table Grid"
header_row(tbl7, cal_cols)
for i, row in enumerate(cal_cases):
    bg = row_colors[i % 2]
    r = tbl7.add_row()
    for j, v in enumerate(row):
        cell_text(r.cells[j], v, font_size=9)
        set_cell_bg(r.cells[j], bg)

doc.add_paragraph()

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7 – Admin > Item
# ═══════════════════════════════════════════════════════════════════════════════
doc.add_page_break()
add_section_heading(doc, "7. Admin > Item — Item Creation & Loop Size")

item_cases = [
    ("TC-ITM-01", "NewItemCreationandAdjustLoopSize.py",
     "Create Items from Excel (Data1)",
     "1. Read item_test_data_1.xlsx (sheet: ItemData)\n"
     "2. For each row: login → Admin > Item → '+ Add' → fill all fields\n"
     "3. Add Supplier link → Save",
     "All Excel items created in application."),

    ("TC-ITM-02", "NewItemCreationandAdjustLoopSize.py",
     "Filter Items (Excel-Driven)",
     "1. Clear any existing filter\n"
     "2. For each item from Excel: apply Name filter\n"
     "3. Verify item appears in filtered list",
     "Each item correctly found via filter."),

    ("TC-ITM-03", "NewItemCreationandAdjustLoopSize.py",
     "Create Item IT010426",
     "1. Login → Admin > Item → '+ Add'\n"
     "2. Fill all mandatory fields for IT010426\n"
     "3. Add Supplier, Save",
     "IT010426 row appears in Item list."),

    ("TC-ITM-04", "NewItemCreationandAdjustLoopSize.py",
     "Create Item IT020426",
     "1. Login → Admin > Item → '+ Add'\n"
     "2. Fill all mandatory fields for IT020426\n"
     "3. Add Supplier, Save",
     "IT020426 row appears in Item list."),

    ("TC-ITM-05", "NewItemCreationandAdjustLoopSize.py",
     "Create Item IT070426",
     "1. Login → Admin > Item → '+ Add'\n"
     "2. Fill all mandatory fields for IT070426\n"
     "3. Add Supplier, Save",
     "IT070426 row appears in Item list."),

    ("TC-ITM-06", "NewItemCreationandAdjustLoopSize.py",
     "Set Initial Loop Size – IT020426",
     "1. Select IT020426 → More Options > Initial Loop Size\n"
     "2. Enter number of cards\n3. Save",
     "Initial loop size set; card count updated."),

    ("TC-ITM-07", "NewItemCreationandAdjustLoopSize.py",
     "Adjust Loop Size – IT020426",
     "1. Select IT020426 → More Options > Adjust Loop Size\n"
     "2. Enter adjusted card count\n3. Save",
     "Adjusted loop size saved; card count reflects new value."),

    ("TC-ITM-08", "NewItemCreationandAdjustLoopSize.py",
     "Excel Item – Initial Loop Size (IT-A140426)",
     "1. Select IT-A140426 (from Excel)\n"
     "2. More Options > Initial Loop Size → enter cards → Save",
     "Initial loop size set for Excel-driven item."),

    ("TC-ITM-09", "NewItemCreationandAdjustLoopSize.py",
     "Excel Item – Adjust Loop Size (IT-A140426)",
     "1. Select IT-A140426 → More Options > Adjust Loop Size\n"
     "2. Enter adjustment → Save",
     "Loop size adjusted for Excel-driven item."),

    ("TC-ITM-10", "NewItemCreationandAdjustLoopSize.py",
     "Create ITTest232 (Kanban)",
     "1. Login → Admin > Item → '+ Add'\n"
     "2. Fill fields for ITTest232 with Kanban type\n3. Save",
     "ITTest232 created; Kanban cards generated."),

    ("TC-ITM-11", "NewItemCreationandAdjustLoopSize.py",
     "Initial Loop Size – ITTest232",
     "1. Select ITTest232 → More Options > Initial Loop Size → Save",
     "Initial loop size set for ITTest232."),

    ("TC-ITM-12", "NewItemCreationandAdjustLoopSize.py",
     "Adjust Loop Size – ITTest232",
     "1. Select ITTest232 → More Options > Adjust Loop Size → Save",
     "Loop size adjusted for ITTest232."),

    ("TC-ITM-13", "NewItemCreationandAdjustLoopSize.py",
     "Create ITDDDD + Full Loop Cycle",
     "1. Create item ITDDDD\n"
     "2. Set Initial Loop Size\n3. Adjust Loop Size\n4. Verify card count",
     "ITDDDD created with correct loop size after both operations."),

    ("TC-ITM-14", "NewItemCreationandAdjustLoopSize.py",
     "Excel-Driven: Create + Adjust Loop (Run_Adjust_Loop=Yes)",
     "1. Read Excel rows where Run_Adjust_Loop=Yes\n"
     "2. For each row: create item + set initial loop + adjust loop\n"
     "3. Verify all steps pass",
     "All flagged Excel items created with loop size fully adjusted."),
]

itm_cols = [
    ("TC ID",    0.85),
    ("File",     2.3),
    ("Title",    1.7),
    ("Test Steps", 2.5),
    ("Expected Result", 1.25),
]
tbl8 = doc.add_table(rows=1, cols=5)
tbl8.style = "Table Grid"
header_row(tbl8, itm_cols)
for i, row in enumerate(item_cases):
    bg = row_colors[i % 2]
    r = tbl8.add_row()
    for j, v in enumerate(row):
        cell_text(r.cells[j], v, font_size=9)
        set_cell_bg(r.cells[j], bg)

doc.add_paragraph()

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 8 – Test Environment
# ═══════════════════════════════════════════════════════════════════════════════
add_section_heading(doc, "8. Test Environment & Tools")

env_data = [
    ("Application URL",   "https://engineering.ultrivalms.com/QALS1011"),
    ("Test User",         "buyeruser / Ultriva!23"),
    ("Browser",           "Google Chrome (maximised, 1920×1080)"),
    ("Automation Tool",   "Python 3 + Selenium WebDriver + pytest"),
    ("Framework",         "pytest (class-scoped fixtures, HTML reports)"),
    ("Reports Location",  "qa_automation/reports/"),
    ("Test Data",         "qa_automation/test_data/ (Excel .xlsx files)"),
    ("Week Covered",      "April 28 – May 1, 2026"),
]

env_cols = [("Parameter", 2.0), ("Value", 5.0)]
tbl9 = doc.add_table(rows=1, cols=2)
tbl9.style = "Table Grid"
header_row(tbl9, env_cols, bg="2E74B5")
for i, (param, value) in enumerate(env_data):
    bg = row_colors[i % 2]
    r = tbl9.add_row()
    cell_text(r.cells[0], param, bold=True, font_size=9)
    cell_text(r.cells[1], value, font_size=9)
    for j in range(2):
        set_cell_bg(r.cells[j], bg)

doc.add_paragraph()

# ── Footer note ───────────────────────────────────────────────────────────────
add_note(doc, "All test cases use randomised test data to avoid conflicts across runs. "
              "Tests are independent and can be run individually or as a full suite.")

# ─── Save ─────────────────────────────────────────────────────────────────────
OUTPUT = r"c:\Prcatices-AI\Weekly_TestCases_Apr28_May1_2026.docx"
doc.save(OUTPUT)
print(f"Document saved: {OUTPUT}")
