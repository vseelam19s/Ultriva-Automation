"""
run_location_code_tests.py – Standalone runner for Location Code test suite.

Runs test cases:
    TC-LC-01  Add  Location Code
    TC-LC-02  Edit Location Code
    TC-LC-03  View Location Code

Usage (from workspace root  c:\\Prcatices-AI):
    python -m qa_automation.admin.Entities.LocationCode

Usage (from qa_automation folder):
    python admin/Entities/LocationCode.py
    -- or --
    python run_location_code_tests.py
"""

import sys
import os

# Ensure qa_automation is on the path when run directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from selenium.webdriver.support.ui import WebDriverWait
from utils.driver_setup import get_driver
from qa_automation.tests.QALS11.Admin.Entities.test_LocationCode import (
    add_location_code,
    edit_location_code,
    view_location_code,
)


def run_location_code_tests():
    """Instantiate WebDriver, run all three Location Code tests, print summary."""
    driver = get_driver()
    wait   = WebDriverWait(driver, 20)

    suite = [
        ("TC-LC-01  Add  Location Code", add_location_code),
        ("TC-LC-02  Edit Location Code", edit_location_code),
        ("TC-LC-03  View Location Code", view_location_code),
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
    print("  LOCATION CODE TESTS – FINAL SUMMARY")
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
    run_location_code_tests()
