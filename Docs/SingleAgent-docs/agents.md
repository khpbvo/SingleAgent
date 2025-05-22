# Agents Overview

The SingleAgent system features multiple specialized agents, each designed to help you with a different aspect of your workflow. This page explains what each agent does and when to use them.

## Code Agent
- **Purpose:** Assists with coding tasks, such as writing, editing, patching, and linting code.
- **Best for:**
  - Generating or refactoring code
  - Applying patches or code changes
  - Running code analysis tools (e.g., ruff, pylint)
  - Managing files and code context
- **How to activate:** Default agent on startup, or use `!code`

## Architect Agent
- **Purpose:** Helps you analyze and improve your software architecture and project structure.
- **Best for:**
  - Analyzing project directories and files
  - Identifying design patterns and architecture concepts
  - Suggesting refactoring or improvements
  - Generating TODO lists and project plans
- **How to activate:** Use `!architect`
- **Special commands:** `arch:readfile:path`, `arch:readdir:path`

## Web Browser Agent
- **Purpose:** Assists with web search and fetching information from online sources.
- **Best for:**
  - Looking up documentation or code examples online
  - Researching libraries, APIs, or best practices
  - Fetching and summarizing web content
- **How to activate:** Use `!browser`

## How Agents Work Together
- Agents share context, so you can switch between them without losing your place.
- When you switch agents, the current context is handed off automatically.
- Each agent has specialized tools, but all can access shared files, commands, and chat history.

---

For practical examples, see `usage.md`. For details on context, see `context.md`.
