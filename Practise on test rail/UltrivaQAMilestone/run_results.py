"""
run_results.py  –  Submit pass/fail results to TestRail runs
=============================================================
Commands:
  mark_run    Mark all tests in one run as passed, with specific test IDs as failed
  mark_all    Mark ALL runs in plan P81033 as passed (same fail-list applies)

Run from qa_automation/:
  python "Practise on test rail/UltrivaQAMilestone/run_results.py" mark_run
  python "Practise on test rail/UltrivaQAMilestone/run_results.py" mark_all
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from config.config import TESTRAIL_API_KEY
from utils.testrail_client import TestRailClient

# ── Config ────────────────────────────────────────────────────────────────────
PLAN_ID        = 81033
TARGET_RUN_ID  = 81320          # R81320  –  System Configuration Parameters settings

# Test IDs (T-prefixed) to mark as FAILED; all others → PASSED
FAIL_TEST_IDS  = {41146589, 41146590}

PASSED = 1
FAILED = 5

# ── Helpers ───────────────────────────────────────────────────────────────────
def _connect():
    if not TESTRAIL_API_KEY:
        print("[ERROR] TESTRAIL_API_KEY not set."); sys.exit(1)
    return TestRailClient()

def _submit_run(tr, run_id):
    """Pass all tests in run_id; fail any whose id is in FAIL_TEST_IDS."""
    raw   = tr._client.tests.get_tests(run_id=run_id)
    tests = raw.get("tests", raw) if isinstance(raw, dict) else raw
    if not tests:
        print(f"  [skip] R{run_id} – no tests")
        return 0, 0

    results = [
        {"test_id": t["id"],
         "status_id": FAILED if t["id"] in FAIL_TEST_IDS else PASSED}
        for t in tests
    ]
    tr._client.results.add_results(run_id=run_id, results=results)

    passed = sum(1 for r in results if r["status_id"] == PASSED)
    failed = sum(1 for r in results if r["status_id"] == FAILED)
    print(f"  R{run_id:<7}  total={len(results):4d}  passed={passed}  failed={failed}"
          + (f"  → {[r['test_id'] for r in results if r['status_id']==FAILED]}" if failed else ""))
    return passed, failed

# ── Commands ──────────────────────────────────────────────────────────────────
def mark_run():
    """Submit results for TARGET_RUN_ID only."""
    tr = _connect()
    print(f"Submitting results for R{TARGET_RUN_ID} ...")
    p, f = _submit_run(tr, TARGET_RUN_ID)
    print(f"\n[Done] passed={p}  failed={f}")

def mark_all():
    """Submit results for every run in PLAN_ID."""
    tr      = _connect()
    plan    = tr._client.plans.get_plan(plan_id=PLAN_ID)
    entries = plan.get("entries", [])
    runs    = [e["runs"][0]["id"] for e in entries if e.get("runs")]

    print(f"Plan P{PLAN_ID}  –  {len(runs)} runs to process ...\n")
    total_p = total_f = 0
    for rid in runs:
        p, f     = _submit_run(tr, rid)
        total_p += p
        total_f += f

    print(f"\n[Done] {len(runs)} runs  –  passed={total_p}  failed={total_f}")

# ── Entry point ───────────────────────────────────────────────────────────────
COMMANDS = {"mark_run": mark_run, "mark_all": mark_all}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd not in COMMANDS:
        print(__doc__); sys.exit(0)
    COMMANDS[cmd]()
