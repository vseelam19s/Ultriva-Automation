from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import string

BASE_URL = 'https://engineering.ultrivalms.com/QALS1011'


def wait_ready(driver, timeout=30):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script('return document.readyState') == 'complete'
    )


def safe_click(driver, element):
    try:
        element.click()
        return
    except Exception:
        try:
            driver.execute_script('arguments[0].click()', element)
        except Exception:
            pass


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
    d.get(f'{BASE_URL}/BuyerAction/AdjustInventoryItems')
    wait_ready(d)
    time.sleep(2)
    try:
        b = WebDriverWait(d, 6).until(EC.element_to_be_clickable((By.ID, 'imgMatStatusGo')))
        b.click()
        wait_ready(d)
        time.sleep(2)
    except Exception:
        pass

    items = d.find_elements(By.XPATH, "//a[contains(@class,'GridLink')]")
    first = items[0]
    first.click(); wait_ready(d); time.sleep(2)
    print('URL AFTER ITEM', d.current_url)
    checkboxes = WebDriverWait(d, 15).until(EC.presence_of_all_elements_located((By.XPATH, "//input[@type='checkbox']")))
    for c in checkboxes[:2]:
        if not c.is_selected():
            safe_click(d, c)
    loc = d.find_elements(By.XPATH, "//input[contains(@id,'CurrentLocation') or contains(@name,'CurrentLocation') or contains(@id,'Location') or contains(@name,'Location')]")
    if loc:
        loc[0].clear(); loc[0].send_keys('LOC-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=5)))
    qty = d.find_elements(By.XPATH, "//input[contains(@id,'AdjustQty') or contains(@name,'AdjustQty') or contains(@id,'AdjustQuantity') or contains(@name,'AdjustQuantity')]")
    for q in qty[:2]:
        q.clear(); q.send_keys('100')

    print('MATCHING ADJUST/INVENTORY ELEMENTS:')
    js = """
    return Array.from(document.querySelectorAll('*')).filter(el => {
      const text = (el.textContent || '').trim();
      const value = (el.value || '').trim();
      const id = (el.id || '').trim();
      const cls = (el.className || '').toString();
      const name = (el.name || '').trim();
      const title = (el.title || '').trim();
      const label = [text, value, id, cls, name, title].join(' ').toLowerCase();
      return label.includes('adjust') || label.includes('inventory') || label.includes('save') || label.includes('submit') || label.includes('update') || label.includes('apply');
    }).map(el => ({
      tag: el.tagName,
      text: (el.textContent || '').trim().slice(0, 120),
      value: (el.value || '').trim(),
      id: el.id || '',
      className: el.className || '',
      name: el.name || '',
      title: el.title || '',
      outer: (el.outerHTML || '').slice(0, 220)
    }));
    """
    matches = d.execute_script(js)
    print('COUNT', len(matches))
    for item in matches[:200]:
        print(item)
    print('--- SCRIPT SOURCE SEARCH ---')
    src = d.page_source.lower()
    for token in ['adjust', 'inventory', 'save', 'submit', 'update', 'apply', 'ok']:
        idx = src.find(token)
        if idx != -1:
            print('TOKEN', token, 'AT', idx)
            print(d.page_source[idx:idx+500])
finally:
    d.quit()
