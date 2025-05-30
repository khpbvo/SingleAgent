# Tools Reference

SingleAgent provides a comprehensive set of tools for both the Code Agent and Architect Agent. These tools enable file operations, code analysis, system interaction, and much more.

## Overview

The tools system is designed to provide agents with capabilities to:

- **File Operations**: Create, read, modify, and analyze files
- **Code Analysis**: Understand and manipulate code structures
- **System Interaction**: Execute commands and manage processes
- **Project Management**: Handle project structure and dependencies
- **Documentation**: Generate and maintain documentation

## Tool Categories

### File System Tools

#### `file_creator`
Creates new files with specified content.

**Parameters:**
- `filepath` (string): Path where the file should be created
- `content` (string): Initial content for the file
- `overwrite` (boolean): Whether to overwrite existing files

**Example:**
```python
file_creator.create_file(
    filepath="src/models/user.py",
    content="class User:\n    def __init__(self, name):\n        self.name = name",
    overwrite=False
)
```

#### `file_reader`
Reads and returns file contents.

**Parameters:**
- `filepath` (string): Path to the file to read
- `encoding` (string): File encoding (default: utf-8)
- `lines` (tuple): Optional line range (start, end)

**Example:**
```python
content = file_reader.read_file("src/main.py")
partial_content = file_reader.read_file("src/main.py", lines=(1, 50))
```

#### `file_modifier`
Modifies existing files with various operations.

**Parameters:**
- `filepath` (string): Path to the file to modify
- `operation` (string): Type of modification (replace, insert, append)
- `content` (string): New content
- `line_number` (int): Target line for insertion
- `search_pattern` (string): Pattern to search and replace

**Example:**
```python
file_modifier.modify_file(
    filepath="src/config.py",
    operation="replace",
    search_pattern="DEBUG = False",
    content="DEBUG = True"
)
```

#### `directory_manager`
Manages directory operations.

**Parameters:**
- `operation` (string): create, list, delete
- `path` (string): Directory path
- `recursive` (boolean): Recursive operation

**Example:**
```python
directory_manager.create_directory("src/models", recursive=True)
files = directory_manager.list_directory("src")
```

### Code Analysis Tools

#### `code_analyzer`
Analyzes code structure and provides insights.

**Parameters:**
- `filepath` (string): Path to code file
- `analysis_type` (string): Type of analysis (structure, complexity, dependencies)
- `language` (string): Programming language

**Example:**
```python
analysis = code_analyzer.analyze_file(
    filepath="src/main.py",
    analysis_type="structure",
    language="python"
)
```

**Returns:**
```python
{
    "classes": ["User", "Database"],
    "functions": ["main", "setup_logging"],
    "imports": ["os", "sys", "logging"],
    "complexity": "medium",
    "lines_of_code": 150
}
```

#### `syntax_checker`
Validates code syntax and identifies errors.

**Parameters:**
- `filepath` (string): Path to code file
- `language` (string): Programming language
- `strict_mode` (boolean): Enable strict checking

**Example:**
```python
result = syntax_checker.check_syntax("src/main.py", language="python")
```

#### `dependency_analyzer`
Analyzes project dependencies and imports.

**Parameters:**
- `project_path` (string): Path to project root
- `language` (string): Programming language
- `include_dev` (boolean): Include development dependencies

**Example:**
```python
deps = dependency_analyzer.analyze_dependencies(
    project_path=".",
    language="python",
    include_dev=True
)
```

### System Interaction Tools

#### `command_executor`
Executes system commands and returns output.

**Parameters:**
- `command` (string): Command to execute
- `working_directory` (string): Working directory for command
- `timeout` (int): Command timeout in seconds
- `capture_output` (boolean): Whether to capture command output

**Example:**
```python
result = command_executor.execute(
    command="pip install requests",
    working_directory=".",
    timeout=30,
    capture_output=True
)
```

#### `process_manager`
Manages long-running processes.

**Parameters:**
- `command` (string): Command to run
- `background` (boolean): Run in background
- `process_id` (string): Unique process identifier

**Example:**
```python
process_manager.start_process(
    command="python server.py",
    background=True,
    process_id="web_server"
)
```

#### `environment_manager`
Manages environment variables and configuration.

**Parameters:**
- `operation` (string): get, set, list, delete
- `variable_name` (string): Environment variable name
- `value` (string): Variable value

**Example:**
```python
environment_manager.set_variable("API_KEY", "your-api-key-here")
api_key = environment_manager.get_variable("API_KEY")
```

### Project Management Tools

#### `project_initializer`
Initializes new projects with templates.

**Parameters:**
- `project_name` (string): Name of the project
- `template` (string): Project template type
- `language` (string): Programming language
- `include_tests` (boolean): Include test structure

**Example:**
```python
project_initializer.create_project(
    project_name="my_web_app",
    template="flask",
    language="python",
    include_tests=True
)
```

#### `package_manager`
Manages project packages and dependencies.

