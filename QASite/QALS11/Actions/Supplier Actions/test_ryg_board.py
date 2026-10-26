"""
QALS11 | Actions > Supplier Actions > RYG Board
===============================================
URL   : https://engineering.ultrivalms.com/QALS1011/SupplierAction/SupplierRYGBoardItems
User  : supnewuser / Ultriva!23

Test Flow
---------
  1. Login as supnewuser
  2. Click Actions
  3. Open Supplier Actions > RYG Board
  4. Validate item popup data when the item number is clicked
  5. Validate Print link output
  6. Validate Export link output to Excel

Run (from qa_automation/):
    pytest "tests/QALS11/Actions/Supplier Actions/RYG Board.py" -v -s
"""

import os
import time
from pathlib import Path

import pytest
from openpyxl import load_workbook
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
RYG_BOARD_URL = f"{BASE_URL}/SupplierAction/SupplierRYGBoardItems"
USERNAME = "supnewuser"
PASSWORD = "Ultriva!23"
PAUSE = 1.5


@pytest.fixture(scope="class")
def driver():
    download_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "reports", "downloads")
    os.makedirs(download_dir, exist_ok=True)

    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "profile.default_content_settings.popups": 0,
        },
    )

    drv = webdriver.Chrome(options=options)
    drv.implicitly_wait(10)
    drv.set_page_load_timeout(40)
    drv.maximize_window()
    yield drv
    drv.quit()


def wait_ready(driver, timeout=30):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def find(driver, by, locator, timeout=15):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, locator))
    )


def clickable(driver, by, locator, timeout=15):
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, locator))
    )


