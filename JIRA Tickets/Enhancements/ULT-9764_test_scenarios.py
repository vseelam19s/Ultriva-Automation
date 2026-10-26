"""
ULT-9764 | Test Scenarios — Add Task Name Filter to Service Monitors Screen

Feature: Task Name filter on Integration Monitor → Errors tab
URL    : https://engineering.ultrivalms.com/QALS1011/SysAdmin/IntgMonitor
Role   : Application $ Administrator (SysAdmin BU)
"""

SCENARIOS = [
    {
        "id": "TS-01",
        "title": "Task Name filter field is visible on the Errors tab",
        "preconditions": "User is logged in as admin. Errors tab is active.",
        "steps": [
            "Navigate to Admin > Integration > Integration Monitor.",
            "Click the 'Errors' tab.",
            "Inspect the filter bar.",
        ],
        "expected": (
            "A 'Task Name' text input field and a 'Go' button are visible beside the Date Range filter."
        ),
        "priority": "Critical",
    },
    {
        "id": "TS-02",
        "title": "Valid exact task name returns only matching records",
        "preconditions": "At least one error record exists with a known task name.",
        "steps": [
            "Navigate to Integration Monitor → Errors tab.",
            "Enter the exact task name (e.g., 'SVC.$batchjob_BSU22ZAQALG') in Task Name field.",
            "Click Go.",
            "Inspect the Name column of every row returned.",
        ],
        "expected": (
            "All rows show the exact task name entered. "
            "The 'Viewing X to Y of Z' count is ≤ unfiltered total."
        ),
        "priority": "Critical",
    },
    {
        "id": "TS-03",
        "title": "Partial / substring task name filters correctly",
        "preconditions": "Error records containing 'sync' in their task name exist.",
        "steps": [
            "Navigate to Integration Monitor → Errors tab.",
            "Enter 'sync' in the Task Name field.",
            "Click Go.",
            "Review the Name column of returned rows.",
        ],
        "expected": (
            "Every returned row has 'sync' in its Name. "
            "Records not containing 'sync' are excluded from results."
        ),
        "priority": "Critical",
    },
    {
        "id": "TS-04",
        "title": "Non-existent task name shows empty / no-results state",
        "preconditions": "User is on the Errors tab.",
        "steps": [
            "Enter 'DOESNOTEXIST_XYZ_999' in the Task Name field.",
            "Click Go.",
            "Observe the results area.",
        ],
        "expected": (
            "No data rows are shown. An appropriate message such as 'No records found' is displayed. "
            "No application error or JavaScript exception occurs."
        ),
        "priority": "High",
    },
    {
        "id": "TS-05",
        "title": "Task Name filter is case-insensitive",
        "preconditions": "Error records containing 'sync' exist.",
        "steps": [
            "Enter 'SYNC' in the Task Name field, click Go. Note the result count.",
            "Clear the field, enter 'sync', click Go. Note the result count.",
            "Clear the field, enter 'Sync', click Go. Note the result count.",
        ],
        "expected": (
            "The result count and records returned are identical for 'SYNC', 'sync', and 'Sync'."
        ),
        "priority": "High",
    },
    {
        "id": "TS-06",
        "title": "Clearing Task Name resets grid to all records for selected date range",
        "preconditions": "Filter was previously set to 'sync'.",
        "steps": [
            "Clear the Task Name field completely.",
            "Click Go.",
            "Observe the total record count in 'Viewing X to Y of Z'.",
        ],
        "expected": (
            "All error records within the selected Date Range are shown "
            "(count matches unfiltered baseline)."
        ),
        "priority": "High",
    },
    {
        "id": "TS-07",
        "title": "Task Name filter combined with Date Range narrows results correctly",
        "preconditions": "User is on the Errors tab with default date range set.",
        "steps": [
            "Select 'Past 7 Days' from the Date Range dropdown.",
            "Enter 'sync' in the Task Name field.",
            "Click Go.",
            "Verify each row's Date falls within Past 7 Days and Name contains 'sync'.",
        ],
        "expected": (
            "Returned records match BOTH the date range and the task name filter. "
            "Records outside the date range or without 'sync' are excluded."
        ),
        "priority": "High",
    },
    {
        "id": "TS-08",
        "title": "Pagination reflects filtered total, not full dataset",
        "preconditions": "Filter 'sync' returns fewer records than the unfiltered set.",
        "steps": [
            "Enter 'sync' in Task Name, click Go.",
            "Read 'Viewing 1 to 200 of <N> | Page 1 of <P>'.",
            "Clear filter, click Go.",
            "Read the same pagination counter.",
        ],
        "expected": (
            "N (filtered) < total unfiltered record count. "
            "Page count P is calculated from filtered N, not the full dataset."
        ),
        "priority": "Medium",
    },
    {
        "id": "TS-09",
        "title": "Go button is required to trigger filter (no auto-search on keystroke)",
        "preconditions": "User is on the Errors tab.",
        "steps": [
            "Note the current result count.",
            "Type 'sync' in the Task Name field but do NOT click Go.",
            "Wait 5 seconds.",
            "Observe the grid.",
        ],
        "expected": (
            "The grid does not update. The results remain unchanged until the user clicks Go."
        ),
        "priority": "Medium",
    },
    {
        "id": "TS-10",
        "title": "Special characters in Task Name handled gracefully",
        "preconditions": "User is on the Errors tab.",
        "steps": [
            "Enter '$' in the Task Name field, click Go.",
            "Enter '<script>' in the Task Name field, click Go.",
            "Observe results and any error messages.",
        ],
        "expected": (
            "No server 500 error. No XSS execution. "
            "Results show matching records or an empty state message."
        ),
        "priority": "Low",
    },
]
