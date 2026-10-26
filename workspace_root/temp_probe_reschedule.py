from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
import time

BASE_URL = 'https://engineering.ultrivalms.com/QALS1011'
USERNAME = 'supnewuser'
PASSWORD = 'Ultriva!23'


def wait_ready(driver, timeout=30):
    WebDriverWait(driver, timeout).until(lambda d: d.execute_script('return document.readyState') == 'complete')


options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--start-maximized')
options.add_experimental_option('excludeSwitches', ['enable-logging'])

driver = webdriver.Chrome(options=options)
try:
    driver.get(f'{BASE_URL}/Account/Login')
    wait_ready(driver)
    driver.find_element(By.ID, 'UserName').send_keys(USERNAME)
    driver.find_element(By.ID, 'Password').send_keys(PASSWORD)
    driver.find_element(By.ID, 'login-button').click()
    time.sleep(2)
    wait_ready(driver)

    for label in ['Actions', 'Supplier Actions', 'Action']:
        els = driver.find_elements(By.XPATH, "//*[self::a or self::button or self::span or self::div][contains(normalize-space(.), '" + label + "')]")
        for el in els:
            if el.is_displayed():
                el.click(); print('clicked menu', label); break
        else:
            continue
        break
    time.sleep(3)

    for label in ['Reschedule Request', 'Supplier Reschedule Request', 'Reschedule']:
        els = driver.find_elements(By.XPATH, "//*[self::a or self::button or self::input or self::span or self::div][contains(normalize-space(.), '" + label + "')]")
        for el in els:
            if el.is_displayed():
                el.click(); print('clicked reschedule', label); break
    time.sleep(3)

    rows = driver.find_elements(By.XPATH, "//tr[.//td and not(.//th)]")
    print('rows', len(rows))
    for row in rows[:25]:
        try:
            if row.is_displayed():
                row.click(); print('row clicked'); break
        except Exception:
            pass
    time.sleep(2)

    buttons = driver.find_elements(By.XPATH, "//*[self::button or self::a or self::div or self::span][contains(normalize-space(.),'Show Cards')]")
    for btn in buttons:
        if btn.is_displayed():
            btn.click(); print('show cards clicked'); break
    time.sleep(5)

    checkboxes = driver.find_elements(By.XPATH, "//input[@type='checkbox' and not(@disabled)]")
    count = 0
    for cb in checkboxes:
        try:
            cname = (cb.get_attribute('class') or '').lower()
            if 'selectall' in cname:
                continue
            if not cb.is_displayed():
                continue
            cb.click(); time.sleep(.5)
            if cb.is_selected() or driver.execute_script('return arguments[0].checked;', cb):
                count += 1
            if count >= 2:
                break
        except Exception:
            pass
    print('selected', count)

    date_inputs = driver.find_elements(By.XPATH, "//input[contains(@name,'ShipDate') or contains(@id,'ShipDate') or contains(@name,'NewReqdShipDate') or contains(@id,'NewReqdShipDate') or contains(@placeholder,'Date') or contains(@title,'Date')]")
    for f in date_inputs:
        if f.is_displayed():
            try:
                f.clear()
            except Exception:
                pass
            f.send_keys('30/09/2026')
            driver.execute_script('arguments[0].value = arguments[1];', f, '30/09/2026')
            print('date set'); break
    time.sleep(2)

    print('URL', driver.current_url)
    print('Relevant controls:')
    for el in driver.find_elements(By.XPATH, "//*[self::button or self::a or self::input or self::span or self::div or self::label or self::select]"):
        txt = (el.text or '').strip()
        val = (el.get_attribute('value') or '').strip()
        combined = (txt or val).strip()
        if combined and any(k in combined.lower() for k in ['reschedule', 'reason', 'ddm', 'date', 'select']):
            print('---', combined)
    print('select count', len(driver.find_elements(By.TAG_NAME, 'select')))
    for sel in driver.find_elements(By.TAG_NAME, 'select'):
        print('SELECT', sel.get_attribute('id'), sel.get_attribute('name'))
        try:
            opts = Select(sel).options
            print('OPTIONS', [o.text for o in opts])
        except Exception as e:
            print('ERR', e)

finally:
    driver.quit()
