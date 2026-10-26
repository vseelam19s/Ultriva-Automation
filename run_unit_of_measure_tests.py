"""
run_unit_of_measure_tests.py – Standalone runner for Unit Of Measure test suite.

Runs test cases:
    TC-UOM-01  Add  Unit Of Measure
    TC-UOM-02  Edit Unit Of Measure
    TC-UOM-03  View Unit Of Measure

QA Site:
    https://engineering.ultrivalms.com/QALS1011

Usage (from workspace root  c:\\Prcatices-AI):
    python -m qa_automation.run_unit_of_measure_tests

Usage (from qa_automation folder):
    python run_unit_of_measure_tests.py
"""

import sys
import os

# Ensure qa_automation is on the path when run directly from the workspace root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from selenium.webdriver.support.ui import WebDriverWait
from utils.driver_setup import get_driver
from admin.Entities.UnitOfMeasure import (
    add_unit_of_measure,
    edit_unit_of_measure,
    view_unit_of_measure,
)


def run_unit_of_measure_tests():
    """Instantiate WebDriver, run all three Unit Of Measure tests, print summary."""
    driver = get_driver()
    wait   = WebDriverWait(driver, 20)

    suite = [
        ("TC-UOM-01  Add  Unit Of Measure", add_unit_of_measure),
        ("TC-UOM-02  Edit Unit Of Measure", edit_unit_of_measure),
        ("TC-UOM-03  View Unit Of Measure", view_unit_of_measure),
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

    # ── Final Summary ─────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  UNIT OF MEASURE TESTS – FINAL SUMMARY")
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
    run_unit_of_measure_tests()
