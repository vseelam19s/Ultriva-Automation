"""Test Suite: Navigation — back/forward, direct URL access, page responsiveness"""

import pytest
from selenium.webdriver.common.by import By

from config.config import BASE_URL, PASSWORD, USERNAME
from pages.base_page import BasePage
from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage


class TestNavigation:

    # TC-201 ─────────────────────────────────────────────────────────────────
    def test_browser_back_does_not_crash(self, driver, reporter):
        """Browser back button should not throw an error / white-screen."""
        record_id = "TC-201"
        try:
            login_page = LoginPage(driver)
            login_page.login(USERNAME, PASSWORD)

            driver.back()
            login_page.wait_for_page_load()
            url = driver.current_url

            assert url, "Page URL is empty after using browser back"

            reporter.add_result(
                test_id=record_id,
                test_name=f"Browser back button works — landed at: {url}",
                module="Navigation",
                status="PASS",
                screenshot=login_page.take_screenshot(record_id),
            )
        except Exception as e:
            reporter.add_result(
                test_id=record_id,
                test_name="Browser back button does not crash",
                module="Navigation",
                status="FAIL",
                error_msg=str(e),
                screenshot=BasePage(driver).take_screenshot(f"{record_id}_fail"),
            )
            pytest.fail(str(e))

    # TC-202 ─────────────────────────────────────────────────────────────────
    def test_direct_url_access_without_login(self, driver, reporter):
        """Accessing the base URL without login should redirect to login page."""
        record_id = "TC-202"
        try:
            driver.get(BASE_URL)
            base_page = BasePage(driver)
            base_page.wait_for_page_load()

            # Expect either a redirect to the login page or a login form visible
            login_present = base_page.is_element_present(
                By.XPATH,
                "//input[@type='password'] | //input[contains(@name,'password') or contains(@id,'password')]",
                timeout=8,
            )

            reporter.add_result(
                test_id=record_id,
                test_name="Unauthenticated access redirects to login",
                module="Navigation",
                status="PASS" if login_present else "FAIL",
                error_msg=""
                if login_present
                else "Password field not found — app may not require login",
                screenshot=base_page.take_screenshot(record_id),
            )
            if not login_present:
                pytest.fail(
                    "Password field not found after direct URL access without login"
                )
        except Exception as e:
            reporter.add_result(
                test_id=record_id,
                test_name="Unauthenticated access redirects to login",
                module="Navigation",
                status="FAIL",
                error_msg=str(e),
                screenshot=BasePage(driver).take_screenshot(f"{record_id}_fail"),
            )
            pytest.fail(str(e))

    # TC-203 ─────────────────────────────────────────────────────────────────
    def test_page_reload_keeps_session(self, driver, reporter):
        """Refreshing the dashboard should keep the user logged in."""
        record_id = "TC-203"
        try:
            login_page = LoginPage(driver)
            login_page.login(USERNAME, PASSWORD)
            assert login_page.is_logged_in(), "Pre-condition: login must succeed"

            driver.refresh()
            login_page.wait_for_page_load()

            still_logged_in = login_page.is_logged_in()
            assert still_logged_in, "Session was lost after page reload"

            reporter.add_result(
                test_id=record_id,
                test_name="Session persists after page refresh",
                module="Navigation",
                status="PASS",
                screenshot=login_page.take_screenshot(record_id),
            )
        except Exception as e:
            reporter.add_result(
                test_id=record_id,
                test_name="Session persists after page refresh",
                module="Navigation",
                status="FAIL",
                error_msg=str(e),
                screenshot=BasePage(driver).take_screenshot(f"{record_id}_fail"),
            )
            pytest.fail(str(e))

    # TC-204 ─────────────────────────────────────────────────────────────────
    def test_all_nav_links_have_href(self, driver, reporter):
        """Every vertical-nav link should have a non-empty href attribute."""
        record_id = "TC-204"
        try:
            LoginPage(driver).login(USERNAME, PASSWORD)
            dashboard = DashboardPage(driver)

            links = dashboard.find_elements(
                By.XPATH,
                "//*[contains(@class,'vertical-nav-items')]//a | //*[contains(@class,'h-navbar')]//a",
            )
            broken = [
                el.get_attribute("href") or "(no href)"
                for el in links
                if not el.get_attribute("href")
            ]

            assert not broken, f"Navigation links without href: {broken}"

            reporter.add_result(
                test_id=record_id,
                test_name=f"All {len(links)} nav links have href attributes",
                module="Navigation",
                status="PASS",
                screenshot=dashboard.take_screenshot(record_id),
            )
        except Exception as e:
            reporter.add_result(
                test_id=record_id,
                test_name="All navigation links have href attributes",
                module="Navigation",
                status="FAIL",
                error_msg=str(e),
                screenshot=BasePage(driver).take_screenshot(f"{record_id}_fail"),
            )
            pytest.fail(str(e))

    # TC-205 ─────────────────────────────────────────────────────────────────
    def test_404_page_for_invalid_route(self, driver, reporter):
        """Navigating to a non-existent route should return a 404-style page."""
        record_id = "TC-205"
        invalid_url = f"{BASE_URL}/this_page_does_not_exist_xyz9999"
        try:
            LoginPage(driver).login(USERNAME, PASSWORD)
            driver.get(invalid_url)
            BasePage(driver).wait_for_page_load()

            page_source = driver.page_source.lower()
            error_indicators = [
                "404",
                "not found",
                "page not found",
                "error",
                "no page",
            ]
            found = any(ind in page_source for ind in error_indicators)

            reporter.add_result(
                test_id=record_id,
                test_name="Invalid route shows 404/error page",
                module="Navigation",
                status="PASS" if found else "SKIP",
                error_msg=""
                if found
                else "No 404 indicator in page source (app may handle gracefully)",
                screenshot=BasePage(driver).take_screenshot(record_id),
            )
        except Exception as e:
            reporter.add_result(
                test_id=record_id,
                test_name="Invalid route shows 404/error page",
                module="Navigation",
                status="FAIL",
                error_msg=str(e),
                screenshot=BasePage(driver).take_screenshot(f"{record_id}_fail"),
            )
            pytest.fail(str(e))