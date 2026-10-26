"""
report_automated_modules.py
Purpose: Query TestRail and report which sections/modules have cases
         marked as "Is Automated" (custom_isautomated = True).

Project  : Ultriva (ID=15)
Run from the qa_automation folder:
    python report_automated_modules.py
"""

import requests
import json
import time
from collections import defaultdict

# ── Config ────────────────────────────────────────────────────────────────────
TESTRAIL_URL = "https://upland.testrail.com/"
EMAIL        = "vseelam@uplandsoftware.com"
API_KEY      = "LR5Bc8syGLl4d.dweMDC-bN9OoDA5pyiO6dKCHlh3"
PROJECT_ID   = 15

AUTH    = (EMAIL, API_KEY)
HEADERS = {"Content-Type": "application/json"}


def api_get(path):
    url  = TESTRAIL_URL + "index.php?/api/v2/" + path
    resp = requests.get(url, headers=HEADERS, auth=AUTH)
    resp.raise_for_status()
    return resp.json()


def get_suites():
    data = api_get(f"get_suites/{PROJECT_ID}")
    if isinstance(data, dict):
        return data.get("suites", list(data.values())[0] if data else [])
    return data


def get_sections(suite_id):
    data = api_get(f"get_sections/{PROJECT_ID}&suite_id={suite_id}")
    return data.get("sections", data) if isinstance(data, dict) else data


def get_cases_for_suite(suite_id):
    """Fetch ALL cases in a suite with pagination."""
    cases  = []
    offset = 0
    limit  = 250
    while True:
        data  = api_get(
            f"get_cases/{PROJECT_ID}"
            f"&suite_id={suite_id}"
            f"&limit={limit}&offset={offset}"
        )
        # API v2 may return list or dict with 'cases' key
        if isinstance(data, list):
            batch = data
        else:
            batch = data.get("cases", [])
        cases.extend(batch)
        if len(batch) < limit:
            break
        offset += limit
        time.sleep(0.3)   # be polite to the API
    return cases


def build_section_map(sections):
    """Return {section_id: full_path_string}."""
    id_to_section = {s["id"]: s for s in sections}
    cache = {}

    def full_name(section_id):
        if section_id in cache:
            return cache[section_id]
        s = id_to_section.get(section_id)
        if not s:
            return f"(section {section_id})"
        parent_id = s.get("parent_id")
        name      = s.get("name", "?")
        if parent_id:
            path = full_name(parent_id) + " > " + name
        else:
            path = name
        cache[section_id] = path
        return path

    for s in sections:
        full_name(s["id"])
    return cache


def main():
    print("=" * 70)
    print("  TestRail – 'Is Automated' Coverage Report")
    print(f"  Project ID : {PROJECT_ID}")
    print("=" * 70)

    # 1. Get all suites
    suites = get_suites()
    print(f"\nFound {len(suites)} suite(s):")
    for s in suites:
        print(f"  S{s['id']}  {s.get('name', '')}")

    grand_total    = 0
    grand_automated = 0

    suite_summaries = []

    for suite in suites:
        suite_id   = suite["id"]
        suite_name = suite.get("name", f"Suite {suite_id}")
        print(f"\n{'═'*70}")
        print(f"  Suite : {suite_name}  (S{suite_id})")
        print(f"{'═'*70}")

        # Build section path map
        try:
            sections  = get_sections(suite_id)
            sec_map   = build_section_map(sections)
        except Exception as e:
            print(f"  [WARN] Could not fetch sections: {e}")
            sec_map = {}

        # Fetch all cases
        try:
            cases = get_cases_for_suite(suite_id)
        except Exception as e:
            print(f"  [FAIL] Could not fetch cases: {e}")
            continue

        # Group by section
        section_stats = defaultdict(lambda: {"total": 0, "automated": 0, "cases": []})
        for c in cases:
            sec_id = c.get("section_id")
            sec_path = sec_map.get(sec_id, f"(section {sec_id})")
            section_stats[sec_path]["total"] += 1
            if c.get("custom_isautomated"):
                section_stats[sec_path]["automated"] += 1
                section_stats[sec_path]["cases"].append(f"C{c['id']} – {c['title']}")

        suite_total     = len(cases)
        suite_automated = sum(1 for c in cases if c.get("custom_isautomated"))
        grand_total     += suite_total
        grand_automated += suite_automated

        # Print sections that have at least one automated case
        automated_sections = {
            path: stats
            for path, stats in sorted(section_stats.items())
            if stats["automated"] > 0
        }

        if not automated_sections:
            print("  (no cases marked Is Automated in this suite)")
        else:
            print(f"\n  Sections with 'Is Automated' cases ({len(automated_sections)}):\n")
            for path, stats in sorted(automated_sections.items()):
                pct = (stats["automated"] / stats["total"] * 100) if stats["total"] else 0
                print(f"  {'✔':2} {path}")
                print(f"      Automated: {stats['automated']}/{stats['total']}  ({pct:.0f}%)")

        print(f"\n  Suite totals : {suite_automated} automated / {suite_total} total")
        suite_summaries.append({
            "suite": suite_name,
            "automated": suite_automated,
            "total": suite_total,
            "sections": automated_sections,
        })

    # ── Grand Summary ─────────────────────────────────────────────────────────
    print(f"\n{'═'*70}")
    print("  GRAND SUMMARY  –  Modules with 'Is Automated' coverage")
    print(f"{'═'*70}")
    for ss in suite_summaries:
        pct = (ss["automated"] / ss["total"] * 100) if ss["total"] else 0
        print(f"\n  [{ss['suite']}]  {ss['automated']}/{ss['total']}  ({pct:.0f}% automated)")
        for path in sorted(ss["sections"].keys()):
            stats = ss["sections"][path]
            print(f"      • {path}  ({stats['automated']}/{stats['total']})")

    overall_pct = (grand_automated / grand_total * 100) if grand_total else 0
    print(f"\n  *** OVERALL: {grand_automated} automated / {grand_total} total = {overall_pct:.1f}% ***")
    print("=" * 70)


if __name__ == "__main__":
    main()
