"""
QALS11 | Reports > Buyer Reports > Total Card Aging Report
===========================================================
URL  : https://engineering.ultrivalms.com/QALS1011
User : buyeruser / Ultriva!23

Test Flow
---------
  1.  Login as buyeruser
  2.  Navigate to Reports -> Buyer Reports -> Card Aging report
  3.  Select Status = On Hand
  4.  Click Show Report
  5.  Verify the report output loads
  6.  Click Change Filter and verify return to filter page
  7.  Select Status = In Process
  8.  Click Show Report and verify the report output loads again

Run (from qa_automation/):
    pytest tests/QALS11/Reports/test_total_card_aging_report.py -v -s
"""

import os
import time

import pytest
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

# ============================================================================
# CONFIGURATION
# ============================================================================
BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
USERNAME = "buyeruser"
PASSWORD = "Ultriva!23"
PAUSE = 1.2
CARD_AGING_URL = f"{BASE_URL}/BuyerReport/CardAging"
CARD_AGING_FILTER_URL = f"{BASE_URL}/BuyerReport/CardAgingFilter"
LOGIN_URL = (
    f"{BASE_URL}/Account/Login?ReturnUrl=%2FQALS1011%2FBuyerReport%2FCardAgingFilter"
)


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture(scope="class")
def driver():
    """Class-scoped Chrome driver - one browser session per test class."""
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
    screenshots_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "reports", "screenshots"
    )
    os.makedirs(screenshots_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(screenshots_dir, f"total_card_aging_{name}_{ts}.png")
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
        "var els = document.querySelectorAll('a, button, input[type=\"button\"], input[type=\"submit\"], option, span, div, li');"
        "for (var i = 0; i < els.length; i++) {"
        "  var el = els[i];"
        "  var txt = (el.innerText || el.textContent || el.value || '').trim().toLowerCase();"
        "  if (!txt) continue;"
        "  if (txt === wanted && el.offsetParent !== null) { el.click(); return el; }"
        "}"
        "return null;",
        text,
    )


def open_url(driver, url, timeout=30):
    """Navigate to a URL and tolerate renderer timeouts if the page is usable."""
    try:
        driver.get(url)
        wait_ready(driver, timeout=timeout)
        return True
    except TimeoutException:
        try:
            driver.execute_script("window.stop();")
        except Exception:
            pass
        time.sleep(PAUSE)
        return True


def on_login_page(driver):
    """Return True when the browser is currently on the login page."""
    if "/Account/Login" in driver.current_url:
        return True
    return bool(driver.find_elements(By.ID, "login-button"))


def ensure_logged_in(driver):
    """Authenticate through the Card Aging return URL when needed."""
    if not on_login_page(driver):
        return

    print("  [INFO] Not logged in - authenticating via Card Aging login URL")
    open_url(driver, LOGIN_URL)

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


def click_change_filter(driver):
    """Click Change Filter on report page."""
    locators = [
        (By.XPATH, "//button[contains(normalize-space(.), 'Change Filter') or contains(normalize-space(.), 'Change filter') ]"),
        (By.XPATH, "//a[contains(normalize-space(.), 'Change Filter') or contains(normalize-space(.), 'Change filter') ]"),
        (By.XPATH, "//button[@id='changeFilter' or contains(@id,'ChangeFilter') or contains(@id,'changeFilter')]"),
        (By.XPATH, "//*[contains(normalize-space(.),'Change Filter') and (self::button or self::a)]"),
    ]
    for locator in locators:
        try:
            element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(locator))
            scroll_to(driver, element)
            driver.execute_script("arguments[0].click();", element)
            wait_ready(driver)
            time.sleep(PAUSE)
            return True
        except Exception:
            continue

    clicked = click_visible_text(driver, "Change Filter")
    if clicked:
        wait_ready(driver)
        time.sleep(PAUSE)
        return True

    return False


