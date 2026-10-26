import os
import time
import pytest
from collections import namedtuple
from openpyxl import load_workbook
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ══════════════════════════════════════════════════════════════════════════════
#  EXCEL DATA LOADER
# ══════════════════════════════════════════════════════════════════════════════

# Resolve from this file's location:
#   tests/QALS11/Admin/Item → 4 levels up → qa_automation/
EXCEL_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..", "..", "..", "..",   # → qa_automation/
        "test_data",
        "item_test_data.xlsx",
    )
)


def load_item_data(run_adjust_only: bool = False):
    """
    Read ItemData sheet from the Excel file.

    Parameters
    ----------
    run_adjust_only : bool
        If True, return only rows where Run_Adjust_Loop == 'Yes'.

    Returns
    -------
    list[namedtuple]
        One entry per data row (header is row 1, data starts at row 2).
    """
    wb = load_workbook(EXCEL_PATH, read_only=True, data_only=True)
    ws = wb["ItemData"]
    rows = list(ws.iter_rows(values_only=True))
    wb.close()

    if len(rows) < 2:
        raise ValueError(f"No data rows found in '{EXCEL_PATH}'")

    # Build namedtuple type from header
    raw_headers = [
        str(h).strip().replace(" ", "_").replace("/", "_")
        for h in rows[0]
    ]
    ItemRow = namedtuple("ItemRow", raw_headers)
    data = [ItemRow(*r) for r in rows[1:] if r[0]]   # skip blank rows

    if run_adjust_only:
        data = [r for r in data if str(r.Run_Adjust_Loop).strip().lower() == "yes"]

    return data

# ══════════════════════════════════════════════════════════════════════════════
#  CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════

BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
USERNAME = "buyeruser"
PASSWORD = "Ultriva!23"
PAUSE = 2

# ══════════════════════════════════════════════════════════════════════════════
#  SHARED HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def wait_ready(driver):
    """Block until document.readyState == 'complete'."""
    WebDriverWait(driver, 30).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def wait_overlay(driver):
    """Wait for any fancybox/loading overlay to disappear."""
    try:
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.ID, "fancy_overlay"))
        )
    except Exception:
        pass


def scroll_to(driver, el):
    """Scroll element to viewport centre."""
    driver.execute_script("arguments[0].scrollIntoView({block:'center'})", el)
    time.sleep(0.3)


def click(driver, by, loc, timeout=15):
    """Wait for element to be clickable and click it."""
    wait_overlay(driver)
    el = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, loc))
    )
    scroll_to(driver, el)
    try:
        el.click()
    except Exception:
        driver.execute_script("arguments[0].click()", el)
    time.sleep(0.5)


def js_click(driver, by, loc, timeout=15):
    """Force-click via JavaScript."""
    wait_overlay(driver)
    el = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, loc))
    )
    scroll_to(driver, el)
    driver.execute_script("arguments[0].click()", el)
    time.sleep(0.5)


def fill(driver, field_id, value):
    """Clear an input (by ID) and type a value; falls back to JS if needed."""
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
    """
    Type into a jQuery UI autocomplete field and select the suggestion.
    """
    el = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.ID, field_id))
    )
    scroll_to(driver, el)
    el.clear()
    el.send_keys(str(value))
    time.sleep(2)
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
    el.send_keys(Keys.DOWN)
    time.sleep(0.5)
    el.send_keys(Keys.ENTER)
    time.sleep(1)


def select_category(driver, category):
    """Select item category (Kanban / Forecast / Virtual) from the Category dropdown."""
    cat = str(category).strip()
    if not cat:
        return
    try:
        from selenium.webdriver.support.ui import Select as SeleniumSelect
        sel_el = WebDriverWait(driver, 8).until(
            EC.presence_of_element_located((By.ID, "ITM_CategoryCode"))
        )
        scroll_to(driver, sel_el)
        sel = SeleniumSelect(sel_el)
        try:
            sel.select_by_visible_text(cat)
        except Exception:
            sel.select_by_value(cat.upper())
        time.sleep(0.5)
        return
    except Exception:
        pass

    try:
        click(driver, By.XPATH, "//*[contains(@id,'CategoryCode') or contains(@id,'category') or contains(@id,'Category')]")
        time.sleep(0.5)
        click(driver, By.XPATH, f"//li[normalize-space(.)='{cat}'] | //option[normalize-space(.)='{cat}'] | //a[normalize-space(.)='{cat}']")
    except Exception:
        pass

