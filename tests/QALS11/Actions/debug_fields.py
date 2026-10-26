import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select as SeleniumSelect
from selenium.webdriver.common.by import By
from selenium import webdriver
import sys
sys.path.insert(0, r"C:\Prcatices-AI\qa_automation")

opts = webdriver.ChromeOptions()
opts.add_argument("--no-sandbox")
opts.add_argument("--start-maximized")
driver = webdriver.Chrome(options=opts)

try:
    # Login
    driver.get("https://engineering.ultrivalms.com/QALS1011/")
    time.sleep(2)
    driver.find_element(By.ID, "UserName").send_keys("buyeruser")
    driver.find_element(By.ID, "Password").send_keys("Ultriva!23")
    driver.find_element(By.ID, "Password").send_keys(Keys.RETURN)
    time.sleep(3)

    # Navigate to Ad hoc Receipts
    driver.get(
        "https://engineering.ultrivalms.com/QALS1011/BuyerAction/AdhocReceipt")
    time.sleep(3)

    # Fill Item No
    itm = WebDriverWait(
        driver, 10).until(
        EC.presence_of_element_located(
            (By.ID, "ITM")))
    itm.clear()
    itm.send_keys("IT091220")
    time.sleep(1.5)
    try:
        sug = WebDriverWait(
            driver, 4).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//li[contains(.,'IT091220')]")))
        sug.click()
    except BaseException:
        itm.send_keys(Keys.RETURN)
    time.sleep(2)

    # Fill Supplier
    try:
        sup = SeleniumSelect(driver.find_element(By.ID, "FILTER_SUP"))
        sup.select_by_visible_text("Supnew")
    except BaseException:
        pass
    time.sleep(0.5)

    # Fill PO Number
    driver.find_element(By.ID, "FILTER_PONum").clear()
    driver.find_element(By.ID, "FILTER_PONum").send_keys("040928")
    time.sleep(0.3)

    # Fill Total Received Qty
    try:
        qty_f = driver.find_element(By.ID, "FILTER_ReceivedQty")
        driver.execute_script("arguments[0].value='';", qty_f)
        qty_f.clear()
        qty_f.send_keys("341")
    except BaseException:
        pass
    time.sleep(0.5)

    # Dump all inputs BEFORE compute cards
    print("=== INPUTS BEFORE COMPUTE CARDS ===")
    all_inputs = driver.execute_script("""
        return Array.from(document.querySelectorAll('input')).map(function(i){
            return {id:i.id, name:i.name, value:i.value, type:i.type, vis:(i.offsetParent!==null)};
        });
    """)
    for inp in all_inputs:
        if inp.get("type") != "hidden" or inp.get("value"):
            print(f"  id={str(inp.get('id',
                                      ''))!r:35} type={str(inp.get('type',
                                                                   ''))!r:10} val={str(inp.get('value',
                                                                                               ''))!r}")

    # Click Compute Cards
    driver.execute_script("_computecards();")
    time.sleep(3)

    # Dismiss any modal
    try:
        ok_btn = WebDriverWait(
            driver, 4).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//*[contains(@class,'modal')]//button")))
        ok_btn.click()
        time.sleep(1)
    except BaseException:
        pass

    # Dump all inputs AFTER compute cards
    print("\n=== INPUTS AFTER COMPUTE CARDS ===")
    all_inputs = driver.execute_script("""
        return Array.from(document.querySelectorAll('input')).map(function(i){
            return {id:i.id, name:i.name, value:i.value, type:i.type, vis:(i.offsetParent!==null)};
        });
    """)
    for inp in all_inputs:
        if inp.get("type") != "hidden" or inp.get("value"):
            print(f"  id={str(inp.get('id',
                                      ''))!r:35} type={str(inp.get('type',
                                                                   ''))!r:10} val={str(inp.get('value',
                                                                                               ''))!r}")

    input("Press Enter to close...")
finally:
    driver.quit()
