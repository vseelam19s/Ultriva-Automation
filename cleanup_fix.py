"""Clean up dead code left by fix_view_timeout.py"""
import re, os, glob

files = glob.glob('admin/Entities/*.py')

dead_pattern = re.compile(
    r'        return True\n'
    r'        _dummy = [^\n]+\n'
    r'        return False\n'
)

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    if '_dummy =' in content:
        new_content = dead_pattern.sub('        return True\n', content)
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'CLEANED: {fpath}')
