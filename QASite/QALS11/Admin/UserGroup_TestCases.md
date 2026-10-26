# User Group – Test Cases

**Module:** Admin > User Group > Local  
**Script:** `UserGroup.py`  
**Application:** Ultriva LMS (QALS1011)

---

## Test Case 1: Create Local User Group

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Log in to QA site | User is logged in successfully |
| 2 | Navigate to Admin > User Group | System Group List page loads |
| 3 | Click the "Local" tab | Local Group List is displayed |
| 4 | Click "+ Add" button | Create Local Group form opens |
| 5 | Enter Title and Description | Fields are filled in |
| 6 | Select "Plant Users" radio button | Radio button is selected |
| 7 | Select privilege checkboxes (Add User, Edit User, View Details, Add User Group, Edit User Group) | Allow toggles turn green |
| 8 | Click Save | Redirected to Local Group List; new group appears |

---

## Test Case 2: Edit Local User Group

| Step | Action | Expected Result |
|------|--------|-----------------|
| 9 | Navigate to Local Group List | List page loads |
| 10 | Search for the created group and click Edit | Edit Local Group form opens with pre-filled data |
| 11 | Modify Title and Description | Fields updated with new values |
| 12 | Toggle privileges – disable "Edit User", enable "View Details", "Enable/Disable User", "Assign Groups" | Privilege images toggle accordingly |
| 13 | Click Save | Changes saved; redirected to list or update page |

---

## Test Case 3: View Local User Group

| Step | Action | Expected Result |
|------|--------|-----------------|
| 14 | Navigate to Local Group List | List page loads |
| 15 | Search for the group and click View | View Local Group page opens (read-only) |
| 16 | Click Cancel | Returned to Local Group List |

---

## Test Case 4: Assign Users to User Group

| Step | Action | Expected Result |
|------|--------|-----------------|
| 17 | Navigate to Local Group List | List page loads |
| 18 | Search for the group and click Assigned Users | Assigned Users page opens |
| 19 | Click "+ Assign User(s)" button | Assign Users page opens with user list |
| 20 | Select a user checkbox and click "+ Assign" | User is assigned to the group |
| 21 | Click Back button | Returned to Assigned Users page |

---

## Test Case 5: My Routines

| Step | Action | Expected Result |
|------|--------|-----------------|
| 22 | Navigate to Local Group List | List page loads |
| 23 | Search for the group and click My Routines | Manage My Routines page opens |
| 24 | Select Daily / Weekly / Monthly checkboxes | Checkboxes are checked |
| 25 | Click Save | Routine schedules saved |

---

## Test Case 6: Clone User Group

| Step | Action | Expected Result |
|------|--------|-----------------|
| 26 | Navigate to Local Group List | List page loads |
| 27 | Search for the group and click Clone Group | Create Local Group (clone) form opens with pre-filled data |
| 28 | Modify Title and Description | New values entered |
| 29 | Optionally modify privileges | Privileges toggled |
| 30 | Click Save | Cloned group saved; appears in the list |

---

## Test Case 7: Delete User Group

| Step | Action | Expected Result |
|------|--------|-----------------|
| 31 | Navigate to Local Group List | List page loads |
| 32 | Search for the target group and click its row | Row is highlighted/selected |
| 33 | Click Delete toolbar button | Confirmation dialog appears ("Do you want to delete this group?") |
| 34 | Click Yes | Group is deleted |
| 35 | Verify group is removed from the list | Group no longer appears in the Local Group List |

---

## Summary

| # | Test Case | Operations Covered |
|---|-----------|-------------------|
| 1 | Create Local User Group | Login, navigation, form fill, privilege selection, save |
| 2 | Edit Local User Group | Search, edit form, modify fields & privileges, save |
| 3 | View Local User Group | Search, view read-only page, cancel/back |
| 4 | Assign Users | Search, open assigned users, assign a user, navigate back |
| 5 | My Routines | Search, open routines, select schedules, save |
| 6 | Clone User Group | Search, clone, modify cloned data, save |
| 7 | Delete User Group | Search, select row, delete with confirmation, verify removal |