# ── UI result display helpers ────────────────────────────────────────────────

def banner(title, char="═", width=70):
    bar = char * width
    print(f"\n{bar}")
    print(f"  {title}")
    print(bar)


def row_out(label, value, width=28):
    print(f"  {label:<{width}} : {value}")


def show_excel_summary(items):
    """Print a summary of what was loaded from Excel."""
    banner("EXCEL DATA — Items to Create")
    print(f"  {'#':<4} {'Item No':<20} {'Category':<12} {'Description'}")
    print(f"  {'-' * 4} {'-' * 20} {'-' * 12} {'-' * 35}")
    for i, item in enumerate(items, 1):
        print(f"  {i:<4} {item.Item_No:<20} {item.Category:<12} {item.Description}")
    banner("END SUMMARY", char="─")

# ══════════════════════════════════════════════════════════════════════════════
#  SHARED NAVIGATION STEPS
# ══════════════════════════════════════════════════════════════════════════════

def nav_login(driver):
    driver.get(BASE_URL)
    wait_ready(driver)
    fill(driver, "UserName", USERNAME)
    fill(driver, "Password", PASSWORD)
    click(driver, By.ID, "login-button")
    wait_ready(driver)
    time.sleep(PAUSE)
    assert "ultrivalms" in driver.current_url, f"Login failed — URL: {driver.current_url}"
    print(f"\n  Logged in as '{USERNAME}' → {driver.current_url}")


def nav_open_admin(driver):
    click(driver, By.XPATH, "//a[contains(@href,'/Admin/Home') or normalize-space(.)='Admin']")
    wait_ready(driver)
    time.sleep(PAUSE)
    print(f"  Admin module → {driver.current_url}")


def nav_open_item_list(driver):
    try:
        click(driver, By.XPATH, "//a[contains(@href,'KanbanItem') or normalize-space(.)='Item' or normalize-space(.)='Items']")
    except Exception:
        driver.get(f"{BASE_URL}/KanbanItem/List")
    wait_ready(driver)
    time.sleep(PAUSE)
    print(f"  Items list → {driver.current_url}")


def nav_click_add(driver):
    try:
        click(driver, By.XPATH, "//a[normalize-space(.)='Add' or contains(@href,'KanbanItem/Create')]")
    except Exception:
        driver.get(f"{BASE_URL}/KanbanItem/Create")
    wait_ready(driver)
    time.sleep(PAUSE)
    assert "KanbanItem" in driver.current_url, f"New Item form not reached — URL: {driver.current_url}"
    print(f"  New Item form → {driver.current_url}")

# ══════════════════════════════════════════════════════════════════════════════
#  ITEM CREATE / VERIFY ACTIONS
# ══════════════════════════════════════════════════════════════════════════════

