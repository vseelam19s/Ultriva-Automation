from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time

BASE_URL='https://engineering.ultrivalms.com/QALS1011'
USERNAME='supnewuser'; PASSWORD='Ultriva!23'
opts=webdriver.ChromeOptions(); opts.add_argument('--no-sandbox'); opts.add_argument('--disable-dev-shm-usage'); opts.add_argument('--disable-gpu'); opts.add_argument('--start-maximized'); opts.add_experimental_option('excludeSwitches',['enable-logging'])
d=webdriver.Chrome(options=opts)
d.implicitly_wait(10); d.set_page_load_timeout(60); d.maximize_window()
try:
    d.get(BASE_URL+'/Account/Login')
    WebDriverWait(d,20).until(lambda x: x.execute_script('return document.readyState')=='complete')
    d.find_element(By.ID,'UserName').send_keys(USERNAME)
    d.find_element(By.ID,'Password').send_keys(PASSWORD)
    d.find_element(By.ID,'login-button').click(); time.sleep(5)

    for xpath in [
        "//*[contains(normalize-space(.), 'Supplier Actions')]",
        "//*[contains(normalize-space(.), 'Reschedule Request')]",
        "//*[contains(normalize-space(.), 'Reschedule')]",
        "//a[contains(normalize-space(.), 'Actions')]",
        "//div[contains(normalize-space(.), 'Actions')]",
        "//span[contains(normalize-space(.), 'Actions')]",
        "//li[contains(normalize-space(.), 'Actions')]",
        "//a[contains(normalize-space(.), 'Supplier')]",
    ]:
        els = d.find_elements(By.XPATH, xpath)
        print('XPATH:', xpath, 'count=', len(els))
        for i, el in enumerate(els[:20]):
            txt=(el.text or '').strip(); href=el.get_attribute('href'); cls=el.get_attribute('class'); iid=el.get_attribute('id');
            print(' ', i, 'txt=', repr(txt[:200]), 'href=', href, 'id=', iid, 'class=', cls[:120])
    print('PAGE SOURCE HAS RESCHEDULE?', 'Reschedule' in d.page_source)
    html = d.page_source.lower()
    for token in ['reschedule', 'supplier actions', 'actions']:
        idx = html.find(token)
        print('TOKEN', token, 'idx', idx)
        if idx != -1:
            print(html[max(0, idx-250):idx+500])
finally:
    d.quit()
