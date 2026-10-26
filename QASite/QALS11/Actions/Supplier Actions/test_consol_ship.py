"""
QALS11 | Actions > Supplier Actions > Consol Ship
=================================================
URL   : https://engineering.ultrivalms.com/QALS1011/SupplierAction/ConsolShipItems
URL   : https://engineering.ultrivalms.com/QALS1011/SupplierAction/ConsolShipCards
User  : supnewuser / Ultriva!23

Test Flow
---------
  1. Login as supnewuser
  2. Navigate to Consol Ship Items
  3. Select the item from the Consol Ship Items list and open the Consol Ship Cards page
  4. Select cards on the Consol Ship Cards page
  5. Click the Ship action on the Consol Ship Cards page only
"""

import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
CONSOL_ITEMS_URL = f"{BASE_URL}/SupplierAction/ConsolShipItems"
CONSOL_CARDS_URL = f"{BASE_URL}/SupplierAction/ConsolShipCards"
USERNAME = "supnewuser"
PASSWORD = "Ultriva!23"
PAUSE = 1.5


class ConsolShipPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    def _is_real_ship_action(self, element):
        """Reject broad navigation/menu items like 'Consolidator Ship' and keep only the cards-page action."""
        if element is None:
            return False
        try:
            tag = (element.tag_name or "").lower()
            text = " ".join((element.text or element.get_attribute("innerText") or "").split()).strip()
            value = (element.get_attribute("value") or "").strip()
            combined = (text or value).lower()
            classes = (element.get_attribute("class") or "").lower()
            href = (element.get_attribute("href") or "").lower()
            ancestors = element.find_elements(
                By.XPATH,
                "./ancestor::*[contains(@class, 'menu') or contains(@class, 'nav') or contains(@class, 'dropdown') or contains(@class, 'breadcrumb') or contains(@role, 'menu')]",
            )
        except Exception:
            return False

        if not combined:
            return False
        if any(token in combined for token in ["consolidator", "consol ship", "ship date", "ship to", "ship cards"]):
            return False
        if ancestors:
            return False
        if "ship" not in combined:
            return False
        if tag in {"button", "input", "span"}:
            return True
        if tag == "a":
            return bool(href) and not any(token in href for token in ["consolshipitems", "consolshipcards", "supplieraction"])
        return False

    def click_ship_button(self):
        """Click only the actual Ship action on the Consol Ship Cards page and keep the flow in the Consol Ship Cards screen."""
        current_url = (self.driver.current_url or "").lower()
        if "consolshipcards" not in current_url and "supplieraction" not in current_url:
            self.driver.get(CONSOL_CARDS_URL)
            wait_ready(self.driver)
            time.sleep(PAUSE)

        ship_ids = ["btndoActTop", "btndoActBot"]
        clicked = False

        for ship_id in ship_ids:
            try:
                el = self.driver.find_element(By.ID, ship_id)
                if el.is_displayed() and el.is_enabled():
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();",
                        el,
                    )
                    clicked = True
                    break
            except Exception:
                continue

        if clicked:
            try:
                WebDriverWait(self.driver, 3).until(EC.alert_is_present())
                alert = self.driver.switch_to.alert
                alert.accept()
            except Exception:
                pass
            return True

        ship_locators = [
            (
                By.XPATH,
                "//button[normalize-space(.)='Ship' or normalize-space(@value)='Ship' or .//span[normalize-space()='Ship']][not(ancestor::*[contains(@class, 'menu') or contains(@class, 'nav') or contains(@class, 'dropdown') or contains(@class, 'breadcrumb') or contains(@role, 'menu')])]",
            ),
            (
                By.XPATH,
                "//span[normalize-space(.)='Ship' or normalize-space(@title)='Ship'][contains(@class, 'vd-blue-btn') or @id='btndoActTop' or @id='btndoActBot'][not(ancestor::*[contains(@class, 'menu') or contains(@class, 'nav') or contains(@class, 'dropdown') or contains(@class, 'breadcrumb') or contains(@role, 'menu')])]",
            ),
            (
                By.XPATH,
                "//input[@type='button' or @type='submit'][normalize-space(@value)='Ship'][not(ancestor::*[contains(@class, 'menu') or contains(@class, 'nav') or contains(@class, 'dropdown') or contains(@class, 'breadcrumb') or contains(@role, 'menu')])]",
            ),
            (
                By.XPATH,
                "//a[normalize-space(.)='Ship' or normalize-space(@title)='Ship' or .//span[normalize-space()='Ship']][not(contains(normalize-space(.), 'Consolidator')) and not(contains(normalize-space(.), 'Ship Date')) and not(contains(normalize-space(.), 'Ship To')) and not(ancestor::*[contains(@class, 'menu') or contains(@class, 'nav') or contains(@class, 'dropdown') or contains(@class, 'breadcrumb') or contains(@role, 'menu')])]",
            ),
        ]

        for by, loc in ship_locators:
            try:
                elements = self.driver.find_elements(by, loc)
                for el in elements:
                    if not el.is_displayed() or not el.is_enabled():
                        continue
                    if not self._is_real_ship_action(el):
                        continue
                    try:
                        self.wait.until(EC.element_to_be_clickable(el))
                        el.click()
                        clicked = True
                        break
                    except Exception:
                        try:
                            self.driver.execute_script("arguments[0].click();", el)
                            clicked = True
                            break
                        except Exception:
                            continue
                if clicked:
                    break
            except Exception:
                continue

        if not clicked:
            return False

        try:
            WebDriverWait(self.driver, 3).until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            alert.accept()
        except Exception:
            pass

        return True

    def _handle_confirmation_dialogs(self):
        """Accepts any confirmation dialogs (Alerts or UI Modals) triggered by Ship action."""
        # 1. Native JS Alert confirmation
        try:
            WebDriverWait(self.driver, 3).until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            alert.accept()
            return
        except Exception:
            pass

        # 2. Modal dialog buttons (e.g., 'Confirm', 'Yes', 'OK', or modal 'Ship')
        modal_btn_locators = [
            "//div[contains(@class, 'modal') or contains(@class, 'dialog') or contains(@class, 'ui-dialog')]//button[contains(., 'OK') or contains(., 'Yes') or contains(., 'Confirm') or contains(., 'Ship')]",
            "//button[normalize-space()='Confirm'] | //button[normalize-space()='Yes'] | //button[normalize-space()='OK']",
        ]
        for xpath in modal_btn_locators:
            try:
                btns = self.driver.find_elements(By.XPATH, xpath)
                for b in btns:
                    if b.is_displayed():
                        self.driver.execute_script("arguments[0].click();", b)
                        return
            except Exception:
                continue


