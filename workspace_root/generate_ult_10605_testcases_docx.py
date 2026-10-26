"""Generate ULT-10605 (Force Steel Origin at supplier-item level) test cases DOCX."""
from pathlib import Path
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = Path(r"c:\Prcatices-AI\docs\ULT-10605_test_cases.docx")

COLS = ["ID", "Title", "Preconditions", "Steps", "Expected Result", "Pri", "Type", "AC"]
WIDTHS = [0.55, 1.35, 1.55, 2.6, 2.3, 0.4, 0.7, 0.45]

PRE_EXT = "Item I1 has external supplier SUP-A (Supplier Type != Workcenter). Logged in as Admin with ADMIN > ITEM > EDIT."
PRE_INT = "Item I2 has workcenter supplier WC-1 (IsSupplierWorkcenter = true). Logged in as Admin with ADMIN > ITEM > EDIT."
PRE_AB = "Item I1 supplied by external SUP-A and SUP-B; item I3 also supplied by SUP-A. None configured for Steel Origin."

SECTIONS = [
    ("1. UI - Default State and Availability", [
        ("TC-01", "Checkbox unchecked by default (never configured)",
         PRE_EXT + " I1/SUP-A has never had forcesteelorigin set.",
         "1. Go to ADMIN > ITEM and open I1.\n2. Open the supplier settings (flex parameters) for SUP-A.",
         "'Force Steel Origin' checkbox is displayed and unchecked.", "High", "Functional", "AC1"),
        ("TC-02", "Legacy supplier-item with no key in IGParams defaults to N",
         "Supplier-item row whose IGParams has other keys (e.g. pick.repack) but no forcesteelorigin key.",
         "1. Open the item and the supplier settings for that supplier.\n2. Verify checkbox state.\n3. Save without changing the checkbox.",
         "Checkbox unchecked. After save the value is stored as N or key remains absent; no error.", "High", "Functional", "AC1"),
        ("TC-03", "Checkbox available for external supplier",
         PRE_EXT,
         "1. Open I1 and the settings for external supplier SUP-A.\n2. Inspect the flex section (SK_EX_I2S_IGParams).",
         "'Force Steel Origin' is displayed as an iPhone-style checkbox with header text 'Force Steel Origin'.", "High", "Functional", "AC2"),
        ("TC-04", "Checkbox available for internal (workcenter) supplier",
         PRE_INT,
         "1. Open I2 and the settings for workcenter supplier WC-1.\n2. Inspect the flex section (SK_I2S_IGParams).",
         "'Force Steel Origin' checkbox is displayed alongside pick.repack, from.loc and frmloc.ctrl; unchecked by default.", "High", "Functional", "AC2"),
        ("TC-05", "Existing flex fields still displayed and unaffected",
         PRE_INT,
         "1. Open the supplier settings for WC-1 and SUP-A.\n2. Verify pick.repack, from.loc, frmloc.ctrl (internal) and existing external flex fields.",
         "All pre-existing fields are still shown, in the same order, and the new checkbox does not break layout.", "Medium", "Regression", "AC2"),
        ("TC-06", "Customer override configs do not hide the new key",
         "Environments/configs using CustomBaseLineUIConfig, CustomQAUIConfig, CustomLFUIConfig, CustomTFUSAUIConfig and CEK_LifeFitness CustomLFUIConfig.",
         "1. For each customer config, open an item with an external supplier.\n2. Repeat with a workcenter supplier.\n3. Check for 'Force Steel Origin'.",
         "Checkbox is visible for both supplier types in every customer config (override FlexConfigurations inherit the new key).", "High", "Config", "AC2"),
    ]),
    ("2. Save / Storage", [
        ("TC-07", "Enable for one supplier-item only (Supplier A)",
         PRE_AB,
         "1. Open I1 > supplier settings for SUP-A.\n2. Check 'Force Steel Origin'.\n3. Save.\n4. Query EboKanbanItems2Suppliers.IGParams for I1/SUP-A.",
         "Save succeeds. IGParams for I1/SUP-A contains forcesteelorigin=Y.", "High", "Functional", "AC3"),
        ("TC-08", "Other supplier of the same item unchanged",
         "TC-07 completed.",
         "1. Open I1 > supplier settings for SUP-B.\n2. Check IGParams of I1/SUP-B in DB.",
         "Checkbox unchecked for SUP-B. IGParams of I1/SUP-B is unchanged (no forcesteelorigin=Y).", "High", "Functional", "AC3"),
        ("TC-09", "Other items for the same supplier unchanged",
         "TC-07 completed.",
         "1. Open I3 > supplier settings for SUP-A.\n2. Check IGParams of I3/SUP-A in DB.",
         "Checkbox unchecked for I3/SUP-A. IGParams unchanged.", "High", "Functional", "AC3"),
        ("TC-10", "Disable - uncheck and save",
         "I1/SUP-A has forcesteelorigin=Y.",
         "1. Open I1 > supplier settings for SUP-A.\n2. Uncheck 'Force Steel Origin'.\n3. Save.\n4. Re-open the settings and check DB.",
         "Checkbox unchecked after reload. IGParams has forcesteelorigin=N (or key removed). IsSteelOriginForcedAtShip returns false for new cards.", "High", "Functional", "AC4"),
        ("TC-11", "Enable for workcenter supplier",
         PRE_INT,
         "1. Check 'Force Steel Origin' for WC-1 on I2.\n2. Save and re-open.\n3. Check DB.",
         "Value persisted as Y in I2/WC-1 IGParams; checkbox checked on reload.", "High", "Functional", "AC2/AC3"),
        ("TC-12", "Enable for both suppliers of the same item independently",
         PRE_AB,
         "1. Check the flag for SUP-A, save.\n2. Check the flag for SUP-B, save.\n3. Uncheck SUP-A, save.",
         "After each step only the intended supplier-item changes. Final state: SUP-A = N, SUP-B = Y.", "Medium", "Functional", "AC3"),
        ("TC-13", "Value persists after logout / re-login and page refresh",
         "I1/SUP-A flagged Y.",
         "1. Log out and log in.\n2. Open I1 > SUP-A settings.",
         "Checkbox still checked.", "Medium", "Functional", "AC3"),
        ("TC-14", "Viewer (read-only) mode shows the saved value",
         "I1/SUP-A flagged Y; user with view-only access to the item (InitSupplierItemFlexParam4Viewer path).",
         "1. Open I1 in view mode and inspect SUP-A settings.",
         "'Force Steel Origin' is shown as checked and is not editable.", "Medium", "Functional", "AC3"),
        ("TC-15", "Add new supplier to an item with flag checked",
         "Admin with ITEM ADD/EDIT; item I4 with no supplier assigned.",
         "1. Open I4 and add supplier SUP-A.\n2. In flex settings check 'Force Steel Origin'.\n3. Save.\n4. Check DB.",
         "New I4/SUP-A row is created with forcesteelorigin=Y.", "High", "Functional", "AC3"),
        ("TC-16", "Saving other flex fields preserves forcesteelorigin",
         "I1/SUP-A flagged Y.",
         "1. Change another flex field (e.g. a pick.repack / other supplier-item field) on I1/SUP-A.\n2. Save.\n3. Check IGParams.",
         "forcesteelorigin=Y is retained along with the other changed values.", "High", "Regression", "AC3"),
        ("TC-17", "Saving forcesteelorigin preserves other flex fields",
         "I1/SUP-A has other flex values set.",
         "1. Check 'Force Steel Origin' only.\n2. Save.\n3. Check IGParams.",
         "Existing flex keys/values remain intact; only forcesteelorigin is added.", "High", "Regression", "AC3"),
        ("TC-18", "Stored in supplier-item IGParams, not item-level IGParams",
         PRE_AB,
         "1. Flag I1/SUP-A.\n2. Inspect EboKanbanItems.IGParams for I1 and EboKanbanItems2Suppliers.IGParams for I1/SUP-A and I1/SUP-B.",
         "forcesteelorigin appears only in EboKanbanItems2Suppliers.IGParams of I1/SUP-A. EboKanbanItems.IGParams has no forcesteelorigin key (decision D1).", "High", "Functional", "AC3"),
        ("TC-19", "Independent of item-level Force Packing Slip No",
         PRE_AB,
         "1. Check item-level 'Force Packing Slip No' on I1 and save.\n2. Verify Steel Origin for SUP-A and SUP-B.\n3. Then set Steel Origin on SUP-A and clear Packing Slip.",
         "Toggling one never changes the other. forcepkslip remains in EboKanbanItems.IGParams; forcesteelorigin stays supplier-item level.", "Medium", "Regression", "AC3"),
        ("TC-20", "Save via the supplier-item (KanbanItem2Supplier) path",
         "Supplier-item edit screen reachable through KanbanItem2SupplierController.",
         "1. Edit the supplier-item through this path.\n2. Check 'Force Steel Origin' and save.\n3. Re-open via the Item page.",
         "Value saved and shown consistently in both entry points.", "Medium", "Functional", "AC3"),
    ]),
    ("3. Rule Constant and Helper", [
        ("TC-21", "FORCE_STEEL_ORIGIN_EXPR defined correctly",
         "Code access.",
         "1. Open EboStaticActionHelper.cs near FORCE_PACKING_SLIP_EXPR / FROM_LOC_REQ_AT_SHIP_EXPR.",
         "const string FORCE_STEEL_ORIGIN_EXPR = \"(I2S_IGParams.forcesteelorigin='Y')\" exists.", "Medium", "Code review", "-"),
        ("TC-22", "IsSteelOriginForcedAtShip returns true for flagged card",
         "Kanban card of I1 supplied by SUP-A (flag = Y).",
         "1. Call IsSteelOriginForcedAtShip(session, cardGID).",
         "Returns true.", "High", "Functional", "AC3"),
        ("TC-23", "IsSteelOriginForcedAtShip returns false for unflagged supplier-item",
         "Cards: I1/SUP-B (no key), I3/SUP-A (no key), and a card with forcesteelorigin=N.",
         "1. Call the helper for each card.",
         "Returns false for all.", "High", "Functional", "AC3/AC4"),
        ("TC-24", "Helper reflects disable",
         "Card of I1/SUP-A; flag Y then changed to N.",
         "1. Call the helper before and after unchecking and saving.",
         "true before, false after.", "High", "Functional", "AC4"),
        ("TC-25", "Helper with invalid / non-existent CardGID",
         "None.",
         "1. Call the helper with an unknown GID, empty string and null.",
         "Returns false without exception.", "Low", "Negative", "-"),
        ("TC-26", "I2S_IGParams exposed in EboQueueKanbanCardsView",
         "DB access.",
         "1. Run: SELECT TOP 10 I2S_IGParams FROM EboQueueKanbanCardsView WHERE I2S_IGParams LIKE '%forcesteelorigin=Y%'.",
         "Column exists and returns the flagged supplier-item IGParams.", "Medium", "DB", "-"),
    ]),
    ("4. Permissions", [
        ("TC-27", "Admin with ITEM EDIT can change the flag",
         "User has ADMIN > ITEM > EDIT.",
         "1. Open an item, toggle 'Force Steel Origin', save.",
         "Change is saved.", "High", "Security", "-"),
        ("TC-28", "Admin with ITEM ADD can set the flag on a new item/supplier",
         "User has ADMIN > ITEM > ADD.",
         "1. Create a new item with a supplier and check 'Force Steel Origin'. Save.",
         "Saved with forcesteelorigin=Y.", "Medium", "Security", "-"),
        ("TC-29", "User without ITEM EDIT cannot change the flag",
         "User lacks ADMIN > ITEM > EDIT (view only or no access).",
         "1. Open the item page / attempt save with modified flag.",
         "Flag is read-only or the page is not accessible; no change persisted.", "High", "Security", "-"),
        ("TC-30", "No new right introduced",
         "Rights/roles admin page.",
         "1. Review the rights list for a new Steel Origin permission.",
         "No new right exists; existing ITEM page node governs the setting.", "Low", "Security", "-"),
    ]),
    ("5. Support Query - SteelOrigin_FlaggedSupplierItems.sql", [
        ("TC-31", "Script exists at the agreed location and runs",
         "SQL Server DB access.",
         "1. Locate DbScripts\\SqlServer\\MiscScripts\\SteelOrigin_FlaggedSupplierItems.sql.\n2. Run it on the test DB.",
         "Script exists and executes without errors.", "High", "DB", "AC5"),
        ("TC-32", "Returns exactly the flagged combinations",
         "Flag Y set on I1/SUP-A and I2/WC-1 only; I1/SUP-B, I3/SUP-A unflagged.",
         "1. Run the script.",
         "Exactly 2 rows: I1/SUP-A and I2/WC-1. Unflagged combinations are not returned.", "High", "DB", "AC5"),
        ("TC-33", "Output columns",
         "As TC-32.",
         "1. Inspect the result set columns.",
         "Plant, Item No, Supplier Code, Supplier Name and Supplier Item Code are returned with correct values.", "High", "DB", "AC5"),
        ("TC-34", "Excludes N, empty and NULL IGParams",
         "Supplier-items with forcesteelorigin=N, key missing, IGParams = '' and IGParams NULL.",
         "1. Run the script.",
         "None of those rows is returned; no error from NULL/empty IGParams.", "High", "DB", "AC5"),
        ("TC-35", "Key position in IGParams does not matter",
         "Rows where forcesteelorigin=Y is first, middle and last in the IGParams string.",
         "1. Run the script.",
         "All three rows are returned.", "Medium", "DB", "AC5"),
        ("TC-36", "No partial key / value false matches",
         "Rows with a similar key (e.g. xforcesteelorigin=Y) or other key whose value is Y.",
         "1. Run the script.",
         "Only exact key forcesteelorigin='Y' rows are returned.", "Medium", "DB", "AC5"),
        ("TC-37", "Reflects disable",
         "I1/SUP-A was flagged then unchecked in UI.",
         "1. Run the script.",
         "I1/SUP-A is no longer returned.", "High", "DB", "AC4/AC5"),
        ("TC-38", "Multi-plant data",
         "Flagged supplier-items exist in two plants.",
         "1. Run the script.",
         "Each row shows the correct Plant; rows from all plants are returned.", "Medium", "DB", "AC5"),
        ("TC-39", "Script is read-only",
         "Row counts of EboKanbanItems2Suppliers recorded.",
         "1. Run the script.\n2. Compare table data/row counts.",
         "SELECT only; no data or schema changed.", "Medium", "DB", "AC5"),
        ("TC-40", "No schema change introduced",
         "Pre/post-release DB schema compare.",
         "1. Compare EboKanbanItems2Suppliers schema before and after.",
         "No new table/column; value held in IGParams only.", "Low", "DB", "-"),
    ]),
    ("6. Out of Scope / Negative Checks", [
        ("TC-41", "No supplier-level or BU-level variant exists",
         "Admin access.",
         "1. Review Supplier and BU settings pages for a 'Force Steel Origin' option.",
         "No such option; the setting is available only at supplier-item level.", "Low", "Negative", "-"),
        ("TC-42", "Item import does not set the flag",
         "Item import template.",
         "1. Check the import template for a Force Steel Origin column.\n2. Import items/suppliers.",
         "No import column; imported supplier-items default to unchecked.", "Low", "Negative", "-"),
    ]),
    ("7. Regression", [
        ("TC-43", "Existing Force Packing Slip No behaviour unchanged",
         "Item with forcepkslip=Y.",
         "1. Ship a card of the item.",
         "Packing slip is still enforced as before; Steel Origin has no effect on it.", "Medium", "Regression", "-"),
        ("TC-44", "Existing supplier-item flex fields still save and load",
         "Internal and external suppliers.",
         "1. Change pick.repack, from.loc, frmloc.ctrl and external flex fields; save; re-open.",
         "All values persist; SaveSupplierIGParams and load paths behave as before.", "Medium", "Regression", "-"),
    ]),
]

