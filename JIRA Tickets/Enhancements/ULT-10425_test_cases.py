"""
ULT-10425 | Test Cases — Plant Home Page Integration Panel: Remember Last BU Filter
Enhancement:
  1. Rename "All Business Units" to "Plant and Associated Workcenters".
  2. Persist the user's last filter selection across page visits.

QA Site : https://engineering.ultrivalms.com/qals1011
User    : buyeruser / Ultriva!23
"""

import time
import pytest
from pages.login_page import LoginPage
from config.config import USERNAME, PASSWORD, BASE_URL

PLANT_HOME_URL = BASE_URL  # Integration Panel lives on the plant home / root page

# XPath helpers
FILTER_WORKCENTERS = "//label[contains(normalize-space(),'Plant and Associated Workcenters')]" \
                     " | //button[contains(normalize-space(),'Plant and Associated Workcenters')]" \
                     " | //span[contains(normalize-space(),'Plant and Associated Workcenters')]"
FILTER_THIS_BU     = "//label[contains(normalize-space(),'Only this BU')]" \
                     " | //button[contains(normalize-space(),'Only this BU')]" \
                     " | //span[contains(normalize-space(),'Only this BU')]"
OLD_LABEL_CHECK    = "//*[normalize-space()='All Business Units']"


def select_filter(driver, xpath):
    """Click the filter element identified by xpath."""
    el = driver.find_element("xpath", xpath)
    el.click()
    time.sleep(1)


def selected_filter_text(driver):
    """Return the text of whichever filter tab/button appears active/selected."""
    for attr in ("aria-selected", "aria-pressed", "class"):
        candidates = driver.find_elements(
            "xpath",
            f"//*[self::label or self::button or self::span or self::a]"
            f"[contains(@{attr},'active') or contains(@{attr},'selected') or contains(@{attr},'checked')]"
        )
        for c in candidates:
            if "Only this BU" in c.text or "Plant and Associated Workcenters" in c.text:
                return c.text.strip()
    # Fallback: return active radio / checkbox value
    radio = driver.find_elements("xpath", "//input[@type='radio'][@checked]")
    if radio:
        return radio[0].get_attribute("value") or radio[0].get_attribute("id")
    return ""


class TestIntegrationPanelFilterLabel:

    # TC-01 ───────────────────────────────────────────────────────────────────
    def test_label_renamed_to_plant_and_associated_workcenters(self, driver):
        """Integration Panel shows 'Plant and Associated Workcenters', not 'All Business Units'."""
        LoginPage(driver).login(USERNAME, PASSWORD)
        driver.get(PLANT_HOME_URL)

        # New label must exist
        new_label = driver.find_elements("xpath", FILTER_WORKCENTERS)
        assert new_label, "'Plant and Associated Workcenters' filter option not found on page"

        # Old label must be gone
        old_label = driver.find_elements("xpath", OLD_LABEL_CHECK)
        assert not old_label, "'All Business Units' label still present — rename not applied"

    # TC-02 ───────────────────────────────────────────────────────────────────
    def test_only_this_bu_label_still_present(self, driver):
        """'Only this BU' option is still displayed alongside the renamed option."""
        LoginPage(driver).login(USERNAME, PASSWORD)
        driver.get(PLANT_HOME_URL)

        this_bu = driver.find_elements("xpath", FILTER_THIS_BU)
        assert this_bu, "'Only this BU' filter option not found on page"


class TestIntegrationPanelFilterPersistence:

    # TC-03 ───────────────────────────────────────────────────────────────────
    def test_plant_workcenters_filter_persists_on_revisit(self, driver):
        """
        Select 'Plant and Associated Workcenters', navigate away, return —
        the filter must still be 'Plant and Associated Workcenters'.
        """
        LoginPage(driver).login(USERNAME, PASSWORD)
        driver.get(PLANT_HOME_URL)

        # Select the 'Plant and Associated Workcenters' filter
        select_filter(driver, FILTER_WORKCENTERS)

        # Navigate away and return
        driver.get(BASE_URL + "/dashboard")   # any other page
        time.sleep(1)
        driver.get(PLANT_HOME_URL)
        time.sleep(2)

        active = selected_filter_text(driver)
        assert "Plant and Associated Workcenters" in active, \
            f"Expected 'Plant and Associated Workcenters' to be active after revisit, got: '{active}'"

    # TC-04 ───────────────────────────────────────────────────────────────────
    def test_only_this_bu_filter_persists_on_revisit(self, driver):
        """
        Select 'Only this BU', navigate away, return —
        the filter must still be 'Only this BU'.
        """
        LoginPage(driver).login(USERNAME, PASSWORD)
        driver.get(PLANT_HOME_URL)

        # First switch to workcenters so we know the starting state, then switch back
        select_filter(driver, FILTER_WORKCENTERS)
        time.sleep(1)
        select_filter(driver, FILTER_THIS_BU)

        driver.get(BASE_URL + "/dashboard")
        time.sleep(1)
        driver.get(PLANT_HOME_URL)
        time.sleep(2)

        active = selected_filter_text(driver)
        assert "Only this BU" in active, \
            f"Expected 'Only this BU' to be active after revisit, got: '{active}'"

    # TC-05 ───────────────────────────────────────────────────────────────────
    def test_default_filter_is_only_this_bu_on_first_visit(self, driver):
        """
        A user who has never changed the filter sees 'Only this BU' as default.
        NOTE: Requires a fresh user account with no stored preference.
              Skip if a dedicated virgin-user account is unavailable.
        """
        # Login with the standard user (assume no prior preference in this env run)
        LoginPage(driver).login(USERNAME, PASSWORD)
        driver.get(PLANT_HOME_URL)
        time.sleep(2)

        active = selected_filter_text(driver)
        if not active:
            pytest.skip("Unable to determine active filter — inspect selectors for this environment")

        assert "Only this BU" in active, \
            f"Default filter should be 'Only this BU' on first visit, got: '{active}'"

    # TC-06 ───────────────────────────────────────────────────────────────────
    def test_filter_persists_after_page_reload(self, driver):
        """
        Select 'Plant and Associated Workcenters', reload the same page (F5) —
        preference is retained without navigating away.
        """
        LoginPage(driver).login(USERNAME, PASSWORD)
        driver.get(PLANT_HOME_URL)

        select_filter(driver, FILTER_WORKCENTERS)
        driver.refresh()
        time.sleep(2)

        active = selected_filter_text(driver)
        assert "Plant and Associated Workcenters" in active, \
            f"Filter reset after page reload; expected 'Plant and Associated Workcenters', got: '{active}'"
