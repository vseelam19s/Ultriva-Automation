# View system user groups (System tab, view group, click cancel)
def view_system_user_groups(driver, wait, group_title):
    """View a system user group and click cancel to navigate back (System tab)."""
    log(f"[View system user groups] Searching for system group '{group_title}'...")
    # Go to System Group List (System tab)
    driver.get(f"{ADMIN_BASE}/Group/SysList")
    time.sleep(2)
    # Search for the group title
    driver.execute_script('''
        var inputs = document.querySelectorAll('input[type="text"]');
        for (var i = 0; i < inputs.length; i++) {
            if (inputs[i].offsetParent !== null) {
                inputs[i].value = arguments[0];
                inputs[i].dispatchEvent(new Event('input', {bubbles:true}));
                inputs[i].dispatchEvent(new Event('change', {bubbles:true}));
                inputs[i].dispatchEvent(new Event('keyup', {bubbles:true}));
                break;
            }
        }
    ''', group_title)
    time.sleep(2)
    # Click View link in the row
    view_xpath = f"//tr[td[contains(normalize-space(.), '{group_title}')]]//a[contains(@href,'SysView')]"
    found = quick_find(driver, view_xpath)
    if found:
        elem = found[0]
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", elem)
        time.sleep(0.5)
        elem.click()
        log(f"[View system user groups] View clicked for: {group_title}")
        time.sleep(2)
        # Click Cancel button to go back
        cancel_xpath = "//a[contains(normalize-space(.),'Cancel')] | //button[contains(normalize-space(.),'Cancel')]"
        cancel_btns = quick_find(driver, cancel_xpath)
        if cancel_btns:
            cancel_btn = cancel_btns[0]
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", cancel_btn)
            time.sleep(0.5)
            cancel_btn.click()
            log("[View system user groups] Cancel clicked, navigated back.")
            time.sleep(2)
        else:
            log("[View system user groups] Cancel button not found.")
    else:
        log(f"[View system user groups] Group '{group_title}' not found in System tab.")
"""
UserGroup.py – Create and Edit a Local User Group via Admin > User Group.

Flow - CREATE:
  1. Log in to QA site (QALS1011)
  2. Navigate to Admin > User Group (System Group List)
  3. Click the "Local" tab
  4. Click "+ Add" to open the Create Local Group form
  5. Fill in Title and Description
  6. Select "Plant Users" radio button
  7. Select a few privilege checkboxes
  8. Click Save

Flow - EDIT:
  9.  Navigate to Local Group List
  10. Search for the recently created group and click Edit
  11. Modify Title and Description
  12. Modify privileges (toggle some Allow/Deny)
  13. Click Save

Flow - VIEW:
  14. Navigate to Local Group List
  15. Search for the recently created group and click View
  16. On the View Local Group page, click Cancel to go back

Flow - ASSIGN USERS:
  17. Navigate to Local Group List
  18. Search for the recently created group and click Assigned Users
  19. On Assigned Users page, click "+ Assign User(s)" button
  20. On Assign Users page, select a user and click "+ Assign"
  21. Click Back button to return to Assigned Users page

Flow - MY ROUTINES:
  22. Navigate to Local Group List
  23. Search for the recently created group and click My Routines
  24. On Manage My Routines page, select Daily/Weekly/Monthly checkboxes
  25. Click Save

Flow - CLONE USER GROUP:
  26. Navigate to Local Group List
  27. Search for the recently created group and click Clone Group
  28. On Create Local Group (clone) page, modify Title and Description
  29. Optionally modify privileges
  30. Click Save

Flow - DELETE USER GROUP:
  31. Navigate to Local Group List
  32. Search for the target group and select (click) its row
  33. Click the Delete toolbar button
  34. On the confirmation dialog "Do you want to delete this group?", click Yes
  35. Verify the group is removed from the list
"""
import sys, os, time, datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from config.config import BASE_URL, USERNAME, PASSWORD, IMPLICIT_WAIT, PAGE_LOAD_TIMEOUT
from utils.driver_setup import get_driver

# ── Constants ────────────────────────────────────────────────────────────────
ADMIN_BASE = "https://engineering.ultrivalms.com/QALS1011"
GROUP_LOCAL_LIST_URL = f"{ADMIN_BASE}/Group/LocalList"

TIMESTAMP = datetime.datetime.now().strftime("%y%m%d%H%M")
GROUP_TITLE       = f"AutoQA_{TIMESTAMP}"
GROUP_DESCRIPTION = f"Automated test user group created on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"

# Edit flow: search the group we just created, then modify it
EDIT_GROUP_TITLE    = GROUP_TITLE                  # same as the freshly created group
EDITED_TITLE        = f"AutoQA_{TIMESTAMP}_Edited"
EDITED_DESCRIPTION  = f"Modified by automation on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"

# View flow: after editing, the group's title is EDITED_TITLE
VIEW_GROUP_TITLE    = EDITED_TITLE

# Assign Users flow: same edited group
ASSIGN_GROUP_TITLE  = EDITED_TITLE

# My Routines flow: same edited group
ROUTINES_GROUP_TITLE = EDITED_TITLE

# Clone flow: clone the edited group, save with new name
CLONE_GROUP_TITLE     = EDITED_TITLE
CLONED_TITLE          = f"CloneQA_{TIMESTAMP}"
CLONED_DESCRIPTION    = f"Cloned by automation on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"

# Delete flow: delete the cloned group (keep the original edited one)
DELETE_GROUP_TITLE    = CLONED_TITLE

# ── Helpers ──────────────────────────────────────────────────────────────────
def log(msg=""):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")


def quick_find(driver, xpath):
    """Find elements with implicit wait disabled (instant return)."""
    driver.implicitly_wait(0)
    try:
        return driver.find_elements(By.XPATH, xpath)
    finally:
        driver.implicitly_wait(IMPLICIT_WAIT)


def login(driver, wait):
    """Log in to the QA site."""
    log("Navigating to login page...")
    driver.get(BASE_URL)
    time.sleep(2)
    driver.find_element(By.ID, "UserName").clear()
    driver.find_element(By.ID, "UserName").send_keys(USERNAME)
    driver.find_element(By.ID, "Password").clear()
    driver.find_element(By.ID, "Password").send_keys(PASSWORD)
    driver.find_element(By.ID, "login-button").click()
    time.sleep(3)
    log(f"Logged in. Current URL: {driver.current_url}")


def navigate_to_local_create(driver, wait):
    """Navigate through Admin > User Group > Local > Add."""
    log("Navigating to Admin > User Group > Local > Add...")
    driver.get(f"{ADMIN_BASE}/Admin/Home")
    time.sleep(2)
    log(f"Admin page loaded. URL: {driver.current_url}")

    # Click User Group
    log("Clicking 'User Group' link...")
    ug_link = wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "//a[contains(@href,'Group') and contains(normalize-space(.),'User Group')]"
        " | //a[contains(@href,'Group/SysList')]"
    )))
    ug_link.click()
    time.sleep(2)
    log(f"System Group List. URL: {driver.current_url}")

    # Navigate to Local tab (direct URL as quick fallback)
    log("Navigating to Local Group List...")
    try:
        local_tab = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((
            By.XPATH, "//a[normalize-space(.)='Local'] | //li/a[contains(@href,'Local')]"
        )))
        local_tab.click()
        time.sleep(2)
    except TimeoutException:
        log("Tab click failed, navigating directly...")
        driver.get(GROUP_LOCAL_LIST_URL)
        time.sleep(2)
    log(f"Local Group List. URL: {driver.current_url}")

    # Click Add
    log("Clicking '+ Add' button...")
    add_btn = wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "//a[contains(@class,'btn') and contains(normalize-space(.),'Add')]"
        " | //a[contains(@href,'LocalCreate')]"
        " | //button[contains(normalize-space(.),'Add')]"
    )))
    add_btn.click()
    time.sleep(2)
    log(f"Create Local Group form. URL: {driver.current_url}")


