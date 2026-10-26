"""

test_abc_code.py – Selenium test cases for Admin > ABC Code natively built for Pytest.

Covered Test Cases:

    TC-ABC-01: Add a new ABC Code (Add flow)

    TC-ABC-02: Edit an existing ABC Code (Edit flow)

    TC-ABC-03: View an existing ABC Code and cancel (View flow)

    TC-ABC-04: Assign Items to ABC Code

Navigation Path:

    Admin > Entities (left nav) > ABC Code

"""

from Admin.UserGroup import login
from utils.driver_setup import get_driver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import sys

import os

import time

import random

import string

import pytest

# Maintain the system path adjustment for your utilities

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


# ── Constants ────────────────────────────────────────────────────────────────

ADMIN_BASE = "https://engineering.ultrivalms.com/QALS1011"

ABC_LIST_URL = f"{ADMIN_BASE}/Entity/List?tk=$Classification&busGID=BSU22ZAQALQG&A~1~ABC&"

# ── Pytest Fixture Setup ─────────────────────────────────────────────────────


@pytest.fixture(scope="class")
def setup_driver():
    """Initializes webdriver once for the entire class block and tears down after."""

    driver = get_driver()

    wait = WebDriverWait(driver, 20)

    yield driver, wait

    driver.quit()

# ── Helper Utilities ─────────────────────────────────────────────────────────


def random_string(length=5):

    return "".join(
        random.choices(
            string.ascii_uppercase +
            string.digits,
            k=length))


def log(msg):

    print(f"\n[{time.strftime('%H:%M:%S')}][ABCCode] {msg}")


def _search_code(driver, wait, code):

    search_xpath = "//input[contains(@placeholder,'Find Code') or @type='text']"

    try:

        box = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, search_xpath)))

        wait.until(EC.element_to_be_clickable((By.XPATH, search_xpath)))

        box.clear()

        box.send_keys(code)

    except Exception as exc:

        log(f"Search box not interactable: {exc} — trying JS fallback.")

        box = driver.find_element(By.XPATH, search_xpath)

        driver.execute_script(

            "arguments[0].value = arguments[1];"

            "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));",

            box, code,

        )

    time.sleep(2)

# ── Test Suite Class Container ───────────────────────────────────────────────


@pytest.mark.usefixtures("setup_driver")
class TestAbccode:
    def test_tc_abc_01_add_code(self, setup_driver):
        """TC-ABC-01 – Add a new ABC Code."""
        driver, wait = setup_driver
        log("=== TC-ABC-01: Add ABC Code ===")

        login(driver, wait)
        log("Step 1 – Navigating to ABC Code list…")
        driver.get(ABC_LIST_URL)
        time.sleep(2)

        add_btn_xpath = "//button[contains(.,'Add')] | //a[contains(.,'Add')]"
        try:
            add_btn = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, add_btn_xpath)))
            driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", add_btn)
            driver.execute_script("arguments[0].click();", add_btn)
            log("Step 2 – Clicked '+ Add' button.")
            time.sleep(2)
        except Exception as exc:
            pytest.fail(f"Step 2 FAILED – Add button not found: {exc}")

        code = f"ABC_{random_string(4)}"
        title = f"ABCTitle_{random_string(4)}"
        desc = f"ABCDesc_{random_string(6)}"
        log(f"Step 3 – Entering Code='{code}', Title='{title}', Desc='{desc}'")

        try:
            driver.find_element(By.NAME, "CODE$ItemName").send_keys(code)
            driver.find_element(By.NAME, "CODE$Title").send_keys(title)
            driver.find_element(By.NAME, "CODE$Description").send_keys(desc)
        except Exception as exc:
            pytest.fail(f"Step 3 FAILED – Could not fill form fields: {exc}")

        save_xpath = (
            "//span[normalize-space()='Save' and contains(@class,'btn-toolbar-right-item')]"
            " | //button[normalize-space()='Save']"
            " | //a[normalize-space()='Save']")
        try:
            save_btn = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, save_xpath)))
            driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", save_btn)
            driver.execute_script("arguments[0].click();", save_btn)
            log("Step 4 – Clicked Save button.")
            time.sleep(2)
        except Exception as exc:
            pytest.fail(f"Step 4 FAILED – Save button not found: {exc}")

        driver.get(ABC_LIST_URL)
        time.sleep(2)
        _search_code(driver, wait, code)
        found = driver.find_elements(By.XPATH, f"//td[contains(.,'{code}')]")

        assert len(
            found) > 0, f"Step 5 FAIL – ABC Code '{code}' not found after creation."
        log(f"Step 5 PASS – ABC Code '{code}' created successfully.")

    def test_tc_abc_02_edit_code(self, setup_driver):
        """TC-ABC-02 – Edit an existing ABC Code."""
        driver, wait = setup_driver

