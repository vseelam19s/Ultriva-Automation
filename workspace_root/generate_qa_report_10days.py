"""
Generate QA Test Cases Report (Last 10 Days: Apr 24 – May 4, 2026)
"""
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import datetime

doc = Document()

# ── Page margins ──────────────────────────────────────────────────────────────
for section in doc.sections:
    section.top_margin    = Inches(0.75)
    section.bottom_margin = Inches(0.75)
    section.left_margin   = Inches(0.9)
    section.right_margin  = Inches(0.9)

# ── Helpers ───────────────────────────────────────────────────────────────────
def set_cell_bg(cell, hex_color):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), hex_color)
    shd.set(qn("w:val"), "clear")
    tcPr.append(shd)

def header_row(table, cols, bg="1F4E79"):
    row = table.rows[0]
    for i, txt in enumerate(cols):
        cell = row.cells[i]
        set_cell_bg(cell, bg)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(txt)
        run.bold = True
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        run.font.size = Pt(9)

def add_row(table, values, bg=None, bold_first=False):
    row = table.add_row()
    for i, val in enumerate(values):
        cell = row.cells[i]
        if bg:
            set_cell_bg(cell, bg)
        p = cell.paragraphs[0]
        run = p.add_run(str(val))
        run.font.size = Pt(9)
        if bold_first and i == 0:
            run.bold = True
    return row

def section_heading(text, level=1):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(12 if level == 1 else 10)
    run.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after  = Pt(4)

# ── Title ─────────────────────────────────────────────────────────────────────
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = title.add_run("QA Automation Test Cases Report")
run.bold = True
run.font.size = Pt(16)
run.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)

sub = doc.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
run2 = sub.add_run("Ultriva Lean Suite – QALS1011 | Period: Apr 24 – May 4, 2026")
run2.font.size = Pt(10)
run2.font.color.rgb = RGBColor(0x44, 0x44, 0x44)

run3 = sub.add_run(f"\nGenerated: {datetime.date.today().strftime('%B %d, %Y')}  |  Site: engineering.ultrivalms.com/QALS1011  |  User: buyeruser")
run3.font.size = Pt(9)
run3.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

doc.add_paragraph()

# ── Summary Table ─────────────────────────────────────────────────────────────
section_heading("1. Summary Overview")

summary_data = [
    ("Admin > External Supplier",           "6 classes",  "44",  "ExternalSupplier.py"),
    ("Admin > Entities > ABC Code",          "1 module",   "4",   "ABCCode.py"),
    ("Admin > Entities > Break Reason Code", "1 module",   "3",   "BreakReasonCode.py"),
    ("Admin > Entities > Carrier",           "1 module",   "3",   "Carrier.py"),
    ("Admin > Entities > Commodity Code",    "1 module",   "1",   "CommodityCode.py"),
    ("Admin > Entities > Container",         "1 module",   "3",   "Container.py"),
    ("Admin > Entities > Exception Code",    "1 module",   "3",   "ExceptionCode.py"),
    ("Admin > Entities > Location Code",     "1 module",   "3",   "LocationCode.py"),
    ("Admin > Entities > Logistics Mode",    "1 module",   "3",   "LogisticsMode.py"),
    ("Admin > Entities > Machine",           "1 module",   "3",   "Machine.py"),
    ("Admin > Entities > Notes",             "1 module",   "3",   "Notes.py"),
    ("Admin > Entities > Operation",         "1 module",   "3",   "Operation.py"),
    ("Admin > Entities > Operation Params",  "1 module",   "3",   "OperationParams.py"),
    ("Admin > Entities > Printer",           "1 module",   "3",   "Printer.py"),
    ("Admin > Entities > Production Issue",  "1 module",   "3",   "ProductionIssue.py"),
    ("Admin > Entities > Reschedule Reason", "1 module",   "3",   "RescheduleReason.py"),
    ("Admin > Entities > Route",             "1 module",   "3",   "Route.py"),
    ("Admin > Entities > Scrap Reason",      "1 module",   "3",   "ScrapReason.py"),
    ("Admin > Entities > Skip Lot Plan",     "1 module",   "3",   "SkipLotPlan.py"),
    ("Admin > Entities > Unit of Measure",   "1 module",   "3",   "UnitOfMeasure.py"),
    ("Admin > Business Unit",                "1 module",   "1",   "BussinessUnit.py"),
    ("Admin > Dropoff Location",             "1 module",   "3",   "DropOffLocation.py"),
    ("Admin > Shift",                        "1 module",   "3",   "Shifts.py"),
]

