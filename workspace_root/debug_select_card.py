from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--start-maximized')
options.add_experimental_option('excludeSwitches', ['enable-logging'])

driver = webdriver.Chrome(options=options)
driver.set_page_load_timeout(60)
try:
    driver.get('https://engineering.ultrivalms.com/QALS1011/Account/Login')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'UserName')))
    driver.find_element(By.ID, 'UserName').send_keys('supnewuser')
    driver.find_element(By.ID, 'Password').send_keys('Ultriva!23')
    driver.find_element(By.ID, 'login-button').click()
    time.sleep(5)
    driver.get('https://engineering.ultrivalms.com/QALS1011/SupplierAction/SetReadyToShipDateItems')
    WebDriverWait(driver, 25).until(EC.url_contains('SetReadyToShipDateItems'))
    item = driver.find_element(By.XPATH, "//a[normalize-space(.)='IT050325']")
    item.click()
    WebDriverWait(driver, 25).until(EC.url_contains('SetReadyToShipDateCards'))
    print('URL=', driver.current_url)
    rows = driver.find_elements(By.XPATH, '//tr')
    print('TOTAL ROWS', len(rows))
    for idx, row in enumerate(rows, 1):
        text = (row.text or '').replace('\n', ' | ')
        if 'KCD39TDQALZ6' in text:
            print('FOUND ROW', idx, text[:800])
            cbs = row.find_elements(By.XPATH, './/input[@type="checkbox"]')
            print('CHECKBOXES', len(cbs))
            for i, cb in enumerate(cbs, 1):
                print('CB', i, 'displayed=', cb.is_displayed(), 'enabled=', cb.is_enabled(), 'selected=', cb.is_selected(), 'name=', cb.get_attribute('name'), 'id=', cb.get_attribute('id'), 'class=', cb.get_attribute('class'))
    print('ALL CHECKBOX count', len(driver.find_elements(By.XPATH, "//input[@type='checkbox']")))
    for i, cb in enumerate(driver.find_elements(By.XPATH, "//input[@type='checkbox']")[:20], 1):
        print('GEN CB', i, 'displayed=', cb.is_displayed(), 'enabled=', cb.is_enabled(), 'name=', cb.get_attribute('name'), 'id=', cb.get_attribute('id'), 'class=', cb.get_attribute('class'))
    print('Find textbox candidates:')
    for xp in [
        "//input[contains(@name,'FindTextbox') or contains(@id,'FindTextbox') or contains(@class,'findbox')]",
        "//input[@name='SetReadyToShipDateCards_FindTextbox']",
        "//input[contains(@name,'Card') and contains(@name,'Find')]",
        "//input[contains(@placeholder,'Find') or contains(@title,'Find') or contains(@placeholder,'Card') or contains(@title,'Card')]",
    ]:
        els = driver.find_elements(By.XPATH, xp)
        print(xp, 'count=', len(els))
        for e in els[:5]:
            print('  ', e.get_attribute('name'), e.get_attribute('id'), e.get_attribute('placeholder'), e.get_attribute('title'), e.get_attribute('class'))
finally:
    driver.quit()
