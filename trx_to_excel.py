"""
Parse the C# Selenium TRX results and produce reports/test_results.xlsx
using the existing ExcelReporter.
"""
import sys
import os
import xml.etree.ElementTree as ET

# Ensure we can import from the qa_automation package
sys.path.insert(0, os.path.dirname(__file__))

from utils.excel_reporter import ExcelReporter

TRX_PATH = os.path.join(
    os.path.dirname(__file__),
    "ultriva_selenium_csharp", "TestResults", "TestResults.trx"
)
EXCEL_PATH = os.path.join(os.path.dirname(__file__), "reports", "test_results.xlsx")

NS = {"ms": "http://microsoft.com/schemas/VisualStudio/TeamTest/2010"}


def parse_duration(duration_str):
    """Convert HH:MM:SS.ffffff to total seconds."""
    try:
        parts = duration_str.split(":")
        hours   = int(parts[0])
        minutes = int(parts[1])
        seconds = float(parts[2])
        return hours * 3600 + minutes * 60 + seconds
    except Exception:
        return 0.0


def extract_screenshot(stdout_text):
    """Pull the screenshot path out of the test stdout."""
    if not stdout_text:
        return ""
    for line in stdout_text.splitlines():
        if "Screenshot saved:" in line:
            return line.replace("Screenshot saved:", "").strip()
    return ""


def main():
    if not os.path.exists(TRX_PATH):
        print(f"ERROR: TRX file not found at {TRX_PATH}")
        sys.exit(1)

    tree = ET.parse(TRX_PATH)
    root = tree.getroot()

    # ── Run-level metadata ────────────────────────────────────────────────────
    times_el = root.find("ms:Times", NS)
    run_start = (times_el.get("start", "") if times_el is not None else "")[:19].replace("T", " ")

    # ── Parse each UnitTestResult ─────────────────────────────────────────────
    reporter = ExcelReporter(path=EXCEL_PATH)

    # Update the summary sheet meta with actual run date
    ws = reporter.summary_ws
    ws.cell(row=4, column=2, value=run_start)   # Run Date row

    results = root.findall("ms:Results/ms:UnitTestResult", NS)

    # Map testId → class name from TestDefinitions
    class_map = {}
    for ut in root.findall("ms:TestDefinitions/ms:UnitTest", NS):
        tid = ut.get("id", "")
        tm  = ut.find("ms:TestMethod", NS)
        class_map[tid] = tm.get("className", "Tests") if tm is not None else "Tests"

    for idx, result in enumerate(results, start=1):
        test_id   = f"TC_{idx:03d}"
        test_name = result.get("testName", "")
        outcome   = result.get("outcome", "").upper()
        duration  = parse_duration(result.get("duration", "0"))
        tid       = result.get("testId", "")
        module    = class_map.get(tid, "ultriva_selenium_csharp.Tests")

        # Map outcome to PASS/FAIL/SKIP
        status_map = {"PASSED": "PASS", "FAILED": "FAIL", "NOTEXECUTED": "SKIP"}
        status = status_map.get(outcome, outcome)

        # Error message (for failed tests)
        error_msg = ""
        err_el = result.find(".//ms:ErrorInfo/ms:Message", NS)
        if err_el is not None and err_el.text:
            error_msg = err_el.text.strip()

        # Screenshot from stdout
        stdout_el = result.find(".//ms:StdOut", NS)
        screenshot = extract_screenshot(stdout_el.text if stdout_el is not None else "")

        reporter.add_result(
            test_id   = test_id,
            test_name = test_name,
            module    = module,
            status    = status,
            duration  = duration,
            error_msg = error_msg,
            screenshot= screenshot,
        )

    path = reporter.save()
    print(f"Excel report saved: {os.path.abspath(path)}")
    return path


if __name__ == "__main__":
    saved = main()
    # Open the file in Excel
    os.startfile(os.path.abspath(saved))