total_tcs = sum(int(r[2]) for r in summary_data)

t = doc.add_table(rows=1, cols=4)
t.style = "Table Grid"
t.alignment = WD_TABLE_ALIGNMENT.CENTER
header_row(t, ["Menu / Module", "Scope", "Test Cases", "File"])

alt_colors = ["DEEAF1", "FFFFFF"]
for idx, row_data in enumerate(summary_data):
    bg = alt_colors[idx % 2]
    r = add_row(t, row_data, bg=bg)

# Totals row
tot = t.add_row()
set_cell_bg(tot.cells[0], "1F4E79")
set_cell_bg(tot.cells[1], "1F4E79")
set_cell_bg(tot.cells[2], "1F4E79")
set_cell_bg(tot.cells[3], "1F4E79")
for i, val in enumerate(["TOTAL", f"{len(summary_data)} modules", str(total_tcs), ""]):
    p = tot.cells[i].paragraphs[0]
    run = p.add_run(val)
    run.bold = True
    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    run.font.size = Pt(9)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

# Column widths
col_widths = [3.2, 1.1, 1.0, 2.0]
for i, w in enumerate(col_widths):
    for row in t.rows:
        row.cells[i].width = Inches(w)

doc.add_paragraph()

# ── Section 2: External Supplier ──────────────────────────────────────────────
section_heading("2. Admin > External Supplier  (File: ExternalSupplier.py)")