AC_MATRIX = [
    ("AC1 - Off by default", "TC-01, TC-02"),
    ("AC2 - Available for external and internal suppliers", "TC-03, TC-04, TC-05, TC-06, TC-11"),
    ("AC3 - Enable for one supplier-item only", "TC-07, TC-08, TC-09, TC-12, TC-15 to TC-20, TC-22"),
    ("AC4 - Disable", "TC-10, TC-23, TC-24, TC-37"),
    ("AC5 - Query flagged supplier-items", "TC-31 to TC-39"),
]


def shade(cell, color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    tcPr.append(shd)


def write(cell, text, size=8, bold=False, color=None, center=False):
    cell.text = ""
    p = cell.paragraphs[0]
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    lines = text.split("\n")
    for i, line in enumerate(lines):
        run = p.add_run(line)
        run.font.size = Pt(size)
        run.bold = bold
        if color:
            run.font.color.rgb = RGBColor.from_string(color)
        if i < len(lines) - 1:
            run.add_break()


def heading(doc, text, size=13):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold = True
    r.font.size = Pt(size)
    r.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)


def set_widths(table, widths):
    for row in table.rows:
        for i, w in enumerate(widths):
            row.cells[i].width = Inches(w)


doc = Document()
sec = doc.sections[0]
sec.orientation = WD_ORIENT.LANDSCAPE
sec.page_width, sec.page_height = sec.page_height, sec.page_width
for m in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
    setattr(sec, m, Inches(0.5))

