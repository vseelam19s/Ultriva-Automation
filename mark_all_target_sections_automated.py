"""
mark_all_target_sections_automated.py
Purpose: Mark ALL test cases in the following AdminModule sections as
         "Is Automated" (custom_isautomated = True):

  ── Plant ─────────────────────────────────────────────────────────────
  • Plant > Calendar                        (92080)

  ── Admin ─────────────────────────────────────────────────────────────
  • Admin > Groups                          (92085)
  • Admin > User Group                      (92086)
  • Admin > Supplier                        (92157)
      └─ Admin > Supplier > Supplier User   (92158)
      └─ Admin > Supplier > Supplier Item   (92160)
      └─ Admin > Supplier > Calendar        (92162)

Project : Ultriva (ID=15)
Suite   : AdminModule (ID=2571)
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
SUITE_ID     = 2571  # AdminModule

AUTH    = (EMAIL, API_KEY)
HEADERS = {"Content-Type": "application/json"}

# ── Target sections ───────────────────────────────────────────────────────────
TARGET_SECTIONS = [
    (92080, "Plant > Calendar"),
    (92085, "Admin > Groups"),
    (92086, "Admin > User Group"),
    (92157, "Admin > Supplier"),
    (92158, "Admin > Supplier > Supplier User"),
    (92160, "Admin > Supplier > Supplier Item"),
    (92162, "Admin > Supplier > Calendar"),
]


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


def get_cases_for_section(section_id):
    """Fetch all cases in a section (handles pagination)."""
    cases  = []
    offset = 0
    limit  = 250
    while True:
        data  = api_get(
            f"get_cases/{PROJECT_ID}"
            f"&suite_id={SUITE_ID}"
            f"&section_id={section_id}"
            f"&limit={limit}&offset={offset}"
        )
        batch = data.get("cases", data) if isinstance(data, dict) else data
        cases.extend(batch)
        if len(batch) < limit:
            break
        offset += limit
    return cases


def update_case_automated(case_id):
    return api_post(f"update_case/{case_id}", {"custom_isautomated": True})


def process_section(section_id, label):
    print(f"\n{'─'*64}")
    print(f"  Section : {label}  (ID={section_id})")
    print(f"{'─'*64}")

    cases = get_cases_for_section(section_id)
    if not cases:
        print("  (no test cases found)")
        return 0, 0, 0

    total    = len(cases)
    skipped  = 0
    updated  = 0
    failed   = 0

    for c in cases:
        case_id = c["id"]
        title   = c.get("title", "")
        already = bool(c.get("custom_isautomated"))

        if already:
            print(f"  [SKIP]  C{case_id:<10} '{title}'  (already automated)")
            skipped += 1
            continue

        try:
            result = update_case_automated(case_id)
            if result.get("custom_isautomated"):
                print(f"  [OK]    C{case_id:<10} '{title}'  → Is Automated = True")
                updated += 1
            else:
                print(f"  [WARN]  C{case_id:<10} '{title}'  – flag not confirmed in response")
                updated += 1
            time.sleep(0.2)   # polite rate-limiting
        except requests.HTTPError as e:
            print(f"  [FAIL]  C{case_id:<10} '{title}'  – {e}")
            failed += 1

    print(f"\n  Result: {updated} updated  |  {skipped} already done  |  {failed} failed  (total={total})")
    return updated, skipped, failed


def main():
    print("=" * 64)
    print("  TestRail – Mark Sections as 'Is Automated'")
    print(f"  Project : Ultriva (ID={PROJECT_ID})")
    print(f"  Suite   : AdminModule (ID={SUITE_ID})")
    print("=" * 64)

    grand_updated = 0
    grand_skipped = 0
    grand_failed  = 0

    for section_id, label in TARGET_SECTIONS:
        u, s, f = process_section(section_id, label)
        grand_updated += u
        grand_skipped += s
        grand_failed  += f

    print(f"\n{'═'*64}")
    print("  GRAND TOTALS")
    print(f"{'═'*64}")
    print(f"  Updated (newly marked)  : {grand_updated}")
    print(f"  Skipped (already done)  : {grand_skipped}")
    print(f"  Failed                  : {grand_failed}")
    print(f"  Total processed         : {grand_updated + grand_skipped + grand_failed}")
    print("=" * 64)


if __name__ == "__main__":
    main()
