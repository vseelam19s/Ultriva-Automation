from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--start-maximized')
options.add_experimental_option('excludeSwitches', ['enable-logging'])

d = webdriver.Chrome(options=options)
d.implicitly_wait(10)
d.set_page_load_timeout(60)

try:
    d.get('https://engineering.ultrivalms.com/QALS1011/Account/Login')
    WebDriverWait(d, 25).until(lambda x: x.execute_script('return document.readyState') == 'complete')

    d.find_element(By.ID, 'UserName').clear()
    d.find_element(By.ID, 'UserName').send_keys('supnewuser')
    d.find_element(By.ID, 'Password').clear()
    d.find_element(By.ID, 'Password').send_keys('Ultriva!23')
    login = d.find_element(By.ID, 'login-button')
    d.execute_script('arguments[0].click();', login)
    WebDriverWait(d, 25).until(lambda x: 'Home' in x.current_url or 'QALS1011' in x.current_url)
    print('LOGIN_URL', d.current_url)

    d.get('https://engineering.ultrivalms.com/QALS1011/SupplierAction/InvoiceCreation')
    WebDriverWait(d, 25).until(lambda x: 'InvoiceCreation' in x.current_url)
    time.sleep(5)

    print('INVOICE_URL', d.current_url)
    print('TITLE', d.title)

    elements = d.find_elements(By.XPATH, "//*[@id or @name or @class or @value]")
    print('TOTAL_ATTR_ELEMENTS', len(elements))

    matches = []
    for el in elements[:500]:
        text = (el.text or '').strip()
        attrs = []
        for attr in ['id', 'name', 'class', 'value', 'onclick', 'href']:
            v = el.get_attribute(attr)
            if v:
                attrs.append(f'{attr}={v[:120]}')
        s = ' | '.join(attrs)
        if not s:
            continue
        low = (text + ' ' + s).lower()
        if any(token in low for token in ['invoice', 'create', 'item', 'select', 'confirm', 'checkbox', 'supplier', 'po', 'action']):
            matches.append((el.tag_name, text[:120], s[:200]))

    print('MATCH_COUNT', len(matches))
    for tag, text, s in matches[:120]:
        print('---')
        print(tag, repr(text))
        print(s)

    print('\nCHECKBOX IDS/NAMES/CLASSES')
    for sel in ['input[type="checkbox"]', 'input[type="radio"]', 'input[type="text"]', 'select', 'button', 'a', 'span']:
        arr = d.find_elements(By.CSS_SELECTOR, sel)
        print(sel, len(arr))
        for i, el in enumerate(arr[:20]):
            txt = (el.text or '').strip()
            print(' ', i, el.tag_name, 'id=', el.get_attribute('id'), 'name=', el.get_attribute('name'), 'class=', el.get_attribute('class'), 'value=', el.get_attribute('value'), 'txt=', repr(txt[:80]))

    print('\nALL TR TEXTS')
    rows = d.find_elements(By.TAG_NAME, 'tr')
    for i, r in enumerate(rows[:40]):
        txt = (r.text or '').replace('\n', ' | ').strip()
        if txt:
            print(i, repr(txt[:300]))

    print('\nPAGE_SNIP')
    src = d.page_source
    low = src.lower()
    for token in ['create invoice', 'confirm and create invoice', 'invoice creation', 'select item', 'item number', 'checkbox', 'supplieraction', 'invoice']:
        idx = low.find(token)
        if idx != -1:
            print('\nTOKEN', token)
            print(src[max(0, idx-500):min(len(src), idx+1500)])

finally:
    d.quit()
