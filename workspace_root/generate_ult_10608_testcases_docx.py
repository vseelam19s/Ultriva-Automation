"""Generate ULT-10608 (Steel Origin | Emerson print plug-in: label fields and 2D barcode element) test cases DOCX."""
from pathlib import Path
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = Path(r"c:\Prcatices-AI\docs\ULT-10608_test_cases.docx")

COLS = ["ID", "Title", "Preconditions", "Steps", "Expected Result", "Pri", "Type", "AC"]
WIDTHS = [0.55, 1.35, 1.55, 2.6, 2.3, 0.4, 0.7, 0.45]

PRE_BASE = ("Emerson custom print plug-in active (SysConfig CUSTOM_PRINT_ASSEMBLY_NAME = Leansuite.Custom.Emerson). "
            "STEEL_ORIGIN_DI = 5Z (default).")
PRE_US = PRE_BASE + " Flagged card C1 shipped with Steel Origin 'US' (steelorigin=US stored)."
PRE_AA = PRE_BASE + " Flagged card C2 shipped with Steel Origin 'AA' (steelorigin=AA stored)."
PRE_NONE = PRE_BASE + " Card C3 with no stored Steel Origin (unflagged, or flagged but never shipped)."
ENV = "GS 5K RS EOT"

SECTIONS = [
    ("1. 2D Barcode - Steel Origin Element", [
        ("TC-01", "PX2dBarCode carries 5ZUS for 'US'",
         PRE_US,
         "1. Print the label of C1 (client print).\n2. Capture the label data (PX2dBarCode) from AddCustomCardData / label data log.",
         "PX2dBarCode ends with GS '5ZUS' RS EOT, i.e. ... GS 5K<PO no> GS 5ZUS RS EOT.", "High", "Functional", "AC1"),
        ("TC-02", "PXIR2dBarCode carries 5ZUS for 'US'",
         PRE_US,
         "1. Print the label of C1.\n2. Capture PXIR2dBarCode.",
         "PXIR2dBarCode ends with GS '5ZUS' RS EOT, i.e. ... GS 5K<PO release no> GS 5ZUS RS EOT.", "High", "Functional", "AC1"),
        ("TC-03", "Existing elements keep content and order (US)",
         PRE_US,
         "1. Capture PX2dBarCode and PXIR2dBarCode for C1.\n2. Compare with output of the previous build for the same card.",
         "Header [)> RS 06 and elements P, Q, V, S, K, 5K are present, unchanged, in the same order. Only 'GS 5ZUS' is added after 5K and before RS EOT.", "High", "Regression", "AC1"),
        ("TC-04", "5Z element is inserted after 5K and before trailer",
         PRE_US,
         "1. Split the 2D string on GS.\n2. Check the position of the 5Z element.",
         "Last data element is 5ZUS; the element directly before it is 5K<value>; RS EOT trailer follows 5ZUS with no extra separator.", "High", "Functional", "AC1"),
        ("TC-05", "2D element for 'AA' (non-US)",
         PRE_AA,
         "1. Print the label of C2.\n2. Capture PX2dBarCode and PXIR2dBarCode.",
         "Both strings end with GS '5ZAA' RS EOT; other elements unchanged.", "High", "Functional", "AC2"),
        ("TC-06", "K element differs per variant, 5Z identical",
         PRE_US,
         "1. Capture both 2D strings for C1.\n2. Compare the K and 5Z elements.",
         "K = PO number in PX2dBarCode and PO release number in PXIR2dBarCode (as before). 5ZUS is identical in both.", "Medium", "Functional", "AC1"),
        ("TC-07", "Header, separators and trailer unchanged",
         PRE_US,
         "1. Compare header ([)> RS 06), GS separators and RS EOT trailer against the previous build.",
         "Header, separator characters/encoding and trailer are identical to the previous build.", "High", "Regression", "AC1"),
        ("TC-08", "Both variants always consistent",
         PRE_US + " Repeat with C2.",
         "1. For each card capture both variants.\n2. Verify 5Z presence in each.",
         "Either both variants carry the 5Z element or neither does; no card has it in only one variant.", "High", "Functional", "AC1/AC2"),
        ("TC-09", "Scan 2D barcode - DataMatrix ECC200 decodes with 5Z element",
         PRE_US + " Desktop print client and a 2D scanner available.",
         "1. Print C1 via the desktop print client.\n2. Scan DM2DBarCode with a 2D scanner.\n3. Inspect the decoded string.",
         "Barcode decodes as DataMatrix ECC200. Decoded data contains P, Q, V, S, K, 5K and 5ZUS in order.", "High", "E2E", "AC1"),
    ]),
    ("2. Label Fields - SteelOrigin and PXSteelOrigin", [
        ("TC-10", "Text field for 'US'",
         PRE_US,
         "1. Print C1.\n2. Read the label field SteelOrigin (AppendString).",
         "SteelOrigin = 'Steel Origin: US'.", "High", "Functional", "AC1"),
        ("TC-11", "1D barcode value for 'US'",
         PRE_US,
         "1. Print C1.\n2. Read the field PXSteelOrigin.",
         "PXSteelOrigin = '5ZUS'.", "High", "Functional", "AC1"),
        ("TC-12", "Text field for 'AA' prints the code (D5)",
         PRE_AA,
         "1. Print C2.\n2. Read SteelOrigin.",
         "SteelOrigin = 'Steel Origin: AA' (code printed, not a translated name such as 'Non-US').", "High", "Functional", "AC2"),
        ("TC-13", "1D barcode value for 'AA'",
         PRE_AA,
         "1. Print C2.\n2. Read PXSteelOrigin.",
         "PXSteelOrigin = '5ZAA'.", "High", "Functional", "AC2"),
        ("TC-14", "Label visual check (client print)",
         PRE_US + " Label template contains SteelOrigin and PXSteelOrigin items.",
         "1. Print C1 and C2 through the desktop print client.\n2. Inspect the printed labels.",
         "Human-readable text and linear barcode are rendered correctly; the 1D barcode scans as 5ZUS / 5ZAA.", "High", "E2E", "AC1/AC2"),
        ("TC-15", "Text, 1D barcode and 2D element are consistent",
         PRE_US + " Repeat with C2.",
         "1. Compare SteelOrigin text, PXSteelOrigin and the 5Z element in both 2D strings.",
         "All three forms express the same value (US/US/5ZUS or AA/AA/5ZAA).", "Medium", "Functional", "AC1/AC2"),
    ]),
    ("3. Missing Value - Label Unchanged (D3 / D11)", [
        ("TC-16", "No stored value - fields empty",
         PRE_NONE,
         "1. Print C3.\n2. Read SteelOrigin and PXSteelOrigin.",
         "SteelOrigin = '' and PXSteelOrigin = ''.", "High", "Functional", "AC3"),
        ("TC-17", "No stored value - 2D strings byte-identical to before",
         PRE_NONE,
         "1. Capture PX2dBarCode and PXIR2dBarCode on the new build.\n2. Capture the same for the same card on the previous build.\n3. Compare byte by byte.",
         "Both strings are identical to the previous build; no GS 5Z element and no extra GS.", "High", "Regression", "AC3"),
        ("TC-18", "Printing depends on stored value, not on current flag (D11)",
         "Card C4 shipped with steelorigin=US while the supplier-item was flagged; flag later set to N.",
         "1. Print / reprint C4.",
         "Label still shows 'Steel Origin: US', PXSteelOrigin=5ZUS and 5ZUS in both 2D strings.", "High", "Functional", "AC3"),
        ("TC-19", "Flag set after shipment, no stored value (D11)",
         "Card C5 shipped while supplier-item was unflagged (no steelorigin stored); flag then set to Y.",
         "1. Print C5.",
         "SteelOrigin and PXSteelOrigin are empty; 2D strings have no 5Z element.", "High", "Functional", "AC3"),
        ("TC-20", "Non-flagged item, label layout unaffected",
         PRE_NONE,
         "1. Print C3 on the client.\n2. Compare the printed label with one printed on the previous build.",
         "Label is visually identical; empty SteelOrigin / PXSteelOrigin items print nothing.", "Medium", "Regression", "AC3"),
        ("TC-21", "steelorigin key present but blank",
         PRE_BASE + " Card with steelorigin='' in CYCL_IGParams and KBC_IGParams.",
         "1. Print the card.",
         "Treated as no value: both fields empty, 2D strings unchanged.", "Medium", "Negative", "AC3"),
    ]),
    ("4. Reading and Validating the Value", [
        ("TC-22", "Value read from CYCL_IGParams",
         PRE_BASE + " Card with steelorigin=US in CYCL_IGParams, none in KBC_IGParams.",
         "1. Print the card.",
         "SteelOrigin = 'Steel Origin: US'; 5ZUS in 2D strings.", "High", "Functional", "AC1"),
        ("TC-23", "Fallback to KBC_IGParams when CYCL has no value",
         PRE_BASE + " Card with no steelorigin in CYCL_IGParams, steelorigin=AA in KBC_IGParams (EboPrintKanbanCardsView).",
         "1. Print the card.",
         "SteelOrigin = 'Steel Origin: AA'; 5ZAA in 2D strings.", "High", "Functional", "AC2"),
        ("TC-24", "CYCL value takes precedence over KBC",
         PRE_BASE + " CYCL_IGParams steelorigin=US, KBC_IGParams steelorigin=AA.",
         "1. Print the card.",
         "US is used: 'Steel Origin: US', 5ZUS.", "High", "Functional", "AC1"),
        ("TC-25", "Invalid value is treated as empty",
         PRE_BASE + " Cards with steelorigin = 'XX', 'USA', 'CN', 'N/A'.",
         "1. Print each card.",
         "For each: SteelOrigin = '', PXSteelOrigin = '', no 5Z element in either 2D string.", "High", "Negative", "AC3"),
        ("TC-26", "Lower-case / padded values",
         PRE_BASE + " Cards with steelorigin = 'us', 'aa', ' US ' (confirm intended behaviour with dev).",
         "1. Print each card.",
         "Per the 'accept only US / AA' rule, non-exact values are treated as empty unless the implementation normalises them; result is consistent and documented.", "Low", "Negative", "AC3"),
        ("TC-27", "Invalid CYCL value and valid KBC value",
         PRE_BASE + " CYCL_IGParams steelorigin=XX, KBC_IGParams steelorigin=US.",
         "1. Print the card.\n2. Record the result (confirm intended behaviour with dev).",
         "Behaviour is deterministic and matches the implementation (either fallback to US, or empty because the CYCL value is invalid). Raise if unclear.", "Low", "Negative", "AC3"),
        ("TC-28", "Value read for the current row in multi-card print",
         "Three cards in one print job: C1 (US), C2 (AA), C3 (no value).",
         "1. Select all three cards and print.\n2. Inspect label data per card.",
         "Each label uses its own row: US / AA / empty. No value leaks between cards.", "High", "Functional", "AC1/AC2/AC3"),
        ("TC-29", "Other supplier / item data unaffected by new read",
         PRE_US,
         "1. Print C1.\n2. Check other custom fields set in AddCustomCardData (P, Q, V, S, PO, release, etc.).",
         "All other fields are unchanged versus the previous build.", "Medium", "Regression", "AC1"),
    ]),
    ("5. Configurable Data Identifier - STEEL_ORIGIN_DI (D9)", [
        ("TC-30", "Default DI is 5Z when key is absent",
         PRE_US + " Key STEEL_ORIGIN_DI deleted from SysConfig.",
         "1. Print C1.",
         "PXSteelOrigin = '5ZUS'; 2D strings end with GS 5ZUS RS EOT; no error.", "High", "Functional", "AC4"),
        ("TC-31", "DI changed to XY applies without rebuild",
         PRE_US,
         "1. Set SysConfig STEEL_ORIGIN_DI = 'XY'.\n2. Print C1 (no rebuild/redeploy).",
         "PXSteelOrigin = 'XYUS'; both 2D strings end with GS 'XYUS' RS EOT. Text field is still 'Steel Origin: US'.", "High", "Functional", "AC4"),
        ("TC-32", "Changed DI applied to 'AA'",
         PRE_AA + " STEEL_ORIGIN_DI = 'XY'.",
         "1. Print C2.",
         "PXSteelOrigin = 'XYAA'; 2D element 'XYAA' in both variants.", "Medium", "Functional", "AC4"),
        ("TC-33", "DI change does not affect empty-value labels",
         PRE_NONE + " STEEL_ORIGIN_DI = 'XY'.",
         "1. Print C3.",
         "Fields empty; 2D strings unchanged and contain no DI.", "Medium", "Regression", "AC3/AC4"),
        ("TC-34", "Restoring DI to 5Z reverts output",
         "STEEL_ORIGIN_DI = 'XY' previously tested.",
         "1. Set STEEL_ORIGIN_DI = '5Z'.\n2. Print C1.",
         "Output returns to 5ZUS.", "Medium", "Functional", "AC4"),
        ("TC-35", "Blank DI value",
         PRE_US + " STEEL_ORIGIN_DI = ''.",
         "1. Print C1.\n2. Record the result (confirm intended behaviour with dev).",
         "Falls back to default 5Z (preferred) or behaves deterministically without exception; label printing does not fail.", "Low", "Negative", "AC4"),
        ("TC-36", "Seed script - key inserted",
         "DbScripts\\SqlServer\\12_CEK1010.sql on a DB without STEEL_ORIGIN_DI.",
         "1. Run the script.\n2. SELECT the STEEL_ORIGIN_DI row in SysConfig.",
         "Key STEEL_ORIGIN_DI exists with default value '5Z'.", "High", "DB", "AC4"),
        ("TC-37", "Seed script - idempotent",
         "STEEL_ORIGIN_DI already exists with value 'XY'.",
         "1. Re-run 12_CEK1010.sql twice.\n2. SELECT the key.",
         "No duplicate row, no error; existing value 'XY' is not overwritten.", "High", "DB", "AC4"),
        ("TC-38", "Seed script - structure conventions",
         "Code review of 12_CEK1010.sql.",
         "1. Review the script.",
         "Insert uses IF NOT EXISTS ... INSERT inside the Mandatory block; @CURRENT_REL_VERSION is bumped; a 'last edit' header line is added.", "Medium", "Code review", "AC4"),
        ("TC-39", "Seed script runs on an existing customer DB",
         "Customer DB with other CEK1010 keys already seeded.",
         "1. Run the script.\n2. Compare other SysConfig rows before/after.",
         "Only STEEL_ORIGIN_DI is added; other rows unchanged.", "Medium", "DB", "AC4"),
    ]),
    ("6. Reprint and History (Cycle GID)", [
        ("TC-40", "Reprint from card history (cycle GID)",
         "Flagged card shipped with 'AA' and printed from card history (EboPrintKanbanHistoryView, CYCL_IGParams only).",
         "1. Open card history and reprint the label for the cycle.\n2. Inspect label data.",
         "SteelOrigin = 'Steel Origin: AA'; PXSteelOrigin = '5ZAA'; both 2D strings carry 5ZAA.", "High", "Functional", "AC5"),
        ("TC-41", "Reprint from history - US",
         "Flagged card shipped with 'US' printed from card history.",
         "1. Reprint from history.",
         "'Steel Origin: US', 5ZUS in 1D and both 2D strings.", "High", "Functional", "AC5"),
        ("TC-42", "History reprint with no stored value",
         "Cycle with no stored steelorigin.",
         "1. Reprint from history.",
         "Fields empty; 2D strings identical to previous build.", "High", "Regression", "AC3/AC5"),
        ("TC-43", "Card print and reprint (EboPrintKanbanCardsView)",
         PRE_US,
         "1. Print C1 from the card print screen.\n2. Reprint C1.",
         "Both prints produce identical label data containing 'Steel Origin: US' and 5ZUS.", "High", "Functional", "AC1"),
        ("TC-44", "Reprint after correction on Set Shipment Information (T6)",
         "Card shipped with 'US', then corrected to 'AA' on Set Shipment Information.",
         "1. Reprint the label.",
         "Label shows 'Steel Origin: AA' and 5ZAA; value is re-queried each time, no stale 'US'.", "High", "Functional", "AC5"),
        ("TC-45", "Reprint after correction removes nothing else",
         "As TC-44.",
         "1. Compare reprint data before and after the correction.",
         "Only Steel Origin related text/barcode values change; all other elements identical.", "Medium", "Regression", "AC5"),
    ]),
    ("7. Item Weight Defect Fix (D7)", [
        ("TC-46", "ItemWeight uses current row in multi-card print",
         "Cards C1, C2, C3 of items with different ItemWeight values (e.g. 1.5, 2.5, 3.5) printed in one job.",
         "1. Print all three cards together.\n2. Read the ItemWeight field per label.",
         "Each label shows its own item weight (1.5 / 2.5 / 3.5); card 1's weight is not repeated.", "High", "Defect fix", "-"),
        ("TC-47", "ItemWeight single card unchanged",
         "Single card with known ItemWeight.",
         "1. Print the card.",
         "ItemWeight value is the same as before the change.", "Medium", "Regression", "-"),
        ("TC-48", "ItemWeight with first card having no weight",
         "Multi-card print: card 1 has empty ItemWeight, card 2 has 2.5.",
         "1. Print both cards.",
         "Card 2 shows 2.5 (not empty from row 0).", "Medium", "Defect fix", "-"),
        ("TC-49", "ItemWeight in history reprint",
         "Multi-cycle history reprint of cards with different weights.",
         "1. Reprint from card history.",
         "Each label shows the right weight; no exception if ITM_IGParams is unavailable.", "Low", "Regression", "-"),
    ]),
    ("8. Regression, Rendering and Risks", [
        ("TC-50", "Non-Emerson / no plug-in printing unaffected",
         "CUSTOM_PRINT_ASSEMBLY_NAME empty or set to another assembly.",
         "1. Print a card.",
         "Label prints as before; no Steel Origin fields or errors.", "Medium", "Regression", "AC3"),
        ("TC-51", "Build of Leansuite.Custom.Emerson / CustomPrintScanSvc.sln",
         "Source access.",
         "1. Build CustomPrintScanSvc.sln.",
         "Build succeeds with no errors or new warnings; assembly loads via EboCardLabel.GetCustomCardData.", "High", "Build", "-"),
        ("TC-52", "Browser GIF renderer / ConfirmPrintController.DoLabel",
         PRE_US,
         "1. Preview the label via the browser GIF renderer (EboLabelItemRT) and secure-link DoLabel.",
         "No error; 2D barcode is not rendered by these paths (known limitation). Verification of 2D is via client print only.", "Low", "Regression", "-"),
        ("TC-53", "Separators encoded as real RS / GS / EOT bytes (unverified)",
         PRE_US + " 2D scanner with raw/hex output.",
         "1. Scan the 2D barcode before and after this change.\n2. View the decoded string in hex.\n3. Check bytes 0x1E, 0x1D, 0x04.",
         "Confirm whether real control bytes or the literal text &#x1E; / &#x1D; / &#x04; is encoded. Result is the same before and after the change; if literal text is encoded, raise it and do not change behaviour silently (see T5/T9).", "High", "E2E", "AC1"),
        ("TC-54", "Legacy ASP include untouched",
         "Code access.",
         "1. Check CoreAppDevCustom\\CEK_EmersonITSS\\CNA\\ASP\\Include\\i_CustomPrintData.asp in the change set.",
         "File is not modified.", "Low", "Code review", "-"),
        ("TC-55", "Barcode length within DataMatrix capacity",
         PRE_US + " Long PO number and PO release number values.",
         "1. Print C1 with maximum-length field values.\n2. Scan.",
         "Adding the 5Z element (6 chars with separator) does not break encoding or readability of the 2D barcode.", "Medium", "Boundary", "AC1"),
    ]),
]

