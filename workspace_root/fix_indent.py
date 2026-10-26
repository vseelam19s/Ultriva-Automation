fp = r'c:\Prcatices-AI\qa_automation\tests\QALS11\Actions\test_adhoc_receipts.py'
with open(fp, 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixed = False
for i, line in enumerate(lines):
    # Fix the extra-indented take_screenshot after the FILTER_QtyPerCard block
    if 'take_screenshot(driver, "04_mandatory_fields_filled")' in line:
        stripped = line.lstrip()
        correct = '        ' + stripped  # 8 spaces = method body indent
        if line != correct:
            print(f"Line {i+1}: {repr(line)} -> {repr(correct)}")
            lines[i] = correct
            fixed = True
        else:
            print(f"Line {i+1} already correct: {repr(line)}")

if not fixed:
    print("No fix needed or line not found")

with open(fp, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("Done.")