def create_item_from_row(driver, item):
    """Fill the New Item form (Base Information + Supplier tab) from one Excel row and click Save."""
    banner(f"Creating Item: {item.Item_No}  [{item.Category}]")
    row_out("Description", item.Description)
    row_out("Coordinator", item.Item_Coord)
    row_out("Supplier", item.Supplier)
    row_out("Lead Time", item.Lead_Time)

    # ── Base Information tab ────────────────────────────────────────────────
    fill(driver, "ITM_ItemNo", item.Item_No)
    fill(driver, "ITM_Description", item.Description)
    fill(driver, "MISC_PlantHandlingTime", item.Landing_Time)
    fill(driver, "ITM_PricePerUOM", item.Price_Per_UOM)
    autocomplete(driver, "MISC_BuyerUser", item.Item_Coord)
    select_category(driver, item.Category)
    fill(driver, "ITM_UsagePerDay", item.Usage_Per_Day)
    fill(driver, "ITM_SafetyStock", item.Safety_Stock)
    fill(driver, "ITM_PalletQty", item.Pallet_Qty)
    fill(driver, "ITM_ShipQtyTol", item.Ship_Tol)
    fill(driver, "ITM_ReceiveQtyTol", item.Receive_Tol)
    time.sleep(PAUSE)
    print(f"  Base Information tab filled")

    # ── Supplier tab ────────────────────────────────────────────────────────
    click(driver, By.XPATH, "//div[contains(@class,'tab-control-item') and contains(.,'Supplier')] | //span[contains(@class,'tab-control-item-txt') and normalize-space(.)='Supplier']")
    time.sleep(PAUSE)
    autocomplete(driver, "MISC_Supplier", item.Supplier)
    supplier_gid = driver.find_element(By.ID, "I2S_SupplierGID").get_attribute("value")
    assert supplier_gid, f"Supplier GID not populated for item '{item.Item_No}'"

    fill(driver, "I2S_SupplierItemCode", item.Supplier_Item_No)
    fill(driver, "I2S_SupplierItemDesc", item.Supplier_Desc)
    fill(driver, "I2S_MinOrderQty", item.Min_Order_Qty)
    autocomplete(driver, "MISC_SupplierUser", item.Supplier_User)
    user_gid = driver.find_element(By.ID, "I2S_SupplierUserGID").get_attribute("value")
    assert user_gid, f"Supplier User GID not populated for item '{item.Item_No}'"

    fill(driver, "MISC_LeadTime", item.Lead_Time)
    fill(driver, "MISC_TransitTime", item.Transit_Time)
    time.sleep(PAUSE)
    print(f"  Supplier tab filled — GID:{supplier_gid}  UserGID:{user_gid}")

    # ── Save ────────────────────────────────────────────────────────────────
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(1)
    click(driver, By.ID, "entryPGSubmit")
    wait_ready(driver)
    time.sleep(3)
    url = driver.current_url
    src = driver.page_source
    saved = (
        "KanbanItem/List" in url
        or "KanbanItem/Edit" in url
        or "PageFlow/List" in url
        or item.Item_No in src
    )
    assert saved, f"Save may have failed for '{item.Item_No}' — URL: {url}"
    print(f"  Saved → {url}")


def verify_item_in_list(driver, item_no):
    """Navigate to Items list and print the row for item_no."""
    driver.get(f"{BASE_URL}/KanbanItem/List")
    wait_ready(driver)
    time.sleep(PAUSE)
    assert item_no in driver.page_source, f"Item '{item_no}' NOT found in Items list — save may have failed."
    item_cell = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, f"//td[normalize-space(.)='{item_no}']"))
    )
    all_tds = item_cell.find_element(By.XPATH, "..").find_elements(By.TAG_NAME, "td")
    start = next((i for i, td in enumerate(all_tds) if td.text.strip() == item_no), 0)
    cells = all_tds[start: start + 10]

    col_labels = [
        "Item No", "Description", "Price Per UOM", "Supplier",
        "Supplier Item No", "Lead Time", "Cards", "Status", "Category", "Other"
    ]

    banner(f"VERIFIED IN LIST — {item_no}")
    for i, cell in enumerate(cells):
        val = cell.text.strip()
        if val:
            row_out(col_labels[i] if i < len(col_labels) else f"Col {i}", val)
    print(f"\n  PASS — '{item_no}' confirmed in Items list")
    banner("END", char="─")

# ══════════════════════════════════════════════════════════════════════════════
#  LOOP SIZE HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def select_item_row(driver, item_no):
    wait_overlay(driver)
    row = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, f"//td[normalize-space(.)='{item_no}'] | //a[normalize-space(.)='{item_no}']"))
    )
    scroll_to(driver, row)
    driver.execute_script("arguments[0].click()", row)
    time.sleep(PAUSE)
    print(f"  Row selected: {item_no}")


def open_cards_list(driver):
    wait_overlay(driver)
    try:
        el = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "Item_tbrCards")))
    except Exception:
        el = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[normalize-space(.)='Cards'] | //button[normalize-space(.)='Cards']")))
    scroll_to(driver, el)
    wait_overlay(driver)
    driver.execute_script("arguments[0].click()", el)
    wait_ready(driver)
    time.sleep(PAUSE)
    print(f"  Cards list → {driver.current_url}")