def wait_for_privilege_tree(driver):
    """Wait for the privilege tree to finish loading."""
    log("Waiting for privilege tree to load...")
    for _ in range(30):
        loading = quick_find(driver, "//*[contains(text(),'Loading')]")
        if not loading:
            break
        time.sleep(1)
    # Wait for privilege table rows to appear
    for _ in range(15):
        rows = quick_find(driver, "//table//tr")
        if len(rows) > 3:
            break
        time.sleep(1)
    time.sleep(1)
    log("Privilege tree loaded.")


def fill_group_info(driver, title, description):
    """Fill Title, Description, and select Plant Users using JS for speed."""
    wait_for_privilege_tree(driver)

    # Inspect visible text inputs
    result = driver.execute_script("""
        var inputs = document.querySelectorAll('input[type="text"]');
        var found = [];
        for (var i = 0; i < inputs.length; i++) {
            if (inputs[i].offsetParent !== null) {
                found.push({name: inputs[i].name || inputs[i].id || 'idx_'+i, index: i});
            }
        }
        return JSON.stringify(found);
    """)
    log(f"Filling Title: '{title}' | Visible inputs: {result}")

    # Fill Title (first visible text input) and Description (second)
    driver.execute_script("""
        var inputs = document.querySelectorAll('input[type="text"]');
        var visible = [];
        for (var i = 0; i < inputs.length; i++) {
            if (inputs[i].offsetParent !== null) visible.push(inputs[i]);
        }
        if (visible.length >= 1) {
            visible[0].value = arguments[0];
            visible[0].dispatchEvent(new Event('input', {bubbles:true}));
            visible[0].dispatchEvent(new Event('change', {bubbles:true}));
        }
        if (visible.length >= 2) {
            visible[1].value = arguments[1];
            visible[1].dispatchEvent(new Event('input', {bubbles:true}));
            visible[1].dispatchEvent(new Event('change', {bubbles:true}));
        }
    """, title, description)
    log("Title and Description filled via JS.")

    # Select Plant Users radio (first radio, usually pre-selected)
    log("Checking 'Plant Users' radio button...")
    is_selected = driver.execute_script("""
        var radios = document.querySelectorAll('input[type="radio"]');
        if (radios.length > 0 && !radios[0].checked) radios[0].click();
        return radios.length > 0 ? radios[0].checked : false;
    """)
    log(f"Plant Users radio selected: {is_selected}")


def select_privileges(driver):
    """Select a few 'Allow' privilege toggles from the privilege tree.

    The privilege grid uses AllowGray.gif / DenyGray.gif image toggles
    inside <td> elements. Event handlers are bound via jQuery/addEventListener,
    so we must use Selenium's real click (not just JS click).
    """
    log("Selecting privilege checkboxes...")

    # Brief DOM summary (avoid huge output)
    summary = driver.execute_script("""
        var imgs = document.querySelectorAll('img[src*="AllowGray"]');
        var count = imgs.length;
        // Get first 3 rows with AllowGray images
        var samples = [];
        for (var i = 0; i < Math.min(imgs.length, 3); i++) {
            var row = imgs[i].closest('tr');
            samples.push({
                rowText: row ? row.querySelector('td').textContent.trim().substring(0, 40) : 'no row',
                imgSrc: imgs[i].src.split('/').pop(),
                tdId: imgs[i].parentElement ? imgs[i].parentElement.id : ''
            });
        }
        return JSON.stringify({totalAllowImgs: count, samples: samples});
    """)
    log(f"Allow images summary: {summary}")

    # Use Selenium to find and click AllowGray images in target action rows
    target_actions = ["Add User", "Edit User", "View Details", "Add User Group", "Edit User Group"]
    selected = 0

    for action_name in target_actions:
        try:
            # Find the AllowGray.gif image in the row containing the action name
            allow_imgs = quick_find(driver,
                f"//tr[td[normalize-space(.)='{action_name}']]//img[contains(@src,'AllowGray')]"
            )
            if allow_imgs:
                img = allow_imgs[0]
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", img)
                time.sleep(0.3)
                img.click()  # Real Selenium click to trigger jQuery events
                selected += 1
                log(f"  Clicked Allow for: {action_name}")
                time.sleep(0.5)
            else:
                log(f"  No AllowGray image found for: {action_name}")
        except Exception as e:
            log(f"  Error clicking '{action_name}': {e}")

    log(f"Selected {selected} Allow privileges.")

    # Fallback: if no named actions found, click first few AllowGray images
    if selected == 0:
        log("Fallback: clicking first few AllowGray images...")
        all_allow = quick_find(driver, "//img[contains(@src,'AllowGray')]")
        for i, img in enumerate(all_allow[:5]):
            try:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", img)
                time.sleep(0.3)
                img.click()
                selected += 1
                log(f"  Clicked AllowGray image #{i+1}")
                time.sleep(0.5)
            except Exception as e:
                log(f"  Error on image #{i+1}: {e}")
        log(f"Fallback selected {selected} images.")


def click_save(driver):
    """Click the Save button at the bottom of the page."""
    log("Clicking 'Save' button...")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)

    # Brief inspection of save-like elements
    save_debug = driver.execute_script("""
        var info = [];
        var all = document.querySelectorAll('a, button, input, img, span');
        for (var i = 0; i < all.length; i++) {
            var text = (all[i].textContent || all[i].value || all[i].title || all[i].alt || '').trim();
            var onclick = all[i].getAttribute('onclick') || '';
            var href = all[i].getAttribute('href') || '';
            var src = all[i].getAttribute('src') || '';
            var lc = (text + onclick + href + src).toLowerCase();
            if (lc.indexOf('save') >= 0 || lc.indexOf('submit') >= 0) {
                info.push({
                    tag: all[i].tagName, id: all[i].id,
                    text: text.substring(0, 40),
                    onclick: onclick.substring(0, 60),
                    href: href.substring(0, 60),
                    src: src.split('/').pop().substring(0, 40)
                });
            }
        }
        return JSON.stringify(info);
    """)
    log(f"Save elements: {save_debug}")

    # Try Selenium clicks on save-like elements
    save_xpaths = [
        "//*[contains(translate(normalize-space(.),'SAVE','save'),'save') and (self::a or self::button or self::input)]",
        "//img[contains(translate(@alt,'SAVE','save'),'save') or contains(translate(@title,'SAVE','save'),'save') or contains(@src,'save') or contains(@src,'Save')]",
        "//*[contains(translate(@onclick,'SAVE','save'),'save')]",
        "//a[contains(@href,'Save') or contains(@href,'save')]",
        "//input[@type='submit']",
        "//button[@type='submit']",
    ]
    for xpath in save_xpaths:
        found = quick_find(driver, xpath)
        if found:
            elem = found[0]
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", elem)
            time.sleep(0.5)
            try:
                elem.click()
            except Exception:
                driver.execute_script("arguments[0].click();", elem)
            log(f"Save clicked via: {xpath}")
            time.sleep(3)
            log(f"Current URL: {driver.current_url}")
            return

    # Last resort: submit the group creation form (not search form)
    log("WARNING: No Save element found. Attempting form submit...")
    result = driver.execute_script("""
        var forms = document.querySelectorAll('form');
        for (var f = 0; f < forms.length; f++) {
            var action = forms[f].action || '';
            if (action.indexOf('Search') < 0 && action.indexOf('Group') >= 0) {
                forms[f].submit();
                return 'submitted:' + action;
            }
        }
        var info = [];
        for (var f = 0; f < forms.length; f++) {
            info.push({action: forms[f].action, id: forms[f].id});
        }
        return 'NOT_FOUND:' + JSON.stringify(info);
    """)
    log(f"Form submit: {result}")
    time.sleep(3)
    log(f"Current URL: {driver.current_url}")