def filter_page_visible(driver):
    """Check whether the Card Aging filter controls are visible."""
    if on_login_page(driver):
        return False

    if "cardagingfilter" in driver.current_url.lower():
        return bool(
            driver.find_elements(
                By.XPATH,
                "//button[contains(normalize-space(.),'Show Report')] | //a[contains(normalize-space(.),'Show Report')] | //select[contains(@id,'Status') or contains(@name,'Status')] | //label[contains(normalize-space(.),'Status')]",
            )
        )

    fields = driver.find_elements(
        By.XPATH,
        "//label[contains(normalize-space(.),'Status')] | //select[contains(@id,'Status') or contains(@name,'Status')] | //button[contains(normalize-space(.),'Show Report')] | //a[contains(normalize-space(.),'Show Report')]",
    )
    return len(fields) > 0


def report_loaded(driver):
    """Check that the Card Aging report output is visible after submit."""
    if on_login_page(driver):
        return False

    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
    if "change filter" in body_text or "age>=" in body_text or "sorted by:" in body_text:
        return True
    rows = driver.find_elements(By.XPATH, "//table//tr[td]")
    return len(rows) > 0


def open_status_dropdown(driver):
    """Open the Status control using multiple locator strategies."""
    status_locators = [
        (By.ID, "Status"),
        (By.NAME, "Status"),
        (By.XPATH, "//select[contains(@id,'Status') or contains(@name,'Status') or contains(@id,'status') or contains(@name,'status')]"),
        (By.XPATH, "//label[contains(normalize-space(.),'Status')]/following::select[1]"),
        (By.XPATH, "//*[contains(normalize-space(.),'Status')]/following::select[1]"),
        (By.XPATH, "//*[@id='divStatus' or contains(@id,'Status')][self::div or self::span]"),
        (By.XPATH, "//label[contains(normalize-space(.),'Status')]/following::*[self::div or self::span][1]"),
        (By.XPATH, "//input[contains(@id,'Status') or contains(@name,'Status') or contains(@id,'status') or contains(@name,'status')]"),
        (By.XPATH, "//label[contains(normalize-space(.),'Status')]/following::input[1]"),
    ]
    for by, locator in status_locators:
        try:
            el = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((by, locator))
            )
            if el.is_displayed() and el.is_enabled():
                scroll_to(driver, el)
                el.click()
                time.sleep(0.8)
                return el
        except Exception:
            continue

    clicked = click_visible_text(driver, "Status")
    if clicked:
        time.sleep(0.8)
        return clicked
    return None


def select_status(driver, status_name):
    """Select a specific Card Aging status value."""
    normalized = status_name.strip().lower()
    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
    if f"status: {normalized}" in body_text:
        print(f"  [INFO] Status '{status_name}' already appears selected")
        return True

    status_selectors = [
        (By.ID, "Status"),
        (By.NAME, "Status"),
        (By.XPATH, "//select[contains(@id,'Status') or contains(@name,'Status') or contains(@id,'status') or contains(@name,'status')][1]"),
        (By.XPATH, "//label[contains(normalize-space(.),'Status')]/following::select[1]"),
    ]
    for by, locator in status_selectors:
        try:
            select_el = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((by, locator))
            )
            scroll_to(driver, select_el)
            if select_el.tag_name.lower() == "select":
                select = Select(select_el)
                try:
                    select.select_by_visible_text(status_name)
                    time.sleep(0.8)
                    print(f"  [INFO] Selected Status '{status_name}' using Select")
                    return True
                except Exception:
                    pass

                for option in select.options:
                    option_text = (option.text or "").strip().lower()
                    if option_text == normalized or normalized in option_text:
                        select.select_by_visible_text(option.text)
                        time.sleep(0.8)
                        print(f"  [INFO] Selected Status '{option.text}' using partial Select match")
                        return True
        except Exception:
            continue

    trigger = open_status_dropdown(driver)
    assert trigger, "Could not find Status trigger on Card Aging filter page"

    option_locators = [
        f"//*[self::option or self::li or self::a or self::span or self::div][normalize-space()='{status_name}']",
        f"//*[self::option or self::li or self::a or self::span or self::div][contains(normalize-space(),'{status_name}')]",
        f"//*[contains(@class,'ui-menu-item')]//*[contains(normalize-space(),'{status_name}')]",
        f"//*[contains(@class,'dropdown-menu')]//*[contains(normalize-space(),'{status_name}')]",
    ]
    for locator in option_locators:
        try:
            option = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, locator))
            )
            scroll_to(driver, option)
            driver.execute_script("arguments[0].click();", option)
            time.sleep(0.8)
            print(f"  [INFO] Selected Status option via: {locator}")
            return True
        except Exception:
            continue

    js_result = driver.execute_script(
        "var wanted = arguments[0].toLowerCase();"
        "var nodes = document.querySelectorAll('option, li, a, span, div');"
        "for (var i = 0; i < nodes.length; i++) {"
        "  var node = nodes[i];"
        "  var text = (node.innerText || node.textContent || '').trim().toLowerCase();"
        "  if (text === wanted || text.indexOf(wanted) !== -1) { node.click(); return true; }"
        "}"
        "return false;",
        status_name,
    )
    if js_result:
        time.sleep(0.8)
        print(f"  [INFO] Selected Status '{status_name}' via JS fallback")
        return True

    return False


