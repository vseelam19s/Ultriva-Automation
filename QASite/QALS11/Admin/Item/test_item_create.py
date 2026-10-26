import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ── Config ──────────────────────────────────────────────────────────────
BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
USERNAME = "buyeruser"
PASSWORD = "Ultriva!23"
PAUSE = 2

# Global Field Constants
LANDING_TIME = "5"
PRICE_PER_UOM = "10"
USAGE_PER_DAY = "2"
SAFETY_STOCK = "1"
PALLET_QTY = "50"
SHIP_TOL = "100"
RECEIVE_TOL = "100"

# Supplier Constants
ITEM_COORD = "buyeruser"
SUPPLIER = "supnew"
SUPPLIER_USER = "supnewuser"
MIN_ORDER_QTY = "1"
LEAD_TIME = "3"
TRANSIT_TIME = "1"

# ── Helpers ─────────────────────────────────────────────────────────────

def page_loaded(driver):
    WebDriverWait(driver, 20).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

def scroll_to(driver, el):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'})", el)
    time.sleep(0.3)

def click(driver, by, loc, timeout=15):
    el = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, loc))
    )
    scroll_to(driver, el)
    el.click()

def fill(driver, field_id, value):
    """Scroll to input, clear it and type value. Falls back to JS if not interactable."""
    el = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.ID, field_id))
    )
    scroll_to(driver, el)
    try:
        el.clear()
        el.send_keys(str(value))
    except Exception:
        driver.execute_script("arguments[0].value = arguments[1]", el, str(value))

def autocomplete(driver, field_id, value):
    """Type into a jQuery UI autocomplete field and select the matching item."""
    el = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.ID, field_id))
    )
    scroll_to(driver, el)
    el.clear()
    el.send_keys(value)
    time.sleep(2)  # let autocomplete fire

    try:
        suggestion = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//ul[contains(@class,'ui-autocomplete') and @style[not(contains(.,'display: none'))]]"
                f"//li[contains(normalize-space(.),'{value}')]"
            ))
        )
        scroll_to(driver, suggestion)
        suggestion.click()
        time.sleep(1)
        return
    except Exception:
        pass

    # Fallback: DOWN arrow to highlight first item, ENTER to select
    el.send_keys(Keys.DOWN)
    time.sleep(0.5)
    el.send_keys(Keys.ENTER)
    time.sleep(1)

def run_verify_item_in_list(driver, item_no):
    """Shared assertion logic to verify an item table row in KanbanItem/List"""
    driver.get(f"{BASE_URL}/KanbanItem/List")
    page_loaded(driver)
    time.sleep(PAUSE)

    assert item_no in driver.page_source, (
        f"Item '{item_no}' NOT found in Items list page source — save may have failed."
    )

    item_cell = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((
            By.XPATH, f"//td[normalize-space(.)='{item_no}']"
        ))
    )

    parent_row = item_cell.find_element(By.XPATH, "..")
    all_tds = parent_row.find_elements(By.TAG_NAME, "td")

    start_idx = 0
    for i, td in enumerate(all_tds):
        if td.text.strip() == item_no:
            start_idx = i
            break

    item_cells = all_tds[start_idx: start_idx + 10]
    col_labels = [
        "Item No", "Description", "Price Per UOM", "Supplier",
        "Supplier Item No", "Lead Time", "Cards", "Status", "Category", "Other"
    ]

    print("\n" + "=" * 65)
    print(f"  CREATED ITEM — QALS1011 Items List ({item_no})")
    print("=" * 65)
    for i, cell in enumerate(item_cells):
        label = col_labels[i] if i < len(col_labels) else f"Col {i}"
        val = cell.text.strip()
        if val:
            print(f"  {label:<25} : {val}")
    print("=" * 65)
    print(f"  PASS — Item '{item_no}' found and verified in Items list")
    print("=" * 65)
    time.sleep(PAUSE)

# ── Item 1 Test Suite ───────────────────────────────────────────────────

