import os
import re

TESTS_DIR = r"C:\Prcatices-AI\qa_automation\tests\QALS11"

def repair_and_wrap_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Step A: Clean out any previous broken, hanging class wrapper attempts
    content = re.sub(r'^class Test\w+:\s*$', '', content, flags=re.MULTILINE)
    
    # Step B: Standardize all loose function declarations to base level for parsing
    content = re.sub(r'^\s*def test_', 'def test_', content, flags=re.MULTILINE)

    lines = content.splitlines()
    new_lines = []

    # Create a dynamic Class Name matching the file naming convention
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    clean_name = base_name.replace("test_", "")
    class_name = "Test" + "".join([w.capitalize() for w in clean_name.split("_") if w])

    class_header_inserted = False
    inside_test_method = False

    for line in lines:
        stripped = line.strip()

        # Remove dead legacy procedural runners from the file baseline
        if "run_" in stripped and "tests(" in stripped:
            continue
        if "__main__" in line or "run_printer_tests" in line or "run_admin_entity_tests" in line:
            continue

        # Position the new class header right above the first test method definition signature
        if stripped.startswith("def test_") and not class_header_inserted:
            new_lines.append(f"\nclass {class_name}:")
            class_header_inserted = True

        if stripped.startswith("def test_"):
            inside_test_method = True
            # Methods inside a class must always be indented by exactly 4 spaces
            new_lines.append("    " + stripped)
            continue

        if inside_test_method:
            # Drop context if we hit global declarations/imports mid-file
            if line.startswith("from ") or line.startswith("import ") or line.startswith("class "):
                inside_test_method = False
                new_lines.append(line)
            elif stripped == "":
                new_lines.append("")
            else:
                # SAFE INDENTATION: Push internal methods logic out to 8 spaces (Class > Method > Logic)
                # This explicitly fixes the block indentation drops that broke the parsing engine.
                new_lines.append("        " + stripped)
        else:
            new_lines.append(line)

    # Write the structurally sound code block back to file storage
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(new_lines).replace("\n\n\n", "\n\n"))
    print(f"Fixed structural indentation for module: {base_name}.py")

# Crawl the QALS11 directories recursively
print("Starting global syntax repair engine...")
for root, _, files in os.walk(TESTS_DIR):
    for file in files:
        if file.endswith(".py") and (file.startswith("test_") or "test" in file.lower()):
            repair_and_wrap_file(os.path.join(root, file))

print("\nAll files successfully repaired and structured!")