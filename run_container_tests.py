"""
run_container_tests.py – Standalone runner for the Container test suite.

Runs test cases:
    TC-CON-01  Add  Container
    TC-CON-02  Edit Container
    TC-CON-03  View Container

Usage (from qa_automation folder):
    python run_container_tests.py

Usage (from workspace root  c:\\Prcatices-AI):
    python -m qa_automation.run_container_tests
"""

import sys
import os

# Ensure qa_automation is on the path when run directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from selenium.webdriver.support.ui import WebDriverWait
from utils.driver_setup import get_driver
from qa_automation.QASite.QALS11.Admin.Entities.test_Container import (
    add_container,
    edit_container,
    view_container,
)


def run_container_tests():
    """Instantiate WebDriver, run all three Container tests, print summary."""
    driver = get_driver()
    wait   = WebDriverWait(driver, 20)

    suite = [
        ("TC-CON-01  Add  Container", add_container),
        ("TC-CON-02  Edit Container", edit_container),
        ("TC-CON-03  View Container", view_container),
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
    print("  CONTAINER TESTS – FINAL SUMMARY")
    print("=" * 70)
    passed = sum(1 for v in results.values() if v)
    failed = len(results) - passed
    for name, ok in results.items():
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}]  {name}")
    print("─" * 70)
    print(f"  Total: {len(results)}  |  Passed: {passed}  |  Failed: {failed}")
    print("=" * 70)


if __name__ == "__main__":
    run_container_tests()
