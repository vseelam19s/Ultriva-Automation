from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

BASE='https://engineering.ultrivalms.com/QALS1011'
USERNAME='supnewuser'
PASSWORD='Ultriva!23'

opts=webdriver.ChromeOptions()
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')
opts.add_argument('--disable-gpu')
opts.add_argument('--start-maximized')
opts.add_experimental_option('excludeSwitches', ['enable-logging'])
d=webdriver.Chrome(options=opts)
try:
    d.get(f'{BASE}/Account/Login')
    WebDriverWait(d,30).until(lambda x: x.execute_script('return document.readyState')=='complete')
    d.find_element(By.ID,'UserName').send_keys(USERNAME)
    d.find_element(By.ID,'Password').send_keys(PASSWORD)
    d.find_element(By.ID,'login-button').click()
    WebDriverWait(d,30).until(lambda x: 'QALS1011' in x.current_url)
    time.sleep(2)
    d.get(f'{BASE}/SupplierAction/SetWorkOrderNoItems')
    WebDriverWait(d,30).until(lambda x: 'SetWorkOrderNoItems' in x.current_url)
    time.sleep(2)
    rows=d.find_elements(By.XPATH,'//tr[.//td and not(.//th)]')
    print('rows', len(rows))
    if rows:
        rows[0].click()
        time.sleep(2)
        elems=d.find_elements(By.XPATH, "//*[contains(normalize-space(.),'Show Cards') or contains(normalize-space(.),'Select Cards')]")
        print('show_cards_count', len(elems))
        for e in elems[:10]:
            print('show card text', repr((e.text or '').strip()), 'visible', e.is_displayed(), 'enabled', e.is_enabled())
        if elems:
            try:
                elems[0].click();
            except Exception:
                d.execute_script('arguments[0].click();', elems[0])
            time.sleep(4)
    print('URL after show cards', d.current_url)
    time.sleep(2)
    checkboxes=d.find_elements(By.XPATH, "//input[@type='checkbox' and not(@disabled)]")
    print('cb count', len(checkboxes))
    for i,cb in enumerate(checkboxes[:10]):
        print('checkbox', i, 'selected', cb.is_selected(), 'visible', cb.is_displayed(), 'id', cb.get_attribute('id'))
    if checkboxes:
        try:
            checkboxes[0].click()
        except Exception:
            d.execute_script('arguments[0].click();', checkboxes[0])
        time.sleep(1)
    elems = d.find_elements(By.XPATH, "//input")
    print('input count', len(elems))
    for i,e in enumerate(elems[:80]):
        txt = e.get_attribute('placeholder') or e.get_attribute('value') or e.get_attribute('name') or e.get_attribute('id') or ''
        if any(k in txt.lower() for k in ['work','order','find','search','txt','value']):
            print(i, 'input', txt, 'visible', e.is_displayed(), 'enabled', e.is_enabled())
    work = None
    for by, loc in [
        (By.XPATH, "//*[@id='workOrderNumber' or @name='workOrderNumber' or contains(@id,'workOrderNumber') or contains(@name,'workOrderNumber')]") ,
        (By.XPATH, "//input[contains(@placeholder,'Work Order Number') or contains(@title,'Work Order Number') or contains(@aria-label,'Work Order Number') or contains(@placeholder,'WO Number') or contains(@title,'WO Number') or contains(@aria-label,'WO Number')]"),
        (By.XPATH, "//input[contains(@name,'WorkOrder') or contains(@id,'WorkOrder') or contains(@name,'WONumber') or contains(@id,'WONumber')]"),
    ]:
        matches = d.find_elements(*((by,loc) if False else (by,loc)))
        print('match candidates', loc, len(matches))
        for m in matches[:10]:
            print('match', m.get_attribute('id'), m.get_attribute('name'), m.get_attribute('placeholder'), 'visible', m.is_displayed(), 'enabled', m.is_enabled())
        if matches:
            work = matches[0]; break
    if work is not None:
        work.clear(); work.send_keys('121212'); time.sleep(1)
        print('value now', work.get_attribute('value'))
    for xp in [
        "//*[contains(normalize-space(.), 'Apply To All')]",
        "//*[contains(normalize-space(.), 'Apply to All')]",
        "//*[contains(normalize-space(.), 'Apply All')]",
        "//*[contains(normalize-space(.), 'Apply')]",
        "//button",
        "//span",
        "//div",
    ]:
        found = d.find_elements(By.XPATH, xp)
        print('xpath', xp, 'count', len(found))
        for i,e in enumerate(found[:30]):
            txt = (e.text or e.get_attribute('value') or '').strip()
            if 'Apply' in txt or 'Work Order' in txt or 'Set WorkOrder' in txt or txt.strip():
                print(i, e.tag_name, repr(txt[:200]), 'visible', e.is_displayed(), 'enabled', e.is_enabled(), 'id', e.get_attribute('id'))
finally:
    d.quit()