class TestItemOneCreate:
    ITEM_NO = "IT010426"
    ITEM_DESC = "Test Item April 2026"
    SUPPLIER_ITEM_NO = "SUP-IT010426"
    SUPPLIER_DESC = "Test Supplier Item"

    def test_01_login(self, driver):
        driver.get(BASE_URL)
        page_loaded(driver)
        fill(driver, "UserName", USERNAME)
        fill(driver, "Password", PASSWORD)
        click(driver, By.ID, "login-button")
        page_loaded(driver)
        time.sleep(PAUSE)
        assert "ultrivalms" in driver.current_url
        print(f"\n  Logged in → {driver.current_url}")

    def test_02_open_admin(self, driver):
        click(driver, By.XPATH, "//a[contains(@href,'/Admin/Home') or normalize-space(.)='Admin']")
        page_loaded(driver)
        time.sleep(PAUSE)
        print(f"\n  Admin home → {driver.current_url}")

    def test_03_click_item_menu(self, driver):
        try:
            click(driver, By.XPATH, "//a[contains(@href,'KanbanItem') or normalize-space(.)='Item' or normalize-space(.)='Items']")
        except Exception:
            driver.get(f"{BASE_URL}/KanbanItem/List")
        page_loaded(driver)
        time.sleep(PAUSE)
        assert "ultrivalms" in driver.current_url
        print(f"\n  Items list → {driver.current_url}")

    def test_04_click_add(self, driver):
        try:
            click(driver, By.XPATH, "//a[normalize-space(.)='Add' or contains(@href,'KanbanItem/Create')]")
        except Exception:
            driver.get(f"{BASE_URL}/KanbanItem/Create")
        page_loaded(driver)
        time.sleep(PAUSE)
        assert "KanbanItem" in driver.current_url
        print(f"\n  New Item form → {driver.current_url}")

    def test_05_fill_base_information(self, driver):
        fill(driver, "ITM_ItemNo", self.ITEM_NO)
        fill(driver, "ITM_Description", self.ITEM_DESC)
        fill(driver, "MISC_PlantHandlingTime", LANDING_TIME)
        fill(driver, "ITM_PricePerUOM", PRICE_PER_UOM)
        autocomplete(driver, "MISC_BuyerUser", ITEM_COORD)
        fill(driver, "ITM_UsagePerDay", USAGE_PER_DAY)
        fill(driver, "ITM_SafetyStock", SAFETY_STOCK)
        fill(driver, "ITM_PalletQty", PALLET_QTY)
        fill(driver, "ITM_ShipQtyTol", SHIP_TOL)
        fill(driver, "ITM_ReceiveQtyTol", RECEIVE_TOL)
        time.sleep(PAUSE)
        print(f"\n  Base Information filled — Item No: {self.ITEM_NO}")

    def test_06_fill_supplier_tab(self, driver):
        click(driver, By.XPATH, "//div[contains(@class,'tab-control-item') and contains(.,'Supplier')] | //span[contains(@class,'tab-control-item-txt') and normalize-space(.)='Supplier']")
        time.sleep(PAUSE)

        autocomplete(driver, "MISC_Supplier", SUPPLIER)
        gid = driver.find_element(By.ID, "I2S_SupplierGID").get_attribute("value")
        assert gid, "Supplier GID not populated"
        time.sleep(1)

        fill(driver, "I2S_SupplierItemCode", self.SUPPLIER_ITEM_NO)
        fill(driver, "I2S_SupplierItemDesc", self.SUPPLIER_DESC)
        fill(driver, "I2S_MinOrderQty", MIN_ORDER_QTY)

        autocomplete(driver, "MISC_SupplierUser", SUPPLIER_USER)
        user_gid = driver.find_element(By.ID, "I2S_SupplierUserGID").get_attribute("value")
        assert user_gid, "Supplier User GID not populated"

        fill(driver, "MISC_LeadTime", LEAD_TIME)
        fill(driver, "MISC_TransitTime", TRANSIT_TIME)
        time.sleep(PAUSE)

    def test_07_save_item(self, driver):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)
        click(driver, By.ID, "entryPGSubmit")
        page_loaded(driver)
        time.sleep(3)
        assert ("KanbanItem/List" in driver.current_url or "KanbanItem/Edit" in driver.current_url or self.ITEM_NO in driver.page_source)

    def test_08_verify_item_in_list(self, driver):
        run_verify_item_in_list(driver, self.ITEM_NO)


