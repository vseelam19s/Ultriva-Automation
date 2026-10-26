from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

BASE_URL = 'https://engineering.ultrivalms.com/QALS1011'

def main():
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-notifications')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(40)
    try:
        driver.get(f'{BASE_URL}/Account/Login')
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'UserName')))
        driver.find_element(By.ID, 'UserName').send_keys('supnewuser')
        driver.find_element(By.ID, 'Password').send_keys('Ultriva!23')
        driver.find_element(By.ID, 'login-button').click()
        WebDriverWait(driver, 20).until(lambda d: 'home' in d.current_url.lower() or BASE_URL.lower() in d.current_url.lower())

        actions = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'Actions')] | //span[contains(., 'Actions')]")))
        actions.click(); time.sleep(1)
        ship_menu = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'SupplierAction/ShipCards') or normalize-space(.)='Ship']")))
        ship_menu.click(); time.sleep(2)
        WebDriverWait(driver, 20).until(lambda d: 'shipcards' in d.current_url.lower())

        checkboxes = driver.find_elements(By.XPATH, "//input[@type='checkbox' and not(@disabled)]")
        print('checkbox count', len(checkboxes))
        for i, cb in enumerate(checkboxes[:10], 1):
            if cb.is_displayed():
                print('selecting checkbox', i)
                cb.click(); break
        time.sleep(2)

        all_text = driver.find_elements(By.XPATH, "//*")
        matched = []
        for el in all_text:
            try:
                txt = (el.text or '').strip().replace('\n', ' | ')
                value = (el.get_attribute('value') or '').strip()
                aria = (el.get_attribute('aria-label') or '').strip()
                text = txt or value or aria
                if 'Ship' in text:
                    matched.append((el.tag_name, text[:200], el.get_attribute('class') or '', el.get_attribute('id') or '', el.get_attribute('href') or '', el.is_displayed(), el.is_enabled()))
            except Exception:
                pass
        print('MATCHED', len(matched))
        for item in matched[:80]:
            print(item)
        input('PAUSE')
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
