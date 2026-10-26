from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--start-maximized')
options.add_experimental_option('excludeSwitches', ['enable-logging'])

# login

d = webdriver.Chrome(options=options)
wait = WebDriverWait(d, 30)
d.get('https://engineering.ultrivalms.com/QALS1011/BuyerAction/BulkPrintItems')
wait.until(EC.presence_of_element_located((By.ID, 'UserName')))
d.find_element(By.ID, 'UserName').send_keys('buyeruser')
d.find_element(By.ID, 'Password').send_keys('Ultriva!23')
d.find_element(By.ID, 'login-button').click()
wait.until(lambda drv: 'BulkPrintItems' in drv.current_url or 'Home' in drv.current_url)
print('URL_AFTER_LOGIN', d.current_url)

# select the filter and observe if it updates the page without a Go click
for s in d.find_elements(By.TAG_NAME, 'select'):
    opts = [o.text.strip() for o in s.find_elements(By.TAG_NAME, 'option')]
    if 'In Cycle' in opts or 'On Hand' in opts:
        print('FOUND_SELECT', s.get_attribute('outerHTML')[:400])
        Select(s).select_by_visible_text('In Cycle')
        print('SELECTED_IN_CYCLE')
        break

time.sleep(4)
print('URL_AFTER_FILTER', d.current_url)
print('BODY_TEXT_SNIP', d.find_element(By.TAG_NAME, 'body').text[:3000])
print('GRID_LINK_COUNT', len(d.find_elements(By.XPATH, "//a[contains(@class,'GridLink')]")))
print('SHOW_CARDS_COUNT', len(d.find_elements(By.XPATH, "//*[contains(normalize-space(.), 'Show Cards')]")))
print('PRINT_COUNT', len(d.find_elements(By.XPATH, "//*[contains(normalize-space(.), 'Print')]")))
print('GO_COUNT', len(d.find_elements(By.XPATH, "//*[contains(normalize-space(.), 'Go')]")))

d.quit()
