"""
mark_buyer_reports_automated.py

Bulk-enable TestRail "Is Automated" for all cases under:
  Reports > Buyer Reports

Behavior:
- Dry-run by default (no updates are sent).
- Requires --apply to perform updates.
- Supports recursive updates for all descendant sections.
- Auto-discovers the suite containing the target path unless --suite-id is provided.

Examples:
  python qa_automation/mark_buyer_reports_automated.py
  python qa_automation/mark_buyer_reports_automated.py --suite-id 2571
  python qa_automation/mark_buyer_reports_automated.py --apply --yes
  python qa_automation/mark_buyer_reports_automated.py --path "Reports>Buyer Reports"
"""

from __future__ import annotations

import argparse
import sys
import time
from collections import defaultdict, deque
from typing import Dict, List, Tuple

from utils.testrail_client import TestRailClient
from config.config import TESTRAIL_PROJECT_ID


DEFAULT_PATH = ["Reports", "Buyer Reports"]


def _clean_name(value: str) -> str:
    return " ".join((value or "").strip().split()).lower()


def _parse_path(raw_path: str) -> List[str]:
    parts = [p.strip() for p in raw_path.split(">")]
    filtered = [p for p in parts if p]
    if not filtered:
        raise ValueError("Invalid path. Example: Reports>Buyer Reports")
    return filtered


def _build_indexes(sections: List[dict]) -> Tuple[Dict[int, dict], Dict[int, List[int]]]:
    by_id = {int(s["id"]): s for s in sections}
    children = defaultdict(list)
    for s in sections:
        sid = int(s["id"])
        parent_id = s.get("parent_id")
        if parent_id is not None:
            children[int(parent_id)].append(sid)
    return by_id, children


def _section_path(section_id: int, by_id: Dict[int, dict]) -> List[str]:
    names = []
    current = by_id.get(section_id)
    while current is not None:
        names.append(current.get("name", ""))
        parent_id = current.get("parent_id")
        current = by_id.get(int(parent_id)) if parent_id is not None else None
    names.reverse()
    return names


def _find_path_matches(sections: List[dict], target_path: List[str]) -> List[int]:
    by_id, _ = _build_indexes(sections)
    normalized_target = [_clean_name(p) for p in target_path]
    matches = []
    for sid in by_id:
        full_path = _section_path(sid, by_id)
        norm_full = [_clean_name(p) for p in full_path]
        if norm_full == normalized_target:
            matches.append(sid)
    return matches


def _collect_descendants(root_id: int, children: Dict[int, List[int]]) -> List[int]:
    out = []
    queue = deque([root_id])
    while queue:
        sid = queue.popleft()
        out.append(sid)
        for child in children.get(sid, []):
            queue.append(child)
    return out


def _get_cases_for_section_paginated(tr: TestRailClient, suite_id: int, section_id: int) -> List[dict]:
    tr._require_client()  # type: ignore[attr-defined]
    limit = 250
    offset = 0
    cases: List[dict] = []

    while True:
        data = tr._client.cases.get_cases(  # type: ignore[attr-defined]
            project_id=TESTRAIL_PROJECT_ID,
            suite_id=suite_id,
            section_id=section_id,
            limit=limit,
            offset=offset,
        )
        batch = data.get("cases", data) if isinstance(data, dict) else data
        if not isinstance(batch, list):
            batch = []
        cases.extend(batch)
        if len(batch) < limit:
            break
        offset += limit
    return cases


def _print_suite_list(suites: List[dict]) -> None:
    print("[INFO] Suites in project:")
    for s in suites:
        print(f"  - S{s.get('id')}: {s.get('name', '')}")


def _resolve_suite_and_roots(tr: TestRailClient, suite_id: int | None, target_path: List[str]) -> Tuple[int, List[int], List[dict]]:
    suites = tr.get_suites()
    if not suites:
        raise RuntimeError("No suites returned for the configured project.")

    if suite_id is not None:
        sections = tr.get_sections(suite_id=suite_id)
        matches = _find_path_matches(sections, target_path)
        if not matches and len(target_path) > 1:
            # Handle suite-prefixed input like "Reports > Buyer Reports" where
            # "Reports" is a suite name, not a section name.
            matches = _find_path_matches(sections, target_path[1:])
        if not matches:
            raise RuntimeError(
                f"Path {' > '.join(target_path)} was not found in suite S{suite_id}."
            )
        return suite_id, matches, sections

    candidates: List[Tuple[int, List[int], List[dict]]] = []
    for suite in suites:
        sid = int(suite["id"])
        sections = tr.get_sections(suite_id=sid)
        matches = _find_path_matches(sections, target_path)
        if not matches and len(target_path) > 1:
            # Handle suite-prefixed input like "Reports > Buyer Reports" where
            # "Reports" is a suite name, not a section name.
            matches = _find_path_matches(sections, target_path[1:])
        if matches:
            candidates.append((sid, matches, sections))

    if not candidates:
        _print_suite_list(suites)
        raise RuntimeError(
            f"Path {' > '.join(target_path)} was not found in any suite. "
            "Pass --suite-id if you want to force a suite."
        )

    if len(candidates) > 1:
        print("[ERROR] Multiple suites contain the requested path:")
        for sid, roots, _ in candidates:
            print(f"  - S{sid} (matches={roots})")
        raise RuntimeError("Ambiguous suite. Re-run with --suite-id.")

    return candidates[0]


