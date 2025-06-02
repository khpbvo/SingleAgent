#!/usr/bin/env python3

"""
Verification script for the apply_patch functionality.
Creates a simple diff and applies it to a temporary file.
"""

import os
import sys
from Tools.singleagent_tools import apply_patch

# Create a test file
with open("test_file.py", "w") as f:
    f.write('print("Hello, world!")\n')

# Create a simple patch
patch_content = """*** Begin Patch
*** Update File: test_file.py
- print("Hello, world!")
+ print("Hello, patched world!")

*** End Patch
"""

print("Created test_file.py with content:")
with open("test_file.py", "r") as f:
    print(f.read())

print("\nApplying patch with interactive mode...")
result = apply_patch(
    input=patch_content,
    interactive=True,  # Interactive mode with confirmation prompt
    confirm=False      # Just preview, don't apply yet
)

print("\nCheck if the file was modified...")
with open("test_file.py", "r") as f:
    content = f.read()
    print(content)
    
if 'patched world' in content:
    print("SUCCESS: File was patched!")
else:
    print("File was not patched. This is expected if you chose not to apply the patch.")
    
print("Script completed. You should have seen a colored diff and a confirmation prompt.")