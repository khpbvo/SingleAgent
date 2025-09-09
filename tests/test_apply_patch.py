"""Tests for the patch utility using the apply_patch.py script."""

from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path


def run_patch(patch_text: str, *flags: str) -> tuple[str, str]:
    """Run apply_patch.py with ``patch_text`` and return stdout and stderr."""
    proc = subprocess.run(
        [sys.executable, "apply_patch.py", *flags],
        input=patch_text.encode(),
        capture_output=True,
        check=True,
    )
    return proc.stdout.decode(), proc.stderr.decode()


def test_apply_patch_updates_file(tmp_path: Path) -> None:
    """Applying a patch with ``--no-preview`` updates the target file."""
    file_path = tmp_path / "sample.txt"
    file_path.write_text("hello\n")
    patch = textwrap.dedent(
        f"""*** Begin Patch
*** Update File: {file_path}
@@
-hello
+patched
*** End Patch
"""
    )
    stdout, stderr = run_patch(patch, "--no-preview")
    assert "Done!" in stdout
    assert stderr == ""
    assert file_path.read_text() == "patched\n"


def test_apply_patch_preview_does_not_modify_file(tmp_path: Path) -> None:
    """Using ``--preview`` shows a diff without applying changes."""
    file_path = tmp_path / "sample.txt"
    file_path.write_text("hello\n")
    patch = textwrap.dedent(
        f"""*** Begin Patch
*** Update File: {file_path}
@@
-hello
+patched
*** End Patch
"""
    )
    stdout, stderr = run_patch(patch, "--preview")
    assert "PATCH PREVIEW" in stdout
    assert "Preview complete" in stdout
    assert stderr == ""
    assert file_path.read_text() == "hello\n"
