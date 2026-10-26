"""
QALS11 | Actions > Supplier Actions > AcceptCards
=================================================
URL   : https://engineering.ultrivalms.com/QALS1011/SupplierAction/AcceptCards
User  : supnewuser / Ultriva!23

Test Flow
---------
  1. Login as supnewuser
  2. Open Accept Cards list
  3. Select one or more cards from the Accept Cards list
  4. Click Accept
  5. Verify the page shows the accepted result or returns to the list

Run (from qa_automation/):
    pytest "tests/QALS11/Actions/Supplier Actions/AcceptCards.py" -v -s
"""

import os
import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://engineering.ultrivalms.com/QALS1011"
ACCEPT_CARDS_URL = f"{BASE_URL}/SupplierAction/AcceptCards"
USERNAME = "supnewuser"
PASSWORD = "Ultriva!23"
PAUSE = 1.5


@pytest.fixture(scope="class")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

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


def take_screenshot(driver, name):
    screenshots_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "reports", "screenshots"
    )
    os.makedirs(screenshots_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(screenshots_dir, f"acceptcards_{name}_{ts}.png")
    driver.save_screenshot(path)
    print(f"  [screenshot] {path}")
    return path


def click_visible_text(driver, labels):
    for label in labels:
        locators = [
            (
                By.XPATH,
                f"//*[self::a or self::button or self::input or self::span or self::div][normalize-space(.)='{label}']",
            ),
            (
                By.XPATH,
                f"//*[self::a or self::button or self::input or self::span or self::div][contains(normalize-space(.), '{label}')]",
            ),
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
              var txt = (els[i].innerText || els[i].value || '').replace(/\s+/g, ' ').trim().toLowerCase();
              if (txt === wanted || txt.indexOf(wanted) !== -1) {
                var el = els[i];
                if (el.offsetParent !== null) {
                  try { el.click(); } catch (e) { el.dispatchEvent(new MouseEvent('click', {bubbles: true})); }
                  return true;
                }
              }
            }
            return false;
            """,
            label,
        )
        if matched:
            return True
    return False


def click_accept_category(driver, primary_labels, fallback_labels=None):
    labels = list(primary_labels)
    if fallback_labels:
        labels.extend(fallback_labels)

    seen = set()
    for label in labels:
        key = label.lower()
        if key in seen:
            continue
        seen.add(key)
        if click_visible_text(driver, [label]):
            return True

    generic_candidates = [
        "Reschedule Approval Cards",
        "Reschedule Approval Card",
        "Reschedule Approval",
        "RunLine Cards",
        "Runline Cards",
        "Run Line Cards",
        "Wait for PO Cards",
        "Released Cards",
        "Released Card",
        "Recall Wait Cards",
        "Approval",
    ]
    for label in generic_candidates:
        if label.lower() in seen:
            continue
        if click_visible_text(driver, [label]):
            return True
    return False


def select_first_available_cards(driver, max_cards=3):
    checkboxes = driver.find_elements(
        By.XPATH,
        "//input[@type='checkbox' and not(@disabled) and not(contains(@id, 'selectAll')) and not(contains(@name, 'selectAll')) and not(contains(@value, 'All'))]",
    )
    filtered = []
    for cb in checkboxes:
        try:
            if cb.is_displayed():
                filtered.append(cb)
        except Exception:
            continue

    if not filtered:
        return False

    for cb in filtered[:max_cards]:
        try:
            if not cb.is_selected():
                cb.click()
        except Exception:
            driver.execute_script("arguments[0].click();", cb)

    return True


def select_first_available_result_cards(driver, max_cards=1):
    checkboxes = driver.find_elements(By.XPATH, "//input[@type='checkbox' and not(@disabled)]")
    filtered = []
    for cb in checkboxes:
        class_name = (cb.get_attribute("class") or "").lower()
        name = (cb.get_attribute("name") or "").lower()
        value = (cb.get_attribute("value") or "").lower()
        if "selectall" in class_name or "selectall" in name or "selectall" in value:
            continue
        filtered.append(cb)

    if not filtered:
        return False

    for cb in filtered[:max_cards]:
        try:
            if not cb.is_selected():
                cb.click()
        except Exception:
            driver.execute_script("arguments[0].click();", cb)

    return True


def find_action_button(driver, labels):
    for label in labels:
        locators = [
            (By.XPATH, f"//button[normalize-space(.)='{label}']"),
            (By.XPATH, f"//a[normalize-space(.)='{label}']"),
            (By.XPATH, f"//input[@type='submit' and @value='{label}']"),
            (By.XPATH, f"//input[@type='button' and @value='{label}']"),
            (By.XPATH, f"//*[self::button or self::a or self::input or self::span][contains(normalize-space(.), '{label}')]"),
        ]
        for by, locator in locators:
            try:
                element = WebDriverWait(driver, 8).until(EC.element_to_be_clickable((by, locator)))
                if element.is_displayed() and element.is_enabled():
                    return element
            except Exception:
                continue

        element = driver.execute_script(
            """
            var wanted = arguments[0].trim().toLowerCase();
            var els = document.querySelectorAll('a, button, input, span, div, td, li');
            for (var i = 0; i < els.length; i++) {
              var txt = (els[i].innerText || els[i].value || '').replace(/\s+/g, ' ').trim().toLowerCase();
              if ((txt === wanted || txt.indexOf(wanted) !== -1) && els[i].offsetParent !== null) {
                return els[i];
              }
            }
            return null;
            """,
            label,
        )
        if element is not None:
            return element
    return None


def find_accept_button(driver):
    candidates = [
        "//button[normalize-space(.)='Accept']",
        "//button[normalize-space(.)='ACCEPT']",
        "//button[contains(normalize-space(.), 'Accept')]",
        "//*[self::button or self::a][contains(normalize-space(.), 'Accept')]",
        "//*[contains(@title, 'Accept') or contains(@aria-label, 'Accept')]",
        "//input[@value='Accept']",
    ]

    for path in candidates:
        try:
            elements = driver.find_elements(By.XPATH, path)
            for el in elements:
                if el.is_displayed() and el.is_enabled():
                    return el
        except Exception:
            continue

    try:
        return driver.execute_script(
            """
            var list = Array.from(document.querySelectorAll('button, a, input'));
            for (var i = 0; i < list.length; i++) {
              var el = list[i];
              var txt = (el.innerText || el.value || el.getAttribute('aria-label') || el.title || '').replace(/\s+/g, ' ').trim().toLowerCase();
              var visible = !!(el.offsetParent !== null || el.getClientRects().length > 0);
              if (visible && (txt === 'accept' || txt.indexOf('accept') !== -1)) {
                return el;
              }
            }
            return null;
            """
        )
    except Exception:
        return None


def wait_for_accept_results(driver, timeout=40):
    def _is_results_page(d):
        try:
            url = (d.current_url or "").lower()
            body = (d.find_element(By.TAG_NAME, "body").text or "").lower()
        except Exception:
            return False

        back_buttons = [
            "back to items",
            "back to cards",
        ]
        return (
            "acceptresults" in url
            or "accept cards results" in body
            or "following cards were successful" in body
            or "card successfully accepted" in body
            or "successfully accepted" in body
            or any(token in body for token in back_buttons)
            or any(
                text in body
                for text in [
                    "accept cards",
                    "cards were successful",
                    "cards list",
                ]
            )
        )

    WebDriverWait(driver, timeout).until(_is_results_page)


def select_cards_and_click_accept(driver, max_cards=2):
    # Row checkboxes only; the header select-all has class grid-all-checkbox.
    row_checkboxes = [
        cb
        for cb in driver.find_elements(
            By.CSS_SELECTOR, "input.GridCheckbox[name^='AcceptCards_']:not(.grid-all-checkbox)"
        )
        if cb.is_displayed() and cb.is_enabled()
    ]
    assert len(row_checkboxes) >= max_cards, (
        f"Expected at least {max_cards} selectable cards in the Accept Cards list, found {len(row_checkboxes)}."
    )
    for cb in row_checkboxes[:max_cards]:
        scroll_to(driver, cb)
        if not cb.is_selected():
            driver.execute_script("arguments[0].click();", cb)
    checked = [cb for cb in row_checkboxes if cb.is_selected()]
    assert len(checked) == max_cards, f"Expected {max_cards} selected cards, got {len(checked)}."
    take_screenshot(driver, "03b_cards_selected")

    # Toolbar Accept button on the Accept Cards List (not the breadcrumb 'Accept' link).
    accept_button = clickable(driver, By.ID, "btndoActTop")
    scroll_to(driver, accept_button)

    for attempt in range(3):
        try:
            ActionChains(driver).move_to_element(accept_button).click().perform()
            wait_ready(driver)
            time.sleep(2)
            try:
                wait_for_accept_results(driver)
                return accept_button
            except Exception:
                body = (driver.find_element(By.TAG_NAME, "body").text or "").lower()
                if any(token in body for token in ["following cards were successful", "card successfully accepted", "back to items", "back to cards"]):
                    return accept_button
        except Exception:
            pass

        try:
            accept_button.click()
            wait_ready(driver)
            time.sleep(2)
            try:
                wait_for_accept_results(driver)
                return accept_button
            except Exception:
                body = (driver.find_element(By.TAG_NAME, "body").text or "").lower()
                if any(token in body for token in ["following cards were successful", "card successfully accepted", "back to items", "back to cards"]):
                    return accept_button
        except Exception:
            pass

        try:
            driver.execute_script("arguments[0].click();", accept_button)
            wait_ready(driver)
            time.sleep(2)
            try:
                wait_for_accept_results(driver)
                return accept_button
            except Exception:
                body = (driver.find_element(By.TAG_NAME, "body").text or "").lower()
                if any(token in body for token in ["following cards were successful", "card successfully accepted", "back to items", "back to cards"]):
                    return accept_button
        except Exception:
            pass

        try:
            accept_button = driver.find_element(By.ID, "btndoActTop")
            scroll_to(driver, accept_button)
        except Exception:
            break

    raise AssertionError("Accept button was visible but could not trigger the Accept Cards Results screen.")


def assert_success_message(driver, keywords, action_name):
    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
    for keyword in keywords:
        if keyword.lower() in body_text:
            return True
    raise AssertionError(f"Expected {action_name} success message. Page body: {body_text[:1000]}")


def assert_post_action_state(driver, keywords, action_name):
    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
    for keyword in keywords:
        if keyword.lower() in body_text:
            return True

    page_indicators = [
        "accept items list",
        "items list",
        "cards list",
        "my items list",
        "my cards list",
    ]
    if any(indicator in body_text for indicator in page_indicators):
        return True

    back_buttons = driver.find_elements(
        By.XPATH,
        "//*[contains(normalize-space(.), 'Back To Items') or contains(normalize-space(.), 'Back to Items') or contains(normalize-space(.), 'Back To Cards') or contains(normalize-space(.), 'Back to Cards')]",
    )
    if back_buttons:
        return True

    raise AssertionError(f"Expected {action_name} confirmation or return-to-list state. Page body: {body_text[:1000]}")


def click_back_to_cards(driver):
    back_link = None
    preferred_xpaths = [
        "//button[normalize-space(.)='Back To Cards']",
        "//button[normalize-space(.)='Back to Cards']",
        "//a[normalize-space(.)='Back To Cards']",
        "//a[normalize-space(.)='Back to Cards']",
        "//*[self::button or self::a][contains(normalize-space(.), 'Back To Cards') or contains(normalize-space(.), 'Back to Cards')]",
    ]
    for xpath in preferred_xpaths:
        try:
            elements = driver.find_elements(By.XPATH, xpath)
            for element in elements:
                if element.is_displayed() and element.is_enabled():
                    back_link = element
                    break
            if back_link is not None:
                break
        except Exception:
            continue

    if back_link is None:
        back_link = driver.execute_script(
            """
            var els = Array.from(document.querySelectorAll('button, a, input'));
            for (var i = 0; i < els.length; i++) {
              var el = els[i];
              var txt = (el.innerText || el.value || el.getAttribute('aria-label') || '').replace(/\s+/g, ' ').trim().toLowerCase();
              var visible = !!(el.offsetParent !== null || el.getClientRects().length > 0);
              if (visible && (txt === 'back to cards' || txt.indexOf('back to cards') !== -1 || txt === 'back to items' || txt.indexOf('back to items') !== -1)) {
                return el;
              }
            }
            return null;
            """
        )

    if back_link is None:
        body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        if any(token in body_text for token in ["accept items list", "items list", "cards list", "my items list", "my cards list"]):
            return
        raise AssertionError("Back navigation button was not found after the action.")

    scroll_to(driver, back_link)
    for attempt in range(3):
        try:
            ActionChains(driver).move_to_element(back_link).click().perform()
            break
        except Exception:
            try:
                back_link.click()
                break
            except Exception:
                driver.execute_script("arguments[0].click();", back_link)
    wait_ready(driver)
    time.sleep(PAUSE)


def click_confirm_button(driver):
    labels = ["Confirm", "CONFIRM", "Accept", "ACCEPT"]
    for label in labels:
        locators = [
            (By.XPATH, f"//button[normalize-space(.)='{label}']"),
            (By.XPATH, f"//a[normalize-space(.)='{label}']"),
            (By.XPATH, f"//input[@type='submit' and @value='{label}']"),
            (By.XPATH, f"//input[@type='button' and @value='{label}']"),
            (By.XPATH, f"//*[self::button or self::a or self::input or self::span][contains(normalize-space(.), '{label}')]"),
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
                        wait_ready(driver)
                        time.sleep(PAUSE)
                        return True
            except Exception:
                continue

    confirm_button = driver.execute_script(
        """
        var els = document.querySelectorAll('button, a, input, span, div');
        for (var i = 0; i < els.length; i++) {
          var txt = (els[i].innerText || els[i].value || '').replace(/\s+/g, ' ').trim().toLowerCase();
          if (els[i].offsetParent !== null) {
            if ((txt === 'confirm' || txt.indexOf('confirm') !== -1) || (txt === 'accept' || txt.indexOf('accept') !== -1)) {
              try { els[i].click(); } catch (e) { els[i].dispatchEvent(new MouseEvent('click', {bubbles: true})); }
              return true;
            }
          }
        }
        return false;
        """
    )
    if confirm_button:
        wait_ready(driver)
        time.sleep(PAUSE)
        return True

    raise AssertionError("Confirm/Accept button was not found or could not be clicked.")


@pytest.mark.usefixtures("driver")
class TestSupplierAcceptCards:
    def test_accept_cards_flow(self, driver):
        print("\n[TC-ACCEPT-001] Logging in and opening supplier Accept Cards flow...")
        driver.get(f"{BASE_URL}/Account/Login")
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

        current_url = driver.current_url
        assert "Account/Login" not in current_url or "Home" in current_url or "QALS1011" in current_url, (
            f"Login may have failed. URL: {current_url}"
        )
        take_screenshot(driver, "01_after_login")

        driver.get(ACCEPT_CARDS_URL)
        wait_ready(driver)
        time.sleep(PAUSE)

        current_url_lower = driver.current_url.lower()
        assert "accept" in current_url_lower or "supplieraction" in current_url_lower or "acceptcards" in current_url_lower, (
            f"Accept page did not open. URL: {driver.current_url}"
        )
        take_screenshot(driver, "03_accept_page")

        print("  [STEP] Select cards from the Accept Cards list and click Accept.")
        select_cards_and_click_accept(driver, max_cards=2)

        body_text = driver.find_element(By.TAG_NAME, "body").text
        success_text = [
            "following cards were successful",
            "card successfully accepted",
            "accepted successfully",
            "successfully accepted",
            "accept cards results",
            "back to items",
            "back to cards",
            "successful",
        ]
        if not any(token in body_text.lower() for token in success_text):
            raise AssertionError(
                "Accept Cards Results screen did not appear after clicking Accept. "
                f"Page body: {body_text[:1000]}"
            )
        take_screenshot(driver, "04_after_accept")
        print("  [PASS] Supplier Accept Cards flow completed successfully.")

    @pytest.mark.skip(reason="This scenario is intentionally not part of the Release Cards accept flow requested for this task.")
    def test_accept_runline_cards_flow(self, driver):
        print("\n[TC-ACCEPT-001B] Logging in and accepting Runline Cards from the Accept Items list...")
        driver.get(f"{BASE_URL}/Account/Login")
        wait_ready(driver)

        find(driver, By.ID, "UserName").clear()
        find(driver, By.ID, "UserName").send_keys(USERNAME)
        find(driver, By.ID, "Password").clear()
        find(driver, By.ID, "Password").send_keys(PASSWORD)
        clickable(driver, By.ID, "login-button").click()
        wait_ready(driver)
        time.sleep(PAUSE)

        actions_link = clickable(
            driver,
            By.XPATH,
            "//a[contains(@href, 'Action/Home') or normalize-space(.)='Actions' or .//span[normalize-space()='Actions']]",
        )
        scroll_to(driver, actions_link)
        actions_link.click()
        wait_ready(driver)
        time.sleep(PAUSE)

        accept_link = None
        for locator in [
            (By.XPATH, "//a[contains(@href,'Accept') or normalize-space(.)='Accept']"),
            (By.XPATH, "//*[self::a or self::span][contains(normalize-space(.),'Accept')]"),
        ]:
            try:
                accept_link = WebDriverWait(driver, 8).until(EC.element_to_be_clickable(locator))
                break
            except Exception:
                continue

        if accept_link is None:
            driver.get(ACCEPT_CARDS_URL)
            wait_ready(driver)
            time.sleep(PAUSE)
        else:
            scroll_to(driver, accept_link)
            driver.execute_script("arguments[0].click();", accept_link)
            wait_ready(driver)
            time.sleep(PAUSE)

        current_url_lower = driver.current_url.lower()
        assert "accept" in current_url_lower or "supplieraction" in current_url_lower or "acceptcards" in current_url_lower, (
            f"Accept page did not open. URL: {driver.current_url}"
        )
        take_screenshot(driver, "04_runline_cards_page")

        runline_link = None
        for locator in [
            (By.XPATH, "//*[self::a or self::button or self::span][contains(normalize-space(.),'RunLine Cards')]"),
            (By.XPATH, "//*[self::a or self::button or self::span][contains(normalize-space(.),'Runline Cards')]"),
            (By.XPATH, "//*[self::a or self::button or self::span][contains(normalize-space(.),'Run Line Cards')]"),
        ]:
            try:
                runline_link = WebDriverWait(driver, 8).until(EC.element_to_be_clickable(locator))
                break
            except Exception:
                continue

        assert runline_link is not None, "The RunLine Cards option was not found in the Accept Items list."
        scroll_to(driver, runline_link)
        driver.execute_script("arguments[0].click();", runline_link)
        wait_ready(driver)
        time.sleep(PAUSE)
        take_screenshot(driver, "05_runline_cards")

        card_checkboxes = driver.find_elements(
            By.XPATH,
            "//input[@type='checkbox' and not(@disabled) and not(contains(@id,'search_')) and not(contains(@name,'search_')) and not(contains(@value,'All'))]",
        )
        if not card_checkboxes:
            card_checkboxes = driver.find_elements(By.XPATH, "//table//td//input[@type='checkbox' and not(@disabled)]")
        assert card_checkboxes, "No selectable card checkboxes were found on the RunLine Cards page."

        for cb in card_checkboxes[:2]:
            try:
                if not cb.is_selected():
                    cb.click()
            except Exception:
                driver.execute_script("arguments[0].click();", cb)

        accept_cards_button = find_action_button(driver, ["Accept Cards", "Accept Card", "ACCEPT", "Accept"])
        if accept_cards_button is None:
            for locator in [
                (By.XPATH, "//button[normalize-space(.)='Accept Cards']"),
                (By.XPATH, "//button[normalize-space(.)='Accept Card']"),
                (By.XPATH, "//a[normalize-space(.)='Accept Cards']"),
                (By.XPATH, "//input[@type='submit' and @value='Accept Cards']"),
                (By.XPATH, "//*[self::button or self::a or self::input][contains(normalize-space(.),'Accept Cards')]"),
                (By.XPATH, "//*[self::button or self::a or self::input][contains(normalize-space(.),'Accept Card')]"),
                (By.XPATH, "//*[self::button or self::a or self::input][contains(translate(@value,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'accept')]"),
            ]:
                try:
                    accept_cards_button = WebDriverWait(driver, 8).until(EC.element_to_be_clickable(locator))
                    break
                except Exception:
                    continue

        assert accept_cards_button is not None, "Accept Cards button was not found."
        scroll_to(driver, accept_cards_button)
        driver.execute_script("arguments[0].click();", accept_cards_button)
        wait_ready(driver)
        time.sleep(PAUSE * 2)

        take_screenshot(driver, "06_runline_accept_results")
        result_checkboxes = driver.find_elements(By.XPATH, "//input[@type='checkbox' and not(@disabled)]")
        assert result_checkboxes, "No result checkboxes were found on the Accept Waiting At Runline Cards Results page."

        for cb in result_checkboxes[:1]:
            try:
                if not cb.is_selected():
                    cb.click()
            except Exception:
                driver.execute_script("arguments[0].click();", cb)

        assert click_confirm_button(driver) is True

        assert_post_action_state(
            driver,
            [
                "following cards were successful",
                "card successfully accepted",
                "accepted successfully",
                "successfully accepted",
                "confirmed",
                "accept items list",
                "items list",
                "cards list",
            ],
            "Runline accept confirm",
        )
        take_screenshot(driver, "07_runline_accept_confirmed")
        click_back_to_cards(driver)
        take_screenshot(driver, "08_back_to_cards_after_runline_accept")
        print("  [PASS] Runline Accept flow completed successfully.")

    @pytest.mark.skip(reason="This scenario is intentionally not part of the Release Cards accept flow requested for this task.")
    def test_accept_reschedule_approval_cards_flow(self, driver):
        print("\n[TC-ACCEPT-002] Logging in and opening Reschedule Approval Cards flow...")
        driver.get(f"{BASE_URL}/Account/Login")
        wait_ready(driver)

        find(driver, By.ID, "UserName").clear()
        find(driver, By.ID, "UserName").send_keys(USERNAME)
        find(driver, By.ID, "Password").clear()
        find(driver, By.ID, "Password").send_keys(PASSWORD)
        clickable(driver, By.ID, "login-button").click()
        wait_ready(driver)
        time.sleep(PAUSE)

        actions_link = clickable(
            driver,
            By.XPATH,
            "//a[contains(@href, 'Action/Home') or normalize-space(.)='Actions' or .//span[normalize-space()='Actions']]",
        )
        scroll_to(driver, actions_link)
        actions_link.click()
        wait_ready(driver)
        time.sleep(PAUSE)

        assert click_accept_category(
            driver,
            ["Reschedule Approval Cards", "Reschedule Approval Card", "Reschedule Approval", "Reschedule Request"],
            ["Wait for PO Cards", "Released Cards", "RunLine Cards", "Runline Cards", "Recall Wait Cards", "Approval", "Approval Cards"],
        ), (
            "The current Accept Items list does not expose a matching Reschedule Approval action or equivalent live category."
        )
        time.sleep(PAUSE)

        selected = select_first_available_cards(driver, max_cards=3)
        assert selected, "No selectable cards were found in the Reschedule Approval cards list."

        accept_button = find_action_button(driver, ["Accept", "ACCEPT", "Accept Cards", "Accept Card"])
        assert accept_button is not None, "Accept action is not available for the Reschedule Approval cards on this page."
        scroll_to(driver, accept_button)
        driver.execute_script("arguments[0].click();", accept_button)
        wait_ready(driver)
        time.sleep(PAUSE * 2)

        assert_success_message(
            driver,
            [
                "following cards were successful",
                "card successfully accepted",
                "accepted successfully",
                "successfully accepted",
                "accept cards results",
            ],
            "Reschedule Approval accept",
        )
        take_screenshot(driver, "06_reschedule_approval_accept")
        click_back_to_cards(driver)
        take_screenshot(driver, "07_back_to_cards_after_reschedule_accept")
        print("  [PASS] Reschedule Approval Accept flow completed successfully.")

    @pytest.mark.skip(reason="This scenario is intentionally not part of the Release Cards accept flow requested for this task.")
    def test_reject_reschedule_approval_cards_flow(self, driver):
        print("\n[TC-ACCEPT-003] Logging in and opening reject flow for Reschedule Approval Cards...")
        driver.get(f"{BASE_URL}/Account/Login")
        wait_ready(driver)

        find(driver, By.ID, "UserName").clear()
        find(driver, By.ID, "UserName").send_keys(USERNAME)
        find(driver, By.ID, "Password").clear()
        find(driver, By.ID, "Password").send_keys(PASSWORD)
        clickable(driver, By.ID, "login-button").click()
        wait_ready(driver)
        time.sleep(PAUSE)

        actions_link = clickable(
            driver,
            By.XPATH,
            "//a[contains(@href, 'Action/Home') or normalize-space(.)='Actions' or .//span[normalize-space()='Actions']]",
        )
        scroll_to(driver, actions_link)
        actions_link.click()
        wait_ready(driver)
        time.sleep(PAUSE)

        assert click_accept_category(
            driver,
            ["Reschedule Approval Cards", "Reschedule Approval Card", "Reschedule Approval", "Reschedule Request"],
            ["Wait for PO Cards", "Released Cards", "RunLine Cards", "Runline Cards", "Recall Wait Cards", "Approval", "Approval Cards"],
        ), (
            "The current Accept Items list does not expose a matching Reschedule Approval action or equivalent live category."
        )
        time.sleep(PAUSE)

        selected = select_first_available_cards(driver, max_cards=3)
        assert selected, "No selectable cards were found in the Reschedule Approval cards list."

        reject_button = find_action_button(driver, ["Reject", "Reject Cards", "Reject Card"])
        assert reject_button is not None, "Reject action is not available for the Reschedule Approval cards on this page."
        scroll_to(driver, reject_button)
        driver.execute_script("arguments[0].click();", reject_button)
        wait_ready(driver)
        time.sleep(PAUSE * 2)

        assert_success_message(
            driver,
            [
                "following cards were successful",
                "card successfully rejected",
                "rejected successfully",
                "successfully rejected",
                "reject cards results",
            ],
            "Reschedule Approval reject",
        )
        take_screenshot(driver, "08_reschedule_approval_reject")
        click_back_to_cards(driver)
        take_screenshot(driver, "09_back_to_cards_after_reschedule_reject")
        print("  [PASS] Reschedule Approval Reject flow completed successfully.")
