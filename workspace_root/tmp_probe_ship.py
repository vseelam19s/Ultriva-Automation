import time, re
from selenium import webdriver
from selenium.webdriver.common.by import By
B = "https://engineering.ultrivalms.com/QALS1011"
d = webdriver.Chrome()
d.maximize_window()
d.get(f"{B}/Account/Login")
d.find_element(By.ID, "UserName").send_keys("supnewuser")
d.find_element(By.ID, "Password").send_keys("Ultriva!23")
d.find_element(By.ID, "login-button").click()
time.sleep(4)
d.get(f"{B}/SupplierAction/ShipFilter")
time.sleep(6)
for page in range(1, 53):
    trs = d.find_elements(By.CSS_SELECTOR, "tr[gid]")
    cbs = d.find_elements(By.CSS_SELECTOR, "tr[gid] input[type='checkbox'], tr[gid] input[type='Checkbox']")
    rw = len(d.find_elements(By.CSS_SELECTOR, "tr[gid] img[src*='ReschWait']"))
    print("X PAGE", page, "rows", len(trs), "cbs", len(cbs), "reschwait", rw, trs[0].get_attribute("gid") if trs else None)
    if cbs: 
        print("X FOUND", [c.get_attribute("name") for c in cbs[:4]]); break
    nxt = d.find_element(By.ID, "ToolbarPager_tbrNext")
    d.execute_script("arguments[0].click();", nxt)
    time.sleep(4)
d.quit()
