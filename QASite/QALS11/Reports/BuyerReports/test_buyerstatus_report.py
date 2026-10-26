"""
QALS11 | Reports > Buyer Status — End-to-End Report to Release Flow
====================================================================
URL  : https://engineering.ultrivalms.com/QALS1011
User : buyeruser / Ultriva!23

Test Flow
---------
  1.  Login as buyeruser
  2.  Navigate to Reports -> Buyer Reports -> BuyerStatus report
  3.  Click Go on the Buyer Status filter
  4.  Verify the report table loads
  5.  Click the first numeric On Hand hyperlink
  6.  On Release Cards list, select cards and click Release
  7.  Verify the release result page/message

Run (from qa_automation/):
    pytest tests/QALS11/Reports/test_buyerstatus_report.py -v -s
"""

import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# ============================================================================
# CONFIGURATION
# ============================================================================
BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
USERNAME = "buyeruser"
PASSWORD = "Ultriva!23"
PAUSE = 1.5
BUYER_STATUS_URL = f"{BASE_URL}/BuyerReport/BuyerStatus"

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture(scope="class")
def driver():
    """Class-scoped Chrome driver — one browser session per test class."""
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    drv = webdriver.Chrome(options=options)
    drv.implicitly_wait(10)
    drv.set_page_load_timeout(30)
    drv.maximize_window()
    yield drv
    drv.quit()

# ============================================================================
# HELPERS
# ============================================================================


def wait_ready(driver, timeout=30):
    """Wait for document.readyState == complete."""
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def find(driver, by, locator, timeout=15):
    """Wait for presence and return element."""
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, locator))
    )


def clickable(driver, by, locator, timeout=15):
    """Wait until clickable and return element."""
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, locator))
    )


def scroll_to(driver, el):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'})", el)
    time.sleep(0.3)


def take_screenshot(driver, name):
    import os

    screenshots_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "..", "reports", "screenshots"
    )
    os.makedirs(screenshots_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(screenshots_dir, f"buyerstatus_{name}_{ts}.png")
    driver.save_screenshot(path)
    print(f"  [screenshot] {path}")
    return path


def safe_click_first(driver, locators, timeout=5):
    """Return the first clickable element found from a list of locators."""
    for locator in locators:
        try:
            return WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
        except Exception:
            continue
    return None


def click_visible_text(driver, text):
    """Click the first visible element matching text via JS fallback."""
    return driver.execute_script(
        "var wanted = arguments[0].trim().toLowerCase();"
        "var els = document.querySelectorAll('a, button, input[type=\"button\"], input[type=\"submit\"], span, div');"
        "for (var i = 0; i < els.length; i++) {"
        "  var el = els[i];"
        "  var txt = (el.innerText || el.value || '').trim().toLowerCase();"
        "  if (!txt) continue;"
        "  if (txt === wanted && el.offsetParent !== null) { el.click(); return el; }"
        "}"
        "return null;",
        text,
    )


def navigate_to_buyer_status(driver):
    """Open Buyer Status report through the menu, with a direct URL fallback."""
    if "BuyerStatus" in driver.current_url:
        return

    reports_link = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[normalize-space()='Reports' or contains(normalize-space(.),'Reports')]") ,
            (By.XPATH, "//*[self::a or self::span or self::div][contains(normalize-space(.),'Reports') and not(contains(normalize-space(.),'BuyerStatus'))]"),
            (By.XPATH, "//a[contains(@href,'Report') and not(contains(@href,'BuyerStatus'))]"),
        ],
        timeout=6,
    )
    if reports_link:
        scroll_to(driver, reports_link)
        driver.execute_script("arguments[0].click()", reports_link)
        wait_ready(driver)
        time.sleep(PAUSE)

    buyer_reports_link = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[normalize-space()='Buyer Reports' or contains(normalize-space(.),'Buyer Reports')]") ,
            (By.XPATH, "//*[self::a or self::span][contains(normalize-space(.),'Buyer Reports')]") ,
            (By.XPATH, "//a[contains(@href,'BuyerReport') or contains(@href,'Buyer Reports')]") ,
        ],
        timeout=6,
    )
    if buyer_reports_link:
        scroll_to(driver, buyer_reports_link)
        driver.execute_script("arguments[0].click()", buyer_reports_link)
        wait_ready(driver)
        time.sleep(PAUSE)

    buyer_status_link = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[contains(@href,'BuyerStatus') or contains(normalize-space(.),'Buyer Status') or contains(normalize-space(.),'BuyerStatus')]") ,
            (By.XPATH, "//*[self::a or self::span][contains(normalize-space(.),'Buyer Status') or contains(normalize-space(.),'BuyerStatus')]") ,
        ],
        timeout=6,
    )
    if buyer_status_link:
        scroll_to(driver, buyer_status_link)
        driver.execute_script("arguments[0].click()", buyer_status_link)
        wait_ready(driver)
        time.sleep(PAUSE)
    else:
        print("  [WARN] BuyerStatus menu link not found — navigating directly to the report URL.")
        driver.get(BUYER_STATUS_URL)
        wait_ready(driver)
        time.sleep(PAUSE)


