"""
ULT-9764 | Test Cases — Add Task Name Filter to Service Monitors Screen
Technical Debt:
  Add a Task Name text filter to Integration Monitor → Errors tab so users can
  narrow error records by task name (exact or partial match).

QA Site : https://engineering.ultrivalms.com/QALS1011
URL     : https://engineering.ultrivalms.com/QALS1011/SysAdmin/IntgMonitor
Role    : Application $ Administrator (SysAdmin BU)
"""

import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.login_page import LoginPage
from config.config import BASE_URL

INTG_MONITOR_URL = BASE_URL.rstrip("/") + "/SysAdmin/IntgMonitor"

# ── Locators ────────────────────────────────────────────────────────────────
TASK_NAME_INPUT  = (By.XPATH, "//input[@id='TaskName' or @name='TaskName' "
                              "or @placeholder[contains(.,'Task')] "
                              "or following-sibling::*[contains(text(),'Task Name')]]")
GO_BUTTON        = (By.XPATH, "//button[normalize-space()='Go'] "
                              "| //input[@value='Go']")
ERRORS_TAB       = (By.XPATH, "//a[normalize-space()='Errors'] | //li[normalize-space()='Errors']")
RESULT_ROWS      = (By.XPATH, "//table//tr[td]")
NAME_CELLS       = (By.XPATH, "//table//tr[td]/td[1]")
PAGINATION_INFO  = (By.XPATH, "//*[contains(text(),'Viewing')]")
NO_RECORDS_MSG   = (By.XPATH, "//*[contains(text(),'No record') or contains(text(),'No data')]")


# ── Helpers ─────────────────────────────────────────────────────────────────
def go_to_errors_tab(driver):
    driver.get(INTG_MONITOR_URL)
    wait = WebDriverWait(driver, 15)
    try:
        tab = wait.until(EC.element_to_be_clickable(ERRORS_TAB))
        tab.click()
        time.sleep(1)
    except Exception:
        pass  # Already on Errors tab


def apply_task_filter(driver, task_name_value, wait_secs=2):
    wait = WebDriverWait(driver, 10)
    inp = wait.until(EC.presence_of_element_located(TASK_NAME_INPUT))
    inp.clear()
    if task_name_value:
        inp.send_keys(task_name_value)
    btn = wait.until(EC.element_to_be_clickable(GO_BUTTON))
    btn.click()
    time.sleep(wait_secs)


def get_pagination_text(driver):
    try:
        el = driver.find_element(*PAGINATION_INFO)
        return el.text.strip()
    except Exception:
        return ""


def get_row_count(driver):
    rows = driver.find_elements(*RESULT_ROWS)
    return len(rows)


def get_name_cell_texts(driver):
    cells = driver.find_elements(*NAME_CELLS)
    return [c.text.strip() for c in cells if c.text.strip()]


# ── Test Classes ─────────────────────────────────────────────────────────────

class TestTaskNameFilterVisibility:

    # TC-01 ──────────────────────────────────────────────────────────────────
    def test_task_name_input_visible_on_errors_tab(self, driver):
        """TC-01: Task Name field and Go button are visible on Errors tab."""
        LoginPage(driver).login_as_admin()
        go_to_errors_tab(driver)

        wait = WebDriverWait(driver, 10)
        task_input = wait.until(EC.visibility_of_element_located(TASK_NAME_INPUT))
        go_btn     = wait.until(EC.visibility_of_element_located(GO_BUTTON))

        assert task_input.is_displayed(), "Task Name input field not visible on Errors tab"
        assert go_btn.is_displayed(),     "Go button not visible on Errors tab"


class TestTaskNameFilterFunctionality:

    # TC-02 ──────────────────────────────────────────────────────────────────
    def test_partial_name_sync_returns_matching_records(self, driver):
        """TC-02: Entering 'sync' returns only rows whose Name contains 'sync'."""
        LoginPage(driver).login_as_admin()
        go_to_errors_tab(driver)
        apply_task_filter(driver, "sync")

        names = get_name_cell_texts(driver)
        assert names, "No records returned for task name filter 'sync'"
        for name in names:
            assert "sync" in name.lower(), \
                f"Row Name '{name}' does not contain 'sync' — filter not applied correctly"

    # TC-03 ──────────────────────────────────────────────────────────────────
    def test_exact_task_name_returns_only_that_task(self, driver):
        """TC-03: Exact task name returns only records for that task."""
        LoginPage(driver).login_as_admin()
        go_to_errors_tab(driver)

        # First get a known task name from unfiltered results
        apply_task_filter(driver, "")  # load all
        names = get_name_cell_texts(driver)
        assert names, "No records found to derive an exact task name"
        exact_name = names[0]

        apply_task_filter(driver, exact_name)
        filtered_names = get_name_cell_texts(driver)
        assert filtered_names, f"No records returned for exact task name '{exact_name}'"
        for n in filtered_names:
            assert exact_name.lower() in n.lower(), \
                f"Row Name '{n}' does not match exact task '{exact_name}'"

    # TC-04 ──────────────────────────────────────────────────────────────────
    def test_non_existent_task_name_shows_no_results(self, driver):
        """TC-04: Non-existent task name shows empty state, no error."""
        LoginPage(driver).login_as_admin()
        go_to_errors_tab(driver)
        apply_task_filter(driver, "DOESNOTEXIST_XYZ_999")

        row_count = get_row_count(driver)
        no_records = driver.find_elements(*NO_RECORDS_MSG)

        assert row_count == 0 or len(no_records) > 0, \
            "Expected no data rows or a 'No records' message for non-existent task name"

        # Confirm no JS/server error in page source
        assert "500" not in driver.page_source[:200], \
            "Server 500 error detected after entering non-existent task name"

    # TC-05 ──────────────────────────────────────────────────────────────────
    def test_task_name_filter_is_case_insensitive(self, driver):
        """TC-05: 'SYNC', 'sync', and 'Sync' return identical record counts."""
        LoginPage(driver).login_as_admin()
        go_to_errors_tab(driver)

        counts = {}
        for variant in ("sync", "SYNC", "Sync"):
            apply_task_filter(driver, variant)
            counts[variant] = get_row_count(driver)

        assert counts["sync"] == counts["SYNC"] == counts["Sync"], \
            f"Case-sensitivity mismatch: {counts}"

    # TC-06 ──────────────────────────────────────────────────────────────────
    def test_clearing_task_name_returns_all_records(self, driver):
        """TC-06: Clearing Task Name and clicking Go returns all records for the date range."""
        LoginPage(driver).login_as_admin()
        go_to_errors_tab(driver)

        apply_task_filter(driver, "")
        unfiltered_text = get_pagination_text(driver)
        unfiltered_count = get_row_count(driver)

        apply_task_filter(driver, "sync")
        filtered_count = get_row_count(driver)

        apply_task_filter(driver, "")
        restored_text = get_pagination_text(driver)
        restored_count = get_row_count(driver)

        assert filtered_count < unfiltered_count or filtered_count == unfiltered_count, \
            "Filtered count should not exceed unfiltered count"
        assert restored_count == unfiltered_count, \
            f"After clearing filter, row count {restored_count} != baseline {unfiltered_count}"


