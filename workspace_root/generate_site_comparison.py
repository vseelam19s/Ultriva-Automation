"""
Generates an Excel report comparing old vs new Ultriva Integration Documentation sites.
Old: https://help.ultrivalms.com/internaldocs
New: https://help.ultrivalms.com/internaldocsv2/
"""

import openpyxl
from openpyxl.styles import (
    Font, PatternFill, Alignment, Border, Side, GradientFill
)
from openpyxl.utils import get_column_letter
from datetime import datetime

# ── Color palette ──────────────────────────────────────────────────────────────
HDR_BG     = "1F4E79"   # dark blue  – section headers
HDR_FG     = "FFFFFF"
SUB_BG     = "BDD7EE"   # light blue – sub-headers
SUB_FG     = "000000"
RED_BG     = "FFCCCC"   # critical
YEL_BG     = "FFF2CC"   # medium
GRN_BG     = "E2EFDA"   # low / ok
WHT_BG     = "FFFFFF"
ALT_BG     = "F2F2F2"   # alternating row

THIN = Side(border_style="thin", color="AAAAAA")
THIN_BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

def header_font(size=11, bold=True, color="FFFFFF"):
    return Font(name="Calibri", size=size, bold=bold, color=color)

def normal_font(size=10, bold=False, color="000000"):
    return Font(name="Calibri", size=size, bold=bold, color=color)

def fill(hex_color):
    return PatternFill("solid", fgColor=hex_color)

def style_cell(cell, bg, fg="000000", bold=False, wrap=True, halign="left", valign="top", size=10):
    cell.font      = Font(name="Calibri", size=size, bold=bold, color=fg)
    cell.fill      = fill(bg)
    cell.alignment = Alignment(wrap_text=wrap, horizontal=halign, vertical=valign)
    cell.border    = THIN_BORDER

def write_header_row(ws, row, cols, bg=HDR_BG, fg=HDR_FG, size=11):
    for c_idx, (col, text) in enumerate(cols, 1):
        cell = ws.cell(row=row, column=c_idx, value=text)
        style_cell(cell, bg, fg, bold=True, size=size, valign="center", halign="center")

def write_section_title(ws, row, title, ncols, bg=HDR_BG):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=ncols)
    cell = ws.cell(row=row, column=1, value=title)
    style_cell(cell, bg, HDR_FG, bold=True, size=12, halign="center", valign="center")
    ws.row_dimensions[row].height = 20

def auto_width(ws, col_widths):
    for col_idx, width in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(col_idx)].width = width


# ── Data ───────────────────────────────────────────────────────────────────────

STRUCTURE_DATA = [
    # (ID, Category, Old Site, New Site, Severity, SeverityCode)
    (1,  "Top-level Navigation",
         "No dedicated Architecture or Data Flow pages at top level",
         "New pages added: Architecture and Data Flow at top level (moved/elevated from Oracle subsection)",
         "Added", "GRN"),
    (2,  "Top-level Navigation",
         "Technical Overview only present inside Oracle Connector sub-section",
         "Also present at top level as standalone page",
         "Added", "GRN"),
    (3,  "SampleIntegration / Developer API",
         "Has SampleIntegration Namespace page with SampleClass (developer API reference)",
         "MISSING ENTIRELY — no equivalent page exists",
         "Critical — Missing in New Site", "RED"),
    (4,  "File-Based > ERP to Ultriva",
         "No 'Item Sync Detail', 'Supplier Sync Detail', 'Supplier Detail' sub-pages",
         "New sub-pages added: Item Sync Detail, Supplier Sync Detail, Supplier Detail",
         "Added", "GRN"),
    (5,  "File-Based > Ultriva to ERP",
         "No 'PO Release Detail' sub-page",
         "New sub-page added: PO Release Detail",
         "Added", "GRN"),
    (6,  "API > Overview",
         "No Client Integration Guide or Interactive API Reference",
         "New pages: Client Integration Guide, Interactive API Reference (Redoc)",
         "Added", "GRN"),
    (7,  "API > Ultriva to ERP",
         "No dedicated status/query endpoints",
         "4 new pages: Card Releases By Status, Inventory Status, Consumption History, Order Status",
         "Added", "GRN"),
    (8,  "API > ERP to Ultriva",
         "No BOM or OEE data load pages",
         "2 new pages: BOM Data Load, OEE Data Load",
         "Added", "GRN"),
    (9,  "Oracle Connector Scope",
         "Oracle section: Technical Overview, Integration Points, Data Flow, Functional Design sub-pages only",
         "Adds: Architecture, Installation Instructions, Integration Data Mapping, ERP to Ultriva, Ultriva to ERP as new Oracle sub-pages",
         "Added", "GRN"),
    (10, "EDI > Container Name",
         "Container named 'EDI Documents' holds 846, 850, 856, 861, 867, 997",
         "Renamed to 'EDI Table of Contents' — restructured",
         "Title Changed", "YEL"),
    (11, "EDI > 861 Page",
         "'861 - Receiving Advice/Acceptance Certificate' (single page with expandable design sub-page)",
         "Two separate pages: 861 - Receiving Advice + 861 - Functional Design",
         "Title Changed / Restructured", "YEL"),
    (12, "EDI > 867 Page",
         "'867 - Product Transfer and Resale Report' (single page with expandable design sub-page)",
         "Two separate pages: 867 - Product Transfer Report + 867 - Functional Design",
         "Title Changed / Restructured", "YEL"),
]

