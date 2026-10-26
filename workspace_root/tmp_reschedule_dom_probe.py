from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

BASE_URL='https://engineering.ultrivalms.com/QALS1011'
USERNAME='supnewuser'
PASSWORD='Ultriva!23'

opts = webdriver.ChromeOptions()
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')
opts.add_argument('--disable-gpu')
opts.add_argument('--start-maximized')
opts.add_experimental_option('excludeSwitches', ['enable-logging'])

d = webdriver.Chrome(options=opts)
d.implicitly_wait(10)
d.set_page_load_timeout(60)

try:
    d.get(f'{BASE_URL}/Account/Login')
    WebDriverWait(d, 25).until(lambda x: x.execute_script('return document.readyState') == 'complete')
    d.find_element(By.ID, 'UserName').send_keys(USERNAME)
    d.find_element(By.ID, 'Password').send_keys(PASSWORD)
    d.find_element(By.ID, 'login-button').click()
    time.sleep(4)

    def click_label(label):
        locators = [
            (By.XPATH, f"//*[self::a or self::button or self::span or self::div or self::li][contains(normalize-space(.), '{label}')]"),
            (By.XPATH, f"//*[@title='{label}' or @aria-label='{label}']"),
            (By.XPATH, f"//*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{label.lower()}')]"),
        ]
        for by, xp in locators:
            els = d.find_elements(by, xp)
            for el in els:
                if el.is_displayed() and el.is_enabled():
                    try:
                        el.click()
                        print('CLICKED', label, 'tag=', el.tag_name, 'txt=', (el.text or '')[:80], 'href=', el.get_attribute('href'))
                        return True
                    except Exception:
                        try:
                            d.execute_script('arguments[0].click()', el)
                            print('JS CLICKED', label, 'tag=', el.tag_name)
                            return True
                        except Exception:
                            pass
        return False

    print('URL after login:', d.current_url)
    click_label('Actions')
    time.sleep(2)
    click_label('Reschedule Request')
    time.sleep(5)
    print('URL after reschedule request click:', d.current_url)

    rows = d.find_elements(By.XPATH, '//tr[.//td and not(.//th)]')
    print('ROW COUNT', len(rows))
    for idx, row in enumerate(rows[:5]):
        print('ROW', idx, 'TEXT', (row.text or '')[:200].replace('\n', ' | '))

    if rows:
        rows[0].click()
        time.sleep(2)
    click_label('Show Cards')
    time.sleep(5)
    print('URL after Show Cards:', d.current_url)

    inputs = d.find_elements(By.XPATH, '//input')
    print('TOTAL INPUT COUNT', len(inputs))
    for i, el in enumerate(inputs[:200]):
        typ = (el.get_attribute('type') or '').lower()
        iid = el.get_attribute('id') or ''
        name = el.get_attribute('name') or ''
        cls = el.get_attribute('class') or ''
        val = el.get_attribute('value') or ''
        if typ or iid or name or cls:
            print(i, {'type': typ, 'id': iid, 'name': name, 'class': cls[:120], 'value': val[:80], 'checked': el.get_attribute('checked')})

    # Print any likely checkbox-like elements from DOM
    for xp in [
        "//input[@type='checkbox']",
        "//*[contains(@id,'Checkbox') or contains(@name,'Checkbox') or contains(@class,'GridCheckbox') or contains(@class,'checkbox')]",
        "//table//input",
        "//div[contains(@class,'Grid') or contains(@class,'grid') or contains(@class,'Card') or contains(@id,'Card')]",
    ]:
        els = d.find_elements(By.XPATH, xp)
        print('XPATH', xp, 'COUNT', len(els))
        for e in els[:20]:
            print('  tag=', e.tag_name, 'id=', e.get_attribute('id'), 'name=', e.get_attribute('name'), 'class=', (e.get_attribute('class') or '')[:120], 'outer=', (e.get_attribute('outerHTML') or '')[:220])

    html = d.page_source
    for token in ['GridCheckbox','CheckboxCard','CheckBox','ApplyNotesToAll','Reschedule Reason','New Reqd Ship Date','btnReschedule']:
        idx = html.find(token)
        print('TOKEN', token, 'IDX', idx)
        if idx != -1:
            print(html[idx-250:idx+600])
            print('---')
finally:
    d.quit()
