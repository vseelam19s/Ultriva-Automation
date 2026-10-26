from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

url='https://engineering.ultrivalms.com/QALS1011'
user='buyeruser'; pw='Ultriva!23'
opts=webdriver.ChromeOptions(); opts.add_argument('--no-sandbox'); opts.add_argument('--disable-dev-shm-usage'); opts.add_argument('--disable-gpu'); opts.add_argument('--start-maximized'); opts.add_experimental_option('excludeSwitches',['enable-logging'])
d=webdriver.Chrome(options=opts); d.implicitly_wait(8); d.set_page_load_timeout(30)
try:
    d.get(url)
    WebDriverWait(d,20).until(EC.presence_of_element_located((By.ID,'UserName')))
    d.find_element(By.ID,'UserName').send_keys(user)
    d.find_element(By.ID,'Password').send_keys(pw)
    d.find_element(By.ID,'login-button').click(); time.sleep(4)
    d.get('https://engineering.ultrivalms.com/QALS1011/BuyerAction/UpdateSerialNo?&bfr='); time.sleep(4)
    d.find_element(By.ID,'FILTER_SerialNo').clear(); d.find_element(By.ID,'FILTER_SerialNo').send_keys('1');
    d.find_element(By.ID,'imgMatStatusGo').click(); time.sleep(4)
    cb = d.find_element(By.NAME,'UpdateSerialNo_1_$CheckboxSerialGID')
    cb.click(); time.sleep(1)
    tb = d.find_element(By.NAME,'UpdateSerialNo_1_$TextboxSerialNo')
    tb.clear(); tb.send_keys('1212'); time.sleep(1)
    print('SUBMIT CANDIDATES:')
    for e in d.find_elements(By.XPATH,'.//*[self::button or self::span or self::input or self::a]'):
        txt=(e.text or '').strip()
        if txt.lower() == 'submit' or 'submit' in txt.lower() or 'back' in txt.lower():
            print('HTML:', e.get_attribute('outerHTML')[:500])
            try:
                e.click();
                print('CLICKED', txt)
                break
            except Exception as ex:
                print('CLICK_ERR', txt, ex)
    time.sleep(6)
    body = d.find_element(By.TAG_NAME,'body').text
    print('URL_AFTER_SUBMIT =', d.current_url)
    print('BODY_SNIP =', body[:4000])
finally:
    d.quit()
