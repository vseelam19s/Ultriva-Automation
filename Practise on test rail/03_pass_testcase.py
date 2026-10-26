"""
Step 3 – Pass case C5157814 in run R80369 and show result.
Run: python "Practise on test rail/03_pass_testcase.py"  (from qa_automation/)
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config.config import TESTRAIL_API_KEY
from utils.testrail_client import TestRailClient

RUN_ID  = 80369
CASE_ID = 5157814

if not TESTRAIL_API_KEY:
    print("[ERROR] TESTRAIL_API_KEY not set."); sys.exit(1)

tr = TestRailClient()

# Submit passed result
result = tr.add_result(
    run_id=RUN_ID,
    case_id=CASE_ID,
    status="passed",
    comment="Marked passed via AuomationPractiseQA practice run.",
)
print(f"\n[OK] Result submitted for C{CASE_ID} in R{RUN_ID}")
print(json.dumps(result, indent=2, default=str))

# Fetch updated test to confirm
test = tr._client.tests.get_tests(run_id=RUN_ID)
tests = test.get("tests", test) if isinstance(test, dict) else test
print(f"\n[Result Summary for Run R{RUN_ID}]")
STATUS = {1:"PASSED", 2:"BLOCKED", 3:"UNTESTED", 4:"RETEST", 5:"FAILED"}
for t in tests:
    print(f"  C{t['case_id']}  {t.get('title','')}  → {STATUS.get(t.get('status_id'), t.get('status_id'))}")
