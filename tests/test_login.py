"""
Test Suite: Login / Authentication
"""

import pytest
from pages.login_page import LoginPage
from config.config import USERNAME, PASSWORD, LOGIN_URL, BASE_URL


class TestLogin:

    # TC-001 ─────────────────────────────────────────────────────────────────
    def test_login_page_loads(self, driver, reporter):
        """Verify the login page loads and has the expected title / URL."""
        record_id = "TC-001"
        try:
            login_page = LoginPage(driver)
            login_page.open()

            url   = login_page.get_url()
            title = login_page.get_title()

            assert login_page.is_element_present(*LoginPage.USERNAME_INPUT), \
                "Username field not found on login page"
            assert login_page.is_element_present(*LoginPage.PASSWORD_INPUT), \
                "Password field not found on login page"

            reporter.add_result(
                test_id   = record_id,
                test_name = "Login page loads with username and password fields",
                module    = "Authentication",
                status    = "PASS",
                error_msg = "",
                screenshot = login_page.take_screenshot(record_id),
            )
        except Exception as e:
            reporter.add_result(
                test_id   = record_id,
                test_name = "Login page loads with username and password fields",
                module    = "Authentication",
                status    = "FAIL",
                error_msg = str(e),
                screenshot = LoginPage(driver).take_screenshot(f"{record_id}_fail"),
            )
            pytest.fail(str(e))

    # TC-002 ─────────────────────────────────────────────────────────────────
    def test_valid_login(self, driver, reporter):
        """Log in with valid credentials and verify successful authentication."""
        record_id = "TC-002"
        try:
            login_page = LoginPage(driver)
            login_page.login(USERNAME, PASSWORD)

            assert login_page.is_logged_in(), \
                "Login failed — logout link / dashboard element not found after login"

            reporter.add_result(
                test_id   = record_id,
                test_name = "Valid login with buyeruser / Ultriva!23",
                module    = "Authentication",
                status    = "PASS",
                screenshot = login_page.take_screenshot(record_id),
            )
        except Exception as e:
            reporter.add_result(
                test_id   = record_id,
                test_name = "Valid login with buyeruser / Ultriva!23",
                module    = "Authentication",
                status    = "FAIL",
                error_msg = str(e),
                screenshot = LoginPage(driver).take_screenshot(f"{record_id}_fail"),
            )
            pytest.fail(str(e))

    # TC-003 ─────────────────────────────────────────────────────────────────
    def test_invalid_username(self, driver, reporter):
        """Login with wrong username should stay on login page / show error."""
        record_id = "TC-003"
        try:
            login_page = LoginPage(driver)
            login_page.login("wrong_user_xyz", PASSWORD)

            assert not login_page.is_logged_in(), \
                "Login should have failed for invalid username but succeeded"

            reporter.add_result(
                test_id   = record_id,
                test_name = "Login rejected for invalid username",
                module    = "Authentication",
                status    = "PASS",
                screenshot = login_page.take_screenshot(record_id),
            )
        except Exception as e:
            reporter.add_result(
                test_id   = record_id,
                test_name = "Login rejected for invalid username",
                module    = "Authentication",
                status    = "FAIL",
                error_msg = str(e),
                screenshot = LoginPage(driver).take_screenshot(f"{record_id}_fail"),
            )
            pytest.fail(str(e))

    # TC-004 ─────────────────────────────────────────────────────────────────
    def test_invalid_password(self, driver, reporter):
        """Login with wrong password should stay on login page / show error."""
        record_id = "TC-004"
        try:
            login_page = LoginPage(driver)
            login_page.login(USERNAME, "WrongPass!99")

            assert not login_page.is_logged_in(), \
                "Login should have failed for invalid password but succeeded"

            reporter.add_result(
                test_id   = record_id,
                test_name = "Login rejected for invalid password",
                module    = "Authentication",
                status    = "PASS",
                screenshot = login_page.take_screenshot(record_id),
            )
        except Exception as e:
            reporter.add_result(
                test_id   = record_id,
                test_name = "Login rejected for invalid password",
                module    = "Authentication",
                status    = "FAIL",
                error_msg = str(e),
                screenshot = LoginPage(driver).take_screenshot(f"{record_id}_fail"),
            )
            pytest.fail(str(e))

    # TC-005 ─────────────────────────────────────────────────────────────────
    def test_empty_credentials(self, driver, reporter):
        """Submitting blank credentials should not log the user in."""
        record_id = "TC-005"
        try:
            login_page = LoginPage(driver)
            login_page.open()
            login_page.click_login()

            assert not login_page.is_logged_in(), \
                "Login should have failed for empty credentials but succeeded"

            reporter.add_result(
                test_id   = record_id,
                test_name = "Login rejected for empty credentials",
                module    = "Authentication",
                status    = "PASS",
                screenshot = login_page.take_screenshot(record_id),
            )
        except Exception as e:
            reporter.add_result(
                test_id   = record_id,
                test_name = "Login rejected for empty credentials",
                module    = "Authentication",
                status    = "FAIL",
                error_msg = str(e),
                screenshot = LoginPage(driver).take_screenshot(f"{record_id}_fail"),
            )
            pytest.fail(str(e))

    # TC-006 ─────────────────────────────────────────────────────────────────
    def test_logout(self, driver, reporter):
        """After login, clicking Logout should end the session."""
        record_id = "TC-006"
        try:
            login_page = LoginPage(driver)
            login_page.login(USERNAME, PASSWORD)
            assert login_page.is_logged_in(), "Pre-condition: login must succeed before testing logout"

            login_page.logout()

            # After logout user should be back at the login page
            assert login_page.is_element_present(*LoginPage.USERNAME_INPUT, timeout=10), \
                "Username input not visible after logout — user may still be logged in"

            reporter.add_result(
                test_id   = record_id,
                test_name = "Logout redirects back to login page",
                module    = "Authentication",
                status    = "PASS",
                screenshot = login_page.take_screenshot(record_id),
            )
        except Exception as e:
            reporter.add_result(
                test_id   = record_id,
                test_name = "Logout redirects back to login page",
                module    = "Authentication",
                status    = "FAIL",
                error_msg = str(e),
                screenshot = LoginPage(driver).take_screenshot(f"{record_id}_fail"),
            )
            pytest.fail(str(e))

    # TC-007 ─────────────────────────────────────────────────────────────────
    def test_page_title_not_empty(self, driver, reporter):
        """Login page should have a non-empty browser title."""
        record_id = "TC-007"
        try:
            login_page = LoginPage(driver)
            login_page.open()
            title = login_page.get_title()
            assert title and title.strip(), "Page title is empty"

            reporter.add_result(
                test_id   = record_id,
                test_name = f"Login page has title: {title}",
                module    = "Authentication",
                status    = "PASS",
                screenshot = login_page.take_screenshot(record_id),
            )
        except Exception as e:
            reporter.add_result(
                test_id   = record_id,
                test_name = "Login page has a non-empty title",
                module    = "Authentication",
                status    = "FAIL",
                error_msg = str(e),
                screenshot = LoginPage(driver).take_screenshot(f"{record_id}_fail"),
            )
            pytest.fail(str(e))