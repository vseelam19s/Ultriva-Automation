"""
ULT-10425 | Add TestRail Cases — Integration Panel BU Filter Persistence & Label Rename

Suite  : S7352  (Enhancements cases)
Folder : Enhancements cases (S7352) → Home page changes  (created if missing)

Run:
    cd qa_automation
    python "JIRA Tickets/Enhancements/ULT-10425_add_testrail_cases.py"
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from utils.testrail_client import TestRailClient

SUITE_ID            = 7352          # S7352 — Enhancements cases
SUBFOLDER_NAME      = "Home page changes"
JIRA_REF            = "ULT-10425"

# ── Test case definitions ─────────────────────────────────────────────────────
TEST_CASES = [
    {
        "title": "TC-01: Integration Panel label reads 'Plant and Associated Workcenters'",
        "custom_preconds": (
            "User is logged in as buyeruser.\n"
            "Plant Home Page is accessible at https://engineering.ultrivalms.com/qals1011"
        ),
        "custom_steps": (
            "1. Navigate to the Plant Home Page.\n"
            "2. Locate the Integration Panel filter options."
        ),
        "custom_expected": (
            "The filter shows 'Plant and Associated Workcenters'.\n"
            "The old label 'All Business Units' is NOT present anywhere on the page."
        ),
        "refs": JIRA_REF,
        "priority_id": 1,   # Critical
    },
    {
        "title": "TC-02: 'Only this BU' filter option is still present after rename",
        "custom_preconds": (
            "User is logged in as buyeruser.\n"
            "Plant Home Page is accessible."
        ),
        "custom_steps": (
            "1. Navigate to the Plant Home Page.\n"
            "2. Locate the Integration Panel filter options."
        ),
        "custom_expected": (
            "Both filter options are displayed:\n"
            "  - 'Plant and Associated Workcenters'\n"
            "  - 'Only this BU'"
        ),
        "refs": JIRA_REF,
        "priority_id": 1,   # Critical
    },
    {
        "title": "TC-03: 'Plant and Associated Workcenters' filter persists after navigation",
        "custom_preconds": (
            "User is logged in as buyeruser.\n"
            "Integration Panel is visible on the Plant Home Page."
        ),
        "custom_steps": (
            "1. Navigate to the Plant Home Page.\n"
            "2. Click 'Plant and Associated Workcenters' in the Integration Panel filter.\n"
            "3. Confirm the panel updates to show all workcenter data.\n"
            "4. Navigate away to any other page.\n"
            "5. Return to the Plant Home Page."
        ),
        "custom_expected": (
            "'Plant and Associated Workcenters' is still selected (pre-highlighted/active).\n"
            "The Integration Panel displays data for all workcenters without user interaction."
        ),
        "refs": JIRA_REF,
        "priority_id": 1,   # Critical
    },
    {
        "title": "TC-04: 'Only this BU' filter persists after navigation",
        "custom_preconds": (
            "User previously selected 'Plant and Associated Workcenters'.\n"
            "User is still logged in."
        ),
        "custom_steps": (
            "1. Navigate to the Plant Home Page.\n"
            "2. Click 'Only this BU' in the Integration Panel filter.\n"
            "3. Navigate away to any other page.\n"
            "4. Return to the Plant Home Page."
        ),
        "custom_expected": (
            "'Only this BU' is still the active filter on return.\n"
            "The Integration Panel shows data for this BU only."
        ),
        "refs": JIRA_REF,
        "priority_id": 2,   # High
    },
    {
        "title": "TC-05: Default filter is 'Only this BU' for a first-time user",
        "custom_preconds": (
            "A user account with no prior Integration Panel preference is used.\n"
            "User logs in fresh (no stored preference)."
        ),
        "custom_steps": (
            "1. Log in with a user that has never selected a filter.\n"
            "2. Navigate to the Plant Home Page.\n"
            "3. Observe the active filter in the Integration Panel — do NOT click anything."
        ),
        "custom_expected": (
            "'Only this BU' is the active/pre-selected filter by default.\n"
            "No error or blank state is shown."
        ),
        "refs": JIRA_REF,
        "priority_id": 2,   # High
    },
    {
        "title": "TC-06: Filter preference persists after page reload (F5)",
        "custom_preconds": (
            "User is logged in as buyeruser.\n"
            "User is on the Plant Home Page."
        ),
        "custom_steps": (
            "1. Navigate to the Plant Home Page.\n"
            "2. Click 'Plant and Associated Workcenters' filter.\n"
            "3. Reload the page (F5 or browser refresh).\n"
            "4. Observe the active filter after reload."
        ),
        "custom_expected": (
            "'Plant and Associated Workcenters' remains selected after the page reload.\n"
            "Panel data reflects the correct filter without any user re-selection."
        ),
        "refs": JIRA_REF,
        "priority_id": 3,   # Medium
    },
]

# ── Helper ────────────────────────────────────────────────────────────────────

def find_section(sections: list, name: str) -> dict | None:
    """Return the first section whose name matches (case-insensitive)."""
    name_lower = name.lower()
    return next((s for s in sections if s.get("name", "").lower() == name_lower), None)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    tr = TestRailClient()

    # 1. Fetch all sections in S7352
    print(f"\n── Fetching sections in suite S{SUITE_ID} ──────────────────────────────")
    sections = tr.get_sections(suite_id=SUITE_ID)

    # 2. Find or create the "Home page changes" subfolder
    print(f"\n── Looking for section '{SUBFOLDER_NAME}' ────────────────────────────────")
    target_section = find_section(sections, SUBFOLDER_NAME)

    if target_section:
        section_id = target_section["id"]
        print(f"   Found existing section ID {section_id}: '{target_section['name']}'")
    else:
        print(f"   Not found — creating '{SUBFOLDER_NAME}' in S{SUITE_ID} ...")
        new_section = tr.add_section(
            name=SUBFOLDER_NAME,
            suite_id=SUITE_ID,
        )
        section_id = new_section["id"]
        print(f"   Created section ID {section_id}")

    # 3. Add test cases under the section
    print(f"\n── Adding {len(TEST_CASES)} test case(s) to section {section_id} ─────────────")
    created_ids = []
    for tc in TEST_CASES:
        case = tr.add_case(
            section_id      = section_id,
            title           = tc["title"],
            custom_preconds = tc.get("custom_preconds", ""),
            custom_steps    = tc.get("custom_steps", ""),
            custom_expected = tc.get("custom_expected", ""),
            refs            = tc.get("refs", ""),
            priority_id     = tc.get("priority_id", 2),
        )
        created_ids.append(case["id"])

    # 4. Summary
    print("\n── Summary ──────────────────────────────────────────────────────────────")
    print(f"  Suite       : S{SUITE_ID}")
    print(f"  Section     : {SUBFOLDER_NAME} (ID {section_id})")
    print(f"  Cases added : {len(created_ids)}")
    for cid in created_ids:
        print(f"    C{cid}  →  https://upland.testrail.com/index.php?/cases/view/{cid}")
    print(f"\n  TestRail suite URL:")
    print(f"  https://upland.testrail.com/index.php?/suites/view/{SUITE_ID}")


if __name__ == "__main__":
    main()
