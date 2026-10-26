"""
run_machine_tests.py – Standalone runner for the 3 Machine entity test cases.

Covered Test Cases:
    TC-MC-01: Add  Machine   – create a new Machine via the + Add form
    TC-MC-02: Edit Machine   – select existing Machine and update Code / Name
    TC-MC-03: View Machine   – open View detail page and Cancel back to list

Navigation Path (UI):
    Admin > (left nav) Entities > Machine

QA Site URL base:
    https://engineering.ultrivalms.com/QALS1011

Usage:
    # From the qa_automation folder:
    python run_machine_tests.py

Reference entity file: admin/Entities/Machine.py
Reference runner     : run_operation_tests.py
"""

import sys
import os

# Ensure qa_automation root is on the path so all imports resolve correctly
sys.path.insert(0, os.path.dirname(__file__))

from selenium.webdriver.support.ui import WebDriverWait
from utils.driver_setup import get_driver

# Import the three Machine test-case functions
from qa_automation.QASite.QALS11.Admin.Entities.test_Machine import add_machine, edit_machine, view_machine

# ── Driver / Wait setup ───────────────────────────────────────────────────────
driver = get_driver()
wait   = WebDriverWait(driver, 20)

# ── Test suite definition ─────────────────────────────────────────────────────
tests = [
    ("TC-MC-01  Add  Machine", add_machine),   # Add flow
    ("TC-MC-02  Edit Machine", edit_machine),  # Edit flow
    ("TC-MC-03  View Machine", view_machine),  # View / Cancel flow
]

results = {}

# ── Run each test case ────────────────────────────────────────────────────────
for name, fn in tests:
    print(f"\n{'─'*55}")
    print(f"  Running: {name}")
    print(f"{'─'*55}")
    try:
        ok = fn(driver, wait)
    except Exception as exc:
        ok = False
        print(f"  EXCEPTION: {exc}")
    results[name] = ok
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}")

# ── Quit browser before printing summary ─────────────────────────────────────
driver.quit()

# ── Final summary ─────────────────────────────────────────────────────────────
print(f"\n{'═'*55}")
print("  MACHINE TEST RESULTS – FINAL SUMMARY")
print(f"{'═'*55}")
for name, ok in results.items():
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}]  {name}")
passed = sum(results.values())
total  = len(results)
print(f"{'─'*55}")
print(f"  Total: {total} | Passed: {passed} | Failed: {total - passed}")
print(f"{'═'*55}\n")
