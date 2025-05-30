# Code Agent Documentation

The Code Agent (SingleAgent) is specialized for code analysis, implementation, debugging, and file operations. This agent focuses on concrete, actionable development tasks.

## Overview

The Code Agent is designed to be your primary programming companion, handling everything from analyzing existing code to implementing new features. It excels at:

- **Code Analysis**: Understanding and explaining code structure and functionality
- **Implementation**: Writing new code and features
- **Debugging**: Identifying and fixing issues
- **File Operations**: Managing project files and directories
- **Testing**: Creating and running tests
- **Refactoring**: Improving code quality and structure

## Core Capabilities

### 1. Code Analysis and Understanding

The Code Agent can analyze your codebase and provide insights:

```
SingleAgent> Analyze the main.py file structure
SingleAgent> Explain how the context management works
SingleAgent> What are the dependencies in this project?
```

**Features:**
- **Syntax Analysis**: Understands code syntax and structure
- **Dependency Mapping**: Identifies relationships between files and modules
- **Pattern Recognition**: Recognizes design patterns and architectural styles
- **Code Quality Assessment**: Evaluates code quality and suggests improvements

### 2. File Operations

Comprehensive file management capabilities:

```
SingleAgent> Show me the contents of config.py
SingleAgent> Create a new utility function in utils.py
SingleAgent> Move the old tests to a backup directory
```

**Available Operations:**
- **Read Files**: Display and analyze file contents
- **Write Files**: Create new files or modify existing ones
- **Directory Operations**: List, create, and manage directories
- **File Search**: Find files by name, content, or pattern
- **Backup and Recovery**: Safely manage file versions

### 3. Code Implementation

The Code Agent can write and implement code:

```
SingleAgent> Implement a function to parse configuration files
SingleAgent> Add error handling to the database connection
SingleAgent> Create a test suite for the user authentication module
```

**Implementation Capabilities:**
- **Function Creation**: Write new functions and methods
- **Class Implementation**: Create and modify classes
- **Module Development**: Build complete modules
- **API Integration**: Implement API calls and integrations
- **Database Operations**: Create database queries and operations

### 4. Debugging and Problem Solving

Expert debugging assistance:

```
SingleAgent> This function is returning None, help me debug it
SingleAgent> Why is my API call failing?
SingleAgent> Find the source of this memory leak
```

**Debugging Features:**
- **Error Analysis**: Interpret error messages and stack traces
- **Logic Debugging**: Identify logical errors in code flow
- **Performance Analysis**: Find performance bottlenecks
- **Testing Assistance**: Create test cases to isolate issues

## Available Tools

The Code Agent has access to a comprehensive set of tools:

### File System Tools

| Tool | Purpose | Example Usage |
|------|---------|---------------|
| `read_file` | Read file contents | Examining source code |
| `write_file` | Create/modify files | Implementing new features |
| `list_directory` | List directory contents | Exploring project structure |
| `create_directory` | Create new directories | Organizing project layout |
| `delete_file` | Remove files safely | Cleaning up old files |
| `move_file` | Move/rename files | Restructuring projects |

### Code Analysis Tools

| Tool | Purpose | Example Usage |
|------|---------|---------------|
| `analyze_syntax` | Check syntax validity | Code review and validation |
| `find_functions` | Locate function definitions | Code navigation |
| `trace_dependencies` | Map module dependencies | Architecture analysis |
| `check_imports` | Validate import statements | Dependency management |
| `measure_complexity` | Assess code complexity | Quality assessment |

### Search and Navigation Tools

| Tool | Purpose | Example Usage |
|------|---------|---------------|
| `search_code` | Search for code patterns | Finding similar implementations |
| `grep_files` | Text search across files | Locating specific functionality |
| `find_references` | Find all references to symbols | Refactoring assistance |
| `locate_definition` | Find where symbols are defined | Code navigation |

### Execution and Testing Tools

| Tool | Purpose | Example Usage |
|------|---------|---------------|
| `run_code` | Execute Python code | Testing implementations |
| `run_tests` | Execute test suites | Validation and QA |
| `validate_syntax` | Check code syntax | Pre-commit validation |
| `profile_performance` | Measure execution performance | Optimization |

### Git and Version Control Tools

| Tool | Purpose | Example Usage |
|------|---------|---------------|
| `git_status` | Check repository status | Version control management |
| `git_diff` | Show file differences | Change review |
| `git_log` | View commit history | Project history analysis |
| `git_branch` | Manage branches | Feature development |

## Usage Patterns

### 1. Code Review and Analysis

**Typical Workflow:**
1. **Project Overview**: "Analyze the overall project structure"
2. **Specific Analysis**: "Explain how the authentication system works"
3. **Quality Assessment**: "Review this function for potential improvements"
4. **Documentation**: "Generate documentation for this module"

### 2. Feature Implementation

