from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time

BASE_URL = 'https://engineering.ultrivalms.com/QALS1011'
opts = webdriver.ChromeOptions()
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')
opts.add_argument('--disable-gpu')
opts.add_argument('--start-maximized')
opts.add_experimental_option('excludeSwitches', ['enable-logging'])

d = webdriver.Chrome(options=opts)
d.implicitly_wait(10)
d.set_page_load_timeout(60)

try:
    d.get(f'{BASE_URL}/Account/Login')
    WebDriverWait(d, 20).until(lambda x: x.execute_script('return document.readyState') == 'complete')
    d.find_element(By.ID, 'UserName').send_keys('supnewuser')
    d.find_element(By.ID, 'Password').send_keys('Ultriva!23')
    d.find_element(By.ID, 'login-button').click()
    time.sleep(3)
    d.get(f'{BASE_URL}/SupplierAction/SupplierRescheduleCards')
    time.sleep(4)
    print('CURRENT URL', d.current_url)

    xpaths = [
        '//input',
        '//select',
        "//*[contains(@id,'ReqShipDate') or contains(@name,'ReqShipDate') or contains(@id,'Reschedule') or contains(@name,'Reschedule')]",
    ]
    for xp in xpaths:
        els = d.find_elements(By.XPATH, xp)
        print('XPATH', xp, 'COUNT', len(els))
        for i, e in enumerate(els[:80]):
            tag = e.tag_name.lower()
            typ = (e.get_attribute('type') or '').lower()
            iid = e.get_attribute('id') or ''
            name = e.get_attribute('name') or ''
            cls = e.get_attribute('class') or ''
            val = e.get_attribute('value') or ''
            print(i, {'tag': tag, 'type': typ, 'id': iid, 'name': name, 'class': cls[:120], 'value': val, 'displayed': e.is_displayed(), 'enabled': e.is_enabled()})

    rows = d.find_elements(By.XPATH, '//tr[td]')
    print('ROWS', len(rows))
    for idx, row in enumerate(rows[:8]):
        print('ROW', idx, 'TEXT', (row.text or '')[:300].replace('\n', ' | '))
        inputs = row.find_elements(By.XPATH, './/input | .//select')
        for e in inputs:
            print('  ', e.tag_name, 'id=', e.get_attribute('id'), 'name=', e.get_attribute('name'), 'type=', e.get_attribute('type'), 'class=', e.get_attribute('class'), 'value=', e.get_attribute('value'), 'display=', e.is_displayed(), 'enabled=', e.is_enabled())
finally:
    d.quit()