def _dry_run_report(
    suite_id: int,
    by_id: Dict[int, dict],
    selected_sections: List[int],
    cases_by_section: Dict[int, List[dict]],
    deduped_cases: Dict[int, dict],
) -> None:
    print("\n" + "=" * 78)
    print("DRY RUN SUMMARY")
    print("=" * 78)
    print(f"Project ID                  : {TESTRAIL_PROJECT_ID}")
    print(f"Suite ID                    : {suite_id}")
    print(f"Sections in scope           : {len(selected_sections)}")
    print(f"Unique cases in scope       : {len(deduped_cases)}")
    print("\nSection breakdown:")
    for sid in selected_sections:
        section_name = by_id.get(sid, {}).get("name", "")
        print(f"  - {section_name} (ID={sid}): {len(cases_by_section.get(sid, []))} case(s)")

    sample_cases = list(deduped_cases.values())[:10]
    if sample_cases:
        print("\nSample cases (up to 10):")
        for c in sample_cases:
            automated = bool(c.get("custom_isautomated"))
            print(
                f"  - C{c.get('id')} | automated={automated} | {c.get('title', '')}"
            )
    print("=" * 78)


def _apply_updates(tr: TestRailClient, deduped_cases: Dict[int, dict], delay_seconds: float) -> Tuple[int, int, List[Tuple[int, str]]]:
    updated = 0
    skipped = 0
    failures: List[Tuple[int, str]] = []

    for case_id in sorted(deduped_cases):
        case = deduped_cases[case_id]
        if bool(case.get("custom_isautomated")):
            skipped += 1
            print(f"[SKIP] C{case_id} already automated")
            continue

        try:
            result = tr.update_case(case_id=case_id, custom_isautomated=True)
            confirmed = bool(result.get("custom_isautomated"))
            updated += 1
            print(f"[OK]   C{case_id} updated (confirmed={confirmed})")
            if delay_seconds > 0:
                time.sleep(delay_seconds)
        except Exception as exc:  # noqa: BLE001
            msg = str(exc)
            print(f"[FAIL] C{case_id} {msg}")
            failures.append((case_id, msg))

    return updated, skipped, failures


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Mark TestRail Is Automated = true for Reports > Buyer Reports."
    )
    parser.add_argument(
        "--path",
        default=">".join(DEFAULT_PATH),
        help="Section path, for example: Reports>Buyer Reports",
    )
    parser.add_argument(
        "--suite-id",
        type=int,
        default=None,
        help="Suite ID to search. If omitted, all suites are searched.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply updates. Without this flag, dry-run only.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip confirmation prompt in apply mode.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.2,
        help="Delay between update calls in seconds (default: 0.2).",
    )
    args = parser.parse_args()

    target_path = _parse_path(args.path)
    tr = TestRailClient()

    print("=" * 78)
    print("TestRail Buyer Reports Is Automated Updater")
    print("=" * 78)
    print(f"Target path: {' > '.join(target_path)}")
    print(f"Mode       : {'APPLY' if args.apply else 'DRY-RUN'}")

    suite_id, root_matches, sections = _resolve_suite_and_roots(
        tr, args.suite_id, target_path
    )

    by_id, children = _build_indexes(sections)
    selected_sections = []
    for root_id in root_matches:
        selected_sections.extend(_collect_descendants(root_id, children))
    selected_sections = sorted(set(selected_sections))

    print(f"Resolved suite: S{suite_id}")
    print(f"Root matches  : {root_matches}")

    cases_by_section: Dict[int, List[dict]] = {}
    deduped_cases: Dict[int, dict] = {}
    for sid in selected_sections:
        cases = _get_cases_for_section_paginated(tr, suite_id, sid)
        cases_by_section[sid] = cases
        for c in cases:
            deduped_cases[int(c["id"])] = c

    _dry_run_report(
        suite_id=suite_id,
        by_id=by_id,
        selected_sections=selected_sections,
        cases_by_section=cases_by_section,
        deduped_cases=deduped_cases,
    )

    if not args.apply:
        print("[INFO] Dry-run complete. Re-run with --apply to update cases.")
        return 0

    if not args.yes:
        answer = input("Proceed with updates? Type YES to continue: ").strip()
        if answer != "YES":
            print("[INFO] Update cancelled.")
            return 1

    updated, skipped, failures = _apply_updates(
        tr=tr,
        deduped_cases=deduped_cases,
        delay_seconds=max(args.delay, 0.0),
    )

    print("\n" + "=" * 78)
    print("APPLY SUMMARY")
    print("=" * 78)
    print(f"Updated (new)              : {updated}")
    print(f"Skipped (already true)     : {skipped}")
    print(f"Failed                     : {len(failures)}")
    print(f"Total unique cases         : {len(deduped_cases)}")
    if failures:
        print("\nFailures:")
        for case_id, error_msg in failures:
            print(f"  - C{case_id}: {error_msg}")
    print("=" * 78)

    return 0 if not failures else 2


if __name__ == "__main__":
    sys.exit(main())
