"""
ULT-10069 | Add TestRail Case — Kanban Loop Design Not Processing

- Suite   : S2571  (Admin module → Kanban Loop Design)
- Ref case: C13569701  (steps + expected results copied from here)
- Precond : Stop Manage Background Service

Run:
    cd qa_automation
    python "JIRA Tickets/Bugs/ULT-10069_add_testrail_case.py"
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from utils.testrail_client import TestRailClient

SECTION_ID   = 372888    # Suite S2571 (Admin) → Kanban Loop Design
REF_CASE_ID  = 13569701  # C13569701
NEW_CASE_ID  = 17520015  # C17520015 — already created; update steps here

tr = TestRailClient()

# ── 1. Fetch reference case ───────────────────────────────────────────────────
print(f"\nFetching reference case C{REF_CASE_ID} ...")
ref = tr.get_case(case_id=REF_CASE_ID)
print(f"  Title    : {ref.get('title')}")
print(f"  Steps    : {ref.get('custom_steps', '')[:80]} ...")
print(f"  Expected : {ref.get('custom_expected', '')[:80]} ...")

# ── 2. Update C17520015 with steps + expected results from reference ──────────
print(f"\nUpdating C{NEW_CASE_ID} with steps and expected results ...")
updated = tr.update_case(
    case_id          = NEW_CASE_ID,
    custom_steps     = ref.get("custom_steps"),
    custom_expected  = ref.get("custom_expected"),
)

print("\n── Result ───────────────────────────────────────────────────────────────")
print(f"  Case ID       : C{updated['id']}")
print(f"  Title         : {updated.get('title')}")
print(f"  Preconditions : {updated.get('custom_preconds')}")
print(f"  Steps         : {updated.get('custom_steps', '')[:120]} ...")
print(f"  Expected      : {updated.get('custom_expected', '')[:120]} ...")
print(f"  URL           : https://upland.testrail.com/index.php?/cases/view/{updated['id']}")
