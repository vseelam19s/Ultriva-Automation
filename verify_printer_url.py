"""Verify tk=$Printers works for the Printer entity page."""
import sys, os, time
sys.path.insert(0, os.path.abspath('.'))
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from utils.driver_setup import get_driver
from admin.UserGroup import login

driver = get_driver()
wait = WebDriverWait(driver, 20)
login(driver, wait)
base = 'https://engineering.ultrivalms.com/QALS1011'

url = base + '/Entity/List?tk=$Printers&busGID=BSU22ZAQALQG&A~1~ABC&'
driver.get(url)
time.sleep(3)
print('URL:', driver.current_url)
print('Title:', driver.title)
body = driver.find_element(By.TAG_NAME, 'body').text[:300].replace('\n', ' ')
print('Body:', body)

# Check if Add button exists
for el in driver.find_elements(By.XPATH, "//a | //button | //span[contains(@class,'btn')]"):
    try:
        txt = el.text.strip()
        if txt in ('Add', '+ Add', 'Edit', 'View'):
            print(f'  Found button: {txt!r}')
    except Exception:
        pass

driver.quit()
print('Done.')
