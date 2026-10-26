from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

BASE_URL = 'https://engineering.ultrivalms.com/QALS1011'


def wait_ready(driver, timeout=30):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script('return document.readyState') == 'complete'
    )


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
    print('URL ON ITEMS', d.current_url)

    for by, locator in [
        (By.ID, 'imgMatStatusGo'),
        (By.XPATH, "//button[normalize-space(.)='Go']"),
        (By.XPATH, "//input[@type='submit' and @value='Go']"),
        (By.XPATH, "//a[normalize-space(.)='Go']"),
        (By.XPATH, "//*[@id='btnGo' or @id='go-button' or @id='goBtn']"),
    ]:
        try:
            b = WebDriverWait(d, 6).until(EC.element_to_be_clickable((by, locator)))
            print('FOUND GO', by, locator)
            b.click(); wait_ready(d); time.sleep(2)
            print('URL AFTER GO', d.current_url)
            break
        except Exception:
            pass

    items = d.find_elements(By.XPATH, "//a[contains(@class,'GridLink')]")
    print('GRIDLINKS', len(items))
    for i, item in enumerate(items[:10]):
        print('ITEM', i, repr(item.text.strip()[:100]), item.get_attribute('href'))

    if items:
        first = items[0]
        first.click(); wait_ready(d); time.sleep(2)
        print('URL AFTER ITEM CLICK', d.current_url)
        print('BODY TEXT')
        text = (d.find_element(By.TAG_NAME, 'body').text or '')
        print(text[:5000])
        print('SHOW_CARDS_PARENT?', 'Show Cards' in text, 'Show cards' in text)

finally:
    d.quit()