**Typical Workflow:**
1. **Requirements Analysis**: "I need to add user registration functionality"
2. **Planning**: "What files need to be modified for this feature?"
3. **Implementation**: "Implement the registration endpoint"
4. **Testing**: "Create tests for the new registration feature"
5. **Integration**: "Update the main application to use the new feature"

### 3. Debugging and Troubleshooting

**Typical Workflow:**
1. **Problem Description**: "The application crashes when uploading files"
2. **Error Analysis**: "Analyze this stack trace"
3. **Investigation**: "Check the file upload handling code"
4. **Solution**: "Fix the file validation logic"
5. **Verification**: "Test the fix with various file types"

### 4. Refactoring and Optimization

**Typical Workflow:**
1. **Assessment**: "Analyze code quality in the user module"
2. **Identification**: "Find areas that need refactoring"
3. **Planning**: "Plan the refactoring approach"
4. **Implementation**: "Refactor the user authentication logic"
5. **Testing**: "Ensure all tests still pass after refactoring"

## Best Practices

### 1. Providing Context

Always provide sufficient context for better assistance:

**Good:**
```
SingleAgent> I'm working on a Flask web application. The user login function 
in auth.py is not validating passwords correctly. Can you help me debug it?
```

**Less Effective:**
```
SingleAgent> Fix my login function
```

### 2. Incremental Approach

Break complex tasks into smaller steps:

**Good:**
```
SingleAgent> First, show me the current authentication system
SingleAgent> Now, help me add two-factor authentication
SingleAgent> Finally, update the tests for the new auth flow
```

### 3. Specify Requirements

Be clear about requirements and constraints:

**Good:**
```
SingleAgent> Create a function to validate email addresses. It should use regex,
handle international domains, and return both validity and error messages.
```

### 4. Request Explanations

Ask for explanations to learn and verify:

**Good:**
```
SingleAgent> Implement the feature and explain how it works
SingleAgent> Why did you choose this approach over alternatives?
```

## Working with Specific Technologies

### Python Projects

The Code Agent excels with Python projects:

```
SingleAgent> Analyze the Python package structure
SingleAgent> Add type hints to the user module
SingleAgent> Create a requirements.txt file
SingleAgent> Set up pytest configuration
```

### Web Development

Strong support for web development:

```
SingleAgent> Review the API endpoint security
SingleAgent> Add CORS handling to the Flask app
SingleAgent> Implement rate limiting middleware
SingleAgent> Create database migration scripts
```

### Data Science

Helpful for data science projects:

```
SingleAgent> Analyze this data processing pipeline
SingleAgent> Optimize the pandas operations
SingleAgent> Add data validation checks
SingleAgent> Create visualization functions
```

## Integration with Architect Agent

The Code Agent works seamlessly with the Architect Agent:

**Typical Collaboration:**
1. **Planning** (Architect): High-level system design
2. **Implementation** (Code): Detailed code implementation
3. **Review** (Both): Architecture and code review
4. **Optimization** (Code): Performance and quality improvements

**Switching Example:**
```
SingleAgent> Implement the user authentication system
SingleAgent> !architect
Architect> How does this authentication fit into the overall security architecture?
Architect> !code
SingleAgent> Update the implementation based on the architectural feedback
```

## Advanced Features

### 1. Context-Aware Assistance

The Code Agent maintains context about your project:

- **Project Understanding**: Remembers your project structure and technologies
- **Conversation History**: Builds on previous discussions
- **Entity Tracking**: Tracks important code entities and relationships
- **Pattern Recognition**: Learns your coding patterns and preferences

### 2. Intelligent Suggestions

Proactive suggestions based on context:

- **Best Practices**: Suggests improvements following best practices
- **Error Prevention**: Warns about potential issues
- **Optimization Opportunities**: Identifies performance improvements
- **Security Considerations**: Highlights security implications

### 3. Multi-file Operations

Handle complex operations across multiple files:

- **Refactoring**: Safe refactoring across multiple files
- **Feature Implementation**: Coordinate changes across the codebase
- **Testing**: Create comprehensive test suites
- **Documentation**: Generate and maintain documentation

## Limitations and Considerations

### 1. Code Execution Safety

- Always review generated code before execution
- Be cautious with file operations in production environments
- Test changes in development environments first
- Backup important files before major modifications

### 2. Technology Scope

While the Code Agent is knowledgeable about many technologies:
- Primary expertise is in Python and web technologies
- May need guidance for specialized or newer technologies
- Always verify suggestions against official documentation

### 3. Project Complexity

For very large or complex projects:
- Break down tasks into smaller components
- Provide additional context about project constraints
- Consider using the Architect Agent for high-level planning

## Getting Help

If you need assistance with the Code Agent:

1. **Type `!help`** for available commands
2. **Be specific** about your needs and context
3. **Ask for explanations** when you need to understand the reasoning
4. **Provide feedback** about the quality of assistance

The Code Agent is designed to be your intelligent coding partner, helping you write better code faster while learning and adapting to your specific needs and preferences.
