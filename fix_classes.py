import os
import re

# Path to your test files directory
TESTS_DIR = r"C:\Prcatices-AI\qa_automation\tests"

def fix_test_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if the file contains a test function that has an accidental 'self' parameter
    # but doesn't have a defined 'class Test...' block yet.
    if "def test_" in content and "self" in content and "class Test" not in content:
        print(f"Fixing layout structure in: {file_path}")
        
        # Split code by lines to insert class cleanly
        lines = content.splitlines()
        new_lines = []
        class_inserted = False
        
        for line in lines:
            # Find the first occurrence of a test function definition
            if re.match(r'^\s*def test_', line) and not class_inserted:
                # Dynamically determine class name based on the file name
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                class_name = "".join([part.capitalize() for part in base_name.replace("test_", "").split("_")])
                
                # Insert the Pytest Class definition right before the first test method
                new_lines.append(f"\nclass Test{class_name}:")
                class_inserted = True
            
            # If we've already inserted the class header, indent subsequent test code blocks by 4 spaces
            if class_inserted and (line.startswith("    def test_") or line.startswith("def test_") or line.strip() == ""):
                # Normalize indentation for class methods
                if line.startswith("def test_"):
                    new_lines.append("    " + line)
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)

        # Remove dead standalone code at the bottom if present to clean up execution paths
        final_code = "\n".join(new_lines)
        final_code = re.sub(r'if __name__\s*==\s*[\'"]__main__[\'"]:\s*\n\s*run_\w+_\w+\(\)', '', final_code)

        # Save the polished class file back to disk
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(final_code)

# Recursively crawl all subdirectories under qa_automation/tests/
for root, dirs, files in os.walk(TESTS_DIR):
    for file in files:
        if file.endswith(".py") and file.startswith("test_"):
            fix_test_file(os.path.join(root, file))

print("\nAll files processed successfully!")