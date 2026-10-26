"""
Generate Admin Module Test Cases Word Document
"""
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import datetime

def set_cell_bg(cell, color_hex):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), color_hex)
    tcPr.append(shd)

def add_heading(doc, text, level=1, color=None):
    p = doc.add_heading(text, level=level)
    if color:
        for run in p.runs:
            run.font.color.rgb = RGBColor(*color)
    return p

def add_tc_table(doc, test_suite_name, test_cases):
    """Add a table with test cases for a given test suite."""
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'
    # Header row
    hdr = table.rows[0].cells
    hdr[0].text = '#'
    hdr[1].text = 'Test Case Name'
    hdr[2].text = 'Description'
    for cell in hdr:
        set_cell_bg(cell, '2E74B5')
        for para in cell.paragraphs:
            for run in para.runs:
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)
                run.font.size = Pt(10)
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    for i, (tc_id, tc_name, tc_desc) in enumerate(test_cases):
        row = table.add_row().cells
        row[0].text = tc_id
        row[1].text = tc_name
        row[2].text = tc_desc
        bg = 'DEEAF1' if i % 2 == 0 else 'FFFFFF'
        for cell in row:
            set_cell_bg(cell, bg)
            for para in cell.paragraphs:
                for run in para.runs:
                    run.font.size = Pt(9)

    doc.add_paragraph()