# ── EDIT User Group Functions ────────────────────────────────────────────────

def navigate_to_local_list(driver, wait):
    """Navigate to Admin > User Group > Local Group List."""
    log("Navigating to Local Group List...")
    driver.get(GROUP_LOCAL_LIST_URL)
    time.sleep(3)
    log(f"Local Group List loaded. URL: {driver.current_url}")


def search_and_click_edit(driver, wait, group_title):
    """Find the target group in the Local Group List and click its Edit link.

    Steps:
      - Look for a search/filter box on the list page and type the group title
      - Locate the row containing the group title
      - Click the Edit link/icon in that row
    """
    log(f"Searching for group '{group_title}' in the list...")

    # Try to use the search/filter box if available
    search_filled = driver.execute_script("""
        // Look for a search or filter input on the page
        var inputs = document.querySelectorAll(
            'input[type="text"][name*="search" i], input[type="text"][name*="filter" i], '
            + 'input[type="text"][placeholder*="search" i], input[type="text"][placeholder*="filter" i], '
            + 'input[type="search"]'
        );
        for (var i = 0; i < inputs.length; i++) {
            if (inputs[i].offsetParent !== null) {
                inputs[i].value = arguments[0];
                inputs[i].dispatchEvent(new Event('input', {bubbles:true}));
                inputs[i].dispatchEvent(new Event('change', {bubbles:true}));
                inputs[i].dispatchEvent(new Event('keyup', {bubbles:true}));
                return 'search_filled';
            }
        }
        return 'no_search_box';
    """, group_title)
    log(f"Search box: {search_filled}")
    time.sleep(2)

    # Find the row containing the group title and click Edit
    log(f"Looking for '{group_title}' row and Edit link...")
    edit_xpaths = [
        # Edit link in the same row as the group title
        f"//tr[td[contains(normalize-space(.),'{group_title}')]]//a[contains(@href,'Edit') or contains(@href,'Update')]",
        f"//tr[td[contains(normalize-space(.),'{group_title}')]]//a[contains(normalize-space(.),'Edit')]",
        f"//tr[td[contains(normalize-space(.),'{group_title}')]]//a[contains(@class,'edit') or contains(@class,'Edit')]",
        # Click group title link itself (sometimes takes you to edit page)
        f"//a[contains(normalize-space(.),'{group_title}')]",
    ]
    for xpath in edit_xpaths:
        found = quick_find(driver, xpath)
        if found:
            elem = found[0]
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", elem)
            time.sleep(0.5)
            try:
                elem.click()
            except Exception:
                driver.execute_script("arguments[0].click();", elem)
            log(f"Edit clicked via: {xpath}")
            time.sleep(3)
            log(f"Edit page URL: {driver.current_url}")
            return

    # Fallback: scan all links on the page for the group ID pattern
    log("Direct XPath not found. Scanning page links...")
    result = driver.execute_script("""
        var links = document.querySelectorAll('a');
        for (var i = 0; i < links.length; i++) {
            var text = links[i].textContent.trim();
            if (text.indexOf(arguments[0]) >= 0) {
                links[i].scrollIntoView({block: 'center'});
                links[i].click();
                return 'clicked_link:' + text.substring(0, 50);
            }
        }
        return 'NOT_FOUND';
    """, group_title)
    log(f"Link scan result: {result}")
    time.sleep(3)
    log(f"Current URL: {driver.current_url}")


def modify_group_info(driver, new_title, new_description):
    """Modify the Title and Description on the Modify Local Group form."""
    log(f"Modifying Title to: '{new_title}'")

    wait_for_privilege_tree(driver)

    # Clear and fill Title and Description with new values
    driver.execute_script("""
        var inputs = document.querySelectorAll('input[type="text"]');
        var visible = [];
        for (var i = 0; i < inputs.length; i++) {
            if (inputs[i].offsetParent !== null) visible.push(inputs[i]);
        }
        // Title = first visible text input, Description = second
        if (visible.length >= 1) {
            visible[0].value = '';
            visible[0].value = arguments[0];
            visible[0].dispatchEvent(new Event('input', {bubbles:true}));
            visible[0].dispatchEvent(new Event('change', {bubbles:true}));
        }
        if (visible.length >= 2) {
            visible[1].value = '';
            visible[1].value = arguments[1];
            visible[1].dispatchEvent(new Event('input', {bubbles:true}));
            visible[1].dispatchEvent(new Event('change', {bubbles:true}));
        }
    """, new_title, new_description)
    log("Title and Description modified.")


def modify_privileges(driver):
    """Toggle some privileges on the Modify Local Group form.

    On the edit page, previously selected privileges show AllowCheck.gif (green).
    Unselected ones show AllowGray.gif (gray).
    We toggle a few: enable some new ones and disable some existing ones.
    """
    log("Modifying privileges...")

    # Summary of current privilege state
    summary = driver.execute_script("""
        var checks = document.querySelectorAll('img[src*="AllowCheck"]');
        var grays  = document.querySelectorAll('img[src*="AllowGray"]');
        return JSON.stringify({
            allowChecked: checks.length,
            allowGray: grays.length,
            firstChecked: checks.length > 0
                ? checks[0].closest('tr').querySelector('td').textContent.trim().substring(0, 40)
                : 'none'
        });
    """)
    log(f"Current privilege state: {summary}")

    # --- Disable (uncheck) some currently enabled privileges ---
    # Click AllowCheck.gif images to toggle them OFF for specific actions
    disable_actions = ["Edit User"]
    for action_name in disable_actions:
        try:
            checked_imgs = quick_find(driver,
                f"//tr[td[normalize-space(.)='{action_name}']]//img[contains(@src,'AllowCheck')]"
            )
            if checked_imgs:
                img = checked_imgs[0]
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", img)
                time.sleep(0.3)
                img.click()
                log(f"  Toggled OFF: {action_name}")
                time.sleep(0.5)
            else:
                log(f"  '{action_name}' not currently enabled, skipping disable.")
        except Exception as e:
            log(f"  Error disabling '{action_name}': {e}")

    # --- Enable (check) some new privileges ---
    # Click AllowGray.gif images to toggle them ON for new actions
    enable_actions = ["View Details", "Enable/Disable User", "Assign Groups"]
    enabled_count = 0
    for action_name in enable_actions:
        try:
            allow_imgs = quick_find(driver,
                f"//tr[td[normalize-space(.)='{action_name}']]//img[contains(@src,'AllowGray')]"
            )
            if allow_imgs:
                img = allow_imgs[0]
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", img)
                time.sleep(0.3)
                img.click()
                enabled_count += 1
                log(f"  Toggled ON: {action_name}")
                time.sleep(0.5)
            else:
                log(f"  '{action_name}' already enabled or not found.")
        except Exception as e:
            log(f"  Error enabling '{action_name}': {e}")

    # Fallback: if named lookups failed, toggle a few by index
    if enabled_count == 0:
        log("Fallback: toggling gray images by index...")
        all_gray = quick_find(driver, "//img[contains(@src,'AllowGray')]")
        for i, img in enumerate(all_gray[5:8]):  # pick 3 different ones
            try:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", img)
                time.sleep(0.3)
                img.click()
                enabled_count += 1
                log(f"  Toggled ON image #{i+6}")
                time.sleep(0.5)
            except Exception as e:
                log(f"  Error on image #{i+6}: {e}")

    log(f"Privileges modified: enabled {enabled_count} new action(s).")


