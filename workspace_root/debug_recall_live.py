from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

opts = webdriver.ChromeOptions()
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')
opts.add_argument('--disable-gpu')
opts.add_argument('--start-maximized')
opts.add_experimental_option('excludeSwitches', ['enable-logging'])

d = webdriver.Chrome(options=opts)
d.set_page_load_timeout(40)
try:
    d.get('https://engineering.ultrivalms.com/QALS1011/Account/Login')
    WebDriverWait(d, 20).until(EC.presence_of_element_located((By.ID, 'UserName')))
    d.find_element(By.ID, 'UserName').send_keys('supnewuser')
    d.find_element(By.ID, 'Password').send_keys('Ultriva!23')
    d.find_element(By.ID, 'login-button').click()
    WebDriverWait(d, 20).until(lambda x: 'Account/Login' not in x.current_url)
    time.sleep(2)

    d.get('https://engineering.ultrivalms.com/QALS1011/SupplierAction/SupplierRecallItems')
    WebDriverWait(d, 20).until(lambda x: 'SupplierRecallItems' in x.current_url)
    time.sleep(4)
    print('URL after items page:', d.current_url)
    items = d.find_elements(By.XPATH, "//a[contains(@class,'GridLink')]")
    print('GridLink count:', len(items))
    if items:
        first = items[0]
        print('First item text:', (first.text or '').strip())
        first.click()
        time.sleep(3)
        print('URL after first item click:', d.current_url)

    d.get('https://engineering.ultrivalms.com/QALS1011/SupplierAction/SupplierRecallCards')
    WebDriverWait(d, 20).until(lambda x: 'SupplierRecallCards' in x.current_url)
    time.sleep(4)
    print('URL after direct cards load:', d.current_url)

    cbs = d.find_elements(By.XPATH, "//input[@type='checkbox']")
    print('checkbox count:', len(cbs))
    for idx, cb in enumerate(cbs[:5], 1):
        try:
            cb.click()
            print('clicked checkbox', idx)
        except Exception as e:
            print('checkbox click error', idx, type(e).__name__, e)
    time.sleep(1)

    recall_matches = d.find_elements(By.XPATH, "//*[self::button or self::a or self::div or self::span or self::input][contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'recall')]")
    print('recall matches:', len(recall_matches))
    for idx, el in enumerate(recall_matches[:20], 1):
        text = (el.text or '').strip()
        print(idx, 'TAG=', el.tag_name, 'TEXT=', text[:200])
    if recall_matches:
        recall_matches[0].click()
        time.sleep(4)
        print('URL after recall click:', d.current_url)

    body = (d.find_element(By.TAG_NAME, 'body').text or '')
    print('BODY:', body[:4000])

    back_matches = d.find_elements(By.XPATH, "//*[self::button or self::a or self::div or self::span or self::input][contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'back to items') or contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'back to item') or contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'back')]")
    print('back matches:', len(back_matches))
    for idx, el in enumerate(back_matches[:20], 1):
        text = (el.text or '').strip()
        print('BACK', idx, 'TAG=', el.tag_name, 'TEXT=', text[:200])
finally:
    d.quit()