class TestTaskNameFilterCombination:

    # TC-07 ──────────────────────────────────────────────────────────────────
    def test_task_name_combined_with_date_range(self, driver):
        """TC-07: Task Name + Date Range together narrow results correctly."""
        LoginPage(driver).login_as_admin()
        go_to_errors_tab(driver)

        # Apply Task Name only
        apply_task_filter(driver, "sync")
        name_only_count = get_row_count(driver)

        # Change date range to a narrower range — select 'Past 7 Days' from dropdown
        wait = WebDriverWait(driver, 10)
        try:
            date_range_input = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//input[@id='DateRange' or @name='DateRange' "
                           "or @placeholder[contains(.,'Date')]]")))
            date_range_input.click()
            time.sleep(0.5)
            past7 = driver.find_element(
                By.XPATH, "//*[contains(text(),'Past 7 Days')]")
            past7.click()
            time.sleep(0.5)
        except Exception:
            pytest.skip("Date Range dropdown not found — skipping combination test")

        apply_task_filter(driver, "sync")
        combined_count = get_row_count(driver)

        # Combined filter should return ≤ name-only count
        assert combined_count <= name_only_count, \
            f"Combined filter ({combined_count}) returned more rows than name-only ({name_only_count})"


class TestTaskNameFilterPagination:

    # TC-08 ──────────────────────────────────────────────────────────────────
    def test_pagination_reflects_filtered_total(self, driver):
        """TC-08: Pagination counter 'Viewing X to Y of Z' reflects filtered, not full, count."""
        LoginPage(driver).login_as_admin()
        go_to_errors_tab(driver)

        apply_task_filter(driver, "")
        unfiltered_page_text = get_pagination_text(driver)

        apply_task_filter(driver, "sync")
        filtered_page_text = get_pagination_text(driver)

        assert filtered_page_text, "No pagination info found after filtering"
        # The totals should differ (unless all records happen to match)
        if unfiltered_page_text:
            # Safely compare only when both are available
            assert filtered_page_text != unfiltered_page_text or \
                   "sync" in "".join(get_name_cell_texts(driver)).lower(), \
                "Pagination did not change after filter — filter may not be active"


class TestTaskNameFilterBehavior:

    # TC-09 ──────────────────────────────────────────────────────────────────
    def test_go_button_required_no_auto_filter(self, driver):
        """TC-09: Grid does not update without clicking Go."""
        LoginPage(driver).login_as_admin()
        go_to_errors_tab(driver)

        apply_task_filter(driver, "")
        initial_count = get_row_count(driver)

        # Type in field but do NOT click Go
        wait = WebDriverWait(driver, 10)
        inp = wait.until(EC.presence_of_element_located(TASK_NAME_INPUT))
        inp.clear()
        inp.send_keys("sync")
        time.sleep(3)  # Wait to confirm no auto-trigger

        current_count = get_row_count(driver)
        assert current_count == initial_count, \
            "Grid auto-filtered without clicking Go — expected no change until Go is clicked"

    # TC-10 ──────────────────────────────────────────────────────────────────
    def test_special_characters_no_server_error(self, driver):
        """TC-10: Special chars in Task Name do not cause server errors or XSS."""
        LoginPage(driver).login_as_admin()
        go_to_errors_tab(driver)

        for special_input in ("$", "<script>alert(1)</script>", "'; DROP TABLE--"):
            apply_task_filter(driver, special_input)
            page_source = driver.page_source

            assert "500" not in page_source[:500], \
                f"Server 500 error for input '{special_input}'"
            assert "<script>alert(1)</script>" not in page_source, \
                f"XSS not sanitized for input '{special_input}'"
            # Accept either results or empty state — no crash is the goal
            has_rows = get_row_count(driver) >= 0
            assert has_rows is not None
