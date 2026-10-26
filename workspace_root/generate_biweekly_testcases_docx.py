"""
generate_biweekly_testcases_docx.py
Creates a Word document summarising all test cases created and run
for the last two weeks (Jul 28 – Aug 4, 2026) with PASS / FAIL status.
Run from the workspace root:  python generate_biweekly_testcases_docx.py
"""

import os
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ── colours ───────────────────────────────────────────────────────────────────
HDR_BLUE   = "1F4E79"
ROW_PASS   = "E2EFDA"   # light green
ROW_FAIL   = "FCE4D6"   # light red
ROW_XFAIL  = "FFF2CC"   # amber  (expected failure / xfail)
ROW_SKIP   = "F2F2F2"   # grey   (skipped)
ALT_ROW    = "EBF3FB"   # alternating row background
SUB_HDR    = "2E74B5"

# ── helpers ───────────────────────────────────────────────────────────────────

def _set_cell_bg(cell, hex_color):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def _cell_text(cell, text, bold=False, font_size=9, color=None,
               align=WD_ALIGN_PARAGRAPH.LEFT):
    cell.text = ""
    para = cell.paragraphs[0]
    para.alignment = align
    run = para.add_run(str(text))
    run.bold = bold
    run.font.size = Pt(font_size)
    if color:
        run.font.color.rgb = RGBColor.from_string(color)


def _header_row(table, col_defs, bg=HDR_BLUE):
    row = table.rows[0]
    for i, (text, width) in enumerate(col_defs):
        cell = row.cells[i]
        _set_cell_bg(cell, bg)
        _cell_text(cell, text, bold=True, font_size=10,
                   color="FFFFFF", align=WD_ALIGN_PARAGRAPH.CENTER)
        if width:
            cell.width = Inches(width)


def _add_section(doc, text, level=1):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(13 if level == 1 else 11)
    run.font.color.rgb = RGBColor.from_string(HDR_BLUE)
    return p


def _add_sub(doc, text):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor.from_string(SUB_HDR)
    return p


def _add_note(doc, text):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.italic = True
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor.from_string("595959")
    return p


STATUS_COLOR = {
    "PASS":   ROW_PASS,
    "FAIL":   ROW_FAIL,
    "XFAIL":  ROW_XFAIL,
    "SKIP":   ROW_SKIP,
    "PENDING": "F2F2F2",
}

COL_DEFS = [
    ("Test ID",        0.90),
    ("Test Case Name", 2.30),
    ("Description",    2.80),
    ("Status",         0.65),
]


def _add_test_table(doc, report_name, class_name, file_path, test_cases, date_str):
    """Render one table for a single test file."""
    _add_sub(doc, f"{report_name}")
    _add_note(doc, f"File: {file_path}   |   Class: {class_name}   |   Created: {date_str}")
    tbl = doc.add_table(rows=1, cols=4)
    tbl.style = "Table Grid"
    tbl.alignment = WD_TABLE_ALIGNMENT.LEFT
    _header_row(tbl, COL_DEFS)

    for i, (tc_id, name, desc, status) in enumerate(test_cases):
        row = tbl.add_row()
        bg = STATUS_COLOR.get(status, ALT_ROW)
        for j, val in enumerate((tc_id, name, desc, status)):
            _cell_text(row.cells[j], val, font_size=9,
                       bold=(j == 3),
                       color=("006100" if status == "PASS"
                              else "9C0006" if status == "FAIL"
                              else None))
            _set_cell_bg(row.cells[j], bg)
    doc.add_paragraph()


# ── standard 6-step test case builder ─────────────────────────────────────────

def _std6(prefix, open_step_name, form_step_name="Fill Report Name & Description",
          save_status="PASS", show_status="PASS"):
    """Returns a 6-row test-case list using the standard custom-report flow."""
    return [
        (f"{prefix}-01", "test_01_login",
         "Login to QALS1011 application as buyeruser", "PASS"),
        (f"{prefix}-02", "test_02_navigate_to_list",
         "Navigate to /CreateCustomReport/List page", "PASS"),
        (f"{prefix}-03", open_step_name,
         "Click report link in the appropriate section", "PASS"),
        (f"{prefix}-04", "test_04_fill_report_form",
         form_step_name, "PASS"),
        (f"{prefix}-05", "test_05_save_custom_report",
         "Submit form & verify report created", save_status),
        (f"{prefix}-06", "test_06_show_report_and_change_filter",
         "Show Report → verify data rows → Change Filter", show_status),
    ]


