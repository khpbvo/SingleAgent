# SingleAgent - User Guide

## What is SingleAgent?

SingleAgent is an intelligent AI assistant that helps you with programming, system design, and documentation. The system features two specialized modes that work together to boost your productivity:

- **Code Agent**: Specialized in programming, debugging, and code-related tasks
- **Architect Agent**: Focused on system design, architecture, and documentation

## Installation and Setup

### Requirements
- Python 3.8 or higher
- OpenAI API key

### Installation Steps

1. **Clone and install dependencies:**
```bash
cd SingleAgent
pip install -r requirements.txt
```

2. **Download the spaCy language model:**
```bash
python -m spacy download en_core_web_lg
```

3. **Set your OpenAI API key:**
```bash
export OPENAI_API_KEY=sk-your-api-key-here
```

4. **Start the program:**
```bash
python main.py
```

## Core Functionalities

### Agent Modes

#### Code Agent Mode (Default)
The Code Agent helps you with:
- ✅ Writing and debugging code
- ✅ Reading and writing files  
- ✅ Executing commands
- ✅ Code reviews and optimizations
- ✅ Error troubleshooting

#### Architect Agent Mode
The Architect Agent helps you with:
- 🏗️ Designing system architecture
- 📋 Generating documentation
- 🔍 Code base analysis
- 📊 Project planning
- 🎯 Best practices advice

### Switching Between Modes

```
!code       # Switch to Code Agent
!architect  # Switch to Architect Agent
```

## Important Commands

### Basic Commands
```
!help       # Show all available commands
!history    # View chat history
!context    # Show context summary
!clear      # Clear chat history
!save       # Manually save context
exit/quit   # Close the program
```

### Context Management
```
!entity     # View tracked entities
!manualctx  # Show manually added context
!delctx:label # Remove context item by label
```

### Special Functions
```
code:read:path          # Add file to persistent context
arch:readfile:path      # Analyze file with Architect Agent
arch:readdir:path       # Analyze directory structure
```

## Practical Examples

### Example 1: Code Generation
```
User: Write a Python function to create a REST API with FastAPI

Code Agent: I'll create a FastAPI application for you...
[Agent generates code with explanation]
```

### Example 2: File Analysis
```
arch:readfile:src/main.py

[Architect Agent analyzes the file and provides detailed feedback on structure and improvements]
```

### Example 3: Project Structure Analysis
```
arch:readdir:src

[Architect Agent scans the directory and provides an overview of the project architecture]
```

### Example 4: Adding Context
```
code:read:config/settings.py

[Adds the file to persistent context so the agent can refer to it in future conversations]
```

## Advanced Features

### Intelligent Context Management
- **Automatic Entity Tracking**: The system automatically recognizes files, commands, and concepts
- **Persistent Context**: Important information is preserved between sessions
- **Token Management**: Efficient context management to stay within API limits

### Real-time Streaming
- **Live Response**: See answers appear in real-time
- **Tool Feedback**: Get immediate feedback when tools are being used
- **Progress Indicators**: See when the system is working on complex tasks

### Smart File Operations
- **Safe Writing**: Automatic backups and validation
- **Directory Scanning**: Intelligent analysis of project structures
- **Content Summarization**: Automatic summaries of large files

## Tips for Effective Use

### 1. Choose the Right Mode
- **Code problems?** → Use Code Agent
- **Architecture questions?** → Use Architect Agent

### 2. Use Context Wisely
```
# Add relevant files to context
code:read:src/models.py
code:read:config.py

# Then ask for help
"Can you optimize these models for better performance?"
```

### 3. Build Up Context
```
# Start with overview
arch:readdir:src

# Zoom in on specific components  
arch:readfile:src/main.py

# Ask for improvements
"How can I better structure this architecture?"
```

### 4. Use Historical Context
The system remembers:
- Previously written code
- Discussed architectural decisions
- Identified problems
- Applied solutions

## Workflow Examples

### New Feature Development
1. **Analyze current code:**
   ```
   arch:readdir:src
   ```

2. **Switch to Code Agent:**
   ```
   !code
   ```

3. **Implement feature:**
   ```
   "Add a user authentication system to my FastAPI app"
   ```

4. **Test and refine:**
   ```
   "Run the tests and fix any errors"
   ```

### Code Review Workflow
1. **Add code to context:**
   ```
   code:read:src/new_feature.py
   ```

2. **Switch to Architect:**
   ```
   !architect
   ```

3. **Ask for review:**
   ```
   "Review this code for best practices and potential improvements"
   ```

### Debugging Workflow
1. **Share error information:**
   ```
   "I'm getting this error: [error message]"
   ```

2. **Add relevant files:**
   ```
   code:read:src/problematic_file.py
   ```

3. **Ask for debugging help:**
   ```
   "Help me debug this error"
   ```

## Troubleshooting

### Common Problems

#### "API Key Error"
```bash
# Check your API key
echo $OPENAI_API_KEY

# Set again if empty
export OPENAI_API_KEY=sk-your-key
```

#### "spaCy Model Not Found"
```bash
# Download the model again
python -m spacy download en_core_web_lg
```

#### "Context Too Large"
```
!clear          # Clear history
!delctx:label   # Remove specific context items
```

#### Agent Responds Slowly
- Clear unnecessary context with `!clear`
- Remove old files from context
- Check your internet connection

### Debug Information
The system saves logs in:
```
logs/main.log           # General logs
logs/singleagent.log    # Code Agent logs
logs/architectagent.log # Architect Agent logs
```

## Best Practices

### 1. Context Hygiene
- **Clear regularly** old conversations with `!clear`
- **Remove irrelevant** context items
- **Add only relevant** files to context

### 2. Effective Questions
- **Be specific** in your questions
- **Provide context** about what you're trying to achieve
- **Use examples** where possible

### 3. Tool Usage
- **Use arch:readdir** for project overviews
- **Use code:read** for specific files
- **Switch between modes** depending on your task

### 4. Workflow Organization
- **Start broad** (architecture overview)
- **Zoom in** on specific components
- **Test iteratively** during development

## Frequently Asked Questions

**Q: How do I know which mode to use?**
A: Code Agent for implementation, Architect Agent for design and planning.

**Q: Is my context automatically saved?**
A: Yes, with every interaction. You can also manually save with `!save`.

**Q: Can I analyze multiple files at once?**
A: Yes, use `arch:readdir` for directory analysis or add multiple files with `code:read`.

**Q: How do I remove old context?**
A: Use `!clear` for everything or `!delctx:label` for specific items.

**Q: Can the system execute code?**
A: Yes, via the run_command tool, but this is done safely in containers where possible.

## Support and Feedback

For technical issues:
1. Check the logs in the `logs/` directory
2. Restart the program
3. Verify your API key and internet connection

The SingleAgent system learns from your usage and becomes more effective the more you work with it. Start with simple tasks and gradually build up to more complex workflows.
