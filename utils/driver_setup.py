from selenium import webdriver
from config.config import BROWSER, HEADLESS, IMPLICIT_WAIT, PAGE_LOAD_TIMEOUT


def get_driver():
    """Create and return a configured WebDriver instance.

    Uses Selenium's built-in Selenium Manager (bundled since Selenium 4.6)
    to automatically locate or download the correct browser driver — no
    third-party webdriver-manager needed.
    """
    browser = BROWSER.lower()

    if browser == "chrome":
        options = webdriver.ChromeOptions()
        # Remove headless for visible UI
        # options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        driver = webdriver.Chrome(options=options)

    elif browser == "firefox":
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")
        options.add_argument("--width=1920")
        options.add_argument("--height=1080")
        driver = webdriver.Firefox(options=options)

    elif browser == "edge":
        options = webdriver.EdgeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")
        driver = webdriver.Edge(options=options)

    else:
        raise ValueError(f"Unsupported browser: {browser}. Use chrome, firefox, or edge.")

    driver.implicitly_wait(IMPLICIT_WAIT)
    driver.set_page_load_timeout(max(PAGE_LOAD_TIMEOUT, 120))
    # Do not maximize window in headless mode
    return driver
