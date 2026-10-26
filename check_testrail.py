"""
TestRail quick-access script.

Run from the qa_automation folder:
    python check_testrail.py

Config is in config/config.py  (URL, email, API key, project ID).
"""

import json
import sys
from config.config import TESTRAIL_URL, TESTRAIL_EMAIL, TESTRAIL_API_KEY, TESTRAIL_PROJECT_ID

CASE_ID = 5242647   # C5242647

print("=" * 60)
print("  TestRail Connection")
print(f"  URL     : {TESTRAIL_URL}")
print(f"  Email   : {TESTRAIL_EMAIL}")
print(f"  Project : {TESTRAIL_PROJECT_ID}")
print(f"  API Key : {'(set)' if TESTRAIL_API_KEY else '(MISSING)'}")
print("=" * 60)

if not TESTRAIL_API_KEY:
    print("\n[ERROR] TESTRAIL_API_KEY is not set.")
    sys.exit(1)

from utils.testrail_client import TestRailClient

tr = TestRailClient()

# ── 1. Project info ───────────────────────────────────────────────────────────
print("\n[1] Project info:")
try:
    project = tr.get_project()
    print(f"    Name : {project.get('name', 'N/A')}")
    print(f"    ID   : {project.get('id', 'N/A')}")
except Exception as e:
    print(f"[FAIL] {e}")
    sys.exit(1)

# ── 2. Fetch specific case C5242647 ───────────────────────────────────────────
print(f"\n[2] Fetching case C{CASE_ID}:")
try:
    case = tr.get_case(case_id=CASE_ID)
    print(f"    ID      : C{case['id']}")
    print(f"    Title   : {case.get('title', 'N/A')}")
    print(f"    Section : {case.get('section_id', 'N/A')}")
    print(f"    Type    : {case.get('type_id', 'N/A')}")
    print(f"    Priority: {case.get('priority_id', 'N/A')}")
    print(f"\n    Full response:")
    print(json.dumps(case, indent=4, default=str))
except Exception as e:
    print(f"[FAIL] get_case C{CASE_ID}: {e}")

# ── 3. Total test cases in project (multi-suite) ─────────────────────────────
print(f"\n[3] Total test cases in project {TESTRAIL_PROJECT_ID}:")
try:
    suites = tr.get_suites()
    total = 0
    for s in suites:
        try:
            cases = tr.get_cases(suite_id=s['id'])
            print(f"    Suite S{s['id']} '{s.get('name', '')}': {len(cases)} case(s)")
            total += len(cases)
        except Exception as se:
            print(f"    Suite S{s['id']} [FAIL]: {se}")
    print(f"\n    *** Total Test Cases (all suites): {total} ***")
except Exception as e:
    print(f"[FAIL] get_suites: {e}")
