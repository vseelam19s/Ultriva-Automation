"""
ULT-10425 | Test Scenarios — Plant Home Page Integration Panel: Remember Last BU Filter
"""

SCENARIOS = [
    {
        "id": "TS-01",
        "title": "Label reads 'Plant and Associated Workcenters' (not 'All Business Units')",
        "preconditions": "User is logged in; Plant Home Page is accessible.",
        "steps": [
            "Log in as buyeruser.",
            "Navigate to the Plant Home Page.",
            "Locate the Integration Panel filter.",
            "Read the label of the 'All Business Units' option.",
        ],
        "expected": (
            "The option is labelled 'Plant and Associated Workcenters'. "
            "No element with text 'All Business Units' is present."
        ),
        "priority": "Critical",
    },
    {
        "id": "TS-02",
        "title": "Selecting 'Plant and Associated Workcenters' is remembered on next visit",
        "preconditions": "User is logged in; Integration Panel is visible.",
        "steps": [
            "Navigate to the Plant Home Page.",
            "Click 'Plant and Associated Workcenters' in the Integration Panel filter.",
            "Navigate away (e.g., open another menu item).",
            "Return to the Plant Home Page.",
            "Observe which filter option is active.",
        ],
        "expected": (
            "'Plant and Associated Workcenters' is pre-selected; "
            "the Integration Panel displays data for all workcenters."
        ),
        "priority": "Critical",
    },
    {
        "id": "TS-03",
        "title": "Selecting 'Only this BU' is remembered on next visit",
        "preconditions": "User previously selected 'Plant and Associated Workcenters'.",
        "steps": [
            "Navigate to the Plant Home Page.",
            "Click 'Only this BU' in the Integration Panel filter.",
            "Navigate away and return to the Plant Home Page.",
            "Observe which filter option is active.",
        ],
        "expected": (
            "'Only this BU' is pre-selected; "
            "the Integration Panel shows data for this BU only."
        ),
        "priority": "High",
    },
    {
        "id": "TS-04",
        "title": "Default filter is 'Only this BU' for a new / first-time user",
        "preconditions": "A user account with no prior Integration Panel preference exists.",
        "steps": [
            "Log in with a fresh user account.",
            "Navigate to the Plant Home Page.",
            "Observe which filter option is active without making any selection.",
        ],
        "expected": (
            "'Only this BU' is active by default. "
            "No earlier preference is applied."
        ),
        "priority": "High",
    },
    {
        "id": "TS-05",
        "title": "Filter preference persists after browser session restart",
        "preconditions": "User has previously selected 'Plant and Associated Workcenters'.",
        "steps": [
            "Select 'Plant and Associated Workcenters' and confirm the panel updates.",
            "Close the browser completely.",
            "Reopen the browser and navigate to the QA site.",
            "Log in as the same user.",
            "Navigate to the Plant Home Page.",
            "Observe the active filter.",
        ],
        "expected": (
            "'Plant and Associated Workcenters' is still active after the browser restart, "
            "confirming the preference is stored server-side or in a persistent cookie."
        ),
        "priority": "Medium",
    },
    {
        "id": "TS-06",
        "title": "Two users have independent filter preferences",
        "preconditions": "Two distinct user accounts are available in the QA environment.",
        "steps": [
            "Log in as User A; select 'Plant and Associated Workcenters'; log out.",
            "Log in as User B; select 'Only this BU'; log out.",
            "Log in as User A again; navigate to the Plant Home Page.",
            "Observe User A's active filter.",
            "Log out; log in as User B; navigate to the Plant Home Page.",
            "Observe User B's active filter.",
        ],
        "expected": (
            "User A sees 'Plant and Associated Workcenters'; "
            "User B sees 'Only this BU'. Preferences are stored per user."
        ),
        "priority": "Medium",
    },
]


if __name__ == "__main__":
    for s in SCENARIOS:
        print(f"\n[{s['id']}] {s['title']}  (Priority: {s['priority']})")
        print("  Pre : " + s["preconditions"])
        for i, step in enumerate(s["steps"], 1):
            print(f"  {i}. {step}")
        print("  Exp : " + s["expected"])
