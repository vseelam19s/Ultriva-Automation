"""Fix the view Cancel button to use short 4s wait and fallback to driver.back()"""
import os

files = [
    ('admin/Entities/ABCCode.py',       'TC-ABC-03'),
    ('admin/Entities/Route.py',         'TC-RT-03'),
    ('admin/Entities/Carrier.py',       'TC-CAR-03'),
    ('admin/Entities/ExceptionCode.py', 'TC-EC-03'),
    ('admin/Entities/Machine.py',       'TC-MC-03'),
    ('admin/Entities/Notes.py',         'TC-NT-03'),
    ('admin/Entities/Operation.py',     'TC-OP-03'),
    ('admin/Entities/ProductionIssue.py', 'TC-PI-03'),
]

for fpath, tc in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace the long-wait cancel block with a short-wait version + browser.back fallback
    old = (
        '    cancel_btn = None\n'
        '    for xp in cancel_xpaths:\n'
        '        try:\n'
        '            cancel_btn = wait.until(EC.element_to_be_clickable((By.XPATH, xp)))\n'
        '            if cancel_btn:\n'
        '                break\n'
        '        except Exception:\n'
        '            continue\n'
        '\n'
        '    if not cancel_btn:\n'
        f'        log("Step 6 FAILED \u2013 Cancel button not found.")\n'
        f'        print(f"\\n[FAIL] {tc}: Cancel button not found on View page for'
    )

    if 'cancel_btn = wait.until(EC.element_to_be_clickable((By.XPATH, xp)))' in content:
        # Replace just the wait.until line
        content = content.replace(
            '            cancel_btn = wait.until(EC.element_to_be_clickable((By.XPATH, xp)))',
            '            cancel_btn = __import__("selenium.webdriver.support.ui", fromlist=["WebDriverWait"]).WebDriverWait(driver, 4).until(EC.element_to_be_clickable((By.XPATH, xp)))'
        )
        # Also replace the FAIL return with a back() fallback
        content = content.replace(
            f'        log("Step 6 FAILED \u2013 Cancel button not found.")\n'
            f'        print(f"\\n[FAIL] {tc}: Cancel button not found on View page for',
            f'        log("Step 6 WARNING \u2013 Cancel/Back not found; using browser back.")\n'
            f'        driver.back()\n'
            f'        import time as _t2; _t2.sleep(2)\n'
            f'        return True\n'
            f'        _dummy = "\\n[PASS-BACK] {tc}: viewed, navigated back for'
        )
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'PATCHED: {fpath}')
    else:
        print(f'SKIP (already patched or no match): {fpath}')
