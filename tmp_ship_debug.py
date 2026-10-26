from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
import time
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox'); options.add_argument('--disable-dev-shm-usage'); options.add_argument('--disable-gpu'); options.add_argument('--start-maximized'); options.add_experimental_option('excludeSwitches',['enable-logging'])
d = webdriver.Chrome(options=options)
d.implicitly_wait(10); d.set_page_load_timeout(40); d.maximize_window()
try:
    d.get('https://engineering.ultrivalms.com/QALS1011/Account/Login')
    WebDriverWait(d, 20).until(lambda x: x.execute_script('return document.readyState') == 'complete')
    d.find_element(By.ID, 'UserName').send_keys('supnewuser')
    d.find_element(By.ID, 'Password').send_keys('Ultriva!23')
    d.find_element(By.ID, 'login-button').click()
    time.sleep(3)
    d.get('https://engineering.ultrivalms.com/QALS1011/SupplierAction/ShipCards')
    WebDriverWait(d, 25).until(lambda x: x.execute_script('return document.readyState') == 'complete')
    time.sleep(4)
    print('URL:', d.current_url)
    # inspect row checkboxes
    row_checkboxes = d.find_elements(By.XPATH, "//input[@type='checkbox' and contains(@name, 'CheckboxCardGID')]")
    print('row checkbox count=', len(row_checkboxes))
    for i, cb in enumerate(row_checkboxes[:5]):
        print('checkbox', i, 'name=', cb.get_attribute('name'), 'value=', cb.get_attribute('value'), 'selected=', cb.is_selected(), 'displayed=', cb.is_displayed())
    # click first row checkbox for visibility of row controls
    if row_checkboxes:
        d.execute_script('arguments[0].click();', row_checkboxes[0])
        time.sleep(1)
    # find by text identifiers for buttons/links in DOM
    elements = d.find_elements(By.XPATH, '//button | //a | //span | //input')
    hits = []
    for e in elements:
        txt = (e.text or e.get_attribute('value') or '').strip().replace('\n', ' ')
        low = txt.lower()
        if any(k in low for k in ['ship', 'attach', 'back to items', 'change filter', 'save', 'confirm', 'notes', 'logistics', 'packing']):
            hits.append((txt[:120], e.tag_name, e.get_attribute('class') or '', e.get_attribute('id') or '', e.get_attribute('name') or '', e.is_displayed(), e.is_enabled()))
    print('interesting elements count=', len(hits))
    for h in hits[:120]:
        print(h)
    # find ids / names of all visible inputs with ship or packing or logistics in name
    for e in d.find_elements(By.XPATH, '//input'):
        name = e.get_attribute('name') or ''
        id_ = e.get_attribute('id') or ''
        val = e.get_attribute('value') or ''
        typ = e.get_attribute('type') or ''
        if 'Ship' in name or 'Packing' in name or 'Logistics' in name or 'Charge' in name or 'Tracking' in name or 'Carrier' in name or 'ShipCards' in name:
            print('input', typ, name, id_, val[:40], 'displayed=', e.is_displayed(), 'enabled=', e.is_enabled())
    # Find submit buttons in page source around ship actions
    for xp in [
        "//*[contains(normalize-space(.), 'Ship')]",
        "//*[contains(normalize-space(.), 'Back To Items')]",
        "//*[contains(normalize-space(.), 'Attach Notes')]",
        "//*[contains(normalize-space(.), 'Change Filter')]",
        "//*[contains(normalize-space(.), 'Apply Notes')]",
        "//*[contains(normalize-space(.), 'Save')]",
        "//*[contains(normalize-space(.), 'Submit')]",
    ]:
        els = d.find_elements(By.XPATH, xp)
        print('xpath', xp, 'count=', len(els))
        for e in els[:25]:
            txt = (e.text or e.get_attribute('value') or '').strip().replace('\n', ' ')
            print('  -', txt[:120], 'tag=', e.tag_name, 'classes=', (e.get_attribute('class') or '')[:80], 'displayed=', e.is_displayed(), 'enabled=', e.is_enabled())
finally:
    d.quit()
