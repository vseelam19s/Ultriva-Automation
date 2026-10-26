import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

base = 'https://engineering.ultrivalms.com/QALS1011'
login = f'{base}/Account/Login'
url = f'{base}/SupplierAction/SupplierRYGBoardItems'

download_dir = r'C:\Prcatices-AI\qa_automation\reports\downloads_debug'
os.makedirs(download_dir, exist_ok=True)
opts = webdriver.ChromeOptions()
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')
opts.add_argument('--disable-gpu')
opts.add_argument('--start-maximized')
opts.add_experimental_option('excludeSwitches', ['enable-logging'])
opts.add_experimental_option('prefs', {
    'download.default_directory': download_dir,
    'download.prompt_for_download': False,
    'download.directory_upgrade': True,
    'safebrowsing.enabled': True,
    'profile.default_content_settings.popups': 0,
})

d = webdriver.Chrome(options=opts)
d.implicitly_wait(10)
d.set_page_load_timeout(40)

d.get(login)
WebDriverWait(d, 20).until(EC.presence_of_element_located((By.ID, 'UserName')))
d.find_element(By.ID, 'UserName').send_keys('supnewuser')
d.find_element(By.ID, 'Password').send_keys('Ultriva!23')
d.find_element(By.ID, 'login-button').click()
WebDriverWait(d, 20).until(lambda x: 'Home' in x.current_url or 'home' in x.current_url.lower())
d.get(url)
WebDriverWait(d, 20).until(lambda x: 'SupplierRYGBoardItems' in x.current_url)

print('URL after load:', d.current_url)

elements = d.find_elements(By.XPATH, "//*[self::a or self::button or self::span][contains(normalize-space(.), 'Export')]" )
print('Export element count=', len(elements))
for i, e in enumerate(elements[:10], 1):
    text = e.text.strip()
    href = e.get_attribute('href')
    onclick = e.get_attribute('onclick')
    target = e.get_attribute('target')
    class_name = e.get_attribute('class')
    print(f'[{i}] text={text!r} href={href!r} onclick={onclick!r} target={target!r} class={class_name!r}')
    if 'Export' in text:
        print('About to click export')
        try:
            e.click()
        except Exception as ex:
            print('click failed', ex)
            d.execute_script('arguments[0].click();', e)
        time.sleep(8)
        print('Current URL after click:', d.current_url)
        print('Page title:', d.title)
        body_text = (d.find_element(By.TAG_NAME, 'body').text or '')[:2000]
        print('BODY START')
        print(body_text)
        print('BODY END')
        print('download dir contents:', os.listdir(download_dir))
        break

print('ALL FILES IN DEBUG DIR:', os.listdir(download_dir))
input('Press enter to close')
d.quit()