def click_show_report(driver):
    """Click Show Report button."""
    show_btn = safe_click_first(
        driver,
        [
            (By.XPATH, "//button[normalize-space(text())='Show Report']"),
            (By.XPATH, "//a[normalize-space(text())='Show Report']"),
            (By.XPATH, "//input[@type='submit' and @value='Show Report']"),
            (By.XPATH, "//*[@id='btnShowReport' or contains(@id,'ShowReport') or contains(@id,'showReport')]"),
            (By.XPATH, "//*[contains(normalize-space(.),'Show Report') and (contains(@class,'btn') or contains(@class,'button'))]"),
        ],
        timeout=6,
    )
    if show_btn:
        scroll_to(driver, show_btn)
        driver.execute_script("arguments[0].click();", show_btn)
        wait_ready(driver)
        time.sleep(PAUSE * 2)
        return True

    clicked = click_visible_text(driver, "Show Report")
    if clicked:
        wait_ready(driver)
        time.sleep(PAUSE * 2)
        return True

    return False


def ensure_card_aging_filter_page(driver):
    """Open the Card Aging filter page via report URL, menu path, or direct filter fallback."""
    if filter_page_visible(driver):
        return

    if "cardaging" not in driver.current_url.lower():
        open_url(driver, CARD_AGING_URL)
        ensure_logged_in(driver)
        time.sleep(PAUSE)

    if filter_page_visible(driver):
        return

    if "cardaging" in driver.current_url.lower() and click_change_filter(driver):
        if filter_page_visible(driver):
            return

    reports_link = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[normalize-space()='Reports' or contains(normalize-space(.),'Reports')]"),
            (By.XPATH, "//*[self::a or self::span or self::div][contains(normalize-space(.),'Reports')]"),
            (By.XPATH, "//a[contains(@href,'Report')]"),
        ],
        timeout=6,
    )
    if reports_link:
        try:
            scroll_to(driver, reports_link)
            driver.execute_script("arguments[0].click()", reports_link)
            wait_ready(driver)
            time.sleep(PAUSE)
        except Exception:
            pass

    buyer_reports_link = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[normalize-space()='Buyer Reports' or contains(normalize-space(.),'Buyer Reports')]"),
            (By.XPATH, "//*[self::a or self::span][contains(normalize-space(.),'Buyer Reports')]"),
            (By.XPATH, "//a[contains(@href,'BuyerReport')]"),
        ],
        timeout=6,
    )
    if buyer_reports_link:
        scroll_to(driver, buyer_reports_link)
        driver.execute_script("arguments[0].click()", buyer_reports_link)
        wait_ready(driver)
        time.sleep(PAUSE)

    card_aging_link = safe_click_first(
        driver,
        [
            (By.XPATH, "//a[contains(@href,'CardAgingFilter') or contains(@href,'CardAging') or contains(normalize-space(.),'Card Aging')]"),
            (By.XPATH, "//*[self::a or self::span][contains(normalize-space(.),'Card Aging')]"),
        ],
        timeout=6,
    )
    if card_aging_link:
        scroll_to(driver, card_aging_link)
        driver.execute_script("arguments[0].click()", card_aging_link)
        wait_ready(driver)
        time.sleep(PAUSE)

    if filter_page_visible(driver):
        return

    if "cardaging" in driver.current_url.lower() and click_change_filter(driver):
        if filter_page_visible(driver):
            return

    open_url(driver, CARD_AGING_FILTER_URL)
    ensure_logged_in(driver)
    time.sleep(PAUSE)


