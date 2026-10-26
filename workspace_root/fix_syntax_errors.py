#!/usr/bin/env python3
"""Fix syntax errors in test files."""

import re
import os

os.chdir('qa_automation')

files_to_fix = [
    'tests/QALS11/Admin/Users/test_users.py',
    'tests/QALS11/Admin/Workcenter/test_Workcenter.py',
    'tests/QALS11/Admin/Users/users_backup.py',
    'tests/test_view_system_user_groups.py',
]

def fix_multiline_fstring(content):
    """Fix multiline f-strings by moving them to single line."""
    # Pattern: print( or assert( or similar with multiline f-string
    # This regex matches patterns like:
    # f"text{
    #     variable}"
    
    # Simple approach: look for f"...{\n with content then \n...}"
    pattern = r'(f"[^"]*)\s*\{\s*\n\s+([^}]*?)\s*\n\s*\}'
    content = re.sub(pattern, r'\1 { \2 }', content, flags=re.MULTILINE)
    
    # Also fix assert with multiline
    pattern = r'assert.*?\n\s+f".*?{\n.*?}"'
    
    return content

for filepath in files_to_fix:
    if not os.path.exists(filepath):
        print(f"Skipping {filepath} - not found")
        continue
    
    print(f"Fixing {filepath}...")
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # Replace problematic patterns
        # For test_users.py
        if 'test_users.py' in filepath:
            # Fix the encoding character issue and multiline f-string
            content = content.replace(
                'print(\n        f"\\n  [SESSION] Logged in as \'{ADMIN_USER}\' â€" URL: {\n            browser.current_url}")',
                'print(f"\\n  [SESSION] Logged in as \'{ADMIN_USER}\' - URL: {browser.current_url}")'
            )
        
        # For test_Workcenter.py  
        if 'test_Workcenter.py' in filepath:
            content = content.replace(
                'assert "ultrivalms" in driver.current_url, f"Login failed - URL: {\n            driver.current_url}")',
                'assert "ultrivalms" in driver.current_url, f"Login failed - URL: {driver.current_url}"'
            )
        
        # For users_backup.py - handle the multiline print statement
        if 'users_backup.py' in filepath:
            # Fix print statement with multiline f-string
            content = re.sub(
                r'print\(\s+f"\\n  Disable button — title=\'{\s+disable_btn\.get_attribute\(\'title\'\)}\' " f"class=\'{\s+disable_btn\.get_attribute\(\'class\'\)}\'"',
                'print(f"\\n  Disable button — title=\'{disable_btn.get_attribute(\'title\')}\' class=\'{disable_btn.get_attribute(\'class\')}\'\")',
                content,
                flags=re.DOTALL
            )
        
        # General fix: any multi-line f-string
        content = fix_multiline_fstring(content)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  ✓ Fixed")
    
    except Exception as e:
        print(f"  ✗ Error: {e}")

print("\nDone!")