@pytest.fixture(scope="class")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    drv = webdriver.Chrome(options=options)
    drv.implicitly_wait(6)
    drv.set_page_load_timeout(40)
    drv.maximize_window()
    yield drv
    drv.quit()


def wait_ready(driver, timeout=20):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def js_click(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    time.sleep(0.3)
    try:
        element.click()
    except Exception:
        driver.execute_script("arguments[0].click();", element)


def take_screenshot(driver, name):
    screenshots_dir = os.path.join(os.path.dirname(__file__), "screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(screenshots_dir, f"{name}_{ts}.png")
    driver.save_screenshot(path)
    return path


def navigate_to_consol_ship_items(driver):
    driver.get(CONSOL_ITEMS_URL)
    wait_ready(driver)
    time.sleep(PAUSE)

    if "consolship" in driver.current_url.lower() or "supplieraction" in driver.current_url.lower():
        return True

    for locator in [
        (By.XPATH, "//a[contains(@href, 'Action/Home') or normalize-space(.)='Actions' or .//span[normalize-space()='Actions']]"),
        (By.XPATH, "//*[self::a or self::span][contains(normalize-space(.), 'Actions')]"),
    ]:
        try:
            actions_link = WebDriverWait(driver, 8).until(EC.element_to_be_clickable(locator))
            js_click(driver, actions_link)
            wait_ready(driver)
            time.sleep(PAUSE)
            break
        except Exception:
            continue

    for locator in [
        (By.XPATH, "//*[self::a or self::span][contains(normalize-space(.), 'Consol Ship')]"),
        (By.XPATH, "//*[self::a or self::span][contains(@href, 'ConsolShip')]"),
        (By.XPATH, "//*[contains(normalize-space(.), 'Consol Ship')]"),
    ]:
        try:
            action_link = WebDriverWait(driver, 8).until(EC.element_to_be_clickable(locator))
            js_click(driver, action_link)
            wait_ready(driver)
            time.sleep(PAUSE)
            if "consolship" in driver.current_url.lower() or "supplieraction" in driver.current_url.lower():
                return True
            break
        except Exception:
            continue

    if "consolship" not in driver.current_url.lower() and "supplieraction" not in driver.current_url.lower():
        driver.get(CONSOL_ITEMS_URL)
        wait_ready(driver)
        time.sleep(PAUSE)

    return "consolship" in driver.current_url.lower() or "supplieraction" in driver.current_url.lower()


def select_first_n_cards(driver, count=2):
    checkboxes = driver.find_elements(By.XPATH, "//table//tbody//tr//input[@type='checkbox']")
    if not checkboxes:
        checkboxes = driver.find_elements(By.XPATH, "//input[@type='checkbox' and not(ancestor::th)]")

    selected = 0
    for cb in checkboxes[:count]:
        if not cb.is_selected():
            js_click(driver, cb)
            selected += 1
    return selected


@pytest.mark.usefixtures("driver")
class TestSupplierConsolShip:

    def test_consol_ship_flow(self, driver):
        wait = WebDriverWait(driver, 15)
        page = ConsolShipPage(driver)

        # 1. Login
        driver.get(f"{BASE_URL}/Account/Login")
        wait_ready(driver)

        wait.until(EC.presence_of_element_located((By.ID, "UserName"))).send_keys(USERNAME)
        wait.until(EC.presence_of_element_located((By.ID, "Password"))).send_keys(PASSWORD)
        wait.until(EC.element_to_be_clickable((By.ID, "login-button"))).click()
        wait_ready(driver)
        take_screenshot(driver, "01_after_login")

        # 2. Navigate to Consol Ship Items
        assert navigate_to_consol_ship_items(driver), (
            f"Failed to navigate to Consol Ship Items. Current URL: {driver.current_url}"
        )
        take_screenshot(driver, "02_items_list")

        # 3. Open Cards List from Items
        item_link = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//table//tbody//tr[1]//a"))
        )
        js_click(driver, item_link)
        wait_ready(driver)

        try:
            show_btn = driver.find_element(By.XPATH, "//*[self::a or self::button][contains(normalize-space(), 'Show Cards')]")
            js_click(driver, show_btn)
            wait_ready(driver)
        except Exception:
            pass

        if "consolshipcards" not in driver.current_url.lower():
            driver.get(CONSOL_CARDS_URL)
            wait_ready(driver)

        time.sleep(PAUSE)
        take_screenshot(driver, "03_cards_page")

        # 4. Select cards
        selected_count = select_first_n_cards(driver, count=2)
        assert selected_count > 0, "No cards could be selected from the table."

        # 5. Click Ship (with confirmation handling)
        ship_clicked = page.click_ship_button()
        assert ship_clicked, "Failed to click Ship button."
        wait_ready(driver)
        time.sleep(PAUSE * 2)
        take_screenshot(driver, "04_after_ship")