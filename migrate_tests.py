import os
import re

# Target directory containing your test files
TARGET_DIR = r"QASite/QALS11/Admin/Entities"

def convert_file_to_pytest(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Skip files that are already configured for pytest or are utilities
    if "class Test" in content or file_path.endswith("__init__.py"):
        print(f"Skipping (Already processed or Init): {file_path}")
        return

    print(f"Processing: {file_path}")

    # 1. Add pytest import if missing
    if "import pytest" not in content:
        content = "import pytest\n" + content

    # 2. Add the scope class driver fixture right before test hooks
    fixture_code = """
# ── Pytest Fixture Setup ─────────────────────────────────────────────────────
@pytest.fixture(scope="class")
def setup_driver():
    \"\"\"Initializes webdriver once for the entire class block.\"\"\"
    driver = get_driver()
    wait = WebDriverWait(driver, 20)
    yield driver, wait
    driver.quit()
"""
    if '@pytest.fixture' not in content:
        # Insert after the last import line or setup utility line
        content = content.replace("from admin.UserGroup import login", "from admin.UserGroup import login\n" + fixture_code)

    # 3. Derive a valid Class Name from the filename (e.g., Calender.py -> TestCalender)
    base_name = os.path.splitext(os.path.basename(file_path))[0].replace("test_", "")
    class_name = f"Test{base_name}"
    
    class_declaration = f"\n\n@pytest.mark.usefixtures(\"setup_driver\")\nclass {class_name}:\n"
    
    # 4. Find all standalone step functions and indent them inside the class wrapper
    # Looks for lines like: def add_item(driver, wait):
    def indent_and_rename_functions(match):
        func_name = match.group(1)
        # Ensure function starts with "test_" for pytest discovery
        if not func_name.startswith("test_"):
            new_func_name = f"test_{func_name}"
        else:
            new_func_name = func_name
        return f"    def {new_func_name}(self, setup_driver):\n        driver, wait = setup_driver\n"

    # Regex targeting top-level functions that accept (driver, wait)
    pattern = r"^def\s+([a-zA-Z0-9_]+)\(\s*driver\s*,\s*wait\s*\)\s*:"
    content = re.sub(pattern, indent_and_rename_functions, content, flags=re.MULTILINE)

    # 5. Comment out or strip the legacy __main__ script blocks at the bottom
    content = content.replace('if __name__ == "__main__":', '# Legacy main execution script removed for Pytest suite compatibility\n# if __name__ == "__main__":')
    
    # Write the modified content back
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

def rename_to_pytest_convention(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") and not file.startswith("test_") and file != "__init__.py":
                old_path = os.path.join(root, file)
                new_path = os.path.join(root, f"test_{file.lower()}")
                os.rename(old_path, new_path)
                print(f"Renamed: {file} -> test_{file.lower()}")

if __name__ == "__main__":
    # Ensure folder is initialized
    init_path = os.path.join(TARGET_DIR, "__init__.py")
    if not os.path.exists(init_path):
        with open(init_path, "w") as f: pass
        print("Created missing __init__.py")

    # Step A: Convert file internals to class definitions
    for root, _, files in os.walk(TARGET_DIR):
        for file in files:
            if file.endswith(".py"):
                convert_file_to_pytest(os.path.join(root, file))

    # Step B: Auto-prefix filenames with test_ so the UI explorer maps them
    rename_to_pytest_convention(TARGET_DIR)
    print("\nMigration Completed Successfully!")