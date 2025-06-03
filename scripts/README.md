# Scripts

This directory contains utility scripts and helper programs.

## Apply Patch System:
The project uses a custom patch system with a special "V4A diff format":

- `apply_patch.py` - **Main script** for applying patches in V4A format
- `apply_patch_prompt.py` - **Tool definition** and description for AI agents
- `verify_patch.py` - **Test script** for verifying patch functionality

The V4A diff format uses context-based patching instead of line numbers, making it more robust for AI agents.

## Other Utilities:
- `count_words.py` - Utility for counting words in files

## Documentation:
For comprehensive documentation about the apply_patch system, see:
`Docs/SingleAgent_docs/eng/apply_patch_tool_documentation.txt`
