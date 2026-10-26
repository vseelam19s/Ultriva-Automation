from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

BASE_URL = 'https://engineering.ultrivalms.com/QALS1011'
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
    WebDriverWait(d, 20).until(lambda x: x.execute_script('return document.readyState') == 'complete')
    d.find_element(By.ID, 'UserName').send_keys('buyeruser')
    d.find_element(By.ID, 'Password').send_keys('Ultriva!23')
    d.find_element(By.ID, 'login-button').click()
    time.sleep(2)
    d.get(f'{BASE_URL}/BuyerAction/AdjustInventoryItems')
    time.sleep(2)
    try:
        WebDriverWait(d, 8).until(EC.element_to_be_clickable((By.ID, 'imgMatStatusGo'))).click(); time.sleep(2)
    except Exception:
        pass
    items = d.find_elements(By.XPATH, "//a[contains(@class,'GridLink')]")
    items[0].click(); time.sleep(2)
    cbs = WebDriverWait(d, 15).until(EC.presence_of_all_elements_located((By.XPATH, "//input[@type='checkbox']")))
    for c in cbs[:2]:
        if not c.is_selected():
            d.execute_script('arguments[0].click()', c)
    # print any element binding to onclick or containing Adjust/Inventory in id/class/name
    xpaths = [
        "//*[@onclick]",
        "//*[contains(@id,'Adjust') or contains(@id,'Inventory') or contains(@name,'Adjust') or contains(@name,'Inventory') or contains(@class,'Adjust') or contains(@class,'Inventory')]",
        "//*[contains(@onclick,'Adjust') or contains(@onclick,'Inventory') or contains(@onclick,'Save') or contains(@onclick,'Submit') or contains(@onclick,'Update')]",
    ]
    seen = set()
    for xp in xpaths:
        els = d.find_elements(By.XPATH, xp)
        print('\nXPATH', xp, 'COUNT', len(els))
        for el in els[:80]:
            tag = el.tag_name.lower()
            ident = el.get_attribute('id') or ''
            name = el.get_attribute('name') or ''
            cls = el.get_attribute('class') or ''
            txt = (el.text or '').strip()
            value = (el.get_attribute('value') or '').strip()
            onclick = (el.get_attribute('onclick') or '').strip()
            key = (tag, ident, name, cls, txt, value, onclick)
            if key in seen:
                continue
            seen.add(key)
            print({'tag': tag, 'id': ident, 'name': name, 'class': cls[:120], 'text': txt[:80], 'value': value[:80], 'onclick': onclick[:200]})
finally:
    d.quit()
