"""
mark_item_automated.py
Purpose: Mark all test cases in AdminModule > Admin > Item (ID=92099) as "Is Automated"
Project : Ultriva (ID=15)
Suite   : AdminModule (ID=2571)
"""
import os
import requests, json, time

TESTRAIL_URL = "https://upland.testrail.com/"
EMAIL        = "vseelam@uplandsoftware.com"
API_KEY      = os.environ["TESTRAIL_API_KEY"]
PROJECT_ID   = 15
SUITE_ID     = 2571
SECTION_ID   = 92099  # Admin > Item

AUTH    = (EMAIL, API_KEY)
HEADERS = {"Content-Type": "application/json"}

def api_get(path):
    resp = requests.get(TESTRAIL_URL + "index.php?/api/v2/" + path, headers=HEADERS, auth=AUTH)
    resp.raise_for_status()
    return resp.json()

def api_post(path, payload):
    resp = requests.post(TESTRAIL_URL + "index.php?/api/v2/" + path, headers=HEADERS, auth=AUTH, data=json.dumps(payload))
    resp.raise_for_status()
    return resp.json()

def get_all_cases():
    cases, offset, limit = [], 0, 250
    while True:
        data  = api_get(f"get_cases/{PROJECT_ID}&suite_id={SUITE_ID}&section_id={SECTION_ID}&limit={limit}&offset={offset}")
        batch = data.get("cases", []) if isinstance(data, dict) else data
        cases.extend(batch)
        if len(batch) < limit:
            break
        offset += limit
    return cases

print("="*60)
print("TestRail: Mark Admin > Item cases as 'Is Automated'")
print(f"  Project : Ultriva (ID={PROJECT_ID})")
print(f"  Suite   : AdminModule (ID={SUITE_ID})")
print(f"  Section : Admin > Item (ID={SECTION_ID})")
print("="*60)

cases = get_all_cases()
print(f"\nFound {len(cases)} test case(s):\n")

updated, skipped, failed = 0, 0, 0
for c in cases:
    cid, title, already = c["id"], c.get("title",""), bool(c.get("custom_isautomated"))
    print(f"  C{cid}  '{title}'  automated={already}")
    if already:
        skipped += 1
        continue
    try:
        result = api_post(f"update_case/{cid}", {"custom_isautomated": True})
        flag = bool(result.get("custom_isautomated"))
        print(f"    → [OK] Is Automated = {flag}")
        updated += 1
    except Exception as e:
        print(f"    → [FAIL] {e}")
        failed += 1
    time.sleep(0.2)

print(f"\n{'='*60}")
print(f"RESULTS  —  Admin > Item section only")
print(f"{'='*60}")
print(f"  Total cases : {len(cases)}")
print(f"  Newly marked: {updated}")
print(f"  Already done: {skipped}")
print(f"  Failed      : {failed}")
print("="*60)
