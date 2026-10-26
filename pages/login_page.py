from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from config.config import LOGIN_URL


class LoginPage(BasePage):
    """Page Object for Login page."""

    # Locators — verified against live site DOM
    USERNAME_INPUT  = (By.ID,    "UserName")
    PASSWORD_INPUT  = (By.ID,    "Password")
    LOGIN_BUTTON    = (By.ID,    "login-button")
    ERROR_MESSAGE   = (By.ID,    "inner-alerts-container")
    AVATAR_DROPDOWN = (By.XPATH, "//button[contains(@class,'avatar-btn') or contains(@class,'dropdown-toggle')]")
    LOGOUT_LINK     = (By.XPATH, "//a[contains(@href,'Account/Logout') or contains(@href,'account/logout')]")
    WELCOME_TEXT    = (By.XPATH, "//*[contains(@class,'vertical-nav') or contains(@class,'main-content')]")

    def open(self):
        self.driver.get(LOGIN_URL)
        self.wait_for_page_load()

    def enter_username(self, username):
        self.type_text(*self.USERNAME_INPUT, username)

    def enter_password(self, password):
        self.type_text(*self.PASSWORD_INPUT, password)

    def click_login(self):
        self.click(*self.LOGIN_BUTTON)

    def login(self, username, password):
        self.open()
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()
        self.wait_for_page_load()

    def get_error_message(self):
        if self.is_element_visible(*self.ERROR_MESSAGE):
            return self.get_text(*self.ERROR_MESSAGE)
        return None

    def is_logged_in(self):
        """Check if login was successful by looking for logout link or dashboard."""
        return (
            self.is_element_present(*self.LOGOUT_LINK, timeout=8)
            or self.is_element_present(*self.WELCOME_TEXT, timeout=8)
        )

    def logout(self):
        # Logout is inside the avatar dropdown — open it first
        if self.is_element_present(*self.AVATAR_DROPDOWN, timeout=8):
            self.click(*self.AVATAR_DROPDOWN)
        if self.is_element_present(*self.LOGOUT_LINK, timeout=8):
            self.click(*self.LOGOUT_LINK)
            self.wait_for_page_load()
