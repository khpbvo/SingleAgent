#!/usr/bin/env python3
"""
Shim launcher for scripts/apply_patch.py so you can run:

    python apply_patch.py < patch.diff

from the repository root. It simply delegates to the implementation in
scripts/apply_patch.py and passes stdin through unchanged.
"""

import os
import sys
import runpy


def main() -> None:
    repo_root = os.path.dirname(os.path.abspath(__file__))
    impl_path = os.path.join(repo_root, "scripts", "apply_patch.py")
    if not os.path.isfile(impl_path):
        sys.stderr.write(f"apply_patch backend not found at: {impl_path}\n")
        sys.exit(1)
    # Execute the real script's __main__ in-process to preserve stdin piping
    runpy.run_path(impl_path, run_name="__main__")


if __name__ == "__main__":
    main()