ext_data = [
    # Class, TC ID, Description, Type
    ("TestExternalSupplier",       "TC-ES-01", "Login & navigate to supplier admin",       "Setup"),
    ("TestExternalSupplier",       "TC-ES-02", "Add new external supplier",                "Add"),
    ("TestExternalSupplier",       "TC-ES-03", "Edit existing supplier",                   "Edit"),
    ("TestExternalSupplier",       "TC-ES-04", "View supplier details",                    "View"),
    ("TestExternalSupplier",       "TC-ES-05", "Open add supplier user form",              "Add User"),
    ("TestExternalSupplier",       "TC-ES-06", "Fill & save supplier user",                "Save"),
    ("TestExternalSupplier",       "TC-ES-07", "Generate summary report",                  "Report"),
    ("TestSupplierConfiguration",  "TC-SC-01", "Login to app",                             "Setup"),
    ("TestSupplierConfiguration",  "TC-SC-02", "Open supplier list",                       "Navigate"),
    ("TestSupplierConfiguration",  "TC-SC-03", "Select supplier & open config",            "Navigate"),
    ("TestSupplierConfiguration",  "TC-SC-04", "Update General tab",                       "Edit"),
    ("TestSupplierConfiguration",  "TC-SC-05", "Update Card tab",                          "Edit"),
    ("TestSupplierConfiguration",  "TC-SC-06", "Update Custom tab",                        "Edit"),
    ("TestSupplierConfiguration",  "TC-SC-07", "Update Invoice tab",                       "Edit"),
    ("TestSupplierConfiguration",  "TC-SC-08", "Update Print tab",                         "Edit"),
    ("TestSupplierConfiguration",  "TC-SC-09", "Update Receive tab",                       "Edit"),
    ("TestSupplierConfiguration",  "TC-SC-10", "Update Scan tab",                          "Edit"),
    ("TestSupplierConfiguration",  "TC-SC-11", "Update Ship tab",                          "Edit"),
    ("TestSupplierConfiguration",  "TC-SC-12", "Generate summary report",                  "Report"),
    ("TestAssignSupplier",         "TC-AS-01", "Login to app",                             "Setup"),
    ("TestAssignSupplier",         "TC-AS-02", "Open external supplier list",              "Navigate"),
    ("TestAssignSupplier",         "TC-AS-03", "Click associate supplier button",          "Action"),
    ("TestAssignSupplier",         "TC-AS-04", "Show unassigned suppliers",                "View"),
    ("TestAssignSupplier",         "TC-AS-05", "Select supplier checkbox",                 "Action"),
    ("TestAssignSupplier",         "TC-AS-06", "Enter supplier code",                      "Input"),
    ("TestAssignSupplier",         "TC-AS-07", "Click Assign & verify assignment",         "Assign"),
    ("TestAssignSupplier",         "TC-AS-08", "Select assigned supplier for removal",     "Action"),
    ("TestAssignSupplier",         "TC-AS-09", "Click Remove button",                      "Delete"),
    ("TestAssignSupplier",         "TC-AS-10", "Confirm removal & verify",                 "Verify"),
    ("TestShippingRules",          "TC-SR-01", "Login to app",                             "Setup"),
    ("TestShippingRules",          "TC-SR-02", "Open supplier list",                       "Navigate"),
    ("TestShippingRules",          "TC-SR-03", "Open shipping rules tab",                  "Navigate"),
    ("TestShippingRules",          "TC-SR-04", "Click Add Shipping Rule",                  "Add"),
    ("TestShippingRules",          "TC-SR-05", "Select rule & confirm",                    "Save"),
    ("TestSupplierCalendar",       "TC-CAL-01","Login to app",                             "Setup"),
    ("TestSupplierCalendar",       "TC-CAL-02","Open supplier list",                       "Navigate"),
    ("TestSupplierCalendar",       "TC-CAL-03","Open supplier calendar",                   "Navigate"),
    ("TestSupplierCalendar",       "TC-CAL-04","Click Add Holiday button",                 "Add"),
    ("TestSupplierCalendar",       "TC-CAL-05","Fill & save holiday entry",                "Save"),
    ("TestSupplierCalendar",       "TC-CAL-06","Verify holiday appears in list",           "Verify"),
    ("TestSupplierCalendar",       "TC-CAL-07","Generate summary report",                  "Report"),
    ("TestSupplierCalendar",       "TC-CAL-08","Add multiple holiday date ranges",         "Add"),
    ("TestShippingRulesSteps",     "TC-SRS-01","Fill mandatory shipping rule links",       "Edit"),
    ("TestShippingRulesSteps",     "TC-SRS-02","Save shipping rule",                       "Save"),
]

t2 = doc.add_table(rows=1, cols=4)
t2.style = "Table Grid"
t2.alignment = WD_TABLE_ALIGNMENT.CENTER
header_row(t2, ["Test Class", "TC ID", "Description", "Type"])

prev_class = ""
for idx, (cls, tcid, desc, typ) in enumerate(ext_data):
    bg = "DEEAF1" if idx % 2 == 0 else "FFFFFF"
    add_row(t2, [cls if cls != prev_class else "", tcid, desc, typ], bg=bg)
    prev_class = cls

for i, w in enumerate([1.8, 0.9, 3.5, 0.8]):
    for row in t2.rows:
        row.cells[i].width = Inches(w)

doc.add_paragraph()

# ── Section 3: Entities ────────────────────────────────────────────────────────
section_heading("3. Admin > Entities  (Folder: admin/Entities/)")

