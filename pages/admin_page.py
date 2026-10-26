"""Page Object for Admin module and its sub-pages."""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage
from config.config import BASE_URL


ADMIN_BASE = "https://engineering.ultrivalms.com/QALS1011"


class AdminPage(BasePage):

    # ── Sidebar nav ───────────────────────────────────────────────────────
    ADMIN_NAV_LINK   = (By.XPATH, "//*[contains(@class,'vertical-nav-items')]//a[contains(@href,'Admin/Home')]")

    # ── Page headings ─────────────────────────────────────────────────────
    PAGE_HEADING     = (By.XPATH, "//h1 | //h2 | //h3 | //*[contains(@class,'page-title')]")
    BREADCRUMB       = (By.XPATH, "//*[contains(@class,'breadCrumb')] | //*[@id='breadcrumb']")
    ADMIN_BREADCRUMB_LINK = (By.XPATH,
        "//li[contains(@class,'breadcrumb') or contains(@class,'bread')]//a[contains(@href,'Admin')] | "
        "//*[@id='breadcrumb']//a[contains(@href,'Admin')] | "
        "//a[contains(@href,'Admin/PopBreadCrumb')] | "
        "//*[contains(@class,'breadcrumb')]//a[contains(normalize-space(.),'Admin')]"
    )

    # ── Toolbar buttons (common across list pages) ─────────────────────────
    VIEWS_BTN        = (By.XPATH, "//*[normalize-space(text())='Views']")
    FILTERS_BTN      = (By.XPATH, "//*[normalize-space(text())='Filters']")
    EXPORT_BTN       = (By.XPATH, "//*[normalize-space(text())='Export'] | //a[contains(@id,'Export') or contains(@class,'export')]")
    PRINT_BTN        = (By.XPATH, "//*[normalize-space(text())='Print']")
    ADD_BTN          = (By.XPATH, "//a[normalize-space(text())='Add'] | //button[normalize-space(text())='Add']")
    CLEAR_FILTER_BTN = (By.XPATH, "//*[normalize-space(text())='Clear Filter']")

    # ── Table / grid ──────────────────────────────────────────────────────
    TABLE_HEADERS    = (By.XPATH, "//th[string-length(normalize-space(.))>0]")
    TABLE_ROWS       = (By.XPATH, "//tbody/tr")

    # ── Global search ─────────────────────────────────────────────────────
    GLOBAL_SEARCH    = (By.NAME, "txtTbSearch")

    # ── Sub-page specific ─────────────────────────────────────────────────
    USER_FILTER      = (By.NAME, "User_FindTextbox")
    SUPPLIER_FILTER  = (By.NAME, "Supplier_FindTextbox")
    CUSTOMER_FILTER  = (By.NAME, "Customer_FindTextbox")
    WORKCENTER_FILTER= (By.NAME, "Workcenter_FindTextbox")
    WAREHOUSE_FILTER = (By.NAME, "Warehouse_FindTextbox")
    ENTITY_FILTER    = (By.NAME, "Family_FindTextbox")
    KANBAN_SUPPLIER_FILTER = (By.NAME, "MISC$SName")
    KANBAN_STATUS_FILTER   = (By.NAME, "MISC$RYG")

    # ── Business Unit ─────────────────────────────────────────────────────
    BUSUNIT_ADD_BTN  = (By.XPATH, "//a[normalize-space(text())='Add'] | //button[normalize-space(text())='Add']")
    BUSUNIT_EDIT_BTN = (By.XPATH, "//a[normalize-space(text())='Edit'] | //button[normalize-space(text())='Edit']")

    # ── Admin Tools sections ──────────────────────────────────────────────
    TOOLS_KANBAN_SECTION    = (By.XPATH, "//*[normalize-space(text())='Kanban']")
    TOOLS_DATALOAD_SECTION  = (By.XPATH, "//*[normalize-space(text())='Data Load']")

    # ── About Info ────────────────────────────────────────────────────────
    ABOUT_TABLE      = (By.XPATH, "//th[contains(text(),'Field Name') or contains(text(),'Field Value')]")

    def navigate_to(self, path):
        self.driver.get(f"{ADMIN_BASE}{path}")
        self.wait_for_page_load()

    def get_page_heading(self):
        if self.is_element_present(*self.PAGE_HEADING, timeout=8):
            els = self.driver.find_elements(*self.PAGE_HEADING)
            for el in els:
                t = el.text.strip()
                if t:
                    return t
        return None

    def get_table_columns(self):
        els = self.driver.find_elements(*self.TABLE_HEADERS)
        seen = set()
        cols = []
        for el in els:
            t = el.text.strip()
            if t and t not in seen:
                seen.add(t); cols.append(t)
        return cols

    def get_row_count(self):
        return len(self.driver.find_elements(*self.TABLE_ROWS))

    def has_views_button(self):
        return self.is_element_present(*self.VIEWS_BTN, timeout=5)

    def has_filters_button(self):
        return self.is_element_present(*self.FILTERS_BTN, timeout=5)

    def has_add_button(self):
        return self.is_element_present(*self.ADD_BTN, timeout=5)

    def has_global_search(self):
        return self.is_element_present(*self.GLOBAL_SEARCH, timeout=5)

    def has_column(self, col_name):
        return col_name in self.get_table_columns()

    def filter_input_present(self, by, value):
        return self.is_element_present(by, value, timeout=5)

    def type_in_filter(self, by, value, text):
        if self.is_element_present(by, value, timeout=5):
            el = self.driver.find_element(by, value)
            try:
                el.clear()
                el.send_keys(text)
            except Exception:
                # Fall back to JavaScript for non-interactable inputs
                self.driver.execute_script(
                    "arguments[0].value = arguments[1]; "
                    "arguments[0].dispatchEvent(new Event('input'));",
                    el, text)
            return True
        return False

    def is_authenticated(self):
        """Returns True if we are still on an authenticated page (not kicked to login)."""
        return "UserName" not in self.driver.page_source or \
               self.is_element_present(
                   By.XPATH,
                   "//*[contains(@class,'vertical-nav') or contains(@href,'Account/Logout')]",
                   timeout=5)
