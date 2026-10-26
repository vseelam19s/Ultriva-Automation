import os
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config.config import EXPLICIT_WAIT, SCREENSHOT_DIR


class BasePage:
    """Base page with common actions for all pages."""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, EXPLICIT_WAIT)

    def find_element(self, by, value):
        return self.wait.until(EC.presence_of_element_located((by, value)))

    def find_elements(self, by, value):
        return self.driver.find_elements(by, value)

    def click(self, by, value):
        element = self.wait.until(EC.element_to_be_clickable((by, value)))
        element.click()

    def type_text(self, by, value, text):
        element = self.find_element(by, value)
        element.clear()
        element.send_keys(text)

    def get_text(self, by, value):
        return self.find_element(by, value).text

    def is_element_visible(self, by, value, timeout=5):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by, value))
            )
            return True
        except TimeoutException:
            return False

    def is_element_present(self, by, value, timeout=5):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return True
        except TimeoutException:
            return False

    def get_title(self):
        return self.driver.title

    def get_url(self):
        return self.driver.current_url

    def take_screenshot(self, name):
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        path = os.path.join(SCREENSHOT_DIR, f"{name}_{timestamp}.png")
        self.driver.save_screenshot(path)
        return path

    def wait_for_page_load(self):
        self.wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