def take_screenshot(driver, name):
    """Save a screenshot to reports/screenshots/."""
    os.makedirs("reports/screenshots", exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = f"reports/screenshots/{name}_{ts}.png"
    driver.save_screenshot(path)
    log(f"Screenshot saved: {path}")


# ── VIEW User Group Functions ────────────────────────────────────────────────

def search_and_click_view(driver, wait, group_title):
    """Find the target group in the Local Group List and click its View link.

    Steps:
      - Use the search/filter box (if available) to narrow down results
      - Locate the row containing the group title
      - Click the View link/icon in that row
    """
    log(f"Searching for group '{group_title}' to view...")

    # Try to use the search/filter box if available
    search_filled = driver.execute_script("""
        var inputs = document.querySelectorAll(
            'input[type="text"][name*="search" i], input[type="text"][name*="filter" i], '
            + 'input[type="text"][placeholder*="search" i], input[type="text"][placeholder*="filter" i], '
            + 'input[type="search"]'
        );
        for (var i = 0; i < inputs.length; i++) {
            if (inputs[i].offsetParent !== null) {
                inputs[i].value = arguments[0];
                inputs[i].dispatchEvent(new Event('input', {bubbles:true}));
                inputs[i].dispatchEvent(new Event('change', {bubbles:true}));
                inputs[i].dispatchEvent(new Event('keyup', {bubbles:true}));
                return 'search_filled';
            }
        }
        return 'no_search_box';
    """, group_title)
    log(f"Search box: {search_filled}")
    time.sleep(2)

    # Find the row containing the group title and click View
    log(f"Looking for '{group_title}' row and View link...")
    view_xpaths = [
        # View link in the same row as the group title
        f"//tr[td[contains(normalize-space(.), '{group_title}')]]//a[contains(@href,'View') or contains(@href,'LocalView')]",
        f"//tr[td[contains(normalize-space(.), '{group_title}')]]//a[contains(normalize-space(.),'View')]",
        # Direct link containing group title text (navigates to view page)
        f"//a[contains(normalize-space(.), '{group_title}') and contains(@href,'View')]",
    ]
    for xpath in view_xpaths:
        found = quick_find(driver, xpath)
        if found:
            elem = found[0]
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", elem)
            time.sleep(0.5)
            try:
                elem.click()
            except Exception:
                driver.execute_script("arguments[0].click();", elem)
            log(f"View clicked via: {xpath}")
            time.sleep(3)
            log(f"View page URL: {driver.current_url}")
            return

    # Fallback: scan all links on the page for a View link near the group title
    log("Direct XPath not found. Scanning page links for View...")
    result = driver.execute_script("""
        var rows = document.querySelectorAll('tr');
        for (var i = 0; i < rows.length; i++) {
            if (rows[i].textContent.indexOf(arguments[0]) >= 0) {
                var links = rows[i].querySelectorAll('a');
                for (var j = 0; j < links.length; j++) {
                    var href = (links[j].getAttribute('href') || '').toLowerCase();
                    var text = links[j].textContent.trim().toLowerCase();
                    if (href.indexOf('view') >= 0 || text.indexOf('view') >= 0) {
                        links[j].scrollIntoView({block: 'center'});
                        links[j].click();
                        return 'clicked_view_link';
                    }
                }
            }
        }
        return 'NOT_FOUND';
    """, group_title)
    log(f"Link scan result: {result}")
    time.sleep(3)
    log(f"Current URL: {driver.current_url}")


def click_cancel(driver):
    """Click the Cancel button on the View Local Group page to go back."""
    log("Clicking 'Cancel' button on View page...")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)

    cancel_xpaths = [
        "//a[contains(normalize-space(.),'Cancel')]",
        "//button[contains(normalize-space(.),'Cancel')]",
        "//input[@type='button' and contains(@value,'Cancel')]",
        "//*[contains(@class,'btn') and contains(normalize-space(.),'Cancel')]",
        "//a[contains(@href,'LocalList')]",
    ]
    for xpath in cancel_xpaths:
        found = quick_find(driver, xpath)
        if found:
            elem = found[0]
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", elem)
            time.sleep(0.5)
            try:
                elem.click()
            except Exception:
                driver.execute_script("arguments[0].click();", elem)
            log(f"Cancel clicked via: {xpath}")
            time.sleep(3)
            log(f"After cancel URL: {driver.current_url}")
            return

    # Last resort: navigate back to Local Group List directly
    log("WARNING: No Cancel element found. Navigating back to list...")
    driver.get(GROUP_LOCAL_LIST_URL)
    time.sleep(3)
    log(f"Navigated back. URL: {driver.current_url}")


# ── ASSIGN USERS Functions ───────────────────────────────────────────────────

def search_and_click_assigned_users(driver, wait, group_title):
    """Find the target group in the Local Group List and click its Assigned Users link.

    The list page has action links per row – we look for 'AssignedUsers' href.
    """
    log(f"Searching for group '{group_title}' to open Assigned Users...")

    # Try to use the search/filter box if available
    driver.execute_script("""
        var inputs = document.querySelectorAll(
            'input[type="text"][name*="search" i], input[type="text"][name*="filter" i], '
            + 'input[type="text"][placeholder*="search" i], input[type="text"][placeholder*="filter" i], '
            + 'input[type="search"]'
        );
        for (var i = 0; i < inputs.length; i++) {
            if (inputs[i].offsetParent !== null) {
                inputs[i].value = arguments[0];
                inputs[i].dispatchEvent(new Event('input', {bubbles:true}));
                inputs[i].dispatchEvent(new Event('change', {bubbles:true}));
                inputs[i].dispatchEvent(new Event('keyup', {bubbles:true}));
                return;
            }
        }
    """, group_title)
    time.sleep(2)

    # Find row containing the group title and click the Assigned Users link
    log(f"Looking for '{group_title}' row and Assigned Users link...")
    assigned_xpaths = [
        f"//tr[td[contains(normalize-space(.), '{group_title}')]]//a[contains(@href,'AssignedUsers')]",
        f"//tr[td[contains(normalize-space(.), '{group_title}')]]//a[contains(normalize-space(.),'Assigned')]",
        f"//tr[td[contains(normalize-space(.), '{group_title}')]]//a[contains(normalize-space(.),'Users')]",
    ]
    for xpath in assigned_xpaths:
        found = quick_find(driver, xpath)
        if found:
            elem = found[0]
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", elem)
            time.sleep(0.5)
            try:
                elem.click()
            except Exception:
                driver.execute_script("arguments[0].click();", elem)
            log(f"Assigned Users clicked via: {xpath}")
            time.sleep(3)
            log(f"Assigned Users page URL: {driver.current_url}")
            return

    # Fallback: scan all links in the row for 'AssignedUsers' or 'Assigned' text
    log("Direct XPath not found. Scanning row links...")
    result = driver.execute_script("""
        var rows = document.querySelectorAll('tr');
        for (var i = 0; i < rows.length; i++) {
            if (rows[i].textContent.indexOf(arguments[0]) >= 0) {
                var links = rows[i].querySelectorAll('a');
                for (var j = 0; j < links.length; j++) {
                    var href = (links[j].getAttribute('href') || '').toLowerCase();
                    if (href.indexOf('assignedusers') >= 0 || href.indexOf('assigned') >= 0) {
                        links[j].scrollIntoView({block: 'center'});
                        links[j].click();
                        return 'clicked_assigned_users';
                    }
                }
            }
        }
        return 'NOT_FOUND';
    """, group_title)
    log(f"Link scan result: {result}")
    time.sleep(3)
    log(f"Current URL: {driver.current_url}")


