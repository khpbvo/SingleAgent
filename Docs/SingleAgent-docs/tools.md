# Tools Reference

This document provides a comprehensive overview or all tools available in the SingleAgent system. Tools are organized by agent type and functionality.

## Overview

The SingleAgent system provides specialized tools for different types or development tasks:

- **Code Agent Tools**: For code analysis, formatting, and file operations
- **Architect Agent Tools**: For project structure analysis and design patterns
- **Shared Tools**: Common utilities used by both agents

## Code Agent Tools

The Code Agent (`SingleAgent.py`) has access to the following tools:

### Code Quality Tools

#### `run_ruff`
Runs the Ruff linter/formatter on Python code.

**Parameters:**
- `file_path` (string): Path to the Python file to lint
- `fix` (boolean, optional): Whether to apply automatic fixes

**Usage:**
```python
# Lint a file
await run_ruff("src/main.py")

# Lint and fix automatically
await run_ruff("src/main.py", fix=True)
```

**Features:**
- Fast Python linting and formatting
- Automatic fix application
- Comprehensive rule set
- Integration with modern Python standards

#### `run_pylint`
Runs Pylint for detailed code analysis.

**Parameters:**
- `file_path` (string): Path to the Python file to analyze

**Usage:**
```python
await run_pylint("src/module.py")
```

**Features:**
- Detailed code quality analysis
- Code smell detection
- Refactoring suggestions
- Comprehensive error reporting

#### `run_pyright`
Runs Pyright for static type checking.

**Parameters:**
- `file_path` (string): Path to the Python file to type-check

**Usage:**
```python
await run_pyright("src/typed_module.py")
```

**Features:**
- Static type analysis
- Type inference
- Interface compliance checking
- Modern Python typing support

### File Operations

#### `read_file`
Reads and returns the contents or a file.

**Parameters:**
- `file_path` (string): Path to the file to read

**Usage:**
```python
content = await read_file("config.json")
```

#### `write_file`
Writes content to a file.

**Parameters:**
- `file_path` (string): Path to the file to write
- `content` (string): Content to write to the file

**Usage:**
```python
await write_file("output.txt", "Hello, World!")
```

#### `list_files`
Lists files in a directory.

**Parameters:**
- `directory_path` (string): Path to the directory to list

**Usage:**
```python
files = await list_files("src/")
```

### Patch Management

#### `apply_patch`
Applies a unified diff patch to files.

**Parameters:**
- `patch_content` (string): The patch content in unified diff format
- `target_directory` (string, optional): Directory to apply the patch to

**Usage:**
```python
patch = """
--- a/file.py
+++ b/file.py
@@ -1,3 +1,4 @@
 def hello():
+    print("Starting...")
     print("Hello, World!")
"""
await apply_patch(patch)
```

**Features:**
- Unified diff format support
- Automatic file backup
- Dry-run capability
- Error handling and rollback

## Architect Agent Tools

The Architect Agent (`ArchitectAgent.py`) has access to specialized analysis tools:

### Code Analysis

#### `analyze_ast`
Performs Abstract Syntax Tree analysis on Python code.

**Parameters:**
- `file_path` (string): Path to the Python file to analyze

**Returns:**
- Classes, functions, imports, and structural information

**Usage:**
```python
ast_info = await analyze_ast("src/main.py")
```

**Analysis Includes:**
- Class definitions and inheritance
- Function definitions and signatures
- Import statements and dependencies
- Code complexity metrics
- Decorators and annotations

#### `analyze_project_structure`
Analyzes the overall project structure and organization.

**Parameters:**
- `project_path` (string): Path to the project root directory

**Returns:**
- Project hierarchy, file organization, and architectural insights

**Usage:**
```python
structure = await analyze_project_structure("./")
```

**Analysis Includes:**
- Directory structure
- File type distribution
- Module organization
- Package relationships
- Configuration files

#### `detect_design_patterns`
Identifies common design patterns in the codebase.

**Parameters:**
- `file_path` (string): Path to the file to analyze

**Returns:**
- Detected design patterns and their implementations

