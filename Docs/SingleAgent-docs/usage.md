# Usage Guide

This page explains how to interact with the SingleAgent system, including all available commands and example workflows.

## Command Overview

### Agent Switching
- `!code` — Switch to Code Agent (for coding, patching, linting, etc.)
- `!architect` — Switch to Architect Agent (for architecture, project structure, design patterns)
- `!browser` — Switch to Web Browser Agent (for web search and online research)

### General Commands
- `!help` — Show help message with all commands
- `!history` — Show chat history with the current agent
- `!context` — Show a summary of the current context (files, commands, entities, etc.)
- `!clear` — Clear the chat history for the current agent
- `!save` — Manually save the current context
- `!entity` — List all tracked entities (files, commands, URLs, etc.)
- `!manualctx` — List all manually added context items
- `!delctx:label` — Remove a manual context item by its label

### Special Commands
- `code:read:path` — Add the file at `path` to the persistent context (for the current agent)
- `arch:readfile:path` — Read and analyze a file with the Architect Agent
- `arch:readdir:path` — Analyze a directory structure with the Architect Agent
    - Optional parameters for `arch:readdir:`:
        - `directory_path`: Directory to analyze (required)
        - `max_depth`: How deep to scan (default: 3)
        - `include`: File patterns to include (default: ['*.py', '*.md', etc.])
        - `exclude`: File patterns to exclude (default: ['__pycache__', '*.pyc', etc.])

- `exit` or `quit` — Exit the program

## Example Workflows

### 1. Coding with the Code Agent
- Start in Code Agent mode (default)
- Ask questions, generate code, or request code changes
- Add a file to context: `code:read:my_script.py`
- View context: `!context`

### 2. Analyzing Architecture
- Switch to Architect Agent: `!architect`
- Analyze a file: `arch:readfile:my_script.py`
- Analyze a directory: `arch:readdir:src/`
- List design patterns/entities: `!entity`

### 3. Web Research
- Switch to Web Browser Agent: `!browser`
- Ask a question that requires web search or fetching online information

### 4. Managing Context
- List manual context items: `!manualctx`
- Remove a context item: `!delctx:label`
- Save context: `!save`

