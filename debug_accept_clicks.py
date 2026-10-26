from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

BASE_URL='https://engineering.ultrivalms.com/QALS1011'
USERNAME='supnewuser'; PASSWORD='Ultriva!23'
options = webdriver.ChromeOptions(); options.add_argument('--no-sandbox'); options.add_argument('--disable-dev-shm-usage'); options.add_argument('--disable-gpu'); options.add_argument('--start-maximized'); options.add_experimental_option('excludeSwitches', ['enable-logging'])
d = webdriver.Chrome(options=options)
d.implicitly_wait(10); d.set_page_load_timeout(40)
try:
    d.get(BASE_URL + '/Account/Login')
    WebDriverWait(d,20).until(EC.presence_of_element_located((By.ID,'UserName')))
    d.find_element(By.ID,'UserName').send_keys(USERNAME)
    d.find_element(By.ID,'Password').send_keys(PASSWORD)
    d.find_element(By.ID,'login-button').click()
    WebDriverWait(d,30).until(lambda x: 'Home' in x.current_url or 'QALS1011' in x.current_url)
    time.sleep(2)
    actions = WebDriverWait(d,20).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'Action/Home') or normalize-space(.)='Actions' or .//span[normalize-space()='Actions']]")))
    actions.click(); time.sleep(2)
    d.get(BASE_URL + '/SupplierAction/AcceptCards'); time.sleep(2)
    labels = ['Reschedule Approval Cards','Reschedule Approval Card','Reschedule Approval','Approval']
    for label in labels:
        matches=[]
        for el in d.find_elements(By.XPATH, "//*[self::a or self::button or self::input or self::span or self::div]"):
            txt=(el.text or '').replace('\n',' ').strip()
            if txt and (txt.lower()==label.lower() or label.lower() in txt.lower() or txt.lower() in label.lower()):
                matches.append((txt, el.is_displayed(), el.is_enabled(), el.get_attribute('outerHTML')[:200]))
        print('LABEL=', label, 'MATCHES=', len(matches))
        for item in matches[:10]:
            print(item[0], 'displayed=', item[1], 'enabled=', item[2])
            print(item[3])
        if matches:
            js = d.execute_script("""
            var wanted = arguments[0].trim().toLowerCase();
            var els = document.querySelectorAll('a, button, input, span, div, td, li');
            var count = 0;
            for (var i = 0; i < els.length; i++) {
              var txt = (els[i].innerText || els[i].value || '').replace(/\s+/g, ' ').trim().toLowerCase();
              if (txt === wanted || txt.indexOf(wanted) !== -1 || wanted.indexOf(txt) !== -1) {
                count++;
                if (els[i].offsetParent !== null) {
                  console.log('JS MATCH', els[i].tagName, txt, 'offset', els[i].offsetParent !== null);
                }
              }
            }
            return count;
            """, label)
            print('JS COUNT=', js)
finally:
    d.quit()
