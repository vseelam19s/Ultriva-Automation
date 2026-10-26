"""
Script: mark_user_cases_automated.py
Purpose: Mark all test cases in AdminModule > Admin > User section as "Is Automated"
         on TestRail (https://upland.testrail.com/)

Targets:
  Project  : Ultriva (ID=15)
  Suite    : AdminModule (ID=2571)
  Section  : Admin > User (ID=92084)
"""

import os
import requests
import json
import time

# ── Config ────────────────────────────────────────────────────────────────────
TESTRAIL_URL = "https://upland.testrail.com/"
EMAIL        = "vseelam@uplandsoftware.com"
API_KEY      = os.environ["TESTRAIL_API_KEY"]
PROJECT_ID   = 15
SUITE_ID     = 2571   # AdminModule
SECTION_ID   = 92084  # Admin > User

AUTH = (EMAIL, API_KEY)
HEADERS = {"Content-Type": "application/json"}


def api_get(path):
    resp = requests.get(TESTRAIL_URL + "index.php?/api/v2/" + path,
                        headers=HEADERS, auth=AUTH)
    resp.raise_for_status()
    return resp.json()


def api_post(path, payload):
    resp = requests.post(TESTRAIL_URL + "index.php?/api/v2/" + path,
                         headers=HEADERS, auth=AUTH,
                         data=json.dumps(payload))
    resp.raise_for_status()
    return resp.json()


def get_all_cases():
    """Fetch all cases in the target section (handles pagination)."""
    cases = []
    offset = 0
    limit  = 250
    while True:
        data = api_get(
            f"get_cases/{PROJECT_ID}"
            f"&suite_id={SUITE_ID}"
            f"&section_id={SECTION_ID}"
            f"&limit={limit}&offset={offset}"
        )
        batch = data.get("cases", [])
        cases.extend(batch)
        if len(batch) < limit:
            break
        offset += limit
    return cases


def update_case_is_automated(case_id, value=True):
    """Set custom_isautomated on a single case."""
    return api_post(f"update_case/{case_id}", {"custom_isautomated": value})


def main():
    print("=" * 60)
    print("TestRail: Mark User Section Cases as 'Is Automated'")
    print(f"  Project ID : {PROJECT_ID}")
    print(f"  Suite      : AdminModule (ID={SUITE_ID})")
    print(f"  Section    : Admin > User (ID={SECTION_ID})")
    print("=" * 60)

    # 1. Fetch cases
    cases = get_all_cases()
    print(f"\nFound {len(cases)} test case(s) in Admin > User section:\n")
    for c in cases:
        status = "✓ ALREADY" if c.get("custom_isautomated") else "○ NOT YET"
        print(f"  [{status}] C{c['id']:>8}  {c['title']}")

    # 2. Update each case
    print(f"\nMarking all {len(cases)} cases as 'Is Automated = True' ...\n")
    results = []
    for c in cases:
        case_id = c["id"]
        title   = c["title"]
        already = bool(c.get("custom_isautomated"))
        if already:
            print(f"  [SKIP]   C{case_id}  '{title}'  (already automated)")
            results.append({"case_id": case_id, "title": title, "status": "already_automated"})
            continue

        try:
            updated = update_case_is_automated(case_id, True)
            flag    = bool(updated.get("custom_isautomated"))
            if flag:
                print(f"  [OK]     C{case_id}  '{title}'  → Is Automated = True")
                results.append({"case_id": case_id, "title": title, "status": "updated"})
            else:
                print(f"  [WARN]   C{case_id}  '{title}'  → unexpected value: {flag}")
                results.append({"case_id": case_id, "title": title, "status": "warn"})
        except Exception as e:
            print(f"  [ERROR]  C{case_id}  '{title}'  → {e}")
            results.append({"case_id": case_id, "title": title, "status": "error", "error": str(e)})

        time.sleep(0.2)   # polite rate-limiting

    # 3. Summary
    print("\n" + "=" * 60)
    updated_ok = [r for r in results if r["status"] == "updated"]
    already    = [r for r in results if r["status"] == "already_automated"]
    errors     = [r for r in results if r["status"] == "error"]

    print(f"SUMMARY: {len(cases)} total cases")
    print(f"  Newly marked : {len(updated_ok)}")
    print(f"  Already done : {len(already)}")
    print(f"  Errors       : {len(errors)}")
    print("=" * 60)
    print(f"\nView in TestRail:")
    print(f"  https://upland.testrail.com/index.php?/cases/view/{PROJECT_ID}"
          f"&suite_id={SUITE_ID}&section_id={SECTION_ID}")

    return results


if __name__ == "__main__":
    main()