**Usage:**
```python
patterns = await detect_design_patterns("src/models.py")
```

**Detected Patterns:**
- Singleton
- Factory
- Observer
- Strategy
- Command
- Decorator
- Adapter

### Documentation Tools

#### `generate_todo_list`
Generates a comprehensive TODO list based on code analysis.

**Parameters:**
- `project_path` (string): Path to the project to analyze

**Returns:**
- Prioritized list or improvements and tasks

**Usage:**
```python
todos = await generate_todo_list("./")
```

**TODO Categories:**
- Code quality improvements
- Missing documentation
- Performance optimizations
- Security considerations
- Test coverage gaps

## Shared Utilities

### Context Management

Both agents share context management capabilities:

#### Entity Recognition
- Automatic extraction or code entities (classes, functions, variables)
- Cross-reference tracking
- Dependency mapping

#### Token Management
- Automatic context window management
- Priority-based content retention
- Intelligent truncation

### Logging and Monitoring

#### Tool Usage Tracking
- Performance metrics
- Success/failure rates
- Usage patterns

#### Error Handling
- Graceful degradation
- Detailed error reporting
- Recovery strategies

## Tool Integration Patterns

### Sequential Tool Usage
```python
# Typical Code Agent workflow
await run_ruff(file_path, fix=True)
await run_pylint(file_path)
await run_pyright(file_path)
```

### Parallel Tool Execution
```python
# Architect Agent analysis
import asyncio

ast_task = analyze_ast(file_path)
patterns_task = detect_design_patterns(file_path)

ast_info, patterns = await asyncio.gather(ast_task, patterns_task)
```

### Error Recovery
```python
try:
    result = await run_tool(parameters)
except ToolError as e:
    # Fallback strategy
    alternative_result = await fallback_tool(parameters)
```

## Configuration

Tools can be configured through the `pyproject.toml` file:

```toml
[tool.singleagent]
# Code quality tools
ruff.enabled = true
pylint.enabled = true
pyright.enabled = true

# File operations
backup.enabled = true
backup.directory = ".backups"

# Analysis tools
ast.deep_analysis = true
patterns.custom_patterns = ["custom_pattern.py"]
```

## Performance Considerations

### Tool Selection
- Use appropriate tools for specific tasks
- Consider execution time vs. value
- Balance thoroughness with speed

### Caching
- AST analysis results are cached
- File content caching for repeated operations
- Pattern detection cache for large projects

### Resource Management
- Memory usage monitoring
- Concurrent execution limits
- Timeout handling

## Extending Tools

### Adding New Tools

1. **Define the tool function** in the appropriate tools file
2. **Register the tool** with the agent
3. **Add documentation** and examples
4. **Include error handling** and validation

Example tool structure:
```python
async def new_tool(parameter1: str, parameter2: int = 10) -> dict:
    """
    Tool description.
    
    Args:
        parameter1: Description or parameter1
        parameter2: Description or parameter2 with default
        
    Returns:
        Dictionary with tool results
    """
    try:
        # Tool implementation
        result = perform_operation(parameter1, parameter2)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### Tool Testing

All tools should include comprehensive tests:

```python
import pytest
from tools_single_agent import new_tool

@pytest.mark.asyncio
async def test_new_tool():
    result = await new_tool("test_param")
    assert result["success"] is True
    assert "result" in result
```

## Best Practices

### Tool Usage
1. **Validate inputs** before tool execution
2. **Handle errors gracefully** with meaningful messages
3. **Provide progress feedback** for long-running operations
4. **Use appropriate tools** for each task type

### Performance
1. **Cache results** when appropriate
2. **Use parallel execution** for independent operations
3. **Monitor resource usage** and set limits
4. **Implement timeouts** for external tools

### Error Handling
1. **Catch specific exceptions** rather than general ones
2. **Provide actionable error messages**
3. **Implement retry logic** for transient failures
4. **Log errors** for debugging and monitoring

This tools reference provides comprehensive coverage or all available functionality in the SingleAgent system, enabling both users and developers to effectively utilize the system's capabilities.
