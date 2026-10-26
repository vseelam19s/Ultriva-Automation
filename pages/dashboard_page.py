from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class DashboardPage(BasePage):
    """Page Object for the Dashboard / Home page after login."""

    # Locators — verified against live site DOM
    PAGE_HEADER     = (By.XPATH, "//*[contains(@class,'page-title')] | //*[contains(@class,'section-header')] | //*[contains(@class,'panel-heading')] | //h1 | //h2 | //h3")
    NAV_MENU        = (By.XPATH, "//*[contains(@class,'vertical-nav')]")
    MENU_ITEMS      = (By.XPATH, "//*[contains(@class,'vertical-nav-items')]//a | //*[contains(@class,'h-navbar')]//a")
    FOOTER          = (By.XPATH, "//a[contains(@href,'Account/Logout')] | //*[contains(@class,'uplandsoftware') or contains(@href,'uplandsoftware')]")
    MAIN_CONTENT    = (By.XPATH, "//*[contains(@class,'main-content')]")
    SEARCH_INPUT    = (By.XPATH, "//input[@type='search'] | //input[contains(@placeholder,'Search') or contains(@name,'search')]")
    NOTIFICATIONS   = (By.XPATH, "//*[contains(@class,'notification') or contains(@class,'alert') or contains(@id,'notification')]")
    USER_PROFILE    = (By.XPATH, "//*[contains(@class,'profile') or contains(@class,'user-menu') or contains(@class,'avatar')]")

    def is_loaded(self):
        return (
            self.is_element_present(*self.PAGE_HEADER, timeout=10)
            or self.is_element_present(*self.NAV_MENU, timeout=10)
            or self.is_element_present(*self.MAIN_CONTENT, timeout=10)
        )

    def get_page_header(self):
        if self.is_element_visible(*self.PAGE_HEADER):
            return self.get_text(*self.PAGE_HEADER)
        return None

    def get_menu_items(self):
        elements = self.find_elements(*self.MENU_ITEMS)
        # Nav links use icon-only design; count links that have a real href
        return [el.get_attribute("href") or "" for el in elements
                if (el.get_attribute("href") or "").strip()]

    def has_navigation_menu(self):
        return self.is_element_present(*self.NAV_MENU)

    def has_footer(self):
        return self.is_element_present(*self.FOOTER)

    def has_search(self):
        return self.is_element_present(*self.SEARCH_INPUT)

    def get_notification_count(self):
        elements = self.find_elements(*self.NOTIFICATIONS)
        return len(elements)

    def is_profile_accessible(self):
        return self.is_element_present(*self.USER_PROFILE)
