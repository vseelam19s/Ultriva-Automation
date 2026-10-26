"""
QA Automation Demo Document Generator
Generates a comprehensive Word document for a lead demo.
Run: python generate_demo_document.py
"""

import os
import io
from datetime import datetime
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ── Paths ────────────────────────────────────────────────────────────────────
SCREENSHOTS_DIR = r"c:\Prcatices-AI\qa_automation\reports\screenshots"
OUTPUT_DOC      = r"c:\Prcatices-AI\QA_Automation_Demo.docx"

# ── Helper: safe screenshot path ─────────────────────────────────────────────
def ss(name):
    p = os.path.join(SCREENSHOTS_DIR, name)
    return p if os.path.exists(p) else None


# ─────────────────────────────────────────────────────────────────────────────
# DIAGRAM GENERATORS
# ─────────────────────────────────────────────────────────────────────────────

def make_architecture_diagram(out_path):
    """Overall QA Automation Architecture."""
    fig, ax = plt.subplots(figsize=(14, 9))
    ax.set_xlim(0, 14); ax.set_ylim(0, 9); ax.axis("off")
    fig.patch.set_facecolor("#F0F4F8")

    # title
    ax.text(7, 8.6, "QA Automation Framework — Architecture Overview",
            ha="center", va="center", fontsize=14, fontweight="bold", color="#1F4E79")

    # ── boxes ────────────────────────────────────────────────────────────────
    boxes = [
        # (x, y, w, h, label, sublabel, fill, text_color)
        (1.0, 6.5, 2.8, 1.1, "mcp.json", "MCP Server Config\n(testrail / jira / playwright)", "#1F4E79", "white"),
        (5.8, 6.5, 2.8, 1.1, "VS Code\nCopilot Chat", "AI Agent + MCP Client", "#2E75B6", "white"),
        (10.5,6.5, 2.8, 1.1, "config/config.py", "Credentials & Settings", "#404040", "white"),

        (1.0, 4.5, 2.8, 1.1, "TestRail MCP\nServer", "testrail.py @ genai.testrail.io", "#538135", "white"),
        (5.8, 4.5, 2.8, 1.1, "JIRA MCP\nServer", "atlassian-mcp-server\natlassian.net", "#C55A11", "white"),
        (10.5,4.5, 2.8, 1.1, "Playwright MCP\nServer", "@playwright/mcp\nBrowser Automation", "#7030A0", "white"),

        (1.0, 2.3, 2.8, 1.1, "pytest\nTest Suite", "tests/  (TC-001 … TC-205)", "#1F4E79", "white"),
        (5.8, 2.3, 2.8, 1.1, "Page Object\nModel", "pages/\n(login, dashboard, admin)", "#2E75B6", "white"),
        (10.5,2.3, 2.8, 1.1, "utils/", "driver_setup.py\nexcel_reporter.py\ntestrail_client.py", "#404040", "white"),

        (3.5, 0.4, 2.8, 1.1, "Reports", "Excel • HTML • Screenshots", "#833C00", "white"),
        (7.5, 0.4, 2.8, 1.1, "Ultriva LMS\nQALS1011", "engineering.ultrivalms.com", "#1F497D", "white"),
    ]

    for (x, y, w, h, label, sub, fill, tc) in boxes:
        rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05",
                              facecolor=fill, edgecolor="white", linewidth=1.5)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h*0.62, label, ha="center", va="center",
                fontsize=9, fontweight="bold", color=tc)
        ax.text(x + w/2, y + h*0.25, sub, ha="center", va="center",
                fontsize=6.5, color=tc, alpha=0.9)

    # ── arrows ───────────────────────────────────────────────────────────────
    arrows = [
        # mcp.json -> copilot
        (3.8, 7.05, 5.8, 7.05),
        # copilot -> testrail mcp
        (6.5, 6.5, 2.8, 5.6),
        # copilot -> jira mcp
        (7.2, 6.5, 7.2, 5.6),
        # copilot -> playwright
        (7.9, 6.5, 11.9, 5.6),
        # testrail mcp -> pytest
        (2.4, 4.5, 2.4, 3.4),
        # playwright -> page objects
        (11.9, 4.5, 7.2, 3.4),
        # pytest -> reports
        (2.4, 2.3, 4.0, 1.5),
        # pytest -> ultriva
        (3.8, 2.85, 7.5, 1.5),
        # page objects -> ultriva
        (7.2, 2.3, 8.0, 1.5),
        # config -> testrail_client (utils)
        (11.9, 4.5, 11.9, 3.4),
    ]
    for (x1,y1,x2,y2) in arrows:
        ax.annotate("", xy=(x2,y2), xytext=(x1,y1),
                    arrowprops=dict(arrowstyle="->", color="#666666", lw=1.2))

    # legend
    legend_items = [
        mpatches.Patch(color="#1F4E79", label="Core Framework"),
        mpatches.Patch(color="#538135", label="TestRail Integration"),
        mpatches.Patch(color="#C55A11", label="JIRA Integration"),
        mpatches.Patch(color="#7030A0", label="Browser Automation"),
        mpatches.Patch(color="#404040", label="Config / Utils"),
    ]
    ax.legend(handles=legend_items, loc="lower right", fontsize=7.5,
              framealpha=0.9, edgecolor="#cccccc")

    plt.tight_layout(pad=0.5)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  [diagram] Saved architecture diagram → {out_path}")


