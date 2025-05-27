#!/usr/bin/env python3

"""
Test script for the apply_patch functionality.
Creates a simple diff and applies it to a temporary file.
"""

import sys
import os
from Tools.tools_single_agent import apply_patch

# Create a simple patch
patch_content = """*** Begin Patch
*** Update File: test_file.py
- print("Hello, world!")
+ print("Hello, patched world!")

*** End Patch
"""

def main():
    # Create the test file if it doesn't exist
    if not os.path.exists("test_file.py"):
        with open("test_file.py", "w") as f:
            f.write('print("Hello, world!")\n')
        print("Created test_file.py")
    
    # Apply the patch
    print("Applying patch...")
    result = apply_patch(
        input=patch_content,
        interactive=True,  # Try interactive mode first
        confirm=False      # Just preview, don't apply yet
    )
    
    print("\nResult from apply_patch:")
    print(result)
    
    # Offer to apply the patch
    choice = input("\nApply this patch? (y/n): ")
    if choice.lower() == 'y':
        result = apply_patch(
            input=patch_content,
            confirm=True  # Now actually apply it
        )
        print("Patch applied:", result)
    else:
        print("Patch not applied.")

if __name__ == "__main__":
    main()