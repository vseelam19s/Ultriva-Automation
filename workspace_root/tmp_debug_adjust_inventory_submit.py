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
    d.find_element(By.ID, 'UserName').send_keys('buyeruser')
    d.find_element(By.ID, 'Password').send_keys('Ultriva!23')
    d.find_element(By.ID, 'login-button').click()
    time.sleep(2)
    WebDriverWait(d, 20).until(lambda x: 'Home' in x.current_url or 'QALS1011' in x.current_url)

    d.get(f'{BASE_URL}/BuyerAction/AdjustInventoryItems')
    time.sleep(2)
    try:
        btn = WebDriverWait(d, 8).until(EC.element_to_be_clickable((By.ID, 'imgMatStatusGo')))
        btn.click(); time.sleep(2)
    except Exception:
        pass

    items = d.find_elements(By.XPATH, "//a[contains(@class,'GridLink')]")
    print('ITEM_COUNT', len(items))
    if not items:
        print('CURRENT URL', d.current_url)
        print(d.page_source[:2000])
        raise SystemExit

    items[0].click(); time.sleep(2)
    checkboxes = WebDriverWait(d, 15).until(EC.presence_of_all_elements_located((By.XPATH, "//input[@type='checkbox']")))
    print('CHECKBOXES', len(checkboxes))
    for c in checkboxes[:2]:
        if not c.is_selected():
            c.click(); time.sleep(0.2)

    qtys = d.find_elements(By.XPATH, "//input[contains(@id,'AdjustQty') or contains(@name,'AdjustQty') or contains(@id,'AdjustQuantity') or contains(@name,'AdjustQuantity')]")
    locs = d.find_elements(By.XPATH, "//input[contains(@id,'CurrentLocation') or contains(@name,'CurrentLocation') or contains(@id,'Location') or contains(@name,'Location')]")
    print('QTY_COUNT', len(qtys), 'LOC_COUNT', len(locs))
    if qtys:
        qtys[0].clear(); qtys[0].send_keys('100')
    if locs:
        locs[0].clear(); locs[0].send_keys('LOC-DEBUG')

    js = """
    const candidates = Array.from(document.querySelectorAll('button,input,a,span,div')).filter(el => {
      const text = (el.textContent || '').trim();
      const id = (el.id || '').trim();
      const name = (el.name || '').trim();
      const value = (el.value || '').trim();
      const className = (el.className || '').toString();
      const hay = [text, id, name, value, className].join(' ').toLowerCase();
      return /adjust|inventory|save|submit|update|apply|ok|go/.test(hay);
    });
    return candidates.slice(0,200).map(el => ({
      tag: el.tagName,
      id: el.id || '',
      name: el.name || '',
      value: el.value || '',
      text: (el.textContent || '').trim().slice(0, 80),
      className: (el.className || '').toString().slice(0, 80),
      outer: (el.outerHTML || '').slice(0, 260)
    }));
    """
    result = d.execute_script(js)
    print('CANDIDATE_COUNT', len(result))
    for entry in result[:80]:
        print(entry)
    print('CURRENT_URL', d.current_url)
finally:
    d.quit()
