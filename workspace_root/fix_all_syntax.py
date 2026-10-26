#!/usr/bin/env python3
"""Fix all unterminated f-string syntax errors in test files."""

import os
import re

os.chdir('qa_automation')

# Files to fix
files_to_fix = [
    'tests/QALS11/Actions/test_expiry_date.py',
    'tests/QALS11/Admin/Calender/test_Calender.py',
    'tests/QALS11/Admin/Entities/test_debug_route_page.py',
    'tests/QALS11/Admin/Item/NewItemCreationandAdjustLoopSize.py',
    'tests/QALS11/Admin/Users/test_UsercreationValidations.py',
    'tests/QALS11/Admin/Users/test_users.py',
    'tests/QALS11/Admin/Users/users_backup.py',
    'tests/QALS11/Admin/Workcenter/test_Workcenter.py',
    'tests/test_data_driven.py',
]

for filepath in files_to_fix:
    if not os.path.exists(filepath):
        print(f"Skipping {filepath} - not found")
        continue
    
    print(f"Fixing {filepath}...")
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # Fix pattern: f"...\n            ...}"
        # This regex finds f-strings that are broken across lines
        content = re.sub(
            r'f"([^"]*)\s*\{\s*\n\s+([^}]*)\}', 
            r'f"\1 { \2 }',
            content,
            flags=re.MULTILINE
        )
        
        # Also handle patterns where the string continues on next line
        content = re.sub(
            r'(\w+)\(\s*\n\s+f"',
            r'\1(f"',
            content,
            flags=re.MULTILINE
        )
        
        # Handle specific patterns with assertion
        content = re.sub(
            r'assert\s+"[^"]*"\s+in\s+\w+\.\w+,\s+f"[^"]*\s*-\s*URL:\s*\{\s*\n\s+([^}]*)\}"',
            r'assert "ultrivalms" in driver.current_url, f"Login failed - URL: { \1 }"',
            content,
            flags=re.MULTILINE | re.DOTALL
        )
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  ✓ Fixed")
    
    except Exception as e:
        print(f"  ✗ Error: {e}")

print("\nDone!")