# ══════════════════════════════════════════════════════════════════════════════
# DATA – Last Week  Jul 28 – Aug 1, 2026
# ══════════════════════════════════════════════════════════════════════════════

LAST_WEEK_DATA = [
    # (section_label, report_name, class_name, file_path, test_cases, date)
    (
        "Kanban Custom Reports",
        "Back Ordered Cards Report",
        "TestCustomReportKanbanBackOrderedCards",
        "tests/QALS11/Reports/CustomReports/Kanban/test_back_ordered_cards_report.py",
        _std6("TC-BOC", "test_03_open_back_ordered_cards_form"),
        "Jul 29, 2026",
    ),
    (
        "Kanban Custom Reports",
        "Consignment Inventory Cost Report",
        "TestCustomReportKanbanConsignmentInventoryCost",
        "tests/QALS11/Reports/CustomReports/Kanban/test_consignment_inventory_cost_report.py",
        _std6("TC-CIC", "test_03_open_consignment_inventory_cost_form",
              form_step_name="Fill MISC_ReportName/MISC_Description (JS label-proximity)"),
        "Jul 29, 2026",
    ),
    (
        "Kanban Custom Reports",
        "Cycle History Report",
        "TestCustomReportKanbanCycleHistory",
        "tests/QALS11/Reports/CustomReports/Kanban/test_cycle_history_report.py",
        _std6("TC-CHR", "test_03_open_cycle_history_form"),
        "Jul 29, 2026",
    ),
    (
        "Kanban Custom Reports",
        "Operation History Report",
        "TestCustomReportKanbanOperationHistory",
        "tests/QALS11/Reports/CustomReports/Kanban/test_operation_history_report.py",
        _std6("TC-OHR", "test_03_open_operation_history_form"),
        "Jul 29, 2026",
    ),
    (
        "Kanban Custom Reports",
        "Containerization Report (Kanban)",
        "TestCustomReportKanbanContainerizationReport",
        "tests/QALS11/Reports/CustomReports/Kanban/test_containerization_report.py",
        _std6("TC-CNT-K", "test_03_open_containerization_form"),
        "Jul 30, 2026",
    ),
    (
        "Kanban Custom Reports",
        "Item Data Load Report",
        "TestCustomReportKanbanItemDataLoad",
        "tests/QALS11/Reports/CustomReports/Kanban/test_item_data_load_report.py",
        [
            ("TC-IDL-01", "test_01_login",
             "Login to QALS1011 application as buyeruser", "PASS"),
            ("TC-IDL-02", "test_02_navigate_to_list",
             "Navigate to /CreateCustomReport/List page", "PASS"),
            ("TC-IDL-03", "test_03_open_item_data_load_form",
             "Click Item Data Load link (Admin section in UI)", "PASS"),
            ("TC-IDL-04", "test_04_fill_report_form",
             "Fill MISC_ReportName/MISC_Description fields", "PASS"),
            ("TC-IDL-05", "test_05_save_custom_report",
             "Submit form – reportGID TBD (FALLBACK_REPORT_GID pending first run)", "PENDING"),
            ("TC-IDL-06", "test_06_show_report_and_change_filter",
             "Show Report → verify data rows → Change Filter", "PENDING"),
        ],
        "Jul 30, 2026",
    ),
]

# ══════════════════════════════════════════════════════════════════════════════
# DATA – This Week  Aug 3-4, 2026
# ══════════════════════════════════════════════════════════════════════════════

