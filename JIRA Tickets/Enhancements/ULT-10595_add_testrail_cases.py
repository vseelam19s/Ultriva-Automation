"""
ULT-10595 | Add TestRail Cases — Fix RYG Color Code

Suite  : S7352  (Enhancements cases)
Folder : Enhancements cases (S7352) → fixcolorcode (created if missing)

Run:
    cd qa_automation
    python "JIRA Tickets/Enhancements/ULT-10595_add_testrail_cases.py"
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from utils.testrail_client import TestRailClient

SUITE_ID       = 7352
SUBFOLDER_NAME = "fixcolorcode"
JIRA_REF       = "ULT-10595"

TEST_CASES = [
    {
        "title": "TC-01: User can open the Fix RYG Color Code screen",
        "custom_preconds": (
            "User is logged in as buyeruser.\n"
            "The QA site is available at https://engineering.ultrivalms.com/qals1011"
        ),
        "custom_steps": (
            "1. Navigate to the application home page.\n"
            "2. Open the Fix RYG Color Code screen or the feature entry point for this ticket.\n"
            "3. Confirm the screen loads without errors."
        ),
        "custom_expected": (
            "The Fix RYG Color Code screen is accessible.\n"
            "The page shows all expected fields and controls for the operation."
        ),
        "refs": JIRA_REF,
        "priority_id": 1,
    },
    {
        "title": "TC-02: Valid item update changes the color code successfully",
        "custom_preconds": (
            "A valid item record exists in the system.\n"
            "The user is on the Fix RYG Color Code screen."
        ),
        "custom_steps": (
            "1. Enter a valid Item No or Item GID.\n"
            "2. Submit the request to update the color code.\n"
            "3. Review the returned status information."
        ),
        "custom_expected": (
            "The update completes successfully.\n"
            "Status Code shows DONE.\n"
            "Status Message shows a success message such as 'Color code updated'."
        ),
        "refs": JIRA_REF,
        "priority_id": 1,
    },
    {
        "title": "TC-03: Result row displays Item No, Item GID, Status Code, and Status Message",
        "custom_preconds": (
            "The feature is open and a valid update request is submitted."
        ),
        "custom_steps": (
            "1. Submit a valid fix request.\n"
            "2. Review the result row returned by the screen."
        ),
        "custom_expected": (
            "The result row includes Item No, Item GID, Status Code, and Status Message.\n"
            "The status message reflects the successful update and the result is visible to the user."
        ),
        "refs": JIRA_REF,
        "priority_id": 1,
    },
    {
        "title": "TC-04: Invalid Item No or Item GID is rejected with a clear error",
        "custom_preconds": (
            "The user is logged in and the Fix RYG Color Code screen is open."
        ),
        "custom_steps": (
            "1. Enter an invalid, missing, or mismatched Item No or Item GID.\n"
            "2. Submit the request."
        ),
        "custom_expected": (
            "The system rejects the update.\n"
            "A clear validation or error message is shown.\n"
            "No invalid data is saved or applied."
        ),
        "refs": JIRA_REF,
        "priority_id": 2,
    },
    {
        "title": "TC-05: No-match scenario is handled gracefully without a crash",
        "custom_preconds": (
            "The user is on the Fix RYG Color Code screen.\n"
            "A valid item value does not exist in the current data set."
        ),
        "custom_steps": (
            "1. Enter an Item No or Item GID that has no matching record.\n"
            "2. Submit the request."
        ),
        "custom_expected": (
            "The feature does not crash.\n"
            "A controlled failure or not-found message is shown.\n"
            "The system remains usable for subsequent valid requests."
        ),
        "refs": JIRA_REF,
        "priority_id": 2,
    },
    {
        "title": "TC-06: Refresh or navigation does not corrupt the fix result state",
        "custom_preconds": (
            "A valid update request has already been processed."
        ),
        "custom_steps": (
            "1. Submit a valid color code update.\n"
            "2. Refresh the page or navigate away and return.\n"
            "3. Review the displayed status and results."
        ),
        "custom_expected": (
            "The page remains stable after refresh or navigation.\n"
            "The result values are consistent and the feature is still usable."
        ),
        "refs": JIRA_REF,
        "priority_id": 2,
    },
    {
        "title": "TC-07: Adjacent RYG logic remains unaffected by the fix",
        "custom_preconds": (
            "The user is logged in and relevant related screens or data are available."
        ),
        "custom_steps": (
            "1. Perform a successful Fix RYG Color Code action.\n"
            "2. Navigate to a related screen or report that uses color rules.\n"
            "3. Verify standard RYG behavior remains unchanged."
        ),
        "custom_expected": (
            "The fix does not introduce regression in existing RYG-related behavior.\n"
            "Associated screens continue to work as expected."
        ),
        "refs": JIRA_REF,
        "priority_id": 2,
    },
]


def find_section(sections: list, name: str) -> dict | None:
    name_lower = name.lower()
    return next((s for s in sections if s.get("name", "").lower() == name_lower), None)


def main():
    tr = TestRailClient()

    print(f"\n── Fetching sections in suite S{SUITE_ID} ──────────────────────────────")
    sections = tr.get_sections(suite_id=SUITE_ID)

    print(f"\n── Looking for section '{SUBFOLDER_NAME}' ───────────────────────────────")
    target_section = find_section(sections, SUBFOLDER_NAME)

    if target_section:
        section_id = target_section["id"]
        print(f"   Found existing section ID {section_id}: '{target_section['name']}'")
    else:
        print(f"   Not found — creating '{SUBFOLDER_NAME}' in S{SUITE_ID} ...")
        new_section = tr.add_section(name=SUBFOLDER_NAME, suite_id=SUITE_ID)
        section_id = new_section["id"]
        print(f"   Created section ID {section_id}")

    print(f"\n── Adding {len(TEST_CASES)} test case(s) to section {section_id} ─────────────")
    created_ids = []
    for tc in TEST_CASES:
        case = tr.add_case(
            section_id=section_id,
            title=tc["title"],
            custom_preconds=tc.get("custom_preconds", ""),
            custom_steps=tc.get("custom_steps", ""),
            custom_expected=tc.get("custom_expected", ""),
            refs=tc.get("refs", ""),
            priority_id=tc.get("priority_id", 2),
        )
        created_ids.append(case["id"])

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
