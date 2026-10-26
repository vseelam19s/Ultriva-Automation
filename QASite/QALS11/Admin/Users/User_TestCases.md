# QALS11 — User Management Test Cases

**Application**: https://engineering.ultrivalms.com/QALS1011  
**Login**: buyeruser / Ultriva!23  
**Source File**: `tests/QALS11/Admin/Users/users.py`  
**Total Test Classes**: 7 | **Total Tests**: 38

---

## Run Commands

```bash
# Run all User tests
cd qa_automation
pytest tests/QALS11/Admin/Users/users.py -v -s

# Run a specific class
pytest tests/QALS11/Admin/Users/users.py::TestUsersList -v -s
pytest tests/QALS11/Admin/Users/users.py::TestEditUser -v -s
pytest tests/QALS11/Admin/Users/users.py::TestCreateUsers -v -s
pytest tests/QALS11/Admin/Users/users.py::TestViewUser -v -s
pytest tests/QALS11/Admin/Users/users.py::TestDisableUser -v -s
pytest tests/QALS11/Admin/Users/users.py::TestEnableUser -v -s
pytest tests/QALS11/Admin/Users/users.py::TestUser150426_1 -v -s
```

---

## 1. TestUsersList (3 tests)

> Verify that a logged-in admin can reach the Admin > Users list page and that user rows are visible in the table.

| # | Test Name | Description |
|---|-----------|-------------|
| 1 | `test_01_login` | Open the QA site and log in with admin credentials |
| 2 | `test_02_open_admin_module` | Navigate to Admin Home |
| 3 | `test_03_view_users_list` | Click the Users menu and see the list |

---

## 2. TestEditUser (5 tests)

> Select the user PlantAdm01 from the Users list and update all mandatory fields, then save.

| # | Test Name | Description |
|---|-----------|-------------|
| 1 | `test_01_login` | Log in with admin credentials |
| 2 | `test_02_navigate_to_users_list` | Navigate to the Users list |
| 3 | `test_03_open_edit_page_for_plantadm01` | Find PlantAdm01 in the list and open the Edit page |
| 4 | `test_04_fill_in_mandatory_fields` | Fill in all mandatory fields with new values |
| 5 | `test_05_save_user` | Click Save and confirm no error appeared |

---

## 3. TestCreateUsers (8 tests)

> Log in, create 6 Plant Administrator users one by one, then export all user IDs and passwords to an Excel report.

| # | Test Name | Description |
|---|-----------|-------------|
| 1 | `test_01_login_as_admin` | Log in with the admin account before creating users |
| 2 | `test_02_create_plantadm01` | Create PlantAdm01 (Alice Johnson) |
| 3 | `test_03_create_plantadm02` | Create PlantAdm02 (Bob Martinez) |
| 4 | `test_04_create_plantadm03` | Create PlantAdm03 (Carol Davis) |
| 5 | `test_05_create_plantadm04` | Create PlantAdm04 (David Wilson) |
| 6 | `test_06_create_plantadm05` | Create PlantAdm05 (Emma Thompson) |
| 7 | `test_07_create_user150426` | Create User150426 (added 15-Apr-2026) |
| 8 | `test_08_export_credentials_to_excel` | Export all credentials to Excel report |

---

## 4. TestViewUser (4 tests)

> Verify the View User page for User150426.

| # | Test Name | Description |
|---|-----------|-------------|
| 1 | `test_01_login` | Log in with admin credentials |
| 2 | `test_02_search_user` | Open User List and search for User150426 |
| 3 | `test_03_select_and_click_view` | Select the row and click the View toolbar button |
| 4 | `test_04_verify_and_cancel` | Confirm the View User page loaded, then click Cancel |

---

## 5. TestDisableUser (7 tests)

> Disable the user 'User150426' from the Admin > User List.

| # | Test Name | Description |
|---|-----------|-------------|
| 1 | `test_01_login` | Log in to the QA site with admin credentials |
| 2 | `test_02_open_user_list` | Open the User List page |
| 3 | `test_03_search_user` | Search for User150426 |
| 4 | `test_04_select_user_row` | Select the user row |
| 5 | `test_05_click_disable_button` | Click the Disable toolbar button |
| 6 | `test_06_confirm_disable` | Confirm Yes in the dialog |
| 7 | `test_07_verify_user_disabled` | Verify the user shows Disabled status |

---

## 6. TestEnableUser (7 tests)

> Re-enable the user 'User150426' from the Disabled User List.

| # | Test Name | Description |
|---|-----------|-------------|
| 1 | `test_01_login` | Log in to the QA site with admin credentials |
| 2 | `test_02_open_disabled_list` | User List → More Options → Show Disabled And Locked |
| 3 | `test_03_search_user` | Search for User150426 in the Disabled list |
| 4 | `test_04_select_user_row` | Select the user row |
| 5 | `test_05_click_enable_button` | Click the Enable toolbar button |
| 6 | `test_06_confirm_enable` | Confirm Yes in the dialog |
| 7 | `test_07_verify_user_enabled` | Verify user is back on the Active list |

---

## 7. TestUser150426_1 — End-to-End Lifecycle (8 tests)

> Complete lifecycle test for user 'User150426_1': create → edit → view → disable → enable → update email → assign groups.

| # | Test Name | Description |
|---|-----------|-------------|
| 1 | `test_01_login` | Login once; browser stays open throughout |
| 2 | `test_02_create_user` | Create the user with random mandatory field values |
| 3 | `test_03_edit_user` | Edit the user with new random values → User List |
| 4 | `test_04_view_user` | View the user → click Cancel → User List |
| 5 | `test_05_disable_user` | Disable the user → User List |
| 6 | `test_06_enable_user` | Show Disabled list → Enable the user → Active User List |
| 7 | `test_07_update_email` | Update the user's email address |
| 8 | `test_08_assign_groups` | Assign user groups |

---

## Summary

| Test Class | Tests | Scope |
|------------|-------|-------|
| TestUsersList | 3 | List page navigation |
| TestEditUser | 5 | Edit existing user |
| TestCreateUsers | 8 | Bulk user creation + Excel export |
| TestViewUser | 4 | View user details |
| TestDisableUser | 7 | Disable a user |
| TestEnableUser | 7 | Re-enable a disabled user |
| TestUser150426_1 | 8 | Full user lifecycle (E2E) |
| **Total** | **42** | |