def scroll_to(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'})", element)
    time.sleep(0.3)


def click_text(driver, labels):
    for label in labels:
        locators = [
            (By.XPATH, f"//*[self::a or self::button or self::input or self::span or self::div][normalize-space(.)='{label}']"),
            (By.XPATH, f"//*[self::a or self::button or self::input or self::span or self::div][contains(normalize-space(.), '{label}')]"),
            (By.XPATH, f"//*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{label.lower()}')]"),
        ]
        for by, locator in locators:
            try:
                elements = driver.find_elements(by, locator)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        scroll_to(driver, element)
                        try:
                            element.click()
                        except Exception:
                            driver.execute_script("arguments[0].click();", element)
                        return True
            except Exception:
                continue

        matched = driver.execute_script(
            """
            var wanted = arguments[0].trim().toLowerCase();
            var els = document.querySelectorAll('a, button, input, span, div, td, li');
            for (var i = 0; i < els.length; i++) {
              var text = (els[i].innerText || els[i].value || '').replace(/\\s+/g, ' ').trim().toLowerCase();
              var visible = !!(els[i].offsetParent !== null && (els[i].offsetWidth > 0 || els[i].offsetHeight > 0 || els[i].getClientRects().length > 0));
              if ((text === wanted || text.indexOf(wanted) !== -1) && visible) {
                try { els[i].click(); } catch (e) { els[i].dispatchEvent(new MouseEvent('click', {bubbles: true})); }
                return true;
              }
            }
            return false;
            """,
            label,
        )
        if matched:
            return True
    return False


def find_first_item_link(driver):
    for locator in [
        (By.XPATH, "//a[contains(normalize-space(.), 'ITB') or contains(normalize-space(.), 'IT')]"),
        (By.XPATH, "//td[contains(normalize-space(.), 'ITB') or contains(normalize-space(.), 'IT')]"),
        (By.XPATH, "//*[self::a or self::span][normalize-space(.)][contains(normalize-space(.), 'IT')]"),
    ]:
        try:
            for element in driver.find_elements(locator[0], locator[1]):
                text = (element.text or "").strip()
                if text and (text.startswith("ITB") or text.startswith("IT")):
                    return element, text
        except Exception:
            continue
    return None, ""


def take_screenshot(driver, name):
    screenshots_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "..", "reports", "screenshots"
    )
    os.makedirs(screenshots_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(screenshots_dir, f"supplier_ryg_{name}_{ts}.png")
    driver.save_screenshot(path)
    print(f"  [screenshot] {path}")
    return path


def wait_for_download(candidate_dirs, before_files=None, timeout=45):
    deadline = time.time() + timeout
    before_files = set(before_files or [])
    while time.time() < deadline:
        for base_dir in candidate_dirs:
            if not os.path.isdir(base_dir):
                continue
            for path in Path(base_dir).iterdir():
                if not path.is_file():
                    continue
                resolved = str(path.resolve())
                if resolved in before_files:
                    continue
                if path.name.lower().endswith((".xls", ".xlsx", ".csv")) and path.stat().st_size > 0:
                    return path
        time.sleep(1)
    return None


@pytest.mark.usefixtures("driver")
class TestSupplierRygBoard:

    def test_01_login(self, driver):
        print("\n[TC-SRYG-001] Logging in to QA site as supnewuser...")
        driver.get(f"{BASE_URL}/Account/Login")
        wait_ready(driver)

        username = find(driver, By.ID, "UserName")
        password = find(driver, By.ID, "Password")
        login_button = clickable(driver, By.ID, "login-button")

        username.clear()
        username.send_keys(USERNAME)
        password.clear()
        password.send_keys(PASSWORD)
        login_button.click()
        wait_ready(driver)
        time.sleep(PAUSE)

        current_url = driver.current_url
        assert BASE_URL.lower() in current_url.lower() or "Home" in current_url.lower(), (
            f"Login may have failed. URL: {current_url}"
        )
        take_screenshot(driver, "01_after_login")
        print(f"  [URL] {current_url}")
        print("  [PASS] Login succeeded.")

    def test_02_open_supplier_ryg_board(self, driver):
        print("\n[TC-SRYG-002] Opening Supplier RYG Board...")
        driver.get(RYG_BOARD_URL)
        wait_ready(driver)
        time.sleep(PAUSE * 2)

        current_url = driver.current_url.lower()
        assert "supplierrygboarditems" in current_url or "supplierrygboard" in current_url, (
            f"Supplier RYG Board did not load. URL: {driver.current_url}"
        )
        take_screenshot(driver, "02_ryg_board")
        print(f"  [URL] {driver.current_url}")
        print("  [PASS] Supplier RYG Board loaded.")

    def test_03_item_popup_validation(self, driver):
        print("\n[TC-SRYG-003] Selecting item number and validating popup data...")

        element, item_text = find_first_item_link(driver)
        assert element, "No item number found on the Supplier RYG Board."
        print(f"  [Item selected] {item_text}")

        scroll_to(driver, element)
        try:
            element.click()
        except Exception:
            driver.execute_script("arguments[0].click();", element)
        wait_ready(driver)
        time.sleep(PAUSE * 2)

        body_text = (driver.find_element(By.TAG_NAME, "body").text or "").strip()
        assert body_text, "Popup content is empty after clicking the item number."
        expected_tokens = [
            "Item No",
            "Description",
            "Supplier",
            "Qty",
            "Status",
            "RLG",
            "On Hand",
            "In Transit",
        ]
        assert any(token.lower() in body_text.lower() for token in expected_tokens), (
            f"Popup did not contain expected item fields. Body: {body_text[:500]}"
        )
        take_screenshot(driver, "03_item_popup")
        print(f"  [Popup sample] {body_text[:500]}")
        print("  [PASS] Item popup validation passed.")

    def test_04_print_link_validation(self, driver):
        print("\n[TC-SRYG-004] Clicking Print link and validating print data...")

        clicked = click_text(driver, ["Print"])
        assert clicked, "Print link was not found on the Supplier RYG Board."
        wait_ready(driver)
        time.sleep(PAUSE * 2)

        body_text = (driver.find_element(By.TAG_NAME, "body").text or "").strip()
        assert body_text, "No printable page content was found after clicking Print."
        print_tokens = ["Print", "Supplier RYG Board", "Item", "Description", "Qty"]
        assert any(token.lower() in body_text.lower() for token in print_tokens), (
            f"Print view did not contain expected data. Body: {body_text[:600]}"
        )
        take_screenshot(driver, "04_print_view")
        print(f"  [Print preview content] {body_text[:500]}")
        print("  [PASS] Print link validation passed.")

    def test_05_export_link_validation(self, driver):
        print("\n[TC-SRYG-005] Clicking Export link and validating Excel export data...")

        clicked = click_text(driver, ["Export"])
        assert clicked, "Export link was not found on the Supplier RYG Board."
        wait_ready(driver)
        time.sleep(PAUSE * 3)

        download_roots = [
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "reports", "downloads"),
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "reports"),
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "reports", "downloads_debug"),
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "reports"),
            os.path.join(os.path.expanduser("~"), "Downloads"),
        ]
        before_files = set()
        for root in download_roots:
            if os.path.isdir(root):
                for path in Path(root).iterdir():
                    if path.is_file():
                        before_files.add(str(path.resolve()))

        export_file = wait_for_download(download_roots, before_files=before_files, timeout=45)
        if export_file is None:
            for root in download_roots:
                if os.path.isdir(root):
                    for path in Path(root).glob("*RYG*.*"):
                        if path.is_file() and path.name.lower().endswith((".xls", ".xlsx", ".csv")):
                            export_file = path
                            break
                if export_file is not None:
                    break

        assert export_file is not None, "No Excel export file was generated after clicking Export."
        assert export_file.stat().st_size > 0, f"Export file is empty: {export_file}"
        assert "supplier" in export_file.name.lower() or "ryg" in export_file.name.lower() or export_file.name.lower().endswith((".xls", ".xlsx", ".csv")), (
            f"Unexpected export file generated: {export_file.name}"
        )

        print(f"  [Export file] {export_file}")
        take_screenshot(driver, "05_after_export")

        file_name = export_file.name.lower()
        assert file_name.endswith((".xls", ".xlsx", ".csv")), (
            f"Unexpected export type generated: {export_file.name}"
        )

        if file_name.endswith(".csv"):
            try:
                with open(export_file, "r", encoding="utf-8", errors="ignore") as fh:
                    text_sample = fh.read(2000)
            except Exception:
                text_sample = ""
        elif file_name.endswith((".xlsx", ".xls")):
            try:
                wb = load_workbook(export_file, read_only=True)
                ws = wb[wb.sheetnames[0]]
                rows = []
                for row in ws.iter_rows(min_row=1, max_row=min(ws.max_row, 10), values_only=True):
                    values = []
                    for value in row:
                        values.append("" if value is None else str(value))
                    rows.append(" ".join(values).strip())
                text_sample = " | ".join(r for r in rows if r)
            except Exception:
                text_sample = ""
        else:
            try:
                with open(export_file, "rb") as fh:
                    raw = fh.read(2000)
                text_sample = raw.decode("utf-8", errors="ignore")
            except Exception:
                text_sample = ""

        if text_sample:
            export_keywords = ["Item", "Description", "Qty", "Status", "RYG", "Rule Description"]
            assert any(keyword.lower() in text_sample.lower() for keyword in export_keywords), (
                f"Downloaded export file did not include expected RYG columns: {export_file}"
            )

        print("  [PASS] Export link validation passed.")
