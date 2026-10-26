"""
show_items_list.py
==================
Read item numbers from item_test_data.xlsx → derive common filter prefix →
open QA site → login → Items List → apply "Item Contains <prefix>" filter
using the native grid filter UI (id='drp' input + Go button) →
display results in terminal.  Browser stays open (detach=True).

Run:
    python show_items_list.py
"""

import os
import time
import sys
from collections import namedtuple
from openpyxl import load_workbook
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ── Config ─────────────────────────────────────────────────────────────────────
BASE_URL  = "https://engineering.ultrivalms.com/QALS1011"
USERNAME  = "buyeruser"
PASSWORD  = "Ultriva!23"
PAUSE     = 2

# Excel file — same path resolution as test_item_excel_driven.py
EXCEL_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "test_data", "item_test_data.xlsx")
)


# ── Excel loader ───────────────────────────────────────────────────────────────

def load_item_numbers():
    """Return list of Item_No strings from item_test_data.xlsx / ItemData sheet."""
    wb   = load_workbook(EXCEL_PATH, read_only=True, data_only=True)
    ws   = wb["ItemData"]
    rows = list(ws.iter_rows(values_only=True))
    wb.close()
    headers = [str(h).strip() for h in rows[0]]
    idx = headers.index("Item_No")
    return [str(r[idx]).strip() for r in rows[1:] if r[idx]]


def common_prefix(strings):
    """Return the longest common prefix shared by all strings in the list."""
    if not strings:
        return ""
    prefix = strings[0]
    for s in strings[1:]:
        while not s.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return ""
    return prefix


# ── Helpers ────────────────────────────────────────────────────────────────────

def wait_ready(driver):
    WebDriverWait(driver, 30).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def wait_overlay(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.ID, "fancy_overlay"))
        )
    except Exception:
        pass


def scroll_to(driver, el):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'})", el)
    time.sleep(0.2)


def fill_id(driver, field_id, value, timeout=15):
    el = WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((By.ID, field_id))
    )
    el.clear()
    el.send_keys(str(value))


def banner(title, char="═", width=90):
    bar = char * width
    print(f"\n{bar}")
    print(f"  {title}")
    print(bar)


def row_out(label, value, width=28):
    print(f"  {label:<{width}} : {value}")


# ── Filter application ─────────────────────────────────────────────────────────

def apply_item_filter(driver, filter_value):
    """
    Apply the 'Item Contains <filter_value>' filter using the native grid
    filter controls on the KanbanItem/List page.

    Discovered element IDs (from inspect_item_filter.py):
      - Filter value input : id='drp'  (name='Item_FilterTextbox')
      - Go button          : <a onclick='sr()'>Go</a>
    """
    wait_overlay(driver)
    time.sleep(PAUSE)

    # Find the filter value input (id='drp', name='Item_FilterTextbox')
    try:
        filter_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "drp"))
        )
    except Exception:
        # Fallback: find by name
        filter_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "Item_FilterTextbox"))
        )

    scroll_to(driver, filter_input)
    driver.execute_script("arguments[0].value = ''", filter_input)
    filter_input.send_keys(filter_value)
    time.sleep(0.5)

    # Click the Go button (onclick='sr()')
    try:
        go_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//a[normalize-space(.)='Go']"
            ))
        )
        scroll_to(driver, go_btn)
        driver.execute_script("arguments[0].click()", go_btn)
    except Exception:
        # Fallback: call sr() directly via JS
        driver.execute_script("if(typeof sr === 'function') sr();")

    wait_ready(driver)
    time.sleep(PAUSE)

    row_out("Filter method", "Item_FilterTextbox (id=drp) + Go")
    row_out("Filter value",  filter_value)
    row_out("Field",         "Item")
    row_out("Operator",      "Contains")
    row_out("Status",        "Applied")


# ── Row scraper ────────────────────────────────────────────────────────────────