entities_data = [
    # Module, TC-ID, Description, Type
    ("ABC Code",          "TC-ABC-01",       "Add a new ABC Code",                        "Add"),
    ("ABC Code",          "TC-ABC-02",       "Edit an existing ABC Code",                 "Edit"),
    ("ABC Code",          "TC-ABC-03",       "View ABC Code and cancel",                  "View"),
    ("ABC Code",          "TC-ABC-04",       "Assign Items to ABC Code",                  "Assign"),
    ("Break Reason Code", "TC-BR-01",        "Add a new Break Reason Code",               "Add"),
    ("Break Reason Code", "TC-BR-02",        "Edit an existing Break Reason Code",        "Edit"),
    ("Break Reason Code", "TC-BR-03",        "View Break Reason Code and cancel",         "View"),
    ("Carrier",           "TC-CAR-01",       "Add a new Carrier",                         "Add"),
    ("Carrier",           "TC-CAR-02",       "Edit an existing Carrier",                  "Edit"),
    ("Carrier",           "TC-CAR-03",       "View Carrier and cancel",                   "View"),
    ("Commodity Code",    "TC-CC-01",        "Add RYG Rule to Commodity Code",            "RYG Rule"),
    ("Container",         "TC-CON-01",       "Add a new Container",                       "Add"),
    ("Container",         "TC-CON-02",       "Edit an existing Container",                "Edit"),
    ("Container",         "TC-CON-03",       "View Container and cancel",                 "View"),
    ("Exception Code",    "TC-EC-01",        "Add a new Exception Code",                  "Add"),
    ("Exception Code",    "TC-EC-02",        "Edit an existing Exception Code",           "Edit"),
    ("Exception Code",    "TC-EC-03",        "View Exception Code and cancel",            "View"),
    ("Location Code",     "TC-LC-01",        "Add a new Location Code",                   "Add"),
    ("Location Code",     "TC-LC-02",        "Edit an existing Location Code",            "Edit"),
    ("Location Code",     "TC-LC-03",        "View Location Code and cancel",             "View"),
    ("Logistics Mode",    "TC-LM-01",        "Add a new Logistics Mode",                  "Add"),
    ("Logistics Mode",    "TC-LM-02",        "Edit an existing Logistics Mode",           "Edit"),
    ("Logistics Mode",    "TC-LM-03",        "View Logistics Mode and cancel",            "View"),
    ("Machine",           "TC-MC-01",        "Add a new Machine",                         "Add"),
    ("Machine",           "TC-MC-02",        "Edit an existing Machine",                  "Edit"),
    ("Machine",           "TC-MC-03",        "View Machine and cancel",                   "View"),
    ("Notes",             "TC-NOT-01",       "Add a new Note code",                       "Add"),
    ("Notes",             "TC-NOT-02",       "Edit an existing Note code",                "Edit"),
    ("Notes",             "TC-NOT-03",       "View Note code and cancel",                 "View"),
    ("Operation",         "TC-OP-01",        "Add a new Operation",                       "Add"),
    ("Operation",         "TC-OP-02",        "Edit an existing Operation",                "Edit"),
    ("Operation",         "TC-OP-03",        "View Operation and cancel",                 "View"),
    ("Operation Params",  "TC-OP-PARAMS-01", "Add a new Operation Params entry",          "Add"),
    ("Operation Params",  "TC-OP-PARAMS-02", "Edit an existing Operation Params entry",  "Edit"),
    ("Operation Params",  "TC-OP-PARAMS-03", "View Operation Params entry and cancel",   "View"),
    ("Printer",           "TC-PR-01",        "Add a new Printer",                         "Add"),
    ("Printer",           "TC-PR-02",        "Edit an existing Printer",                  "Edit"),
    ("Printer",           "TC-PR-03",        "View Printer and cancel",                   "View"),
    ("Production Issue",  "TC-PI-01",        "Add a new Production Issue code",           "Add"),
    ("Production Issue",  "TC-PI-02",        "Edit an existing Production Issue code",    "Edit"),
    ("Production Issue",  "TC-PI-03",        "View Production Issue code and cancel",     "View"),
    ("Reschedule Reason", "TC-RR-01",        "Add a new Reschedule Reason",               "Add"),
    ("Reschedule Reason", "TC-RR-02",        "Edit an existing Reschedule Reason",        "Edit"),
    ("Reschedule Reason", "TC-RR-03",        "View Reschedule Reason and cancel",         "View"),
    ("Route",             "TC-RT-01",        "Add a new Route code",                      "Add"),
    ("Route",             "TC-RT-02",        "Edit an existing Route code",               "Edit"),
    ("Route",             "TC-RT-03",        "View Route code and cancel",                "View"),
    ("Scrap Reason",      "TC-SR-01",        "Add a new Scrap Reason",                    "Add"),
    ("Scrap Reason",      "TC-SR-02",        "Edit an existing Scrap Reason",             "Edit"),
    ("Scrap Reason",      "TC-SR-03",        "View Scrap Reason and cancel",              "View"),
    ("Skip Lot Plan",     "TC-SLP-01",       "Add a new Skip Lot Plan",                   "Add"),
    ("Skip Lot Plan",     "TC-SLP-02",       "Edit an existing Skip Lot Plan",            "Edit"),
    ("Skip Lot Plan",     "TC-SLP-03",       "View Skip Lot Plan and cancel",             "View"),
    ("Unit of Measure",   "TC-UOM-01",       "Add a new Unit of Measure",                 "Add"),
    ("Unit of Measure",   "TC-UOM-02",       "Edit an existing Unit of Measure",          "Edit"),
    ("Unit of Measure",   "TC-UOM-03",       "View Unit of Measure and cancel",           "View"),
]