**Parameters:**
- `operation` (string): install, uninstall, update, list
- `package_name` (string): Package name
- `version` (string): Specific version
- `dev_dependency` (boolean): Development dependency

**Example:**
```python
package_manager.install_package(
    package_name="requests",
    version="2.28.0",
    dev_dependency=False
)
```

#### `git_manager`
Handles Git operations.

**Parameters:**
- `operation` (string): init, add, commit, push, pull, status
- `message` (string): Commit message
- `files` (list): Files to add/commit
- `remote` (string): Remote repository

**Example:**
```python
git_manager.commit_changes(
    message="Add user authentication feature",
    files=["src/auth.py", "tests/test_auth.py"]
)
```

### Testing Tools

#### `test_runner`
Runs tests and provides results.

**Parameters:**
- `test_path` (string): Path to tests
- `test_framework` (string): Testing framework (pytest, unittest)
- `verbose` (boolean): Verbose output
- `coverage` (boolean): Generate coverage report

**Example:**
```python
results = test_runner.run_tests(
    test_path="tests/",
    test_framework="pytest",
    verbose=True,
    coverage=True
)
```

#### `test_generator`
Generates test cases for code.

**Parameters:**
- `source_file` (string): Source file to test
- `test_type` (string): Type of tests (unit, integration)
- `framework` (string): Testing framework

**Example:**
```python
test_generator.generate_tests(
    source_file="src/user.py",
    test_type="unit",
    framework="pytest"
)
```

### Documentation Tools

#### `doc_generator`
Generates documentation from code.

**Parameters:**
- `source_path` (string): Path to source code
- `output_format` (string): Documentation format (markdown, html)
- `include_private` (boolean): Include private methods
- `template` (string): Documentation template

**Example:**
```python
doc_generator.generate_docs(
    source_path="src/",
    output_format="markdown",
    include_private=False,
    template="default"
)
```

#### `readme_generator`
Creates README files for projects.

**Parameters:**
- `project_path` (string): Path to project
- `template` (string): README template
- `include_badges` (boolean): Include status badges
- `sections` (list): Sections to include

**Example:**
```python
readme_generator.create_readme(
    project_path=".",
    template="standard",
    include_badges=True,
    sections=["installation", "usage", "contributing"]
)
```

### Web and API Tools

#### `api_client`
Makes HTTP requests to APIs.

**Parameters:**
- `url` (string): API endpoint URL
- `method` (string): HTTP method (GET, POST, PUT, DELETE)
- `headers` (dict): Request headers
- `data` (dict): Request data
- `timeout` (int): Request timeout

**Example:**
```python
response = api_client.request(
    url="https://api.example.com/users",
    method="GET",
    headers={"Authorization": "Bearer token"},
    timeout=10
)
```

#### `web_scraper`
Scrapes content from web pages.

**Parameters:**
- `url` (string): URL to scrape
- `selector` (string): CSS selector for content
- `wait_time` (int): Wait time for dynamic content
- `headers` (dict): Request headers

**Example:**
```python
content = web_scraper.scrape_content(
    url="https://example.com",
    selector=".main-content",
    wait_time=3
)
```

### Database Tools

#### `database_manager`
Manages database connections and operations.

**Parameters:**
- `database_type` (string): Database type (sqlite, postgresql, mysql)
- `connection_string` (string): Database connection string
- `operation` (string): Database operation
- `query` (string): SQL query
- `parameters` (dict): Query parameters

**Example:**
```python
database_manager.execute_query(
    database_type="sqlite",
    connection_string="database.db",
    operation="select",
    query="SELECT * FROM users WHERE age > ?",
    parameters={"age": 18}
)
```

#### `migration_manager`
Handles database migrations.

**Parameters:**
- `migration_path` (string): Path to migration files
- `operation` (string): up, down, status
- `target_version` (string): Target migration version

**Example:**
```python
migration_manager.run_migration(
    migration_path="migrations/",
    operation="up",
    target_version="latest"
)
```

## Tool Configuration

### Environment Setup

Configure tools through environment variables:

```bash
# File system tools
WORKSPACE_PATH=/path/to/workspace
MAX_FILE_SIZE=10MB

# Code analysis tools
DEFAULT_LANGUAGE=python
SYNTAX_CHECK_STRICT=true

# System tools
COMMAND_TIMEOUT=30
MAX_PROCESSES=5

# API tools
DEFAULT_TIMEOUT=10
MAX_RETRIES=3
```

### Tool Permissions

Configure tool permissions for security:

```python
TOOL_PERMISSIONS = {
    "file_creator": {
        "allowed_extensions": [".py", ".js", ".md", ".txt"],
        "forbidden_paths": ["/etc", "/usr", "/var"],
        "max_file_size": "10MB"
    },
    "command_executor": {
        "allowed_commands": ["pip", "npm", "git", "python"],
        "forbidden_commands": ["rm -rf", "sudo", "chmod"],
        "timeout_limit": 300
    }
}
```

### Tool Logging