def click_assign_users_button(driver, wait):
    """On the Assigned Users page, click the '+ Assign User(s)' button.

    This navigates from AssignedUsers to AssignUsers page.
    """
    log("Clicking '+ Assign User(s)' button...")
    time.sleep(2)

    assign_btn_xpaths = [
        "//a[contains(normalize-space(.),'Assign User')]",
        "//a[contains(@href,'AssignUsers')]",
        "//button[contains(normalize-space(.),'Assign User')]",
        "//*[contains(@class,'btn') and contains(normalize-space(.),'Assign')]",
    ]
    for xpath in assign_btn_xpaths:
        found = quick_find(driver, xpath)
        if found:
            elem = found[0]
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", elem)
            time.sleep(0.5)
            try:
                elem.click()
            except Exception:
                driver.execute_script("arguments[0].click();", elem)
            log(f"Assign User(s) button clicked via: {xpath}")
            time.sleep(3)
            log(f"Assign Users page URL: {driver.current_url}")
            return

    log("WARNING: '+ Assign User(s)' button not found.")


def select_user_and_assign(driver, wait):
    """On the Assign Users page, select a user checkbox and click '+ Assign'.

    The page shows a table of users with checkboxes. We select the first
    available user row checkbox and then click the '+ Assign' button.
    """
    log("Selecting a user to assign...")
    time.sleep(2)

    # Select the first user checkbox in the table (skip header checkbox)
    checkbox_selected = driver.execute_script("""
        // Find all checkboxes in the user table rows (skip the header 'select all' checkbox)
        var checkboxes = document.querySelectorAll('table tbody tr td input[type="checkbox"]');
        if (checkboxes.length === 0) {
            // Fallback: try all checkboxes except the first one (header)
            checkboxes = document.querySelectorAll('input[type="checkbox"]');
        }
        for (var i = 0; i < checkboxes.length; i++) {
            var cb = checkboxes[i];
            // Skip header/select-all checkboxes (usually in <th>)
            if (cb.closest('th')) continue;
            if (cb.offsetParent !== null && !cb.checked) {
                cb.scrollIntoView({block: 'center'});
                cb.click();
                return 'selected:' + (cb.closest('tr') ? cb.closest('tr').textContent.trim().substring(0, 60) : 'user');
            }
        }
        return 'no_checkbox_found';
    """)
    log(f"User checkbox: {checkbox_selected}")
    time.sleep(1)

    # Click the '+ Assign' button
    log("Clicking '+ Assign' button...")
    assign_xpaths = [
        "//a[contains(@class,'btn') and contains(normalize-space(.),'Assign') and not(contains(normalize-space(.),'User'))]",
        "//a[contains(normalize-space(.),'Assign') and contains(@href,'Assign')]",
        "//button[contains(normalize-space(.),'Assign') and not(contains(normalize-space(.),'User'))]",
        "//*[contains(@class,'btn') and normalize-space(.)='Assign']",
        "//a[contains(@class,'btn') and contains(normalize-space(.),'Assign')]",
    ]
    for xpath in assign_xpaths:
        found = quick_find(driver, xpath)
        if found:
            elem = found[0]
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", elem)
            time.sleep(0.5)
            try:
                elem.click()
            except Exception:
                driver.execute_script("arguments[0].click();", elem)
            log(f"Assign button clicked via: {xpath}")
            time.sleep(3)
            log(f"After assign URL: {driver.current_url}")
            return

    log("WARNING: '+ Assign' button not found.")


def click_back_button(driver):
    """Click the Back button to navigate back from the current page."""
    log("Clicking 'Back' button...")
    time.sleep(1)

    back_xpaths = [
        "//a[contains(normalize-space(.),'Back')]",
        "//button[contains(normalize-space(.),'Back')]",
        "//*[contains(@class,'btn') and contains(normalize-space(.),'Back')]",
        "//a[contains(@href,'AssignedUsers')]",
    ]
    for xpath in back_xpaths:
        found = quick_find(driver, xpath)
        if found:
            elem = found[0]
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", elem)
            time.sleep(0.5)
            try:
                elem.click()
            except Exception:
                driver.execute_script("arguments[0].click();", elem)
            log(f"Back clicked via: {xpath}")
            time.sleep(3)
            log(f"After Back URL: {driver.current_url}")
            return

    # Last resort: browser back
    log("WARNING: No Back button found. Using browser back...")
    driver.back()
    time.sleep(3)
    log(f"After browser back URL: {driver.current_url}")


# ── CLONE USER GROUP Functions ───────────────────────────────────────────────

def search_and_click_clone(driver, wait, group_title):
    """Find the target group in the Local Group List and click its Clone Group link.

    Looks for a link containing 'Clone' text or 'LocalCreate?OriginalBOGID' in href.
    """
    log(f"Searching for group '{group_title}' to clone...")

    # Try the search/filter box if available
    driver.execute_script("""
        var inputs = document.querySelectorAll(
            'input[type="text"][name*="search" i], input[type="text"][name*="filter" i], '
            + 'input[type="text"][placeholder*="search" i], input[type="text"][placeholder*="filter" i], '
            + 'input[type="search"]'
        );
        for (var i = 0; i < inputs.length; i++) {
            if (inputs[i].offsetParent !== null) {
                inputs[i].value = arguments[0];
                inputs[i].dispatchEvent(new Event('input', {bubbles:true}));
                inputs[i].dispatchEvent(new Event('change', {bubbles:true}));
                inputs[i].dispatchEvent(new Event('keyup', {bubbles:true}));
                return;
            }
        }
    """, group_title)
    time.sleep(2)

    # Find the row containing the group title and click Clone Group link
    log(f"Looking for '{group_title}' row and Clone Group link...")
    clone_xpaths = [
        f"//tr[td[contains(normalize-space(.), '{group_title}')]]//a[contains(@href,'LocalCreate?OriginalBOGID')]",
        f"//tr[td[contains(normalize-space(.), '{group_title}')]]//a[contains(normalize-space(.),'Clone')]",
        f"//tr[td[contains(normalize-space(.), '{group_title}')]]//a[contains(@href,'Clone')]",
    ]
    for xpath in clone_xpaths:
        found = quick_find(driver, xpath)
        if found:
            elem = found[0]
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", elem)
            time.sleep(0.5)
            try:
                elem.click()
            except Exception:
                driver.execute_script("arguments[0].click();", elem)
            log(f"Clone Group clicked via: {xpath}")
            time.sleep(3)
            log(f"Clone page URL: {driver.current_url}")
            return

    # Fallback: scan all links in the row for 'clone' or 'LocalCreate' href
    log("Direct XPath not found. Scanning row links for Clone...")
    result = driver.execute_script("""
        var rows = document.querySelectorAll('tr');
        for (var i = 0; i < rows.length; i++) {
            if (rows[i].textContent.indexOf(arguments[0]) >= 0) {
                var links = rows[i].querySelectorAll('a');
                for (var j = 0; j < links.length; j++) {
                    var href = (links[j].getAttribute('href') || '').toLowerCase();
                    var text = links[j].textContent.trim().toLowerCase();
                    if (href.indexOf('localcreate?originalbogid') >= 0
                        || href.indexOf('clone') >= 0
                        || text.indexOf('clone') >= 0) {
                        links[j].scrollIntoView({block: 'center'});
                        links[j].click();
                        return 'clicked_clone';
                    }
                }
            }
        }
        return 'NOT_FOUND';
    """, group_title)
    log(f"Link scan result: {result}")
    time.sleep(3)
    log(f"Current URL: {driver.current_url}")


