"""Run all 3 Exception Code tests."""
import sys, os
sys.path.insert(0, os.path.abspath('.'))
from utils.driver_setup import get_driver
from selenium.webdriver.support.ui import WebDriverWait
from admin.ExceptionCode import add_exception_code, edit_exception_code, view_exception_code

driver = get_driver()
wait = WebDriverWait(driver, 20)
results = []
results.append(('TC-EC-01', add_exception_code(driver, wait)))
results.append(('TC-EC-02', edit_exception_code(driver, wait)))
results.append(('TC-EC-03', view_exception_code(driver, wait)))
driver.quit()

print()
print('='*50)
for tc, r in results:
    status = 'PASS' if r else 'FAIL'
    print(f'  [{status}] {tc}')
passed = sum(1 for _, r in results if r)
print(f'  {passed}/{len(results)} passed')
