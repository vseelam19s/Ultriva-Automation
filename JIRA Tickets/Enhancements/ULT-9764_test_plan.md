# ULT-9764 — Add Task Name Filter to Service Monitors Screen

**Type:** Technical Debt  
**Status:** In QA Review  
**Assignee:** Sherif Hamdy  
**QA Site:** https://engineering.ultrivalms.com/QALS1011  
**URL Under Test:** https://engineering.ultrivalms.com/QALS1011/SysAdmin/IntgMonitor  
**Credentials:** Application $ Administrator (admin)  

---

## Feature Summary

The **Integration Monitor → Errors** screen (Admin > Integration > Integration Monitor) now
includes a **Task Name** text-filter field alongside the existing **Date Range** filter.

Users can type a full or partial task name and press **Go** to narrow error-log results to
records whose `Name` column matches the input.  The filter works in combination with the
Date Range picker and affects paginated results on the **Errors** tab.

---

## Scope

| In Scope | Out of Scope |
|---|---|
| Task Name filter field visible on Errors tab | Current Status tab (separate scope) |
| Filter by exact task name | Cross-user/cross-session persistence |
| Filter by partial/substring task name | Admin task management |
| Case-insensitive matching | Integration Monitor data content |
| Combining Task Name + Date Range filters | Other SysAdmin screens |
| Empty / no-match result state | API-level integration validation |
| Clearing Task Name resets results | |
| Pagination with filter applied | |
| Go button required to trigger filter | |

---

## Test Scenarios (Summary)

| ID | Scenario | Priority |
|---|---|---|
| TS-01 | Task Name filter field is visible on Errors tab | Critical |
| TS-02 | Valid exact task name returns only matching records | Critical |
| TS-03 | Partial / substring task name returns matching records | Critical |
| TS-04 | Non-existent task name shows empty/no-results state | High |
| TS-05 | Task Name filter is case-insensitive | High |
| TS-06 | Clearing Task Name field and clicking Go returns all records | High |
| TS-07 | Task Name combined with Date Range filters results correctly | High |
| TS-08 | Pagination is accurate when Task Name filter is active | Medium |
| TS-09 | Go button is required to trigger filtering (no auto-search) | Medium |
| TS-10 | Special characters in Task Name field handled gracefully | Low |

---

## Test Plan

### Objective
Verify that the **Task Name** filter on the Integration Monitor Errors screen:
- Is correctly rendered next to the existing Date Range filter.
- Returns records whose Name matches the input (exact and partial).
- Works in combination with the Date Range filter.
- Shows an appropriate empty state when no records match.
- Requires clicking **Go** to apply; does not auto-filter on keystroke.

### Environment
| Item | Value |
|---|---|
| Application | Ultriva Lean Suite |
| Site | QALS1011 |
| Browser | Chrome (latest) |
| Role | Application $ Administrator (SysAdmin BU) |
| Navigation | Admin → Integration → Integration Monitor → Errors tab |

### Entry Criteria
- QALS1011 is accessible and user can login.
- At least one Integration Monitor error record exists with a known task name
  (e.g., a record containing "sync", such as `SVC.$batchjob_BSU22ZAQALG`).

### Exit Criteria
- All Critical / High test cases pass.
- No blocker defects open against the Task Name filter.

### Test Data
| Variable | Value |
|---|---|
| Known task substring | `sync` |
| Known full task name | `SVC.$batchjob_BSU22ZAQALG` (or similar from live data) |
| Non-existent task name | `DOESNOTEXIST_XYZ_999` |
| Date range (default) | 04/04/2026 – 04/08/2026 |

---

## Risk Analysis

| Risk | Impact | Mitigation |
|---|---|---|
| Filter not wired to backend query | Critical — wrong results | Verify record count changes on filter |
| Case-sensitive matching excludes records | High — usability | Test upper/lower/mixed case |
| Pagination resets page count without filter | Medium | Check "Viewing X to Y of Z" after filter |
| Special chars cause server error | Low | Test one special-char case (e.g., `$`) |

---

## Short-Form Test Cases (from Screenshot)

| TC | Description | Steps | Expected |
|---|---|---|---|
| TC-01 | Filter field visible | Open Errors tab | "Task Name" input and "Go" button are visible |
| TC-02 | Filter by partial name "sync" | Enter "sync" → click Go | Only records with "sync" in Name column shown |
| TC-03 | Filter by exact name | Paste full task name → click Go | Only that task's records shown |
| TC-04 | No match | Enter "DOESNOTEXIST_XYZ_999" → click Go | Empty grid or "No records" message |
| TC-05 | Case-insensitive | Enter "SYNC" → click Go | Same records as "sync" search |
| TC-06 | Clear filter | Clear Task Name field → click Go | All records for selected date range returned |
| TC-07 | Combined filters | Set date range Past 7 Days + Task Name "sync" → Go | Records match both date and name criteria |
| TC-08 | Pagination with filter | Filter "sync" → check page count | Page count reflects filtered total (not all records) |
| TC-09 | Go required | Type name; do NOT click Go | Grid does not update until Go is clicked |
| TC-10 | Special char in name | Enter "$" → click Go | No server error; results or empty state shown |
