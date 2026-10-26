from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

BASE_URL = 'https://engineering.ultrivalms.com/QALS1011'
USERNAME = 'buyeruser'
PASSWORD = 'Ultriva!23'

opts = webdriver.ChromeOptions()
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')
opts.add_argument('--disable-gpu')
opts.add_argument('--start-maximized')
opts.add_experimental_option('excludeSwitches', ['enable-logging'])

d = webdriver.Chrome(options=opts)
d.implicitly_wait(10)
d.set_page_load_timeout(30)

try:
    d.get(BASE_URL)
    WebDriverWait(d, 20).until(EC.presence_of_element_located((By.ID, 'UserName')))
    d.find_element(By.ID, 'UserName').send_keys(USERNAME)
    d.find_element(By.ID, 'Password').send_keys(PASSWORD)
    d.find_element(By.ID, 'login-button').click()
    time.sleep(2)
    d.get(f'{BASE_URL}/BuyerAction/SetExpiryDateFilter')
    time.sleep(2)
    if 'Login' in d.current_url:
        print('LOGIN PAGE AGAIN')
    go = d.execute_script("""
    var tags=['button','a','input'];
    for (var t=0; t<tags.length; t++) {
      var els = document.querySelectorAll(tags[t]);
      for (var i=0; i<els.length; i++) {
        var txt = (els[i].value || els[i].textContent || '').trim();
        if (txt === 'Go' || txt === 'GO' || /^Go\b/.test(txt)) return els[i];
      }
    }
    return null;
    """)
    print('go element exists?', bool(go))
    if go:
        d.execute_script('arguments[0].click()', go)
    time.sleep(4)
    items = d.find_elements(By.XPATH, "//a[contains(@class,'GridLink')]")
    print('item links', len(items))
    if items:
        d.execute_script('arguments[0].click()', items[0])
        time.sleep(4)
    if 'SetExpiryDateCard' not in d.current_url:
        for xp in [
            "//button[contains(normalize-space(),'Show Cards')]",
            "//a[contains(normalize-space(),'Show Cards')]",
            "//*[contains(@id,'ShowCards') or contains(@id,'showCards')]",
        ]:
            try:
                show = WebDriverWait(d, 8).until(EC.element_to_be_clickable((By.XPATH, xp)))
                print('show button by', xp)
                d.execute_script('arguments[0].click()', show)
                time.sleep(4)
                break
            except Exception:
                pass
    print('final url:', d.current_url)
    cbs = d.find_elements(By.XPATH, "//input[@type='checkbox']")
    print('checkboxes total:', len(cbs))
    for i, cb in enumerate(cbs[:20]):
        name = cb.get_attribute('name') or ''
        idx = cb.get_attribute('id') or ''
        klass = cb.get_attribute('class') or ''
        print(i, 'name=', name, 'id=', idx, 'class=', klass, 'displayed=', cb.is_displayed(), 'enabled=', cb.is_enabled())
    print('has CheckboxCardGID:', 'CheckboxCardGID' in d.page_source)
    print('has GridCheckbox:', 'GridCheckbox' in d.page_source)
finally:
    d.quit()