INTRO_DATA = [
    ("Scope Statement",
     "Old Site:\n\"This Help document describes the common integration points between Ultriva and ERP systems using Flat File based approach.\"",
     "New Site:\n\"This documentation describes the common integration points between Ultriva and ERP systems using all supported approaches.\"",
     "SIGNIFICANT — Old site scoped to flat-file only; new site covers all approaches"),
]

TYPO_DATA = [
    ("Page Intro",      "cosume / Commma / seperated",         "consume / Comma / separated"),
    ("File Name section","must be appeneded",                   "must be appended"),
    ("Header Line Format","the character which is idenfied as delimited", "the character which is identified as delimiter"),
    ("Data Line Format", "the character which is idenfied as delimited",  "the character which is identified as delimiter"),
    ("Data Line Format", "A String value map be encoded in double quotes","A String value may be encoded in double quotes"),
]

ORACLE_DATA = [
    ("Architecture",           "Not a dedicated page (diagram embedded inside Technical Overview)", "✅ Dedicated Architecture page with Oracle integration diagram", "Added"),
    ("Installation Instructions","❌ Not present",                        "✅ New page: oracle/installation/",               "Added"),
    ("Integration Data Mapping","❌ Not present",                         "✅ New page: oracle/integration-data-mapping/",   "Added"),
    ("ERP to Ultriva (Oracle)", "❌ Not as standalone page",              "✅ Separate page: oracle/erp-to-ultriva/",        "Added"),
    ("Ultriva to ERP (Oracle)", "❌ Not as standalone page",              "✅ Separate page: oracle/ultriva-to-erp/",        "Added"),
    ("Technical Overview",      "✅ Present under Oracle (correct content)","✅ Present — same content",                    "Match"),
    ("Integration Points",      "✅ Present (full integration points table)","✅ Present — same content",                   "Match"),
]

SAME_DATA = [
    ("SQL Table Format",                  "✅ Match", "General guidelines, diagram, description identical"),
    ("Import Export Processor",           "✅ Match", "Import/export details, DateTime formats identical"),
    ("Technical Overview (Oracle)",       "✅ Match", "Integration server description + diagram identical"),
    ("Oracle Integration Points",         "✅ Match", "Full table (Item Master Sync, Supplier Sync, MRP Orders, etc.)"),
    ("File-Based ERP to Ultriva sub-pages","✅ Match", "Item Sync through NCR Data Load — all present"),
    ("File-Based Ultriva to ERP sub-pages","✅ Match", "Inventory Transfer through Customer SO Consol Ship — all present"),
    ("EDI 846, 850, 856, 997",            "✅ Match", "All four EDI pages present with consistent content"),
    ("Flat File Format — General Guidelines","✅ Match","File Location, File Name, Upload Frequency, File Contents, Header/Data Line Format"),
]

CRITICAL_DATA = [
    ("🔴 HIGH", "SampleIntegration page missing from new site",
     "Old site has SampleIntegration Namespace developer reference with SampleClass API documentation. This is entirely absent in the new site. Developer integrators relying on this reference have no equivalent."),
    ("🔴 HIGH", "Introduction scope change",
     "Old site explicitly stated flat-file only scope. New site claims all approaches. If integration consumers rely on the introduction for scope guidance, this is a breaking change in documentation intent."),
    ("🟡 MEDIUM", "EDI 861 page title shortened",
     "Old: '861 - Receiving Advice/Acceptance Certificate'\nNew: '861 - Receiving Advice'\n'Acceptance Certificate' was dropped from the title — may affect searchability."),
    ("🟡 MEDIUM", "EDI 867 title shortened",
     "Old: '867 - Product Transfer and Resale Report'\nNew: '867 - Product Transfer Report'\n'and Resale' dropped — may affect users searching for resale documentation."),
    ("🟢 LOW", "Oracle Installation Instructions (new in v2)",
     "Old site had no installation page. New site adds oracle/installation/. This is an addition, not a regression."),
    ("🟢 LOW", "Typo fixes in Flat File Format",
     "6 typos corrected in new site (cosume→consume, Commma→Comma, seperated→separated, appeneded→appended, idenfied→identified, map→may, delimited→delimiter). Improvements, not regressions."),
]

# ── Build workbook ─────────────────────────────────────────────────────────────

wb = openpyxl.Workbook()

# ── Sheet 1: Summary ──────────────────────────────────────────────────────────
ws1 = wb.active
ws1.title = "Summary"

ws1.merge_cells("A1:D1")
c = ws1["A1"]
c.value = "Ultriva Integration Documentation — Site Comparison Report"
style_cell(c, HDR_BG, HDR_FG, bold=True, size=14, halign="center", valign="center")
ws1.row_dimensions[1].height = 30

ws1.merge_cells("A2:D2")
c = ws1["A2"]
c.value = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}   |   Old Site: help.ultrivalms.com/internaldocs   |   New Site: help.ultrivalms.com/internaldocsv2/"
style_cell(c, SUB_BG, "000000", bold=False, size=10, halign="center", valign="center")
ws1.row_dimensions[2].height = 16

# Summary stats
stats = [
    ("Total pages compared (approx.)", "~90+ pages across both sites"),
    ("Pages confirmed identical",       "8 major sections / all file-based integration points"),
    ("Pages added in new site (new content)", "15+ new pages (API query endpoints, Oracle sub-pages, file detail pages)"),
    ("Pages missing from new site",     "1 (SampleIntegration Namespace)"),
    ("Page title changes",              "3 (EDI 861, EDI 867, EDI Documents container)"),
    ("Typo corrections in new site",    "6 typos fixed in Flat File Format page"),
    ("Scope change",                    "Introduction now covers all integration approaches (was flat-file only)"),
]

