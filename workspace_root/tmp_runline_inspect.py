from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

BASE_URL='https://engineering.ultrivalms.com/QALS1011'
opts=webdriver.ChromeOptions(); opts.add_argument('--no-sandbox'); opts.add_argument('--disable-dev-shm-usage'); opts.add_argument('--disable-gpu'); opts.add_argument('--start-maximized'); opts.add_experimental_option('excludeSwitches',['enable-logging'])
d=webdriver.Chrome(options=opts)
d.get(BASE_URL+'/Account/Login')
WebDriverWait(d,20).until(EC.visibility_of_element_located((By.ID,'UserName')))
d.find_element(By.ID,'UserName').send_keys('supnewuser')
d.find_element(By.ID,'Password').send_keys('Ultriva!23')
d.find_element(By.ID,'login-button').click()
WebDriverWait(d,30).until(lambda x: 'Account/Login' not in x.current_url)
time.sleep(3)
d.get(BASE_URL+'/SupplierAction/AcceptItems?bfc=y')
WebDriverWait(d,30).until(lambda x: 'AcceptItems' in x.current_url)
button = d.find_element(By.ID, 'AcceptItems_tbrAcceptRunline')
button.click(); time.sleep(5)
print('AFTER RUNLINE URL', d.current_url)
print('BEFORE CHECKBOX COUNT', len(d.find_elements(By.XPATH, "//input[contains(@name, '$CheckboxCardGID')]")))
for i, cb in enumerate(d.find_elements(By.XPATH, "//input[contains(@name, '$CheckboxCardGID')]")[:10], 1):
    print('BEFORE', i, 'name=', cb.get_attribute('name'), 'value=', cb.get_attribute('value'), 'class=', cb.get_attribute('class'))
# select a couple
for cb in d.find_elements(By.XPATH, "//input[contains(@name, '$CheckboxCardGID')]")[:2]:
    if not cb.is_selected():
        cb.click(); print('CLICKED', cb.get_attribute('name'), cb.get_attribute('value'))
# accept button after selection
for btn_id in ['btndoActTop','btndoActBot','btnapNodoAct']:
    try:
        b=d.find_element(By.ID, btn_id)
        print('FOUND BUTTON', btn_id, 'displayed', b.is_displayed(), 'enabled', b.is_enabled())
        b.click(); print('CLICKED ACCEPT BUTTON', btn_id)
        break
    except Exception:
        pass

time.sleep(8)
print('AFTER ACCEPT URL', d.current_url)
print('AFTER ACCEPT BODY', (d.find_element(By.TAG_NAME,'body').text)[:3000])
print('AFTER ACCEPT checkbox names:')
for i, cb in enumerate(d.find_elements(By.XPATH, "//input[contains(@name, '$CheckboxCardGID')]")[:20], 1):
    print(i, 'name=', cb.get_attribute('name'), 'value=', cb.get_attribute('value'), 'class=', cb.get_attribute('class'), 'displayed=', cb.is_displayed())
print('ALL BUTTONS AFTER ACCEPT')
for el in d.find_elements(By.XPATH, '//button | //a | //input[@type="button" or @type="submit"]'):
    t=(el.text or '').strip()
    if t:
        print('BUTTON', repr(t), 'id=', el.get_attribute('id'), 'class=', (el.get_attribute('class') or '')[:120])
d.quit()
