"""
run_break_reason_code_tests.py – Standalone runner for Break Reason Code test suite.

Runs test cases:
    TC-BR-01  Add  Break Reason Code
    TC-BR-02  Edit Break Reason Code
    TC-BR-03  View Break Reason Code

QA Site:
    https://engineering.ultrivalms.com/QALS1011

Usage (from workspace root  c:\\Prcatices-AI):
    python -m qa_automation.run_break_reason_code_tests

Usage (from qa_automation folder):
    python run_break_reason_code_tests.py
"""

import sys
import os

# Ensure qa_automation is on the path when run directly from the workspace root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from selenium.webdriver.support.ui import WebDriverWait
from utils.driver_setup import get_driver
from qa_automation.tests.QALS11.Admin.Entities.test_BreakReasonCode import (
    add_break_reason_code,
    edit_break_reason_code,
    view_break_reason_code,
)


def run_break_reason_code_tests():
    """Instantiate WebDriver, run all three Break Reason Code tests, print summary."""
    driver = get_driver()
    wait   = WebDriverWait(driver, 20)

    suite = [
        ("TC-BR-01  Add  Break Reason Code", add_break_reason_code),
        ("TC-BR-02  Edit Break Reason Code", edit_break_reason_code),
        ("TC-BR-03  View Break Reason Code", view_break_reason_code),
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
    print("  BREAK REASON CODE TESTS – FINAL SUMMARY")
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
    run_break_reason_code_tests()