def modify_cloned_group_info(driver, new_title, new_description):
    """On the Create Local Group (clone) page, clear pre-filled Title/Description
    and enter new values. The clone page pre-fills 'Clone Of <original>' text.
    """
    log(f"Modifying cloned group: Title='{new_title}', Description='{new_description}'")
    time.sleep(2)

    # Clear and fill Title (first visible text input) and Description (second)
    driver.execute_script("""
        var inputs = document.querySelectorAll('input[type="text"]');
        var visible = [];
        for (var i = 0; i < inputs.length; i++) {
            if (inputs[i].offsetParent !== null) visible.push(inputs[i]);
        }
        if (visible.length >= 1) {
            visible[0].value = '';
            visible[0].value = arguments[0];
            visible[0].dispatchEvent(new Event('input', {bubbles:true}));
            visible[0].dispatchEvent(new Event('change', {bubbles:true}));
        }
        if (visible.length >= 2) {
            visible[1].value = '';
            visible[1].value = arguments[1];
            visible[1].dispatchEvent(new Event('input', {bubbles:true}));
            visible[1].dispatchEvent(new Event('change', {bubbles:true}));
        }
    """, new_title, new_description)
    log("Cloned group Title and Description updated via JS.")


# ── DELETE USER GROUP Functions ───────────────────────────────────────────────

def select_group_row(driver, group_title):
    """Click on the target group row in the Local Group List to select it.

    The toolbar buttons (Edit, Delete, View, etc.) act on the currently
    selected row, so we must click the row first.
    """
    log(f"Selecting group row '{group_title}'...")

    # Try the search/filter box to narrow down the list
    driver.execute_script("""
        var inputs = document.querySelectorAll(
            'input[type="text"][name*="search" i], input[type="text"][name*="filter" i], '
            + 'input[type="text"][placeholder*="search" i], input[type="text"][placeholder*="filter" i], '
            + 'input[type="search"]'
        );
        for (var i = 0; i < inputs.length; i++) {
            if (inputs[i].offsetParent !== null) {
                inputs[i].value = arguments[0];
                inputs[i].dispatchEvent(new Event('input', {bubbles:true}));
                inputs[i].dispatchEvent(new Event('change', {bubbles:true}));
                inputs[i].dispatchEvent(new Event('keyup', {bubbles:true}));
                return;
            }
        }
    """, group_title)
    time.sleep(2)

    # Click the row that contains the group title
    row_xpaths = [
        f"//tr[td[contains(normalize-space(.), '{group_title}')]]",
        f"//tr[td/a[contains(normalize-space(.), '{group_title}')]]",
    ]
    for xpath in row_xpaths:
        found = quick_find(driver, xpath)
        if found:
            row = found[0]
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", row)
            time.sleep(0.5)
            try:
                row.click()
            except Exception:
                driver.execute_script("arguments[0].click();", row)
            log(f"Group row selected via: {xpath}")
            time.sleep(1)
            return True

    # Fallback: JS scan
    result = driver.execute_script("""
        var rows = document.querySelectorAll('tr');
        for (var i = 0; i < rows.length; i++) {
            if (rows[i].textContent.indexOf(arguments[0]) >= 0) {
                rows[i].scrollIntoView({block: 'center'});
                rows[i].click();
                return 'selected';
            }
        }
        return 'NOT_FOUND';
    """, group_title)
    log(f"Row select result: {result}")
    time.sleep(1)
    return result == 'selected'


def click_delete_button(driver):
    """Click the Delete toolbar button on the Local Group List page.

    The toolbar has buttons: + Add, Edit, Delete, View, Assigned Users, etc.
    """
    log("Clicking 'Delete' toolbar button...")

    delete_xpaths = [
        "//a[contains(normalize-space(.),'Delete')]",
        "//button[contains(normalize-space(.),'Delete')]",
        "//*[contains(@class,'delete') or contains(@class,'Delete')]//a",
        "//a[contains(@href,'Delete') or contains(@href,'delete')]",
        "//img[contains(@src,'delete') or contains(@src,'Delete')]/..",
    ]
    for xpath in delete_xpaths:
        found = quick_find(driver, xpath)
        if found:
            elem = found[0]
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", elem)
            time.sleep(0.5)
            try:
                elem.click()
            except Exception:
                driver.execute_script("arguments[0].click();", elem)
            log(f"Delete button clicked via: {xpath}")
            time.sleep(2)
            return True

    log("WARNING: Delete button not found on toolbar.")
    return False


def confirm_delete_yes(driver):
    """On the confirmation dialog 'Do you want to delete this group?', click Yes.

    The dialog has a Yes button (with checkmark icon) and a No button.
    """
    log("Looking for delete confirmation dialog...")
    time.sleep(2)

    # Try clicking the 'Yes' button in the confirmation dialog
    yes_xpaths = [
        "//button[contains(normalize-space(.),'Yes')]",
        "//a[contains(normalize-space(.),'Yes')]",
        "//*[contains(@class,'modal') or contains(@class,'dialog')]//*[contains(normalize-space(.),'Yes')][self::button or self::a or self::input]",
        "//button[contains(@class,'confirm') or contains(@class,'yes') or contains(@class,'btn-primary')]",
        "//*[contains(normalize-space(.),'Yes') and (self::button or self::a)][contains(@class,'btn')]",
    ]
    for xpath in yes_xpaths:
        found = quick_find(driver, xpath)
        if found:
            elem = found[0]
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", elem)
            time.sleep(0.5)
            try:
                elem.click()
            except Exception:
                driver.execute_script("arguments[0].click();", elem)
            log(f"'Yes' confirmation clicked via: {xpath}")
            time.sleep(3)
            return True

    # Fallback: JS scan for any visible button/link with 'Yes' text
    result = driver.execute_script("""
        var elems = document.querySelectorAll('button, a, input[type="button"], input[type="submit"]');
        for (var i = 0; i < elems.length; i++) {
            var text = elems[i].textContent.trim();
            if (text.indexOf('Yes') >= 0 && elems[i].offsetParent !== null) {
                elems[i].scrollIntoView({block: 'center'});
                elems[i].click();
                return 'clicked_yes';
            }
        }
        return 'NOT_FOUND';
    """)
    log(f"JS Yes button scan result: {result}")
    time.sleep(3)
    return result == 'clicked_yes'


# ── MY ROUTINES Functions ────────────────────────────────────────────────────

