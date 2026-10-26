from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

BASE_URL = 'https://engineering.ultrivalms.com/QALS1011'
USERNAME = 'buyeruser'
PASSWORD = 'Ultriva!23'

opt = webdriver.ChromeOptions()
opt.add_argument('--no-sandbox')
opt.add_argument('--disable-dev-shm-usage')
opt.add_argument('--disable-gpu')
opt.add_argument('--start-maximized')
opt.add_experimental_option('excludeSwitches', ['enable-logging'])

d = webdriver.Chrome(options=opt)
d.set_page_load_timeout(30)
try:
    d.get(BASE_URL)
    time.sleep(2)
    d.find_element(By.ID, 'UserName').clear()
    d.find_element(By.ID, 'UserName').send_keys(USERNAME)
    d.find_element(By.ID, 'Password').clear()
    d.find_element(By.ID, 'Password').send_keys(PASSWORD)
    d.find_element(By.ID, 'login-button').click()
    WebDriverWait(d, 20).until(lambda x: 'Home' in x.current_url or 'QALS1011' in x.current_url)
    print('LOGIN_URL', d.current_url)

    actions = WebDriverWait(d, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'Action/Home') or normalize-space(.)='Actions']"))
    )
    actions.click()
    time.sleep(3)
    print('AFTER_ACTIONS', d.current_url)

    matches = d.execute_script("""
        return Array.from(document.querySelectorAll('*')).filter(el => {
            const t = (el.textContent || '').replace(/\s+/g, ' ').trim();
            return /Adjust Inventory/i.test(t) || /AdjustInventory/i.test((el.getAttribute('href') || '')) || /AdjustInventory/i.test((el.getAttribute('id') || ''));
        }).slice(0, 30).map(el => ({
            tag: el.tagName,
            txt: (el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 200),
            href: el.getAttribute('href'),
            id: el.getAttribute('id'),
            cls: el.getAttribute('class'),
            onclick: el.getAttribute('onclick'),
            outer: el.outerHTML.slice(0, 300).replace(/\s+/g, ' ')
        }));
    """)
    print('MATCH_COUNT', len(matches))
    for i, m in enumerate(matches, 1):
        print('---', i)
        for k, v in m.items():
            print(k, ':', v)

    for url in [
        BASE_URL + '/Scan/AdjustInventory',
        BASE_URL + '/BuyerAction/AdjustInventoryItems',
        BASE_URL + '/BuyerAction/AdjustInventoryCards',
        BASE_URL + '/BuyerAction/AdjustInventory',
        BASE_URL + '/Scan/AdjustInventoryItems',
    ]:
        try:
            d.get(url)
            time.sleep(2)
            print('TRY_URL', url, '->', d.current_url)
            print('TITLE', d.title)
            print('BODY_SNIP', (d.find_element(By.TAG_NAME, 'body').text or '')[:500])
        except Exception as e:
            print('URL_ERROR', url, type(e).__name__, e)
finally:
    d.quit()