# ── Item 2 Test Suite ───────────────────────────────────────────────────

class TestItemTwoCreate:
    ITEM_NO = "IT020426"
    ITEM_DESC = "Test Item 02 April 2026"
    SUPPLIER_ITEM_NO = "SUP-IT020426"
    SUPPLIER_DESC = "Test Supplier Item 02"

    def test_01_login(self, driver):
        driver.get(BASE_URL)
        page_loaded(driver)
        fill(driver, "UserName", USERNAME)
        fill(driver, "Password", PASSWORD)
        click(driver, By.ID, "login-button")
        page_loaded(driver)
        time.sleep(PAUSE)
        assert "ultrivalms" in driver.current_url

    def test_02_open_admin(self, driver):
        click(driver, By.XPATH, "//a[contains(@href,'/Admin/Home') or normalize-space(.)='Admin']")
        page_loaded(driver)
        time.sleep(PAUSE)

    def test_03_click_item_menu(self, driver):
        try:
            click(driver, By.XPATH, "//a[contains(@href,'KanbanItem') or normalize-space(.)='Item' or normalize-space(.)='Items']")
        except Exception:
            driver.get(f"{BASE_URL}/KanbanItem/List")
        page_loaded(driver)
        time.sleep(PAUSE)

    def test_04_click_add(self, driver):
        try:
            click(driver, By.XPATH, "//a[normalize-space(.)='Add' or contains(@href,'KanbanItem/Create')]")
        except Exception:
            driver.get(f"{BASE_URL}/KanbanItem/Create")
        page_loaded(driver)
        time.sleep(PAUSE)

    def test_05_fill_base_information(self, driver):
        fill(driver, "ITM_ItemNo", self.ITEM_NO)
        fill(driver, "ITM_Description", self.ITEM_DESC)
        fill(driver, "MISC_PlantHandlingTime", LANDING_TIME)
        fill(driver, "ITM_PricePerUOM", PRICE_PER_UOM)
        autocomplete(driver, "MISC_BuyerUser", ITEM_COORD)
        fill(driver, "ITM_UsagePerDay", USAGE_PER_DAY)
        fill(driver, "ITM_SafetyStock", SAFETY_STOCK)
        fill(driver, "ITM_PalletQty", PALLET_QTY)
        fill(driver, "ITM_ShipQtyTol", SHIP_TOL)
        fill(driver, "ITM_ReceiveQtyTol", RECEIVE_TOL)
        time.sleep(PAUSE)

    def test_06_fill_supplier_tab(self, driver):
        click(driver, By.XPATH, "//div[contains(@class,'tab-control-item') and contains(.,'Supplier')] | //span[contains(@class,'tab-control-item-txt') and normalize-space(.)='Supplier']")
        time.sleep(PAUSE)

        autocomplete(driver, "MISC_Supplier", SUPPLIER)
        gid = driver.find_element(By.ID, "I2S_SupplierGID").get_attribute("value")
        assert gid, "Supplier GID not populated"
        time.sleep(1)

        fill(driver, "I2S_SupplierItemCode", self.SUPPLIER_ITEM_NO)
        fill(driver, "I2S_SupplierItemDesc", self.SUPPLIER_DESC)
        fill(driver, "I2S_MinOrderQty", MIN_ORDER_QTY)

        autocomplete(driver, "MISC_SupplierUser", SUPPLIER_USER)
        user_gid = driver.find_element(By.ID, "I2S_SupplierUserGID").get_attribute("value")
        assert user_gid, "Supplier User GID not populated"

        fill(driver, "MISC_LeadTime", LEAD_TIME)
        fill(driver, "MISC_TransitTime", TRANSIT_TIME)
        time.sleep(PAUSE)

    def test_07_save_item(self, driver):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)
        click(driver, By.ID, "entryPGSubmit")
        page_loaded(driver)
        time.sleep(3)
        assert ("KanbanItem/List" in driver.current_url or "KanbanItem/Edit" in driver.current_url or "PageFlow/List" in driver.current_url or self.ITEM_NO in driver.page_source)

    def test_08_verify_item_in_list(self, driver):
        run_verify_item_in_list(driver, self.ITEM_NO)


