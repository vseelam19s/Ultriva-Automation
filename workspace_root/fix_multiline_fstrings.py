#!/usr/bin/env python3
"""Fix multiline f-strings by merging them into single lines."""

import os

os.chdir('qa_automation')

fixes = {
    'tests/QALS11/Admin/Calender/test_Calender.py': [
        {
            'start': 838,
            'old': '''                    print(f"  [PASS] Holiday selected (Date: {
                            selected_date or 'N/A'}, Description:  { selected_desc or 'N/A' })")''',
            'new': '''                    print(f"  [PASS] Holiday selected (Date: {selected_date or 'N/A'}, Description: {selected_desc or 'N/A'}")'''
        }
    ],
    'tests/QALS11/Admin/Entities/test_debug_route_page.py': [
        {
            'start': 89,
            'old': '''         print(f"  name='{
                t.get_attribute('name')}'  id=' { t.get_attribute('id') }'")''',
            'new': '''        print(f"  name='{t.get_attribute('name')}'  id='{t.get_attribute('id')}'")'''
        }
    ],
    'tests/QALS11/Admin/Item/NewItemCreationandAdjustLoopSize.py': [
        {
            'start': 794,
            'old': '''             print(f"  {
                    i:<4} {
                    item.Item_No:<20} {
                    item.Revision_No:<12} {
                    item.Item_Description:<35}")''',
            'new': '''            print(f"  {i:<4} {item.Item_No:<20} {item.Revision_No:<12} {item.Item_Description:<35}")'''
        }
    ],
    'tests/QALS11/Admin/Users/users_backup.py': [
        {
            'start': 1661,
            'old': '''         print(f"
  Disable button — title='{disable_btn.get_attribute('title')}' class='{disable_btn.get_attribute('class')}'")''',
            'new': '''        print(f"Disable button - title='{disable_btn.get_attribute('title')}' class='{disable_btn.get_attribute('class')}'")'''
        }
    ],
    'tests/QALS11/Admin/Workcenter/test_Workcenter.py': [
        {
            'start': 3068,
            'old': '''         print(f"    [FILLED] Input '{
                inp.get_attribute('id')}' =  { inp.get_attribute('value') }")''',
            'new': '''        print(f"    [FILLED] Input '{inp.get_attribute('id')}' = {inp.get_attribute('value')}")'''
        }
    ],
    'tests/test_data_driven.py': [
        {
            'start': 79,
            'old': '''# ══════════════════════════════════════════════════════════════════════════════

    """Parametrized login scenarios read directly from Login_TestData sheet."""

    @pytest.mark.parametrize("row", _negative_login, ids=_ids(_negative_login))''',
            'new': '''# ══════════════════════════════════════════════════════════════════════════════

def _negative_login_tests():
    """Parametrized login scenarios read directly from Login_TestData sheet."""

    @pytest.mark.parametrize("row", _negative_login, ids=_ids(_negative_login))'''
        }
    ],
}

for filepath, fix_list in fixes.items():
    if not os.path.exists(filepath):
        print(f"Skipping {filepath} - not found")
        continue
    
    print(f"Fixing {filepath}...")
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        for fix in fix_list:
            if fix['old'] in content:
                content = content.replace(fix['old'], fix['new'])
                print(f"  ✓ Applied fix at line {fix['start']}")
            else:
                print(f"  ✗ Could not find pattern at line {fix['start']}")
                # Try to find similar content
                lines = content.split('\n')
                target_line = lines[fix['start'] - 1] if fix['start'] <= len(lines) else ""
                print(f"     Current line {fix['start']}: {target_line[:80]}")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
    except Exception as e:
        print(f"  ✗ Error: {e}")

print("\nDone!")
