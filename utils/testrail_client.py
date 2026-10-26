"""
TestRail client utility for QA Automation.

Usage:
    from utils.testrail_client import TestRailClient

    tr = TestRailClient()

    # List test cases for the configured project
    cases = tr.get_cases()

    # Get a specific case
    case = tr.get_case(case_id=1001)

    # Create a new test run (auto-creates if TESTRAIL_RUN_ID is None)
    run_id = tr.get_or_create_run()

    # Push a single result
    tr.add_result(run_id=run_id, case_id=1001, status="passed", comment="All assertions OK")

    # Push results for an entire pytest session (called from conftest fixture)
    tr.push_results(run_id, results_list)

    # Close a run after all results are submitted
    tr.close_run(run_id)

TestRail status codes:
    1 = Passed | 2 = Blocked | 3 = Untested | 4 = Retest | 5 = Failed
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from testrail_api import TestRailAPI
from config.config import (
    TESTRAIL_URL,
    TESTRAIL_EMAIL,
    TESTRAIL_API_KEY,
    TESTRAIL_PROJECT_ID,
    TESTRAIL_SUITE_ID,
    TESTRAIL_RUN_ID,
    TESTRAIL_AUTO_CREATE_RUN,
    TESTRAIL_RUN_NAME,
    TESTRAIL_ENABLED,
)

# ── Status mapping ────────────────────────────────────────────────────────────
STATUS_MAP = {
    "passed":  1,
    "pass":    1,
    "blocked": 2,
    "skip":    3,   # untested / skipped
    "retest":  4,
    "failed":  5,
    "fail":    5,
    "error":   5,
}


class TestRailClient:
    """Thin wrapper around the testrail-api library configured from config.py."""

    def __init__(self):
        if not TESTRAIL_ENABLED:
            print("[TestRail] Integration disabled (TESTRAIL_ENABLED=False). "
                  "Set it to True in config.py once credentials are ready.")
            self._client = None
            return
        self._client = self._connect()

    # ── Connection ────────────────────────────────────────────────────────────

    def _connect(self) -> TestRailAPI:
        if not TESTRAIL_API_KEY:
            raise ValueError(
                "TESTRAIL_API_KEY is not set.\n"
                "Set it via the TESTRAIL_API_KEY environment variable or in config.py."
            )
        client = TestRailAPI(
            url=TESTRAIL_URL,
            email=TESTRAIL_EMAIL,
            password=TESTRAIL_API_KEY,
        )
        print(f"[TestRail] Connected to {TESTRAIL_URL} as {TESTRAIL_EMAIL}")
        return client

    def _require_client(self):
        if self._client is None:
            raise RuntimeError(
                "TestRail client is not initialised. "
                "Set TESTRAIL_ENABLED=True and provide valid credentials."
            )

    # ── Test Cases ───────────────────────────────────────────────────────────

    def get_cases(self, suite_id: int = None, section_id: int = None) -> list:
        """
        Return all test cases for the configured project.

        Args:
            suite_id:   Override TESTRAIL_SUITE_ID for this call.
            section_id: Restrict to a specific section/folder.

        Returns:
            List of case dicts from the TestRail API.
        """
        self._require_client()
        sid = suite_id or TESTRAIL_SUITE_ID
        params = {}
        if sid:
            params["suite_id"] = sid
        if section_id:
            params["section_id"] = section_id

        cases = self._client.cases.get_cases(
            project_id=TESTRAIL_PROJECT_ID, **params
        )
        case_list = cases.get("cases", cases) if isinstance(cases, dict) else cases
        print(f"[TestRail] Retrieved {len(case_list)} test case(s) "
              f"from project {TESTRAIL_PROJECT_ID}")
        for c in case_list:
            print(f"  C{c['id']}  {c.get('title', '')}")
        return case_list

    def get_case(self, case_id: int) -> dict:
        """Fetch a single test case by its ID (C-prefix in TestRail UI)."""
        self._require_client()
        case = self._client.cases.get_case(case_id=case_id)
        print(f"[TestRail] Case C{case['id']}: {case.get('title', '')}")
        return case

    def get_test(self, test_id: int) -> dict:
        """
        Fetch a single test *instance* by its ID (T-prefix in TestRail UI).

        Tests live inside a test run.  They are created automatically when a
        run is started and reference the underlying case via 'case_id'.
        Use get_case() to fetch the reusable case definition instead.
        """
        self._require_client()
        test = self._client.tests.get_test(test_id=test_id)
        print(
            f"[TestRail] Test T{test['id']}: {test.get('title', '')} "
            f"| Case C{test.get('case_id', '?')} "
            f"| Run R{test.get('run_id', '?')} "
            f"| Status: {test.get('status_id', '?')}"
        )
        return test

    def get_sections(self, suite_id: int = None) -> list:
        """Return all sections (folders) for the project."""
        self._require_client()
        sid = suite_id or TESTRAIL_SUITE_ID
        params = {"suite_id": sid} if sid else {}
        sections = self._client.sections.get_sections(
            project_id=TESTRAIL_PROJECT_ID, **params
        )
        return sections.get("sections", sections) if isinstance(sections, dict) else sections

    def get_suites(self) -> list:
        """Return all suites for the project (multi-suite projects only)."""
        self._require_client()
        result = self._client.suites.get_suites(project_id=TESTRAIL_PROJECT_ID)
        suites = result.get("suites", result) if isinstance(result, dict) else result
        print(f"[TestRail] Suites for project {TESTRAIL_PROJECT_ID}:")
        for s in suites:
            print(f"  S{s['id']}  {s.get('name', '')}")
        return suites

    # ── Test Runs ─────────────────────────────────────────────────────────────

    def get_runs(self) -> list:
        """Return all active test runs for the project."""
        self._require_client()
        result = self._client.runs.get_runs(project_id=TESTRAIL_PROJECT_ID)
        runs = result.get("runs", result) if isinstance(result, dict) else result
        print(f"[TestRail] {len(runs)} active run(s) in project {TESTRAIL_PROJECT_ID}")
        for r in runs:
            print(f"  R{r['id']}  {r.get('name', '')}  "
                  f"passed={r.get('passed_count', 0)}  "
                  f"failed={r.get('failed_count', 0)}")
        return runs

    def get_run(self, run_id: int) -> dict:
        """Fetch a single test run by its ID."""
        self._require_client()
        return self._client.runs.get_run(run_id=run_id)

    def create_run(self, name: str = None, case_ids: list = None,
                   suite_id: int = None) -> int:
        """
        Create a new test run and return its ID.

        Args:
            name:      Run name (defaults to TESTRAIL_RUN_NAME with today's date).
            case_ids:  List of case IDs to include; None = include all cases.
            suite_id:  Suite ID for multi-suite projects.

        Returns:
            The new run's integer ID.
        """
        self._require_client()
        run_name = (name or TESTRAIL_RUN_NAME).replace(
            "{date}", datetime.now().strftime("%Y-%m-%d %H:%M")
        )
        payload = {
            "name":       run_name,
            "include_all": case_ids is None,
        }
        sid = suite_id or TESTRAIL_SUITE_ID
        if sid:
            payload["suite_id"] = sid
        if case_ids:
            payload["case_ids"] = case_ids

        run = self._client.runs.add_run(
            project_id=TESTRAIL_PROJECT_ID, **payload
        )
        print(f"[TestRail] Created run R{run['id']}: {run_name}")
        return run["id"]

    def get_or_create_run(self, name: str = None, case_ids: list = None) -> int:
        """
        Return TESTRAIL_RUN_ID if set, otherwise create a new run.

        Returns:
            Integer run ID to use for result submissions.
        """
        self._require_client()
        if TESTRAIL_RUN_ID:
            print(f"[TestRail] Using existing run R{TESTRAIL_RUN_ID}")
            return TESTRAIL_RUN_ID
        if TESTRAIL_AUTO_CREATE_RUN:
            return self.create_run(name=name, case_ids=case_ids)
        raise RuntimeError(
            "No TESTRAIL_RUN_ID configured and TESTRAIL_AUTO_CREATE_RUN is False. "
            "Set one of them in config.py."
        )

    def close_run(self, run_id: int):
        """Close a test run (marks it complete in TestRail)."""
        self._require_client()
        self._client.runs.close_run(run_id=run_id)
        print(f"[TestRail] Closed run R{run_id}")

    # ── Results ───────────────────────────────────────────────────────────────

    def add_result(
        self,
        run_id: int,
        case_id: int,
        status: str = "passed",
        comment: str = "",
        elapsed: str = None,
    ):
        """
        Submit a single test result.

        Args:
            run_id:  TestRail run ID.
            case_id: TestRail case ID (integer, without the 'C' prefix).
            status:  One of: passed, failed, blocked, skip, retest, error.
            comment: Optional comment / error message.
            elapsed: Time taken, e.g. "1m 30s" or "45s".
        """
        self._require_client()
        status_id = STATUS_MAP.get(status.lower(), 5)
        payload = {"status_id": status_id, "comment": comment}
        if elapsed:
            payload["elapsed"] = elapsed

        result = self._client.results.add_result_for_case(
            run_id=run_id, case_id=case_id, **payload
        )
        label = {1: "PASSED", 2: "BLOCKED", 3: "UNTESTED", 4: "RETEST", 5: "FAILED"}.get(
            status_id, "UNKNOWN"
        )
        print(f"[TestRail] R{run_id}/C{case_id} → {label}")
        return result

    def push_results(self, run_id: int, results: list):
        """
        Bulk-submit results using add_results_for_cases.

        Args:
            run_id:  TestRail run ID.
            results: List of dicts with keys: case_id, status, comment, elapsed (all optional except case_id).

        Example:
            results = [
                {"case_id": 1001, "status": "passed", "comment": "OK"},
                {"case_id": 1002, "status": "failed", "comment": "AssertionError: expected True"},
            ]
        """
        self._require_client()
        if not results:
            print("[TestRail] No results to push.")
            return

        payload = []
        for r in results:
            status_str = r.get("status", "failed")
            entry = {
                "case_id":   r["case_id"],
                "status_id": STATUS_MAP.get(status_str.lower(), 5),
                "comment":   r.get("comment", ""),
            }
            if r.get("elapsed"):
                entry["elapsed"] = r["elapsed"]
            payload.append(entry)

        self._client.results.add_results_for_cases(
            run_id=run_id, results=payload
        )
        passed  = sum(1 for e in payload if e["status_id"] == 1)
        failed  = sum(1 for e in payload if e["status_id"] == 5)
        skipped = sum(1 for e in payload if e["status_id"] == 3)
        print(
            f"[TestRail] Pushed {len(payload)} result(s) to R{run_id} – "
            f"passed={passed}  failed={failed}  skipped={skipped}"
        )

    # ── Convenience ───────────────────────────────────────────────────────────

    def find_case_by_title(self, title: str, suite_id: int = None) -> dict | None:
        """Search cases for an exact title match (case-insensitive)."""
        cases = self.get_cases(suite_id=suite_id)
        title_lower = title.lower()
        return next(
            (c for c in cases if c.get("title", "").lower() == title_lower),
            None,
        )

    def get_project(self) -> dict:
        """Return metadata for the configured project."""
        self._require_client()
        project = self._client.projects.get_project(
            project_id=TESTRAIL_PROJECT_ID
        )
        print(f"[TestRail] Project: {project.get('name', '')} (ID {project['id']})")
        return project

    def add_case(self, section_id: int, title: str, **kwargs) -> dict:
        """
        Create a new test case in the given section.

        Args:
            section_id: TestRail section (folder) ID.
            title:      Test case title.
            **kwargs:   Any additional TestRail case fields
                        (type_id, priority_id, refs, custom_preconds, etc.)

        Returns:
            The created case dict from the TestRail API.
        """
        self._require_client()
        case = self._client.cases.add_case(
            section_id=section_id, title=title, **kwargs
        )
        print(f"[TestRail] Created case C{case['id']}: {case.get('title', '')}")
        return case

    def update_case(self, case_id: int, **kwargs) -> dict:
        """
        Update fields on an existing test case.

        Args:
            case_id:  TestRail case ID (integer, without the 'C' prefix).
            **kwargs: Fields to update (title, custom_steps, custom_expected, etc.)

        Returns:
            The updated case dict from the TestRail API.
        """
        self._require_client()
        case = self._client.cases.update_case(case_id=case_id, **kwargs)
        print(f"[TestRail] Updated case C{case['id']}: {case.get('title', '')}")
        return case

    def add_section(self, name: str, suite_id: int = None, parent_id: int = None) -> dict:
        """
        Create a new section (folder) in the project.

        Args:
            name:      Section name.
            suite_id:  Suite ID (required for multi-suite projects).
            parent_id: Parent section ID to create a nested sub-folder.

        Returns:
            The created section dict from the TestRail API.
        """
        self._require_client()
        kwargs = {}
        sid = suite_id or TESTRAIL_SUITE_ID
        if sid:
            kwargs["suite_id"] = sid
        if parent_id:
            kwargs["parent_id"] = parent_id
        section = self._client.sections.add_section(
            project_id=TESTRAIL_PROJECT_ID, name=name, **kwargs
        )
        print(f"[TestRail] Created section ID {section['id']}: {section.get('name', '')}")
        return section
