from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

url='https://engineering.ultrivalms.com/QALS1011'
user='buyeruser'; pw='Ultriva!23'
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--start-maximized')
options.add_experimental_option('excludeSwitches', ['enable-logging'])
d = webdriver.Chrome(options=options)
d.implicitly_wait(8)
d.set_page_load_timeout(30)
try:
    d.get(url)
    WebDriverWait(d, 20).until(EC.presence_of_element_located((By.ID, 'UserName')))
    d.find_element(By.ID, 'UserName').send_keys(user)
    d.find_element(By.ID, 'Password').send_keys(pw)
    d.find_element(By.ID, 'login-button').click()
    time.sleep(4)
    d.get('https://engineering.ultrivalms.com/QALS1011/BuyerAction/UpdateSerialNo?&bfr=')
    time.sleep(4)
    print('URL_BEFORE=', d.current_url)
    field = None
    for sel in ['#FILTER_SerialNo', '#FILTER$SerialNo', 'input[name*="Serial"]', 'input[id*="Serial"]', 'input[id*="FILTER"]', 'input[name*="FILTER"]']:
        try:
            field = d.find_element(By.CSS_SELECTOR, sel)
            print('FOUND_BY', sel)
            break
        except Exception:
            pass
    if field is None:
        for e in d.find_elements(By.TAG_NAME, 'input'):
            n = (e.get_attribute('name') or '') + ' ' + (e.get_attribute('id') or '') + ' ' + (e.get_attribute('class') or '')
            if 'serial' in n.lower() or 'filter' in n.lower():
                field = e
                print('FOUND_BY_SCAN', n)
                break
    print('FIELD', field.get_attribute('outerHTML') if field else 'NONE')
    if field:
        field.clear(); field.send_keys('1')
        button = None
        for sel in ['span:contains("Search")', '.imgMatStatusGo', '.btn-filter-submit-item', '.green-btn', 'span']:
            try:
                elems = d.find_elements(By.CSS_SELECTOR, sel)
                for e in elems:
                    txt = (e.text or '').strip()
                    if 'Search' in txt or 'search' in txt.lower():
                        button = e
                        print('CLICK_BUTTON', e.get_attribute('outerHTML'))
                        break
                if button:
                    break
            except Exception:
                pass
        if button is None:
            for e in d.find_elements(By.TAG_NAME, 'span'):
                txt = (e.text or '').strip()
                if txt.lower() == 'search':
                    button = e
                    print('FOUND_SPAN', e.get_attribute('outerHTML'))
                    break
        if button:
            button.click()
            time.sleep(5)
            print('URL_AFTER=', d.current_url)
            body = d.find_element(By.TAG_NAME, 'body').text
            print('BODY_SNIP=', body[:4000])
            print('INPUTS=', [(e.get_attribute('type'), e.get_attribute('id'), e.get_attribute('name'), e.get_attribute('value')) for e in d.find_elements(By.TAG_NAME, 'input')][:50])
            print('CHECKBOXES=', len(d.find_elements(By.XPATH, "//input[@type='checkbox']")))
            for idx, cb in enumerate(d.find_elements(By.XPATH, "//input[@type='checkbox']")[:15]):
                print('CB', idx, cb.get_attribute('outerHTML'))
finally:
    d.quit()
