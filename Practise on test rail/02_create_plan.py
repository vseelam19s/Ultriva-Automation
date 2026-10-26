"""
Step 2 – Create test plan "AuomationPractiseQA", assign to milestone,
         add suite S2571 (Admin module), include case C5157814.
Run: python "Practise on test rail/02_create_plan.py"  (from qa_automation/)

Requires 01_create_milestone.py to have been run first (needs milestone_id).
Set MILESTONE_ID below after running step 1.
"""
import sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config.config import TESTRAIL_PROJECT_ID, TESTRAIL_API_KEY
from utils.testrail_client import TestRailClient

# ── Config ────────────────────────────────────────────────────────────────────
MILESTONE_ID = 2632   # M2632 – AuomationPractiseQA
PLAN_NAME    = "AuomationPractiseQA"
SUITE_ID     = 2571   # Admin module
CASE_ID      = 5157814

if not TESTRAIL_API_KEY:
    print("[ERROR] TESTRAIL_API_KEY not set."); sys.exit(1)

if MILESTONE_ID is None:
    print("[ERROR] Set MILESTONE_ID at the top of this file first."); sys.exit(1)

tr = TestRailClient()

# Create plan with suite entry (runs scoped to one case)
entry = {
    "suite_id":    SUITE_ID,
    "name":        "Admin Module",
    "include_all": False,
    "case_ids":    [CASE_ID],
}
plan = tr._client.plans.add_plan(
    project_id=TESTRAIL_PROJECT_ID,
    name=PLAN_NAME,
    milestone_id=MILESTONE_ID,
    entries=[entry],
)
plan_id = plan["id"]
print(f"[OK] Plan created: P{plan_id}  '{plan['name']}'  milestone=M{MILESTONE_ID}")

# Print the run created inside the plan entry
for e in plan.get("entries", []):
    for r in e.get("runs", []):
        print(f"     Run R{r['id']}  suite=S{SUITE_ID}  cases={[CASE_ID]}")

print(json.dumps(plan, indent=2, default=str))
