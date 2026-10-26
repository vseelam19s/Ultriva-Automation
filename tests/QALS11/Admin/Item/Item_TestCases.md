# QALS11 — Item Management Test Cases

**Application**: https://engineering.ultrivalms.com/QALS1011  
**Login**: buyeruser / Ultriva!23  
**Source Files**:
- `tests/QALS11/Admin/Item/NewItemCreationandAdjustLoopSize.py`
- `tests/QALS11/Admin/Item/test_item_excel_driven.py`

**Total Test Classes**: 17 | **Total Tests**: ~107

---

## Run Commands

```bash
cd qa_automation

# Run ALL Item tests
pytest tests/QALS11/Admin/Item/ -v -o "python_files=*.py"

# Run specific file
pytest tests/QALS11/Admin/Item/NewItemCreationandAdjustLoopSize.py -v -o "python_files=*.py"
pytest tests/QALS11/Admin/Item/test_item_excel_driven.py -v

# Run specific class
pytest tests/QALS11/Admin/Item/NewItemCreationandAdjustLoopSize.py::TestCreateItem -v -o "python_files=*.py"
pytest tests/QALS11/Admin/Item/NewItemCreationandAdjustLoopSize.py::TestCreateItemITDDDD -v -o "python_files=*.py" --html=reports/ITDDDD_report.html
pytest tests/QALS11/Admin/Item/NewItemCreationandAdjustLoopSize.py::TestExcelCreateAndAdjustLoop -v -o "python_files=*.py" --html=reports/excel_loop_report.html
```

---

## Data Source (Excel-driven classes)

- **File**: `qa_automation/test_data/item_test_data_1.xlsx` (sheet: ItemData)
- **Columns**: Item_No, Description, Category, Item_Coord, Landing_Time, Price_Per_UOM, Usage_Per_Day, Safety_Stock, Pallet_Qty, Ship_Tol, Receive_Tol, Supplier, Supplier_User, Supplier_Item_No, Supplier_Desc, Min_Order_Qty, Lead_Time, Transit_Time, Cards_To_Add, Run_Adjust_Loop

---

## File: NewItemCreationandAdjustLoopSize.py

### 1. TestCreateItemsData1 (3 tests)

> Create items from Excel data file (`item_test_data_1.xlsx`).

| # | Test Name | Description |
|---|-----------|-------------|
| 1 | `test_01_load_excel` | Load item data from Excel workbook |
| 2 | `test_02_login` | Log in with admin credentials |
| 3 | `test_03_create_all_items` | Create all items from the loaded Excel data |

---

### 2. TestFilterItemsData1 (3 tests)

> Clear filter and verify each newly created item appears in the item list.

| # | Test Name | Description |
|---|-----------|-------------|
| 1 | `test_01_login` | Log in with admin credentials |
| 2 | `test_02_clear_filter` | Clear existing filters on the item list |
| 3 | `test_03_filter_by_each_item` | Filter and verify each item appears |

---

### 3. TestCreateItem — IT010426 (8 tests)

> Create item IT010426 ("Test Item April 2026") with supplier info.

| # | Test Name | Description |
|---|-----------|-------------|
| 1 | `test_01_login` | Log in |
| 2 | `test_02_open_admin` | Navigate to Admin module |
| 3 | `test_03_open_item_list` | Open the Item List page |
| 4 | `test_04_click_add` | Click Add button |
| 5 | `test_05_fill_base_info` | Fill item base info (IT010426) |
| 6 | `test_06_fill_supplier_tab` | Fill supplier tab details |
| 7 | `test_07_save` | Save the item |
| 8 | `test_08_verify_in_list` | Verify item appears in the list |

---

### 4. TestCreateItem2 — IT020426 (8 tests)

> Create item IT020426 ("Test Item 02 April 2026") with supplier info.

| # | Test Name | Description |
|---|-----------|-------------|
| 1–8 | Same flow as TestCreateItem | Login → Admin → Item List → Add → Fill → Save → Verify |

---

