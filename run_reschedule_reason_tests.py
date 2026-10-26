"""
run_reschedule_reason_tests.py – Standalone runner for Reschedule Reason test suite.

Runs test cases:
    TC-RR-01  Add  Reschedule Reason
    TC-RR-02  Edit Reschedule Reason
    TC-RR-03  View Reschedule Reason

Usage (from workspace root  c:\\Prcatices-AI):
    python -m qa_automation.run_reschedule_reason_tests

Usage (from qa_automation folder):
    python admin/Entities/RescheduleReason.py
    -- or --
    python run_reschedule_reason_tests.py
"""

import sys
import os

# Ensure qa_automation is on the path when run directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from selenium.webdriver.support.ui import WebDriverWait
from utils.driver_setup import get_driver
from qa_automation.QASite.QALS11.Admin.Entities.test_RescheduleReason import (
    add_reschedule_reason,
    edit_reschedule_reason,
    view_reschedule_reason,
)


def run_reschedule_reason_tests():
    """Instantiate WebDriver, run all three Reschedule Reason tests, print summary."""
    driver = get_driver()
    wait   = WebDriverWait(driver, 20)

    suite = [
        ("TC-RR-01  Add  Reschedule Reason", add_reschedule_reason),
        ("TC-RR-02  Edit Reschedule Reason", edit_reschedule_reason),
        ("TC-RR-03  View Reschedule Reason", view_reschedule_reason),
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
    print("  RESCHEDULE REASON TESTS – FINAL SUMMARY")
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
    run_reschedule_reason_tests()
