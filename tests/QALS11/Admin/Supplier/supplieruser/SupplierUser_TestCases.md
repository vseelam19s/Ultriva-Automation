# QALS11 — Supplier User Creation Test Cases

**Application**: https://engineering.ultrivalms.com/QALS1011  
**Login**: buyeruser / Ultriva!23  
**Source File**: `tests/QALS11/Admin/Supplier/supplieruser/SupplierUserCreation.py`  
**Total Test Classes**: 1 | **Total Tests**: 10

---

## Run Commands

```bash
cd qa_automation

# Run all Supplier User Creation tests
pytest tests/QALS11/Admin/Supplier/supplieruser/SupplierUserCreation.py -v -s -o "python_files=*.py"

# Run specific test
pytest tests/QALS11/Admin/Supplier/supplieruser/SupplierUserCreation.py::TestSupplierUserCreation::test_01_login -v -s -o "python_files=*.py"
```

---

## TestSupplierUserCreation (10 tests)

> Login as buyeruser, navigate to Admin > Supplier list, select External Supplier "TestSup197", add a new Supplier Administrator user with unique random credentials, save, and verify.

**Target Supplier**: TestSup197  
**Account Type**: Supplier Administrators  
**User ID Pattern**: `SupUsr{random 4-digit}` (generated at runtime)  
**Password Pattern**: `SupUsr@{random}!X` (meets complexity: >8 chars, 1 upper, 1 lower, 1 digit, 1 symbol)

| # | Test Name | Description |
|---|-----------|-------------|
| 1 | `test_01_login` | Log in to the QA site with admin credentials |
| 2 | `test_02_open_admin` | Click Admin module |
| 3 | `test_03_click_supplier_menu` | Click Supplier menu → Supplier list (`/Supplier/List`) |
| 4 | `test_04_select_supplier` | Select External Supplier "TestSup197" from the list |
| 5 | `test_05_click_add_user` | Click "Add User" button on the supplier page |
| 6 | `test_06_fill_user_form` | Fill Create User form — First Name, Last Name, Work Phone, Email |
| 7 | `test_07_set_account_and_userid` | Set Account Type to "Supplier Administrators" and enter unique User ID |
| 8 | `test_08_set_password` | Enter password meeting all complexity rules |
| 9 | `test_09_save_user` | Save the new user |
| 10 | `test_10_show_results` | Verify the new user appears and display results |

---

## Test Flow

```
Login → Admin → Supplier Menu → Supplier List
  → Select "TestSup197" → Add User
    → Fill: First Name, Last Name, Work Phone, Email
    → Set: Account Type = Supplier Administrators
    → Set: User ID = SupUsr{rand}
    → Set: Password = SupUsr@{rand}!X
    → Save
  → Verify user created
```

---

## User Data (Generated at Runtime)

| Field | Value |
|-------|-------|
| First Name | SupUser |
| Last Name | Test{random 4-digit} |
| Work Phone | 555{random}0000 |
| Email | supuser{random}@testsupplier.example.com |
| User ID | SupUsr{random} |
| Password | SupUsr@{random}!X |
| Account Type | Supplier Administrators |

---

## Summary

| Test Class | Tests | Target Supplier | Scope |
|------------|-------|-----------------|-------|
| TestSupplierUserCreation | 10 | TestSup197 | Create supplier admin user |
| **Total** | **10** | | |