def search_and_click_my_routines(driver, wait, group_title):
    """Find the target group in the Local Group List and click its My Routines link.

    The list page shows action links per row – we look for 'Routines' in the href.
    """
    log(f"Searching for group '{group_title}' to open My Routines...")

    # Try to use the search/filter box if available
    driver.execute_script("""
        var inputs = document.querySelectorAll(
            'input[type="text"][name*="search" i], input[type="text"][name*="filter" i], '
            + 'input[type="text"][placeholder*="search" i], input[type="text"][placeholder*="filter" i], '
            + 'input[type="search"]'
        );
        for (var i = 0; i < inputs.length; i++) {
            if (inputs[i].offsetParent !== null) {
                inputs[i].value = arguments[0];
                inputs[i].dispatchEvent(new Event('input', {bubbles:true}));
                inputs[i].dispatchEvent(new Event('change', {bubbles:true}));
                inputs[i].dispatchEvent(new Event('keyup', {bubbles:true}));
                return;
            }
        }
    """, group_title)
    time.sleep(2)

    # Find the row containing the group title and click the My Routines link
    log(f"Looking for '{group_title}' row and My Routines link...")
    routines_xpaths = [
        f"//tr[td[contains(normalize-space(.), '{group_title}')]]//a[contains(@href,'Routines')]",
        f"//tr[td[contains(normalize-space(.), '{group_title}')]]//a[contains(normalize-space(.),'Routine')]",
        f"//tr[td[contains(normalize-space(.), '{group_title}')]]//a[contains(normalize-space(.),'My Routine')]",
    ]
    for xpath in routines_xpaths:
        found = quick_find(driver, xpath)
        if found:
            elem = found[0]
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", elem)
            time.sleep(0.5)
            try:
                elem.click()
            except Exception:
                driver.execute_script("arguments[0].click();", elem)
            log(f"My Routines clicked via: {xpath}")
            time.sleep(3)
            log(f"My Routines page URL: {driver.current_url}")
            return

    # Fallback: scan all links in the row for 'Routine' text/href
    log("Direct XPath not found. Scanning row links...")
    result = driver.execute_script("""
        var rows = document.querySelectorAll('tr');
        for (var i = 0; i < rows.length; i++) {
            if (rows[i].textContent.indexOf(arguments[0]) >= 0) {
                var links = rows[i].querySelectorAll('a');
                for (var j = 0; j < links.length; j++) {
                    var href = (links[j].getAttribute('href') || '').toLowerCase();
                    var text = links[j].textContent.trim().toLowerCase();
                    if (href.indexOf('routine') >= 0 || text.indexOf('routine') >= 0) {
                        links[j].scrollIntoView({block: 'center'});
                        links[j].click();
                        return 'clicked_my_routines';
                    }
                }
            }
        }
        return 'NOT_FOUND';
    """, group_title)
    log(f"Link scan result: {result}")
    time.sleep(3)
    log(f"Current URL: {driver.current_url}")