def make_mcp_flow_diagram(out_path):
    """TestRail + JIRA MCP flow diagram."""
    fig, ax = plt.subplots(figsize=(13, 7))
    ax.set_xlim(0, 13); ax.set_ylim(0, 7); ax.axis("off")
    fig.patch.set_facecolor("#FAFAFA")

    ax.text(6.5, 6.6, "MCP Server Integration Flow — TestRail & JIRA",
            ha="center", fontsize=13, fontweight="bold", color="#1F4E79")

    steps_testrail = [
        (0.4, 4.8, "1. VS Code Copilot\nChat (Prompt)"),
        (2.6, 4.8, "2. MCP Client\n(mcp.json)"),
        (4.8, 4.8, "3. TestRail MCP\nServer Process"),
        (7.0, 4.8, "4. testrail_client.py\n(API Wrapper)"),
        (9.2, 4.8, "5. TestRail REST\nAPI"),
        (11.2,4.8, "6. Test Cases\nCreated / Updated"),
    ]
    colors_tr = ["#2E75B6","#1F4E79","#538135","#375623","#538135","#70AD47"]

    for i,(x,y,label) in enumerate(steps_testrail):
        rect = FancyBboxPatch((x,y), 1.8, 0.9, boxstyle="round,pad=0.05",
                              facecolor=colors_tr[i], edgecolor="white", linewidth=1.2)
        ax.add_patch(rect)
        ax.text(x+0.9, y+0.45, label, ha="center", va="center",
                fontsize=7.5, color="white", fontweight="bold")
        if i < len(steps_testrail)-1:
            ax.annotate("", xy=(x+1.95, y+0.45), xytext=(x+1.8, y+0.45),
                        arrowprops=dict(arrowstyle="->", color="#333", lw=1.4))

    ax.text(0.4, 5.85, "TestRail MCP Flow:", fontsize=9, color="#538135", fontweight="bold")

    steps_jira = [
        (0.4, 2.8, "1. VS Code Copilot\nChat (Prompt)"),
        (2.6, 2.8, "2. Atlassian MCP\nServer (HTTP)"),
        (4.8, 2.8, "3. JIRA REST\nAPI Call"),
        (7.0, 2.8, "4. jira_client.py\n(Python wrapper)"),
        (9.2, 2.8, "5. Issue / Subtask\nCreated"),
        (11.2,2.8, "6. Test Cases\nLinked to Ticket"),
    ]
    colors_jira = ["#2E75B6","#C55A11","#C55A11","#843C0C","#ED7D31","#FFC000"]

    for i,(x,y,label) in enumerate(steps_jira):
        rect = FancyBboxPatch((x,y), 1.8, 0.9, boxstyle="round,pad=0.05",
                              facecolor=colors_jira[i], edgecolor="white", linewidth=1.2)
        ax.add_patch(rect)
        ax.text(x+0.9, y+0.45, label, ha="center", va="center",
                fontsize=7.5, color="white", fontweight="bold")
        if i < len(steps_jira)-1:
            ax.annotate("", xy=(x+1.95, y+0.45), xytext=(x+1.8, y+0.45),
                        arrowprops=dict(arrowstyle="->", color="#333", lw=1.4))

    ax.text(0.4, 3.85, "JIRA MCP Flow:", fontsize=9, color="#C55A11", fontweight="bold")

    # mcp.json config excerpt box
    config_text = (
        'mcp.json  — Key Servers\n\n'
        '"testrail": {\n'
        '  command: python testrail.py\n'
        '  env: TESTRAIL_URL / EMAIL / API_KEY\n'
        '}\n\n'
        '"com.atlassian/atlassian-mcp-server": {\n'
        '  type: http\n'
        '  url: https://mcp.atlassian.com/v1/mcp\n'
        '  headers: Authorization Bearer <token>\n'
        '}'
    )
    rect2 = FancyBboxPatch((0.3, 0.2), 12.4, 2.0, boxstyle="round,pad=0.1",
                           facecolor="#F2F2F2", edgecolor="#AAAAAA", linewidth=1)
    ax.add_patch(rect2)
    ax.text(6.5, 0.3, config_text, ha="center", va="bottom",
            fontsize=7, color="#333333", family="monospace")

    plt.tight_layout(pad=0.3)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  [diagram] Saved MCP flow diagram → {out_path}")


def make_test_execution_diagram(out_path):
    """Pytest execution flow."""
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(0,12); ax.set_ylim(0,6); ax.axis("off")
    fig.patch.set_facecolor("#F8F9FA")

    ax.text(6, 5.65, "Pytest Test Execution Flow",
            ha="center", fontsize=13, fontweight="bold", color="#1F4E79")

    steps = [
        (0.5,3.2, "pytest\ncommand", "#1F4E79"),
        (2.3,3.2, "conftest.py\nFixtures\n& Hooks", "#2E75B6"),
        (4.1,3.2, "driver_setup.py\nChrome/Firefox\n/Edge Driver", "#404040"),
        (5.9,3.2, "Page Object\nModel\n(login/dashboard)", "#2E75B6"),
        (7.7,3.2, "Ultriva LMS\nQALS1011\nApp Under Test", "#1F497D"),
        (9.5,3.2, "excel_reporter\n+\npytest-html", "#833C00"),
        (11.0,3.2,"TestRail\nResults Push", "#538135"),
    ]

    for i,(x,y,label,color) in enumerate(steps):
        rect = FancyBboxPatch((x,y), 1.6, 1.1, boxstyle="round,pad=0.08",
                              facecolor=color, edgecolor="white", linewidth=1.5)
        ax.add_patch(rect)
        ax.text(x+0.8, y+0.55, label, ha="center", va="center",
                fontsize=7.5, color="white", fontweight="bold")
        if i < len(steps)-1:
            ax.annotate("", xy=(x+1.68,y+0.55), xytext=(x+1.6,y+0.55),
                        arrowprops=dict(arrowstyle="->", color="#555", lw=1.5))

    # bottom labels
    labels_under = [
        (1.3, 2.9, "1. Collect tests"),
        (3.1, 2.9, "2. Setup browser"),
        (4.9, 2.9, "3. Open browser"),
        (6.7, 2.9, "4. Interact with UI"),
        (8.5, 2.9, "5. Assert"),
        (10.3,2.9, "6. Report"),
        (11.8,2.9, "7. Push results"),
    ]
    for (x,y,t) in labels_under:
        ax.text(x, y, t, ha="center", fontsize=6.5, color="#666")

    # sub-detail boxes
    details = [
        (1.3,  1.4, "Test Suites\ntest_login.py\ntest_dashboard.py\ntest_navigation.py"),
        (5.1,  1.4, "Locators (By.ID / By.XPATH)\nExplicit Wait 15s\nScreenshots on fail"),
        (9.3,  1.4, "PASS=Green\nFAIL=Red\nSKIP=Amber\nExcel + HTML"),
    ]
    for (x,y,t) in details:
        rect = FancyBboxPatch((x-0.8,y-0.1),2.2,1.2, boxstyle="round,pad=0.05",
                              facecolor="#EEF2F7", edgecolor="#AABBCC", linewidth=0.8)
        ax.add_patch(rect)
        ax.text(x+0.3, y+0.5, t, ha="center", va="center",
                fontsize=6.5, color="#333")

    plt.tight_layout(pad=0.3)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  [diagram] Saved test execution diagram → {out_path}")


# ─────────────────────────────────────────────────────────────────────────────
# WORD DOCUMENT BUILDER
# ─────────────────────────────────────────────────────────────────────────────

def set_cell_bg(cell, hex_color):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def add_heading(doc, text, level=1, color="1F4E79"):
    h = doc.add_heading(text, level=level)
    run = h.runs[0] if h.runs else h.add_run(text)
    run.font.color.rgb = RGBColor.from_string(color)
    h.paragraph_format.space_before = Pt(12)
    h.paragraph_format.space_after  = Pt(4)
    return h