def open_initial_loop_wizard_if_needed(driver):
    """Runs Initial Loop Size wizard if the item is newly created (0 cards)."""
    wait_overlay(driver)
    time.sleep(PAUSE)
    add_cards_btns = driver.find_elements(By.XPATH, "//*[@title='Add Cards']")
    if not add_cards_btns:
        return False   # item already has cards
    
    print(f"  New item detected (0 cards) — running Initial Loop Size wizard first")
    el = add_cards_btns[0]
    scroll_to(driver, el)
    driver.execute_script("arguments[0].click()", el)
    wait_ready(driver)
    time.sleep(PAUSE)
    
    try:
        uoh = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "WIZARD_UnitsOnHand")))
        scroll_to(driver, uoh)
        uoh.clear()
        uoh.send_keys("0")
    except Exception:
        pass
    try:
        uoo = driver.find_element(By.ID, "WIZARD_UnitsOnOrder")
        uoo.clear()
        uoo.send_keys("0")
    except Exception:
        pass
    time.sleep(0.5)

    js_click(driver, By.XPATH, "//*[@id='wizNextBtn' or @title='Next']")
    wait_ready(driver)
    time.sleep(PAUSE)

    for _ in range(10):
        fin = driver.find_elements(By.XPATH, "//*[@id='wizFinishBtn' or @title='Finish' or @title='Done' or (self::button and normalize-space(.)='Finish')]")
        if fin:
            driver.execute_script("arguments[0].click()", fin[0])
            wait_ready(driver)
            time.sleep(PAUSE)
            break
        nxt = driver.find_elements(By.XPATH, "//*[@id='wizNextBtn' or @title='Next']")
        if nxt:
            driver.execute_script("arguments[0].click()", nxt[0])
            wait_ready(driver)
            time.sleep(PAUSE)
        else:
            break
    return True


def open_adjust_wizard(driver):
    card_list_url = driver.current_url
    ran_initial = open_initial_loop_wizard_if_needed(driver)
    if ran_initial:
        driver.get(card_list_url)
        wait_ready(driver)
        time.sleep(PAUSE)
    wait_overlay(driver)
    el = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "ItemCard_tbrAdd")))
    scroll_to(driver, el)
    driver.execute_script("arguments[0].click()", el)
    wait_ready(driver)
    time.sleep(PAUSE)
    assert "EboLoopsizeWizard" in driver.current_url, f"Adjust LoopSize wizard not reached — URL: {driver.current_url}"
    print(f"  Adjust LoopSize wizard → {driver.current_url}")


def wizard_select_add_replenishment(driver):
    radio = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "WIZARD$CardOperation1")))
    driver.execute_script("arguments[0].click()", radio)
    time.sleep(0.5)
    assert radio.is_selected(), "'Add Replenishment Cards' radio not selected"
    js_click(driver, By.ID, "wizNextBtn")
    wait_ready(driver)
    time.sleep(PAUSE)
    print(f"  'Add Replenishment Cards' selected → step 2")


def wizard_enter_cards_finish(driver, cards_to_add):
    el = WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.ID, "WIZARD_RCardsToAdd")))
    scroll_to(driver, el)
    driver.execute_script("arguments[0].removeAttribute('readonly')", el)
    driver.execute_script(f"arguments[0].value = '{cards_to_add}'", el)
    el.send_keys(" \b")   # trigger change event
    time.sleep(0.5)

    release_radio = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "WIZARD$LoopsizeAction1")))
    driver.execute_script("arguments[0].click()", release_radio)
    time.sleep(0.5)
    assert release_radio.is_selected(), "'Release to Supplier' radio not selected"
    row_out("Cards to Add", cards_to_add)
    row_out("Action", "Release to Supplier")

    finish = driver.find_elements(By.ID, "wizFinishBtn")
    if finish:
        driver.execute_script("arguments[0].click()", finish[0])
    else:
        js_click(driver, By.ID, "wizNextBtn")
    wait_ready(driver)
    time.sleep(PAUSE)

    for _ in range(5):
        fin = driver.find_elements(By.ID, "wizFinishBtn")
        if fin:
            driver.execute_script("arguments[0].click()", fin[0])
            wait_ready(driver)
            time.sleep(PAUSE)
            print(f"  Finish clicked → {driver.current_url}")
            break
        nxt = driver.find_elements(By.ID, "wizNextBtn")
        if nxt:
            driver.execute_script("arguments[0].click()", nxt[0])
            wait_ready(driver)
            time.sleep(PAUSE)
        else:
            break

# ══════════════════════════════════════════════════════════════════════════════
#  TEST CLASS 1 — Excel-Driven Item Creation
# ══════════════════════════════════════════════════════════════════════════════

