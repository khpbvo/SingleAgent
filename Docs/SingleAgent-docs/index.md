# SingleAgent Documentation

SingleAgent is an advanced dual-agent system built on the OpenAI Agents SDK. It provides two specialized AI agents - a Code Agent for programming-related tasks and an Architect Agent for software architecture and project analysis.

## Overview

SingleAgent leverages the powerful OpenAI Agents SDK to provide two complementary AI assistants:

- **Code Agent (SingleAgent)**: Specialized in code analysis, debugging, testing, and direct programming assistance
- **Architect Agent**: Focused on software architecture, project structure analysis, and high-level design decisions

The system supports seamless switching between agents and provides advanced context management, entity tracking, and streaming output.

## Contents

1. [Quick Start Guide](quickstart.md) - Get started with SingleAgent immediately
2. [Installation](installation.md) - Complete installation instructions
3. [Architecture Overview](architecture.md) - How the system is structured
4. [Code Agent](code-agent.md) - Detailed documentation for the Code Agent
5. [Architect Agent](architect-agent.md) - Detailed documentation for the Architect Agent
6. [Tools](tools.md) - Overview or all available tools
7. [Context Management](context-management.md) - How context and entity tracking works
8. [Configuration](configuration.md) - Configuration options and customizations
9. [Usage Examples](examples.md) - Practical examples and use cases
10. [API Reference](api-reference.md) - Technical API documentation
11. [Troubleshooting](troubleshooting.md) - Common issues and solutions

## Requirements

- Python 3.8+
- OpenAI API key
- Several Python packages (see [installation](installation.md))

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key
export OPENAI_API_KEY=sk-...

# Start the system
python main.py
```

For more details, see the [Quick Start Guide](quickstart.md).

## Key Features

### Dual Agent System
- **!code** - Switch to Code Agent mode for programming tasks
- **!architect** - Switch to Architect Agent mode for architecture analysis

### Advanced Context Management
- Automatic entity tracking (files, commands, tasks)
- Smart context summaries to manage token limits
- Persistent context storage between sessions

### Comprehensive Tool Sets
- **Code Agent Tools**: Ruff, Pylint, Pyright, file operations, patch management
- **Architect Agent Tools**: AST analysis, project structure analysis, dependency graphs, design pattern detection

### Interactive CLI
- Prompt_toolkit powered interface with history and auto-suggest
- Real-time streaming output
- Color-coded output for better readability

## Who Is This For?

This documentation is written for:

- **Developers** who want to use SingleAgent for code analysis and debugging
- **Software Architects** who want to use the system for project analysis
- **Contributors** who want to understand the codebase and contribute
- **DevOps Engineers** who want to integrate the system into workflows

We assume you're familiar with:
- Basic Python programming
- [OpenAI Agents SDK](../openai-agents-sdk-docs_copy/index.md) concepts
- Command-line interfaces

## Support

For questions, bugs, or feature requests, see the [Troubleshooting](troubleshooting.md) section or consult the source code in the repository.
