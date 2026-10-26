from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

BASE_URL = 'https://engineering.ultrivalms.com/QALS1011'
USERNAME = 'supnewuser'
PASSWORD = 'Ultriva!23'

opts = webdriver.ChromeOptions()
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')
opts.add_argument('--disable-gpu')
opts.add_argument('--start-maximized')
opts.add_experimental_option('excludeSwitches', ['enable-logging'])

d = webdriver.Chrome(options=opts)
d.implicitly_wait(10)
d.set_page_load_timeout(60)
d.maximize_window()

try:
    d.get(f'{BASE_URL}/Account/Login')
    WebDriverWait(d, 20).until(lambda x: x.execute_script('return document.readyState') == 'complete')
    d.find_element(By.ID, 'UserName').send_keys(USERNAME)
    d.find_element(By.ID, 'Password').send_keys(PASSWORD)
    d.find_element(By.ID, 'login-button').click()
    time.sleep(3)

    actions = d.find_elements(By.XPATH, "//*[contains(@title, 'Actions') or normalize-space(.)='Actions' or contains(@href, '/Action/Home')]")
    print('ACTIONS MATCHES', len(actions))
    for el in actions[:20]:
        txt = (el.text or '').strip()
        href = el.get_attribute('href')
        title = el.get_attribute('title')
        print('ACTION NODE', txt, 'href=', href, 'title=', title, 'tag=', el.tag_name)
        if 'Actions' in (txt or '') or title == 'Actions':
            el.click(); break
    time.sleep(3)

    # dump all links containing Action or Reschedule after login
    links = d.find_elements(By.XPATH, "//a[contains(@href, 'Action') or contains(@href, 'Reschedule') or contains(normalize-space(.), 'Reschedule') or contains(normalize-space(.), 'Action')]")
    print('LINKS WITH RESCHEDULE/ACTION', len(links))
    for idx, el in enumerate(links[:80]):
        txt = (el.text or '').strip()
        href = el.get_attribute('href')
        print(idx, 'TEXT=', txt[:120], 'HREF=', href)

    # Try the likely direct route from app structure
    for path in [
        '/QALS1011/Action/Home',
        '/QALS1011/SupplierAction/RescheduleRequestItems',
        '/QALS1011/SupplierAction/SupplierRescheduleItems',
        '/QALS1011/SupplierAction/RescheduleItems',
        '/QALS1011/Action/RescheduleRequestItems',
    ]:
        try:
            d.get(f'{BASE_URL}{path}')
            print('VISITED', path, 'URL=', d.current_url)
            time.sleep(3)
        except Exception as e:
            print('ERR visit', path, e)

finally:
    d.quit()
