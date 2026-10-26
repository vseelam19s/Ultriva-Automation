"""Apply all three fixes to test_adhoc_receipts.py."""
import re

fp = r'c:\Prcatices-AI\qa_automation\tests\QALS11\Actions\test_adhoc_receipts.py'
with open(fp, 'r', encoding='utf-8') as f:
    content = f.read()

# ============================================================
# FIX 1: Fill FILTER_QtyPerCard (the '@' field) in TC-04
# ============================================================
MARKER_F1 = '        take_screenshot(driver, "04_mandatory_fields_filled")\n        print("  [PASS] Mandatory fields filled successfully.")'

INSERT_F1 = '''        # -- Qty Per Card (id='FILTER_QtyPerCard') -- the '@' field next to No of Cards --
        # Required for server-side validation. per-card qty = TOTAL_RECV_QTY // NO_OF_CARDS = 1
        _per_card_qty = str(int(TOTAL_RECV_QTY) // int(NO_OF_CARDS))
        try:
            qpc_field = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "FILTER_QtyPerCard"))
            )
            scroll_to(driver, qpc_field)
            driver.execute_script("arguments[0].value = '';", qpc_field)
            qpc_field.clear()
            qpc_field.send_keys(_per_card_qty)
            driver.execute_script(
                "arguments[0].dispatchEvent(new Event('change',{bubbles:true}))",
                qpc_field,
            )
            time.sleep(0.3)
            print(f"  [INFO] Qty Per Card (@) set to: {_per_card_qty}")
        except Exception as e:
            print(f"  [WARN] Qty Per Card (FILTER_QtyPerCard) error: {e}")

        '''

if MARKER_F1 in content:
    content = content.replace(MARKER_F1, INSERT_F1 + MARKER_F1, 1)
    print('Fix 1 applied: FILTER_QtyPerCard fill added before TC-04 screenshot')
else:
    print('ERROR Fix 1: marker not found')

# ============================================================
# FIX 2: Remove the false validation bypass in TC-06
# The last fallback just checks if btnSubmitT *exists* (it always does),
# which is wrong. Remove it so the test fails correctly when validation fails.
# ============================================================
OLD_F2 = '''        if not validated:
            print("  [WARN] Validation success banner not detected \xe2\x80\x94 checking Submit button availability.")
            try:
                submit_btn = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, "btnSubmitT"))
                )
                print("  [INFO] Submit Receipt button found \xe2\x80\x94 treating validation as passed.")
                validated = True
            except Exception:
                pass

        assert validated, "Validate Receipt did not produce a success indicator."
        print("  [PASS] Receipt validated successfully.")'''

NEW_F2 = '''        assert validated, (
            "Validate Receipt failed: Submit button still has 'off' class or no success indicator. "
            "Check that all required fields (incl. FILTER_QtyPerCard) are filled before validating."
        )
        print("  [PASS] Receipt validated successfully.")'''

# Try with actual unicode bytes from the file
# The em dash character: â€" appears in the file as UTF-8 for various dashes
# Let me search more flexibly
if 'treating validation as passed.' in content:
    # Find the block by a unique enough fragment
    pattern = r'        if not validated:\n            print\("  \[WARN\] Validation success banner not detected.*?print\("  \[PASS\] Receipt validated successfully\."\)'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        content = content[:match.start()] + NEW_F2 + content[match.end():]
        print('Fix 2 applied: removed false validation bypass in TC-06')
    else:
        print('ERROR Fix 2: regex did not match')
else:
    print('Fix 2: "treating validation as passed" not found, may already be fixed')

# ============================================================
# FIX 3: In TC-07 verify Submit btn is active before submitting
# ============================================================
OLD_F3 = '''        assert submit_btn, "Submit Receipt button not found on Ad hoc Receipts form"
        scroll_to(driver, submit_btn)
        try:
            driver.execute_script("_submitReceipt('SUBMIT');")
        except Exception:
            driver.execute_script("arguments[0].click()", submit_btn)'''

NEW_F3 = '''        assert submit_btn, "Submit Receipt button not found on Ad hoc Receipts form"

        # Verify Submit button is active (no 'off' class) — it only becomes active after
        # successful validation. If it still has 'off', TC-06 validation failed.
        submit_cls = submit_btn.get_attribute("class") or ""
        assert "off" not in submit_cls, (
            f"Submit Receipt button is disabled ('off' class present: '{submit_cls}'). "
            "TC-06 validation did not succeed — cannot submit receipt."
        )

        scroll_to(driver, submit_btn)
        try:
            driver.execute_script("_submitReceipt('SUBMIT');")
        except Exception:
            driver.execute_script("arguments[0].click()", submit_btn)'''

if OLD_F3 in content:
    content = content.replace(OLD_F3, NEW_F3, 1)
    print('Fix 3 applied: Submit btn activity check added to TC-07')
else:
    print('ERROR Fix 3: marker not found')

with open(fp, 'w', encoding='utf-8') as f:
    f.write(content)

print('\nAll fixes written to file.')
