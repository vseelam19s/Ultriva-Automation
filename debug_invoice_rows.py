from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--start-maximized')
options.add_experimental_option('excludeSwitches', ['enable-logging'])

d = webdriver.Chrome(options=options)
d.implicitly_wait(10)
d.set_page_load_timeout(60)
try:
    d.get('https://engineering.ultrivalms.com/QALS1011/Account/Login')
    WebDriverWait(d, 25).until(lambda x: x.execute_script('return document.readyState') == 'complete')
    d.find_element(By.ID, 'UserName').clear(); d.find_element(By.ID, 'UserName').send_keys('supnewuser')
    d.find_element(By.ID, 'Password').clear(); d.find_element(By.ID, 'Password').send_keys('Ultriva!23')
    btn = d.find_element(By.ID, 'login-button')
    print('BEFORE_LOGIN_URL', d.current_url)
    print('LOGIN_BUTTON_TAG', btn.tag_name, 'enabled', btn.is_enabled(), 'displayed', btn.is_displayed())
    btn.click()
    time.sleep(5)
    print('AFTER_LOGIN_URL', d.current_url)
    print('PW_TEXT', d.find_element(By.ID, 'Password').get_attribute('value'))
    d.get('https://engineering.ultrivalms.com/QALS1011/SupplierAction/InvoiceCreation')
    WebDriverWait(d, 25).until(lambda x: 'InvoiceCreation' in x.current_url)
    time.sleep(5)
    print('INVOICE_URL', d.current_url)
    print('TITLE', d.title)
    print('ROWS', len(d.find_elements(By.TAG_NAME, 'tr')))
    for i, el in enumerate(d.find_elements(By.TAG_NAME, 'tr')[:25]):
        txt = (el.text or '').replace('\n', ' | ').strip()
        if txt:
            print('ROW', i, repr(txt[:300]))
    print('BUTTONS')
    for i, el in enumerate(d.find_elements(By.TAG_NAME, 'button')[:25]):
        txt = (el.text or '').strip()
        print(i, repr(txt), 'id=', el.get_attribute('id'), 'class=', el.get_attribute('class'))
    print('ANCHORS')
    for i, el in enumerate(d.find_elements(By.TAG_NAME, 'a')[:25]):
        txt = (el.text or '').strip()
        if txt:
            print(i, repr(txt), 'href=', el.get_attribute('href'))
    print('TEXT_MATCHES')
    for i, el in enumerate(d.find_elements(By.XPATH, "//*[self::a or self::button or self::input or self::span or self::div]")[:200]):
        txt = (el.text or '').strip()
        if txt and len(txt) < 120 and any(k in txt.lower() for k in ['create', 'invoice', 'item', 'select', 'confirm', 'po']):
            print('EL', i, el.tag_name, repr(txt), 'id=', el.get_attribute('id'), 'class=', el.get_attribute('class'))
finally:
    d.quit()
