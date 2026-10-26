from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

cands = ['1212','12121','A1212','SER1212','99999','123456','TEST123','ABC123','UNIQ0001','QALS1212','1A2B3C','0001','1213','001212','12345678','1','2','10','121200','121211']
opts=webdriver.ChromeOptions(); opts.add_argument('--no-sandbox'); opts.add_argument('--disable-dev-shm-usage'); opts.add_argument('--disable-gpu'); opts.add_argument('--start-maximized'); opts.add_experimental_option('excludeSwitches',['enable-logging'])
d=webdriver.Chrome(options=opts); d.implicitly_wait(8); d.set_page_load_timeout(30)
try:
    d.get('https://engineering.ultrivalms.com/QALS1011')
    WebDriverWait(d,20).until(EC.presence_of_element_located((By.ID,'UserName')))
    d.find_element(By.ID,'UserName').send_keys('buyeruser')
    d.find_element(By.ID,'Password').send_keys('Ultriva!23')
    d.find_element(By.ID,'login-button').click(); time.sleep(4)
    d.get('https://engineering.ultrivalms.com/QALS1011/BuyerAction/UpdateSerialNo?&bfr='); time.sleep(4)
    for cand in cands:
        d.get('https://engineering.ultrivalms.com/QALS1011/BuyerAction/UpdateSerialNo?&bfr='); time.sleep(2)
        d.find_element(By.ID,'FILTER_SerialNo').clear(); d.find_element(By.ID,'FILTER_SerialNo').send_keys('1');
        d.find_element(By.ID,'imgMatStatusGo').click(); time.sleep(4)
        chk = d.find_element(By.NAME,'UpdateSerialNo_1_$CheckboxSerialGID')
        chk.click(); time.sleep(0.3)
        tb = d.find_element(By.NAME,'UpdateSerialNo_1_$TextboxSerialNo')
        tb.clear(); tb.send_keys(cand); time.sleep(0.3)
        submit = d.find_element(By.ID,'btndoActTop')
        submit.click(); time.sleep(4)
        body = d.find_element(By.TAG_NAME,'body').text
        print('CAND=', repr(cand))
        if 'there are errors in selected rows' in body.lower():
            print('RESULT=ERROR')
        elif 'success' in body.lower() or 'updated' in body.lower():
            print('RESULT=SUCCESS')
        else:
            print('RESULT=OTHER'); print(body[:500])
        print('---')
finally:
    d.quit()
