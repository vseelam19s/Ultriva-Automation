"""
QALS11 | Buyer Report — Cycle Time Drill-down
=============================================
Flow:
1. Open Cycle Time Details by Item
2. Click any Item
3. On Cycle Time Details By Card ID, click Card ID
4. On Cycle Time Details for a Card, click Back to Summary
5. Verify it returns to Cycle Time Details By Card ID

Run:
    pytest reports/cycle_time_report.py -v -s
"""

import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
USERNAME = "buyeruser"
PASSWORD = "Ultriva!23"
PAUSE = 2


@pytest.fixture(scope="function")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    drv = webdriver.Chrome(options=options)
    drv.implicitly_wait(10)
    drv.set_page_load_timeout(120)
    drv.maximize_window()
    yield drv
    drv.quit()


def page_loaded(drv):
    WebDriverWait(drv, 60).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def scroll_to(drv, el):
    drv.execute_script("arguments[0].scrollIntoView({block:'center'})", el)
    time.sleep(0.3)


def safe_fill(drv, by, locator, value, timeout=15):
    el = WebDriverWait(drv, timeout).until(
        EC.visibility_of_element_located((by, locator))
    )
    scroll_to(drv, el)
    try:
        el.clear()
        el.send_keys(str(value))
    except Exception:
        drv.execute_script("arguments[0].value = arguments[1]", el, str(value))


def safe_click(drv, by, locator, timeout=15):
    el = WebDriverWait(drv, timeout).until(
        EC.element_to_be_clickable((by, locator))
    )
    scroll_to(drv, el)
    el.click()
    return el


def safe_screenshot(drv, name):
    try:
        drv.save_screenshot(name)
    except Exception:
        pass


def test_cycle_time_item_cardid_back_to_summary(driver):
    driver.get(f"{BASE_URL}/BuyerReport/CycleTime")
    page_loaded(driver)
    time.sleep(PAUSE)

    # If redirected to login, authenticate and open report again.
    if "login" in driver.current_url.lower() or driver.find_elements(By.ID, "login-button"):
        safe_fill(driver, By.ID, "UserName", USERNAME)
        safe_fill(driver, By.ID, "Password", PASSWORD)
        safe_click(driver, By.ID, "login-button")
        page_loaded(driver)
        driver.get(f"{BASE_URL}/BuyerReport/CycleTime")
        page_loaded(driver)
        time.sleep(PAUSE)

    heading = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((
            By.XPATH,
            "//h1[contains(.,'Cycle Time Details by Item') or "
            "contains(.,'Cycle Time Details By Item')]"
        ))
    )
    assert heading.is_displayed(), "Cycle Time Details by Item page did not load"
    safe_screenshot(driver, "cycle_time_by_item.png")

    item_link = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((
            By.XPATH,
            "(//table//tbody//tr[not(contains(.,'Total'))][1]//td[1]//a)[1] | "
            "(//table//tbody//tr[not(contains(.,'Total'))][1]//a)[1]"
        ))
    )
    scroll_to(driver, item_link)
    item_link.click()
    page_loaded(driver)
    time.sleep(PAUSE)

    card_heading = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((
            By.XPATH,
            "//h1[contains(.,'Cycle Time Details By Card ID') or "
            "contains(.,'Cycle Time Details by Card ID')]"
        ))
    )
    assert card_heading.is_displayed(), "Cycle Time Details By Card ID page did not load"
    safe_screenshot(driver, "cycle_time_by_card_id.png")

    card_id_link = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((
            By.XPATH,
            "(//table//tbody//tr[not(contains(.,'Total'))][1]//td[1]//a)[1] | "
            "(//table//tbody//tr[not(contains(.,'Total'))][1]//a)[1]"
        ))
    )
    scroll_to(driver, card_id_link)
    card_id_link.click()
    page_loaded(driver)
    time.sleep(PAUSE)

    card_detail_heading = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((
            By.XPATH,
            "//h1[contains(.,'Cycle Time Details for a Card')]"
        ))
    )
    assert card_detail_heading.is_displayed(), "Cycle Time Details for a Card page did not load"
    safe_screenshot(driver, "cycle_time_for_card.png")

    back_btn = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//a[contains(normalize-space(.),'Back to Summary')] | "
            "//button[contains(normalize-space(.),'Back to Summary')]"
        ))
    )
    scroll_to(driver, back_btn)
    back_btn.click()
    page_loaded(driver)
    time.sleep(PAUSE)

    card_heading_after_back = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((
            By.XPATH,
            "//h1[contains(.,'Cycle Time Details By Card ID') or "
            "contains(.,'Cycle Time Details by Card ID')]"
        ))
    )
    assert card_heading_after_back.is_displayed(), "Back to Summary did not return to Card ID summary page"
    safe_screenshot(driver, "cycle_time_back_to_summary.png")
