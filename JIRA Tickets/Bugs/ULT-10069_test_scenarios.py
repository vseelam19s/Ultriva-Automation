"""
ULT-10069 | Scenarios — Kanban Loop Design Not Processing
Bug: KLD batch job stays at 'Created' when B2B exchange type is HTTP after Item Data Load.
"""

SCENARIOS = [
    {
        "id": "TS-01",
        "title": "KLD processes after Item Data Load sets HTTP exchange type",
        "priority": "Critical",
        "steps": [
            "Run Item Data Load to set B2B exchange type to HTTP",
            "Trigger Kanban Loop Design",
            "Open Integration Batch Job Status → Item Sync",
        ],
        "expected": "KLD batch job transitions from Created to Completed",
    },
    {
        "id": "TS-02",
        "title": "Batch job status transitions: Created → InProgress → Completed",
        "priority": "Critical",
        "steps": [
            "Trigger Kanban Loop Design",
            "Poll Batch Job Status screen for the KLD Item Sync record",
        ],
        "expected": "Status progresses through Created → InProgress → Completed",
    },
    {
        "id": "TS-03",
        "title": "Item Data Load continues to process (no regression)",
        "priority": "High",
        "steps": [
            "Run Item Data Load",
            "Check Batch Job Status for Item Data Load entries",
        ],
        "expected": "Item Data Load entries reach Completed status",
    },
    {
        "id": "TS-04",
        "title": "KLD processes when exchange type is HTTPS",
        "priority": "High",
        "steps": [
            "Ensure B2B process record exchange type is HTTPS",
            "Trigger Kanban Loop Design",
            "Check Batch Job Status screen",
        ],
        "expected": "KLD batch job completes successfully",
    },
    {
        "id": "TS-05",
        "title": "Multiple KLD batch jobs with HTTP exchange type all process",
        "priority": "Medium",
        "steps": [
            "Run Item Data Load multiple times to create multiple HTTP B2B records",
            "Trigger Kanban Loop Design for each",
            "Check Batch Job Status for all KLD Item Sync records",
        ],
        "expected": "All KLD batch jobs reach Completed status",
    },
    {
        "id": "TS-06",
        "title": "Batch Job Status screen shows correct KLD Item Sync status",
        "priority": "Medium",
        "steps": [
            "Trigger KLD",
            "Navigate to Integration → Batch Job Status",
            "Filter by Item Sync",
        ],
        "expected": "KLD Item Sync record visible with accurate status",
    },
]