def add_subheading(doc, text, color="2E75B6"):
    h = doc.add_heading(text, level=3)
    for run in h.runs:
        run.font.color.rgb = RGBColor.from_string(color)
    h.paragraph_format.space_before = Pt(8)
    return h


def add_body(doc, text):
    p = doc.add_paragraph(text)
    p.paragraph_format.space_after = Pt(4)
    for run in p.runs:
        run.font.size = Pt(10)
    return p


def add_code_block(doc, code, title=None):
    if title:
        p = doc.add_paragraph()
        run = p.add_run(f"  {title}")
        run.font.bold = True
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(0x53, 0x81, 0x35)
        p.paragraph_format.space_after = Pt(1)

    for line in code.strip().split("\n"):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.3)
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(line if line else " ")
        run.font.name = "Courier New"
        run.font.size = Pt(8)
        run.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
        # light grey background via shading
        pPr = p._p.get_or_add_pPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), "EEF2F7")
        pPr.append(shd)


def add_file_label(doc, filename, description):
    p = doc.add_paragraph()
    run = p.add_run(f"File: {filename}")
    run.font.bold = True
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0xC5, 0x5A, 0x11)
    p.add_run(f"  —  {description}").font.size = Pt(9)
    p.paragraph_format.space_after = Pt(2)


def add_screenshot(doc, path, caption, width=Inches(5.8)):
    if path and os.path.exists(path):
        doc.add_picture(path, width=width)
        last = doc.paragraphs[-1]
        last.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap = doc.add_paragraph(caption)
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap.runs[0].font.italic = True
        cap.runs[0].font.size = Pt(9)
        cap.runs[0].font.color.rgb = RGBColor(0x66, 0x66, 0x66)
    else:
        p = doc.add_paragraph(f"[Screenshot: {caption}]")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.runs[0].font.italic = True
        p.runs[0].font.color.rgb = RGBColor(0x99, 0x99, 0x99)


def add_info_table(doc, rows, headers=None):
    cols = len(rows[0])
    tbl = doc.add_table(rows=0, cols=cols)
    tbl.style = "Table Grid"
    tbl.alignment = WD_TABLE_ALIGNMENT.LEFT

    if headers:
        hrow = tbl.add_row()
        for i, h in enumerate(headers):
            cell = hrow.cells[i]
            cell.text = h
            cell.paragraphs[0].runs[0].font.bold = True
            cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            cell.paragraphs[0].runs[0].font.size = Pt(9)
            set_cell_bg(cell, "1F4E79")

    for j, row in enumerate(rows):
        trow = tbl.add_row()
        for i, val in enumerate(row):
            cell = trow.cells[i]
            cell.text = str(val)
            cell.paragraphs[0].runs[0].font.size = Pt(9)
            if j % 2 == 0:
                set_cell_bg(cell, "EEF4FB")
    return tbl


def add_step_table(doc, steps):
    """Numbered steps table: Step # | Action | Expected Result."""
    tbl = doc.add_table(rows=1, cols=3)
    tbl.style = "Table Grid"
    hdr = tbl.rows[0]
    for i, h in enumerate(["Step", "Action", "Expected Result"]):
        hdr.cells[i].text = h
        hdr.cells[i].paragraphs[0].runs[0].font.bold = True
        hdr.cells[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF,0xFF,0xFF)
        hdr.cells[i].paragraphs[0].runs[0].font.size = Pt(9)
        set_cell_bg(hdr.cells[i], "2E75B6")
    for i, (step, action, expected) in enumerate(steps):
        r = tbl.add_row()
        r.cells[0].text = str(step)
        r.cells[1].text = action
        r.cells[2].text = expected
        for c in r.cells:
            c.paragraphs[0].runs[0].font.size = Pt(9)
            if i % 2 == 0:
                set_cell_bg(c, "EEF4FB")
    return tbl