t3 = doc.add_table(rows=1, cols=4)
t3.style = "Table Grid"
t3.alignment = WD_TABLE_ALIGNMENT.CENTER
header_row(t3, ["Module", "TC ID", "Description", "Type"])

prev_mod = ""
for idx, (mod, tcid, desc, typ) in enumerate(entities_data):
    bg = "DEEAF1" if idx % 2 == 0 else "FFFFFF"
    add_row(t3, [mod if mod != prev_mod else "", tcid, desc, typ], bg=bg)
    prev_mod = mod

for i, w in enumerate([1.5, 1.4, 3.3, 0.9]):
    for row in t3.rows:
        row.cells[i].width = Inches(w)

doc.add_paragraph()

# ── Section 4: Admin Direct ────────────────────────────────────────────────────
section_heading("4. Admin (Direct Menus)")

admin_data = [
    ("Business Unit",    "BussinessUnit.py",   "TC-BU-01",      "Update Business Unit Configuration (edit address, save)", "Edit"),
    ("Dropoff Location", "DropOffLocation.py", "TC-DOL-01",     "Add a new Dropoff Location",                              "Add"),
    ("Dropoff Location", "DropOffLocation.py", "TC-DOL-02",     "Edit an existing Dropoff Location",                       "Edit"),
    ("Dropoff Location", "DropOffLocation.py", "TC-DOL-03",     "View Dropoff Location and cancel",                        "View"),
    ("Shift",            "Shifts.py",          "TC-SHIFT-01",   "Add a new Shift (name, start time, duration, break)",     "Add"),
    ("Shift",            "Shifts.py",          "TC-SHIFT-02",   "Edit an existing Shift (rename with _ED suffix)",         "Edit"),
    ("Shift",            "Shifts.py",          "TC-SHIFT-03",   "View Shift details and return to list",                   "View"),
]

t4 = doc.add_table(rows=1, cols=5)
t4.style = "Table Grid"
t4.alignment = WD_TABLE_ALIGNMENT.CENTER
header_row(t4, ["Menu", "File", "TC ID", "Description", "Type"])

prev_menu = ""
for idx, (menu, fil, tcid, desc, typ) in enumerate(admin_data):
    bg = "DEEAF1" if idx % 2 == 0 else "FFFFFF"
    add_row(t4, [menu if menu != prev_menu else "", fil, tcid, desc, typ], bg=bg)
    prev_menu = menu

for i, w in enumerate([1.2, 1.4, 1.0, 2.9, 0.7]):
    for row in t4.rows:
        row.cells[i].width = Inches(w)

doc.add_paragraph()

# ── Footer note ───────────────────────────────────────────────────────────────
note = doc.add_paragraph()
run = note.add_run(
    f"Total Test Cases Automated: {total_tcs + len(ext_data) + len(entities_data) - len(summary_data) + len(admin_data)}   |   "
    "Framework: Selenium 4 + Python 3.11   |   "
    "Environment: QA – QALS1011   |   "
    "All test cases validated on live QA site."
)
# Correct total
run.font.size = Pt(8)
run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
note.alignment = WD_ALIGN_PARAGRAPH.CENTER

# Print real total
real_total = len(ext_data) + len(entities_data) + len(admin_data)
print(f"Total TCs in document: {real_total}")

out_path = r"C:\Prcatices-AI\QA_TestCases_Report_Apr24_May4_2026.docx"
doc.save(out_path)
print(f"Report saved: {out_path}")
