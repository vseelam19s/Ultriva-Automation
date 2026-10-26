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
    print('URL_AFTER_ACTIONS=', d.current_url)
    body = d.find_element(By.TAG_NAME,'body').text
    print('RESCHEDULE IN BODY=', 'Reschedule' in body)
    print('RELEASED IN BODY=', 'Released' in body)
    print('ACCEPT IN BODY=', 'Accept' in body)
    print('REJECT IN BODY=', 'Reject' in body)
    labels=[]
    for el in d.find_elements(By.XPATH, "//*[self::a or self::button or self::input or self::span or self::div]"):
        txt=(el.text or '').strip()
        if txt and el.is_displayed():
            labels.append(txt)
    uniq=sorted(set(labels))
    for t in uniq:
        low=t.lower()
        if any(k in low for k in ['reschedule','released','accept','reject','approval','cards','items','wait','confirm']):
            print('LABEL=', t)
    print('BODY_SNIP=', body[:1500])
finally:
    d.quit()