# ─────────────────────────────────────────────────────────────────────────────
# MAIN DOCUMENT BUILD
# ─────────────────────────────────────────────────────────────────────────────
def build_document():
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

    # ── generate diagrams ────────────────────────────────────────────────────
    arch_path  = os.path.join(SCREENSHOTS_DIR, "diag_architecture.png")
    mcp_path   = os.path.join(SCREENSHOTS_DIR, "diag_mcp_flow.png")
    exec_path  = os.path.join(SCREENSHOTS_DIR, "diag_test_execution.png")
    print("\nGenerating diagrams …")
    make_architecture_diagram(arch_path)
    make_mcp_flow_diagram(mcp_path)
    make_test_execution_diagram(exec_path)

    # ── create document ──────────────────────────────────────────────────────
    doc = Document()

    # page margins
    for section in doc.sections:
        section.top_margin    = Cm(2.0)
        section.bottom_margin = Cm(2.0)
        section.left_margin   = Cm(2.5)
        section.right_margin  = Cm(2.0)

    # default font
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(10)

    # ══════════════════════════════════════════════════════════════════════════
    # COVER PAGE
    # ══════════════════════════════════════════════════════════════════════════
    doc.add_paragraph()
    title = doc.add_heading("QA Automation Framework", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in title.runs:
        run.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
        run.font.size = Pt(28)

    sub = doc.add_paragraph("Lead Demo — Ultriva LMS (QALS1011)")
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.runs[0].font.size = Pt(16)
    sub.runs[0].font.color.rgb = RGBColor(0x2E, 0x75, 0xB6)

    doc.add_paragraph()
    meta = doc.add_paragraph(
        f"Prepared by: QA Engineer  |  Date: {datetime.now().strftime('%B %d, %Y')}\n"
        "Application: https://engineering.ultrivalms.com/qals1011\n"
        "Framework: Python · Selenium · Pytest · TestRail MCP · JIRA MCP"
    )
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in meta.runs:
        run.font.size = Pt(11)
        run.font.color.rgb = RGBColor(0x40, 0x40, 0x40)

    doc.add_page_break()

    # ══════════════════════════════════════════════════════════════════════════
    # TABLE OF CONTENTS
    # ══════════════════════════════════════════════════════════════════════════
    add_heading(doc, "Table of Contents", level=1)
    toc_items = [
        ("1", "Project Overview & Architecture", "3"),
        ("2", "Project Structure & Key Files", "4"),
        ("3", "Step-by-Step Test Execution Demo", "6"),
        ("4", "TestRail Integration with MCP Server", "9"),
        ("5", "JIRA Integration with MCP Server & Creating Subtasks", "12"),
        ("6", "Reports — Excel, HTML & Screenshots", "15"),
        ("7", "Summary & Key Benefits", "16"),
    ]
    for num, name, pg in toc_items:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        p.add_run(f"  {num}.  {name}").font.size = Pt(10)
        p.add_run(f"  ........................... {pg}").font.size = Pt(9)

    doc.add_page_break()

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 1 — PROJECT OVERVIEW
    # ══════════════════════════════════════════════════════════════════════════
    add_heading(doc, "1.  Project Overview & Architecture")
    add_body(doc,
        "This document demonstrates how an end-to-end QA Automation Framework has been built "
        "for the Ultriva Lean Management Suite (QALS1011). The framework covers automated "
        "browser testing with Selenium/Pytest, test case management through TestRail (via MCP), "
        "and defect tracking through JIRA (via MCP). All integrations are orchestrated through "
        "the VS Code Copilot Chat agent using the Model Context Protocol (MCP)."
    )

    add_subheading(doc, "1.1  Architecture Overview Diagram")
    add_screenshot(doc, arch_path,
                   "Fig 1.1 — QA Automation Architecture: Framework → MCP Servers → TestRail / JIRA / Browser",
                   width=Inches(6.0))
    doc.add_paragraph()

    add_subheading(doc, "1.2  Technology Stack")
    add_info_table(doc,
        rows=[
            ("Python 3.x",          "Core language for all automation scripts"),
            ("Selenium 4.18",        "Browser automation (Chrome / Firefox / Edge)"),
            ("Pytest 8.1",           "Test runner with fixtures, parametrize, HTML reports"),
            ("python-docx",          "Word document generation"),
            ("openpyxl",             "Excel test result reporter"),
            ("testrail-api",         "TestRail case & run management"),
            ("jira (python-jira)",   "JIRA issue creation, comments, transitions"),
            ("MCP (testrail.py)",    "Model Context Protocol server for TestRail"),
            ("Atlassian MCP (HTTP)", "Model Context Protocol server for JIRA"),
            ("Playwright MCP",       "@playwright/mcp — AI-driven browser screenshots"),
            ("VS Code Copilot",      "AI agent orchestrating all MCP tool calls"),
        ],
        headers=["Technology", "Purpose"],
    )
    doc.add_paragraph()
    doc.add_page_break()

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 2 — PROJECT STRUCTURE
    # ══════════════════════════════════════════════════════════════════════════
    add_heading(doc, "2.  Project Structure & Key Files")
    add_body(doc,
        "All automation code lives under the qa_automation/ folder. "
        "The Page Object Model (POM) pattern is used throughout so that locator "
        "changes only need to be updated in one place."
    )

    add_subheading(doc, "2.1  Folder Tree")
    add_code_block(doc, """\
qa_automation/
├── config/
│   └── config.py           ← Credentials, URLs, TestRail & JIRA settings
├── pages/
│   ├── base_page.py        ← Selenium helpers (wait, click, screenshot)
│   ├── login_page.py       ← Login page locators & actions
│   └── dashboard_page.py   ← Dashboard page object
├── tests/
│   ├── test_login.py       ← TC-001 – TC-007  (Authentication)
│   ├── test_dashboard.py   ← TC-101 – TC-107  (Dashboard UI)
│   └── test_navigation.py  ← TC-201 – TC-205  (Navigation)
├── utils/
│   ├── driver_setup.py     ← WebDriver factory (Chrome / Firefox / Edge)
│   ├── excel_reporter.py   ← Colour-coded Excel results (PASS/FAIL/SKIP)
│   ├── testrail_client.py  ← TestRail API wrapper
│   └── jira_client.py      ← JIRA API wrapper
├── JIRA Tickets/
│   ├── Bugs/               ← ULT-10069 bug scripts + test plans
│   └── Enhancements/       ← ULT-10425, ULT-10511 enhancement scripts
├── conftest.py             ← Pytest session fixtures & TestRail hook
├── pytest.ini              ← Pytest settings
└── requirements.txt        ← pip dependencies""",
        title="Directory: qa_automation/"
    )
    doc.add_paragraph()

    add_subheading(doc, "2.2  Key File: config/config.py")
    add_file_label(doc, "qa_automation/config/config.py",
                   "Central configuration — URLs, credentials, TestRail & JIRA settings")
    add_code_block(doc, """\
# Application
BASE_URL  = "https://engineering.ultrivalms.com/qals1011"
USERNAME  = "buyeruser"
PASSWORD  = "Ultriva!23"
BROWSER   = "chrome"        # chrome | firefox | edge
HEADLESS  = True

# TestRail
TESTRAIL_URL         = os.environ.get("TESTRAIL_URL", "https://upland.testrail.com/")
TESTRAIL_EMAIL       = os.environ.get("TESTRAIL_EMAIL", "vseelam@uplandsoftware.com")
TESTRAIL_API_KEY     = os.environ.get("TESTRAIL_API_KEY", "...")
TESTRAIL_PROJECT_ID  = 15
TESTRAIL_ENABLED     = True

# JIRA
JIRA_SERVER      = "https://uplandsoftware.atlassian.net"
JIRA_EMAIL       = "vseelam@uplandsoftware.com"
JIRA_API_TOKEN   = os.environ.get("ATLASSIAN_API_TOKEN", "")
JIRA_PROJECT_KEY = "ULT""",
        title="File: config/config.py — Core Settings"
    )
    doc.add_paragraph()

    add_subheading(doc, "2.3  Key File: pages/login_page.py")
    add_file_label(doc, "qa_automation/pages/login_page.py",
                   "Page Object for Login — locators, open(), login(), logout(), is_logged_in()")
    add_code_block(doc, """\
class LoginPage(BasePage):
    # Locators — verified against live DOM
    USERNAME_INPUT  = (By.ID,    "UserName")
    PASSWORD_INPUT  = (By.ID,    "Password")
    LOGIN_BUTTON    = (By.ID,    "login-button")
    ERROR_MESSAGE   = (By.ID,    "inner-alerts-container")
    LOGOUT_LINK     = (By.XPATH, "//a[contains(@href,'Account/Logout')]")

    def login(self, username, password):
        self.open()               # driver.get(LOGIN_URL)
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()
        self.wait_for_page_load()

    def is_logged_in(self):
        return (
            self.is_element_present(*self.LOGOUT_LINK, timeout=8)
            or self.is_element_present(*self.WELCOME_TEXT, timeout=8)
        )""",
        title="File: pages/login_page.py — Page Object Model"
    )
    doc.add_paragraph()

    add_subheading(doc, "2.4  Key File: utils/driver_setup.py")
    add_file_label(doc, "qa_automation/utils/driver_setup.py",
                   "WebDriver factory — supports Chrome, Firefox, Edge with Selenium Manager auto-download")
    add_code_block(doc, """\
def get_driver():
    browser = BROWSER.lower()
    if browser == "chrome":
        options = webdriver.ChromeOptions()
        if HEADLESS:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        driver = webdriver.Chrome(options=options)
    elif browser == "firefox":
        options = webdriver.FirefoxOptions()
        driver = webdriver.Firefox(options=options)
    elif browser == "edge":
        driver = webdriver.Edge(options=...)
    driver.implicitly_wait(IMPLICIT_WAIT)     # 10 s
    driver.set_page_load_timeout(30)
    driver.maximize_window()
    return driver""",
        title="File: utils/driver_setup.py — WebDriver Factory"
    )
    doc.add_paragraph()
    doc.add_page_break()

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 3 — STEP-BY-STEP TEST EXECUTION DEMO
    # ══════════════════════════════════════════════════════════════════════════
    add_heading(doc, "3.  Step-by-Step Test Execution Demo")
    add_body(doc,
        "Below is a full walkthrough of how automated tests run from command line to "
        "results. Screenshots of the live Ultriva application are captured at each key step."
    )

    add_subheading(doc, "3.1  Test Execution Flow Diagram")
    add_screenshot(doc, exec_path,
                   "Fig 3.1 — Test Execution Flow: pytest → fixtures → WebDriver → POM → App → Reports",
                   width=Inches(6.0))
    doc.add_paragraph()

    add_subheading(doc, "3.2  Step 1 — Install & Configure")
    add_step_table(doc, [
        (1, "Clone repo & activate venv\n  cd qa_automation\n  python -m venv .venv\n  .venv\\Scripts\\activate",
           "Virtual environment active (venv)"),
        (2, "Install dependencies\n  pip install -r requirements.txt",
           "Selenium 4.18, pytest, openpyxl, testrail-api, jira installed"),
        (3, "Edit config/config.py — set BASE_URL, USERNAME, PASSWORD,\n  TESTRAIL_URL, TESTRAIL_API_KEY, JIRA_API_TOKEN",
           "Config file updated. All credentials point to QALS1011"),
        (4, "Verify connectivity\n  python check_testrail.py",
           "TestRail project 15 listed; all API calls succeed"),
    ])
    doc.add_paragraph()

    add_subheading(doc, "3.3  Step 2 — Login Page (TC-001, TC-002)")
    add_body(doc,
        "The LoginPage object navigates to the BASE_URL, enters credentials "
        "and verifies successful authentication by checking for the logout link or dashboard element."
    )
    add_screenshot(doc, ss("demo_01_login_page.png"),
                   "Screenshot 3.3a — Ultriva LMS Login Page (QALS1011) — file: demo_01_login_page.png")
    doc.add_paragraph()

    add_file_label(doc, "qa_automation/tests/test_login.py",
                   "TC-001: Login page loads | TC-002: Valid login | TC-003–005: Invalid cases | TC-006: Logout")
    add_code_block(doc, """\
# tests/test_login.py  ——  TC-002  Valid login
def test_valid_login(self, driver, reporter):
    login_page = LoginPage(driver)
    login_page.login(USERNAME, PASSWORD)      # open → enter creds → click
    assert login_page.is_logged_in(), \\
        "Login failed — logout link / dashboard not found"
    reporter.add_result(
        test_id="TC-002", test_name="Valid login",
        module="Authentication", status="PASS",
        screenshot=login_page.take_screenshot("TC-002"),
    )""",
        title="File: tests/test_login.py — TC-002 Valid Login Test"
    )
    doc.add_paragraph()

    add_subheading(doc, "3.4  Step 3 — Dashboard After Login")
    add_screenshot(doc, ss("demo_02_after_login.png"),
                   "Screenshot 3.4a — Buyer Home Dashboard after successful login — file: demo_02_after_login.png")
    doc.add_paragraph()
    add_body(doc,
        "After login, the Dashboard tests (TC-101–TC-107) verify: navigation menu present, "
        "correct URL, page header visible, menu items populated, and footer visible."
    )

    add_subheading(doc, "3.5  Step 4 — Execute Full Test Suite")
    add_step_table(doc, [
        (1, "cd qa_automation", "Working directory set"),
        (2, "pytest tests/ -v --html=reports/report.html --self-contained-html",
           "All 17 tests executed; HTML report generated"),
        (3, "pytest tests/test_login.py -v  (run one module)",
           "7 login tests pass in ~35 seconds"),
        (4, "pytest tests/ --tb=short -q  (quiet mode)",
           "Summary: 17 passed, 0 failed in 2.5m"),
    ])
    doc.add_paragraph()

    add_subheading(doc, "3.6  Test Cases Table (Full)")
    add_info_table(doc,
        rows=[
            ("TC-001","Login page loads with input fields",      "Authentication"),
            ("TC-002","Valid login – buyeruser/Ultriva!23",      "Authentication"),
            ("TC-003","Login rejected — invalid username",       "Authentication"),
            ("TC-004","Login rejected — invalid password",       "Authentication"),
            ("TC-005","Login rejected — empty credentials",      "Authentication"),
            ("TC-006","Logout redirects to login page",          "Authentication"),
            ("TC-007","Login page non-empty browser title",      "Authentication"),
            ("TC-101","Dashboard loads after valid login",        "Dashboard"),
            ("TC-102","Navigation menu is present",              "Dashboard"),
            ("TC-103","URL changes after login",                 "Dashboard"),
            ("TC-104","Page header visible",                     "Dashboard"),
            ("TC-105","Menu items are populated",                "Dashboard"),
            ("TC-106","Footer is present",                       "Dashboard"),
            ("TC-107","Dashboard browser title non-empty",       "Dashboard"),
            ("TC-201","Browser back button does not crash",      "Navigation"),
            ("TC-202","Unauthenticated access → redirects",     "Navigation"),
            ("TC-203","Session persists after page refresh",     "Navigation"),
        ],
        headers=["Test ID","Test Case Name","Module"],
    )
    doc.add_paragraph()
    doc.add_page_break()

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 4 — TESTRAIL MCP
    # ══════════════════════════════════════════════════════════════════════════
    add_heading(doc, "4.  TestRail Integration with MCP Server")
    add_body(doc,
        "TestRail test cases and runs are managed automatically through a Model Context "
        "Protocol (MCP) server. VS Code Copilot Chat triggers the MCP tools to create, "
        "update and fetch test cases — all without leaving the IDE."
    )

    add_subheading(doc, "4.1  MCP Flow Diagram")
    add_screenshot(doc, mcp_path,
                   "Fig 4.1 — TestRail & JIRA MCP Flow: VS Code Copilot → MCP Server → API → Result",
                   width=Inches(6.0))
    doc.add_paragraph()

    add_subheading(doc, "4.2  mcp.json — TestRail Server Configuration")
    add_file_label(doc, ".vscode/mcp.json",
                   "MCP server definitions — testrail entry launches testrail.py as stdio server")
    add_code_block(doc, """\
// .vscode/mcp.json  — TestRail MCP Server entry
"testrail": {
    "command": "C:/Users/.../python.exe",
    "args":    ["C:/genai-training/Labs/Lab5/testrail.py"],
    "env": {
        "TESTRAIL_URL":      "https://genai.testrail.io",
        "TESTRAIL_EMAIL":    "user@example.com",
        "TESTRAIL_API_KEY":  "your_api_key_here"
    },
    "type": "stdio"
}""",
        title="File: .vscode/mcp.json — TestRail MCP Server Entry"
    )
    doc.add_paragraph()
    add_body(doc,
        "How it works:  When VS Code starts, it reads mcp.json and launches testrail.py "
        "as a child process. Copilot Chat can then call TestRail tools directly in the chat "
        "with natural language — e.g. 'Create a test case for TC-002 in project 15'."
    )

    add_subheading(doc, "4.3  utils/testrail_client.py — API Wrapper")
    add_file_label(doc, "qa_automation/utils/testrail_client.py",
                   "Wraps testrail-api library; provides get_case(), add_result(), push_results(), close_run()")
    add_code_block(doc, """\
# utils/testrail_client.py
from testrail_api import TestRailAPI
from config.config import TESTRAIL_URL, TESTRAIL_EMAIL, TESTRAIL_API_KEY

class TestRailClient:
    def __init__(self):
        self._client = TestRailAPI(TESTRAIL_URL, TESTRAIL_EMAIL, TESTRAIL_API_KEY)

    def get_or_create_run(self) -> int:
        # Creates a new Test Run in TestRail for this session
        name = TESTRAIL_RUN_NAME.replace("{date}", datetime.now().strftime("%Y-%m-%d %H:%M"))
        run = self._client.runs.add_run(
            project_id=TESTRAIL_PROJECT_ID,
            name=name,
            suite_id=TESTRAIL_SUITE_ID,
        )
        return run["id"]

    def add_result(self, run_id, case_id, status, comment=""):
        self._client.results.add_result_for_case(
            run_id=run_id, case_id=case_id,
            status_id=STATUS_MAP[status],
            comment=comment,
        )""",
        title="File: utils/testrail_client.py — Core Methods"
    )
    doc.add_paragraph()

    add_subheading(doc, "4.4  JIRA Ticket Scripts — TestRail Case Creation")
    add_file_label(doc, "qa_automation/JIRA Tickets/Bugs/ULT-10069_add_testrail_case.py",
                   "Fetches reference case C13569701, creates/updates C17520015 for bug ULT-10069")
    add_code_block(doc, """\
# JIRA Tickets/Bugs/ULT-10069_add_testrail_case.py
from utils.testrail_client import TestRailClient

SECTION_ID  = 372888     # Suite S2571 (Admin) → Kanban Loop Design
REF_CASE_ID = 13569701   # C13569701 — reference case

tr = TestRailClient()
ref = tr.get_case(case_id=REF_CASE_ID)      # fetch reference steps

updated = tr.update_case(
    case_id=17520015,
    custom_steps    = ref["custom_steps"],
    custom_expected = ref["custom_expected"],
)
print(f"Updated: C{updated['id']} — {updated['title']}")""",
        title="File: JIRA Tickets/Bugs/ULT-10069_add_testrail_case.py"
    )
    doc.add_paragraph()

    add_subheading(doc, "4.5  TestRail MCP — Step-by-Step Demo Steps")
    add_step_table(doc, [
        (1, "Open VS Code → Copilot Chat panel",
           "MCP servers auto-start (testrail.py process visible in background)"),
        (2, "Type: '@testrail Get project info for project 15'",
           "MCP tool: get_project → returns Project Name, ID, Suite count"),
        (3, "Type: '@testrail List test cases for suite S2571'",
           "MCP returns list of all cases: C-IDs, titles, priorities"),
        (4, "Type: '@testrail Create a test case for ULT-10069 in section 372888'",
           "New test case created; Copilot returns Case ID (e.g. C17520015)"),
        (5, "Run: python check_testrail.py",
           "Verifies connection and prints project info + case C5242647 details"),
        (6, "Run: pytest tests/ (with TESTRAIL_ENABLED=True)",
           "Each TC result auto-pushed to TestRail run; run closed at end of session"),
    ])
    doc.add_paragraph()

    add_subheading(doc, "4.6  check_testrail.py — Quick Verification Script")
    add_file_label(doc, "qa_automation/check_testrail.py",
                   "Quick script to verify TestRail connection and fetch case C5242647")
    add_code_block(doc, """\
# check_testrail.py
from utils.testrail_client import TestRailClient

tr = TestRailClient()
project = tr.get_project()          # [1] Project info
print(f"Name: {project['name']}")

case = tr.get_case(case_id=5242647) # [2] Specific case
print(f"Case: C{case['id']} — {case['title']}")

runs = tr.get_runs()                # [3] Recent runs
for r in runs[:3]:
    print(f"Run {r['id']}: {r['name']} — {r['passed_count']} passed")""",
        title="File: qa_automation/check_testrail.py — Verification Script"
    )
    doc.add_paragraph()
    doc.add_page_break()

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 5 — JIRA MCP
    # ══════════════════════════════════════════════════════════════════════════
    add_heading(doc, "5.  JIRA Integration with MCP Server & Creating Subtasks")
    add_body(doc,
        "JIRA is integrated through the Atlassian MCP HTTP server. VS Code Copilot Chat "
        "can list tickets, get issue details, create subtasks, add comments, and transition "
        "issues — directly from the chat panel using natural language commands."
    )

    add_subheading(doc, "5.1  mcp.json — Atlassian MCP Server Configuration")
    add_file_label(doc, ".vscode/mcp.json",
                   "Atlassian MCP entry — HTTP server with Bearer token auth; supports JIRA + Confluence")
    add_code_block(doc, """\
// .vscode/mcp.json  — Atlassian MCP Server
"com.atlassian/atlassian-mcp-server": {
    "type":    "http",
    "url":     "https://mcp.atlassian.com/v1/mcp",
    "headers": {
        "Authorization": "Bearer ${input:ATLASSIAN_API_TOKEN}"
    }
}

// inputs section — prompts for token securely
"inputs": [
    {
        "id":          "ATLASSIAN_API_TOKEN",
        "type":        "promptString",
        "description": "Atlassian API Token (from id.atlassian.com)",
        "password":    true
    }
]""",
        title="File: .vscode/mcp.json — Atlassian MCP (JIRA) Configuration"
    )
    doc.add_paragraph()

    add_subheading(doc, "5.2  utils/jira_client.py — Python JIRA Wrapper")
    add_file_label(doc, "qa_automation/utils/jira_client.py",
                   "Wraps python-jira library; connect(), search(), get_issue(), create_bug(), create_subtask()")
    add_code_block(doc, """\
# utils/jira_client.py
from jira import JIRA
from config.config import JIRA_SERVER, JIRA_EMAIL, JIRA_API_TOKEN

class JiraClient:
    def __init__(self):
        self._client = JIRA(
            server=JIRA_SERVER,
            basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN),
        )

    def get_issue(self, key):
        return self._client.issue(key)

    def create_bug(self, summary, description, labels=None):
        issue_dict = {
            "project":     {"key": self.project_key},
            "summary":     summary,
            "description": description,
            "issuetype":   {"name": "Bug"},
            "labels":      labels or [],
        }
        issue = self._client.create_issue(fields=issue_dict)
        return issue.key

    def create_subtask(self, parent_key, summary, description):
        parent = self.get_issue(parent_key)
        issue_dict = {
            "project":      {"key": self.project_key},
            "summary":      summary,
            "description":  description,
            "issuetype":    {"name": "Sub-task"},
            "parent":       {"id": parent.id},
        }
        subtask = self._client.create_issue(fields=issue_dict)
        return subtask.key

    def add_comment(self, issue_key, body):
        self._client.add_comment(issue_key, body)

    def transition_issue(self, issue_key, transition_name):
        transitions = self._client.transitions(issue_key)
        for t in transitions:
            if t["name"].lower() == transition_name.lower():
                self._client.transition_issue(issue_key, t["id"])
                return t["name"]""",
        title="File: utils/jira_client.py — Full JIRA Client"
    )
    doc.add_paragraph()

    add_subheading(doc, "5.3  JIRA Tickets — Bug ULT-10069")
    add_file_label(doc, "qa_automation/JIRA Tickets/Bugs/ULT-10069_test_plan.md",
                   "Bug: Kanban Loop Design not processing when HTTP exchange type is set")
    add_info_table(doc,
        rows=[
            ("ULT-10069", "Kanban Loop Design Not Processing", "Bug", "Critical", "In QA Review", "Sherif Hamdy"),
            ("TS-01",     "KLD processes after Item Data Load sets HTTP exchange type", "Scenario", "Critical", "–", "–"),
            ("TS-02",     "Batch job transitions Created → InProgress → Completed",    "Scenario", "Critical", "–", "–"),
            ("TS-03",     "Item Data Load continues to work — no regression",           "Scenario", "High",     "–", "–"),
            ("TS-04",     "KLD processes when exchange type is HTTPS",                 "Scenario", "High",     "–", "–"),
        ],
        headers=["Ticket / ID", "Summary", "Type", "Priority", "Status", "Assignee"],
    )
    doc.add_paragraph()

    add_subheading(doc, "5.4  JIRA Tickets — Enhancement ULT-10425")
    add_file_label(doc, "qa_automation/JIRA Tickets/Enhancements/ULT-10425_test_plan.md",
                   "Enhancement: Plant Home Page Integration Panel — remember last BU filter & label rename")
    add_info_table(doc,
        rows=[
            ("ULT-10425", "Plant Home Page: Remember Last BU Filter Choice",       "Enhancement","Critical","In QA Review","Sherif Hamdy"),
            ("TC-01",     "Label reads 'Plant and Associated Workcenters'",         "Test Case",  "Critical","–","–"),
            ("TC-02",     "'Only this BU' option still present after rename",       "Test Case",  "Critical","–","–"),
            ("TC-03",     "'Plant and Associated Workcenters' persists after nav",  "Test Case",  "High",    "–","–"),
            ("TC-04",     "Default filter = 'Only this BU' for first-time user",   "Test Case",  "High",    "–","–"),
        ],
        headers=["Ticket / ID","Summary","Type","Priority","Status","Assignee"],
    )
    doc.add_paragraph()

    add_subheading(doc, "5.5  Creating Subtasks via MCP — Step-by-Step")
    add_step_table(doc, [
        (1, "Open VS Code → Copilot Chat\nEnsure ATLASSIAN_API_TOKEN environment variable is set",
           "Atlassian MCP server authenticates to uplandsoftware.atlassian.net"),
        (2, "Type: 'List open issues in project ULT assigned to me'",
           "MCP tool: searchJiraIssuesUsingJql returns ticket list with keys, titles, status"),
        (3, "Type: 'Get details for ULT-10069'",
           "MCP returns: summary, description, status (In QA Review), assignee, components"),
        (4, "Type: 'Create a subtask under ULT-10069 for writing automated test cases'",
           "MCP tool: createJiraIssue with issuetype=Sub-task, parent=ULT-10069"),
        (5, "Type: 'Add comment to ULT-10069: Test cases created in TestRail Suite S2571'",
           "MCP tool: addCommentToJiraIssue — comment appears in JIRA ticket"),
        (6, "Type: 'Transition ULT-10069 to In Progress'",
           "MCP tool: transitionJiraIssue — ticket status changes to In Progress"),
        (7, "Run: python jira_client.py (standalone verification)",
           "Console prints connected JIRA server + sample issue key"),
    ])
    doc.add_paragraph()

    add_subheading(doc, "5.6  JIRA Test Case Script — ULT-10425")
    add_file_label(doc, "qa_automation/JIRA Tickets/Enhancements/ULT-10425_test_cases.py",
                   "Automated Selenium test cases for the Integration Panel filter feature")
    add_code_block(doc, """\
# JIRA Tickets/Enhancements/ULT-10425_test_cases.py
class TestIntegrationPanelFilterLabel:

    # TC-01: Verify label renamed
    def test_label_renamed_to_plant_and_associated_workcenters(self, driver):
        LoginPage(driver).login(USERNAME, PASSWORD)
        driver.get(PLANT_HOME_URL)
        elements = driver.find_elements("xpath", FILTER_WORKCENTERS)
        assert elements, "Label 'Plant and Associated Workcenters' NOT found!"
        old = driver.find_elements("xpath", OLD_LABEL_CHECK)
        assert not old, "Old label 'All Business Units' still present!"

    # TC-03: Verify persistence after navigation
    def test_filter_persists_after_navigation(self, driver):
        LoginPage(driver).login(USERNAME, PASSWORD)
        driver.get(PLANT_HOME_URL)
        select_filter(driver, FILTER_WORKCENTERS)
        driver.refresh()
        active = selected_filter_text(driver)
        assert "Plant and Associated Workcenters" in active, \\
            f"Filter not persisted, got: {active!r}" """,
        title="File: JIRA Tickets/Enhancements/ULT-10425_test_cases.py"
    )
    doc.add_paragraph()
    doc.add_page_break()

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 6 — REPORTS
    # ══════════════════════════════════════════════════════════════════════════
    add_heading(doc, "6.  Reports — Excel, HTML & Screenshots")

    add_subheading(doc, "6.1  Excel Report (utils/excel_reporter.py)")
    add_file_label(doc, "qa_automation/utils/excel_reporter.py",
                   "Generates colour-coded Excel report: PASS=Green, FAIL=Red, SKIP=Amber")
    add_code_block(doc, """\
# utils/excel_reporter.py  — ExcelReporter class
PASS_COLOR   = "92D050"   # Green
FAIL_COLOR   = "FF0000"   # Red
SKIP_COLOR   = "FFC000"   # Amber
HEADER_COLOR = "1F4E79"   # Dark blue

# Columns: Test ID | Test Case | Module | Status | Duration | Timestamp | Error | Screenshot
reporter.add_result(
    test_id="TC-002", test_name="Valid login",
    module="Authentication", status="PASS",
    duration=1.23, error_msg="", screenshot="reports/screenshots/TC-002.png",
)
# Output: reports/test_results.xlsx""",
        title="File: utils/excel_reporter.py — Excel Report Generator"
    )
    doc.add_paragraph()

    add_subheading(doc, "6.2  HTML Report (pytest-html)")
    add_body(doc,
        "The HTML report is generated by pytest-html automatically after each run. "
        "It includes: pass/fail totals, test duration, error tracebacks, and embedded screenshots. "
        "Open: qa_automation/reports/report.html in any browser."
    )

    add_subheading(doc, "6.3  Screenshots")
    add_body(doc,
        "Every test calls take_screenshot(test_id) on pass and fail. Screenshots are saved "
        "under reports/screenshots/ with the test ID as filename (e.g. TC-002.png). "
        "Failed tests append '_fail' (e.g. TC-003_fail.png)."
    )

    add_info_table(doc,
        rows=[
            ("reports/report.html",                 "pytest-html HTML report (self-contained)"),
            ("reports/test_results.xlsx",           "Colour-coded Excel workbook with all results"),
            ("reports/screenshots/TC-001.png",      "Screenshot on each test (pass & fail)"),
            ("reports/screenshots/TC-002.png",      "TC-002 valid login pass screenshot"),
            ("reports/screenshots/demo_01_login_page.png",
             "Playwright screenshot – Login Page (used in this document)"),
            ("reports/screenshots/demo_02_after_login.png",
             "Playwright screenshot – Dashboard after login"),
            ("reports/screenshots/diag_architecture.png", "Architecture diagram (generated)"),
            ("reports/screenshots/diag_mcp_flow.png",     "MCP flow diagram (generated)"),
            ("reports/screenshots/diag_test_execution.png","Test execution flow diagram (generated)"),
        ],
        headers=["File / Path", "Description"],
    )
    doc.add_paragraph()
    doc.add_page_break()

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 7 — SUMMARY
    # ══════════════════════════════════════════════════════════════════════════
    add_heading(doc, "7.  Summary & Key Benefits")

    add_subheading(doc, "7.1  What Was Demonstrated")
    add_info_table(doc,
        rows=[
            ("Automation Framework",
             "Python + Selenium + Pytest with Page Object Model covering 17 test cases "
             "across Authentication, Dashboard, and Navigation modules"),
            ("MCP — TestRail",
             "testrail.py MCP server launched from mcp.json; Copilot Chat creates/updates "
             "test cases, creates runs, and pushes pass/fail results automatically"),
            ("MCP — JIRA",
             "Atlassian HTTP MCP server integrated via Bearer token; Copilot Chat lists "
             "open tickets, reads issue details, creates subtasks, adds comments, transitions"),
            ("MCP — Playwright",
             "@playwright/mcp server used live to navigate the app, login, and capture "
             "screenshots directly in the demo document"),
            ("Reports",
             "Colour-coded Excel + pytest-html + per-test PNG screenshots "
             "— all generated automatically on each test run"),
            ("AI Acceleration",
             "VS Code Copilot Chat with MCP eliminated context switching: "
             "all test management tasks done inside the IDE in natural language"),
        ],
        headers=["Area", "Details"],
    )
    doc.add_paragraph()

    add_subheading(doc, "7.2  File Summary Reference")
    add_info_table(doc,
        rows=[
            ("config/config.py",                        "All credentials, URLs, TestRail & JIRA settings"),
            ("pages/base_page.py",                      "Selenium helpers — wait, click, screenshot, type"),
            ("pages/login_page.py",                     "Login Page Object — locators & login/logout methods"),
            ("pages/dashboard_page.py",                 "Dashboard Page Object"),
            ("tests/test_login.py",                     "TC-001 – TC-007  Authentication tests"),
            ("tests/test_dashboard.py",                 "TC-101 – TC-107  Dashboard tests"),
            ("tests/test_navigation.py",                "TC-201 – TC-205  Navigation tests"),
            ("utils/driver_setup.py",                   "WebDriver factory for Chrome/Firefox/Edge"),
            ("utils/excel_reporter.py",                 "Colour-coded Excel test report"),
            ("utils/testrail_client.py",                "TestRail API wrapper (get/create/push)"),
            ("utils/jira_client.py",                    "JIRA API wrapper (search/create/subtask)"),
            ("conftest.py",                             "Pytest fixtures, session setup & TestRail hook"),
            ("check_testrail.py",                       "Quick TestRail connectivity verification"),
            ("JIRA Tickets/Bugs/ULT-10069_test_plan.md","Bug test plan — Kanban Loop Design"),
            ("JIRA Tickets/Bugs/ULT-10069_add_testrail_case.py","Creates/updates TestRail case C17520015"),
            ("JIRA Tickets/Enhancements/ULT-10425_test_plan.md","Enhancement test plan — BU Filter"),
            ("JIRA Tickets/Enhancements/ULT-10425_test_cases.py","Selenium tests for BU filter feature"),
            (".vscode/mcp.json",                        "MCP server definitions (testrail, atlassian, playwright)"),
        ],
        headers=["File", "Purpose"],
    )
    doc.add_paragraph()

    # footer note
    p = doc.add_paragraph(
        f"\n\nGenerated automatically on {datetime.now().strftime('%B %d, %Y at %H:%M')}  |  "
        "QA Automation Framework — Ultriva LMS QALS1011"
    )
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.runs[0].font.size = Pt(8)
    p.runs[0].font.color.rgb = RGBColor(0x88, 0x88, 0x88)

    # ── save ─────────────────────────────────────────────────────────────────
    doc.save(OUTPUT_DOC)
    print(f"\n✓ Document saved → {OUTPUT_DOC}")
    return OUTPUT_DOC


if __name__ == "__main__":
    build_document()