Enable logging for tool operations:

```python
TOOL_LOGGING = {
    "enabled": True,
    "level": "INFO",
    "log_file": "tools.log",
    "include_parameters": False,  # Exclude sensitive parameters
    "max_log_size": "100MB"
}
```

## Custom Tools

### Creating Custom Tools

Extend the tools system with custom tools:

```python
from tools.base import BaseTool

class CustomTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.name = "custom_tool"
        self.description = "A custom tool for specific tasks"
    
    def execute(self, **kwargs):
        """
        Execute the custom tool functionality
        """
        # Implementation here
        return {"status": "success", "result": "Custom tool executed"}
    
    def validate_parameters(self, **kwargs):
        """
        Validate tool parameters
        """
        required_params = ["param1", "param2"]
        for param in required_params:
            if param not in kwargs:
                raise ValueError(f"Missing required parameter: {param}")
```

### Registering Custom Tools

Register custom tools with the system:

```python
from tools.registry import ToolRegistry

# Register the custom tool
registry = ToolRegistry()
registry.register_tool("custom_tool", CustomTool())

# Use the custom tool
result = registry.execute_tool("custom_tool", param1="value1", param2="value2")
```

## Error Handling

### Common Error Types

Tools may raise various exceptions:

```python
from tools.exceptions import (
    ToolExecutionError,
    InvalidParameterError,
    PermissionDeniedError,
    TimeoutError
)

try:
    result = file_creator.create_file("protected/file.py", "content")
except PermissionDeniedError:
    print("Cannot create file in protected directory")
except ToolExecutionError as e:
    print(f"Tool execution failed: {e}")
```

### Retry Logic

Implement retry logic for failing tools:

```python
import time
from tools.exceptions import ToolExecutionError

def execute_with_retry(tool, max_retries=3, delay=1, **kwargs):
    for attempt in range(max_retries):
        try:
            return tool.execute(**kwargs)
        except ToolExecutionError:
            if attempt == max_retries - 1:
                raise
            time.sleep(delay * (2 ** attempt))  # Exponential backoff
```

## Performance Optimization

### Tool Caching

Cache tool results to improve performance:

```python
from functools import lru_cache

class CachedCodeAnalyzer:
    @lru_cache(maxsize=100)
    def analyze_file(self, filepath, analysis_type):
        # Expensive analysis operation
        return self._perform_analysis(filepath, analysis_type)
```

### Batch Operations

Perform batch operations when possible:

```python
# Instead of multiple individual operations
files = ["file1.py", "file2.py", "file3.py"]
for file in files:
    syntax_checker.check_syntax(file)

# Use batch operation
syntax_checker.check_syntax_batch(files)
```

### Async Tool Execution

Use async tools for concurrent operations:

```python
import asyncio

async def parallel_file_operations():
    tasks = [
        file_creator.create_file_async("file1.py", "content1"),
        file_creator.create_file_async("file2.py", "content2"),
        file_creator.create_file_async("file3.py", "content3")
    ]
    results = await asyncio.gather(*tasks)
    return results
```

## Best Practices

### Tool Selection

1. **Use Appropriate Tools**: Select the most suitable tool for each task
2. **Combine Tools**: Use multiple tools together for complex operations
3. **Validate Inputs**: Always validate tool parameters before execution
4. **Handle Errors**: Implement proper error handling and recovery

### Security Considerations

1. **Parameter Validation**: Validate all tool parameters
2. **Path Traversal**: Prevent directory traversal attacks
3. **Command Injection**: Sanitize command inputs
4. **File Permissions**: Respect file system permissions

### Performance Tips

1. **Cache Results**: Cache expensive operations
2. **Batch Operations**: Use batch operations when available
3. **Async Execution**: Use async tools for I/O operations
4. **Resource Limits**: Set appropriate resource limits

## Integration Examples

### Code Agent Tool Usage

```python
# Code Agent using multiple tools
def implement_feature(feature_description):
    # Analyze existing code
    analysis = code_analyzer.analyze_project(".")
    
    # Generate new code files
    files = file_creator.create_files_from_template(
        template="feature",
        feature_name=feature_description
    )
    
    # Run tests
    test_results = test_runner.run_tests("tests/")
    
    # Generate documentation
    doc_generator.update_docs(files)
    
    return {
        "files_created": files,
        "test_results": test_results,
        "documentation_updated": True
    }
```

### Architect Agent Tool Usage

```python
# Architect Agent using tools for system design
def design_system_architecture(requirements):
    # Analyze current project structure
    structure = directory_manager.analyze_structure(".")
    
    # Generate architecture documentation
    architecture_doc = doc_generator.create_architecture_doc(
        requirements=requirements,
        current_structure=structure
    )
    
    # Create project template
    project_initializer.create_structure_from_design(
        architecture_doc=architecture_doc
    )
    
    return architecture_doc
```

---

*For more information, see [Code Agent](code-agent.md) and [Architect Agent](architect-agent.md).*
