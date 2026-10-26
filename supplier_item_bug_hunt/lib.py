import time, json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

BASE = "https://engineering.ultrivalms.com/POC"
COLS = ["PlantItemNo", "SupplierItemCode", "SupplierItemDesc", "Carrier", "LeadTime", "TransitTime", "PalletQty", "UnitDescription"]
LABELS = {"PlantItemNo": "Plant Item No", "SupplierItemCode": "Supplier Item No.", "SupplierItemDesc": "Description", "Carrier": "Carrier",
          "LeadTime": "Lead Time", "TransitTime": "Transit Time", "PalletQty": "Qty On Card", "UnitDescription": "Unit Description"}
NUMERIC = {"LeadTime", "TransitTime", "PalletQty"}
PLANTS = {"Cust240720": "BSU22ZJQALGH", "Cust1201023": "BSU233MQALZH"}


def make_driver():
    o = Options()
    o.add_argument("--window-size=1920,1080")
    o.add_experimental_option("excludeSwitches", ["enable-logging"])
    d = webdriver.Chrome(options=o)
    d.implicitly_wait(2)
    return d


def login(d):
    d.get(BASE + "/")
    d.find_element(By.ID, "UserName").send_keys("buyeruser")
    d.find_element(By.ID, "Password").send_keys("Ultriva!23")
    d.find_element(By.ID, "login-button").click()
    time.sleep(3)


def open_list(d):
    d.get(BASE + "/SupplierItem/List")
    time.sleep(3)


def select_plant(d, val):
    d.execute_script("var s=document.querySelector('#drpPlant');s.value=arguments[0];s.dispatchEvent(new Event('change',{bubbles:true}));", val)
    click_text(d, "Go")
    time.sleep(2.5)


def click_text(d, text):
    return d.execute_script("var b=[...document.querySelectorAll('button,a,input[type=button]')].find(b=>(b.innerText||b.value||'').trim()==arguments[0]&&b.offsetParent);if(b){b.click();return true}return false", text)


def rows(d):
    return d.execute_script("""
      var pin=[...document.querySelectorAll('.ag-center-cols-container .ag-row')];
      pin.sort((a,b)=>parseInt(a.getAttribute('row-index'))-parseInt(b.getAttribute('row-index')));
      return pin.map(r=>{var o={};r.querySelectorAll('.ag-cell').forEach(c=>{var k=c.getAttribute('col-id');if(k)o[k]=c.innerText.trim()});return o});
    """)


def paging(d):
    return d.execute_script("return ((document.querySelector('.ag-paging-panel')||{}).innerText||'').replace(/\\s+/g,' ')")


def sort_state(d):
    return d.execute_script("var o={};document.querySelectorAll('.ag-header-cell[col-id]').forEach(h=>{o[h.getAttribute('col-id')]=h.getAttribute('aria-sort')});return o")


def click_header(d, col, shift=False):
    h = d.find_element(By.CSS_SELECTOR, f".ag-header-cell[col-id='{col}'] .ag-header-cell-label")
    if shift:
        from selenium.webdriver.common.action_chains import ActionChains
        ActionChains(d).key_down(Keys.SHIFT).click(h).key_up(Keys.SHIFT).perform()
    else:
        h.click()
    time.sleep(0.8)


def clear_filters(d):
    d.execute_script("var b=document.querySelector('#ag-toolbar-clear');if(b)b.click()")
    time.sleep(0.8)


def open_filter(d, col):
    d.execute_script("document.querySelector(\".ag-header-cell[col-id='\"+arguments[0]+\"'] .ag-header-cell-filter-button\").click()", col)
    time.sleep(0.7)


def close_popup(d):
    d.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
    d.execute_script("document.querySelector('.ag-header-viewport')?.click()")
    time.sleep(0.4)
