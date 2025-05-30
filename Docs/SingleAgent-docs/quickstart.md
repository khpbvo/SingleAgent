# Quick Start Guide

This guide helps you quickly set up SingleAgent and perform your first tasks.

## Before You Begin

Make sure you have:
- Python 3.8 or higher installed
- An OpenAI API key
- Git (optional, for cloning repository)

## Step 1: Installation

### Basic Setup

```bash
# Clone the repository (or download the files)
cd your-project-directory

# Install required packages
pip install -r requirements.txt
```

### Required Packages

SingleAgent requires the following packages:
```
openai
prompt_toolkit
pydantic
tiktoken
spacy
networkx
typing_extensions
toml
ruff
pylint
pyright
```

### SpaCy Model Setup

For the best entity recognition, you need to download a spaCy model:

```bash
python -m spacy download en_core_web_lg
```

## Step 2: API Key Configuration

Set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY=sk-your-api-key-here
```

For permanent setup, add this to your `~/.bashrc`, `~/.zshrc`, or equivalent.

## Step 3: First Start

Start the system:

```bash
python main.py
```

You should see:
```
Initializing spaCy model (this may take a moment)...
Dual-Agent system initialized.
Currently in Code Agent mode.
Use !code or !architect to switch between agents.
Use !history to view chat history or !clear to clear it.

=== Code Agent Mode ===

Context Summary: Working in /path/to/your/project
  - Project: your-project-name
  - Files tracked: 0
  - Commands tracked: 0
  - Token usage: 0/50000

User: 
```

## Step 4: Basic Usage

### Code Agent Tasks

The system starts in Code Agent mode by default. Try these commands:

```
# File analysis
Can you analyze the main.py file?

# Code quality check
Run ruff on all Python files

# Debugging help
I'm getting an error on line 45 or SingleAgent.py, can you help?
```

### Architect Agent Tasks

Switch to Architect mode and try:

```
!architect

# Project structure analysis
Analyze the project structure or this codebase

# Design pattern detection
What design patterns do you see in ArchitectAgent.py?

# TODO list generation
Create a TODO list for improving the code architecture
```

### Basic Commands

| Command | Description |
|---------|-------------|
| `!code` | Switch to Code Agent mode |
| `!architect` | Switch to Architect Agent mode |
| `!history` | Show chat history |
| `!clear` | Clear chat history |
| `!entities` | Show tracked entities |
| `!context` | Show context summary |
| `!manualctx` | Add manual context |

## Step 5: Example Workflow

Here's a typical workflow for analyzing a Python project:

### 1. Project Exploration (Architect Agent)
```
!architect
Analyze the project structure and give me an overview or the architecture
```

### 2. Code Quality Check (Code Agent)
```
!code
Run all linters (ruff, pylint, pyright) on the codebase
```

### 3. Specific File Analysis (Code Agent)
```
Read the main.py file and explain how it works
```

### 4. Architecture Improvements (Architect Agent)
```
!architect
What design patterns do you see and what improvements do you suggest?
```

### 5. TODO Planning (Architect Agent)
```
Create a structured TODO list with priorities for this project
```

## Tips for Effective Use

### 1. Context Management
- The system remembers your conversation history
- Entities like files and commands are automatically tracked
- Use `!context` to see what the system knows

### 2. Agent Selection
- **Code Agent** for: debugging, testing, file operations, patches
- **Architect Agent** for: structure analysis, design patterns, planning

### 3. Tool Usage
- Agents automatically use the right tools
- You don't need to specify which tool to use
- Tools are intelligently combined for complex tasks

### 4. Streaming Output
- Output is streamed in real-time for better responsiveness
- You can see the output while the agent is working

## Next Steps

Now that you have SingleAgent running, explore further:

- [Code Agent Details](code-agent.md) - Deep dive into Code Agent capabilities
- [Architect Agent Details](architect-agent.md) - Learn about architecture analysis
- [Tools Overview](tools.md) - All available tools and their usage
- [Usage Examples](examples.md) - More complex examples and use cases

## Common Issues

### "No module named 'agents'"
Make sure all packages are installed with `pip install -r requirements.txt`

### SpaCy Model Error
Download the spaCy model: `python -m spacy download en_core_web_lg`

### OpenAI API Error
Check that your API key is correctly set and valid.

For more troubleshooting, see [Troubleshooting Guide](troubleshooting.md).
