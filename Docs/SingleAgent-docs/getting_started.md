# Getting Started

This guide will help you install, launch, and use the SingleAgent multi-agent system from a user's perspective.

## Installation

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <repo-url>
   cd SingleAgent
   ```
2. **Install dependencies** (Python 3.9+ recommended):
   ```bash
   pip install -r requirements.txt
   # or, if requirements.txt is missing, install manually:
   pip install openai prompt_toolkit spacy
   python -m spacy download en_core_web_lg
   ```

## Launching the System

Start the interactive CLI with:
```bash
python main.py
```

You will see a welcome message and the system will initialize the spaCy model (for entity recognition). The default agent is the **Code Agent**.

## Basic Usage

- Type your question or command and press Enter.
- Use the up/down arrows to browse your input history.
- The system will suggest completions based on your history.

### Switching Agents
You can switch between agents at any time:
- `!code` — Switch to Code Agent
- `!architect` — Switch to Architect Agent
- `!browser` — Switch to Web Browser Agent

### Getting Help
Type `!help` to see all available commands and special features.

---

See `usage.md` for a full list of commands and example workflows.
