"""
Script: mark_admin_sections_automated.py
Purpose: Mark all test cases in the following AdminModule sections as "Is Automated":
  - Admin > Groups        (92085)
  - Admin > User Group    (92086)
  - Admin > Supplier      (92157) + all sub-folders:
      - Supplier User     (92158)
      - Supplier Item     (92160)
      - Calendar          (92162)

Project  : Ultriva (ID=15)
Suite    : AdminModule (ID=2571)
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

# Sections to process: (section_id, label)
TARGET_SECTIONS = [
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
        batch = data.get("cases", [])
        cases.extend(batch)
        if len(batch) < limit:
            break
        offset += limit
    return cases


def update_case_automated(case_id):
    return api_post(f"update_case/{case_id}", {"custom_isautomated": True})


def process_section(section_id, label):
    print(f"\n{'─'*60}")
    print(f"  Section : {label}  (ID={section_id})")
    print(f"{'─'*60}")

    cases = get_cases_for_section(section_id)
    if not cases:
        print("  (no test cases found)")
        return []

    results = []
    for c in cases:
        case_id = c["id"]
        title   = c["title"]
        already = bool(c.get("custom_isautomated"))

        if already:
            print(f"  [SKIP]   C{case_id}  '{title}'")
            results.append({"section": label, "case_id": case_id, "title": title, "status": "already"})
            continue

        try:
            updated = update_case_automated(case_id)
            flag    = bool(updated.get("custom_isautomated"))
            mark    = "[OK]  " if flag else "[WARN]"
            print(f"  {mark}  C{case_id}  '{title}'  → Is Automated = {flag}")
            results.append({"section": label, "case_id": case_id, "title": title,
                            "status": "updated" if flag else "warn"})
        except Exception as e:
            print(f"  [ERROR]  C{case_id}  '{title}'  → {e}")
            results.append({"section": label, "case_id": case_id, "title": title,
                            "status": "error", "error": str(e)})

        time.sleep(0.2)

    return results


def main():
    print("=" * 60)
    print("TestRail: Mark Sections as 'Is Automated'")
    print(f"  Project : Ultriva (ID={PROJECT_ID})")
    print(f"  Suite   : AdminModule (ID={SUITE_ID})")
    print(f"  Targets : {len(TARGET_SECTIONS)} sections")
    print("=" * 60)

    all_results = []
    for section_id, label in TARGET_SECTIONS:
        section_results = process_section(section_id, label)
        all_results.extend(section_results)

    # ── Summary ───────────────────────────────────────────────────────────────
    updated = [r for r in all_results if r["status"] == "updated"]
    already = [r for r in all_results if r["status"] == "already"]
    errors  = [r for r in all_results if r["status"] == "error"]

    print(f"\n{'='*60}")
    print("FINAL SUMMARY")
    print(f"{'='*60}")
    print(f"  Total cases processed : {len(all_results)}")
    print(f"  Newly marked          : {len(updated)}")
    print(f"  Already automated     : {len(already)}")
    print(f"  Errors                : {len(errors)}")

    if all_results:
        print(f"\n{'─'*60}")
        print("  DETAIL BY SECTION:")
        from collections import defaultdict
        by_section = defaultdict(list)
        for r in all_results:
            by_section[r["section"]].append(r)
        for sec, rows in by_section.items():
            ok  = sum(1 for r in rows if r["status"] == "updated")
            sk  = sum(1 for r in rows if r["status"] == "already")
            err = sum(1 for r in rows if r["status"] == "error")
            print(f"  {sec}")
            print(f"    {len(rows)} cases  |  {ok} updated  |  {sk} skipped  |  {err} errors")
            for r in rows:
                tag = "✓" if r["status"] in ("updated","already") else "✗"
                print(f"      {tag} C{r['case_id']}  {r['title']}")

    print(f"\n{'='*60}")
    print("View in TestRail:")
    print("  https://upland.testrail.com/index.php?/suites/view/2571")
    print("=" * 60)


if __name__ == "__main__":
    main()
