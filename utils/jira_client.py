"""
JIRA client utility for QA Automation.

Usage:
    from utils.jira_client import JiraClient

    jira = JiraClient()

    # List tickets in a project
    issues = jira.search("project = QA ORDER BY created DESC", max_results=20)

    # Get a specific ticket
    issue = jira.get_issue("QA-123")

    # Create a bug ticket for a failed test
    key = jira.create_bug(
        summary="Login test failed on staging",
        description="PerformLogin() raised WebDriverTimeoutException",
        labels=["automation", "regression"],
    )

    # Add a comment to a ticket
    jira.add_comment("QA-123", "Automated test passed on 2026-03-18.")

    # Update ticket status (transition)
    jira.transition_issue("QA-123", transition_name="In Progress")
"""

import sys
import os

# Allow running this file standalone from the qa_automation directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from jira import JIRA, JIRAError
from config.config import (
    JIRA_SERVER,
    JIRA_EMAIL,
    JIRA_API_TOKEN,
    JIRA_PAT,
    JIRA_PROJECT_KEY,
)


class JiraClient:
    """Thin wrapper around the jira library configured from config.py."""

    def __init__(self):
        self.project_key = JIRA_PROJECT_KEY
        self._client = self._connect()

    # ── Connection ────────────────────────────────────────────────────────────

    def _connect(self) -> JIRA:
        """
        Connect using API Token (Atlassian Cloud) or PAT (Server/DC).
        Priority: PAT > API Token.
        """
        if JIRA_PAT:
            # Personal Access Token – used with Jira Server / Data Center
            client = JIRA(
                server=JIRA_SERVER,
                token_auth=JIRA_PAT,
            )
            print(f"[JIRA] Connected via PAT to {JIRA_SERVER}")
        elif JIRA_EMAIL and JIRA_API_TOKEN:
            # Basic auth with API token – used with Atlassian Cloud
            client = JIRA(
                server=JIRA_SERVER,
                basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN),
            )
            print(f"[JIRA] Connected via API Token to {JIRA_SERVER}")
        else:
            raise ValueError(
                "JIRA credentials not configured.\n"
                "Set JIRA_API_TOKEN (+ JIRA_EMAIL) for Atlassian Cloud,\n"
                "or JIRA_PAT for Jira Server/Data Center in config/config.py."
            )
        return client

    # ── Read operations ───────────────────────────────────────────────────────

    def get_issue(self, issue_key: str):
        """Fetch a single issue by key (e.g. 'QA-123')."""
        try:
            issue = self._client.issue(issue_key)
            print(f"[JIRA] {issue.key}: {issue.fields.summary} [{issue.fields.status.name}]")
            return issue
        except JIRAError as e:
            print(f"[JIRA] Error fetching {issue_key}: {e.status_code} {e.text}")
            raise

    def search(self, jql: str = None, max_results: int = 50):
        """
        Search for issues using JQL.
        Defaults to all open issues in the configured project.
        """
        if jql is None:
            jql = f"project = {self.project_key} AND statusCategory != Done ORDER BY created DESC"
        issues = self._client.search_issues(jql, maxResults=max_results)
        print(f"[JIRA] Found {len(issues)} issue(s) for JQL: {jql}")
        for issue in issues:
            print(f"  {issue.key}  [{issue.fields.status.name}]  {issue.fields.summary}")
        return issues

    def get_transitions(self, issue_key: str):
        """Return available status transitions for an issue."""
        return self._client.transitions(issue_key)

    # ── Write operations ──────────────────────────────────────────────────────

    def create_bug(
        self,
        summary: str,
        description: str = "",
        priority: str = "Medium",
        labels: list = None,
        project_key: str = None,
    ) -> str:
        """Create a Bug issue and return its key."""
        fields = {
            "project":     {"key": project_key or self.project_key},
            "summary":     summary,
            "description": description,
            "issuetype":   {"name": "Bug"},
            "priority":    {"name": priority},
        }
        if labels:
            fields["labels"] = labels

        issue = self._client.create_issue(fields=fields)
        print(f"[JIRA] Created bug: {issue.key} – {summary}")
        return issue.key

    def create_task(
        self,
        summary: str,
        description: str = "",
        project_key: str = None,
    ) -> str:
        """Create a Task issue and return its key."""
        fields = {
            "project":     {"key": project_key or self.project_key},
            "summary":     summary,
            "description": description,
            "issuetype":   {"name": "Task"},
        }
        issue = self._client.create_issue(fields=fields)
        print(f"[JIRA] Created task: {issue.key} – {summary}")
        return issue.key

    def add_comment(self, issue_key: str, body: str):
        """Add a comment to an existing issue."""
        comment = self._client.add_comment(issue_key, body)
        print(f"[JIRA] Comment added to {issue_key}")
        return comment

    def transition_issue(self, issue_key: str, transition_name: str):
        """Move an issue to a new status by transition name."""
        transitions = self._client.transitions(issue_key)
        match = next(
            (t for t in transitions if t["name"].lower() == transition_name.lower()),
            None,
        )
        if match is None:
            available = [t["name"] for t in transitions]
            raise ValueError(
                f"Transition '{transition_name}' not found for {issue_key}. "
                f"Available: {available}"
            )
        self._client.transition_issue(issue_key, match["id"])
        print(f"[JIRA] {issue_key} transitioned to '{transition_name}'")

    def attach_file(self, issue_key: str, file_path: str):
        """Attach a local file (e.g. screenshot) to an issue."""
        with open(file_path, "rb") as f:
            self._client.add_attachment(issue=issue_key, attachment=f,
                                        filename=os.path.basename(file_path))
        print(f"[JIRA] Attached {file_path} to {issue_key}")

    # ── Project info ──────────────────────────────────────────────────────────

    def list_projects(self):
        """Print all accessible projects."""
        projects = self._client.projects()
        print(f"[JIRA] Accessible projects ({len(projects)}):")
        for p in projects:
            print(f"  {p.key:10s}  {p.name}")
        return projects
