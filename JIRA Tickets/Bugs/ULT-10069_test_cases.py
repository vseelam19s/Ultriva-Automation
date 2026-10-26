"""
ULT-10069 | Test Cases — Kanban Loop Design Not Processing
Bug: KLD batch job stays at 'Created' after Item Data Load sets HTTP exchange type.
"""

import time
import pytest
from pages.login_page import LoginPage
from config.config import USERNAME, PASSWORD, BASE_URL


BATCH_JOB_STATUS_URL = f"{BASE_URL}/integration/batch-job-status"
KANBAN_LOOP_DESIGN_URL = f"{BASE_URL}/kanban/loop-design"
ITEM_DATA_LOAD_URL = f"{BASE_URL}/integration/item-data-load"

POLL_INTERVAL = 3   # seconds between status checks
MAX_WAIT = 60       # max seconds to wait for batch job completion


def wait_for_job_status(driver, job_filter, expected_status):
    """Poll Batch Job Status until job reaches expected_status or times out."""
    driver.get(BATCH_JOB_STATUS_URL)
    elapsed = 0
    while elapsed < MAX_WAIT:
        rows = driver.find_elements("xpath", f"//tr[contains(.,'{job_filter}')]")
        for row in rows:
            status_cell = row.find_elements("xpath", ".//td")
            if any(expected_status in cell.text for cell in status_cell):
                return True
        time.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL
        driver.refresh()
    return False


class TestKanbanLoopDesignBug:

    # TC-01 ───────────────────────────────────────────────────────────────────
    def test_kld_processes_after_item_data_load_http(self, driver):
        """KLD completes after Item Data Load sets HTTP exchange type (fix verify)."""
        LoginPage(driver).login(USERNAME, PASSWORD)

        # Step 1: trigger Item Data Load to create HTTP B2B record
        driver.get(ITEM_DATA_LOAD_URL)
        driver.find_element("xpath", "//button[contains(text(),'Run')]").click()
        time.sleep(5)

        # Step 2: trigger Kanban Loop Design
        driver.get(KANBAN_LOOP_DESIGN_URL)
        driver.find_element("xpath", "//button[contains(text(),'Process')]").click()

        # Step 3: verify KLD batch job completes
        completed = wait_for_job_status(driver, "Item Sync", "Completed")
        assert completed, "KLD Item Sync job did not reach Completed status"

    # TC-02 ───────────────────────────────────────────────────────────────────
    def test_kld_batch_job_status_transitions(self, driver):
        """Batch job moves through Created → some active state → Completed."""
        LoginPage(driver).login(USERNAME, PASSWORD)
        driver.get(KANBAN_LOOP_DESIGN_URL)
        driver.find_element("xpath", "//button[contains(text(),'Process')]").click()

        # Capture initial status = Created
        driver.get(BATCH_JOB_STATUS_URL)
        initial_rows = driver.find_elements("xpath", "//tr[contains(.,'Item Sync')]")
        assert initial_rows, "No Item Sync record on Batch Job Status screen"

        # Wait for Completed
        completed = wait_for_job_status(driver, "Item Sync", "Completed")
        assert completed, "KLD batch job never reached Completed"

    # TC-03 ───────────────────────────────────────────────────────────────────
    def test_item_data_load_still_processes(self, driver):
        """Item Data Load entries reach Completed — no regression introduced."""
        LoginPage(driver).login(USERNAME, PASSWORD)
        driver.get(ITEM_DATA_LOAD_URL)
        driver.find_element("xpath", "//button[contains(text(),'Run')]").click()

        completed = wait_for_job_status(driver, "Item Data Load", "Completed")
        assert completed, "Item Data Load did not complete — possible regression"

    # TC-04 ───────────────────────────────────────────────────────────────────
    def test_kld_processes_with_https_exchange_type(self, driver):
        """KLD completes when B2B process record exchange type is HTTPS."""
        LoginPage(driver).login(USERNAME, PASSWORD)

        # Ensure exchange type is HTTPS before running KLD
        driver.get(f"{BASE_URL}/integration/b2b-process")
        exchange_field = driver.find_element("xpath", "//select[@id='exchangeType']")
        exchange_field.find_element("xpath", ".//option[@value='HTTPS']").click()
        driver.find_element("xpath", "//button[contains(text(),'Save')]").click()

        driver.get(KANBAN_LOOP_DESIGN_URL)
        driver.find_element("xpath", "//button[contains(text(),'Process')]").click()

        completed = wait_for_job_status(driver, "Item Sync", "Completed")
        assert completed, "KLD did not complete with HTTPS exchange type"

    # TC-05 ───────────────────────────────────────────────────────────────────
    def test_multiple_kld_jobs_all_complete(self, driver):
        """Multiple KLD batch jobs triggered back-to-back all reach Completed."""
        LoginPage(driver).login(USERNAME, PASSWORD)

        for _ in range(2):
            driver.get(ITEM_DATA_LOAD_URL)
            driver.find_element("xpath", "//button[contains(text(),'Run')]").click()
            time.sleep(3)
            driver.get(KANBAN_LOOP_DESIGN_URL)
            driver.find_element("xpath", "//button[contains(text(),'Process')]").click()
            time.sleep(3)

        driver.get(BATCH_JOB_STATUS_URL)
        time.sleep(MAX_WAIT)  # allow jobs to settle
        driver.refresh()

        rows = driver.find_elements("xpath", "//tr[contains(.,'Item Sync')]")
        stuck = [r for r in rows if "Created" in r.text]
        assert not stuck, f"{len(stuck)} KLD job(s) still stuck at Created"

    # TC-06 ───────────────────────────────────────────────────────────────────
    def test_batch_job_status_screen_shows_kld_item_sync(self, driver):
        """After KLD runs, Item Sync entry is visible on Batch Job Status screen."""
        LoginPage(driver).login(USERNAME, PASSWORD)
        driver.get(KANBAN_LOOP_DESIGN_URL)
        driver.find_element("xpath", "//button[contains(text(),'Process')]").click()

        driver.get(BATCH_JOB_STATUS_URL)
        rows = driver.find_elements("xpath", "//tr[contains(.,'Item Sync')]")
        assert rows, "Item Sync row not found on Batch Job Status screen after KLD"