### 5. TestCreateItem3 — IT070426 (8 tests)

> Create item IT070426 ("Test Item 07 April 2026") with supplier info.

| # | Test Name | Description |
|---|-----------|-------------|
| 1–8 | Same flow as TestCreateItem | Login → Admin → Item List → Add → Fill → Save → Verify |

---

### 6. TestCreateItem4 (8 tests)

> Create a 4th item with supplier info.

| # | Test Name | Description |
|---|-----------|-------------|
| 1–8 | Same flow as TestCreateItem | Login → Admin → Item List → Add → Fill → Save → Verify |

---

### 7. TestInitialLoopSize — IT020426 (8 tests)

> Set initial loop size for item IT020426.

| # | Test Name | Description |
|---|-----------|-------------|
| 1 | `test_01_login` | Log in |
| 2 | `test_02_open_admin` | Navigate to Admin module |
| 3 | `test_03_open_item_list` | Open the Item List page |
| 4 | `test_04_select_item` | Select IT020426 from the list |
| 5 | `test_05_click_cards` | Click Cards button |
| 6 | `test_06_click_add_cards` | Click Add Cards |
| 7 | `test_07_fill_units_and_next` | Fill units per card and click Next |
| 8 | `test_08_complete_wizard` | Complete the Initial Loop Size wizard |

---

### 8. TestAdjustLoopSize — IT020426 (8 tests)

> Adjust loop size for item IT020426.

| # | Test Name | Description |
|---|-----------|-------------|
| 1 | `test_01_login` | Log in |
| 2 | `test_02_open_admin` | Navigate to Admin module |
| 3 | `test_03_open_item_list` | Open the Item List page |
| 4 | `test_04_select_item` | Select IT020426 from the list |
| 5 | `test_05_click_cards` | Click Cards button |
| 6 | `test_06_open_adjust_wizard` | Open Adjust Loop Size wizard |
| 7 | `test_07_select_add_replenishment` | Select Add Replenishment option |
| 8 | `test_08_enter_cards_and_finish` | Enter cards to add and finish wizard |

---

### 9. TestExcelItemInitialLoop — IT-A140426 (8 tests)

> Set initial loop size for Excel-created item IT-A140426.

| # | Test Name | Description |
|---|-----------|-------------|
| 1–8 | Same flow as TestInitialLoopSize | Login → Admin → Item List → Select → Cards → Add → Fill → Complete |

---

### 10. TestExcelItemAdjustLoop — IT-A140426 (8 tests)

> Adjust loop size for Excel-created item IT-A140426.

| # | Test Name | Description |
|---|-----------|-------------|
| 1–8 | Same flow as TestAdjustLoopSize | Login → Admin → Item List → Select → Cards → Adjust → Add Replenishment → Finish |

---

### 11. TestITTest232Create — ITTest232 (8 tests)

> Create Kanban item ITTest232.

| # | Test Name | Description |
|---|-----------|-------------|
| 1–8 | Same flow as TestCreateItem | Login → Admin → Item List → Add → Fill → Save → Verify |

---

### 12. TestITTest232InitialLoop — ITTest232 (8 tests)

> Set initial loop size for ITTest232.

| # | Test Name | Description |
|---|-----------|-------------|
| 1–8 | Same flow as TestInitialLoopSize | Login → Admin → Item List → Select → Cards → Add → Fill → Complete |

---

### 13. TestITTest232AdjustLoop — ITTest232 (8 tests)

> Adjust loop size for ITTest232.

| # | Test Name | Description |
|---|-----------|-------------|
| 1–8 | Same flow as TestAdjustLoopSize | Login → Admin → Item List → Select → Cards → Adjust → Add Replenishment → Finish |

---

### 14. TestCreateItemITDDDD (14 tests) — NEW

> Create item ITDDDD, set initial loop size, then adjust loop size — all in one test class.

