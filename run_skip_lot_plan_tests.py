"""
run_skip_lot_plan_tests.py – Standalone runner for the Skip Lot Plan test suite.

Runs test cases:
    TC-SLP-01  Add  Skip Lot Plan
    TC-SLP-02  Edit Skip Lot Plan
    TC-SLP-03  View Skip Lot Plan

QA Site:
    https://engineering.ultrivalms.com/QALS1011

Navigation Path:
    Admin > Entities (left nav tab) > Skip Lot Plan

Usage (from qa_automation folder):
    python run_skip_lot_plan_tests.py

Usage (from workspace root  c:\\Prcatices-AI):
    python -m qa_automation.run_skip_lot_plan_tests

Reference pattern: run_break_reason_code_tests.py / run_printer_tests.py
"""

import sys
import os

# Ensure qa_automation is on the path when run directly from the workspace root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from selenium.webdriver.support.ui import WebDriverWait
from utils.driver_setup import get_driver
from admin.Entities.SkipLotPlan import (
    add_skip_lot_plan,
    edit_skip_lot_plan,
    view_skip_lot_plan,
)


def run_skip_lot_plan_tests():
    """Instantiate WebDriver, run all three Skip Lot Plan tests, print summary."""
    driver = get_driver()
    wait   = WebDriverWait(driver, 20)

    # Test suite – each tuple is (display name, test function)
    suite = [
        ("TC-SLP-01  Add  Skip Lot Plan", add_skip_lot_plan),
        ("TC-SLP-02  Edit Skip Lot Plan", edit_skip_lot_plan),
        ("TC-SLP-03  View Skip Lot Plan", view_skip_lot_plan),
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
    print("  SKIP LOT PLAN TESTS – FINAL SUMMARY")
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
    run_skip_lot_plan_tests()
