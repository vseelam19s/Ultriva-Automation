"""
mark_entities_automated.py
Purpose: Mark all test cases in AdminModule > Admin > Entities and ALL sub-folders as "Is Automated"
Project : Ultriva (ID=15)
Suite   : AdminModule (ID=2571)

Section tree (from API):
  Admin > Entities                              (92092)
  ├─ Product Line                               (92093)
  ├─ Commodity Code                             (92094)
  ├─ Carrier                                    (92095)
  │   └─ Tracking URL in multiple areas in CSP (385372)
  ├─ Notes                                      (92096)
  ├─ Exception Code                             (92097)
  ├─ Location Code                              (92098)
  └─ Machine                                    (144109)
"""
import requests, json, time

TESTRAIL_URL = "https://upland.testrail.com/"
EMAIL        = "vseelam@uplandsoftware.com"
API_KEY      = "LR5Bc8syGLl4d.dweMDC-bN9OoDA5pyiO6dKCHlh3"
PROJECT_ID   = 15
SUITE_ID     = 2571

AUTH    = (EMAIL, API_KEY)
HEADERS = {"Content-Type": "application/json"}

TARGET_SECTIONS = [
    (92092,  "Admin > Entities"),
    (92093,  "Admin > Entities > Product Line"),
    (92094,  "Admin > Entities > Commodity Code"),
    (92095,  "Admin > Entities > Carrier"),
    (385372, "Admin > Entities > Carrier > Tracking URL in multiple areas in CSP"),
    (92096,  "Admin > Entities > Notes"),
    (92097,  "Admin > Entities > Exception Code"),
    (92098,  "Admin > Entities > Location Code"),
    (144109, "Admin > Entities > Machine"),
]

def api_get(path):
    resp = requests.get(TESTRAIL_URL + "index.php?/api/v2/" + path, headers=HEADERS, auth=AUTH)
    resp.raise_for_status()
    return resp.json()

def api_post(path, payload):
    resp = requests.post(TESTRAIL_URL + "index.php?/api/v2/" + path, headers=HEADERS, auth=AUTH, data=json.dumps(payload))
    resp.raise_for_status()
    return resp.json()

def get_cases_for_section(section_id):
    cases, offset, limit = [], 0, 250
    while True:
        data  = api_get(f"get_cases/{PROJECT_ID}&suite_id={SUITE_ID}&section_id={section_id}&limit={limit}&offset={offset}")
        batch = data.get("cases", []) if isinstance(data, dict) else data
        cases.extend(batch)
        if len(batch) < limit:
            break
        offset += limit
    return cases

def process_section(section_id, label):
    print(f"\n{'─'*64}")
    print(f"  Section : {label}  (ID={section_id})")
    print(f"{'─'*64}")
    cases = get_cases_for_section(section_id)
    if not cases:
        print("  (no test cases found)")
        return 0, 0, 0
    updated, skipped, failed = 0, 0, 0
    for c in cases:
        cid, title, already = c["id"], c.get("title",""), bool(c.get("custom_isautomated"))
        if already:
            print(f"  [SKIP]  C{cid:<10} '{title}'")
            skipped += 1
            continue
        try:
            result = api_post(f"update_case/{cid}", {"custom_isautomated": True})
            flag = bool(result.get("custom_isautomated"))
            print(f"  [OK]    C{cid:<10} '{title}'  → Is Automated = {flag}")
            updated += 1
        except Exception as e:
            print(f"  [FAIL]  C{cid:<10} '{title}'  → {e}")
            failed += 1
        time.sleep(0.2)
    print(f"\n  Result: {updated} updated  |  {skipped} already done  |  {failed} failed  (total={len(cases)})")
    return updated, skipped, failed

print("="*64)
print("  TestRail – Mark Admin > Entities (all sub-folders) as 'Is Automated'")
print(f"  Project : Ultriva (ID={PROJECT_ID})")
print(f"  Suite   : AdminModule (ID={SUITE_ID})")
print(f"  Sections: {len(TARGET_SECTIONS)}")
print("="*64)

grand_updated = grand_skipped = grand_failed = 0
for sid, label in TARGET_SECTIONS:
    u, s, f = process_section(sid, label)
    grand_updated += u
    grand_skipped += s
    grand_failed  += f

print(f"\n{'='*64}")
print("  GRAND TOTALS  —  Admin > Entities (all sub-folders)")
print(f"{'='*64}")
print(f"  Total sections  : {len(TARGET_SECTIONS)}")
print(f"  Newly marked    : {grand_updated}")
print(f"  Already done    : {grand_skipped}")
print(f"  Failed          : {grand_failed}")
print("="*64)
