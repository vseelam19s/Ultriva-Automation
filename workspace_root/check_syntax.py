#!/usr/bin/env python3
"""Check for syntax errors in specific files."""

import ast
import sys
import os

os.chdir('qa_automation')

files_to_check = [
    'tests/QALS11/Admin/Calender/test_Calender.py',
    'tests/QALS11/Admin/Entities/test_debug_route_page.py',
    'tests/QALS11/Admin/Item/NewItemCreationandAdjustLoopSize.py',
    'tests/QALS11/Admin/Users/users_backup.py',
    'tests/QALS11/Admin/Workcenter/test_Workcenter.py',
    'tests/test_data_driven.py',
]

for filepath in files_to_check:
    if not os.path.exists(filepath):
        print(f"\n{filepath} - NOT FOUND")
        continue
    
    print(f"\n{'='*60}")
    print(f"File: {filepath}")
    print(f"{'='*60}")
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        ast.parse(content)
        print("✓ No syntax errors found")
        
    except SyntaxError as e:
        print(f"✗ SyntaxError at line {e.lineno}: {e.msg}")
        if e.text:
            print(f"  Code: {e.text.strip()}")
        
        # Show context
        lines = content.split('\n')
        start = max(0, e.lineno - 3)
        end = min(len(lines), e.lineno + 2)
        
        print(f"\n  Context (lines {start+1}-{end}):")
        for i in range(start, end):
            prefix = ">>> " if i == e.lineno - 1 else "    "
            print(f"{prefix}{i+1:4d}: {lines[i][:100]}")
        
    except IndentationError as e:
        print(f"✗ IndentationError at line {e.lineno}: {e.msg}")
        if e.text:
            print(f"  Code: {e.text.strip()}")
        
        # Show context
        lines = content.split('\n')
        start = max(0, e.lineno - 3)
        end = min(len(lines), e.lineno + 2)
        
        print(f"\n  Context (lines {start+1}-{end}):")
        for i in range(start, end):
            prefix = ">>> " if i == e.lineno - 1 else "    "
            print(f"{prefix}{i+1:4d}: {lines[i][:100]}")
    
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {e}")

print("\nDone!")