row = 4
ws1.merge_cells(f"A{row}:D{row}")
c = ws1.cell(row=row, column=1, value="SUMMARY STATISTICS")
style_cell(c, HDR_BG, HDR_FG, bold=True, size=11, halign="center", valign="center")
ws1.row_dimensions[row].height = 18
row += 1

for i, (label, val) in enumerate(stats):
    bg = ALT_BG if i % 2 else WHT_BG
    c1 = ws1.cell(row=row, column=1, value=label)
    c2 = ws1.cell(row=row, column=2, value=val)
    ws1.merge_cells(start_row=row, start_column=2, end_row=row, end_column=4)
    style_cell(c1, bg, "000000", bold=True,  size=10)
    style_cell(c2, bg, "000000", bold=False, size=10)
    row += 1

# Critical items on summary
row += 1
ws1.merge_cells(f"A{row}:D{row}")
c = ws1.cell(row=row, column=1, value="CRITICAL ITEMS")
style_cell(c, "C00000", HDR_FG, bold=True, size=11, halign="center", valign="center")
ws1.row_dimensions[row].height = 18
row += 1

crit_cols = [("A","Priority"), ("B","Issue"), ("C","Details (see Critical Findings sheet)")]
for col, label in crit_cols:
    c = ws1[f"{col}{row}"]
    c.value = label
    style_cell(c, SUB_BG, "000000", bold=True, size=10, halign="center")
row += 1

for item in CRITICAL_DATA:
    bg = RED_BG if "HIGH" in item[0] else (YEL_BG if "MEDIUM" in item[0] else GRN_BG)
    for col_i, val in enumerate(item, 1):
        if col_i == 3:
            val = val.replace("\n", " ")
        c = ws1.cell(row=row, column=col_i, value=val)
        style_cell(c, bg, "000000", bold=(col_i==1), size=10)
    row += 1

auto_width(ws1, [45, 45, 65, 5])


# ── Sheet 2: Structure Differences ───────────────────────────────────────────
ws2 = wb.create_sheet("Structure Differences")

write_section_title(ws2, 1, "NAVIGATION & STRUCTURE DIFFERENCES", 5)
ws2.row_dimensions[1].height = 22

col_hdrs = [("A","#"), ("B","Category"), ("C","Old Site (internaldocs)"),
            ("D","New Site (internaldocsv2)"), ("E","Severity")]
write_header_row(ws2, 2, col_hdrs, bg=SUB_BG, fg="000000", size=10)
ws2.row_dimensions[2].height = 16

for i, row_data in enumerate(STRUCTURE_DATA):
    r = i + 3
    code = row_data[5]
    if code == "RED":
        bg = RED_BG
    elif code == "YEL":
        bg = YEL_BG
    else:
        bg = GRN_BG if i % 2 == 0 else "D9EAD3"
    for col_i, val in enumerate(row_data[:5], 1):
        c = ws2.cell(row=r, column=col_i, value=val)
        style_cell(c, bg, "000000", bold=(col_i==1), size=10)
        ws2.row_dimensions[r].height = 40

auto_width(ws2, [5, 28, 48, 52, 28])


# ── Sheet 3: Content Differences ─────────────────────────────────────────────
ws3 = wb.create_sheet("Content Differences")

# Introduction change
write_section_title(ws3, 1, "INTRODUCTION PAGE — SCOPE CHANGE", 4)
ws3.row_dimensions[1].height = 22
write_header_row(ws3, 2, [("A","Field"),("B","Old Site Content"),("C","New Site Content"),("D","Impact")],
                 bg=SUB_BG, fg="000000", size=10)
for i, row_data in enumerate(INTRO_DATA):
    r = i + 3
    bg = YEL_BG
    for col_i, val in enumerate(row_data, 1):
        c = ws3.cell(row=r, column=col_i, value=val)
        style_cell(c, bg, "000000", size=10)
    ws3.row_dimensions[r].height = 60

# Typo section
row_start = 6
write_section_title(ws3, row_start, "FLAT FILE FORMAT — TYPO CORRECTIONS", 4)
ws3.row_dimensions[row_start].height = 22
write_header_row(ws3, row_start + 1,
                 [("A","Location"),("B","Old Site (with typo)"),("C","New Site (corrected)"),("D","Status")],
                 bg=SUB_BG, fg="000000", size=10)
for i, row_data in enumerate(TYPO_DATA):
    r = row_start + 2 + i
    bg = GRN_BG if i % 2 == 0 else "D9EAD3"
    for col_i, val in enumerate(row_data, 1):
        c = ws3.cell(row=r, column=col_i, value=val)
        style_cell(c, bg, "000000", size=10)
    c_status = ws3.cell(row=r, column=4, value="Fixed in v2 ✓")
    style_cell(c_status, GRN_BG, "000000", bold=True, size=10, halign="center")
    ws3.row_dimensions[r].height = 30

auto_width(ws3, [28, 55, 55, 18])


# ── Sheet 4: Oracle Connector ─────────────────────────────────────────────────
ws4 = wb.create_sheet("Oracle Connector")

write_section_title(ws4, 1, "ORACLE CONNECTOR — PAGE COMPARISON", 4)
ws4.row_dimensions[1].height = 22
write_header_row(ws4, 2,
                 [("A","Page"),("B","Old Site (internaldocs)"),("C","New Site (internaldocsv2)"),("D","Status")],
                 bg=SUB_BG, fg="000000", size=10)