| # | Test Name | Description |
|---|-----------|-------------|
| 1 | `test_01_login` | Log in |
| 2 | `test_02_open_admin` | Navigate to Admin module |
| 3 | `test_03_open_item_list` | Open the Item List page |
| 4 | `test_04_click_add` | Click Add button |
| 5 | `test_05_fill_base_info` | Fill item base info (ITDDDD) |
| 6 | `test_06_fill_supplier_tab` | Fill supplier tab |
| 7 | `test_07_save` | Save the item |
| 8 | `test_08_verify_in_list` | Verify item in list |
| 9 | `test_09_select_item_for_loop` | Select ITDDDD for loop size setup |
| 10 | `test_10_click_cards` | Click Cards |
| 11 | `test_11_set_initial_loop_size` | Complete Initial Loop Size wizard |
| 12 | `test_12_navigate_back_to_item` | Navigate back to item list |
| 13 | `test_13_click_cards_for_adjust` | Click Cards again for adjust |
| 14 | `test_14_adjust_loop_size` | Complete Adjust Loop Size wizard |

---

### 15. TestExcelCreateAndAdjustLoop (5 tests) — NEW

> Excel-driven: for rows where `Run_Adjust_Loop=Yes`, create item + initial loop + adjust loop.

| # | Test Name | Description |
|---|-----------|-------------|
| 1 | `test_01_login` | Log in |
| 2 | `test_02_preview_excel_data` | Preview/load Excel rows to process |
| 3 | `test_03_create_excel_items` | Create items from Excel data |
| 4 | `test_04_set_initial_loop_size` | Set initial loop size for each item |
| 5 | `test_05_adjust_loop_size` | Adjust loop size for each item |

---

## File: test_item_excel_driven.py

### 16. TestItemExcelCreate (4 tests)

> Read all rows from `item_test_data.xlsx`, create each item, and verify in list.

| # | Test Name | Description |
|---|-----------|-------------|
| 1 | `test_01_load_excel_data` | Load item data from Excel |
| 2 | `test_02_login` | Log in |
| 3 | `test_03_create_items_from_excel` | Create all items from Excel rows |
| 4 | `test_04_verify_all_items_in_list` | Verify all items appear in the list |

---

### 17. TestAdjustLoopExcel (3 tests)

> For Kanban items, run Adjust Loop Size wizard.

| # | Test Name | Description |
|---|-----------|-------------|
| 1 | `test_01_load_kanban_items` | Load Kanban items from Excel |
| 2 | `test_02_login` | Log in |
| 3 | `test_03_adjust_loop_size_all_kanban` | Run Adjust Loop Size for all Kanban items |

---

## Summary

| Test Class | Tests | Item | Scope |
|------------|-------|------|-------|
| TestCreateItemsData1 | 3 | Excel rows | Bulk create from Excel |
| TestFilterItemsData1 | 3 | Excel rows | Filter & verify |
| TestCreateItem | 8 | IT010426 | Create single item |
| TestCreateItem2 | 8 | IT020426 | Create single item |
| TestCreateItem3 | 8 | IT070426 | Create single item |
| TestCreateItem4 | 8 | — | Create single item |
| TestInitialLoopSize | 8 | IT020426 | Initial loop size |
| TestAdjustLoopSize | 8 | IT020426 | Adjust loop size |
| TestExcelItemInitialLoop | 8 | IT-A140426 | Initial loop (Excel) |
| TestExcelItemAdjustLoop | 8 | IT-A140426 | Adjust loop (Excel) |
| TestITTest232Create | 8 | ITTest232 | Create Kanban item |
| TestITTest232InitialLoop | 8 | ITTest232 | Initial loop size |
| TestITTest232AdjustLoop | 8 | ITTest232 | Adjust loop size |
| TestCreateItemITDDDD | 14 | ITDDDD | Create + Initial + Adjust (E2E) |
| TestExcelCreateAndAdjustLoop | 5 | Excel rows | Create + loops (Excel) |
| TestItemExcelCreate | 4 | Excel rows | Create from Excel |
| TestAdjustLoopExcel | 3 | Kanban items | Adjust loop (Excel) |
| **Total** | **~112** | | |