def scrape_matching_rows(driver, filter_value):
    """
    Scrape all visible <td> cells that contain filter_value.
    Returns list of dicts keyed by column label.
    """
    col_labels = [
        "Item No", "Description", "Standard Qty", "Default Supplier",
        "Commodity Code", "ABC Code", "No. of Cards", "Status",
    ]

    time.sleep(2)   # let AJAX grid render after filter

    cells_found = driver.find_elements(
        By.XPATH,
        f"//td[starts-with(normalize-space(.),'{filter_value}')]"
    )

    found_items = []
    seen = set()

    for cell in cells_found:
        cell_text = cell.text.strip()
        # Only process cells where text actually starts with the filter prefix
        if cell_text in seen or not cell_text.startswith(filter_value):
            continue
        seen.add(cell_text)
        try:
            parent_row = cell.find_element(By.XPATH, "..")
            all_tds    = parent_row.find_elements(By.TAG_NAME, "td")
            start = next(
                (i for i, td in enumerate(all_tds) if td.text.strip() == cell_text),
                0,
            )
            row_cells = all_tds[start: start + len(col_labels)]
            found_items.append({
                col_labels[i] if i < len(col_labels) else f"Col {i}": td.text.strip()
                for i, td in enumerate(row_cells)
            })
        except Exception:
            pass

    return found_items


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    # ── Load Excel → derive filter ─────────────────────────────────────────
    banner("STEP 1 — Read Excel Items")
    assert os.path.isfile(EXCEL_PATH), f"Excel file not found: {EXCEL_PATH}"
    item_numbers = load_item_numbers()
    assert item_numbers, "No item numbers found in Excel"

    row_out("Excel file",   EXCEL_PATH)
    row_out("Items loaded", len(item_numbers))
    for i, n in enumerate(item_numbers, 1):
        print(f"    {i}. {n}")

    # Derive common filter prefix (e.g. 'IT130426' from IT130426-Kan, IT130426_1_FS, IT130426-Virt)
    filter_value = common_prefix(item_numbers).rstrip("-_").strip()
    assert filter_value, "Cannot derive a common filter prefix from the Excel item numbers"
    row_out("Filter prefix", filter_value)

    # ── Launch Chrome (stays open after script) ────────────────────────────
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_experimental_option("detach", True)   # ← keeps browser open

    print("\n  Launching Chrome browser ...")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)

    try:
        # ── Step 2: Login ───────────────────────────────────────────────────
        banner("STEP 2 — Login")
        driver.get(BASE_URL)
        wait_ready(driver)

        fill_id(driver, "UserName", USERNAME)
        fill_id(driver, "Password", PASSWORD)
        el = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.ID, "login-button"))
        )
        driver.execute_script("arguments[0].click()", el)
        wait_ready(driver)
        time.sleep(PAUSE)

        assert "ultrivalms" in driver.current_url, \
            f"Login failed — URL: {driver.current_url}"
        row_out("Status", "Logged in")
        row_out("User",   USERNAME)
        row_out("URL",    driver.current_url)

        # ── Step 3: Navigate to Items List ──────────────────────────────────
        banner("STEP 3 — Navigate to Items List")
        driver.get(f"{BASE_URL}/KanbanItem/List")
        wait_ready(driver)
        time.sleep(PAUSE)
        row_out("Items List URL", driver.current_url)

        # ── Step 4: Apply filter ────────────────────────────────────────────
        banner(f"STEP 4 — Apply Filter: Item Contains '{filter_value}'")
        apply_item_filter(driver, filter_value)

        # ── Step 5: Scrape and display results ──────────────────────────────
        banner("STEP 5 — Items List Result")

        found_items = scrape_matching_rows(driver, filter_value)

        if not found_items:
            print(f"  No items matching '{filter_value}' visible in grid.")
            print("  Check the browser window — the filter may still be loading.")
        else:
            col_w = 22
            hdrs  = ["Item No", "Description", "Default Supplier", "No. of Cards", "Status"]
            print(f"\n  Filter   : Item Contains '{filter_value}'")
            print(f"  Matched  : {len(found_items)} item(s)")
            print(f"  URL      : {driver.current_url}")
            print()
            print("  " + "  ".join(f"{h:<{col_w}}" for h in hdrs))
            print("  " + "  ".join("-" * col_w for _ in hdrs))
            for i, item in enumerate(found_items, 1):
                vals = [(item.get(h) or "")[:col_w-1] for h in hdrs]
                print(f"  [{i:>2}] " + "  ".join(f"{v:<{col_w}}" for v in vals))

            # Detail view
            banner(f"DETAIL VIEW — {len(found_items)} Item(s)", char="─", width=90)
            for i, item in enumerate(found_items, 1):
                print(f"\n  [{i}]  {item.get('Item No', '?')}")
                print("  " + "-" * 55)
                for lbl, val in item.items():
                    if val:
                        row_out(lbl, val, width=22)

        banner("DONE — Browser open at Items List with filter applied", char="═", width=90)
        row_out("URL",    driver.current_url)
        row_out("Filter", f"Item Contains '{filter_value}'")
        print("  The browser will stay open. Close it manually when done.")
        print()

    except AssertionError as ex:
        print(f"\n  ERROR: {ex}", file=sys.stderr)

    except Exception as ex:
        print(f"\n  UNEXPECTED ERROR: {ex}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)


if __name__ == "__main__":
    main()