# ============================================================================
# TEST CLASS
# ============================================================================


@pytest.mark.usefixtures("driver")
class TestTotalCardAgingReport:
    def test_01_login(self, driver):
        """Login to QA site with buyeruser credentials."""
        print("\n[TC-TCAR-001] Logging in to QA site...")
        open_url(driver, LOGIN_URL)
        ensure_logged_in(driver)
        time.sleep(PAUSE)

        take_screenshot(driver, "01_after_login")
        current_url = driver.current_url
        print(f"  [URL] {current_url}")
        assert "/account/login" not in current_url.lower(), (
            f"Login may have failed. URL: {current_url}"
        )
        print("  [PASS] Login successful.")

    def test_02_open_total_card_aging_report(self, driver):
        """Navigate to Reports -> Buyer Reports -> Card Aging report."""
        print("\n[TC-TCAR-002] Opening Total Card Aging report...")
        ensure_card_aging_filter_page(driver)

        take_screenshot(driver, "02_card_aging_filter")
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        assert filter_page_visible(driver) or "card aging report" in page_text, (
            f"Expected Card Aging filter page. Got: {driver.current_url}"
        )
        print(f"  [PASS] Card Aging filter page loaded: {driver.current_url}")

    def test_03_select_on_hand_and_show_report(self, driver):
        """Select Status as On Hand and click Show Report."""
        print("\n[TC-TCAR-003] Selecting Status = On Hand and clicking Show Report...")

        selected = select_status(driver, "On Hand")
        assert selected, "Could not set Status to On Hand"

        clicked = click_show_report(driver)
        assert clicked, "Show Report button not found on Card Aging filter page"

        take_screenshot(driver, "03_on_hand_report")
        assert report_loaded(driver), f"Card Aging report did not load. URL: {driver.current_url}"
        print("  [PASS] Card Aging report loaded for Status = On Hand.")

    def test_04_click_change_filter(self, driver):
        """Click Change Filter and verify return to filter page."""
        print("\n[TC-TCAR-004] Clicking Change Filter...")

        clicked = click_change_filter(driver)
        assert clicked, "Change Filter button was not found on Card Aging report page"

        take_screenshot(driver, "04_after_change_filter")
        assert filter_page_visible(driver), (
            f"Did not return to Card Aging filter page. URL: {driver.current_url}"
        )
        print("  [PASS] Change Filter returned to Card Aging filter page.")

    def test_05_select_in_process_and_show_report(self, driver):
        """Select Status as In Process and click Show Report again."""
        print("\n[TC-TCAR-005] Selecting Status = In Process and clicking Show Report...")

        selected = select_status(driver, "In Process")
        assert selected, "Could not set Status to In Process"

        clicked = click_show_report(driver)
        assert clicked, "Show Report button not found on Card Aging filter page"

        take_screenshot(driver, "05_in_process_report")
        assert report_loaded(driver), (
            f"Card Aging report did not reload for In Process. URL: {driver.current_url}"
        )
        print("  [PASS] Card Aging report loaded for Status = In Process.")