import os
import time
from openpyxl import Workbook, load_workbook
from openpyxl.styles import (
    Font, PatternFill, Alignment, Border, Side
)
from openpyxl.utils import get_column_letter
from config.config import EXCEL_REPORT_PATH


# ── Color palette ────────────────────────────────────────────────────────────
PASS_COLOR   = "92D050"   # green
FAIL_COLOR   = "FF0000"   # red
SKIP_COLOR   = "FFC000"   # amber
HEADER_COLOR = "1F4E79"   # dark blue
ROW_ALT      = "D6E4F0"   # light blue (alternating rows)

thin = Side(style="thin")
border = Border(left=thin, right=thin, top=thin, bottom=thin)


def _header_font():
    return Font(bold=True, color="FFFFFF", size=11, name="Calibri")


def _cell_font():
    return Font(size=10, name="Calibri")


def _fill(hex_color):
    return PatternFill(start_color=hex_color, end_color=hex_color, fill_type="solid")


def _center():
    return Alignment(horizontal="center", vertical="center", wrap_text=True)


def _left():
    return Alignment(horizontal="left", vertical="center", wrap_text=True)


class ExcelReporter:
    """Writes test results to an Excel workbook."""

    COLUMNS = [
        ("Test ID",       12),
        ("Test Case",     40),
        ("Module",        20),
        ("Status",        10),
        ("Duration (s)",  14),
        ("Timestamp",     22),
        ("Error Message", 60),
        ("Screenshot",    50),
    ]

    def __init__(self, path=None):
        self.path = path or EXCEL_REPORT_PATH
        os.makedirs(os.path.dirname(self.path) if os.path.dirname(self.path) else ".", exist_ok=True)
        self.wb = Workbook()
        self._build_results_sheet()
        self._build_summary_sheet()
        self.row = 2          # current data row in Results sheet
        self.test_counter = 0
        self.stats = {"PASS": 0, "FAIL": 0, "SKIP": 0}

    # ── Sheet builders ────────────────────────────────────────────────────────

    def _build_results_sheet(self):
        ws = self.wb.active
        ws.title = "Test Results"
        ws.freeze_panes = "A2"

        for col_idx, (header, width) in enumerate(self.COLUMNS, start=1):
            cell = ws.cell(row=1, column=col_idx, value=header)
            cell.font      = _header_font()
            cell.fill      = _fill(HEADER_COLOR)
            cell.alignment = _center()
            cell.border    = border
            ws.column_dimensions[get_column_letter(col_idx)].width = width

        ws.row_dimensions[1].height = 22
        self.results_ws = ws

    def _build_summary_sheet(self):
        ws = self.wb.create_sheet("Summary", 0)
        ws.column_dimensions["A"].width = 25
        ws.column_dimensions["B"].width = 20

        title = ws.cell(row=1, column=1, value="QA Automation Test Report")
        title.font      = Font(bold=True, size=14, color="1F4E79", name="Calibri")
        title.alignment = _center()
        ws.merge_cells("A1:B1")
        ws.row_dimensions[1].height = 28

        meta = [
            ("URL",        "https://engineering.ultrivalms.com/qals1011"),
            ("User",       "buyeruser"),
            ("Run Date",   time.strftime("%Y-%m-%d %H:%M:%S")),
            ("Total",      "=SUM(B8:B10)"),
            ("",           ""),
            ("Passed",     0),
            ("Failed",     0),
            ("Skipped",    0),
        ]
        for i, (k, v) in enumerate(meta, start=2):
            ws.cell(row=i, column=1, value=k).font  = Font(bold=True, name="Calibri")
            ws.cell(row=i, column=2, value=v).font  = Font(name="Calibri")

        self.summary_ws = ws
        self._summary_rows = {
            "total":   5,
            "passed":  8,
            "failed":  9,
            "skipped": 10,
        }

    # ── Public API ────────────────────────────────────────────────────────────

    def add_result(self, test_id, test_name, module, status,
                   duration=0.0, error_msg="", screenshot=""):
        """Append one test result row."""
        self.test_counter += 1
        status = status.upper()
        self.stats[status] = self.stats.get(status, 0) + 1

        color = {"PASS": PASS_COLOR, "FAIL": FAIL_COLOR, "SKIP": SKIP_COLOR}.get(status, "FFFFFF")
        row_fill = _fill(ROW_ALT) if self.row % 2 == 0 else _fill("FFFFFF")

        values = [
            test_id or f"TC_{self.test_counter:03d}",
            test_name,
            module,
            status,
            round(duration, 2),
            time.strftime("%Y-%m-%d %H:%M:%S"),
            error_msg[:500] if error_msg else "",
            screenshot,
        ]

        ws = self.results_ws
        for col_idx, value in enumerate(values, start=1):
            cell = ws.cell(row=self.row, column=col_idx, value=value)
            cell.font      = _cell_font()
            cell.alignment = _center() if col_idx in (1, 4, 5, 6) else _left()
            cell.border    = border
            cell.fill      = row_fill

            # Colour the Status cell
            if col_idx == 4:
                cell.fill = _fill(color)
                cell.font = Font(bold=True, size=10, name="Calibri",
                                 color="FFFFFF" if status in ("PASS", "FAIL") else "000000")

        ws.row_dimensions[self.row].height = 18
        self.row += 1

    def save(self):
        """Update summary counters and save workbook."""
        ws = self.summary_ws
        r = self._summary_rows
        ws.cell(row=r["passed"],  column=2, value=self.stats.get("PASS", 0))
        ws.cell(row=r["failed"],  column=2, value=self.stats.get("FAIL", 0))
        ws.cell(row=r["skipped"], column=2, value=self.stats.get("SKIP", 0))
        ws.cell(row=r["total"],   column=2, value=sum(self.stats.values()))

        # Colour the summary counts
        ws.cell(row=r["passed"],  column=2).fill = _fill(PASS_COLOR)
        ws.cell(row=r["failed"],  column=2).fill = _fill(FAIL_COLOR)
        ws.cell(row=r["skipped"], column=2).fill = _fill(SKIP_COLOR)

        self.wb.save(self.path)
        return self.path