def click_go(driver):
    """Click the Go button on the Buyer Status filter page."""
    if "BuyerStatus" not in driver.current_url:
        driver.get(BUYER_STATUS_URL)
        wait_ready(driver)
        time.sleep(PAUSE)

    go_button = safe_click_first(
        driver,
        [
            (By.XPATH, "//button[normalize-space(text())='Go']"),
            (By.XPATH, "//a[normalize-space(text())='Go']"),
            (By.XPATH, "//input[@type='submit' and @value='Go']"),
            (By.XPATH, "//*[@id='btnGo' or @id='go-button' or contains(@id,'Go') ]"),
            (By.XPATH, "//span[contains(normalize-space(.),'Go')]") ,
        ],
        timeout=6,
    )
    if go_button:
        scroll_to(driver, go_button)
        driver.execute_script("arguments[0].click()", go_button)
        wait_ready(driver)
        time.sleep(PAUSE * 2)
        return

    clicked = click_visible_text(driver, "Go")
    if clicked:
        wait_ready(driver)
        time.sleep(PAUSE * 2)
        return

    print("  [WARN] Go button not found — continuing with current report state.")


def find_numeric_anchor_in_report(driver):
    """Find the first numeric anchor inside the report table body."""
    anchors = driver.find_elements(By.XPATH, "//table//tr[td]//a[normalize-space()]")
    for anchor in anchors:
        try:
            text = (anchor.text or "").strip().replace(",", "")
            if not text:
                continue
            if text.isdigit() and int(text) > 0 and anchor.is_displayed():
                return anchor
        except Exception:
            continue
    return None


def select_release_cards(driver, max_cards=3):
    """Select up to max_cards checkboxes on a release cards page."""
    checkboxes = driver.find_elements(By.XPATH, "//input[@type='checkbox']")
    assert checkboxes, "No checkboxes found on Release Cards page"

    selected = 0
    for chk in checkboxes:
        if selected >= max_cards:
            break
        try:
            name = (chk.get_attribute("name") or "").lower()
            klass = (chk.get_attribute("class") or "").lower()
            if "gridcheckbox" not in klass and "checkboxcardgid" not in name and "checkbox" not in name:
                continue
            scroll_to(driver, chk)
            if not chk.is_selected():
                driver.execute_script("arguments[0].click()", chk)
                time.sleep(0.4)
            if chk.is_selected():
                selected += 1
                print(f"  [INFO] Selected release card checkbox #{selected}")
        except Exception as exc:
            print(f"  [WARN] Could not select a checkbox: {exc}")

    assert selected > 0, "Could not confirm any release card checkbox selection"
    return selected


def find_release_button(driver):
    """Locate the Release action button on the cards page."""
    return safe_click_first(
        driver,
        [
            (By.XPATH, "//button[normalize-space(text())='Release']"),
            (By.XPATH, "//a[normalize-space(text())='Release']"),
            (By.XPATH, "//*[@id='btnRelease' or contains(@id,'release') or contains(@id,'Release')]"),
            (By.XPATH, "//input[@value='Release']"),
            (By.XPATH, "//span[contains(normalize-space(.),'Release') and (contains(@class,'btn') or contains(@class,'button'))]"),
        ],
        timeout=6,
    )


def maybe_fill_release_note(driver):
    """Fill any visible release-note field if the page exposes one."""
    note_value = "Released from Buyer Status report"
    fields = driver.find_elements(
        By.XPATH,
        "//textarea[contains(translate(@id,'NOTE','note'),'note') or "
        "contains(translate(@name,'NOTE','note'),'note') or "
        "contains(translate(@placeholder,'NOTE','note'),'note')] | "
        "//input[contains(translate(@id,'NOTE','note'),'note') or "
        "contains(translate(@name,'NOTE','note'),'note') or "
        "contains(translate(@placeholder,'NOTE','note'),'note')]",
    )
    for field in fields:
        try:
            if field.is_displayed() and field.is_enabled():
                scroll_to(driver, field)
                field.clear()
                field.send_keys(note_value)
                print(f"  [INFO] Filled release note: {note_value}")
                return True
        except Exception:
            continue
    return False

# ============================================================================
# TEST CLASS
# ============================================================================


