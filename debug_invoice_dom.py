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
d.set_page_load_timeout(40)

try:
    d.get('https://engineering.ultrivalms.com/QALS1011/Account/Login')
    WebDriverWait(d, 20).until(lambda x: x.execute_script('return document.readyState') == 'complete')
    d.find_element(By.ID, 'UserName').send_keys('supnewuser')
    d.find_element(By.ID, 'Password').send_keys('Ultriva!23')
    d.find_element(By.ID, 'login-button').click()
    WebDriverWait(d, 20).until(lambda x: 'Home' in x.current_url or 'QALS1011' in x.current_url)
    d.get('https://engineering.ultrivalms.com/QALS1011/SupplierAction/InvoiceCreation')
    WebDriverWait(d, 20).until(lambda x: 'InvoiceCreation' in x.current_url)
    time.sleep(5)
    print('URL:', d.current_url)
    print('TITLE:', d.title)
    print('TR COUNT:', len(d.find_elements(By.TAG_NAME, 'tr')))
    print('BUTTON COUNT:', len(d.find_elements(By.TAG_NAME, 'button')))
    print('CHECKBOX COUNT:', len(d.find_elements(By.CSS_SELECTOR, 'input[type="checkbox"]')))
    for i, el in enumerate(d.find_elements(By.TAG_NAME, 'tr')[:50]):
        txt = (el.text or '').replace('\n', ' | ').strip()
        if txt:
            print(f'ROW {i}: {txt[:500]}')
    print('BUTTONS:')
    for i, el in enumerate(d.find_elements(By.TAG_NAME, 'button')[:50]):
        txt = (el.text or '').strip()
        print(f'BTN {i}: {txt[:200]} | id={el.get_attribute("id")} | class={el.get_attribute("class")}')
    print('TEXT CANDIDATES')
    for i, el in enumerate(d.find_elements(By.XPATH, "//*[self::a or self::button or self::input or self::span or self::div][:150]")[:150]):
        txt = (el.text or '').strip()
        if txt and len(txt) < 120 and any(k in txt for k in ['Create', 'Invoice', 'Select', 'Card', 'Item', 'Action', 'Back', 'Confirm']):
            print(f'EL {i}: tag={el.tag_name} txt={txt[:200]} id={el.get_attribute("id")} class={el.get_attribute("class")}')
finally:
    d.quit()
