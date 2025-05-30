# Quick Start Guide

This guide will help you get started with SingleAgent quickly. You'll learn the basic concepts and how to start using both agents effectively.

## Prerequisites

Before starting, ensure you have:
- Python 3.8 or higher
- OpenAI API key
- Basic familiarity with command-line interfaces

## First Steps

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd SingleAgent

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Set up your OpenAI API key:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 3. Running SingleAgent

Start the system:

```bash
python main.py
```

You'll see the interactive CLI with the prompt:
```
SingleAgent>
```

## Basic Usage

### Understanding the Dual-Agent System

SingleAgent features two specialized agents:

1. **Code Agent** (default): Best for code analysis, implementation, and file operations
2. **Architect Agent**: Best for system design, architecture planning, and high-level decisions

### Switching Between Agents

Use these commands to switch agents:

```
!code      # Switch to Code Agent
!architect # Switch to Architect Agent
```

When you switch agents, you'll see the prompt change to indicate the active agent.

### Your First Interaction

Start with a simple question:

```
SingleAgent> What is the structure of this project?
```

The Code Agent will analyze the project structure and provide insights about the codebase.

### Working with Files

The Code Agent can help with file operations:

```
SingleAgent> Show me the contents of main.py
SingleAgent> Create a new file called test.py with a simple function
SingleAgent> Explain the purpose of the context_data.py file
```

### Architecture Planning

Switch to the Architect Agent for high-level planning:

```
SingleAgent> !architect
Architect> How should I structure a new web application?
Architect> What design patterns would work best for this project?
```

## Key Commands

| Command | Description |
|---------|-------------|
| `!code` | Switch to Code Agent |
| `!architect` | Switch to Architect Agent |
| `!help` | Show available commands |
| `!context` | View current context |
| `!clear` | Clear conversation history |
| `!exit` or `!quit` | Exit the application |

## Context Management

SingleAgent automatically manages context across conversations:

- **Entity Tracking**: Automatically identifies and tracks important entities in your conversations
- **Persistent Storage**: Context is saved and can be retrieved in future sessions
- **Manual Context**: You can manually add important information to the context

### Adding Manual Context

```
SingleAgent> !context add "This project uses FastAPI for the backend"
```

## Tips for Effective Use

1. **Start Specific**: Begin with specific questions about your codebase
2. **Use Appropriate Agents**: Use Code Agent for implementation, Architect Agent for design
3. **Build Context**: Let the agents learn about your project gradually
4. **Switch When Needed**: Don't hesitate to switch agents based on your current task

## Example Workflow

Here's a typical workflow when starting a new project:

1. **Initial Analysis** (Code Agent):
   ```
   SingleAgent> Analyze the current project structure
   ```

2. **Architecture Planning** (Architect Agent):
   ```
   SingleAgent> !architect
   Architect> How should I improve the architecture of this project?
   ```

3. **Implementation** (Code Agent):
   ```
   Architect> !code
   SingleAgent> Implement the suggested architectural changes
   ```

## Next Steps

Now that you're familiar with the basics:

- Read the [Architecture Overview](architecture.md) to understand how the system works
- Explore the [Tools Reference](tools.md) to see what capabilities are available
- Check out [Examples](examples.md) for more complex usage scenarios
- Review [Configuration](configuration.md) to customize your setup

## Getting Help

If you need help at any time:
- Type `!help` in the CLI
- Check the [Troubleshooting Guide](troubleshooting.md)
- Review the [Examples](examples.md) for common patterns

Happy coding with SingleAgent!
