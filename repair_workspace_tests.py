import os
import re

TESTS_DIR = r"C:\Prcatices-AI\qa_automation\tests"

def rebuild_test_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    content = "".join(lines)
    # Check if a class header is already partially present
    has_class = "class Test" in content

    # Generate a clean Class Name based on the file name
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    clean_name = base_name.replace("test_", "")
    class_name = "Test" + "".join([word.capitalize() for word in clean_name.split("_") if word])

    new_lines = []
    class_header_inserted = has_class
    inside_test_method = False

    for line in lines:
        stripped = line.strip()
        
        # Skip legacy execution runners and main blocks at the bottom
        if "run_" in stripped and "tests(" in stripped:
            continue
        if "__main__" in line or "run_printer_tests" in line or "run_admin_entity_tests" in line:
            continue

        # Insert class header right before the first test method if it doesn't have one
        if stripped.startswith("def test_") and not class_header_inserted:
            new_lines.append(f"\nclass {class_name}:")
            class_header_inserted = True

        # Handle formatting for test methods
        if stripped.startswith("def test_"):
            inside_test_method = True
            # Force exactly 4 spaces of indentation for the method definition signature
            new_lines.append("    " + stripped)
            continue

        # Handle lines inside the test methods
        if inside_test_method:
            # Stop matching lines inside a method if we hit a global import or another class definition
            if line.startswith("from ") or line.startswith("import ") or line.startswith("class "):
                inside_test_method = False
                new_lines.append(line)
            elif stripped == "":
                new_lines.append("")
            else:
                # Ensure the contents of the method are pushed 8 spaces out (inside the class method context)
                new_lines.append("        " + stripped)
        else:
            new_lines.append(line)

    # Save cleanly back to disk
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(new_lines).replace("\n\n\n", "\n\n"))
    print(f"Normalized and fully repaired formatting for: {base_name}.py")

# Fixed the file iteration loop layout here
for root, _, files in os.walk(TESTS_DIR):
    for file in files:
        if file.endswith(".py") and file.startswith("test_"):
            rebuild_test_file(os.path.join(root, file))

print("\nWorkspace test suites normalized and fully repaired!")