def generate_document():
    doc = Document()

    # Title
    title = doc.add_heading('Admin Module – Test Cases Summary', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in title.runs:
        run.font.color.rgb = RGBColor(31, 78, 121)

    # Metadata
    meta = doc.add_paragraph()
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = meta.add_run(f'Project: QALS11  |  Module: Admin  |  Generated: {datetime.date.today().strftime("%d %b %Y")}')
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(89, 89, 89)

    doc.add_paragraph()

    # ─── 1. CALENDAR MENU ───────────────────────────────────────────
    add_heading(doc, '1. Calendar Menu', level=1, color=(31, 78, 121))
    doc.add_paragraph('File: Admin/Calender/Calender.py  |  Class: TestCalender').runs[0].font.italic = True

    calendar_tcs = [
        ('TC-01', 'Add New Holiday',                        'Add a single holiday to the calendar'),
        ('TC-02', 'Edit Holiday',                           'Edit an existing holiday entry'),
        ('TC-03', 'Add Range of Holidays',                  'Add a date range as holidays'),
        ('TC-04', 'Delete Holiday',                         'Delete an existing holiday'),
        ('TC-05', 'Convert Active Date to Holiday',         'Convert an active working date to a holiday'),
        ('TC-06', 'Direct Convert Specific Date to Holiday','Directly convert a specific date to holiday'),
        ('TC-07', 'Direct Convert Random Active Date to Holiday', 'Directly convert a random active date to holiday'),
    ]
    add_tc_table(doc, 'TestCalender', calendar_tcs)

    # ─── 2. ITEM MENU ───────────────────────────────────────────────
    add_heading(doc, '2. Item Menu', level=1, color=(31, 78, 121))

    # 2.1 Item Create (test_item_create.py)
    add_heading(doc, '2.1 Item Creation – Manual (test_item_create.py)', level=2)

    item_create_base = [
        ('TC-01', 'Login',              'Login to the application'),
        ('TC-02', 'Open Admin',         'Navigate to Admin module'),
        ('TC-03', 'Click Item Menu',    'Open Item menu from Admin'),
        ('TC-04', 'Click Add',          'Click Add button to open new item form'),
        ('TC-05', 'Fill Base Information', 'Fill in the base/general information fields'),
        ('TC-06', 'Fill Supplier Tab',  'Fill Supplier tab details'),
        ('TC-07', 'Save Item',          'Save the newly created item'),
        ('TC-08', 'Verify Item in List','Verify the item appears in the item list'),
    ]
    doc.add_paragraph('Class: TestItemCreate (Dataset 1)').runs[0].font.italic = True
    add_tc_table(doc, 'TestItemCreate', item_create_base)

    doc.add_paragraph('Class: TestItemCreate2 (Dataset 2)').runs[0].font.italic = True
    add_tc_table(doc, 'TestItemCreate2', item_create_base)

    doc.add_paragraph('Class: TestItemCreate3 (Dataset 3)').runs[0].font.italic = True
    add_tc_table(doc, 'TestItemCreate3', item_create_base)

    # 2.2 NewItemCreationandAdjustLoopSize.py
    add_heading(doc, '2.2 New Item Creation & Adjust Loop Size (NewItemCreationandAdjustLoopSize.py)', level=2)

    tcs_create_items_data = [
        ('TC-01', 'Load Excel',         'Load Excel file with item data'),
        ('TC-02', 'Login',              'Login to application'),
        ('TC-03', 'Create All Items',   'Create all items from loaded Excel data'),
    ]
    doc.add_paragraph('Class: TestCreateItemsData1 – Bulk create from Excel').runs[0].font.italic = True
    add_tc_table(doc, 'TestCreateItemsData1', tcs_create_items_data)

    tcs_filter_items = [
        ('TC-01', 'Login',              'Login to application'),
        ('TC-02', 'Clear Filter',       'Clear existing item filters'),
        ('TC-03', 'Filter by Each Item','Filter item list by each item in data set'),
    ]
    doc.add_paragraph('Class: TestFilterItemsData1 – Filter items').runs[0].font.italic = True
    add_tc_table(doc, 'TestFilterItemsData1', tcs_filter_items)

    tcs_create_item_single = [
        ('TC-01', 'Login',              'Login to application'),
        ('TC-02', 'Open Admin',         'Open Admin module'),
        ('TC-03', 'Open Item List',     'Navigate to Item list'),
        ('TC-04', 'Click Add',          'Click Add to open new item form'),
        ('TC-05', 'Fill Base Info',     'Fill in base information'),
        ('TC-06', 'Fill Supplier Tab',  'Fill Supplier tab'),
        ('TC-07', 'Save',               'Save the item'),
        ('TC-08', 'Verify in List',     'Verify item in list'),
    ]
    for cls in ['TestCreateItem', 'TestCreateItem2', 'TestCreateItem3', 'TestCreateItem4']:
        doc.add_paragraph(f'Class: {cls} – Single item create variation').runs[0].font.italic = True
        add_tc_table(doc, cls, tcs_create_item_single)

    tcs_initial_loop = [
        ('TC-01', 'Login',              'Login to application'),
        ('TC-02', 'Open Admin',         'Open Admin module'),
        ('TC-03', 'Open Item List',     'Navigate to Item list'),
        ('TC-04', 'Select Item',        'Select target item'),
        ('TC-05', 'Click Cards',        'Click Cards option'),
        ('TC-06', 'Click Add Cards',    'Click Add Cards button'),
        ('TC-07', 'Fill Units and Next','Enter unit values and proceed'),
        ('TC-08', 'Complete Wizard',    'Complete the loop size wizard'),
    ]
    doc.add_paragraph('Class: TestInitialLoopSize – Set initial loop size').runs[0].font.italic = True
    add_tc_table(doc, 'TestInitialLoopSize', tcs_initial_loop)

    tcs_adjust_loop = [
        ('TC-01', 'Login',                    'Login to application'),
        ('TC-02', 'Open Admin',               'Open Admin module'),
        ('TC-03', 'Open Item List',           'Navigate to Item list'),
        ('TC-04', 'Select Item',              'Select target item'),
        ('TC-05', 'Click Cards',              'Click Cards option'),
        ('TC-06', 'Open Adjust Wizard',       'Open the Adjust Loop Size wizard'),
        ('TC-07', 'Select Add Replenishment', 'Select Add Replenishment option'),
        ('TC-08', 'Enter Cards and Finish',   'Enter card count and finish'),
    ]
    doc.add_paragraph('Class: TestAdjustLoopSize – Adjust loop size').runs[0].font.italic = True
    add_tc_table(doc, 'TestAdjustLoopSize', tcs_adjust_loop)

    doc.add_paragraph('Class: TestExcelItemInitialLoop – Set initial loop size from Excel data').runs[0].font.italic = True
    add_tc_table(doc, 'TestExcelItemInitialLoop', tcs_initial_loop)

    doc.add_paragraph('Class: TestExcelItemAdjustLoop – Adjust loop size from Excel data').runs[0].font.italic = True
    add_tc_table(doc, 'TestExcelItemAdjustLoop', tcs_adjust_loop)

    # ITTest232 group
    doc.add_paragraph('Class: TestITTest232Create – IT232 item create').runs[0].font.italic = True
    add_tc_table(doc, 'TestITTest232Create', tcs_create_item_single)

    doc.add_paragraph('Class: TestITTest232InitialLoop – IT232 set initial loop').runs[0].font.italic = True
    add_tc_table(doc, 'TestITTest232InitialLoop', tcs_initial_loop)

    doc.add_paragraph('Class: TestITTest232AdjustLoop – IT232 adjust loop').runs[0].font.italic = True
    add_tc_table(doc, 'TestITTest232AdjustLoop', tcs_adjust_loop)

    # ITDDDD group
    tcs_itdddd = [
        ('TC-01', 'Login',                  'Login to application'),
        ('TC-02', 'Open Admin',             'Open Admin module'),
        ('TC-03', 'Open Item List',         'Navigate to Item list'),
        ('TC-04', 'Click Add',              'Click Add to open new item form'),
        ('TC-05', 'Fill Base Info',         'Fill in base information'),
        ('TC-06', 'Fill Supplier Tab',      'Fill Supplier tab'),
        ('TC-07', 'Save',                   'Save the item'),
        ('TC-08', 'Verify in List',         'Verify item in list'),
        ('TC-09', 'Select Item for Loop',   'Select item to configure loop'),
        ('TC-10', 'Click Cards',            'Click Cards option'),
        ('TC-11', 'Set Initial Loop Size',  'Set the initial loop size'),
        ('TC-12', 'Navigate Back to Item',  'Navigate back to item page'),
        ('TC-13', 'Click Cards for Adjust', 'Click Cards for adjust operation'),
        ('TC-14', 'Adjust Loop Size',       'Adjust loop size to new value'),
    ]
    doc.add_paragraph('Class: TestCreateItemITDDDD – ITDDDD full create & loop flow').runs[0].font.italic = True
    add_tc_table(doc, 'TestCreateItemITDDDD', tcs_itdddd)

    # TestExcelCreateAndAdjustLoop
    tcs_excel_create_adjust = [
        ('TC-01', 'Login',               'Login to application'),
        ('TC-02', 'Preview Excel Data',  'Preview items from Excel file'),
        ('TC-03', 'Create Excel Items',  'Create all items from Excel'),
        ('TC-04', 'Set Initial Loop Size','Set initial loop size for all items'),
        ('TC-05', 'Adjust Loop Size',    'Adjust loop size for all items'),
    ]
    doc.add_paragraph('Class: TestExcelCreateAndAdjustLoop – Excel-driven create and adjust').runs[0].font.italic = True
    add_tc_table(doc, 'TestExcelCreateAndAdjustLoop', tcs_excel_create_adjust)

    # TestCreateItemIT190426
    doc.add_paragraph('Class: TestCreateItemIT190426 – IT190426 item create').runs[0].font.italic = True
    add_tc_table(doc, 'TestCreateItemIT190426', tcs_create_item_single)

    # 2.3 test_item_excel_driven.py
    add_heading(doc, '2.3 Item Excel-Driven Tests (test_item_excel_driven.py)', level=2)

    tcs_item_excel_create = [
        ('TC-01', 'Load Excel Data',         'Load item data from Excel file'),
        ('TC-02', 'Login',                   'Login to application'),
        ('TC-03', 'Create Items from Excel', 'Create all items from Excel data'),
        ('TC-04', 'Verify All Items in List','Verify all created items appear in list'),
    ]
    doc.add_paragraph('Class: TestItemExcelCreate – Bulk create from Excel (driven)').runs[0].font.italic = True
    add_tc_table(doc, 'TestItemExcelCreate', tcs_item_excel_create)

    tcs_adjust_loop_excel = [
        ('TC-01', 'Load Kanban Items',          'Load Kanban item data from Excel'),
        ('TC-02', 'Login',                      'Login to application'),
        ('TC-03', 'Adjust Loop Size All Kanban','Adjust loop size for all Kanban items'),
    ]
    doc.add_paragraph('Class: TestAdjustLoopExcel – Adjust loop for all Kanban items from Excel').runs[0].font.italic = True
    add_tc_table(doc, 'TestAdjustLoopExcel', tcs_adjust_loop_excel)

    # ─── 3. SUPPLIER MENU ───────────────────────────────────────────
    add_heading(doc, '3. Supplier Menu', level=1, color=(31, 78, 121))
    doc.add_paragraph('File: Admin/Supplier/InternalSupplier.py  |  Class: TestInternalSupplierConfig').runs[0].font.italic = True

    supplier_tcs = [
        ('TC-01', 'Login and Navigate to Supplier',       'Login and go to Supplier section'),
        ('TC-02', 'Switch to Internal & Search WCLine',   'Switch to Internal supplier tab and search for WCLine'),
        ('TC-03', 'Open WCLine Configuration',            'Open the configuration page for WCLine'),
        ('TC-04', 'Update Configuration Tabs',            'Update all configuration tabs (General, Schedule, etc.)'),
        ('TC-05', 'Generate Report',                      'Generate and save supplier configuration report'),
    ]
    add_tc_table(doc, 'TestInternalSupplierConfig', supplier_tcs)

    # ─── 4. USERS MENU ───────────────────────────────────────────────
    add_heading(doc, '4. Users Menu', level=1, color=(31, 78, 121))

    # 4.1 users.py
    add_heading(doc, '4.1 User CRUD Operations (users.py)', level=2)

    tcs_add_user = [
        ('TC-01', 'Open Create Form',    'Open the user creation form'),
        ('TC-02', 'Fill Form and Save',  'Fill in user details and save'),
        ('TC-03', 'Verify User in List', 'Verify newly created user appears in list'),
    ]
    doc.add_paragraph('Class: TestAddUser – Create a new user').runs[0].font.italic = True
    add_tc_table(doc, 'TestAddUser', tcs_add_user)

    tcs_edit_user = [
        ('TC-01', 'Search and Select',  'Search for user and select from list'),
        ('TC-02', 'Edit Fields',        'Modify user fields'),
        ('TC-03', 'Save and Verify',    'Save changes and verify updated values'),
    ]
    doc.add_paragraph('Class: TestEditUser – Edit an existing user').runs[0].font.italic = True
    add_tc_table(doc, 'TestEditUser', tcs_edit_user)

    tcs_view_user = [
        ('TC-01', 'Search and Select',    'Search for user and select from list'),
        ('TC-02', 'View User Details',    'View user details in read-only mode'),
        ('TC-03', 'Cancel and Return',    'Cancel view and return to list'),
    ]
    doc.add_paragraph('Class: TestViewUser – View user details').runs[0].font.italic = True
    add_tc_table(doc, 'TestViewUser', tcs_view_user)

    tcs_disable_user = [
        ('TC-01', 'Search and Select',    'Search for user and select from list'),
        ('TC-02', 'Click Disable Button', 'Click the Disable button'),
        ('TC-03', 'Confirm Disable',      'Confirm disable action in dialog'),
    ]
    doc.add_paragraph('Class: TestDisableUser – Disable a user').runs[0].font.italic = True
    add_tc_table(doc, 'TestDisableUser', tcs_disable_user)

    tcs_enable_user = [
        ('TC-01', 'Open Disabled List',  'Open the disabled users list'),
        ('TC-02', 'Search and Select',   'Search for disabled user and select'),
        ('TC-03', 'Enable User',         'Click Enable button'),
        ('TC-04', 'Verify User Active',  'Verify user appears in active list'),
    ]
    doc.add_paragraph('Class: TestEnableUser – Re-enable a disabled user').runs[0].font.italic = True
    add_tc_table(doc, 'TestEnableUser', tcs_enable_user)

    # 4.2 UsercreationValidations.py
    add_heading(doc, '4.2 User Creation Validations (UsercreationValidations.py)', level=2)

    tcs_create_manual = [
        ('TC-01', 'Verify Login',          'Verify login works successfully'),
        ('TC-02', 'Create plantadm01',     'Create user plantadm01'),
        ('TC-03', 'Create plantadm02',     'Create user plantadm02'),
        ('TC-04', 'Create plantadm03',     'Create user plantadm03'),
        ('TC-05', 'Create plantadm04',     'Create user plantadm04'),
        ('TC-06', 'Create plantadm05',     'Create user plantadm05'),
        ('TC-07', 'Create user170426',     'Create user with ID user170426'),
    ]
    doc.add_paragraph('Class: TestCreateUsersManual – Manual user creation').runs[0].font.italic = True
    add_tc_table(doc, 'TestCreateUsersManual', tcs_create_manual)

    tcs_create_from_excel = [
        ('TC-01', 'Read Excel File',         'Read user data from Excel file'),
        ('TC-02', 'Create Users from Excel', 'Create all users from Excel data'),
    ]
    doc.add_paragraph('Class: TestCreateUsersFromExcel – Create users from Excel').runs[0].font.italic = True
    add_tc_table(doc, 'TestCreateUsersFromExcel', tcs_create_from_excel)

    tcs_export_creds = [
        ('TC-01', 'Export to Excel', 'Export user credentials to Excel file'),
    ]
    doc.add_paragraph('Class: TestExportCredentials – Export credentials').runs[0].font.italic = True
    add_tc_table(doc, 'TestExportCredentials', tcs_export_creds)

    # 4.3 users_backup.py (reference/backup file)
    add_heading(doc, '4.3 Users Backup / Extended Tests (users_backup.py)', level=2)
    doc.add_paragraph(
        'Note: This is a backup/extended test file covering the same operations with more detailed steps.'
    ).runs[0].font.italic = True

    tcs_users_list = [
        ('TC-01', 'Login',            'Login to application'),
        ('TC-02', 'Open Admin Module','Open Admin module'),
        ('TC-03', 'View Users List',  'View the Users list page'),
    ]
    doc.add_paragraph('Class: TestUsersList – View users list').runs[0].font.italic = True
    add_tc_table(doc, 'TestUsersList', tcs_users_list)

    tcs_edit_user_bkp = [
        ('TC-01', 'Login',                        'Login to application'),
        ('TC-02', 'Navigate to Users List',       'Navigate to Users list'),
        ('TC-03', 'Open Edit Page for plantadm01','Open edit page for plantadm01'),
        ('TC-04', 'Fill in Mandatory Fields',     'Fill in all mandatory fields'),
        ('TC-05', 'Save User',                    'Save the user'),
    ]
    doc.add_paragraph('Class: TestEditUser (backup) – Edit user with detailed steps').runs[0].font.italic = True
    add_tc_table(doc, 'TestEditUser_backup', tcs_edit_user_bkp)

    tcs_create_users_bkp = [
        ('TC-01', 'Login as Admin',            'Login as admin user'),
        ('TC-02', 'Create plantadm01',         'Create user plantadm01'),
        ('TC-03', 'Create plantadm02',         'Create user plantadm02'),
        ('TC-04', 'Create plantadm03',         'Create user plantadm03'),
        ('TC-05', 'Create plantadm04',         'Create user plantadm04'),
        ('TC-06', 'Create plantadm05',         'Create user plantadm05'),
        ('TC-07', 'Create user150426',         'Create user150426'),
        ('TC-08', 'Export Credentials to Excel','Export user credentials to Excel'),
    ]
    doc.add_paragraph('Class: TestCreateUsers (backup) – Create multiple users').runs[0].font.italic = True
    add_tc_table(doc, 'TestCreateUsers_backup', tcs_create_users_bkp)

    tcs_view_user_bkp = [
        ('TC-01', 'Login',                    'Login to application'),
        ('TC-02', 'Search User',              'Search for specific user'),
        ('TC-03', 'Select and Click View',    'Select user and click View'),
        ('TC-04', 'Verify and Cancel',        'Verify user data and cancel'),
    ]
    doc.add_paragraph('Class: TestViewUser (backup) – View user details').runs[0].font.italic = True
    add_tc_table(doc, 'TestViewUser_backup', tcs_view_user_bkp)

    tcs_disable_bkp = [
        ('TC-01', 'Login',              'Login to application'),
        ('TC-02', 'Open User List',     'Open Users list'),
        ('TC-03', 'Search User',        'Search for target user'),
        ('TC-04', 'Select User Row',    'Select the user row'),
        ('TC-05', 'Click Disable',      'Click Disable button'),
        ('TC-06', 'Confirm Disable',    'Confirm disable in dialog'),
        ('TC-07', 'Verify User Disabled','Verify user is now disabled'),
    ]
    doc.add_paragraph('Class: TestDisableUser (backup) – Disable user detailed flow').runs[0].font.italic = True
    add_tc_table(doc, 'TestDisableUser_backup', tcs_disable_bkp)

    tcs_enable_bkp = [
        ('TC-01', 'Login',              'Login to application'),
        ('TC-02', 'Open Disabled List', 'Open disabled users list'),
        ('TC-03', 'Search User',        'Search for disabled user'),
        ('TC-04', 'Select User Row',    'Select the user row'),
        ('TC-05', 'Click Enable',       'Click Enable button'),
        ('TC-06', 'Confirm Enable',     'Confirm enable action'),
        ('TC-07', 'Verify User Enabled','Verify user is now active'),
    ]
    doc.add_paragraph('Class: TestEnableUser (backup) – Enable user detailed flow').runs[0].font.italic = True
    add_tc_table(doc, 'TestEnableUser_backup', tcs_enable_bkp)

    tcs_user150426 = [
        ('TC-01', 'Login',         'Login to application'),
        ('TC-02', 'Create User',   'Create a specific test user (user150426)'),
        ('TC-03', 'Edit User',     'Edit the created user'),
        ('TC-04', 'View User',     'View user details'),
        ('TC-05', 'Disable User',  'Disable the user'),
        ('TC-06', 'Enable User',   'Re-enable the user'),
        ('TC-07', 'Update Email',  'Update user email address'),
        ('TC-08', 'Assign Groups', 'Assign user groups'),
    ]
    doc.add_paragraph('Class: TestUser150426_1 – Full user lifecycle flow').runs[0].font.italic = True
    add_tc_table(doc, 'TestUser150426_1', tcs_user150426)

    # ─── 5. WORKCENTER MENU ──────────────────────────────────────────
    add_heading(doc, '5. Workcenter Menu', level=1, color=(31, 78, 121))

    # 5.1 Workcenter.py
    add_heading(doc, '5.1 Workcenter CRUD & Configuration (Workcenter.py)', level=2)
    doc.add_paragraph('Class: TestWorkcenter').runs[0].font.italic = True

    wc_tcs = [
        ('TC-01', 'Login & Navigate to Workcenter',       'Login and navigate to Workcenter menu'),
        ('TC-02', 'Create New Workcenter',                 'Create a new Workcenter'),
        ('TC-03', 'Generate Creation Report',              'Generate and save workcenter creation report'),
        ('TC-04', 'Edit Workcenter',                       'Edit existing workcenter details'),
        ('TC-05', 'Generate Edit Report',                  'Generate and save workcenter edit report'),
        ('TC-06', 'Navigate to Workcenter Users',          'Navigate to the Users tab of Workcenter'),
        ('TC-07', 'Add Workcenter User',                   'Add a new user to the Workcenter'),
        ('TC-08', 'Verify User in Workcenter List',        'Verify newly added user is in the list'),
        ('TC-09', 'Edit Workcenter User',                  'Edit an existing Workcenter user'),
        ('TC-10', 'View Workcenter User',                  'View Workcenter user details'),
        ('TC-11', 'Disable & Enable Workcenter User',      'Disable and then re-enable a Workcenter user'),
        ('TC-12', 'Generate Workcenter Users Report',      'Generate report for Workcenter users'),
        ('TC-13', 'Update Schedule Config',                'Update schedule configuration for Workcenter'),
        ('TC-14', 'Add Shipping Rule',                     'Add a new shipping rule'),
        ('TC-15', 'Print Shipping Rules',                  'Print the list of shipping rules'),
        ('TC-16', 'Export Shipping Rules',                 'Export shipping rules to file'),
        ('TC-17', 'Move Up Shipping Rule',                 'Move a shipping rule up in priority order'),
        ('TC-18', 'Move Down Shipping Rule',               'Move a shipping rule down in priority order'),
        ('TC-19', 'Delete Shipping Rule',                  'Delete an existing shipping rule'),
        ('TC-20', 'Add RYG Rule',                          'Add a Red-Yellow-Green (RYG) rule'),
        ('TC-21', 'Edit RYG Rule',                         'Edit an existing RYG rule'),
        ('TC-22', 'Delete RYG Rule',                       'Delete an existing RYG rule'),
        ('TC-23', 'Check Kanban Formula',                  'Validate the Kanban formula values'),
        ('TC-24', 'Attach File to Workcenter',             'Attach a file/image to Workcenter'),
        ('TC-25', 'Edit Attachment',                       'Edit the attached file metadata'),
        ('TC-26', 'Crop Attachment Image',                 'Crop the attached image'),
        ('TC-27', 'Filter Workcenter List',                'Filter the Workcenter list view'),
    ]
    add_tc_table(doc, 'TestWorkcenter', wc_tcs)

    # 5.2 WorkcenterConfiguration.py
    add_heading(doc, '5.2 Workcenter Configuration (WorkcenterConfiguration.py)', level=2)
    doc.add_paragraph('Class: TestWorkcenterConfiguration').runs[0].font.italic = True

    wc_config_tcs = [
        ('TC-01', 'Login & Navigate to Workcenter', 'Login and navigate to Workcenter'),
        ('TC-02', 'Search & Select Workcenter',      'Search and select target Workcenter'),
        ('TC-03', 'Open Configuration',              'Open Workcenter configuration page'),
        ('TC-04', 'Update Configuration Tabs',       'Update all configuration tab settings'),
        ('TC-05', 'Generate Report',                 'Generate and save configuration report'),
    ]
    add_tc_table(doc, 'TestWorkcenterConfiguration', wc_config_tcs)

    # 5.3 ProductionSequenceConfiguration.py
    add_heading(doc, '5.3 Production Sequence Configuration (ProductionSequenceConfiguration.py)', level=2)
    doc.add_paragraph('Class: TestProductionSequenceConfiguration').runs[0].font.italic = True

    prod_seq_tcs = [
        ('TC-01', 'Login & Navigate to Workcenter',          'Login and navigate to Workcenter'),
        ('TC-02', 'Search & Select Workcenter',               'Search and select target Workcenter'),
        ('TC-03', 'Open Production Sequence Configuration',   'Open Production Sequence config page'),
        ('TC-04', 'Update Production Sequence Tabs',          'Update all production sequence tab settings'),
        ('TC-05', 'Generate Report',                          'Generate and save production sequence report'),
    ]
    add_tc_table(doc, 'TestProductionSequenceConfiguration', prod_seq_tcs)

    # ─── 6. ENTITIES MENU ──────────────────────────────────────────
    add_heading(doc, '6. Entities Menu', level=1, color=(31, 78, 121))
    doc.add_paragraph(
        'Path: Admin > Entities  |  Files: admin/Entities/*.py  |  Style: function-based (not pytest classes)'
    ).runs[0].font.italic = True

    # Common 3-step pattern for ABC Code, Carrier, Exception Code, Logistics Mode, Notes, Production Issue
    tcs_entity_3step = [
        ('TC-01', 'Add',   'Navigate to entity list, click +Add, fill Code/Title/Description, save and verify in list'),
        ('TC-02', 'Edit',  'Search for existing entity, click Edit, update fields, save and verify updated values'),
        ('TC-03', 'View',  'Search for existing entity, click View (read-only), verify details, click Cancel'),
    ]

    entities_simple = [
        ('ABC Code',        'ABCCode.py',       'TC-ABC-01/02/03', 'Admin > Entities > ABC Code'),
        ('Carrier',         'Carrier.py',        'TC-CAR-01/02/03', 'Admin > Entities > Carrier'),
        ('Exception Code',  'ExceptionCode.py',  'TC-EC-01/02/03',  'Admin > Entities > Exception Code'),
        ('Logistics Mode',  'LogisticsMode.py',  'TC-LM-01/02/03',  'Admin > Entities > Logistics Mode'),
        ('Notes',           'Notes.py',          'TC-NOT-01/02/03', 'Admin > Entities > Notes'),
        ('Production Issue','ProductionIssue.py','TC-PI-01/02/03',  'Admin > Entities > Production Issue'),
    ]

    for name, file, tc_ids, nav in entities_simple:
        add_heading(doc, f'6.x {name} ({file})', level=2)
        doc.add_paragraph(f'Navigation: {nav}  |  TC IDs: {tc_ids}').runs[0].font.italic = True
        add_tc_table(doc, name, tcs_entity_3step)

    # 6.7 Commodity Code – extended (CommodityCode.py)
    add_heading(doc, '6.7 Commodity Code (CommodityCode.py)', level=2)
    doc.add_paragraph('Navigation: Admin > Entities > Commodity Code  |  Extended with RYG Rules').runs[0].font.italic = True

    tcs_commodity = [
        ('TC-CC-01', 'Create Commodity Code',         'Click +Add, fill Code/Title/Description with random values, save and verify in list'),
        ('TC-CC-02', 'Edit Commodity Code',           'Search for existing code, click Edit, update Code/Title/Description, save and verify'),
        ('TC-CC-03', 'View Commodity Code Details',   'Find existing code, click View, verify Code/Title/Desc displayed, click Cancel'),
        ('TC-CC-04', 'Add RYG Rule to Commodity Code','Select a code, open More Options > RYG Rules, click +Add, select rule, enter Red/Yellow values, save'),
        ('TC-CC-05', 'Edit RYG Rule',                 'Select existing RYG rule on Commodity Code, click Edit, modify values, save and verify'),
        ('TC-CC-06', 'Delete RYG Rule',               'Select existing RYG rule on Commodity Code, click Delete, confirm deletion'),
    ]
    add_tc_table(doc, 'CommodityCode', tcs_commodity)

    # 6.8 User Group (admin/UserGroup.py)
    add_heading(doc, '6.8 User Group (UserGroup.py)', level=2)
    doc.add_paragraph('Navigation: Admin > User Group (Local tab)  |  File: admin/UserGroup.py').runs[0].font.italic = True

    tcs_user_group = [
        ('TC-UG-01', 'Create Local User Group',    'Login → Admin > User Group → Local tab → +Add → fill Title/Description → select Plant Users radio → select privileges → Save → verify in list'),
        ('TC-UG-02', 'Edit Local User Group',      'Search group → click Edit → modify Title/Description → toggle privileges (disable Edit User, enable others) → Save'),
        ('TC-UG-03', 'View Local User Group',      'Search group → click View → read-only page → verify fields → click Cancel → return to list'),
        ('TC-UG-04', 'Assign Users to User Group', 'Search group → Assigned Users → click +Assign User(s) → select user checkbox → click +Assign → click Back'),
        ('TC-UG-05', 'My Routines',                'Search group → click My Routines → select Daily/Weekly/Monthly → Save'),
        ('TC-UG-06', 'Clone User Group',           'Search group → click Clone Group → modify Title/Description → optionally modify privileges → Save → verify cloned group in list'),
        ('TC-UG-07', 'Delete User Group',          'Search group → select row → click Delete toolbar button → click Yes in confirmation → verify group removed from list'),
        ('TC-UG-08', 'View System User Groups',    'Navigate to System Group List → search for system group → click View → verify → click Cancel'),
    ]
    add_tc_table(doc, 'UserGroup', tcs_user_group)

    # ─── SUMMARY ──────────────────────────────────────────────────
    doc.add_page_break()
    add_heading(doc, 'Summary – Test Case Count by Menu', level=1, color=(31, 78, 121))

    summary_table = doc.add_table(rows=1, cols=3)
    summary_table.style = 'Table Grid'
    hdr = summary_table.rows[0].cells
    hdr[0].text = 'Menu'
    hdr[1].text = 'Test Suites / Functions'
    hdr[2].text = 'Total Test Cases'
    for cell in hdr:
        set_cell_bg(cell, '1F4E79')
        for para in cell.paragraphs:
            for run in para.runs:
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)
                run.font.size = Pt(10)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    summary_data = [
        ('Calendar',   '1 class',    '7'),
        ('Item',       '22 classes', '122+'),
        ('Supplier',   '1 class',    '5'),
        ('Users',      '12 classes', '51'),
        ('Workcenter', '3 classes',  '37'),
        ('Entities',   '8 modules',  '24'),
        ('TOTAL',      '47 modules', '246+'),
    ]
    for i, (menu, suites, count) in enumerate(summary_data):
        row = summary_table.add_row().cells
        row[0].text = menu
        row[1].text = suites
        row[2].text = count
        bg = 'DEEAF1' if i % 2 == 0 else 'FFFFFF'
        if menu == 'TOTAL':
            bg = 'BDD7EE'
        for cell in row:
            set_cell_bg(cell, bg)
            for para in cell.paragraphs:
                for run in para.runs:
                    run.font.size = Pt(9)
                    if menu == 'TOTAL':
                        run.font.bold = True

    out_path = r'c:\Prcatices-AI\qa_automation\tests\QALS11\Admin\Admin_TestCases.docx'
    doc.save(out_path)
    print(f'Document saved: {out_path}')


if __name__ == '__main__':
    generate_document()
