"""
run_printer_tests.py – Standalone runner for the Printer test suite.

Runs test cases:
    TC-PR-01  Add  Printer
    TC-PR-02  Edit Printer
    TC-PR-03  View Printer

QA Site:
    https://engineering.ultrivalms.com/QALS1011

Usage (from qa_automation folder):
    python run_printer_tests.py

Usage (from workspace root  c:\\Prcatices-AI):
    python -m qa_automation.run_printer_tests
"""

import sys
import os

# Ensure qa_automation is on the path when run directly from the workspace root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from selenium.webdriver.support.ui import WebDriverWait
from utils.driver_setup import get_driver
from qa_automation.tests.QALS11.Admin.Entities.test_Printer import (
    add_printer,
    edit_printer,
    view_printer,
)


def run_printer_tests():
    """Instantiate WebDriver, run all three Printer tests, print summary."""
    driver = get_driver()
    wait   = WebDriverWait(driver, 20)

    suite = [
        ("TC-PR-01  Add  Printer", add_printer),
        ("TC-PR-02  Edit Printer", edit_printer),
        ("TC-PR-03  View Printer", view_printer),
    ]

    results = {}
    for name, fn in suite:
        print(f"\n{'─' * 55}")
        print(f"  Running: {name}")
        print(f"{'─' * 55}")
        try:
            results[name] = fn(driver, wait)
        except Exception as exc:
            print(f"  [ERROR] {name}: {exc}")
            results[name] = False

    driver.quit()

    # ── Final Summary ──────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  PRINTER TESTS – FINAL SUMMARY")
    print("=" * 70)
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}]  {name}")
    print("=" * 70)
    total  = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    print(f"  Total: {total} | Passed: {passed} | Failed: {failed}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_printer_tests()