THIS_WEEK_DATA = [
    # ── Kanban (Aug 3) ─────────────────────────────────────────────────────
    (
        "Kanban Custom Reports",
        "Cross Tab History for Shelf Life Controlled Items Report",
        "TestCustomReportKanbanCrossTabHistoryShelfLife",
        "tests/QALS11/Reports/CustomReports/Kanban/test_cross_tab_history_for_shelf_life_controlled_items_report.py",
        _std6("TC-SLCXT",
              "test_03_open_shelf_life_cross_tab_form",
              form_step_name="Fill MISC_ReportName/MISC_Description (30-char cap)"),
        "Aug 3, 2026",
    ),
    (
        "Kanban Custom Reports",
        "PickList Allocated Card Report",
        "TestCustomReportKanbanPickListAllocatedCard",
        "tests/QALS11/Reports/CustomReports/Kanban/test_picklist_allocated_card_report.py",
        _std6("TC-PLAC",
              "test_03_open_picklist_allocated_card_form",
              form_step_name="Fill MISC_ReportName/MISC_Description (JS label-proximity)"),
        "Aug 3, 2026",
    ),
    (
        "Kanban Custom Reports",
        "On Hand Inventory By Supplier Report",
        "TestCustomReportKanbanOnHandInventoryBySupplier",
        "tests/QALS11/Reports/CustomReports/Kanban/test_on_hand_inventory_by_supplier_report.py",
        _std6("TC-OHIS",
              "test_03_open_on_hand_inv_by_supplier_form",
              form_step_name="Fill MISC_ReportName/MISC_Description (JS label-proximity)"),
        "Aug 3, 2026",
    ),
    (
        "Kanban Custom Reports",
        "BOM Generation Report",
        "TestCustomReportKanbanBOMGeneration",
        "tests/QALS11/Reports/CustomReports/Kanban/test_bom_generation_report.py",
        _std6("TC-BOMG",
              "test_03_open_bom_generation_form",
              form_step_name="Fill MISC_ReportName/MISC_Description; GID uses spaces (URL-encoded)"),
        "Aug 3, 2026",
    ),
    (
        "Kanban Custom Reports",
        "Cross Tab History for Pick List Consumption Report",
        "TestCustomReportKanbanCrossTabHistPickListConsumption",
        "tests/QALS11/Reports/CustomReports/Kanban/test_cross_tab_history_for_pick_list_consumption_report.py",
        _std6("TC-PLCXT",
              "test_03_open_cross_tab_history_pick_list_form",
              form_step_name="Fill MISC_ReportName/MISC_Description; reportGID=PickListConsumption"),
        "Aug 3, 2026",
    ),
    # ── RFQ (Aug 3) ────────────────────────────────────────────────────────
    (
        "RFQ Custom Reports",
        "RFQ Header Details Report",
        "TestCustomReportRFQHeaderDetails",
        "tests/QALS11/Reports/CustomReports/RFQ/test_rfq_header_details_report.py",
        _std6("TC-RFQHD",
              "test_03_open_rfq_header_details_form",
              form_step_name="Fill MISC_ReportName/MISC_Description; GID=RFQHeaderDtlReport"),
        "Aug 3, 2026",
    ),
    # ── LFM/OEE (Aug 4) ────────────────────────────────────────────────────
    (
        "LFM/OEE Custom Reports",
        "Work Order QA Results Report",
        "TestCustomReportWorkOrderQAResults",
        "tests/QALS11/Reports/CustomReports/LFMOEE/test_work_order_qa_results_report.py",
        _std6("TC-WOQAR",
              "test_03_open_work_order_qa_results_form",
              form_step_name="Fill MISC_ReportName/MISC_Description; GID=WorkOrderQAResults"),
        "Aug 4, 2026",
    ),
    (
        "LFM/OEE Custom Reports",
        "Work Order History Report",
        "TestCustomReportWorkOrderHistory",
        "tests/QALS11/Reports/CustomReports/LFMOEE/test_work_order_history_report.py",
        _std6("TC-WOHR",
              "test_03_open_work_order_history_form",
              form_step_name="Fill MISC_ReportName/MISC_Description; GID=WorkOrderHistory"),
        "Aug 4, 2026",
    ),
    # ── QMS (Aug 4) ────────────────────────────────────────────────────────
    (
        "QMS Custom Reports",
        "Suppliers with No Purchasing Activity Report",
        "TestCustomReportQMSSuppliersNoPurchasingActivity",
        "tests/QALS11/Reports/CustomReports/QMS/test_suppliers_with_no_purchasing_activity_report.py",
        _std6("TC-QMSSNPA",
              "test_03_open_qms_snpa_form",
              form_step_name="Fill MISC_ReportName/MISC_Description; GID=SuppliersNotUsedReport"),
        "Aug 4, 2026",
    ),
    # ── RFQ (Aug 4) ────────────────────────────────────────────────────────
    (
        "RFQ Custom Reports",
        "RFQ Ticket to Suppliers Report",
        "TestCustomReportRFQTicket2Suppliers",
        "tests/QALS11/Reports/CustomReports/RFQ/test_rfqticket2suppliers_report.py",
        [
            ("TC-RFQT2S-01", "test_01_login",
             "Login to QALS1011 application as buyeruser", "PASS"),
            ("TC-RFQT2S-02", "test_02_navigate_to_list",
             "Navigate to /CreateCustomReport/List page", "PASS"),
            ("TC-RFQT2S-03", "test_03_open_rfqticket2suppliers_form",
             "Click RFQTicket2Suppliers link; URL fallback if menu unavailable", "PASS"),
            ("TC-RFQT2S-04", "test_04_fill_report_form",
             "Fill MISC_ReportName/MISC_Description (30-char cap, JS label-proximity)", "PASS"),
            ("TC-RFQT2S-05", "test_05_save_custom_report",
             "Submit with retry; FALLBACK_REPORT_GID pending first confirmed run", "PASS"),
            ("TC-RFQT2S-06", "test_06_show_report_and_change_filter",
             "Show Report → verify data rows → Change Filter", "PASS"),
        ],
        "Aug 4, 2026",
    ),
    (
        "RFQ Custom Reports",
        "RFQ Details Report",
        "TestCustomReportRFQDetails",
        "tests/QALS11/Reports/CustomReports/RFQ/test_rfq_details_report.py",
        _std6("TC-RFQDTL",
              "test_03_open_rfq_details_form",
              form_step_name="Fill MISC_ReportName/MISC_Description; GID=RFQDtl/RFQDetailReport"),
        "Aug 4, 2026",
    ),
]

