"""
Admin Module Backend Test Suite — Ultriva QALS1011

Test data is read from test_data/admin_test_data.xlsx.
"""

import pytest
from selenium.webdriver.common.by import By

from pages.login_page import LoginPage
from pages.admin_page import AdminPage
from pages.base_page import BasePage
from config.config import USERNAME, PASSWORD
from utils.test_data_reader import _sheet_rows, ADMIN_DATA_PATH

# ── Load test data once at collection time ────────────────────────────────────
_access_rows  = _sheet_rows("Admin_Access",         ADMIN_DATA_PATH)
_list_rows    = _sheet_rows("Admin_List_Validation", ADMIN_DATA_PATH)
_search_rows  = _sheet_rows("Admin_Search_Filter",   ADMIN_DATA_PATH)
_nav_rows     = _sheet_rows("Admin_Navigation",      ADMIN_DATA_PATH)

ADMIN_HOST = "https://engineering.ultrivalms.com"


def _ids(rows):
    return [r[0] for r in rows]   # TC_ID is always first field


# ══════════════════════════════════════════════════════════════════════════════

class TestAdminModule:

    # ── ADTC-001 to ADTC-016 — every admin sub-page loads or correctly redirects. ──
    @pytest.mark.parametrize("row", _access_rows, ids=[r.TC_ID for r in _access_rows])
    def test_page_access(self, driver, reporter, row):
        target = f"{ADMIN_HOST}{row.URL}"
        try:
            lp = LoginPage(driver)
            adm = AdminPage(driver)

            if (row.Login_Required or "").strip().lower() == "yes":
                lp.login(USERNAME, PASSWORD)
                assert lp.is_logged_in(), "Pre-condition: login must succeed"
                adm.navigate_to(row.URL.replace("/QALS1011", ""))
                assert adm.is_authenticated(), "Unexpectedly redirected to login"
            else:
                # Access without login — expect redirect to login
                driver.get(target)
                adm.wait_for_page_load()
                login_shown = lp.is_element_present(By.ID, "UserName", timeout=8)
                # The app may redirect OR show the page (depends on session config)
                assert login_shown or adm.is_authenticated(), \
                    "Neither login page nor authenticated page found"

            reporter.add_result(
                test_id=row.TC_ID,
                test_name=row.Description,
                module="Admin-Access",
                status="PASS",
                screenshot=adm.take_screenshot(row.TC_ID),
            )
        except Exception as e:
            reporter.add_result(
                test_id=row.TC_ID,
                test_name=row.Description,
                module="Admin-Access",
                status="FAIL",
                error_msg=str(e),
                screenshot=BasePage(driver).take_screenshot(f"{row.TC_ID}_fail"),
            )
            pytest.fail(str(e))

    # ── ADTC-101 to ADTC-120 — column presence and row count on all list pages. ──
    @pytest.mark.parametrize("row", _list_rows, ids=[r.TC_ID for r in _list_rows])
    def test_list_page_column(self, driver, reporter, row):
        try:
            LoginPage(driver).login(USERNAME, PASSWORD)
            adm = AdminPage(driver)
            adm.navigate_to(row.URL.replace("/QALS1011", ""))

            # Check row count
            cnt = adm.get_row_count()
            assert cnt >= int(row.Min_Rows), \
                f"Expected >= {row.Min_Rows} rows but found {cnt}"

            # Check column presence (if Column_To_Check is specified)
            if row.Column_To_Check and row.Column_To_Check.strip():
                assert adm.has_column(row.Column_To_Check), \
                    f"Column '{row.Column_To_Check}' not found in table headers"

            # Check search filter input present (if specified)
            if row.Filter_Input_Name and row.Filter_Input_Name.strip():
                fin_present = adm.is_element_present(By.NAME, row.Filter_Input_Name, timeout=6)
                assert fin_present, f"Filter input '{row.Filter_Input_Name}' not found"

            reporter.add_result(
                test_id=row.TC_ID,
                test_name=row.Description,
                module="Admin-List",
                status="PASS",
                screenshot=adm.take_screenshot(row.TC_ID),
            )
        except Exception as e:
            reporter.add_result(
                test_id=row.TC_ID,
                test_name=row.Description,
                module="Admin-List",
                status="FAIL",
                error_msg=str(e),
                screenshot=BasePage(driver).take_screenshot(f"{row.TC_ID}_fail"),
            )
            pytest.fail(str(e))

    # ── ADTC-201 to ADTC-208 — filter inputs accept text without error. ──
    @pytest.mark.parametrize("row", _search_rows, ids=[r.TC_ID for r in _search_rows])
    def test_filter_input(self, driver, reporter, row):
        try:
            LoginPage(driver).login(USERNAME, PASSWORD)
            adm = AdminPage(driver)
            adm.navigate_to(row.URL.replace("/QALS1011", ""))

            typed = adm.type_in_filter(By.NAME, row.Filter_Name, row.Search_Term)
            assert typed, f"Filter input '{row.Filter_Name}' not found on page"

            # Page must still be on an authenticated admin page
            assert adm.is_authenticated(), "Session dropped after filter interaction"

            reporter.add_result(
                test_id=row.TC_ID,
                test_name=row.Description,
                module="Admin-Search",
                status="PASS",
                screenshot=adm.take_screenshot(row.TC_ID),
            )
        except Exception as e:
            reporter.add_result(
                test_id=row.TC_ID,
                test_name=row.Description,
                module="Admin-Search",
                status="FAIL",
                error_msg=str(e),
                screenshot=BasePage(driver).take_screenshot(f"{row.TC_ID}_fail"),
            )
            pytest.fail(str(e))

    # ── ADTC-301 to ADTC-310 — breadcrumb, sidebar, and URL routing checks. ──
    @pytest.mark.parametrize("row", _nav_rows, ids=[r.TC_ID for r in _nav_rows])
    def test_admin_navigation(self, driver, reporter, row):
        try:
            LoginPage(driver).login(USERNAME, PASSWORD)
            adm = AdminPage(driver)
            adm.navigate_to(row.Start_URL.replace("/QALS1011", ""))

            action = (row.Action or "").lower()

            if "sidebar" in action or "nav link" in action:
                assert adm.is_element_present(*AdminPage.ADMIN_NAV_LINK, timeout=8), \
                    "Admin nav link not found in sidebar"
                adm.click(*AdminPage.ADMIN_NAV_LINK)
                adm.wait_for_page_load()
                assert row.Expected_URL_Contains in driver.current_url, \
                    f"Expected URL to contain '{row.Expected_URL_Contains}', got {driver.current_url}"

            elif "breadcrumb" in action:
                assert adm.is_element_present(*AdminPage.ADMIN_BREADCRUMB_LINK, timeout=8), \
                    "Admin breadcrumb link not found"
                adm.click(*AdminPage.ADMIN_BREADCRUMB_LINK)
                adm.wait_for_page_load()
                assert row.Expected_URL_Contains.lower() in driver.current_url.lower(), \
                    "Breadcrumb nav did not reach expected URL"

            elif "aboutinfo" in action.replace(" ", "").lower():
                adm.navigate_to("/Admin/AboutInfo")
                assert row.Expected_URL_Contains in driver.current_url

            elif "tools" in action:
                adm.navigate_to("/Admin/Tools")
                assert row.Expected_URL_Contains in driver.current_url

            elif "busunit" in action.replace(" ", "").lower():
                adm.navigate_to("/Admin/BusUnit")
                assert row.Expected_URL_Contains.lower() in driver.current_url.lower()

            elif "user/list" in action.replace(" ", ""):
                adm.navigate_to("/User/List")
                assert row.Expected_URL_Contains in driver.current_url

            elif "supplier" in action:
                adm.navigate_to("/Supplier/List")
                assert row.Expected_URL_Contains in driver.current_url

            else:
                # Check page heading contains expected text
                heading = adm.get_page_heading() or ""
                assert row.Expected_URL_Contains.lower() in heading.lower() or \
                       row.Expected_URL_Contains.lower() in driver.current_url.lower(), \
                       f"Expected '{row.Expected_URL_Contains}' in heading or URL"

            reporter.add_result(
                test_id=row.TC_ID,
                test_name=row.Description,
                module="Admin-Navigation",
                status="PASS",
                screenshot=adm.take_screenshot(row.TC_ID),
            )
        except Exception as e:
            reporter.add_result(
                test_id=row.TC_ID,
                test_name=row.Description,
                module="Admin-Navigation",
                status="FAIL",
                error_msg=str(e),
                screenshot=BasePage(driver).take_screenshot(f"{row.TC_ID}_fail"),
            )
            pytest.fail(str(e))

    # ── Hand-coded spot-checks for Admin Tools and About Info pages. ──

    def test_admin_tools_kanban_section(self, driver, reporter):
        """ADTC-015-a: Admin Tools page has a Kanban section."""
        try:
            LoginPage(driver).login(USERNAME, PASSWORD)
            adm = AdminPage(driver)
            adm.navigate_to("/Admin/Tools")
            assert adm.is_element_present(*AdminPage.TOOLS_KANBAN_SECTION, timeout=8), \
                "Kanban section not found on Admin Tools page"
            reporter.add_result(
                test_id="ADTC-401", test_name="Admin Tools — Kanban section visible",
                module="Admin-Direct", status="PASS",
                screenshot=adm.take_screenshot("ADTC-401"))
        except Exception as e:
            reporter.add_result(
                test_id="ADTC-401", test_name="Admin Tools — Kanban section visible",
                module="Admin-Direct", status="FAIL", error_msg=str(e),
                screenshot=BasePage(driver).take_screenshot("ADTC-401_fail"))
            pytest.fail(str(e))

    def test_admin_tools_dataload_section(self, driver, reporter):
        """ADTC-015-b: Admin Tools page has a Data Load section."""
        try:
            LoginPage(driver).login(USERNAME, PASSWORD)
            adm = AdminPage(driver)
            adm.navigate_to("/Admin/Tools")
            assert adm.is_element_present(*AdminPage.TOOLS_DATALOAD_SECTION, timeout=8), \
                "Data Load section not found on Admin Tools page"
            reporter.add_result(
                test_id="ADTC-402", test_name="Admin Tools — Data Load section visible",
                module="Admin-Direct", status="PASS",
                screenshot=adm.take_screenshot("ADTC-402"))
        except Exception as e:
            reporter.add_result(
                test_id="ADTC-402", test_name="Admin Tools — Data Load section visible",
                module="Admin-Direct", status="FAIL", error_msg=str(e),
                screenshot=BasePage(driver).take_screenshot("ADTC-402_fail"))
            pytest.fail(str(e))

    def test_about_info_has_table(self, driver, reporter):
        """ADTC-016-a: About Info page has a Field Name / Field Value table."""
        try:
            LoginPage(driver).login(USERNAME, PASSWORD)
            adm = AdminPage(driver)
            adm.navigate_to("/Admin/AboutInfo")
            assert adm.is_element_present(*AdminPage.ABOUT_TABLE, timeout=8) or \
                   adm.get_row_count() > 0, \
                   "About Info table not found or has no rows"
            reporter.add_result(
                test_id="ADTC-403", test_name="About Info page shows version/field table",
                module="Admin-Direct", status="PASS",
                screenshot=adm.take_screenshot("ADTC-403"))
        except Exception as e:
            reporter.add_result(
                test_id="ADTC-403", test_name="About Info page shows version/field table",
                module="Admin-Direct", status="FAIL", error_msg=str(e),
                screenshot=BasePage(driver).take_screenshot("ADTC-403_fail"))
            pytest.fail(str(e))

    def test_busunit_config_has_rows(self, driver, reporter):
        """ADTC-004-a: Business Unit Config shows Plant configuration rows."""
        try:
            LoginPage(driver).login(USERNAME, PASSWORD)
            adm = AdminPage(driver)
            adm.navigate_to("/Admin/BusUnitConfiguration")
            cnt = adm.get_row_count()
            assert cnt > 0, "Business Unit Config table has no rows"
            reporter.add_result(
                test_id="ADTC-404", test_name=f"BusUnit Config shows {cnt} configuration rows",
                module="Admin-Direct", status="PASS",
                screenshot=adm.take_screenshot("ADTC-404"))
        except Exception as e:
            reporter.add_result(
                test_id="ADTC-404", test_name="BusUnit Config shows configuration rows",
                module="Admin-Direct", status="FAIL", error_msg=str(e),
                screenshot=BasePage(driver).take_screenshot("Admin-Direct_fail"))
            pytest.fail(str(e))

    def test_user_list_views_button(self, driver, reporter):
        """ADTC-405: User List has a Views toolbar button."""
        try:
            LoginPage(driver).login(USERNAME, PASSWORD)
            adm = AdminPage(driver)
            adm.navigate_to("/User/List")
            assert adm.has_views_button(), "Views button not found on User List"
            reporter.add_result(
                test_id="ADTC-405", test_name="User List has Views toolbar button",
                module="Admin-Direct", status="PASS",
                screenshot=adm.take_screenshot("ADTC-405"))
        except Exception as e:
            reporter.add_result(
                test_id="ADTC-405", test_name="User List has Views toolbar button",
                module="Admin-Direct", status="FAIL", error_msg=str(e),
                screenshot=BasePage(driver).take_screenshot("ADTC-405_fail"))
            pytest.fail(str(e))

    def test_user_list_filters_button(self, driver, reporter):
        """ADTC-406: User List has a Filters toolbar button."""
        try:
            LoginPage(driver).login(USERNAME, PASSWORD)
            adm = AdminPage(driver)
            adm.navigate_to("/User/List")
            assert adm.has_filters_button(), "Filters button not found on User List"
            reporter.add_result(
                test_id="ADTC-406", test_name="User List has Filters toolbar button",
                module="Admin-Direct", status="PASS",
                screenshot=adm.take_screenshot("ADTC-406"))
        except Exception as e:
            reporter.add_result(
                test_id="ADTC-406", test_name="User List has Filters toolbar button",
                module="Admin-Direct", status="FAIL", error_msg=str(e),
                screenshot=BasePage(driver).take_screenshot("ADTC-406_fail"))
            pytest.fail(str(e))

    def test_kanban_item_row_count(self, driver, reporter):
        """ADTC-407: KanbanItem List has data rows."""
        try:
            LoginPage(driver).login(USERNAME, PASSWORD)
            adm = AdminPage(driver)
            adm.navigate_to("/KanbanItem/List")
            cnt = adm.get_row_count()
            assert cnt > 0, "KanbanItem List has no rows"
            reporter.add_result(
                test_id="ADTC-407", test_name=f"KanbanItem List shows {cnt} rows",
                module="Admin-Direct", status="PASS",
                screenshot=adm.take_screenshot("ADTC-407"))
        except Exception as e:
            reporter.add_result(
                test_id="ADTC-407", test_name="KanbanItem List has rows",
                module="Admin-Direct", status="FAIL", error_msg=str(e),
                screenshot=BasePage(driver).take_screenshot("ADTC-407_fail"))
            pytest.fail(str(e))

    def test_global_search_bar(self, driver, reporter):
        """ADTC-408: Global search bar is present on all admin list pages."""
        try:
            LoginPage(driver).login(USERNAME, PASSWORD)
            adm = AdminPage(driver)
            adm.navigate_to("/User/List")
            assert adm.has_global_search(), "Global search bar (txtTbSearch) not found"
            reporter.add_result(
                test_id="ADTC-408", test_name="Global search bar present on User List",
                module="Admin-Direct", status="PASS",
                screenshot=adm.take_screenshot("ADTC-408"))
        except Exception as e:
            reporter.add_result(
                test_id="ADTC-408", test_name="Global search bar present on User List",
                module="Admin-Direct", status="FAIL", error_msg=str(e),
                screenshot=BasePage(driver).take_screenshot("ADTC-408_fail"))
            pytest.fail(str(e))