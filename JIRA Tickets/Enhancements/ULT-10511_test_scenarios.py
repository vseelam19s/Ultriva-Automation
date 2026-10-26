"""
ULT-10511 | Test Scenarios — Export All Scheduled Jobs Report
"""

SCENARIOS = [
    {
        "id": "TS-01",
        "title": "Export all scheduled jobs",
        "steps": [
            "Log in as an authorised user",
            "Navigate to Scheduled Jobs export page",
            "Click 'Export All' button",
            "Verify report is triggered",
        ],
        "expected": "Report generation starts successfully",
    },
    {
        "id": "TS-02",
        "title": "Report format matches reference template",
        "steps": [
            "Trigger export of all scheduled jobs",
            "Open downloaded file",
            "Compare column headers with 'Remaining production hours' export",
        ],
        "expected": "Headers and row format match reference exactly",
    },
    {
        "id": "TS-03",
        "title": "Report runs as background job (no timeout)",
        "steps": [
            "Trigger export with large dataset",
            "Confirm UI does not freeze or timeout",
            "Wait for background job to complete",
            "Verify download link appears",
        ],
        "expected": "Report completes in background; UI stays responsive",
    },
    {
        "id": "TS-04",
        "title": "Report includes all scheduled jobs across all dates",
        "steps": [
            "Note total count of scheduled jobs in the system",
            "Trigger export",
            "Open report and count rows",
        ],
        "expected": "Row count matches total scheduled jobs in system",
    },
    {
        "id": "TS-05",
        "title": "Column headers and data alignment are correct",
        "steps": [
            "Open exported file",
            "Validate each column header",
            "Check data in each column maps to correct field",
        ],
        "expected": "All columns correctly labelled and data is aligned",
    },
    {
        "id": "TS-06",
        "title": "Downloaded file is accessible after job completes",
        "steps": [
            "Trigger export",
            "Wait for completion notification",
            "Click download link",
            "Verify file opens without errors",
        ],
        "expected": "File downloads and opens successfully",
    },
    {
        "id": "TS-07",
        "title": "Empty state — no scheduled jobs",
        "steps": [
            "Ensure no scheduled jobs exist in the system",
            "Trigger export",
        ],
        "expected": "Report generates with headers only, no data rows; no error shown",
    },
    {
        "id": "TS-08",
        "title": "Large dataset export completes without error",
        "steps": [
            "Load system with 1000+ scheduled job records",
            "Trigger export",
            "Verify job finishes and file is valid",
        ],
        "expected": "Export succeeds with all records present in file",
    },
    {
        "id": "TS-09",
        "title": "Unauthorised user cannot trigger export",
        "steps": [
            "Log in as a user without export permissions",
            "Navigate to Scheduled Jobs export page",
            "Attempt to trigger export",
        ],
        "expected": "Access denied; appropriate error message displayed",
    },
    {
        "id": "TS-10",
        "title": "Export is idempotent",
        "steps": [
            "Run export twice without changing any data",
            "Compare output files",
        ],
        "expected": "Both files contain identical data",
    },
]
