from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

url='https://engineering.ultrivalms.com/QALS1011/Account/Login'
opts=webdriver.ChromeOptions()
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')
opts.add_argument('--disable-gpu')
opts.add_argument('--start-maximized')
opts.add_experimental_option('excludeSwitches',['enable-logging'])
d=webdriver.Chrome(options=opts)
d.set_page_load_timeout(40)
try:
    d.get(url)
    WebDriverWait(d,20).until(EC.presence_of_element_located((By.ID,'UserName')))
    d.find_element(By.ID,'UserName').send_keys('supnewuser')
    d.find_element(By.ID,'Password').send_keys('Ultriva!23')
    d.find_element(By.ID,'login-button').click()
    WebDriverWait(d,20).until(lambda x: 'Account/Login' not in x.current_url)
    time.sleep(2)
    d.get('https://engineering.ultrivalms.com/QALS1011/SupplierAction/SupplierRecallItems')
    WebDriverWait(d,20).until(lambda x: 'SupplierRecallItems' in x.current_url)
    time.sleep(5)
    print('URL:', d.current_url)
    print('TITLE:', d.title)
    all_els = d.find_elements(By.XPATH, '//*[contains(normalize-space(.), "Show Cards") or contains(normalize-space(.), "Show cards") or contains(normalize-space(.), "Recall") or contains(normalize-space(.), "Back To Items") or contains(normalize-space(.), "Back to Items")]')
    print('MATCHED ELEMENTS:', len(all_els))
    for i, e in enumerate(all_els[:30], 1):
        txt = (e.text or '').strip().replace('\n', ' | ')
        outer = e.get_attribute('outerHTML')
        print('--- IDX', i, 'TEXT=', txt[:300])
        print(outer[:800] if outer else '<no outerHTML>')
    print('\n\nSELECTABLE ROWS:')
    for e in d.find_elements(By.XPATH, '//tr')[:10]:
        txt = (e.text or '').strip().replace('\n', ' | ')
        if txt:
            print('ROW:', txt[:300])
finally:
    d.quit()
