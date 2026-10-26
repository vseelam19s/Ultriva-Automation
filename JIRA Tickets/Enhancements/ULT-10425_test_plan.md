# ULT-10425 — Plant Home Page Integration Panel: Remember Last BU Filter Choice

**Type:** Enhancement / Customer Request  
**Status:** In QA Review  
**Assignee:** Sherif Hamdy  
**QA Site:** https://engineering.ultrivalms.com/qals1011  
**Credentials:** buyeruser / Ultriva!23  

---

## Feature Summary

On the **Plant Home Page**, the Integration Panel includes a filter toggle with two options:

| Old Label | New Label |
|---|---|
| All Business Units | **Plant and Associated Workcenters** |
| Only this BU | Only this BU *(unchanged)* |

**Two changes requested:**

1. **Persistence** — The filter remembers the user's last selection. If the user picks  
   "Plant and Associated Workcenters", the page must restore that choice the next time  
   the user visits (instead of always resetting to "Only this BU").  
2. **Label Rename** — "All Business Units" must be relabelled to  
   **"Plant and Associated Workcenters"**.

---

## Scope

| In Scope | Out of Scope |
|---|---|
| Label rename on Integration Panel filter | Other Home Page panels or filters |
| Filter selection persistence per user | Admin-level filter reset or override |
| Persistence across page navigations | Cross-device / cross-browser sync |
| Persistence across browser sessions | Role-based filter visibility |
| Default state for first-time / new users | Integration Panel data content changes |
| Regression of "Only this BU" filter behaviour | |

---

## Test Scenarios (Summary)

| ID | Scenario | Priority |
|---|---|---|
| TS-01 | Label reads "Plant and Associated Workcenters" (not "All Business Units") | Critical |
| TS-02 | Selecting "Plant and Associated Workcenters" is remembered on next page visit | Critical |
| TS-03 | Selecting "Only this BU" is remembered on next page visit | High |
| TS-04 | Default filter is "Only this BU" for a fresh / first-time user | High |
| TS-05 | Preference persists after full browser session restart | Medium |
| TS-06 | Two different users have independent filter preferences | Medium |

---

## Test Plan

### Objective
Verify that:
- The Integration Panel filter option is correctly renamed to "Plant and Associated Workcenters".  
- The panel remembers and restores the user's last filter choice on every visit.

### Test Types
- Functional (label verification, persistence logic)  
- Regression (ensure the "Only this BU" view still works correctly)  
- Session / State (preference survives navigation and browser restart)

### Environment
| Item | Value |
|---|---|
| QA URL | https://engineering.ultrivalms.com/qals1011 |
| User 1 | buyeruser / Ultriva!23 |
| Browser | Chrome (latest) |
| Page under test | Plant Home Page → Integration Panel |

### Test Data Requirements
- At least **two distinct user accounts** to validate independent preference storage.  
- A user with **no prior selection** to validate the default state.  
- Items visible under both "Only this BU" and "Plant and Associated Workcenters" views  
  to confirm the correct data is loaded per filter.

### Entry Criteria
- Enhancement deployed to QA environment (https://engineering.ultrivalms.com/qals1011).  
- Integration Panel is visible and functional on the Plant Home Page.  
- At least two test user accounts available.

### Exit Criteria
- All Critical and High priority test cases pass with no open defects.  
- No regression in "Only this BU" filter or Integration Panel data display.

### Risk
| Risk | Mitigation |
|---|---|
| Preference stored in cookie (clears on browser close) | Execute TS-05 with a new browser session |
| Label change may break existing XPath selectors | Update selectors to use new label text |
| Only one test user available | Re-run with the same user, clearing preference between runs |

---
