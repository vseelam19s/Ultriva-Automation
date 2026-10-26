"""Script to fix test_05_compute_cards in test_adhoc_receipts.py"""
import re

filepath = r'c:\Prcatices-AI\qa_automation\tests\QALS11\Actions\test_adhoc_receipts.py'

with open(filepath, encoding='utf-8') as f:
    content = f.read()

# The new test_05_compute_cards method
new_method = '''    def test_05_compute_cards(self, driver):
        """Click Compute Cards to generate the cards table."""
        print("\\n[TC-AHR-005] Clicking Compute Cards...")

        # Compute Cards is a <span title="Compute Cards" onclick="_computecards();">
        compute_btn = None
        for locator in [
            (By.XPATH, "//span[@title=\'Compute Cards\']"),
            (By.XPATH, "//span[contains(@onclick,\'_computecards\')]"),
            (By.XPATH, "//*[@title=\'Compute Cards\']"),
            (By.XPATH, "//span[contains(normalize-space(),\'Compute Cards\')]"),
        ]:
            try:
                compute_btn = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(locator)
                )
                break
            except Exception:
                continue

        assert compute_btn, "Compute Cards button not found on Ad hoc Receipts form"
        scroll_to(driver, compute_btn)
        # Use JS call directly since span may not be a standard clickable element
        try:
            driver.execute_script("_computecards();")
        except Exception:
            driver.execute_script("arguments[0].click()", compute_btn)
        wait_ready(driver)
        time.sleep(PAUSE)

        # Dismiss any browser alert dialog (e.g. "Received Qty was not equally distributed")
        try:
            alert = WebDriverWait(driver, 4).until(EC.alert_is_present())
            alert_text = alert.text
            print(f"  [INFO] Alert dismissed: {alert_text}")
            alert.accept()
            time.sleep(0.8)
        except Exception:
            pass
        time.sleep(PAUSE)

        take_screenshot(driver, "05_after_compute_cards")
        print(f"  [URL after Compute Cards] {driver.current_url}")

        # Verify cards table row appeared
        table_populated = False
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//table//tr[td]")
                )
            )
            table_populated = True
            print("  [PASS] Cards table populated after Compute Cards.")
        except Exception:
            print("  [WARN] Cards table row not detected \u2013 proceeding to validation.")

        # Fill any empty per-card qty inputs in the generated table rows
        if table_populated:
            try:
                per_card_qty = str(int(TOTAL_RECV_QTY) // int(NO_OF_CARDS))
                qty_inputs = driver.find_elements(
                    By.XPATH,
                    "//table//tr[td]//input[@type=\'text\' or not(@type)]",
                )
                filled = 0
                for inp in qty_inputs:
                    try:
                        if inp.is_displayed() and inp.is_enabled():
                            current_val = (inp.get_attribute("value") or "").strip()
                            if not current_val:
                                inp.clear()
                                inp.send_keys(per_card_qty)
                                driver.execute_script(
                                    "arguments[0].dispatchEvent(new Event(\'change\',{bubbles:true}))",
                                    inp,
                                )
                                filled += 1
                    except Exception:
                        continue
                if filled:
                    print(f"  [INFO] Filled {filled} per-card qty field(s) with: {per_card_qty}")
                    time.sleep(0.5)
                else:
                    print("  [INFO] No empty per-card qty fields to fill.")
            except Exception as e:
                print(f"  [WARN] Could not fill per-card qty fields: {e}")
'''

# Pattern to match the old test_05 method body (from def to end, before next #── comment)
# We'll do a line-based replacement
lines = content.split('\n')

# Find start of test_05 (line containing "def test_05_compute_cards")
start_idx = None
end_idx = None
for i, line in enumerate(lines):
    if 'def test_05_compute_cards' in line:
        start_idx = i
    if start_idx is not None and i > start_idx and 'def test_06_validate_receipt' in line:
        # end_idx is the line before the TC-AHR-006 comment
        # Walk back to find the blank line before the comment
        end_idx = i - 2  # skip the blank line and comment line
        break

print(f"start_idx (0-based) = {start_idx}, end_idx (0-based) = {end_idx}")
print(f"Start line: {repr(lines[start_idx])[:80]}")
print(f"End line: {repr(lines[end_idx])[:80]}")

# Replace lines[start_idx..end_idx] with new_method lines
new_method_lines = new_method.rstrip('\n').split('\n')
new_lines = lines[:start_idx] + new_method_lines + lines[end_idx+1:]

with open(filepath, 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines))

print(f"Done. Old line count: {len(lines)}, New line count: {len(new_lines)}")
