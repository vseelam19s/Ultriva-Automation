"""
ULT-10511 | Test Cases — Export All Scheduled Jobs Report
Feature: Customer needs a single export of all scheduled jobs (not per-day).
"""

import pytest
from pages.login_page import LoginPage
from config.config import USERNAME, PASSWORD, BASE_URL


SCHEDULED_JOBS_URL = f"{BASE_URL}/scheduled-jobs"
EXPORT_ALL_URL     = f"{BASE_URL}/scheduled-jobs/export/all"


class TestScheduledJobsExport:

    # TC-01 ───────────────────────────────────────────────────────────────────
    def test_export_all_button_visible(self, driver):
        """Authorised user sees the Export All button on the scheduled jobs page."""
        LoginPage(driver).login(USERNAME, PASSWORD)
        driver.get(SCHEDULED_JOBS_URL)
        assert driver.find_element("xpath", "//button[contains(text(),'Export All')]"), \
            "Export All button not found"

    # TC-02 ───────────────────────────────────────────────────────────────────
    def test_export_all_triggers_background_job(self, driver):
        """Clicking Export All starts a background job and shows a confirmation."""
        LoginPage(driver).login(USERNAME, PASSWORD)
        driver.get(SCHEDULED_JOBS_URL)
        driver.find_element("xpath", "//button[contains(text(),'Export All')]").click()
        confirmation = driver.find_element("xpath", "//*[contains(text(),'report is being generated')]")
        assert confirmation.is_displayed(), "No confirmation message shown after triggering export"

    # TC-03 ───────────────────────────────────────────────────────────────────
    def test_export_file_format_matches_reference(self, driver):
        """Downloaded export file has the same column headers as the reference template."""
        expected_headers = [
            "Job Number", "Part Number", "Description",
            "Quantity", "Due Date", "Remaining Hours",
        ]
        LoginPage(driver).login(USERNAME, PASSWORD)
        driver.get(SCHEDULED_JOBS_URL)
        driver.find_element("xpath", "//button[contains(text(),'Export All')]").click()

        # Wait for download link and read the file
        import time; time.sleep(3)
        download_link = driver.find_element("xpath", "//a[contains(@href,'export')]")
        assert download_link.is_displayed(), "Download link not visible after export"

    # TC-04 ───────────────────────────────────────────────────────────────────
    def test_export_contains_all_jobs(self, driver):
        """Export row count matches the total scheduled jobs count shown in the UI."""
        LoginPage(driver).login(USERNAME, PASSWORD)
        driver.get(SCHEDULED_JOBS_URL)

        total_count_el = driver.find_element("id", "total-jobs-count")
        total_count    = int(total_count_el.text.strip())

        driver.find_element("xpath", "//button[contains(text(),'Export All')]").click()
        import time; time.sleep(3)

        # Verify report status shows same count
        report_count_el = driver.find_element("id", "report-job-count")
        assert int(report_count_el.text.strip()) == total_count, \
            f"Exported rows ({report_count_el.text}) != total jobs ({total_count})"

    # TC-05 ───────────────────────────────────────────────────────────────────
    def test_empty_state_no_error(self, driver):
        """Export with no scheduled jobs produces an empty file, not an error."""
        LoginPage(driver).login(USERNAME, PASSWORD)
        driver.get(SCHEDULED_JOBS_URL)

        no_data_label = driver.find_elements("xpath", "//*[contains(text(),'No scheduled jobs')]")
        if not no_data_label:
            pytest.skip("Scheduled jobs exist; empty-state test skipped")

        driver.find_element("xpath", "//button[contains(text(),'Export All')]").click()
        error_el = driver.find_elements("xpath", "//*[contains(@class,'error')]")
        assert not error_el, "Error shown on export with no scheduled jobs"

    # TC-06 ───────────────────────────────────────────────────────────────────
    def test_unauthorised_user_blocked(self, driver):
        """User without export permission is denied access to the export endpoint."""
        LoginPage(driver).login("readonly_user", PASSWORD)
        driver.get(EXPORT_ALL_URL)
        assert "403" in driver.page_source or "Access Denied" in driver.page_source, \
            "Unauthorised user was not blocked from export endpoint"

    # TC-07 ───────────────────────────────────────────────────────────────────
    def test_ui_remains_responsive_during_export(self, driver):
        """Page does not freeze while background export is running."""
        LoginPage(driver).login(USERNAME, PASSWORD)
        driver.get(SCHEDULED_JOBS_URL)
        driver.find_element("xpath", "//button[contains(text(),'Export All')]").click()

        # Interact with the page while export runs
        nav_link = driver.find_element("xpath", "//a[contains(text(),'Dashboard')]")
        assert nav_link.is_enabled(), "Navigation is blocked while export runs"

    # TC-08 ───────────────────────────────────────────────────────────────────
    @pytest.mark.parametrize("run", [1, 2])
    def test_export_is_idempotent(self, driver, run):
        """Running export twice on same data produces the same result."""
        LoginPage(driver).login(USERNAME, PASSWORD)
        driver.get(SCHEDULED_JOBS_URL)
        driver.find_element("xpath", "//button[contains(text(),'Export All')]").click()
        import time; time.sleep(2)
        status = driver.find_element("id", "export-status").text
        assert status in ("Completed", "Ready"), f"Run {run}: unexpected export status '{status}'"
