"""
run_admin_entity_tests.py – Master runner for all Admin Entity test suites.

Runs test cases for:
    • Logistics Mode   (TC-LM-01  Add, TC-LM-02  Edit, TC-LM-03  View)
    • ABC Code         (TC-ABC-01 Add, TC-ABC-02 Edit, TC-ABC-03 View)
    • Carrier          (TC-CAR-01 Add, TC-CAR-02 Edit, TC-CAR-03 View)
    • Notes            (TC-NOT-01 Add, TC-NOT-02 Edit, TC-NOT-03 View)
    • Production Issue (TC-PI-01  Add, TC-PI-02  Edit, TC-PI-03  View)
    • Exception Code   (TC-EC-01  Add, TC-EC-02  Edit, TC-EC-03  View)
    • Operation        (TC-OP-01  Add, TC-OP-02  Edit, TC-OP-03  View)
    • Machine          (TC-MC-01  Add, TC-MC-02  Edit, TC-MC-03  View)

Usage:
    python run_admin_entity_tests.py
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from selenium.webdriver.support.ui import WebDriverWait
from utils.driver_setup import get_driver

# Import per-entity test functions
from qa_automation.QASite.QALS11.Admin.Entities.test_logisticsMode   import add_logistics_mode,    edit_logistics_mode,    view_logistics_mode
from qa_automation.QASite.QALS11.Admin.Entities.test_ABCCode         import add_abc_code,          edit_abc_code,          view_abc_code
from qa_automation.QASite.QALS11.Admin.Entities.test_Carrier         import add_carrier,           edit_carrier,           view_carrier
from qa_automation.QASite.QALS11.Admin.Entities.test_Notes           import add_note,              edit_note,              view_note
from qa_automation.QASite.QALS11.Admin.Entities.test_ProductionIssue import add_production_issue,  edit_production_issue,  view_production_issue
from qa_automation.QASite.QALS11.Admin.Entities.test_ExceptionCode   import add_exception_code,    edit_exception_code,    view_exception_code
from qa_automation.QASite.QALS11.Admin.Entities.test_Operation       import add_operation,         edit_operation,         view_operation
from qa_automation.QASite.QALS11.Admin.Entities.test_Machine         import add_machine,           edit_machine,           view_machine


def run_all():
    driver = get_driver()
    wait   = WebDriverWait(driver, 20)

    suite = [
        # (display name,                          test function)
        ("TC-LM-01  Add  Logistics Mode",         add_logistics_mode),
        ("TC-LM-02  Edit Logistics Mode",         edit_logistics_mode),
        ("TC-LM-03  View Logistics Mode",         view_logistics_mode),
        ("TC-ABC-01 Add  ABC Code",               add_abc_code),
        ("TC-ABC-02 Edit ABC Code",               edit_abc_code),
        ("TC-ABC-03 View ABC Code",               view_abc_code),
        ("TC-CAR-01 Add  Carrier",                add_carrier),
        ("TC-CAR-02 Edit Carrier",                edit_carrier),
        ("TC-CAR-03 View Carrier",                view_carrier),
        ("TC-NOT-01 Add  Note",                   add_note),
        ("TC-NOT-02 Edit Note",                   edit_note),
        ("TC-NOT-03 View Note",                   view_note),
        ("TC-PI-01  Add  Production Issue",       add_production_issue),
        ("TC-PI-02  Edit Production Issue",       edit_production_issue),
        ("TC-PI-03  View Production Issue",       view_production_issue),
        ("TC-EC-01  Add  Exception Code",         add_exception_code),
        ("TC-EC-02  Edit Exception Code",         edit_exception_code),
        ("TC-EC-03  View Exception Code",         view_exception_code),
        ("TC-OP-01  Add  Operation",              add_operation),
        ("TC-OP-02  Edit Operation",              edit_operation),
        ("TC-OP-03  View Operation",              view_operation),
        ("TC-MC-01  Add  Machine",                add_machine),
        ("TC-MC-02  Edit Machine",                edit_machine),
        ("TC-MC-03  View Machine",                view_machine),
    ]

    results = {}
    for name, fn in suite:
        print(f"\n{'─'*55}")
        print(f"  Running: {name}")
        print(f"{'─'*55}")
        try:
            results[name] = fn(driver, wait)
        except Exception as exc:
            print(f"  [ERROR] {name}: {exc}")
            results[name] = False

    driver.quit()

    # ── Final Summary ─────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  ADMIN ENTITY TESTS – FINAL SUMMARY")
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

    return failed == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