for i, row_data in enumerate(ORACLE_DATA):
    r = i + 3
    status = row_data[3]
    if status == "Added":
        bg = GRN_BG
    elif status == "Match":
        bg = WHT_BG if i % 2 == 0 else ALT_BG
    else:
        bg = YEL_BG
    for col_i, val in enumerate(row_data, 1):
        c = ws4.cell(row=r, column=col_i, value=val)
        style_cell(c, bg, "000000", bold=(col_i==4), size=10)
    ws4.row_dimensions[r].height = 35

auto_width(ws4, [30, 52, 52, 12])


# ── Sheet 5: Confirmed Same ───────────────────────────────────────────────────
ws5 = wb.create_sheet("Confirmed Same")

write_section_title(ws5, 1, "PAGES CONFIRMED IDENTICAL IN BOTH SITES", 3)
ws5.row_dimensions[1].height = 22
write_header_row(ws5, 2,
                 [("A","Page / Section"),("B","Status"),("C","Notes")],
                 bg=SUB_BG, fg="000000", size=10)
for i, row_data in enumerate(SAME_DATA):
    r = i + 3
    bg = GRN_BG if i % 2 == 0 else "D9EAD3"
    for col_i, val in enumerate(row_data, 1):
        c = ws5.cell(row=r, column=col_i, value=val)
        style_cell(c, bg, "000000", bold=(col_i==2), size=10, halign=("center" if col_i==2 else "left"))
    ws5.row_dimensions[r].height = 25

auto_width(ws5, [45, 14, 62])


# ── Sheet 6: Critical Findings ────────────────────────────────────────────────
ws6 = wb.create_sheet("Critical Findings")

write_section_title(ws6, 1, "CRITICAL FINDINGS — ACTION REQUIRED", 3)
ws6.row_dimensions[1].height = 22
write_header_row(ws6, 2,
                 [("A","Priority"),("B","Issue"),("C","Details")],
                 bg=SUB_BG, fg="000000", size=10)
for i, row_data in enumerate(CRITICAL_DATA):
    r = i + 3
    if "HIGH" in row_data[0]:
        bg = RED_BG
    elif "MEDIUM" in row_data[0]:
        bg = YEL_BG
    else:
        bg = GRN_BG
    for col_i, val in enumerate(row_data, 1):
        c = ws6.cell(row=r, column=col_i, value=val)
        style_cell(c, bg, "000000", bold=(col_i==1), size=10)
    ws6.row_dimensions[r].height = 55

auto_width(ws6, [14, 45, 80])


# ── Sheet 7: Full Page Inventory ──────────────────────────────────────────────
ws7 = wb.create_sheet("Full Page Inventory")

write_section_title(ws7, 1, "COMPLETE PAGE INVENTORY — OLD vs NEW SITE", 5)
ws7.row_dimensions[1].height = 22
write_header_row(ws7, 2,
                 [("A","Section"),("B","Page Name"),("C","Old Site URL / HTM"),("D","New Site URL"),("E","Status")],
                 bg=SUB_BG, fg="000000", size=10)

