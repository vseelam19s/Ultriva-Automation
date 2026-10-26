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
    print('URL AFTER ACTIONS', d.current_url)

    inv = WebDriverWait(d, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'AdjustInventory') or contains(normalize-space(.),'Adjust Inventory')]"))
    )
    inv.click()
    wait_ready(d)
    time.sleep(2)
    print('URL AFTER INV', d.current_url)

    for by, locator in [
        (By.ID, 'imgMatStatusGo'),
        (By.XPATH, "//button[normalize-space(.)='Go']"),
        (By.XPATH, "//input[@type='submit' and @value='Go']"),
        (By.XPATH, "//a[normalize-space(.)='Go']"),
        (By.XPATH, "//*[@id='btnGo' or @id='go-button' or @id='goBtn']"),
    ]:
        try:
            b = WebDriverWait(d, 6).until(EC.element_to_be_clickable((by, locator)))
            print('FOUND GO', by, locator)
            b.click()
            wait_ready(d)
            time.sleep(2)
            break
        except Exception:
            pass

    print('URL AFTER GO', d.current_url)
    item_links = WebDriverWait(d, 20).until(
        EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class,'GridLink')]"))
    )
    print('ITEM COUNT', len(item_links))
    print('ITEM TEXTS', [x.text.strip()[:80] for x in item_links[:10]])
    first = item_links[0]
    print('FIRST ITEM', first.text)
    first.click()
    wait_ready(d)
    time.sleep(2)
    print('URL AFTER ITEM CLICK', d.current_url)
    body_text = (d.find_element(By.TAG_NAME, 'body').text or '')[:4000]
    print('BODY TEXT START')
    print(body_text)
finally:
    d.quit()
