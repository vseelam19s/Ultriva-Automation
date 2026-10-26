from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

BASE='https://engineering.ultrivalms.com/QALS1011'
USER='supnewuser'; PW='Ultriva!23'
opts=webdriver.ChromeOptions(); opts.add_argument('--no-sandbox'); opts.add_argument('--disable-dev-shm-usage'); opts.add_argument('--disable-gpu'); opts.add_argument('--start-maximized'); opts.add_experimental_option('excludeSwitches',['enable-logging'])
d=webdriver.Chrome(options=opts)
d.implicitly_wait(10)
d.set_page_load_timeout(40)
try:
    d.get(f'{BASE}/Account/Login')
    WebDriverWait(d,20).until(lambda driver: driver.execute_script('return document.readyState')=='complete')
    d.find_element(By.ID, 'UserName').send_keys(USER)
    d.find_element(By.ID, 'Password').send_keys(PW)
    d.find_element(By.ID, 'login-button').click()
    WebDriverWait(d,20).until(lambda driver: 'Account/Login' not in driver.current_url or 'Home' in driver.current_url or 'QALS1011' in driver.current_url)
    time.sleep(1.5)
    actions = WebDriverWait(d,15).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'Action/Home') or normalize-space(.)='Actions' or .//span[normalize-space()='Actions']]")))
    actions.click(); time.sleep(1.5)
    try:
        acc = WebDriverWait(d,8).until(EC.element_to_be_clickable((By.XPATH, "//*[self::a or self::span][contains(normalize-space(.),'Accept')]")))
        acc.click(); time.sleep(1.5)
    except Exception:
        d.get(f'{BASE}/SupplierAction/AcceptCards'); time.sleep(1.5)
    print('URL accept page=', d.current_url)
    print('BODY before click runline:')
    print(d.find_element(By.TAG_NAME,'body').text[:2000])
    run_candidates = d.find_elements(By.XPATH, "//*[self::a or self::button or self::span][contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'runline cards')]")
    print('RUNLINE_CANDIDATES=', len(run_candidates))
    for i, el in enumerate(run_candidates[:10], 1):
        print('R', i, 'tag=', el.tag_name, 'text=', repr((el.text or '').strip()), 'href=', el.get_attribute('href'))
    if run_candidates:
        run_candidates[0].click(); time.sleep(2)
        print('URL after runline=', d.current_url)
        print('BODY after click runline:')
        print(d.find_element(By.TAG_NAME,'body').text[:3000])
        print('--- visible matching texts ---')
        els = d.find_elements(By.XPATH, "//*[self::button or self::a or self::input or self::span or self::div]")
        for el in els:
            t=(el.text or el.get_attribute('value') or '').strip()
            if t and any(k in t.lower() for k in ['accept','confirm','back','card','status','go','submit','release']):
                print(repr(t), 'tag=', el.tag_name)
finally:
    d.quit()