pages = [
    # Section, Page Name, Old URL fragment, New URL, Status
    ("Top Level","Introduction","04a7037a...b.htm","introduction/","Match"),
    ("Top Level","SQL Table Format","ca5c40ce...9.htm","sql-table-format/","Match"),
    ("Top Level","Import Export Processor","59710a47...4.htm","import-processor/","Match"),
    ("Top Level","Flat File Format","bd527592...7.htm","flat-file-format/","Match"),
    ("Top Level","Architecture","(Not present)","architecture/","Added in v2"),
    ("Top Level","Data Flow","(Not present)","data-flow/","Added in v2"),
    ("Top Level","Technical Overview","(Embedded in Oracle only)","technical-overview/","Added at top level in v2"),
    ("File-Based","Overview","eda992e3...f.htm","file-based/","Match"),
    ("File-Based > ERP→Ultriva","ERP to Ultriva Overview","16544c5f...a.htm","file-based/erp-to-ultriva/","Match"),
    ("File-Based > ERP→Ultriva","Item Sync","e3916242...1.htm","file-based/erp-to-ultriva/item-sync/","Match"),
    ("File-Based > ERP→Ultriva","Item Sync Detail","(Not present)","file-based/erp-to-ultriva/item-sync-detail/","Added in v2"),
    ("File-Based > ERP→Ultriva","Supplier Sync","db9b7f17...3.htm","file-based/erp-to-ultriva/supplier-sync/","Match"),
    ("File-Based > ERP→Ultriva","Supplier Sync Detail","(Not present)","file-based/erp-to-ultriva/supplier-sync-detail/","Added in v2"),
    ("File-Based > ERP→Ultriva","Supplier Detail","(Not present)","file-based/erp-to-ultriva/supplier-detail/","Added in v2"),
    ("File-Based > ERP→Ultriva","Workcenter Sync","6ee963fe...4.htm","file-based/erp-to-ultriva/workcenter-sync/","Match"),
    ("File-Based > ERP→Ultriva","Consumption Data","38d56c9a...c.htm","file-based/erp-to-ultriva/consumption-data/","Match"),
    ("File-Based > ERP→Ultriva","Inventory Sync","3851ad33...f.htm","file-based/erp-to-ultriva/inventory-sync/","Match"),
    ("File-Based > ERP→Ultriva","Accept Data","cf86eb3b...8.htm","file-based/erp-to-ultriva/accept-data/","Match"),
    ("File-Based > ERP→Ultriva","PO Change Data","e0a72f19...5.htm","file-based/erp-to-ultriva/po-change-data/","Match"),
    ("File-Based > ERP→Ultriva","PO Cancel Data","99b58acc...b.htm","file-based/erp-to-ultriva/po-cancel-data/","Match"),
    ("File-Based > ERP→Ultriva","Shipment Data","47804929...2.htm","file-based/erp-to-ultriva/shipment-data/","Match"),
    ("File-Based > ERP→Ultriva","Consol Shipment Data","e5f9da17...6.htm","file-based/erp-to-ultriva/consol-shipment-data/","Match"),
    ("File-Based > ERP→Ultriva","Card Receipts","87a520ac...f.htm","file-based/erp-to-ultriva/card-receipts/","Match"),
    ("File-Based > ERP→Ultriva","Receipt Data","f161cdff...8.htm","file-based/erp-to-ultriva/receipt-data/","Match"),
    ("File-Based > ERP→Ultriva","Inspect/Reject Data","7cfba370...1.htm","file-based/erp-to-ultriva/inspect-reject-data/","Match"),
    ("File-Based > ERP→Ultriva","Set Del Card","2d74989e...f.htm","file-based/erp-to-ultriva/set-del-card/","Match"),
    ("File-Based > ERP→Ultriva","Set PO","f32f5f94...0.htm","file-based/erp-to-ultriva/set-po/","Match"),
    ("File-Based > ERP→Ultriva","Set WO","e32ded81...a.htm","file-based/erp-to-ultriva/set-wo/","Match"),
    ("File-Based > ERP→Ultriva","Set PO Accept","b87674dc...9.htm","file-based/erp-to-ultriva/set-po-accept/","Match"),
    ("File-Based > ERP→Ultriva","Set PO Change","70e07fed...6.htm","file-based/erp-to-ultriva/set-po-change/","Match"),
    ("File-Based > ERP→Ultriva","Set PO Recall","00a5a6b5...1.htm","file-based/erp-to-ultriva/set-po-recall/","Match"),
    ("File-Based > ERP→Ultriva","Set PO Ship","fa52623c...2.htm","file-based/erp-to-ultriva/set-po-ship/","Match"),
    ("File-Based > ERP→Ultriva","Set PO Consol Ship","ee3b6284...2.htm","file-based/erp-to-ultriva/set-po-consol-ship/","Match"),
    ("File-Based > ERP→Ultriva","Set PO Receipt","9686937c...6.htm","file-based/erp-to-ultriva/set-po-receipt/","Match"),
    ("File-Based > ERP→Ultriva","Set WO Receive/Close","8fcdffb1...9.htm","file-based/erp-to-ultriva/set-wo-receive-close/","Match"),
    ("File-Based > ERP→Ultriva","Set PO Inspect/Approve","7429220b...e.htm","file-based/erp-to-ultriva/set-po-inspect-approve/","Match"),
    ("File-Based > ERP→Ultriva","Set Close Production","18659635...4.htm","file-based/erp-to-ultriva/set-close-production/","Match"),
    ("File-Based > ERP→Ultriva","Planned Orders","f8ea56a9...4.htm","file-based/erp-to-ultriva/planned-orders/","Match"),
    ("File-Based > ERP→Ultriva","PO Sync","9205f3b9...b.htm","file-based/erp-to-ultriva/po-sync/","Match"),
    ("File-Based > ERP→Ultriva","Forecast Data","5434299c...c.htm","file-based/erp-to-ultriva/forecast-data/","Match"),
    ("File-Based > ERP→Ultriva","Customer Sync","f9eb1eb9...c.htm","file-based/erp-to-ultriva/customer-sync/","Match"),
    ("File-Based > ERP→Ultriva","Customer Item Sync","b4138da0...5.htm","file-based/erp-to-ultriva/customer-item-sync/","Match"),
    ("File-Based > ERP→Ultriva","Customer Consumption Data","7ce9c8ab...d.htm","file-based/erp-to-ultriva/customer-consumption-data/","Match"),
    ("File-Based > ERP→Ultriva","Customer Orders","61842d8f...6.htm","file-based/erp-to-ultriva/customer-orders/","Match"),
    ("File-Based > ERP→Ultriva","Customer Order Changes","9545e794...6.htm","file-based/erp-to-ultriva/customer-order-changes/","Match"),
    ("File-Based > ERP→Ultriva","Customer Card Receipts","e934c8cc...a.htm","file-based/erp-to-ultriva/customer-card-receipts/","Match"),
    ("File-Based > ERP→Ultriva","Customer Set SO","2b2eb86e...0.htm","file-based/erp-to-ultriva/customer-set-so/","Match"),
    ("File-Based > ERP→Ultriva","Customer Set SO Ship","b42442ff...9.htm","file-based/erp-to-ultriva/customer-set-so-ship/","Match"),
    ("File-Based > ERP→Ultriva","Customer Set SO Consol Ship","f940b0cf...4.htm","file-based/erp-to-ultriva/customer-set-so-consol-ship/","Match"),
    ("File-Based > ERP→Ultriva","Customer Shipment Data","341c5d30...a.htm","file-based/erp-to-ultriva/customer-shipment-data/","Match"),
    ("File-Based > ERP→Ultriva","Customer Consol Shipment Data","cd3e3901...4.htm","file-based/erp-to-ultriva/customer-consol-shipment-data/","Match"),
    ("File-Based > ERP→Ultriva","NCR Data Load","c26be53d...4.htm","file-based/erp-to-ultriva/ncr-data-load/","Match"),
    ("File-Based > Ultriva→ERP","Ultriva To ERP Overview","fb1e7c9d...0.htm","file-based/ultriva-to-erp/","Match"),
    ("File-Based > Ultriva→ERP","Inventory Transfer","2ed4e17c...7.htm","file-based/ultriva-to-erp/inventory-transfer/","Match"),
    ("File-Based > Ultriva→ERP","Card Delete Data","075177ff...7.htm","file-based/ultriva-to-erp/card-delete-data/","Match"),
    ("File-Based > Ultriva→ERP","Purchase Order Release/Create","13c9f304...b.htm","file-based/ultriva-to-erp/po-release/","Match"),
    ("File-Based > Ultriva→ERP","PO Release Detail","(Not present)","file-based/ultriva-to-erp/po-release-detail/","Added in v2"),
    ("File-Based > Ultriva→ERP","Work Order Release/Create","3fe0a83b...b.htm","file-based/ultriva-to-erp/wo-release/","Match"),
    ("File-Based > Ultriva→ERP","Purchase Order Accept","a0b4f655...8.htm","file-based/ultriva-to-erp/po-accept/","Match"),
    ("File-Based > Ultriva→ERP","Purchase Order Change","31a873d3...6.htm","file-based/ultriva-to-erp/po-change/","Match"),
    ("File-Based > Ultriva→ERP","Purchase Order Recall","7216a496...5.htm","file-based/ultriva-to-erp/po-recall/","Match"),
    ("File-Based > Ultriva→ERP","Purchase Order Ship","3bc14082...0.htm","file-based/ultriva-to-erp/po-ship/","Match"),
    ("File-Based > Ultriva→ERP","Purchase Order Consol Ship","297d6314...7.htm","file-based/ultriva-to-erp/po-consol-ship/","Match"),
    ("File-Based > Ultriva→ERP","Purchase Order Receipt","6d94c818...2.htm","file-based/ultriva-to-erp/po-receipt/","Match"),
    ("File-Based > Ultriva→ERP","Work Order Close/Receive","e33d3bf5...4.htm","file-based/ultriva-to-erp/wo-receive/","Match"),
    ("File-Based > Ultriva→ERP","Purchase Order Inspect/Approve","2fa434b0...3.htm","file-based/ultriva-to-erp/po-inspect-approve/","Match"),
    ("File-Based > Ultriva→ERP","Close Production","c93bc384...f.htm","file-based/ultriva-to-erp/close-production/","Match"),
    ("File-Based > Ultriva→ERP","Customer Sales Order Release","a0326e02...c.htm","file-based/ultriva-to-erp/customer-so-release/","Match"),
    ("File-Based > Ultriva→ERP","Customer Sales Order Ship","3bab7b73...8.htm","file-based/ultriva-to-erp/customer-so-ship/","Match"),
    ("File-Based > Ultriva→ERP","Customer Sales Order Consol Ship","0a49ea26...0.htm","file-based/ultriva-to-erp/customer-so-consol-ship/","Match"),
    ("File-Based","Error File Format","a0a55dca...5.htm","file-based/error-file-format/","Match"),
    ("API","API Based Overview","f0539d93...8.htm","api/","Match"),
    ("API","Client Integration Guide","(Not present)","api/client-guide/","Added in v2"),
    ("API","Interactive API Reference","(Not present)","api/redoc.html","Added in v2"),
    ("API > Ultriva→ERP","Ultriva To ERP Overview","e3281bbb...a.htm","api/ultriva-to-erp/","Match"),
    ("API > Ultriva→ERP","Inventory Transfer","(in API section)","api/ultriva-to-erp/inventory-transfer/","Match"),
    ("API > Ultriva→ERP","Card Delete Data","(in API section)","api/ultriva-to-erp/card-delete-data/","Match"),
    ("API > Ultriva→ERP","Purchase Order Release/Create","(in API section)","api/ultriva-to-erp/po-release/","Match"),
    ("API > Ultriva→ERP","Work Order Release/Create","(in API section)","api/ultriva-to-erp/wo-release/","Match"),
    ("API > Ultriva→ERP","Purchase Order Accept","(in API section)","api/ultriva-to-erp/po-accept/","Match"),
    ("API > Ultriva→ERP","Purchase Order Change","(in API section)","api/ultriva-to-erp/po-change/","Match"),
    ("API > Ultriva→ERP","Purchase Order Recall","(in API section)","api/ultriva-to-erp/po-recall/","Match"),
    ("API > Ultriva→ERP","Purchase Order Ship","(in API section)","api/ultriva-to-erp/po-ship/","Match"),
    ("API > Ultriva→ERP","Purchase Order Consol Ship","(in API section)","api/ultriva-to-erp/po-consol-ship/","Match"),
    ("API > Ultriva→ERP","Purchase Order Receipt","(in API section)","api/ultriva-to-erp/po-receipt/","Match"),
    ("API > Ultriva→ERP","Work Order Close/Receive","(in API section)","api/ultriva-to-erp/wo-receive/","Match"),
    ("API > Ultriva→ERP","Purchase Order Inspect/Approve","(in API section)","api/ultriva-to-erp/po-inspect-approve/","Match"),
    ("API > Ultriva→ERP","Close Production","(in API section)","api/ultriva-to-erp/close-production/","Match"),
    ("API > Ultriva→ERP","Customer Sales Order Release","(in API section)","api/ultriva-to-erp/customer-so-release/","Match"),
    ("API > Ultriva→ERP","Customer Sales Order Ship","(in API section)","api/ultriva-to-erp/customer-so-ship/","Match"),
    ("API > Ultriva→ERP","Customer Sales Order Consol Ship","(in API section)","api/ultriva-to-erp/customer-so-consol-ship/","Match"),
    ("API > Ultriva→ERP","Card Releases By Status","(Not present)","api/ultriva-to-erp/card-releases-by-status/","Added in v2"),
    ("API > Ultriva→ERP","Inventory Status","(Not present)","api/ultriva-to-erp/inventory-status/","Added in v2"),
    ("API > Ultriva→ERP","Consumption History","(Not present)","api/ultriva-to-erp/consumption-history/","Added in v2"),
    ("API > Ultriva→ERP","Order Status","(Not present)","api/ultriva-to-erp/order-status/","Added in v2"),
    ("API > ERP→Ultriva","ERP To Ultriva Overview","65b053c4...5.htm","api/erp-to-ultriva/","Match"),
    ("API > ERP→Ultriva","Item Sync","(in API section)","api/erp-to-ultriva/item-sync/","Match"),
    ("API > ERP→Ultriva","Supplier Sync","(in API section)","api/erp-to-ultriva/supplier-sync/","Match"),
    ("API > ERP→Ultriva","Workcenter Sync","(in API section)","api/erp-to-ultriva/workcenter-sync/","Match"),
    ("API > ERP→Ultriva","Consumption Data","(in API section)","api/erp-to-ultriva/consumption-data/","Match"),
    ("API > ERP→Ultriva","Inventory Sync","(in API section)","api/erp-to-ultriva/inventory-sync/","Match"),
    ("API > ERP→Ultriva","Accept Data","(in API section)","api/erp-to-ultriva/accept-data/","Match"),
    ("API > ERP→Ultriva","PO Change Data","(in API section)","api/erp-to-ultriva/po-change-data/","Match"),
    ("API > ERP→Ultriva","PO Cancel Data","(in API section)","api/erp-to-ultriva/po-cancel-data/","Match"),
    ("API > ERP→Ultriva","Shipment Data","(in API section)","api/erp-to-ultriva/shipment-data/","Match"),
    ("API > ERP→Ultriva","Consol Shipment Data","(in API section)","api/erp-to-ultriva/consol-shipment-data/","Match"),
    ("API > ERP→Ultriva","Card Receipts","(in API section)","api/erp-to-ultriva/card-receipts/","Match"),
    ("API > ERP→Ultriva","Receipt Data","(in API section)","api/erp-to-ultriva/receipt-data/","Match"),
    ("API > ERP→Ultriva","Inspect/Reject Data","(in API section)","api/erp-to-ultriva/inspect-reject-data/","Match"),
    ("API > ERP→Ultriva","Set Del Card","(in API section)","api/erp-to-ultriva/set-del-card/","Match"),
    ("API > ERP→Ultriva","Set PO","(in API section)","api/erp-to-ultriva/set-po/","Match"),
    ("API > ERP→Ultriva","Set WO","(in API section)","api/erp-to-ultriva/set-wo/","Match"),
    ("API > ERP→Ultriva","Set PO Accept ... (remaining Set pages)","(in API section)","api/erp-to-ultriva/set-po-accept/ etc.","Match"),
    ("API > ERP→Ultriva","Planned Orders","(in API section)","api/erp-to-ultriva/planned-orders/","Match"),
    ("API > ERP→Ultriva","PO Sync","(in API section)","api/erp-to-ultriva/po-sync/","Match"),
    ("API > ERP→Ultriva","Forecast Data","(in API section)","api/erp-to-ultriva/forecast-data/","Match"),
    ("API > ERP→Ultriva","Customer Sync ... (all Customer pages)","(in API section)","api/erp-to-ultriva/customer-sync/ etc.","Match"),
    ("API > ERP→Ultriva","NCR Data Load","(in API section)","api/erp-to-ultriva/ncr-data-load/","Match"),
    ("API > ERP→Ultriva","BOM Data Load","(Not present)","api/erp-to-ultriva/bom-data-load/","Added in v2"),
    ("API > ERP→Ultriva","OEE Data Load","(Not present)","api/erp-to-ultriva/oee-data-load/","Added in v2"),
    ("SQL","SQL Based Overview","6fdb864a...5.htm","sql/","Match"),
    ("SQL > ERP→Ultriva","ERP To Ultriva Overview","71f07239...0.htm","sql/erp-to-ultriva/","Match"),
    ("SQL > ERP→Ultriva","Item Sync","(in SQL section)","sql/erp-to-ultriva/item-sync/","Match"),
    ("SQL > ERP→Ultriva","Supplier Sync","(in SQL section)","sql/erp-to-ultriva/supplier-sync/","Match"),
    ("SQL > ERP→Ultriva","Set PO","(in SQL section)","sql/erp-to-ultriva/set-po/","Match"),
    ("SQL > Ultriva→ERP","Ultriva To ERP Overview","6c6f008c...6.htm","sql/ultriva-to-erp/","Match"),
    ("SQL > Ultriva→ERP","Purchase Order Release/Create","(in SQL section)","sql/ultriva-to-erp/po-release/","Match"),
    ("SQL > Ultriva→ERP","Purchase Order Receipt","(in SQL section)","sql/ultriva-to-erp/po-receipt/","Match"),
    ("SQL","Support Tables","414d65c1...1.htm","sql/support-tables/","Match"),
    ("Oracle Connector","Overview","97a56274...3.htm","oracle/","Match"),
    ("Oracle Connector","Architecture","(Not standalone)","oracle/architecture/","Added in v2"),
    ("Oracle Connector","Technical Overview","995d6c27...2.htm","oracle/technical-overview/","Match"),
    ("Oracle Connector","Installation Instructions","(Not present)","oracle/installation/","Added in v2"),
    ("Oracle Connector","Integration Points","45f42d9c...b.htm","oracle/integration-points/","Match"),
    ("Oracle Connector","Integration Data Mapping","(Not present)","oracle/integration-data-mapping/","Added in v2"),
    ("Oracle > Functional Design","IR/ISO","(in Oracle section)","oracle/functional-design/ir-iso/","Match"),
    ("Oracle > Functional Design","Item Sync","(in Oracle section)","oracle/functional-design/item-sync/","Match"),
    ("Oracle > Functional Design","Data Flow","01c92061...5.htm","oracle/functional-design/data-flow/","Match"),
    ("Oracle > Functional Design","ASN","(in Oracle section)","oracle/functional-design/asn/","Match"),
    ("Oracle > Functional Design","Blanket PO Release","(in Oracle section)","oracle/functional-design/blanket-po-release/","Match"),
    ("Oracle > Functional Design","Gross Requirements","(in Oracle section)","oracle/functional-design/gross-requirements/","Match"),
    ("Oracle > Functional Design","Inter Org Inventory Transfer","(in Oracle section)","oracle/functional-design/inter-org-transfer/","Match"),
    ("Oracle > Functional Design","Inter Org Transfer (Receipt)","(in Oracle section)","oracle/functional-design/inter-org-transfer-receipt/","Match"),
    ("Oracle > Functional Design","Intra Org Transfer","(in Oracle section)","oracle/functional-design/intra-org-transfer/","Match"),
    ("Oracle > Functional Design","Misc Sub Transfer","(in Oracle section)","oracle/functional-design/misc-sub-transfer/","Match"),
    ("Oracle > Functional Design","Order Acknowledgment","(in Oracle section)","oracle/functional-design/order-acknowledgment/","Match"),
    ("Oracle > Functional Design","PO Create/Release","(in Oracle section)","oracle/functional-design/po-create-release/","Match"),
    ("Oracle > Functional Design","PO Receipt","(in Oracle section)","oracle/functional-design/po-receipt/","Match"),
    ("Oracle > Functional Design","Standard PO","(in Oracle section)","oracle/functional-design/standard-po/","Match"),
    ("Oracle > Functional Design","Sub Inventory Transfer","(in Oracle section)","oracle/functional-design/sub-inventory-transfer/","Match"),
    ("Oracle > Functional Design","Virtual Kanban","(in Oracle section)","oracle/functional-design/virtual-kanban/","Match"),
    ("Oracle","ERP to Ultriva (Oracle)","(Not standalone)","oracle/erp-to-ultriva/","Added in v2"),
    ("Oracle","Ultriva to ERP (Oracle)","(Not standalone)","oracle/ultriva-to-erp/","Added in v2"),
    ("EDI","EDI Interface Overview","1880d23d...7.htm","edi/","Match"),
    ("EDI","Architecture","fe336120...8.htm","edi/architecture/","Match"),
    ("EDI","EDI Documents/Table of Contents","54a9b68a...c.htm","edi/edi-toc/","Title Changed"),
    ("EDI","846 - Inventory Inquiry/Advice","bfc17c2b...e.htm","edi/edi-846/","Match"),
    ("EDI","850 - Purchase Order","e2297164...3.htm","edi/edi-850/","Match"),
    ("EDI","856 - ASN","4511fe72...a.htm","edi/edi-856/","Match"),
    ("EDI","861 - Receiving Advice/Acceptance Certificate","6ed465d0...1.htm","edi/edi-861/","Title Shortened in v2"),
    ("EDI","861 - Functional Design","(sub-page of 861)","edi/edi-861-design/","Separated in v2"),
    ("EDI","867 - Product Transfer and Resale Report","147eadd2...2.htm","edi/edi-867/","Title Shortened in v2"),
    ("EDI","867 - Functional Design","(sub-page of 867)","edi/edi-867-design/","Separated in v2"),
    ("EDI","997 - Functional Acknowledgment","9b2057a3...6.htm","edi/edi-997/","Match"),
    ("Developer API","SampleIntegration Namespace","64a518a0...1.htm","(NOT PRESENT)","⚠ MISSING in v2"),
    ("Developer API","SampleClass","000f8878...0.htm","(NOT PRESENT)","⚠ MISSING in v2"),
]

