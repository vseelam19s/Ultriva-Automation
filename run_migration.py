import os
import re

target = r"qa_automation/QASite/QALS11/Admin/Entities"

if not os.path.exists(target):
    os.makedirs(target)

init_file = os.path.join(target, "__init__.py")
if not os.path.exists(init_file):
    with open(init_file, "w") as f: pass

for root, _, files in os.walk(target):
    for file in files:
        if not file.endswith(".py") or file == "__init__.py":
            continue
        fp = os.path.join(root, file)
        with open(fp, "r", encoding="utf-8") as f:
            content = f.read()
        if "class Test" in content:
            continue
        if "import pytest" not in content:
            content = "import pytest\n" + content
        
        fix_str = "from admin.UserGroup import login\n@pytest.fixture(scope=\"class\")\ndef setup_driver():\n    driver = get_driver()\n    wait = WebDriverWait(driver, 20)\n    yield driver, wait\n    driver.quit()\n"
        content = content.replace("from admin.UserGroup import login", fix_str)
        content = re.sub(r"^def\s+([a-zA-Z0-9_]+)\(\s*driver\s*,\s*wait\s*\)\s*:", r"    def test_\1(self, setup_driver):\n        driver, wait = setup_driver\n", content, flags=re.MULTILINE)
        content = content.replace('if __name__ == "__main__":', '# Pytest active\n# if __name__ == "__main__":')
        
        with open(fp, "w", encoding="utf-8") as f:
            f.write(content)

for file in os.listdir(target):
    if file.endswith(".py") and not file.startswith("test_") and file != "__init__.py":
        os.rename(os.path.join(target, file), os.path.join(target, f"test_{file.lower()}"))

print("--- All Files Converted Successfully! ---")
