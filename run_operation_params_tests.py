"""
run_operation_params_tests.py – Standalone runner for Operation Params test suite.

Runs test cases:
    TC-OP-PARAMS-01  Add  Operation Params
    TC-OP-PARAMS-02  Edit Operation Params
    TC-OP-PARAMS-03  View Operation Params

QA Site:
    https://engineering.ultrivalms.com/QALS1011

Navigation Path:
    Admin > Entities (left nav) > Operation Params

Entity Token:
    tk=$OperationParams

Usage (from workspace root  c:\\Prcatices-AI):
    python -m qa_automation.run_operation_params_tests

Usage (from qa_automation folder):
    python run_operation_params_tests.py
"""

import sys
import os

# Ensure qa_automation is on the path when run directly from the workspace root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from selenium.webdriver.support.ui import WebDriverWait
from utils.driver_setup import get_driver
from qa_automation.tests.QALS11.Admin.Entities.Test_OperationParams import (
    add_operation_params,
    edit_operation_params,
    view_operation_params,
)


def run_operation_params_tests():
    """
    Instantiate WebDriver, run all three Operation Params tests, print summary.

    Test Suite:
        TC-OP-PARAMS-01  Add  Operation Params
        TC-OP-PARAMS-02  Edit Operation Params
        TC-OP-PARAMS-03  View Operation Params
    """
    driver = get_driver()
    wait   = WebDriverWait(driver, 20)

    suite = [
        ("TC-OP-PARAMS-01  Add  Operation Params", add_operation_params),
        ("TC-OP-PARAMS-02  Edit Operation Params", edit_operation_params),
        ("TC-OP-PARAMS-03  View Operation Params", view_operation_params),
    ]

    results = {}
    for name, fn in suite:
        print(f"\n{'─' * 60}")
        print(f"  Running: {name}")
        print(f"{'─' * 60}")
        try:
            results[name] = fn(driver, wait)
        except Exception as exc:
            print(f"  [ERROR] {name}: {exc}")
            results[name] = False

    driver.quit()

    # ── Final Summary ─────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  OPERATION PARAMS TESTS – FINAL SUMMARY")
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
    run_operation_params_tests()
