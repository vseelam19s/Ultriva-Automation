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
d.maximize_window()

try:
    d.get('https://engineering.ultrivalms.com/QALS1011/Account/Login')
    WebDriverWait(d, 20).until(lambda x: x.execute_script('return document.readyState') == 'complete')
    d.find_element(By.ID, 'UserName').send_keys('supnewuser')
    d.find_element(By.ID, 'Password').send_keys('Ultriva!23')
    d.find_element(By.ID, 'login-button').click()
    time.sleep(3)
    d.get('https://engineering.ultrivalms.com/QALS1011/SupplierAction/ShipCards')
    WebDriverWait(d, 25).until(lambda x: x.execute_script('return document.readyState') == 'complete')
    time.sleep(3)

    print('URL after login:', d.current_url)

    cbs = d.find_elements(By.XPATH, "//input[@type='checkbox' and not(@disabled)]")
    print('checkbox count total:', len(cbs))
    for idx, cb in enumerate(cbs[:8]):
        txt = 'id=' + (cb.get_attribute('id') or '') + ' name=' + (cb.get_attribute('name') or '') + ' display=' + str(cb.is_displayed()) + ' enabled=' + str(cb.is_enabled()) + ' selected=' + str(cb.is_selected())
        print(idx, txt)

    for idx, cb in enumerate(cbs[:3]):
        if cb.is_displayed() and cb.is_enabled():
            d.execute_script('arguments[0].click();', cb)
            print('clicked checkbox', idx)
            time.sleep(1)
            break

    # collect all text-like controls containing ship / attach / back / change filter / note / done / submit
    found = []
    els = d.find_elements(By.XPATH, '//button | //a | //input | //span | //div')
    for e in els:
        txt = (e.text or e.get_attribute('value') or '').strip().replace('\n', ' ')
        low = txt.lower()
        if any(k in low for k in ['ship', 'attach', 'back', 'change filter', 'save', 'done', 'submit', 'confirm', 'notes']):
            found.append((txt[:120], e.tag_name, e.get_attribute('id') or '', e.get_attribute('name') or '', (e.get_attribute('class') or '')[:80], e.is_displayed(), e.is_enabled()))
    print('matching controls:', len(found))
    for item in found[:80]:
        print(item)

    # Print visible buttons by text exactly
    for x in [
        "//*[contains(normalize-space(.), 'Ship')]",
        "//*[contains(normalize-space(.), 'Attach Notes')]",
        "//*[contains(normalize-space(.), 'Back To Items')]",
        "//*[contains(normalize-space(.), 'Change Filter')]",
        "//*[contains(normalize-space(.), 'Submit')]",
        "//*[contains(normalize-space(.), 'Done')]",
        "//*[contains(normalize-space(.), 'Save')]",
    ]:
        els = d.find_elements(By.XPATH, x)
        print('\nXPATH', x, 'count=', len(els))
        for e in els[:20]:
            txt = (e.text or e.get_attribute('value') or '').strip().replace('\n', ' ')
            print(' -', repr(txt), 'tag=', e.tag_name, 'id=', e.get_attribute('id'), 'name=', e.get_attribute('name'), 'displayed=', e.is_displayed(), 'enabled=', e.is_enabled())

finally:
    d.quit()