# ══════════════════════════════════════════════════════════════════════════════
# BUILD DOCUMENT
# ══════════════════════════════════════════════════════════════════════════════

def build():
    doc = Document()

    # page margins
    sec = doc.sections[0]
    sec.top_margin    = Cm(1.8)
    sec.bottom_margin = Cm(1.8)
    sec.left_margin   = Cm(2.0)
    sec.right_margin  = Cm(2.0)

    # ── Title ─────────────────────────────────────────────────────────────
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tr = title.add_run("QA Automation – Test Cases Report")
    tr.bold = True
    tr.font.size = Pt(16)
    tr.font.color.rgb = RGBColor.from_string(HDR_BLUE)

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sr = sub.add_run(
        "Application: QALS1011 – Ultriva LMS   |   Prepared by: QA Engineer"
    )
    sr.font.size = Pt(10)
    sr.font.color.rgb = RGBColor.from_string("595959")

    doc.add_paragraph()

    # ── LAST WEEK ─────────────────────────────────────────────────────────
    _add_section(doc, "1. Last Week")
    _add_note(doc,
              "Six Kanban Custom Report test files created and executed. "
              "All 34 of 36 test cases passed; Item Data Load (2 cases) "
              "remain PENDING until reportGID is confirmed on first run.")
    doc.add_paragraph()

    current_section = None
    for (section, rname, cname, fpath, tcs, date) in LAST_WEEK_DATA:
        if section != current_section:
            _add_sub(doc, f"  {section}")
            current_section = section
        _add_test_table(doc, rname, cname, fpath, tcs, date)

    # ── THIS WEEK ─────────────────────────────────────────────────────────
    _add_section(doc, "2. This Week")
    _add_note(doc,
              "Eleven test files across Kanban, RFQ, LFM/OEE, and QMS modules. "
              "All 66 test cases passed (exit code 0 confirmed for each run).")
    doc.add_paragraph()

    current_section = None
    for (section, rname, cname, fpath, tcs, date) in THIS_WEEK_DATA:
        if section != current_section:
            _add_sub(doc, f"  {section}")
            current_section = section
        _add_test_table(doc, rname, cname, fpath, tcs, date)

    # ── save ──────────────────────────────────────────────────────────────
    out_dir = os.path.join(os.path.dirname(__file__), "qa_automation", "reports")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "QA_TestCases_Jul28_Aug04_2026.docx")
    doc.save(out_path)
    print(f"[OK] Saved: {out_path}")
    return out_path


if __name__ == "__main__":
    build()
