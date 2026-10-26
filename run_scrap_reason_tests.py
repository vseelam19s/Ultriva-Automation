"""
run_scrap_reason_tests.py – Standalone runner for Scrap Reason test suite.

Runs test cases:
    TC-SR-01  Add  Scrap Reason
    TC-SR-02  Edit Scrap Reason
    TC-SR-03  View Scrap Reason

QA Site:
    https://engineering.ultrivalms.com/QALS1011

Usage (from workspace root  c:\\Prcatices-AI):
    python -m qa_automation.run_scrap_reason_tests

Usage (from qa_automation folder):
    python run_scrap_reason_tests.py
"""

import sys
import os

# Ensure qa_automation is on the path when run directly from the workspace root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from selenium.webdriver.support.ui import WebDriverWait
from utils.driver_setup import get_driver
from admin.Entities.ScrapReason import (
    add_scrap_reason,
    edit_scrap_reason,
    view_scrap_reason,
)


def run_scrap_reason_tests():
    """Instantiate WebDriver, run all three Scrap Reason tests, print summary."""
    driver = get_driver()
    wait   = WebDriverWait(driver, 20)

    suite = [
        ("TC-SR-01  Add  Scrap Reason", add_scrap_reason),
        ("TC-SR-02  Edit Scrap Reason", edit_scrap_reason),
        ("TC-SR-03  View Scrap Reason", view_scrap_reason),
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
    print("  SCRAP REASON TESTS – FINAL SUMMARY")
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
    run_scrap_reason_tests()