class TestItemExcelCreate:
    def test_01_load_excel_data(self, driver):
        """Verify the Excel file exists and print its contents to the terminal."""
        assert os.path.isfile(EXCEL_PATH), f"Excel file not found: {EXCEL_PATH}"
        items = load_item_data()
        assert len(items) > 0, "No data rows found in Excel file"
        show_excel_summary(items)
        banner("EXCEL FILE INFO")
        row_out("Path", EXCEL_PATH)
        row_out("Rows", len(items))
        banner("END", char="─")
        print(f"\n  PASS — Excel loaded: {len(items)} item(s) found")

    def test_02_login(self, driver):
        nav_login(driver)

    def test_03_create_items_from_excel(self, driver):
        """Iterate every row in the Excel sheet and create items."""
        items = load_item_data()
        results = []

        for item in items:
            try:
                nav_open_admin(driver)
                nav_open_item_list(driver)
                nav_click_add(driver)
                create_item_from_row(driver, item)
                results.append((item.Item_No, item.Category, "PASS", driver.current_url))
            except Exception as exc:
                results.append((item.Item_No, item.Category, "FAIL", str(exc)))
                # Log execution table details before exiting out via raise exception block
                raise

        banner("CREATE ITEMS — FINAL RESULTS")
        print(f"  {'#':<4} {'Item No':<20} {'Category':<12} {'Status':<8} {'Details'}")
        print(f"  {'-' * 4} {'-' * 20} {'-' * 12} {'-' * 8} {'-' * 35}")
        for i, (item_no, cat, status, detail) in enumerate(results, 1):
            short = detail[-50:] if len(detail) > 50 else detail
            print(f"  {i:<4} {item_no:<20} {cat:<12} {status:<8} {short}")
        banner("END", char="─")

    def test_04_verify_all_items_in_list(self, driver):
        """Navigate to Items list and verify each item number appears."""
        items = load_item_data()
        banner("VERIFYING ITEMS IN LIST")
        for item in items:
            verify_item_in_list(driver, item.Item_No)
        banner("ALL ITEMS VERIFIED")
        print(f"  PASS — {len(items)} item(s) confirmed in Items list")

# ══════════════════════════════════════════════════════════════════════════════
#  TEST CLASS 2 — Adjust Loop Size for Kanban items (from Excel)
# ══════════════════════════════════════════════════════════════════════════════

class TestAdjustLoopExcel:
    def test_01_load_kanban_items(self, driver):
        """Print which items will have loop size adjusted."""
        kanban_items = load_item_data(run_adjust_only=True)
        assert kanban_items, "No rows with Run_Adjust_Loop='Yes' found in Excel"
        banner("ADJUST LOOP SIZE — Kanban Items (from Excel)")
        print(f"  {'#':<4} {'Item No':<20} {'Category':<12} {'Cards_To_Add'}")
        print(f"  {'-' * 4} {'-' * 20} {'-' * 12} {'-' * 14}")
        for i, item in enumerate(kanban_items, 1):
            print(f"  {i:<4} {item.Item_No:<20} {item.Category:<12} {item.Cards_To_Add}")
        banner("END", char="─")

    def test_02_login(self, driver):
        nav_login(driver)

    def test_03_adjust_loop_size_all_kanban(self, driver):
        """For every row where Run_Adjust_Loop == 'Yes', run the loop wizard."""
        kanban_items = load_item_data(run_adjust_only=True)
        results = []

        for item in kanban_items:
            try:
                banner(f"Adjust Loop Size: {item.Item_No}  [{item.Category}]")
                row_out("Cards to Add", item.Cards_To_Add)
                nav_open_admin(driver)
                nav_open_item_list(driver)
                select_item_row(driver, item.Item_No)
                open_cards_list(driver)
                open_adjust_wizard(driver)
                wizard_select_add_replenishment(driver)
                wizard_enter_cards_finish(driver, item.Cards_To_Add)
                assert "ultrivalms" in driver.current_url
                results.append((item.Item_No, item.Category, item.Cards_To_Add, "PASS"))
            except Exception as exc:
                results.append((item.Item_No, item.Category, item.Cards_To_Add, f"FAIL: {exc}"))
                raise

        banner("ADJUST LOOP SIZE — FINAL RESULTS")
        print(f"  {'#':<4} {'Item No':<20} {'Category':<12} {'Cards':<8} {'Status'}")
        print(f"  {'-' * 4} {'-' * 20} {'-' * 12} {'-' * 8} {'-' * 8}")
        for i, (item_no, cat, cards, status) in enumerate(results, 1):
            print(f"  {i:<4} {item_no:<20} {cat:<12} {cards:<8} {status}")
        banner("DONE", char="═")