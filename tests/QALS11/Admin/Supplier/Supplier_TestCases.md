# QALS11 — Internal Supplier Test Cases

**Application**: https://engineering.ultrivalms.com/QALS1011  
**Login**: buyeruser / Ultriva!23  
**Source File**: `tests/QALS11/Admin/Supplier/InternalSupplier.py`  
**Total Test Classes**: 1 | **Total Tests**: 5

---

## Run Commands

```bash
cd qa_automation

# Run all Internal Supplier tests
pytest tests/QALS11/Admin/Supplier/InternalSupplier.py -v -s -o "python_files=*.py"

# Run specific test
pytest tests/QALS11/Admin/Supplier/InternalSupplier.py::TestInternalSupplierConfig::test_01_login_and_navigate_to_supplier -v -s -o "python_files=*.py"
```

---

## TestInternalSupplierConfig (5 tests)

> Login, navigate to Admin > Supplier, switch to Internal Supplier tab, search for "WCLine", open its configuration, update random values on each tab, and generate a report.

**Target Workcenter**: WCLine

| # | Test Name | Description |
|---|-----------|-------------|
| 1 | `test_01_login_and_navigate_to_supplier` | Log in as buyeruser, navigate to Admin > Supplier list |
| 2 | `test_02_switch_to_internal_and_search_wcline` | Switch to Internal Supplier tab, search "WCLine" using Find Name field |
| 3 | `test_03_open_wcline_configuration` | Select the WCLine row, click "More Options" toolbar > Configuration |
| 4 | `test_04_update_configuration_tabs` | On Supply Workcenter Configuration, click each tab, update random values, Save |
| 5 | `test_05_generate_report` | Generate the configuration report |

---

## Test Flow

```
Login → Admin → Supplier List → Internal Supplier tab
  → Find "WCLine" → Select row → More Options → Configuration
    → Update Tab 1 values → Save
    → Update Tab 2 values → Save
    → Update Tab N values → Save
  → Generate Report
```

---

## Summary

| Test Class | Tests | Target | Scope |
|------------|-------|--------|-------|
| TestInternalSupplierConfig | 5 | WCLine | Internal supplier workcenter configuration |
| **Total** | **5** | | |
