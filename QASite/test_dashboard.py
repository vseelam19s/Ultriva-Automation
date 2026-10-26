"""
Test Suite: Dashboard — page load, navigation, basic UI elements
"""

import pytest

from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from config.config import USERNAME, PASSWORD


class TestDashboard:
        # TC-101 ─────────────────────────────────────────────────────────────────
        def test_dashboard_loads_after_login(self, driver, reporter):
                """Dashboard page should load successfully after valid login."""
                record_id = "TC-101"
                try:
                        login_page = LoginPage(driver)
                        login_page.login(USERNAME, PASSWORD)

                        dashboard = DashboardPage(driver)
                        assert dashboard.is_loaded(), "Dashboard did not load after login"

                        reporter.add_result(
                                test_id=record_id,
                                test_name="Dashboard loads after valid login",
                                module="Dashboard",
                                status="PASS",
                                screenshot=dashboard.take_screenshot(record_id),
                        )
                except Exception as e:
                        reporter.add_result(
                                test_id=record_id,
                                test_name="Dashboard loads after valid login",
                                module="Dashboard",
                                status="FAIL",
                                error_msg=str(e),
                                screenshot=DashboardPage(driver).take_screenshot(f"{record_id}_fail"),
                        )
                        pytest.fail(str(e))

        # TC-102 ─────────────────────────────────────────────────────────────────
        def test_navigation_menu_present(self, driver, reporter):
                """A navigation menu should be visible on the dashboard."""
                record_id = "TC-102"
                try:
                        LoginPage(driver).login(USERNAME, PASSWORD)
                        dashboard = DashboardPage(driver)

                        assert dashboard.has_navigation_menu(), "Navigation menu not found on dashboard"

                        reporter.add_result(
                                test_id=record_id,
                                test_name="Navigation menu is present on dashboard",
                                module="Dashboard",
                                status="PASS",
                                screenshot=dashboard.take_screenshot(record_id),
                        )
                except Exception as e:
                        reporter.add_result(
                                test_id=record_id,
                                test_name="Navigation menu is present on dashboard",
                                module="Dashboard",
                                status="FAIL",
                                error_msg=str(e),
                                screenshot=DashboardPage(driver).take_screenshot(f"{record_id}_fail"),
                        )
                        pytest.fail(str(e))

        # TC-103 ─────────────────────────────────────────────────────────────────
        def test_page_url_changes_after_login(self, driver, reporter):
                """URL after login should differ from the login URL."""
                record_id = "TC-103"
                try:
                        login_page = LoginPage(driver)
                        login_page.open()
                        login_url = login_page.get_url()
                        login_page.login(USERNAME, PASSWORD)

                        dashboard = DashboardPage(driver)
                        post_login_url = dashboard.get_url()

                        assert post_login_url != login_url, (
                                f"URL did not change after login: still at {post_login_url}"
                        )

                        reporter.add_result(
                                test_id=record_id,
                                test_name=f"URL changes after login to: {post_login_url}",
                                module="Dashboard",
                                status="PASS",
                                screenshot=dashboard.take_screenshot(record_id),
                        )
                except Exception as e:
                        reporter.add_result(
                                test_id=record_id,
                                test_name="URL changes after login",
                                module="Dashboard",
                                status="FAIL",
                                error_msg=str(e),
                                screenshot=DashboardPage(driver).take_screenshot(f"{record_id}_fail"),
                        )
                        pytest.fail(str(e))

        # TC-104 ─────────────────────────────────────────────────────────────────
        def test_page_header_visible(self, driver, reporter):
                """Dashboard must show main content area (app uses icon nav, no h1/h2 heading)."""
                record_id = "TC-104"
                try:
                        LoginPage(driver).login(USERNAME, PASSWORD)
                        dashboard = DashboardPage(driver)

                        # The app uses a vertical icon nav, no h1/h2; verify main content loaded.
                        main_loaded = dashboard.is_element_present(*DashboardPage.MAIN_CONTENT, timeout=10)
                        assert main_loaded, "Main content area not found on dashboard"

                        header = dashboard.get_page_header()
                        label = (
                                f"main-content visible (header='{header}')"
                                if header
                                else "main-content area visible"
                        )

                        reporter.add_result(
                                test_id=record_id,
                                test_name=label,
                                module="Dashboard",
                                status="PASS",
                                screenshot=dashboard.take_screenshot(record_id),
                        )
                except Exception as e:
                        reporter.add_result(
                                test_id=record_id,
                                test_name="Dashboard main content area is visible",
                                module="Dashboard",
                                status="FAIL",
                                error_msg=str(e),
                                screenshot=DashboardPage(driver).take_screenshot(f"{record_id}_fail"),
                        )
                        pytest.fail(str(e))

        # TC-105 ─────────────────────────────────────────────────────────────────
        def test_menu_items_not_empty(self, driver, reporter):
                """Vertical navigation should contain at least one link (icon-based nav)."""
                record_id = "TC-105"
                try:
                        LoginPage(driver).login(USERNAME, PASSWORD)
                        dashboard = DashboardPage(driver)
                        items = dashboard.get_menu_items()

                        assert len(items) > 0, "No navigation links found in vertical-nav"

                        reporter.add_result(
                                test_id=record_id,
                                test_name=f"Vertical nav has {len(items)} link(s)",
                                module="Dashboard",
                                status="PASS",
                                screenshot=dashboard.take_screenshot(record_id),
                        )
                except Exception as e:
                        reporter.add_result(
                                test_id=record_id,
                                test_name="Navigation menu links are populated",
                                module="Dashboard",
                                status="FAIL",
                                error_msg=str(e),
                                screenshot=DashboardPage(driver).take_screenshot(f"{record_id}_fail"),
                        )
                        pytest.fail(str(e))

        # TC-106 ─────────────────────────────────────────────────────────────────
        def test_footer_present(self, driver, reporter):
                """Logout button (user session toolbar) should be visible on every page."""
                record_id = "TC-106"
                try:
                        LoginPage(driver).login(USERNAME, PASSWORD)
                        dashboard = DashboardPage(driver)

                        # The app has no traditional footer; verify the logout/session button exists.
                        assert dashboard.has_footer(), (
                                "Logout/session button not found — page chrome may be missing"
                        )

                        reporter.add_result(
                                test_id=record_id,
                                test_name="Logout button (session toolbar) is present",
                                module="Dashboard",
                                status="PASS",
                                screenshot=dashboard.take_screenshot(record_id),
                        )
                except Exception as e:
                        reporter.add_result(
                                test_id=record_id,
                                test_name="Logout button (session toolbar) is present",
                                module="Dashboard",
                                status="FAIL",
                                error_msg=str(e),
                                screenshot=DashboardPage(driver).take_screenshot(f"{record_id}_fail"),
                        )
                        pytest.fail(str(e))

        # TC-107 ─────────────────────────────────────────────────────────────────
        def test_dashboard_title_not_empty(self, driver, reporter):
                """Browser tab title after login should be non-empty."""
                record_id = "TC-107"
                try:
                        LoginPage(driver).login(USERNAME, PASSWORD)
                        dashboard = DashboardPage(driver)
                        title = dashboard.get_title()

                        assert title and title.strip(), "Browser title is empty after login"

                        reporter.add_result(
                                test_id=record_id,
                                test_name=f"Dashboard browser title: '{title}'",
                                module="Dashboard",
                                status="PASS",
                                screenshot=dashboard.take_screenshot(record_id),
                        )
                except Exception as e:
                        reporter.add_result(
                                test_id=record_id,
                                test_name="Dashboard browser title is non-empty",
                                module="Dashboard",
                                status="FAIL",
                                error_msg=str(e),
                                screenshot=DashboardPage(driver).take_screenshot(f"{record_id}_fail"),
                        )
                        pytest.fail(str(e))