STATUS_COLOR = {
    "Match":           WHT_BG,
    "Added in v2":     GRN_BG,
    "Added":           GRN_BG,
    "Title Changed":   YEL_BG,
    "Title Shortened in v2": YEL_BG,
    "Separated in v2": YEL_BG,
    "⚠ MISSING in v2": RED_BG,
}

for i, (section, page, old_url, new_url, status) in enumerate(pages):
    r = i + 3
    bg = STATUS_COLOR.get(status, ALT_BG if i % 2 else WHT_BG)
    for col_i, val in enumerate([section, page, old_url, new_url, status], 1):
        c = ws7.cell(row=r, column=col_i, value=val)
        style_cell(c, bg, "000000", bold=(status == "⚠ MISSING in v2"),
                   size=9 if col_i in (3,4) else 10)
    ws7.row_dimensions[r].height = 18

auto_width(ws7, [32, 38, 36, 44, 22])

# Freeze top 2 rows on every sheet
for ws in [ws1, ws2, ws3, ws4, ws5, ws6, ws7]:
    ws.freeze_panes = "A3"

# ── Save ───────────────────────────────────────────────────────────────────────
out = r"C:\Prcatices-AI\reports\Ultriva_Site_Comparison.xlsx"
wb.save(out)
print(f"Saved: {out}")