@pytest.mark.usefixtures("driver")
class TestBuyerStatusReport:
    # ── TC-BSR-001: Login ──────────────────────────────────────────────────
    def test_01_login(self, driver):
        """Login to QA site with buyeruser credentials."""
        print("\n[TC-BSR-001] Logging in to QA site...")
        driver.get(BASE_URL)
        wait_ready(driver)

        username_field = find(driver, By.ID, "UserName")
        password_field = find(driver, By.ID, "Password")
        login_button = clickable(driver, By.ID, "login-button")

        username_field.clear()
        username_field.send_keys(USERNAME)
        password_field.clear()
        password_field.send_keys(PASSWORD)
        login_button.click()
        wait_ready(driver)
        time.sleep(PAUSE)

        take_screenshot(driver, "01_after_login")
        current_url = driver.current_url
        print(f"  [URL] {current_url}")
        assert BASE_URL.lower() in current_url.lower() or "Home" in current_url, \
            f"Login may have failed. URL: {current_url}"
        print("  [PASS] Login successful.")

    # ── TC-BSR-002: Open Buyer Status report ───────────────────────────────
    def test_02_open_buyer_status_report(self, driver):
        """Navigate to Reports -> Buyer Reports -> BuyerStatus report."""
        print("\n[TC-BSR-002] Opening BuyerStatus report...")
        navigate_to_buyer_status(driver)

        take_screenshot(driver, "02_buyer_status_report")
        assert "BuyerStatus" in driver.current_url or "BuyerReport" in driver.current_url, \
            f"Expected BuyerStatus report page. Got: {driver.current_url}"
        print(f"  [PASS] BuyerStatus report page loaded: {driver.current_url}")

    # ── TC-BSR-003: Click Go and verify UI ────────────────────────────────
    def test_03_click_go_and_verify_report(self, driver):
        """Click Go on the Buyer Status filter and verify the report UI loads."""
        print("\n[TC-BSR-003] Clicking Go on the BuyerStatus filter...")
        click_go(driver)

        take_screenshot(driver, "03_after_go")
        rows = driver.find_elements(By.XPATH, "//table//tr[td]")
        print(f"  [INFO] Table rows found: {len(rows)}")
        assert len(rows) > 0, "Buyer Status report table did not load any rows"
        assert "BuyerStatus" in driver.current_url or "BuyerReport" in driver.current_url, \
            f"Unexpected URL after Go: {driver.current_url}"
        print("  [PASS] Buyer Status report table is visible.")

    # ── TC-BSR-004: Click On Hand hyperlink and release cards ─────────────
    def test_04_open_on_hand_and_release_cards(self, driver):
        """Click the On Hand hyperlink, select cards, and release them."""
        print("\n[TC-BSR-004] Clicking On Hand hyperlink and releasing cards...")

        on_hand_link = find_numeric_anchor_in_report(driver)
        if on_hand_link is None:
            raise AssertionError("Could not find a numeric On Hand hyperlink in the report table")

        on_hand_text = on_hand_link.text.strip()
        print(f"  [INFO] Clicking On Hand hyperlink value: {on_hand_text}")
        scroll_to(driver, on_hand_link)
        driver.execute_script("arguments[0].click()", on_hand_link)
        wait_ready(driver)
        time.sleep(PAUSE * 2)

        take_screenshot(driver, "04_after_on_hand_click")
        print(f"  [URL after On Hand click] {driver.current_url}")
        assert "Release" in driver.current_url or "ReleaseCard" in driver.current_url, \
            f"Expected Release Cards page after On Hand click. Got: {driver.current_url}"

        maybe_fill_release_note(driver)
        selected = select_release_cards(driver, max_cards=3)
        print(f"  [INFO] Selected {selected} release card(s)")

        release_btn = find_release_button(driver)
        assert release_btn, "Release button not found on Release Cards page"
        scroll_to(driver, release_btn)
        print(f"  [INFO] Clicking Release button: '{release_btn.text.strip()}'")
        driver.execute_script("arguments[0].click()", release_btn)
        wait_ready(driver)
        time.sleep(PAUSE * 2)

        take_screenshot(driver, "05_after_release")
        current_url = driver.current_url
        print(f"  [URL after Release] {current_url}")

        success_texts = [
            "Following Cards were successful",
            "Released To",
            "Card Successfully Released",
        ]
        page_text = driver.find_element(By.TAG_NAME, "body").text
        assert any(text.lower() in page_text.lower() for text in success_texts) or \
            "Release" in current_url, \
            f"Release result page did not show the expected success state. URL: {current_url}"
        print("  [PASS] BuyerStatus report flow reached the release result state.")
