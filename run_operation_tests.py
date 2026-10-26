"""
run_operation_tests.py – Runs only the 3 Operation entity test cases.
    TC-OP-01: Add Operation
    TC-OP-02: Edit Operation
    TC-OP-03: View Operation
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from selenium.webdriver.support.ui import WebDriverWait
from utils.driver_setup import get_driver
from qa_automation.QASite.QALS11.Admin.Entities.test_Operation import add_operation, edit_operation, view_operation

driver = get_driver()
wait   = WebDriverWait(driver, 20)
results = {}

tests = [
    ("TC-OP-01  Add  Operation", add_operation),
    ("TC-OP-02  Edit Operation", edit_operation),
    ("TC-OP-03  View Operation", view_operation),
]

for name, fn in tests:
    print(f"\n{'─'*55}")
    print(f"  Running: {name}")
    print(f"{'─'*55}")
    try:
        ok = fn(driver, wait)
    except Exception as e:
        ok = False
        print(f"  EXCEPTION: {e}")
    results[name] = ok
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}")

driver.quit()

print(f"\n{'─'*55}")
print("  FINAL RESULTS")
print(f"{'─'*55}")
for name, ok in results.items():
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
passed = sum(results.values())
print(f"\n  {passed}/{len(results)} tests passed.")
