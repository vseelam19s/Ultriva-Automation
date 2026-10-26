import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = 'https://engineering.ultrivalms.com/QALS1011'
USERNAME = 'buyeruser'
PASSWORD = 'Ultriva!23'

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--start-maximized')
options.add_experimental_option('excludeSwitches', ['enable-logging'])


def wait_ready(driver, timeout=30):
    WebDriverWait(driver, timeout).until(lambda d: d.execute_script('return document.readyState') == 'complete')


for label, func in [('start', lambda d: None)]:
    pass

d = webdriver.Chrome(options=options)
d.set_page_load_timeout(40)
try:
    print('[1] Login')
    d.get(BASE_URL)
    wait_ready(d)
    d.find_element(By.ID, 'UserName').clear(); d.find_element(By.ID, 'UserName').send_keys(USERNAME)
    d.find_element(By.ID, 'Password').clear(); d.find_element(By.ID, 'Password').send_keys(PASSWORD)
    d.find_element(By.ID, 'login-button').click()
    time.sleep(2)
    WebDriverWait(d, 20).until(lambda x: 'Home' in x.current_url or 'QALS1011' in x.current_url)
    print('After login URL:', d.current_url)

    print('[2] Open Actions page')
    actions_link = WebDriverWait(d, 15).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'Action/Home') or (.//span[normalize-space()='Actions']) or normalize-space(.)='Actions']")))
    actions_link.click(); time.sleep(2)
    wait_ready(d)
    print('Actions URL:', d.current_url)

    print('[3] Open Adjust Inventory')
    adjust_inv_link = None
    for locator in [
        (By.XPATH, "//*[self::a or self::div or self::span or self::button][contains(normalize-space(.),'Adjust Inventory')]"),
        (By.XPATH, "//a[contains(@href,'AdjustInventory') and not(contains(@class,'toplinks'))]"),
        (By.XPATH, "//a[contains(normalize-space(),'Adjust Inventory') and not(contains(@class,'toplinks'))]"),
        (By.XPATH, "//a[contains(@href,'AdjustInventory')]"),
    ]:
        try:
            adjust_inv_link = WebDriverWait(d, 8).until(EC.element_to_be_clickable(locator))
            print('Found link by', locator)
            break
        except Exception:
            continue
    print('Adjust link selected?', bool(adjust_inv_link), 'URL now=', d.current_url)
    if adjust_inv_link is None:
        d.get(f'{BASE_URL}/BuyerAction/AdjustInventoryItems')
        wait_ready(d)
        print('Fallback URL after direct GET:', d.current_url)
    else:
        adjust_inv_link.click(); time.sleep(2); wait_ready(d)
        print('After clicking Adjust URL:', d.current_url)

    # Try Go button logic
    try:
        go = WebDriverWait(d, 8).until(EC.element_to_be_clickable((By.ID, 'imgMatStatusGo')))
        print('Found Go button id=imgMatStatusGo')
        go.click(); time.sleep(2); wait_ready(d)
        print('After Go URL:', d.current_url)
    except Exception:
        print('No Go button id=imgMatStatusGo')

    try:
        item_links = WebDriverWait(d, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class,'GridLink')]")))
        print('Found item links count=', len(item_links))
    except Exception as e:
        print('NO ITEM LINKS after wait. Current URL=', d.current_url)
        print('Page source contains AdjustInventory?', 'AdjustInventory' in d.page_source)
        print('Page title=', d.title)
        for selector in [
            "//a[contains(@class,'GridLink')]",
            "//a[contains(@href,'AdjustInventory')]",
            "//*[contains(normalize-space(.),'Adjust Inventory')]",
            "//*[@id='imgMatStatusGo']",
            "//span[contains(normalize-space(.),'Adjust Inventory')]",
        ]:
            els = d.find_elements(By.XPATH, selector)
            print('Selector', selector, 'count=', len(els))
            for e in els[:5]:
                try:
                    print(' -> tag=', e.tag_name, 'text=', (e.text or '')[:80], 'id=', e.get_attribute('id'), 'class=', e.get_attribute('class'))
                except Exception:
                    pass
        raise
    print('Ready to select item')
    first = item_links[0]
    first.click(); time.sleep(2); wait_ready(d)
    print('After click item URL=', d.current_url)
    print('Has cards page?', 'AdjustInventoryCard' in d.current_url or 'AdjustInventoryCards' in d.current_url)

finally:
    d.quit()
