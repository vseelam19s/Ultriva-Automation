from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

BASE_URL = 'https://engineering.ultrivalms.com/QALS1011'


def wait_ready(driver, timeout=30):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script('return document.readyState') == 'complete'
    )


options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--start-maximized')
options.add_experimental_option('excludeSwitches', ['enable-logging'])

d = webdriver.Chrome(options=options)
d.set_page_load_timeout(30)
try:
    d.get(BASE_URL)
    wait_ready(d)
    d.find_element(By.ID, 'UserName').send_keys('buyeruser')
    d.find_element(By.ID, 'Password').send_keys('Ultriva!23')
    d.find_element(By.ID, 'login-button').click()
    time.sleep(2)
    WebDriverWait(d, 20).until(lambda x: 'Home' in x.current_url or 'QALS1011' in x.current_url)
    actions = WebDriverWait(d, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'Action/Home') or normalize-space(.)='Actions']"))
    )
    actions.click()
    wait_ready(d)
    time.sleep(2)
    print('CURRENT_URL', d.current_url)
    print('TITLE', d.title)
    print('A LINK TEXTS')
    for a in d.find_elements(By.TAG_NAME, 'a')[:50]:
        txt = (a.text or '').strip()
        if txt:
            print(repr(txt[:120]))
    print('BODY TEXT')
    print((d.find_element(By.TAG_NAME, 'body').text or '')[:2000])
finally:
    d.quit()
