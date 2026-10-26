"""
Generate QALS11 Automated Test Cases Summary Document
Produces a Word (.docx) file organized by Suite > Menu > Test Module > Test Cases
"""

from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from datetime import date

# ─────────────────────────────────────────────────────────────────────────────
# DATA  –  Suite > Menu > [ (Module, TestCase, Description) ]
# ─────────────────────────────────────────────────────────────────────────────

SUITE_DATA = [

    # ══════════════════════════════════════════════════════════════════════════
    # SUITE 1 : ADMIN
    # ══════════════════════════════════════════════════════════════════════════
    {
        "suite": "Admin",
        "color": RGBColor(0x1F, 0x49, 0x7D),   # dark-blue header
        "menus": [
            {
                "menu": "Admin > Entities > ABC Code",
                "rows": [
                    ("test_ABCCode", "test_tc_abc_01_add_code",  "Add a new ABC Code and verify it is saved"),
                    ("test_ABCCode", "test_tc_abc_02_edit_code", "Edit an existing ABC Code and verify update"),
                ],
            },
            {
                "menu": "Admin > Entities > Break Reason Code",
                "rows": [
                    ("test_BreakReasonCode", "test_add_break_reason_code",  "Add a new Break Reason Code"),
                    ("test_BreakReasonCode", "test_edit_break_reason_code", "Edit an existing Break Reason Code"),
                    ("test_BreakReasonCode", "test_view_break_reason_code", "View Break Reason Code details"),
                ],
            },
            {
                "menu": "Admin > Entities > Carrier",
                "rows": [
                    ("test_Carrier", "test_add_carrier",  "Add a new Carrier record"),
                    ("test_Carrier", "test_edit_carrier", "Edit an existing Carrier"),
                    ("test_Carrier", "test_view_carrier", "View Carrier details"),
                ],
            },
            {
                "menu": "Admin > Entities > Commodity Code",
                "rows": [
                    ("test_CommodityCode", "test_create_commodity_code",         "Create a new Commodity Code"),
                    ("test_CommodityCode", "test_view_commodity_code_details",   "View Commodity Code details page"),
                    ("test_CommodityCode", "test_add_ryg_rule_to_commodity_code","Add RYG rule to Commodity Code"),
                    ("test_CommodityCode", "test_edit_ryg_rule",                 "Edit an existing RYG rule"),
                    ("test_CommodityCode", "test_delete_ryg_rule",               "Delete a RYG rule from Commodity Code"),
                    ("test_CommodityCode", "test_assign_items_to_commodity_code","Assign items to Commodity Code"),
                ],
            },
            {
                "menu": "Admin > Entities > Container",
                "rows": [
                    ("test_Container", "test_add_container",  "Add a new Container type"),
                    ("test_Container", "test_edit_container", "Edit an existing Container"),
                    ("test_Container", "test_view_container", "View Container details"),
                ],
            },
            {
                "menu": "Admin > Entities > Exception Code",
                "rows": [
                    ("test_ExceptionCode", "test_add_exception_code",  "Add a new Exception Code"),
                    ("test_ExceptionCode", "test_edit_exception_code", "Edit an existing Exception Code"),
                    ("test_ExceptionCode", "test_view_exception_code", "View Exception Code details"),
                ],
            },
            {
                "menu": "Admin > Entities > Location Code",
                "rows": [
                    ("test_LocationCode", "test_add_location_code",  "Add a new Location Code"),
                    ("test_LocationCode", "test_edit_location_code", "Edit an existing Location Code"),
                    ("test_LocationCode", "test_view_location_code", "View Location Code details"),
                ],
            },
            {
                "menu": "Admin > Entities > Logistics Mode",
                "rows": [
                    ("test_logisticsMode", "test_add_logistics_mode",  "Add a new Logistics Mode"),
                    ("test_logisticsMode", "test_edit_logistics_mode", "Edit an existing Logistics Mode"),
                    ("test_logisticsMode", "test_view_logistics_mode", "View Logistics Mode details"),
                ],
            },
            {
                "menu": "Admin > Entities > Machine",
                "rows": [
                    ("test_Machine", "test_add_machine",  "Add a new Machine record"),
                    ("test_Machine", "test_edit_machine", "Edit an existing Machine"),
                    ("test_Machine", "test_view_machine", "View Machine details"),
                ],
            },
            {
                "menu": "Admin > Entities > Notes",
                "rows": [
                    ("test_Notes", "test_add_note",  "Add a new Note template"),
                    ("test_Notes", "test_edit_note", "Edit an existing Note"),
                    ("test_Notes", "test_view_note", "View Note details"),
                ],
            },
            {
                "menu": "Admin > Entities > Operation",
                "rows": [
                    ("test_Operation", "test_add_operation",  "Add a new Operation"),
                    ("test_Operation", "test_edit_operation", "Edit an existing Operation"),
                    ("test_Operation", "test_view_operation", "View Operation details"),
                ],
            },
            {
                "menu": "Admin > Entities > Operation Params",
                "rows": [
                    ("test_OperationParams", "test_add_operation_params",  "Add new Operation Parameters"),
                    ("test_OperationParams", "test_edit_operation_params", "Edit existing Operation Parameters"),
                    ("test_OperationParams", "test_view_operation_params", "View Operation Parameters details"),
                ],
            },
            {
                "menu": "Admin > Entities > Printer",
                "rows": [
                    ("test_Printer", "test_add_printer",  "Add a new Printer configuration"),
                    ("test_Printer", "test_edit_printer", "Edit an existing Printer"),
                    ("test_Printer", "test_view_printer", "View Printer details"),
                ],
            },
            {
                "menu": "Admin > Entities > Production Issue",
                "rows": [
                    ("test_ProductionIssue", "test_add_production_issue",  "Add a new Production Issue type"),
                    ("test_ProductionIssue", "test_edit_production_issue", "Edit an existing Production Issue"),
                    ("test_ProductionIssue", "test_view_production_issue", "View Production Issue details"),
                ],
            },
            {
                "menu": "Admin > Entities > Reschedule Reason",
                "rows": [
                    ("test_RescheduleReason", "test_add_reschedule_reason",  "Add a new Reschedule Reason"),
                    ("test_RescheduleReason", "test_edit_reschedule_reason", "Edit an existing Reschedule Reason"),
                    ("test_RescheduleReason", "test_view_reschedule_reason", "View Reschedule Reason details"),
                ],
            },
            {
                "menu": "Admin > Entities > Scrap Reason",
                "rows": [
                    ("test_ScrapReason", "test_add_scrap_reason",  "Add a new Scrap Reason"),
                    ("test_ScrapReason", "test_edit_scrap_reason", "Edit an existing Scrap Reason"),
                    ("test_ScrapReason", "test_view_scrap_reason", "View Scrap Reason details"),
                ],
            },
            {
                "menu": "Admin > Entities > Skip Lot Plan",
                "rows": [
                    ("test_SkipLotPlan", "test_add_skip_lot_plan",  "Add a new Skip Lot Plan"),
                    ("test_SkipLotPlan", "test_edit_skip_lot_plan", "Edit an existing Skip Lot Plan"),
                    ("test_SkipLotPlan", "test_view_skip_lot_plan", "View Skip Lot Plan details"),
                ],
            },
            {
                "menu": "Admin > Entities > Unit of Measure",
                "rows": [
                    ("test_UnitOfMeasure", "test_add_unit_of_measure",  "Add a new Unit of Measure"),
                    ("test_UnitOfMeasure", "test_edit_unit_of_measure", "Edit an existing Unit of Measure"),
                    ("test_UnitOfMeasure", "test_view_unit_of_measure", "View Unit of Measure details"),
                ],
            },
            {
                "menu": "Admin > Entities > Route (UTE)",
                "rows": [
                    ("test_ute", "test_add_route",  "Add a new Route definition"),
                    ("test_ute", "test_edit_route", "Edit an existing Route"),
                    ("test_ute", "test_view_route", "View Route details"),
                ],
            },
            {
                "menu": "Admin > Calendar",
                "rows": [
                    ("test_Calender", "test_01_add_new_holiday",                       "Add a single new holiday to the calendar"),
                    ("test_Calender", "test_02_edit_holiday",                          "Edit an existing holiday date/description"),
                    ("test_Calender", "test_03_add_range_of_holidays",                 "Add a date-range of holidays in bulk"),
                    ("test_Calender", "test_04_delete_holiday",                        "Delete an existing holiday"),
                    ("test_Calender", "test_05_convert_active_date_to_holiday",        "Convert an active working date to holiday"),
                    ("test_Calender", "test_06_direct_convert_specific_date_to_holiday","Convert a specific date to holiday directly"),
                    ("test_Calender", "test_07_direct_convert_random_active_date_to_holiday","Convert a random active date to holiday"),
                ],
            },
            {
                "menu": "Admin > Item",
                "rows": [
                    ("test_item_create",       "test_01..08 (ItemType1)",   "Create Item type 1 – fill base info + supplier tab + save + verify"),
                    ("test_item_create",       "test_01..08 (ItemType2)",   "Create Item type 2 – fill base info + supplier tab + save + verify"),
                    ("test_item_create",       "test_01..08 (ItemType3)",   "Create Item type 3 – fill base info + supplier tab + save + verify"),
                    ("test_item_excel_driven", "test_01..04 (BulkCreate)",  "Load Excel data and create multiple items in bulk"),
                    ("test_item_excel_driven", "test_01..03 (AdjustLoop)",  "Load Kanban items and adjust loop size for all"),
                ],
            },
            {
                "menu": "Admin > Supplier > Internal Supplier",
                "rows": [
                    ("test_InternalSupplier", "test_01_login_and_navigate_to_supplier", "Login and navigate to Supplier module"),
                    ("test_InternalSupplier", "test_02_switch_to_internal_and_search_wcline","Switch to Internal view and search for WCLine supplier"),
                    ("test_InternalSupplier", "test_03_open_wcline_configuration",      "Open WCLine Supplier configuration page"),
                    ("test_InternalSupplier", "test_04_update_configuration_tabs",      "Update all configuration tabs (General, Card, etc.)"),
                    ("test_InternalSupplier", "test_05_generate_report",                "Generate and verify Internal Supplier configuration report"),
                ],
            },
            {
                "menu": "Admin > Supplier > External Supplier",
                "rows": [
                    ("test_ExternalSupplier", "test_01_login_and_setup",           "Login and setup for external supplier tests"),
                    ("test_ExternalSupplier", "test_02_add_supplier",              "Add a new external supplier"),
                    ("test_ExternalSupplier", "test_03_edit_supplier",             "Edit existing external supplier details"),
                    ("test_ExternalSupplier", "test_04_view_supplier",             "View external supplier details"),
                    ("test_ExternalSupplier", "test_05_add_supplier_user_form",    "Open Add Supplier User form"),
                    ("test_ExternalSupplier", "test_06_fill_and_save_supplier_user","Fill and save new supplier user"),
                    ("test_ExternalSupplier", "test_07_summary_report",            "Generate supplier summary report"),
                ],
            },
            {
                "menu": "Admin > Supplier > Supplier Configuration",
                "rows": [
                    ("test_ExternalSupplier (SupplierConfig)", "test_01..02 Login + Open List",   "Login and open external supplier list"),
                    ("test_ExternalSupplier (SupplierConfig)", "test_03_select_supplier_open_config","Select supplier and open configuration"),
                    ("test_ExternalSupplier (SupplierConfig)", "test_04_update_general_tab",      "Update General configuration tab"),
                    ("test_ExternalSupplier (SupplierConfig)", "test_05_update_card_tab",         "Update Card configuration tab"),
                    ("test_ExternalSupplier (SupplierConfig)", "test_06_update_custom_tab",       "Update Custom configuration tab"),
                    ("test_ExternalSupplier (SupplierConfig)", "test_07_update_invoice_tab",      "Update Invoice configuration tab"),
                    ("test_ExternalSupplier (SupplierConfig)", "test_08_update_print_tab",        "Update Print configuration tab"),
                    ("test_ExternalSupplier (SupplierConfig)", "test_09_update_receive_tab",      "Update Receive configuration tab"),
                    ("test_ExternalSupplier (SupplierConfig)", "test_10_update_scan_tab",         "Update Scan configuration tab"),
                    ("test_ExternalSupplier (SupplierConfig)", "test_11_update_ship_tab",         "Update Ship configuration tab"),
                    ("test_ExternalSupplier (SupplierConfig)", "test_12_summary_report",          "Generate configuration summary report"),
                ],
            },
            {
                "menu": "Admin > Supplier > Assign / Remove Supplier",
                "rows": [
                    ("test_ExternalSupplier (Assign)", "test_01..02 Login + Open List",         "Login and open external supplier list"),
                    ("test_ExternalSupplier (Assign)", "test_03_click_associate_supplier",      "Click Associate Supplier button"),
                    ("test_ExternalSupplier (Assign)", "test_04_show_unassigned_suppliers",     "Show all unassigned suppliers"),
                    ("test_ExternalSupplier (Assign)", "test_05_select_supplier_checkbox",      "Select supplier checkbox to assign"),
                    ("test_ExternalSupplier (Assign)", "test_06_enter_supplier_code",           "Enter supplier code in assignment form"),
                    ("test_ExternalSupplier (Assign)", "test_07_click_assign_and_verify",       "Click Assign and verify assignment success"),
                    ("test_ExternalSupplier (Assign)", "test_08_select_assigned_supplier_for_removal","Select assigned supplier for removal"),
                    ("test_ExternalSupplier (Assign)", "test_09_click_remove",                  "Click Remove supplier button"),
                    ("test_ExternalSupplier (Assign)", "test_10_confirm_remove_and_verify",     "Confirm removal and verify supplier removed"),
                ],
            },
            {
                "menu": "Admin > Supplier > Shipping Rules",
                "rows": [
                    ("test_ExternalSupplier (ShipRules)", "test_01..02 Login + Open List",   "Login and open supplier list"),
                    ("test_ExternalSupplier (ShipRules)", "test_03_open_shipping_rules",     "Open Shipping Rules for supplier"),
                    ("test_ExternalSupplier (ShipRules)", "test_04_click_add_shipping_rule", "Click Add Shipping Rule button"),
                    ("test_ExternalSupplier (ShipRules)", "test_05_select_rule_and_click_select","Select rule type and confirm selection"),
                ],
            },
            {
                "menu": "Admin > Supplier > Supplier Calendar / Holiday",
                "rows": [
                    ("test_ExternalSupplier (Calendar)", "test_01..02 Login + Open List",     "Login and open supplier list"),
                    ("test_ExternalSupplier (Calendar)", "test_03_open_supplier_calendar",    "Open Supplier Calendar page"),
                    ("test_ExternalSupplier (Calendar)", "test_04_click_add_holiday",         "Click Add Holiday button"),
                    ("test_ExternalSupplier (Calendar)", "test_05_fill_and_save_holiday",     "Fill holiday details and save"),
                    ("test_ExternalSupplier (Calendar)", "test_06_verify_holiday_in_list",    "Verify new holiday appears in list"),
                    ("test_ExternalSupplier (Calendar)", "test_07_summary_report",            "Generate supplier calendar report"),
                    ("test_ExternalSupplier (Calendar)", "test_08_add_holiday_ranges",        "Add a range of holidays to supplier calendar"),
                ],
            },
            {
                "menu": "Admin > Users",
                "rows": [
                    ("test_users (CreateUser)",     "test_01_open_create_form",      "Open user creation form"),
                    ("test_users (CreateUser)",     "test_02_fill_form_and_save",    "Fill user form fields and save"),
                    ("test_users (CreateUser)",     "test_03_verify_user_in_list",   "Verify new user appears in user list"),
                    ("test_users (EditUser)",       "test_01_search_and_select",     "Search and select user to edit"),
                    ("test_users (EditUser)",       "test_02_edit_fields",           "Edit user field values"),
                    ("test_users (EditUser)",       "test_03_save_and_verify",       "Save changes and verify update"),
                    ("test_users (ViewUser)",       "test_01_search_and_select",     "Search and select user to view"),
                    ("test_users (ViewUser)",       "test_02_view_user_details",     "View all user details"),
                    ("test_users (ViewUser)",       "test_03_cancel_and_return",     "Cancel view and return to list"),
                    ("test_users (DisableUser)",    "test_01_search_and_select",     "Search and select user to disable"),
                    ("test_users (DisableUser)",    "test_02_click_disable_button",  "Click Disable button"),
                    ("test_users (DisableUser)",    "test_03_confirm_disable",       "Confirm disable action"),
                    ("test_users (EnableUser)",     "test_01_open_disabled_list",    "Open list of disabled users"),
                    ("test_users (EnableUser)",     "test_02_search_and_select",     "Search and select disabled user"),
                    ("test_users (EnableUser)",     "test_03_enable_user",           "Enable the selected user"),
                    ("test_users (EnableUser)",     "test_04_verify_user_active",    "Verify user is now active"),
                    ("test_UsercreationValidations","test_01..07 Create Users",      "Create 5 plant admin users + 1 specific user + validations"),
                    ("test_UsercreationValidations","test_01_read_excel_file",       "Read user data from Excel file"),
                    ("test_UsercreationValidations","test_02_create_users_from_excel","Create multiple users from Excel data"),
                    ("test_UsercreationValidations","test_01_export_to_excel",       "Export user list to Excel"),
                ],
            },
            {
                "menu": "Admin > Workcenter",
                "rows": [
                    ("test_WorkcenterConfiguration", "test_01_login_and_navigate_to_workcenter", "Login and navigate to Workcenter module"),
                    ("test_WorkcenterConfiguration", "test_02_search_and_select_workcenter",     "Search and select a workcenter"),
                    ("test_WorkcenterConfiguration", "test_03_open_configuration",               "Open Workcenter configuration page"),
                    ("test_WorkcenterConfiguration", "test_04_update_configuration_tabs",        "Update all configuration tabs"),
                    ("test_WorkcenterConfiguration", "test_05_generate_report",                  "Generate and verify Workcenter config report"),
                ],
            },
            {
                "menu": "Admin > Workcenter > Production Sequence",
                "rows": [
                    ("test_ProductionSequenceConfiguration", "test_01_login_and_navigate_to_workcenter", "Login and navigate to Workcenter"),
                    ("test_ProductionSequenceConfiguration", "test_02_search_and_select_workcenter",     "Search and select workcenter"),
                    ("test_ProductionSequenceConfiguration", "test_03_open_production_sequence_configuration","Open Production Sequence Configuration"),
                    ("test_ProductionSequenceConfiguration", "test_04_update_production_sequence_tabs",  "Update all Production Sequence tabs"),
                    ("test_ProductionSequenceConfiguration", "test_05_generate_report",                  "Generate Production Sequence config report"),
                ],
            },
            {
                "menu": "Admin > Business Unit (Legacy)",
                "rows": [
                    ("BussinessUnit", "test_bussiness_unit_suite", "Full Business Unit management suite (Add / Edit / View)"),
                ],
            },
            {
                "menu": "Admin > Drop Off Location (Legacy)",
                "rows": [
                    ("DropOffLocation", "test_dropoff_location_suite", "Full Drop-Off Location suite (Add / Edit / View)"),
                ],
            },
            {
                "menu": "Admin > Shifts (Legacy)",
                "rows": [
                    ("Shifts", "test_shift_suite", "Full Shifts suite (Add / Edit / View)"),
                ],
            },
            {
                "menu": "Admin > Manage Tolerance % (Legacy)",
                "rows": [
                    ("ManageTolerancePercentage", "test_manage_tolerance_percentage_suite", "Full Tolerance Percentage suite (Add / Edit / View)"),
                ],
            },
        ],
    },

    # ══════════════════════════════════════════════════════════════════════════
    # SUITE 2 : ACTIONS
    # ══════════════════════════════════════════════════════════════════════════
    {
        "suite": "Actions",
        "color": RGBColor(0x37, 0x5A, 0x30),   # dark-green header
        "menus": [
            {
                "menu": "Actions > Receive",
                "rows": [
                    ("test_receive", "test_01_login",                        "Login to the application"),
                    ("test_receive", "test_02_navigate_to_actions",          "Navigate to the Actions menu"),
                    ("test_receive", "test_03_click_receive",                "Click the Receive tile"),
                    ("test_receive", "test_04_apply_filter_and_load_items",  "Apply filter and load item list"),
                    ("test_receive", "test_05_select_item_show_cards",       "Select an item and show its Kanban cards"),
                    ("test_receive", "test_06_select_cards_attach_notes_and_receive","Select cards, attach notes, and receive"),
                    ("test_receive", "test_07_verify_receive_results",       "Verify receive action results"),
                    ("test_receive", "test_08_back_to_items",                "Navigate back to items list"),
                ],
            },
            {
                "menu": "Actions > Release",
                "rows": [
                    ("test_release", "test_01_login",                       "Login to the application"),
                    ("test_release", "test_02_navigate_to_actions",         "Navigate to Actions menu"),
                    ("test_release", "test_03_click_release",               "Click the Release tile"),
                    ("test_release", "test_04_apply_filter_and_load_items", "Apply filter and load items"),
                    ("test_release", "test_05_select_item_show_cards",      "Select item and show cards"),
                    ("test_release", "test_06_select_cards_and_release",    "Select cards and execute release"),
                    ("test_release", "test_07_verify_release_results",      "Verify release action results"),
                    ("test_release", "test_08_back_to_items",               "Back to items list"),
                ],
            },
            {
                "menu": "Actions > Reschedule",
                "rows": [
                    ("test_reschedule", "test_01_login",                       "Login to application"),
                    ("test_reschedule", "test_02_navigate_to_actions",         "Navigate to Actions"),
                    ("test_reschedule", "test_03_click_reschedule",            "Click Reschedule tile"),
                    ("test_reschedule", "test_04_apply_filter_and_load_items", "Apply filter and load items"),
                    ("test_reschedule", "test_05_select_item_show_cards",      "Select item and show cards"),
                    ("test_reschedule", "test_06_select_cards_and_enter_date", "Select cards and enter new schedule date"),
                    ("test_reschedule", "test_07_compute_ship_date",           "Compute new ship date"),
                    ("test_reschedule", "test_08_click_reschedule_button",     "Click Reschedule button to confirm"),
                    ("test_reschedule", "test_09_verify_reschedule_results",   "Verify reschedule operation results"),
                    ("test_reschedule", "test_10_back_to_items",               "Back to items list"),
                ],
            },
            {
                "menu": "Actions > Add Notes",
                "rows": [
                    ("test_add_notes", "test_01_login",                         "Login to application"),
                    ("test_add_notes", "test_02_navigate_to_actions",           "Navigate to Actions"),
                    ("test_add_notes", "test_03_click_add_notes",               "Click Add Notes tile"),
                    ("test_add_notes", "test_04_apply_filter_and_load_items",   "Apply filter and load items"),
                    ("test_add_notes", "test_05_select_item_show_cards",        "Select item and show cards"),
                    ("test_add_notes", "test_06_select_cards_and_attach_notes", "Select cards and attach note template"),
                    ("test_add_notes", "test_07_select_note_and_apply_to_all",  "Select note and apply to all cards"),
                    ("test_add_notes", "test_08_click_submit",                  "Submit notes attachment"),
                    ("test_add_notes", "test_09_verify_results",                "Verify notes were attached successfully"),
                    ("test_add_notes", "test_10_back_to_items",                 "Back to items list"),
                ],
            },
            {
                "menu": "Actions > Adhoc Receipts",
                "rows": [
                    ("test_adhoc_receipts", "test_01_login",                      "Login to application"),
                    ("test_adhoc_receipts", "test_02_navigate_to_actions",        "Navigate to Actions"),
                    ("test_adhoc_receipts", "test_03_click_adhoc_receipts",       "Click Adhoc Receipts tile"),
                    ("test_adhoc_receipts", "test_04_fill_mandatory_fields",      "Fill all mandatory fields in form"),
                    ("test_adhoc_receipts", "test_05_compute_cards",              "Compute Kanban cards for receipt"),
                    ("test_adhoc_receipts", "test_06_validate_receipt",           "Validate receipt data before submit"),
                    ("test_adhoc_receipts", "test_07_submit_receipt",             "Submit the adhoc receipt"),
                    ("test_adhoc_receipts", "test_08_verify_results",             "Verify receipt creation results"),
                    ("test_adhoc_receipts", "test_09_back_to_adhoc_receipt",      "Back to Adhoc Receipt page"),
                ],
            },
            {
                "menu": "Actions > Adjust Inventory",
                "rows": [
                    ("test_adjust_inventory", "test_01_login",                    "Login to application"),
                    ("test_adjust_inventory", "test_02_navigate_to_actions",      "Navigate to Actions"),
                    ("test_adjust_inventory", "test_03_click_adjust_inventory",   "Click Adjust Inventory tile"),
                    ("test_adjust_inventory", "test_04_select_item_show_cards",   "Select item and show cards"),
                    ("test_adjust_inventory", "test_05_adjust_inventory",         "Adjust inventory quantity for selected cards"),
                    ("test_adjust_inventory", "test_06_back_to_items",            "Back to items list"),
                ],
            },
            {
                "menu": "Actions > Approve Cards",
                "rows": [
                    ("test_approve_reject_cards (Approve)", "test_01_login",                       "Login to application"),
                    ("test_approve_reject_cards (Approve)", "test_02_navigate_to_actions",         "Navigate to Actions"),
                    ("test_approve_reject_cards (Approve)", "test_03_click_approve",               "Click Approve tile"),
                    ("test_approve_reject_cards (Approve)", "test_04_apply_filter_and_load_items", "Apply filter and load items"),
                    ("test_approve_reject_cards (Approve)", "test_05_select_item_show_cards",      "Select item and show cards"),
                    ("test_approve_reject_cards (Approve)", "test_06_select_cards_approve_and_finish","Select cards and complete approval"),
                    ("test_approve_reject_cards (Approve)", "test_07_back_to_items",               "Back to items list"),
                ],
            },
            {
                "menu": "Actions > Reject Cards",
                "rows": [
                    ("test_approve_reject_cards (Reject)", "test_01_login",                       "Login to application"),
                    ("test_approve_reject_cards (Reject)", "test_02_navigate_to_actions",         "Navigate to Actions"),
                    ("test_approve_reject_cards (Reject)", "test_03_click_approve_tile",          "Click Approve/Reject tile"),
                    ("test_approve_reject_cards (Reject)", "test_04_apply_filter_load_items",     "Apply filter and load items"),
                    ("test_approve_reject_cards (Reject)", "test_05_click_item_show_cards",       "Click item and show cards"),
                    ("test_approve_reject_cards (Reject)", "test_06_select_cards_reject_with_comment","Select cards and reject with comment"),
                    ("test_approve_reject_cards (Reject)", "test_07_back_to_items",               "Back to items list"),
                ],
            },
            {
                "menu": "Actions > Call Off",
                "rows": [
                    ("test_calloff", "test_01_login",                        "Login to application"),
                    ("test_calloff", "test_02_navigate_to_actions",          "Navigate to Actions"),
                    ("test_calloff", "test_03_click_calloff",                "Click Call Off tile"),
                    ("test_calloff", "test_04_apply_filter_and_load_items",  "Apply filter and load items"),
                    ("test_calloff", "test_05_select_item_show_cards",       "Select item and show cards"),
                    ("test_calloff", "test_06_select_cards_and_calloff",     "Select cards and perform call off"),
                    ("test_calloff", "test_07_verify_calloff_results",       "Verify call off results"),
                    ("test_calloff", "test_08_back_to_items",                "Back to items list"),
                ],
            },
            {
                "menu": "Actions > Set Expiry Date",
                "rows": [
                    ("test_expiry_date", "test_01_login",                       "Login to application"),
                    ("test_expiry_date", "test_02_navigate_to_actions",         "Navigate to Actions"),
                    ("test_expiry_date", "test_03_click_set_expiry_date",       "Click Set Expiry Date tile"),
                    ("test_expiry_date", "test_04_click_go_and_select_item",    "Click Go and select item"),
                    ("test_expiry_date", "test_05_select_card_and_set_expiry_date","Select card and set expiry date"),
                    ("test_expiry_date", "test_06_verify_expiry_date_results",  "Verify expiry date was set correctly"),
                    ("test_expiry_date", "test_07_back_to_items",               "Back to items list"),
                ],
            },
            {
                "menu": "Actions > Issue Inventory",
                "rows": [
                    ("test_issue_inventory", "test_01_login",                     "Login to application"),
                    ("test_issue_inventory", "test_02_navigate_to_actions",       "Navigate to Actions"),
                    ("test_issue_inventory", "test_03_click_issue_inventory",     "Click Issue Inventory tile"),
                    ("test_issue_inventory", "test_04_click_go_load_items",       "Click Go and load items"),
                    ("test_issue_inventory", "test_05_select_item_show_cards",    "Select item and show cards"),
                    ("test_issue_inventory", "test_06_enter_details_and_issue",   "Enter issue details and confirm issue"),
                    ("test_issue_inventory", "test_07_verify_results",            "Verify issue inventory results"),
                    ("test_issue_inventory", "test_08_back_to_items",             "Back to items list"),
                ],
            },
            {
                "menu": "Actions > Move Location",
                "rows": [
                    ("test_move_location", "test_01_login",                       "Login to application"),
                    ("test_move_location", "test_02_navigate_to_actions",         "Navigate to Actions"),
                    ("test_move_location", "test_03_click_move_location",         "Click Move Location tile"),
                    ("test_move_location", "test_04_select_item_show_cards",      "Select item and show cards"),
                    ("test_move_location", "test_05_enter_locations_and_select_cards","Enter source/destination locations and select cards"),
                    ("test_move_location", "test_06_verify_move_location_results","Verify card moved to new location"),
                    ("test_move_location", "test_07_back_to_items",               "Back to items list"),
                ],
            },
            {
                "menu": "Actions > Runline Approve",
                "rows": [
                    ("test_runline_approve", "test_01_login",                     "Login to application"),
                    ("test_runline_approve", "test_02_navigate_to_actions",       "Navigate to Actions"),
                    ("test_runline_approve", "test_03_click_runline_approve",     "Click Runline Approve tile"),
                    ("test_runline_approve", "test_04_apply_filter_and_load_items","Apply filter and load items"),
                    ("test_runline_approve", "test_05_select_item_and_show_cards","Select item and show cards"),
                    ("test_runline_approve", "test_06_select_card_and_approve",   "Select card and approve"),
                    ("test_runline_approve", "test_07_back_to_items",             "Back to items list"),
                ],
            },
            {
                "menu": "Actions > Set PO",
                "rows": [
                    ("test_set_po", "test_01_login",                     "Login to application"),
                    ("test_set_po", "test_02_navigate_to_actions",       "Navigate to Actions"),
                    ("test_set_po", "test_03_click_set_po",              "Click Set PO tile"),
                    ("test_set_po", "test_04_apply_filter_and_load_items","Apply filter and load items"),
                    ("test_set_po", "test_05_select_item_show_cards",    "Select item and show cards"),
                    ("test_set_po", "test_06_select_cards_and_set_po",   "Select cards and set PO number"),
                    ("test_set_po", "test_07_verify_set_po_results",     "Verify PO was set on cards"),
                    ("test_set_po", "test_08_back_to_items",             "Back to items list"),
                ],
            },
        ],
    },

    # ══════════════════════════════════════════════════════════════════════════
    # SUITE 3 : REPORTS – BUYER REPORTS
    # ══════════════════════════════════════════════════════════════════════════
    {
        "suite": "Reports – Buyer Reports",
        "color": RGBColor(0x7B, 0x36, 0x06),   # dark-orange/brown header
        "menus": [
            {
                "menu": "Reports > Buyer Reports > Supplier Performance",
                "rows": [
                    ("test_supplier_performance_report", "test_01_login",                       "Login as buyer user"),
                    ("test_supplier_performance_report", "test_02_open_supplier_performance_report","Open Supplier Performance Report filter"),
                    ("test_supplier_performance_report", "test_03_select_year_to_date_show_report","Select Year To Date and show report"),
                ],
            },
            {
                "menu": "Reports > Buyer Reports > Supplier On-Time",
                "rows": [
                    ("test_supplier_ontime_report", "test_01_login",                    "Login as buyer user"),
                    ("test_supplier_ontime_report", "test_02_open_ontime_shipment_report","Open On-Time Shipment filter"),
                    ("test_supplier_ontime_report", "test_03_select_filters_show_report","Select Past One Year + Supplier and show report"),
                ],
            },
            {
                "menu": "Reports > Buyer Reports > Supplier Scorecard",
                "rows": [
                    ("test_supplier_scorecard_report", "test_01_login",                   "Login as buyer user"),
                    ("test_supplier_scorecard_report", "test_02_open_supplier_scorecard", "Open Supplier Scorecard report"),
                    ("test_supplier_scorecard_report", "test_03_click_supnew_supplier_link","Click Supnew supplier link to open details"),
                    ("test_supplier_scorecard_report", "test_04_back_to_summary",         "Click Back to Summary"),
                ],
            },
            {
                "menu": "Reports > Buyer Reports > Savings Analysis By Time",
                "rows": [
                    ("test_savings_analysis_by_time_report", "test_01_login",                          "Login as buyer user"),
                    ("test_savings_analysis_by_time_report", "test_02_open_savings_analysis_by_time_report","Open Savings Analysis By Time filter"),
                    ("test_savings_analysis_by_time_report", "test_03_select_past_one_year_show_report","Select Past One Year and show report"),
                ],
            },
            {
                "menu": "Reports > Buyer Reports > Cycle Time",
                "rows": [
                    ("test_cycle_time_report", "test_01_login",                            "Login as buyer user"),
                    ("test_cycle_time_report", "test_02_open_cycle_time_report",           "Open Cycle Time filter"),
                    ("test_cycle_time_report", "test_03_select_past_one_year_and_show_report","Set date range (past 365 days) and show report"),
                ],
            },
            {
                "menu": "Reports > Buyer Reports > Inventory Cost",
                "rows": [
                    ("test_inventorycost_report", "test_01_login",                  "Login as buyer user"),
                    ("test_inventorycost_report", "test_02_open_inventorycost_report","Open Inventory Cost filter"),
                    ("test_inventorycost_report", "test_03_set_date_range_show_report","Set date range and show report"),
                ],
            },
            {
                "menu": "Reports > Buyer Reports > On Hand Inventory",
                "rows": [
                    ("test_onhand_inventory_report", "test_01_login",                      "Login as buyer user"),
                    ("test_onhand_inventory_report", "test_02_open_onhand_inventory_report","Open On Hand Inventory filter"),
                    ("test_onhand_inventory_report", "test_03_keep_defaults_show_report",  "Keep default filter values and show report"),
                    ("test_onhand_inventory_report", "test_04_click_change_filter",        "Click Change Filter and return to filter"),
                ],
            },
            {
                "menu": "Reports > Buyer Reports > On Hand Inventory (Full Flow)",
                "rows": [
                    ("test_onhand_inventory_full_flow", "test_01_login",                      "Login as buyer user"),
                    ("test_onhand_inventory_full_flow", "test_02_open_onhand_inventory_report","Open On Hand Inventory filter"),
                    ("test_onhand_inventory_full_flow", "test_03_keep_defaults_show_report",  "Show report with defaults"),
                    ("test_onhand_inventory_full_flow", "test_04_click_item_in_summary",      "Click an item link in summary table"),
                    ("test_onhand_inventory_full_flow", "test_05_back_to_summary",            "Click Back to Summary"),
                    ("test_onhand_inventory_full_flow", "test_06_click_change_filter",        "Click Change Filter"),
                ],
            },
            {
                "menu": "Reports > Buyer Reports > Red Item Analysis",
                "rows": [
                    ("test_red_item_analysis_report", "test_01_login",                      "Login as buyer user"),
                    ("test_red_item_analysis_report", "test_02_open_red_item_analysis_report","Open Red Item Analysis filter"),
                    ("test_red_item_analysis_report", "test_03_verify_page_loaded",         "Verify filter page loaded"),
                    ("test_red_item_analysis_report", "test_04_select_plant_and_show_report","Select plant and show report"),
                ],
            },
            {
                "menu": "Reports > Buyer Reports > Buyer Status",
                "rows": [
                    ("test_buyerstatus_report", "test_01_login",                      "Login as buyer user"),
                    ("test_buyerstatus_report", "test_02_open_buyer_status_report",   "Open Buyer Status report filter"),
                    ("test_buyerstatus_report", "test_03_click_go_and_verify_report", "Click Go and verify report data"),
                    ("test_buyerstatus_report", "test_04_click_change_filter",        "Click Change Filter"),
                ],
            },
            {
                "menu": "Reports > Buyer Reports > Stockout",
                "rows": [
                    ("test_stockout_report", "test_01_login",             "Login as buyer user"),
                    ("test_stockout_report", "test_02_open_stockout_report","Open Stockout report filter"),
                    ("test_stockout_report", "test_03_show_report",       "Show Stockout report"),
                ],
            },
            {
                "menu": "Reports > Buyer Reports > Kanban Inventory",
                "rows": [
                    ("test_kanban_inventory_report", "test_01_login",                        "Login as buyer user"),
                    ("test_kanban_inventory_report", "test_02_open_kanban_inventory_report", "Open Kanban Inventory filter"),
                    ("test_kanban_inventory_report", "test_03_click_show_report",            "Show Kanban Inventory report"),
                    ("test_kanban_inventory_report", "test_04_click_change_filter",          "Click Change Filter"),
                ],
            },
            {
                "menu": "Reports > Buyer Reports > Reschedule Notes History",
                "rows": [
                    ("test_rechedule_notes_history_report", "test_01_login",                                "Login as buyer user"),
                    ("test_rechedule_notes_history_report", "test_02_open_rechedule_notes_history_report",  "Open Reschedule Notes History filter"),
                    ("test_rechedule_notes_history_report", "test_03_show_report",                          "Show report"),
                    ("test_rechedule_notes_history_report", "test_04_click_change_filter",                  "Click Change Filter"),
                ],
            },
            {
                "menu": "Reports > Buyer Reports > Item Details By Supplier",
                "rows": [
                    ("test_item_details_by_supplier_report", "test_01_login",          "Login as buyer user"),
                    ("test_item_details_by_supplier_report", "test_02_open_report",    "Open Item Details By Supplier filter"),
                    ("test_item_details_by_supplier_report", "test_03_show_report",    "Keep defaults (This Plant) and show report"),
                    ("test_item_details_by_supplier_report", "test_04_change_filter",  "Click Change Filter"),
                ],
            },
            {
                "menu": "Reports > Buyer Reports > Total Spend",
                "rows": [
                    ("test_total_spend_report", "test_01_login",                            "Login as buyer user"),
                    ("test_total_spend_report", "test_02_open_total_spend_report",          "Open Total Spend filter"),
                    ("test_total_spend_report", "test_03_select_year_to_date_and_show_report","Select Year To Date and show report"),
                    ("test_total_spend_report", "test_04_click_change_filter",              "Click Change Filter"),
                ],
            },
            {
                "menu": "Reports > Buyer Reports > Total Card Aging",
                "rows": [
                    ("test_total_card_aging_report", "test_01_login",                         "Login as buyer user"),
                    ("test_total_card_aging_report", "test_02_open_total_card_aging_report",  "Open Card Aging filter"),
                    ("test_total_card_aging_report", "test_03_select_on_hand_and_show_report","Select Status = On Hand and show report"),
                    ("test_total_card_aging_report", "test_04_click_change_filter",           "Click Change Filter"),
                    ("test_total_card_aging_report", "test_05_select_in_process_show_report", "Select Status = In Process and show report"),
                ],
            },
            {
                "menu": "Reports > Buyer Reports > Outstanding Receipts",
                "rows": [
                    ("test_outstanding_receipts_report", "test_01_login_and_load_filter_page","Login and load Outstanding Receipts filter"),
                    ("test_outstanding_receipts_report", "test_02_show_report_and_verify_table","Show report and verify data table"),
                    ("test_outstanding_receipts_report", "test_03_click_change_filter",       "Click Change Filter"),
                ],
            },
        ],
    },

    # ══════════════════════════════════════════════════════════════════════════
    # SUITE 4 : REPORTS – SUPPLIER REPORTS
    # ══════════════════════════════════════════════════════════════════════════
    {
        "suite": "Reports – Supplier Reports",
        "color": RGBColor(0x4F, 0x30, 0x6E),   # purple header
        "menus": [
            {
                "menu": "Reports > Supplier Reports > Supplier Status",
                "rows": [
                    ("test_supplier_status_report", "test_01_login",        "Login as supplier user (supnewuser)"),
                    ("test_supplier_status_report", "test_02_open_report",  "Open Supplier Status filter"),
                    ("test_supplier_status_report", "test_03_click_go",     "Click Go with defaults and verify grid"),
                ],
            },
            {
                "menu": "Reports > Supplier Reports > Supplier Cycle Time",
                "rows": [
                    ("test_supplier_cycle_time_report", "test_01_login",                        "Login as supnewuser"),
                    ("test_supplier_cycle_time_report", "test_02_open_cycle_time_report",       "Open Supplier Cycle Time filter"),
                    ("test_supplier_cycle_time_report", "test_03_select_date_range_and_show_report","Select Past One Year and show report"),
                    ("test_supplier_cycle_time_report", "test_04_back_to_filter",               "Click Back / Change Filter"),
                    ("test_supplier_cycle_time_report", "test_05_drill_down_by_itemno",         "Drill down by Item No in summary"),
                    ("test_supplier_cycle_time_report", "test_06_back_to_summary",              "Back to Cycle Time Summary"),
                ],
            },
            {
                "menu": "Reports > Supplier Reports > Supplier On-Hand Inventory",
                "rows": [
                    ("test_supplier_onhand_inventory_report", "test_01_login",                           "Login as supnewuser"),
                    ("test_supplier_onhand_inventory_report", "test_02_open_supplier_onhand_inventory_report","Open Supplier On-Hand Inventory filter"),
                    ("test_supplier_onhand_inventory_report", "test_03_keep_defaults_show_report",       "Keep defaults and show report"),
                    ("test_supplier_onhand_inventory_report", "test_04_click_item_in_summary",           "Click item link in summary table"),
                    ("test_supplier_onhand_inventory_report", "test_05_back_to_summary",                 "Back to Supplier On-Hand Summary"),
                ],
            },
            {
                "menu": "Reports > Supplier Reports > View Notes History",
                "rows": [
                    ("test_supplier_view_notes_history_report", "test_01_login",                               "Login as supnewuser"),
                    ("test_supplier_view_notes_history_report", "test_02_open_view_notes_history_report",      "Open View Notes History filter"),
                    ("test_supplier_view_notes_history_report", "test_03_show_report",                         "Show Notes History report"),
                    ("test_supplier_view_notes_history_report", "test_04_click_change_filter",                 "Click Change Filter"),
                ],
            },
            {
                "menu": "Reports > Supplier Reports > Outstanding Shipments",
                "rows": [
                    ("test_outstanding_shipments_report", "test_01_login",                              "Login as supnewuser"),
                    ("test_outstanding_shipments_report", "test_02_open_outstanding_shipments_report",  "Open Outstanding Shipments filter"),
                    ("test_outstanding_shipments_report", "test_03_show_report",                        "Show report with defaults"),
                    ("test_outstanding_shipments_report", "test_04_click_total_orders_link",            "Click Total Orders value to open details"),
                    ("test_outstanding_shipments_report", "test_05_back_to_summary",                    "Back to Outstanding Shipments Summary"),
                    ("test_outstanding_shipments_report", "test_06_click_change_filter",                "Click Change Filter"),
                ],
            },
            {
                "menu": "Reports > Supplier Reports > Card Aging",
                "rows": [
                    ("test_card_aging_report", "test_01_login",              "Login as supnewuser"),
                    ("test_card_aging_report", "test_02_open_card_aging_filter","Open Card Aging filter"),
                    ("test_card_aging_report", "test_03_click_show_report",  "Select Status = On Hand and show report"),
                    ("test_card_aging_report", "test_04_click_change_filter","Click Change Filter"),
                ],
            },
            {
                "menu": "Reports > Supplier Reports > Consolidated Demand",
                "rows": [
                    ("test_consolidated_demand_report", "test_01_login",                "Login as supnewuser"),
                    ("test_consolidated_demand_report", "test_02_open_report",          "Open Consolidated Demand filter"),
                    ("test_consolidated_demand_report", "test_03_verify_summary_grid",  "Verify summary data grid"),
                    ("test_consolidated_demand_report", "test_04_click_supplier_item",  "Click supplier item link"),
                    ("test_consolidated_demand_report", "test_05_change_filter",        "Click Change Filter"),
                ],
            },
            {
                "menu": "Reports > Supplier Reports > Shipment Due",
                "rows": [
                    ("test_shipment_due_report", "test_01_login",                    "Login as supnewuser"),
                    ("test_shipment_due_report", "test_02_open_shipment_due_report", "Open Shipment Due filter"),
                    ("test_shipment_due_report", "test_03_show_report",              "Show Shipment Due report"),
                    ("test_shipment_due_report", "test_04_click_supplier_item_no",   "Click Supplier Item No for details"),
                    ("test_shipment_due_report", "test_05_change_filter",            "Click Change Filter"),
                ],
            },
            {
                "menu": "Reports > Supplier Reports > Supplier On-Time",
                "rows": [
                    ("test_supplier_on_time_report", "test_01_login",               "Login as supnewuser"),
                    ("test_supplier_on_time_report", "test_02_open_supplier_on_time_report","Open Supplier On-Time filter"),
                    ("test_supplier_on_time_report", "test_03_click_show_report",   "Show On-Time Shipment report"),
                    ("test_supplier_on_time_report", "test_04_click_change_filter", "Click Change Filter"),
                    ("test_supplier_on_time_report", "test_05_show_receipt_performance","Set Receipt Performance type and show report"),
                ],
            },
            {
                "menu": "Reports > Supplier Reports > Supplier Performance",
                "rows": [
                    ("test_supplier_performance_report (Supplier)", "test_01_login_and_switch_to_supplier","Login and switch to supplier application"),
                    ("test_supplier_performance_report (Supplier)", "test_02_open_supplier_performance_filter","Open Supplier Performance filter"),
                    ("test_supplier_performance_report (Supplier)", "test_03_set_past_one_year_and_show_report","Select Past One Year and show report"),
                    ("test_supplier_performance_report (Supplier)", "test_04_click_plant_and_verify_item_report","Drill down by Plant to item-level report"),
                    ("test_supplier_performance_report (Supplier)", "test_05_click_any_item_and_verify_cardid_report","Drill down by Item to card-ID report"),
                    ("test_supplier_performance_report (Supplier)", "test_06_back_to_summary",             "Back to Supplier Performance Summary"),
                ],
            },
            {
                "menu": "Reports > Supplier Reports > Supplier Ontime (Buyer View)",
                "rows": [
                    ("test_supplier_ontime_report (SupReports)", "test_01_login",                     "Login as supnewuser"),
                    ("test_supplier_ontime_report (SupReports)", "test_02_open_ontime_shipment_report","Open Supplier On-Time filter"),
                    ("test_supplier_ontime_report (SupReports)", "test_03_select_filters_and_show_report","Select Past One Year and show report"),
                ],
            },
        ],
    },

    # ══════════════════════════════════════════════════════════════════════════
    # SUITE 5 : REPORTS – LFM / OEE REPORTS
    # ══════════════════════════════════════════════════════════════════════════
    {
        "suite": "Reports – LFM / OEE Reports",
        "color": RGBColor(0x1D, 0x60, 0x5C),   # teal header
        "menus": [
            {
                "menu": "Reports > LFM/OEE Reports > Closed Production",
                "rows": [
                    ("test_closed_production_report", "test_01_login",                           "Login as Databizwarehouseuser"),
                    ("test_closed_production_report", "test_02_open_closed_production_filter",   "Open Closed Production filter"),
                    ("test_closed_production_report", "test_03_select_past_one_year_show_report","Select Past One Year and show report"),
                    ("test_closed_production_report", "test_04_click_item_open_details",         "Click Item No to open Closed Production Details"),
                    ("test_closed_production_report", "test_05_back_to_summary",                 "Click Back to Summary"),
                    ("test_closed_production_report", "test_06_click_change_filter",             "Click Change Filter"),
                ],
            },
            {
                "menu": "Reports > LFM/OEE Reports > Operator Efficiency",
                "rows": [
                    ("test_operator_efficiency_report", "test_01_login",                             "Login as Databizwarehouseuser"),
                    ("test_operator_efficiency_report", "test_02_open_operator_efficiency_filter",   "Open Operator Efficiency filter"),
                    ("test_operator_efficiency_report", "test_03_select_past_one_year_show_report",  "Select Past One Year and show report"),
                    ("test_operator_efficiency_report", "test_04_click_operator_open_details",       "Click Operator Name to open details"),
                    ("test_operator_efficiency_report", "test_05_back_to_summary",                   "Click Back to Summary"),
                    ("test_operator_efficiency_report", "test_06_click_change_filter",               "Click Change Filter"),
                ],
            },
            {
                "menu": "Reports > LFM/OEE Reports > Jobs Not Completed",
                "rows": [
                    ("test_jobs_not_completed_report", "test_01_login",                           "Login as Databizwarehouseuser"),
                    ("test_jobs_not_completed_report", "test_02_open_jobs_not_completed_filter",  "Open Jobs Not Completed filter"),
                    ("test_jobs_not_completed_report", "test_03_select_past_one_year_show_report","Select Past One Year and show report"),
                    ("test_jobs_not_completed_report", "test_04_click_item_open_details",         "Click Item No to open details"),
                    ("test_jobs_not_completed_report", "test_05_back_to_summary",                 "Click Back to Summary"),
                    ("test_jobs_not_completed_report", "test_06_click_change_filter",             "Click Change Filter"),
                ],
            },
            {
                "menu": "Reports > LFM/OEE Reports > Hourly Production By Part",
                "rows": [
                    ("test_hourly_production_by_part_report", "test_01_login",                                "Login as Databizwarehouseuser"),
                    ("test_hourly_production_by_part_report", "test_02_open_hourly_production_by_part_filter","Open Hourly Production By Part filter"),
                    ("test_hourly_production_by_part_report", "test_03_select_past_one_year_show_report",     "Select Past One Year and show report"),
                    ("test_hourly_production_by_part_report", "test_04_click_change_filter",                  "Click Change Filter"),
                ],
            },
            {
                "menu": "Reports > LFM/OEE Reports > Scrap",
                "rows": [
                    ("test_scrap_report", "test_01_login",                           "Login as Databizwarehouseuser"),
                    ("test_scrap_report", "test_02_open_scrap_filter",               "Open Scrap filter"),
                    ("test_scrap_report", "test_03_select_past_one_year_show_report","Select Past One Year and show report"),
                    ("test_scrap_report", "test_04_click_supplier_item_open_details","Click Supplier Item No to open Scrap Details"),
                    ("test_scrap_report", "test_05_back_to_summary",                 "Click Back to Summary"),
                    ("test_scrap_report", "test_06_click_change_filter",             "Click Change Filter"),
                ],
            },
            {
                "menu": "Reports > LFM/OEE Reports > OEE",
                "rows": [
                    ("test_oee_report", "test_01_login",                           "Login as Databizwarehouseuser"),
                    ("test_oee_report", "test_02_open_oee_filter",                 "Open OEE filter"),
                    ("test_oee_report", "test_03_select_past_one_year_show_report","Select Past One Year and show report"),
                    ("test_oee_report", "test_04_click_change_filter",             "Click Change Filter"),
                ],
            },
            {
                "menu": "Reports > LFM/OEE Reports > Production Summary",
                "rows": [
                    ("test_production_summary_report", "test_01_login",                            "Login as Databizwarehouseuser"),
                    ("test_production_summary_report", "test_02_open_production_summary_filter",   "Open Production Summary (Calendar view)"),
                    ("test_production_summary_report", "test_03_click_date_open_machine_summary",  "Click current date to open Machine Summary"),
                    ("test_production_summary_report", "test_04_click_first_machine_code",         "Click first Machine Code for assigned jobs"),
                    ("test_production_summary_report", "test_05_back_to_machine_summary",          "Back to Machine Summary"),
                ],
            },
            {
                "menu": "Reports > LFM/OEE Reports > Production History",
                "rows": [
                    ("test_production_history_report", "test_01_login",                          "Login as Databizwarehouseuser"),
                    ("test_production_history_report", "test_02_open_production_history_filter", "Open Production History filter"),
                    ("test_production_history_report", "test_03_show_report",                    "Show report with defaults"),
                    ("test_production_history_report", "test_04_click_item_open_details",        "Click first Operation Name link"),
                    ("test_production_history_report", "test_05_back_to_summary",                "Click Back to Summary"),
                    ("test_production_history_report", "test_06_click_change_filter",            "Click Change Filter"),
                ],
            },
            {
                "menu": "Reports > LFM/OEE Reports > Production Setup History",
                "rows": [
                    ("test_production_setup_history_report", "test_01_login",                                "Login as Databizwarehouseuser"),
                    ("test_production_setup_history_report", "test_02_open_production_setup_history_filter", "Open Production Setup History filter"),
                    ("test_production_setup_history_report", "test_03_show_report",                          "Show report with defaults"),
                    ("test_production_setup_history_report", "test_04_click_change_filter",                  "Click Change Filter"),
                ],
            },
        ],
    },

    # ══════════════════════════════════════════════════════════════════════════
    # SUITE 6 : REPORTS – ADMIN REPORTS
    # ══════════════════════════════════════════════════════════════════════════
    {
        "suite": "Reports – Admin Reports",
        "color": RGBColor(0x5C, 0x3A, 0x1E),   # brown header
        "menus": [
            {
                "menu": "Reports > Admin Reports > User Account Type",
                "rows": [
                    ("test_user_account_type_report", "test_flow_login_show_change_filter","Login → Show Report → Change Filter (end-to-end flow)"),
                ],
            },
            {
                "menu": "Reports > Admin Reports > User Auditing",
                "rows": [
                    ("test_user_auditing_report", "test_flow_login_show_change_filter","Login → Show Report → Change Filter (end-to-end flow)"),
                ],
            },
        ],
    },

    # ══════════════════════════════════════════════════════════════════════════
    # SUITE 7 : REPORTS – CUSTOM REPORTS (ADMIN)
    # ══════════════════════════════════════════════════════════════════════════
    {
        "suite": "Reports – Custom Reports (Admin)",
        "color": RGBColor(0x0D, 0x47, 0x24),   # dark-green header
        "menus": [
            {
                "menu": "Reports > Custom Reports > Admin > Users",
                "rows": [
                    ("test_users_report", "test_01_login",                           "Login as buyer user"),
                    ("test_users_report", "test_02_navigate_to_create_custom_report_list","Navigate to Create Custom Report list"),
                    ("test_users_report", "test_03_click_users_under_admin",         "Click 'Users' under Admin section"),
                    ("test_users_report", "test_04_fill_report_form",                "Fill Name and Description fields"),
                    ("test_users_report", "test_05_submit_form_verify_success",      "Save form and verify redirect"),
                    ("test_users_report", "test_06_show_report",                     "Click Show Report and verify data"),
                ],
            },
            {
                "menu": "Reports > Custom Reports > Admin > User Login Session Details",
                "rows": [
                    ("test_user_login_session_details_report", "test_01_login",                          "Login as buyer user"),
                    ("test_user_login_session_details_report", "test_02_navigate_to_list",               "Navigate to Custom Report list"),
                    ("test_user_login_session_details_report", "test_03_click_user_login_session_details","Click User Login Session Details report"),
                    ("test_user_login_session_details_report", "test_04_fill_mandatory_fields",          "Fill Name and Description"),
                    ("test_user_login_session_details_report", "test_05_save_custom_report",             "Save custom report"),
                ],
            },
            {
                "menu": "Reports > Custom Reports > Admin > Supplier Holidays",
                "rows": [
                    ("test_supplier_holidays_report", "test_01_login",                      "Login as buyer user"),
                    ("test_supplier_holidays_report", "test_02_navigate_to_list",           "Navigate to Custom Report list"),
                    ("test_supplier_holidays_report", "test_03_click_supplier_holidays_report","Click Supplier Holidays report"),
                    ("test_supplier_holidays_report", "test_04_fill_mandatory_fields",      "Fill Name and Description"),
                    ("test_supplier_holidays_report", "test_05_save_custom_report",         "Save custom report (xfail: known server error)"),
                    ("test_supplier_holidays_report", "test_06_show_report",                "Show Report (skipped when save fails)"),
                ],
            },
            {
                "menu": "Reports > Custom Reports > Admin > Buyer Holidays",
                "rows": [
                    ("test_buyer_holidays_report", "test_01_login",                   "Login as buyer user"),
                    ("test_buyer_holidays_report", "test_02_navigate_to_list",        "Navigate to Custom Report list"),
                    ("test_buyer_holidays_report", "test_03_click_buyer_holidays_report","Click Buyer Holidays report"),
                    ("test_buyer_holidays_report", "test_04_fill_mandatory_fields",   "Fill Name and Description (send_keys + Tab)"),
                    ("test_buyer_holidays_report", "test_05_save_custom_report",      "Save custom report with retry"),
                    ("test_buyer_holidays_report", "test_06_show_report",             "Show Report with Previous Year date range"),
                ],
            },
            {
                "menu": "Reports > Custom Reports > Admin > Containerization",
                "rows": [
                    ("test_containerization_report", "test_01_login",                      "Login as buyer user"),
                    ("test_containerization_report", "test_02_navigate_to_list",           "Navigate to Custom Report list"),
                    ("test_containerization_report", "test_03_click_containerization_report","Click Containerization report"),
                    ("test_containerization_report", "test_04_fill_mandatory_fields",      "Fill Name and Description"),
                    ("test_containerization_report", "test_05_save_custom_report",         "Save custom report"),
                    ("test_containerization_report", "test_06_show_report",                "Show Report and verify data grid"),
                ],
            },
            {
                "menu": "Reports > Custom Reports > Admin > Buyer To Supplier Contacts",
                "rows": [
                    ("test_buyer_to_supplier_contacts_report", "test_01_login",                              "Login as buyer user"),
                    ("test_buyer_to_supplier_contacts_report", "test_02_navigate_to_list",                   "Navigate to Custom Report list"),
                    ("test_buyer_to_supplier_contacts_report", "test_03_open_buyer_to_supplier_contacts_form","Click Buyer To Supplier Contacts report"),
                    ("test_buyer_to_supplier_contacts_report", "test_04_fill_report_form",                   "Fill Name and Description"),
                    ("test_buyer_to_supplier_contacts_report", "test_05_save_custom_report",                 "Save custom report"),
                    ("test_buyer_to_supplier_contacts_report", "test_06_show_report",                        "Show Report"),
                ],
            },
            {
                "menu": "Reports > Custom Reports > Admin > Customers Users",
                "rows": [
                    ("test_customers_users_report", "test_01_login",                              "Login as buyer user"),
                    ("test_customers_users_report", "test_02_navigate_to_create_custom_report_list","Navigate to Custom Report list"),
                    ("test_customers_users_report", "test_03_click_customers_users_under_admin",  "Click Customers Users under Admin"),
                    ("test_customers_users_report", "test_04_fill_report_form",                   "Fill Name and Description"),
                    ("test_customers_users_report", "test_05_submit_form_verify_success",         "Submit form and verify success"),
                    ("test_customers_users_report", "test_06_show_report",                        "Show Report"),
                ],
            },
            {
                "menu": "Reports > Custom Reports > Admin > Item To Suppliers",
                "rows": [
                    ("test_item_to_suppliers_report", "test_01_login",                "Login as buyer user"),
                    ("test_item_to_suppliers_report", "test_02_navigate_to_list",     "Navigate to Custom Report list"),
                    ("test_item_to_suppliers_report", "test_03_click_item_to_suppliers","Click Item To Suppliers report"),
                    ("test_item_to_suppliers_report", "test_04_fill_form",            "Fill Name and Description"),
                    ("test_item_to_suppliers_report", "test_05_submit",               "Submit form"),
                    ("test_item_to_suppliers_report", "test_06_show_report",          "Show Report"),
                ],
            },
            {
                "menu": "Reports > Custom Reports > Admin > Suppliers Users",
                "rows": [
                    ("test_suppliers_users_report", "test_01_login",                  "Login as buyer user"),
                    ("test_suppliers_users_report", "test_02_navigate_to_list",       "Navigate to Custom Report list"),
                    ("test_suppliers_users_report", "test_03_click_suppliers_users",  "Click Suppliers Users report"),
                    ("test_suppliers_users_report", "test_04_fill_mandatory_fields",  "Fill Name and Description"),
                    ("test_suppliers_users_report", "test_05_save_custom_report",     "Save custom report"),
                    ("test_suppliers_users_report", "test_06_show_report",            "Show Report"),
                ],
            },
            {
                "menu": "Reports > Custom Reports > Admin > User Group",
                "rows": [
                    ("test_user_group_report", "test_01_login",                "Login as buyer user"),
                    ("test_user_group_report", "test_02_navigate_to_list",     "Navigate to Custom Report list"),
                    ("test_user_group_report", "test_03_click_user_group",     "Click User Group report"),
                    ("test_user_group_report", "test_04_fill_mandatory_fields","Fill Name and Description"),
                    ("test_user_group_report", "test_05_save_custom_report",   "Save custom report"),
                    ("test_user_group_report", "test_06_show_report",          "Show Report"),
                ],
            },
        ],
    },

    # ══════════════════════════════════════════════════════════════════════════
    # SUITE 8 : REPORTS – CUSTOM REPORTS (KANBAN)
    # ══════════════════════════════════════════════════════════════════════════
    {
        "suite": "Reports – Custom Reports (Kanban)",
        "color": RGBColor(0x1A, 0x3A, 0x5C),   # navy header
        "menus": [
            {
                "menu": "Reports > Custom Reports > Kanban > Active Cards",
                "rows": [
                    ("test_active_cards_report", "test_01_login",                  "Login as buyer user"),
                    ("test_active_cards_report", "test_02_navigate_to_list",       "Navigate to Custom Report list"),
                    ("test_active_cards_report", "test_03_open_active_cards_form", "Click Active Cards under Kanban"),
                    ("test_active_cards_report", "test_04_fill_report_form",       "Fill Name and Description"),
                    ("test_active_cards_report", "test_05_save_custom_report",     "Save custom report (xfail: known server error)"),
                    ("test_active_cards_report", "test_06_show_report",            "Show Report and count visible data rows"),
                ],
            },
            {
                "menu": "Reports > Custom Reports > Kanban > Cross Tab History",
                "rows": [
                    ("test_cross_tab_history_report", "test_01_login",                        "Login as buyer user"),
                    ("test_cross_tab_history_report", "test_02_navigate_to_list",             "Navigate to Custom Report list"),
                    ("test_cross_tab_history_report", "test_03_open_cross_tab_history_form",  "Click Cross Tab History under Kanban"),
                    ("test_cross_tab_history_report", "test_04_fill_report_form",             "Fill Name and Description"),
                    ("test_cross_tab_history_report", "test_05_save_custom_report",           "Save custom report"),
                    ("test_cross_tab_history_report", "test_06_show_report",                  "Show Report and click Change Filter"),
                ],
            },
            {
                "menu": "Reports > Custom Reports > Kanban > History",
                "rows": [
                    ("test_history_report", "test_01_login",             "Login as buyer user"),
                    ("test_history_report", "test_02_navigate_to_list",  "Navigate to Custom Report list"),
                    ("test_history_report", "test_03_open_history_form", "Click History under Kanban"),
                    ("test_history_report", "test_04_fill_report_form",  "Fill Name and Description"),
                    ("test_history_report", "test_05_save_custom_report","Save custom report"),
                    ("test_history_report", "test_06_show_report",       "Show Report and click Change Filter"),
                ],
            },
            {
                "menu": "Reports > Custom Reports > Kanban > Action Audit",
                "rows": [
                    ("test_action_audit_report", "test_01_login",                  "Login as buyer user"),
                    ("test_action_audit_report", "test_02_navigate_to_list",       "Navigate to Custom Report list"),
                    ("test_action_audit_report", "test_03_open_action_audit_form", "Click Action Audit under Kanban"),
                    ("test_action_audit_report", "test_04_fill_report_form",       "Fill Name and Description"),
                    ("test_action_audit_report", "test_05_save_custom_report",     "Save custom report"),
                    ("test_action_audit_report", "test_06_show_report",            "Show Report and click Change Filter"),
                ],
            },
        ],
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def set_cell_bg(cell, hex_color: str):
    """Set table cell background colour (hex string like 'FF0000')."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def rgb_to_hex(rgb: RGBColor) -> str:
    return f"{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"


def add_header_row(table, headers: list, bg_rgb: RGBColor):
    """Add a styled header row to a table."""
    row = table.rows[0]
    for i, hdr in enumerate(headers):
        cell = row.cells[i]
        cell.text = hdr
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        set_cell_bg(cell, rgb_to_hex(bg_rgb))
        para = cell.paragraphs[0]
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = para.runs[0]
        run.bold = True
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        run.font.size = Pt(9)


def add_data_row(table, values: list, shade: bool = False):
    """Append a data row to a table."""
    row = table.add_row()
    for i, val in enumerate(values):
        cell = row.cells[i]
        cell.text = str(val)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        para = cell.paragraphs[0]
        para.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = para.runs[0]
        run.font.size = Pt(8.5)
        if shade:
            set_cell_bg(cell, "F2F2F2")


def set_col_widths(table, widths_cm: list):
    """Approximate column widths (python-docx doesn't guarantee, but sets preferred)."""
    for row in table.rows:
        for i, w in enumerate(widths_cm):
            if i < len(row.cells):
                row.cells[i].width = Cm(w)


def add_menu_heading(doc, text: str, suite_color: RGBColor):
    """Add a menu-path heading paragraph."""
    para = doc.add_paragraph()
    para.paragraph_format.space_before = Pt(6)
    para.paragraph_format.space_after = Pt(2)
    run = para.add_run(text)
    run.bold = True
    run.font.size = Pt(10)
    run.font.color.rgb = suite_color


# ─────────────────────────────────────────────────────────────────────────────
# DOCUMENT BUILDER
# ─────────────────────────────────────────────────────────────────────────────

def build_document():
    doc = Document()

    # ── Page margins ──────────────────────────────────────────────────────────
    for section in doc.sections:
        section.top_margin    = Cm(1.5)
        section.bottom_margin = Cm(1.5)
        section.left_margin   = Cm(1.8)
        section.right_margin  = Cm(1.8)

    # ── Title ─────────────────────────────────────────────────────────────────
    title = doc.add_heading("QALS11 – Automated Test Cases Summary", level=1)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].font.size = Pt(16)
    title.runs[0].font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)

    sub = doc.add_paragraph(f"Prepared by: QA Automation Engineer   |   Date: {date.today():%B %d, %Y}   |   Application: QALS11 / Ultriva LMS")
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.runs[0].font.size = Pt(9)
    sub.runs[0].font.color.rgb = RGBColor(0x55, 0x55, 0x55)

    doc.add_paragraph()  # spacer

    # ── Summary table ─────────────────────────────────────────────────────────
    doc.add_heading("1. Executive Summary", level=2)

    summary_headers = ["#", "Suite", "Sub-Module / Menu Area", "Test Files", "Test Cases"]
    sum_table = doc.add_table(rows=1, cols=len(summary_headers))
    sum_table.style = "Table Grid"
    sum_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    add_header_row(sum_table, summary_headers, RGBColor(0x1F, 0x49, 0x7D))

    grand_files = 0
    grand_cases = 0
    suite_no = 1

    for suite in SUITE_DATA:
        total_files  = len(suite["menus"])
        total_cases  = sum(len(m["rows"]) for m in suite["menus"])
        grand_files += total_files
        grand_cases += total_cases
        shade = (suite_no % 2 == 0)
        add_data_row(sum_table,
                     [suite_no, suite["suite"],
                      ", ".join(set(m["menu"].split(" > ")[1] for m in suite["menus"]))[:90],
                      total_files, total_cases],
                     shade=shade)
        suite_no += 1

    # Totals row
    row = sum_table.add_row()
    totals = ["", "TOTAL", "", grand_files, grand_cases]
    for i, val in enumerate(totals):
        cell = row.cells[i]
        cell.text = str(val)
        set_cell_bg(cell, "D9E2F3")
        para = cell.paragraphs[0]
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = para.runs[0]
        run.bold = True
        run.font.size = Pt(9)

    set_col_widths(sum_table, [0.8, 4.5, 8.0, 2.0, 2.0])
    doc.add_paragraph()

    # ── Per-suite detail tables ────────────────────────────────────────────────
    doc.add_heading("2. Detailed Test Cases", level=2)

    col_headers = ["#", "Menu Path", "Test Module", "Test Case", "Description"]
    col_widths  = [0.7, 5.2, 4.5, 5.8, 7.5]

    for suite in SUITE_DATA:
        # Section heading
        sh = doc.add_heading(f"Suite: {suite['suite']}", level=3)
        sh.runs[0].font.color.rgb = suite["color"]

        detail_table = doc.add_table(rows=1, cols=len(col_headers))
        detail_table.style = "Table Grid"
        detail_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        add_header_row(detail_table, col_headers, suite["color"])

        row_no   = 1
        shade    = False
        prev_menu = None

        for menu_block in suite["menus"]:
            menu_label = menu_block["menu"]
            for (module, case, desc) in menu_block["rows"]:
                display_menu = menu_label if menu_label != prev_menu else ""
                add_data_row(detail_table,
                             [row_no, display_menu, module, case, desc],
                             shade=shade)
                prev_menu = menu_label
                row_no   += 1
            shade = not shade   # alternate row shading per menu block

        set_col_widths(detail_table, col_widths)
        doc.add_paragraph()  # spacer between suites

    return doc


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    out_path = rf"c:\Prcatices-AI\QALS11_TestCases_Summary_{date.today():%Y-%m-%d}.docx"
    print("Building document …")
    doc = build_document()
    doc.save(out_path)
    print(f"Saved: {out_path}")