AC_MATRIX = [
    ("AC1 - Value encoded in both 2D variants (US)", "TC-01 to TC-04, TC-06 to TC-11, TC-15, TC-22, TC-24, TC-43, TC-53, TC-55"),
    ("AC2 - Non-US (AA): 2D element 5ZAA and text 'Steel Origin: AA'", "TC-05, TC-08, TC-12, TC-13, TC-14, TC-23, TC-28"),
    ("AC3 - Unflagged / missing value, barcode unchanged", "TC-16 to TC-21, TC-25 to TC-28, TC-33, TC-42, TC-50"),
    ("AC4 - Configurable Data Identifier", "TC-30 to TC-39"),
    ("AC5 - Reprint from history", "TC-40 to TC-42, TC-44, TC-45"),
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
r = t.add_run("ULT-10608 - Test Cases")
r.bold = True
r.font.size = Pt(18)
r.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
doc.add_paragraph("Steel Origin | Emerson print plug-in: label fields and 2D barcode element").runs[0].font.size = Pt(11)

info = doc.add_table(rows=0, cols=2)
info.style = "Table Grid"
for k, v in [
    ("Ticket", "ULT-10608 (Epic ULT-10604) - Status: In QA Review - Fix version 10.10.6"),
    ("Labels", "Copeland, SteelOrigin"),
    ("Depends on / Blocks", "Depends on ULT-10607; blocks T5"),
    ("Scope", "PrintData.cs (CustomPrintScanSvc.PrintData, AddCustomCardData): read steelorigin from CYCL_IGParams / KBC_IGParams (US/AA only); "
              "label fields SteelOrigin and PXSteelOrigin; 5Z element in PX2dBarCode and PXIR2dBarCode; SysConfig STEEL_ORIGIN_DI (default 5Z) seeded in 12_CEK1010.sql; "
              "ItemWeight row fix (row 0 -> nRow)."),
    ("2D format", "[)> RS 06 GS P GS Q GS V GS S GS K GS 5K [GS <DI><value>] RS EOT - the bracketed element is added only when a value exists."),
    ("Out of scope", "Legacy ASP i_CustomPrintData.asp (reference only); browser GIF renderer and ConfirmPrintController.DoLabel do not render 2D barcodes."),
    ("Open points", "'5Z' DI still provisional (open item 1c); real RS/GS/EOT byte encoding unverified (TC-53); behaviour for lower-case/padded values and invalid CYCL + valid KBC values to be confirmed (TC-26, TC-27)."),
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