t = doc.add_paragraph()
r = t.add_run("ULT-10605 - Test Cases")
r.bold = True
r.font.size = Pt(18)
r.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
doc.add_paragraph("Steel Origin | Force Steel Origin setting at supplier-item level").runs[0].font.size = Pt(11)

info = doc.add_table(rows=0, cols=2)
info.style = "Table Grid"
for k, v in [
    ("Ticket", "ULT-10605 (Epic ULT-10604)"),
    ("Labels", "Copeland, SteelOrigin"),
    ("Scope", "Force Steel Origin checkbox at supplier-item level (EboKanbanItems2Suppliers.IGParams key forcesteelorigin, Y/N, default N); "
              "FORCE_STEEL_ORIGIN_EXPR and IsSteelOriginForcedAtShip; support query SteelOrigin_FlaggedSupplierItems.sql."),
    ("Out of scope", "Bulk import / API / ERP sync of the flag; BU-level or supplier-level variant."),
    ("Total test cases", str(sum(len(c) for _, c in SECTIONS))),
]:
    row = info.add_row()
    write(row.cells[0], k, size=9, bold=True)
    shade(row.cells[0], "DCE6F1")
    write(row.cells[1], v, size=9)
set_widths(info, [1.5, 8.5])

for title, cases in SECTIONS:
    heading(doc, f"{title} ({len(cases)})")
    tbl = doc.add_table(rows=1, cols=len(COLS))
    tbl.style = "Table Grid"
    for i, h in enumerate(COLS):
        write(tbl.rows[0].cells[i], h, size=9, bold=True, color="FFFFFF", center=True)
        shade(tbl.rows[0].cells[i], "1F4E79")
    for n, case in enumerate(cases):
        row = tbl.add_row()
        for i, val in enumerate(case):
            write(row.cells[i], val, bold=(i == 0), center=(i in (0, 5, 6, 7)))
            if n % 2:
                shade(row.cells[i], "F2F2F2")
    set_widths(tbl, WIDTHS)

heading(doc, "Acceptance Criteria Traceability")
m = doc.add_table(rows=1, cols=2)
m.style = "Table Grid"
for i, h in enumerate(["Acceptance Criteria", "Test Cases"]):
    write(m.rows[0].cells[i], h, size=9, bold=True, color="FFFFFF")
    shade(m.rows[0].cells[i], "1F4E79")
for a, b in AC_MATRIX:
    row = m.add_row()
    write(row.cells[0], a, size=9)
    write(row.cells[1], b, size=9)
set_widths(m, [4.0, 6.0])

OUT.parent.mkdir(parents=True, exist_ok=True)
doc.save(OUT)
print(f"Created: {OUT}")
