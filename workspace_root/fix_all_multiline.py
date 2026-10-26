#!/usr/bin/env python3
"""Fix all multiline f-strings by finding and merging them."""

import os
import re

os.chdir('qa_automation')

files_to_fix = [
    'tests/QALS11/Admin/Entities/test_debug_route_page.py',
    'tests/QALS11/Admin/Item/NewItemCreationandAdjustLoopSize.py',
    'tests/QALS11/Admin/Users/users_backup.py',
    'tests/QALS11/Admin/Workcenter/test_Workcenter.py',
]

for filepath in files_to_fix:
    if not os.path.exists(filepath):
        print(f"Skipping {filepath} - not found")
        continue
    
    print(f"\nFixing {filepath}...")
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
        
        fixed_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Look for lines that start a print(f" statement
            if re.search(r'^\s*print\s*\(\s*f"', line) and not line.rstrip().endswith('"'):
                # This is a multiline f-string
                merged = line.rstrip()
                start_i = i
                i += 1
                
                # Keep merging lines until we find the closing quote
                while i < len(lines):
                    next_line = lines[i].rstrip()
                    if next_line:  # Skip empty lines
                        # Add the content
                        merged += ' ' + next_line.lstrip()
                        
                        # Check if we've found the closing quote
                        if merged.count('"') % 2 == 1 and merged.rstrip().endswith(')'):
                            break
                    i += 1
                
                # Clean up excessive spaces
                merged = re.sub(r'\s+', ' ', merged)
                merged = re.sub(r'\s*{\s*', '{ ', merged)
                merged = re.sub(r'\s*}\s*', ' }', merged)
                
                fixed_lines.append(merged + '\n')
            else:
                fixed_lines.append(line)
            
            i += 1
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(fixed_lines)
        
        print(f"  ✓ Fixed")
        
    except Exception as e:
        print(f"  ✗ Error: {e}")

print("\nDone!")