# ── Item 3 Test Suite ───────────────────────────────────────────────────

class TestItemThreeCreate:
    ITEM_NO = "IT070426"
    ITEM_DESC = "Test Item 07 April 2026"
    SUPPLIER_ITEM_NO = "SUP-IT070426"
    SUPPLIER_DESC = "Test Supplier Item 07"

    def test_01_login(self, driver):
        driver.get(BASE_URL)
        page_loaded(driver)
        fill(driver, "UserName", USERNAME)
        fill(driver, "Password", PASSWORD)
        click(driver, By.ID, "login-button")
        page_loaded(driver)
        time.sleep(PAUSE)
        assert "ultrivalms" in driver.current_url

    def test_02_open_admin(self, driver):
        click(driver, By.XPATH, "//a[contains(@href,'/Admin/Home') or normalize-space(.)='Admin']")
        page_loaded(driver)
        time.sleep(PAUSE)

    def test_03_click_item_menu(self, driver):
        try:
            click(driver, By.XPATH, "//a[contains(@href,'KanbanItem') or normalize-space(.)='Item' or normalize-space(.)='Items']")
        except Exception:
            driver.get(f"{BASE_URL}/KanbanItem/List")
        page_loaded(driver)
        time.sleep(PAUSE)

    def test_04_click_add(self, driver):
        try:
            click(driver, By.XPATH, "//a[normalize-space(.)='Add' or contains(@href,'KanbanItem/Create')]")
        except Exception:
            driver.get(f"{BASE_URL}/KanbanItem/Create")
        page_loaded(driver)
        time.sleep(PAUSE)

    def test_05_fill_base_information(self, driver):
        fill(driver, "ITM_ItemNo", self.ITEM_NO)
        fill(driver, "ITM_Description", self.ITEM_DESC)
        fill(driver, "MISC_PlantHandlingTime", LANDING_TIME)
        fill(driver, "ITM_PricePerUOM", PRICE_PER_UOM)
        autocomplete(driver, "MISC_BuyerUser", ITEM_COORD)
        fill(driver, "ITM_UsagePerDay", USAGE_PER_DAY)
        fill(driver, "ITM_SafetyStock", SAFETY_STOCK)
        fill(driver, "ITM_PalletQty", PALLET_QTY)
        fill(driver, "ITM_ShipQtyTol", SHIP_TOL)
        fill(driver, "ITM_ReceiveQtyTol", RECEIVE_TOL)
        time.sleep(PAUSE)

    def test_06_fill_supplier_tab(self, driver):
        click(driver, By.XPATH, "//div[contains(@class,'tab-control-item') and contains(.,'Supplier')] | //span[contains(@class,'tab-control-item-txt') and normalize-space(.)='Supplier']")
        time.sleep(PAUSE)

        autocomplete(driver, "MISC_Supplier", SUPPLIER)
        gid = driver.find_element(By.ID, "I2S_SupplierGID").get_attribute("value")
        assert gid, "Supplier GID not populated"
        time.sleep(1)

        fill(driver, "I2S_SupplierItemCode", self.SUPPLIER_ITEM_NO)
        fill(driver, "I2S_SupplierItemDesc", self.SUPPLIER_DESC)
        fill(driver, "I2S_MinOrderQty", MIN_ORDER_QTY)

        autocomplete(driver, "MISC_SupplierUser", SUPPLIER_USER)
        user_gid = driver.find_element(By.ID, "I2S_SupplierUserGID").get_attribute("value")
        assert user_gid, "Supplier User GID not populated"

        fill(driver, "MISC_LeadTime", LEAD_TIME)
        fill(driver, "MISC_TransitTime", TRANSIT_TIME)
        time.sleep(PAUSE)

    def test_07_save_item(self, driver):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)
        click(driver, By.ID, "entryPGSubmit")
        page_loaded(driver)
        time.sleep(3)
        assert ("KanbanItem/List" in driver.current_url or "KanbanItem/Edit" in driver.current_url or "PageFlow/List" in driver.current_url or self.ITEM_NO in driver.page_source)

    def test_08_verify_item_in_list(self, driver):
        run_verify_item_in_list(driver, self.ITEM_NO)