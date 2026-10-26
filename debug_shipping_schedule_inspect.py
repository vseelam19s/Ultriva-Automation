from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

opts = webdriver.ChromeOptions()
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')
opts.add_argument('--disable-gpu')
opts.add_argument('--start-maximized')
opts.add_experimental_option('excludeSwitches', ['enable-logging'])

d = webdriver.Chrome(options=opts)
d.implicitly_wait(10)
d.set_page_load_timeout(40)
try:
    d.get('https://engineering.ultrivalms.com/QALS1011/Account/Login')
    WebDriverWait(d, 20).until(EC.presence_of_element_located((By.ID, 'UserName')))
    d.find_element(By.ID, 'UserName').send_keys('supnewuser')
    d.find_element(By.ID, 'Password').send_keys('Ultriva!23')
    d.find_element(By.ID, 'login-button').click()
    time.sleep(4)
    d.get('https://engineering.ultrivalms.com/QALS1011/SupplierAction/ManageShipQuantitiesItems')
    time.sleep(4)
    rows = d.find_elements(By.XPATH, '//tr[td or a or span]')
    print('ROW_COUNT', len(rows))
    for idx, row in enumerate(rows[:40]):
        txt = (row.text or '').replace('\n', ' | ')
        if txt.strip():
            print('ROW', idx, txt[:220])
    target = None
    for idx, row in enumerate(rows):
        try:
            txt = (row.text or '').replace('\n', ' | ')
            low = txt.lower()
            if 'schedule' in low or 'ship' in low:
                target = row
                print('TARGET_ROW', idx, txt[:200])
                break
        except Exception:
            pass
    if target is None:
        target = rows[0]
    try:
        target.click()
        print('CLICKED_TARGET_ROW')
    except Exception as e:
        print('TARGET_CLICK_ERR', e)
    time.sleep(2)
    print('URL_AFTER_ROW', d.current_url)
    show_candidates = d.find_elements(By.XPATH, "//*[contains(normalize-space(.), 'Show Cards') or contains(normalize-space(.), 'Show cards') or contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'show cards') or contains(@id,'ShowCards') or contains(@id,'showCards') or contains(@onclick,'ShowCards') or contains(@onclick,'showCards')]")
    print('SHOW_COUNT', len(show_candidates))
    for c in show_candidates[:50]:
        try:
            text = (c.text or '').strip()
            print('SHOW', repr(text[:120]), 'id=', c.get_attribute('id'), 'cls=', c.get_attribute('class'), 'tag=', c.tag_name)
        except Exception as e:
            print('ERR_SHOW', e)
    if show_candidates:
        try:
            show_candidates[0].click(); time.sleep(3)
            print('URL_AFTER_SHOW', d.current_url)
        except Exception as e:
            print('SHOW_CLICK_ERR', type(e), e)
    time.sleep(2)
    all_els = d.find_elements(By.XPATH, '//*')
    matches = []
    for el in all_els:
        txt = (el.text or '').strip()
        low = txt.lower()
        if any(s in low for s in ['ship', 'schedule', 'date', 'qty', 'done', 'card', 'item']):
            matches.append((txt[:120], el.tag_name, el.get_attribute('id'), el.get_attribute('class')))
    print('MATCH_COUNT', len(matches))
    for m in matches[:200]:
        print('MATCH', m)
    print('BODY', (d.find_element(By.TAG_NAME,'body').text or '')[:5000])
finally:
    d.quit()