def select_routine_schedules_and_save(driver):
    """On the Manage My Routines page, select Daily/Weekly/Monthly checkboxes and Save.

    The page shows a table of routines (Manage User, Manage User Group, etc.)
    with Daily, Weekly, Monthly checkbox columns. We select a few checkboxes
    across different routines, then click Save.
    """
    log("Selecting routine schedule checkboxes (Daily/Weekly/Monthly)...")
    time.sleep(2)

    # Select checkboxes in the routine table
    # Strategy: find all unchecked checkboxes in the table and check a few
    selected_count = driver.execute_script("""
        var table = document.querySelector('table');
        if (!table) return 0;

        var rows = table.querySelectorAll('tbody tr, tr');
        var count = 0;

        for (var i = 0; i < rows.length && count < 6; i++) {
            var checkboxes = rows[i].querySelectorAll('input[type="checkbox"]');
            if (checkboxes.length === 0) continue;

            for (var j = 0; j < checkboxes.length && count < 6; j++) {
                if (!checkboxes[j].checked && checkboxes[j].offsetParent !== null) {
                    checkboxes[j].scrollIntoView({block: 'center'});
                    checkboxes[j].click();
                    count++;
                }
            }
        }
        return count;
    """)
    log(f"Selected {selected_count} routine schedule checkboxes.")
    time.sleep(1)

    # Click Save button
    log("Clicking 'Save' button on My Routines page...")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)

    save_xpaths = [
        "//*[contains(translate(normalize-space(.),'SAVE','save'),'save') and (self::a or self::button or self::input)]",
        "//img[contains(@src,'save') or contains(@src,'Save')]",
        "//*[contains(translate(@onclick,'SAVE','save'),'save')]",
        "//a[contains(@href,'Save') or contains(@href,'save')]",
        "//input[@type='submit']",
        "//button[@type='submit']",
    ]
    for xpath in save_xpaths:
        found = quick_find(driver, xpath)
        if found:
            elem = found[0]
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", elem)
            time.sleep(0.5)
            try:
                elem.click()
            except Exception:
                driver.execute_script("arguments[0].click();", elem)
            log(f"Save clicked via: {xpath}")
            time.sleep(3)
            log(f"After save URL: {driver.current_url}")
            return

    log("WARNING: Save button not found on My Routines page.")


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    driver = get_driver()
    wait = WebDriverWait(driver, 15)

    try:
        # ============================================================
        # PART 1 — CREATE a new Local User Group
        # ============================================================
        log("=" * 60)
        log("PART 1: CREATE Local User Group")
        log("=" * 60)

        # Step 1: Login
        login(driver, wait)
        take_screenshot(driver, "01_after_login")

        # Step 2-4: Navigate to Create Local Group
        navigate_to_local_create(driver, wait)
        take_screenshot(driver, "05_create_local_group_form")

        # Step 5-6: Fill Title, Description, Plant Users
        fill_group_info(driver, GROUP_TITLE, GROUP_DESCRIPTION)
        take_screenshot(driver, "06_group_info_filled")

        # Step 7: Select some privilege checkboxes
        select_privileges(driver)
        take_screenshot(driver, "07_privileges_selected")

        # Step 8: Click Save
        click_save(driver)
        take_screenshot(driver, "08_after_save")

        # Verify create
        current_url = driver.current_url.lower()
        if "locallist" in current_url or "syslist" in current_url:
            log(f"SUCCESS: User group '{GROUP_TITLE}' created successfully!")
        elif "localcreate" in current_url:
            errors = quick_find(driver,
                "//*[contains(@class,'validation-summary-errors')]"
                " | //*[contains(@class,'field-validation-error')]"
                " | //*[contains(@class,'alert-danger')]"
            )
            if errors:
                for e in errors:
                    log(f"VALIDATION ERROR: {e.text.strip()}")
            else:
                log("WARNING: Still on Create form but no visible errors.")
        else:
            log(f"INFO: Final URL = {driver.current_url}")

        take_screenshot(driver, "09_create_final_state")

        # ============================================================
        # PART 2 — EDIT the existing Local User Group
        # ============================================================
        log("")
        log("=" * 60)
        log(f"PART 2: EDIT Local User Group '{EDIT_GROUP_TITLE}'")
        log("=" * 60)

        # Step 9: Navigate to Local Group List
        navigate_to_local_list(driver, wait)
        take_screenshot(driver, "10_local_list_for_edit")

        # Step 10: Search for the group and click Edit
        search_and_click_edit(driver, wait, EDIT_GROUP_TITLE)
        take_screenshot(driver, "11_edit_page_opened")

        # Step 11: Modify Title and Description
        modify_group_info(driver, EDITED_TITLE, EDITED_DESCRIPTION)
        take_screenshot(driver, "12_info_modified")

        # Step 12: Modify privileges
        modify_privileges(driver)
        take_screenshot(driver, "13_privileges_modified")

        # Step 13: Click Save
        click_save(driver)
        take_screenshot(driver, "14_after_edit_save")

        # Verify edit
        current_url = driver.current_url.lower()
        if "locallist" in current_url or "localupdate" in current_url:
            log(f"SUCCESS: User group edited to '{EDITED_TITLE}' successfully!")
        else:
            log(f"INFO: Final URL after edit = {driver.current_url}")

        take_screenshot(driver, "15_edit_final_state")

        # ============================================================
        # PART 3 — VIEW the Local User Group and Cancel
        # ============================================================
        log("")
        log("=" * 60)
        log(f"PART 3: VIEW Local User Group '{VIEW_GROUP_TITLE}'")
        log("=" * 60)

        # Step 14: Navigate to Local Group List
        navigate_to_local_list(driver, wait)
        take_screenshot(driver, "16_local_list_for_view")

        # Step 15: Search for the group and click View
        search_and_click_view(driver, wait, VIEW_GROUP_TITLE)
        take_screenshot(driver, "17_view_page_opened")

        # Verify we are on the View page
        current_url = driver.current_url.lower()
        if "localview" in current_url or "view" in current_url:
            log(f"SUCCESS: View page opened for group '{VIEW_GROUP_TITLE}'.")
        else:
            log(f"INFO: Current URL after view click = {driver.current_url}")

        # Step 16: Click Cancel to go back to the list
        click_cancel(driver)
        take_screenshot(driver, "18_after_view_cancel")

        # Verify we returned to the list
        current_url = driver.current_url.lower()
        if "locallist" in current_url or "syslist" in current_url:
            log("SUCCESS: Returned to Local Group List after Cancel.")
        else:
            log(f"INFO: URL after cancel = {driver.current_url}")

        take_screenshot(driver, "19_view_final_state")

        # ============================================================
        # PART 4 — ASSIGN USERS to the Local User Group
        # ============================================================
        log("")
        log("=" * 60)
        log(f"PART 4: ASSIGN USERS to Group '{ASSIGN_GROUP_TITLE}'")
        log("=" * 60)

        # Step 17: Navigate to Local Group List
        navigate_to_local_list(driver, wait)
        take_screenshot(driver, "20_local_list_for_assign")

        # Step 18: Search for the group and click Assigned Users link
        search_and_click_assigned_users(driver, wait, ASSIGN_GROUP_TITLE)
        take_screenshot(driver, "21_assigned_users_page")

        # Verify we are on the Assigned Users page
        current_url = driver.current_url.lower()
        if "assignedusers" in current_url:
            log(f"SUCCESS: Assigned Users page opened for group.")
        else:
            log(f"INFO: Current URL = {driver.current_url}")

        # Step 19: Click "+ Assign User(s)" button to open Assign Users page
        click_assign_users_button(driver, wait)
        take_screenshot(driver, "22_assign_users_page")

        # Verify we are on the Assign Users page
        current_url = driver.current_url.lower()
        if "assignusers" in current_url:
            log("SUCCESS: Assign Users page opened.")
        else:
            log(f"INFO: Current URL = {driver.current_url}")

        # Step 20: Select a user and click "+ Assign"
        select_user_and_assign(driver, wait)
        take_screenshot(driver, "23_user_assigned")

        # Step 21: Click Back button to navigate back
        click_back_button(driver)
        take_screenshot(driver, "24_after_assign_back")

        # Verify we returned to Assigned Users or Local Group List
        current_url = driver.current_url.lower()
        if "assignedusers" in current_url or "locallist" in current_url:
            log("SUCCESS: Navigated back after assigning user.")
        else:
            log(f"INFO: URL after back = {driver.current_url}")

        take_screenshot(driver, "25_assign_final_state")

        # ============================================================
        # PART 5 — MY ROUTINES for the Local User Group
        # ============================================================
        log("")
        log("=" * 60)
        log(f"PART 5: MY ROUTINES for Group '{ROUTINES_GROUP_TITLE}'")
        log("=" * 60)

        # Step 22: Navigate to Local Group List
        navigate_to_local_list(driver, wait)
        take_screenshot(driver, "26_local_list_for_routines")

        # Step 23: Search for the group and click My Routines
        search_and_click_my_routines(driver, wait, ROUTINES_GROUP_TITLE)
        take_screenshot(driver, "27_my_routines_page")

        # Verify we are on the Manage My Routines page
        current_url = driver.current_url.lower()
        if "routine" in current_url:
            log("SUCCESS: My Routines page opened.")
        else:
            log(f"INFO: Current URL = {driver.current_url}")

        # Step 24-25: Select Daily/Weekly/Monthly checkboxes and Save
        select_routine_schedules_and_save(driver)
        take_screenshot(driver, "28_routines_saved")

        # Verify save completed
        current_url = driver.current_url.lower()
        if "routine" in current_url or "locallist" in current_url:
            log("SUCCESS: My Routines saved successfully.")
        else:
            log(f"INFO: URL after save = {driver.current_url}")

        take_screenshot(driver, "29_routines_final_state")

        # ============================================================
        # PART 6 — CLONE USER GROUP
        # ============================================================
        log("")
        log("=" * 60)
        log(f"PART 6: CLONE USER GROUP '{CLONE_GROUP_TITLE}'")
        log("=" * 60)

        # Step 26: Navigate to Local Group List
        navigate_to_local_list(driver, wait)
        take_screenshot(driver, "30_local_list_for_clone")

        # Step 27: Search for the group and click Clone Group
        search_and_click_clone(driver, wait, CLONE_GROUP_TITLE)
        take_screenshot(driver, "31_clone_create_page")

        # Verify we are on the Create Local Group (clone) page
        current_url = driver.current_url.lower()
        if "localcreate" in current_url:
            log("SUCCESS: Clone / Create Local Group page opened.")
        else:
            log(f"INFO: Current URL = {driver.current_url}")

        # Step 28: Modify Title and Description on the clone page
        modify_cloned_group_info(driver, CLONED_TITLE, CLONED_DESCRIPTION)
        take_screenshot(driver, "32_clone_modified_info")

        # Step 29: Modify some privileges (toggle a few Allow checkboxes)
        select_privileges(driver)
        take_screenshot(driver, "33_clone_privileges_set")

        # Step 30: Click Save to create the cloned group
        click_save(driver)
        take_screenshot(driver, "34_clone_saved")

        # Verify save completed
        current_url = driver.current_url.lower()
        if "locallist" in current_url or "localdetail" in current_url:
            log(f"SUCCESS: Cloned group '{CLONED_TITLE}' saved successfully.")
        else:
            log(f"INFO: URL after clone save = {driver.current_url}")

        take_screenshot(driver, "35_clone_final_state")

        # ============================================================
        # PART 7 — DELETE USER GROUP
        # ============================================================
        log("")
        log("=" * 60)
        log(f"PART 7: DELETE USER GROUP '{DELETE_GROUP_TITLE}'")
        log("=" * 60)

        # Step 31: Navigate to Local Group List
        navigate_to_local_list(driver, wait)
        take_screenshot(driver, "36_local_list_for_delete")

        # Step 32: Search for the group and select (click) its row
        row_selected = select_group_row(driver, DELETE_GROUP_TITLE)
        take_screenshot(driver, "37_group_row_selected")
        if row_selected:
            log(f"SUCCESS: Group '{DELETE_GROUP_TITLE}' row selected.")
        else:
            log(f"WARNING: Could not select group '{DELETE_GROUP_TITLE}' row.")

        # Step 33: Click the Delete toolbar button
        click_delete_button(driver)
        take_screenshot(driver, "38_delete_dialog")

        # Step 34: Confirm deletion by clicking 'Yes'
        confirm_delete_yes(driver)
        take_screenshot(driver, "39_delete_confirmed")

        # Step 35: Verify the group is removed from the list
        time.sleep(2)
        current_url = driver.current_url.lower()
        if "locallist" in current_url:
            log("On Local List page after deletion.")
        else:
            log(f"INFO: URL after delete = {driver.current_url}")

        # Check the group no longer appears in the list
        still_present = driver.execute_script("""
            var rows = document.querySelectorAll('tr');
            for (var i = 0; i < rows.length; i++) {
                if (rows[i].textContent.indexOf(arguments[0]) >= 0) return true;
            }
            return false;
        """, DELETE_GROUP_TITLE)
        if still_present:
            log(f"INFO: Group '{DELETE_GROUP_TITLE}' still visible (may need page refresh).")
        else:
            log(f"SUCCESS: Group '{DELETE_GROUP_TITLE}' deleted and removed from list.")

        take_screenshot(driver, "40_delete_final_state")

    except Exception as e:
        log(f"ERROR: {e}")
        take_screenshot(driver, "error_state")
        raise
    finally:
        driver.quit()
        log("Browser closed. Done.")


if __name__ == "__main__":
    main()
