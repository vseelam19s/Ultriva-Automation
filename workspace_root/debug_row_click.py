from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

options = webdriver.ChromeOptions(); options.add_argument('--no-sandbox'); options.add_argument('--disable-dev-shm-usage'); options.add_argument('--disable-gpu'); options.add_argument('--start-maximized'); options.add_experimental_option('excludeSwitches', ['enable-logging'])
d = webdriver.Chrome(options=options); d.set_page_load_timeout(60)
try:
    d.get('https://engineering.ultrivalms.com/QALS1011/Account/Login')
    WebDriverWait(d, 20).until(EC.presence_of_element_located((By.ID, 'UserName')))
    d.find_element(By.ID, 'UserName').send_keys('supnewuser')
    d.find_element(By.ID, 'Password').send_keys('Ultriva!23')
    d.find_element(By.ID, 'login-button').click()
    time.sleep(4)
    d.get('https://engineering.ultrivalms.com/QALS1011/SupplierAction/SetReadyToShipDateItems')
    WebDriverWait(d, 25).until(EC.url_contains('SetReadyToShipDateItems'))
    d.find_element(By.XPATH, "//a[normalize-space(.)='IT050325']").click()
    WebDriverWait(d, 25).until(EC.url_contains('SetReadyToShipDateCards'))
    target = 'KCD39TDQALZ6'
    row = None
    rows = d.find_elements(By.XPATH, '//tr')
    for r in rows:
        text = (r.text or '').replace('\n', ' | ')
        if target in text:
            row = r
            print('row selected', text[:500])
            break
    print('row is none?', row is None)
    if row:
        print('row innerHTML snippet:', row.get_attribute('innerHTML')[:1200])
        for sel in ['.//input[@type="checkbox"]', './/td', './/a', './/span', './/div']:
            items = row.find_elements(By.XPATH, sel)
            print('selector', sel, 'count', len(items))
            for i, it in enumerate(items[:10], 1):
                txt = (it.text or '').strip()
                print('  ', i, 'displayed', it.is_displayed(), 'enabled', it.is_enabled(), 'text', txt[:80])
        d.execute_script("""
            var rows = Array.from(document.querySelectorAll('tr'));
            for (var i = 0; i < rows.length; i++) {
                var t = (rows[i].innerText || rows[i].textContent || '').replace(/\s+/g, ' ').trim();
                if (t.indexOf(arguments[0]) !== -1) {
                    var target = rows[i];
                    var els = target.querySelectorAll('td, a, div, span');
                    for (var j = 0; j < els.length; j++) {
                        var el = els[j];
                        if (el.offsetParent !== null) {
                            try { el.click(); console.log('clicked element', el.tagName, (el.innerText || el.textContent || '').trim().slice(0,60)); return; } catch (e) { }
                        }
                    }
                    return;
                }
            }
        """, target)
        time.sleep(2)
        print('after click checkboxes:')
        for i, cb in enumerate(d.find_elements(By.XPATH, "//input[@type='checkbox']")[:20], 1):
            print(i, cb.is_displayed(), cb.is_enabled(), cb.is_selected(), cb.get_attribute('name'), cb.get_attribute('id'), cb.get_attribute('class'))
finally:
    d.quit()
