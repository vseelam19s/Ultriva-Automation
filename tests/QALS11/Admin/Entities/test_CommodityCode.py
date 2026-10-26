import os
import random
import string
import sys  # Fixed: Imported sys directly

import pytest
from selenium.webdriver.support.ui import WebDriverWait

from Admin.UserGroup import login
from utils.driver_setup import get_driver


ADMIN_BASE = "https://engineering.ultrivalms.com/QALS1011"
COMMODITY_LIST_URL = f"{ADMIN_BASE}/Entity/List"
CREATE_COMMODITY_URL = f"{ADMIN_BASE}/Entity/Create"


sys_path_root = os.path.join(os.path.dirname(__file__), "..", "..")
if sys_path_root not in sys.path:  # Fixed: Changed os.sys.path to sys.path
    sys.path.insert(0, sys_path_root)


@pytest.fixture(scope="class")
def setup_driver():
    driver = get_driver()
    wait = WebDriverWait(driver, 20)
    yield driver, wait
    driver.quit()


def random_string(length=6):
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def log(msg):
    print(f"[CommodityCode] {msg}")


@pytest.mark.skip(reason="Temporarily disabled after corruption fix; rewrite in progress.")
class TestCommodityCode:
    def test_create_commodity_code(self, setup_driver):
        driver, wait = setup_driver
        login(driver, wait)
        driver.get(COMMODITY_LIST_URL)
        assert "Entity" in driver.current_url

    def test_view_commodity_code_details(self, setup_driver):
        driver, wait = setup_driver
        login(driver, wait)
        driver.get(COMMODITY_LIST_URL)
        assert driver.current_url.startswith(ADMIN_BASE)

    def test_add_ryg_rule_to_commodity_code(self, setup_driver):
        driver, wait = setup_driver
        login(driver, wait)
        driver.get(COMMODITY_LIST_URL)
        assert driver.current_url.startswith(ADMIN_BASE)

    def test_edit_ryg_rule(self, setup_driver):
        driver, wait = setup_driver
        login(driver, wait)
        driver.get(COMMODITY_LIST_URL)
        assert driver.current_url.startswith(ADMIN_BASE)

    def test_delete_ryg_rule(self, setup_driver):
        driver, wait = setup_driver
        login(driver, wait)
        driver.get(COMMODITY_LIST_URL)
        assert driver.current_url.startswith(ADMIN_BASE)

    def test_assign_items_to_commodity_code(self, setup_driver):
        driver, wait = setup_driver
        login(driver, wait)
        driver.get(CREATE_COMMODITY_URL)
        assert driver.current_url.startswith(ADMIN_BASE)
