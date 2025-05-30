# Configuration

This document covers all configuration options for the SingleAgent system, including environment setup, agent behavior, tools, and performance tuning.

## Configuration Overview

SingleAgent uses multiple configuration methods:
- **Environment variables** for runtime settings
- **pyproject.toml** for project-specific configuration  
- **Command-line arguments** for session overrides
- **Runtime configuration** for dynamic adjustments

## Environment Variables

### Required Environment Variables

```bash
# OpenAI API Configuration
OPENAI_API_KEY="sk-your-api-key-here"

# Optional: Custom OpenAI endpoint
OPENAI_BASE_URL="https://api.openai.com/v1"
```

### Optional Environment Variables

```bash
# Agent Configuration
SINGLEAGENT_DEFAULT_AGENT="code"          # Default agent: "code" or "architect"
SINGLEAGENT_MODEL="gpt-4"                 # OpenAI model to use
SINGLEAGENT_MAX_TOKENS=8000               # Maximum context tokens

# Logging Configuration  
SINGLEAGENT_LOG_LEVEL="INFO"              # Log level: DEBUG, INFO, WARN, ERROR
SINGLEAGENT_LOG_FILE="singleagent.log"    # Log file path

# Performance Configuration
SINGLEAGENT_CACHE_DIR="~/.singleagent/cache"  # Cache directory
SINGLEAGENT_TIMEOUT=30                    # Tool execution timeout (seconds)
SINGLEAGENT_MAX_RETRIES=3                 # Maximum retry attempts

# Development Configuration
SINGLEAGENT_DEBUG=false                   # Enable debug mode
SINGLEAGENT_PROFILE=false                 # Enable performance profiling
```

## pyproject.toml Configuration

### Basic Configuration

```toml
[tool.singleagent]
# Project information
name = "my-project"
description = "Project description"
version = "1.0.0"

# Default settings
default_agent = "code"
model = "gpt-4"
max_tokens = 8000

# Working directory
project_root = "."
source_dirs = ["src", "lib"]
test_dirs = ["tests", "test"]
docs_dirs = ["docs", "documentation"]
```

### Agent Configuration

```toml
[tool.singleagent.agents]

[tool.singleagent.agents.code]
# Code Agent specific settings
enabled = true
tools = ["ruff", "pylint", "pyright", "file_ops", "patch"]
auto_format = true
auto_lint = true
strict_type_checking = false

[tool.singleagent.agents.architect]
# Architect Agent specific settings
enabled = true
tools = ["ast_analysis", "project_structure", "design_patterns", "todo_generation"]
deep_analysis = true
pattern_detection = true
generate_todos = true
```

### Tool Configuration

```toml
[tool.singleagent.tools]

# Code Quality Tools
[tool.singleagent.tools.ruff]
enabled = true
config_file = "pyproject.toml"
auto_fix = true
ignore_errors = ["E501"]  # Line too long
select_rules = ["E", "W", "F"]

[tool.singleagent.tools.pylint]
enabled = true
config_file = ".pylintrc"
score_threshold = 8.0
disable_warnings = ["missing-docstring"]

[tool.singleagent.tools.pyright]
enabled = true
config_file = "pyrightconfig.json"
strict_mode = false
type_checking_mode = "basic"

# File Operations
[tool.singleagent.tools.file_ops]
enabled = true
backup_enabled = true
backup_dir = ".backups"
max_file_size = "10MB"
allowed_extensions = [".py", ".txt", ".md", ".json", ".yaml", ".toml"]

# Patch Management
[tool.singleagent.tools.patch]
enabled = true
auto_backup = true
dry_run_first = true
max_patch_size = "1MB"

# Analysis Tools
[tool.singleagent.tools.ast_analysis]
enabled = true
cache_results = true
deep_analysis = true
track_dependencies = true

[tool.singleagent.tools.project_structure]
enabled = true
ignore_dirs = [".git", "__pycache__", "node_modules", ".venv"]
max_depth = 10
analyze_config_files = true

[tool.singleagent.tools.design_patterns]
enabled = true
custom_patterns = []
confidence_threshold = 0.7
```

### Context Management

```toml
[tool.singleagent.context]
# Token Management
max_context_tokens = 8000
context_window_buffer = 500
priority_threshold = 0.5
summarization_ratio = 0.3

# Entity Tracking
track_all_variables = false
track_local_variables = false
deep_dependency_analysis = true
max_entity_depth = 5
entity_cache_size = 1000

# Conversation Management
max_conversation_history = 100
conversation_summary_threshold = 50
auto_summarize = true

# Memory Management
session_cache_size = 1000
file_cache_size = 500
persistent_cache = true
cache_ttl = 3600  # 1 hour
```

### Performance Tuning

```toml
[tool.singleagent.performance]
# Concurrency
max_concurrent_tools = 3
tool_timeout = 30
enable_parallel_analysis = true

# Caching
enable_caching = true
cache_directory = "~/.singleagent/cache"
cache_compression = true
cache_max_size = "100MB"

# Background Processing
enable_background_tasks = true
background_analysis = true
preemptive_caching = false

# Resource Limits
max_memory_usage = "500MB"
max_cpu_percentage = 80
disk_space_threshold = "1GB"
```

### Logging Configuration

```toml
[tool.singleagent.logging]
# Basic Logging
level = "INFO"
file = "singleagent.log"
max_file_size = "10MB"
backup_count = 5

# Advanced Logging
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"

# Component Logging
[tool.singleagent.logging.components]
agents = "INFO"
tools = "DEBUG"
context = "INFO"
performance = "WARN"

# Log Filtering
[tool.singleagent.logging.filters]
exclude_modules = ["urllib3", "requests"]
sensitive_data_masking = true
```

## Command-Line Configuration

### Global Options

```bash
# Model and API configuration
python -m singleagent --model gpt-4-turbo --max-tokens 16000

# Agent selection
python -m singleagent --agent architect

# Logging configuration
python -m singleagent --log-level DEBUG --log-file debug.log

# Performance options
python -m singleagent --timeout 60 --max-retries 5
```

### Tool-Specific Options

```bash
# Code quality tools
python -m singleagent --enable-ruff --disable-pylint --strict-typing

# Analysis tools
python -m singleagent --deep-analysis --pattern-detection

# File operations
python -m singleagent --backup-files --max-file-size 50MB
```

## Runtime Configuration

### Dynamic Configuration Updates

Configuration can be updated during runtime:

```python
# Update agent settings
!config set agents.code.auto_format true
!config set context.max_tokens 12000

# Update tool settings  
!config set tools.ruff.auto_fix false
!config set tools.pylint.score_threshold 9.0

# View current configuration
!config show
!config show agents.code
!config show tools.ruff
```

### Session-Specific Overrides

```python
# Temporary overrides for current session
!set max_tokens 16000
!set agent architect
!set debug_mode true

# Reset to defaults
!reset config
```

## Configuration Profiles

### Development Profile

```toml
[tool.singleagent.profiles.development]
extends = "default"

# More verbose logging
logging.level = "DEBUG"
logging.components.tools = "DEBUG"

# Aggressive analysis
tools.ast_analysis.deep_analysis = true
tools.design_patterns.confidence_threshold = 0.5

# Performance settings for development
performance.enable_background_tasks = false
performance.preemptive_caching = false
```

### Production Profile

```toml
[tool.singleagent.profiles.production]
extends = "default"

# Minimal logging
logging.level = "WARN"
logging.file = "/var/log/singleagent.log"

# Conservative analysis
tools.ast_analysis.deep_analysis = false
tools.design_patterns.confidence_threshold = 0.8

# Performance optimization
performance.enable_caching = true
performance.cache_compression = true
performance.max_concurrent_tools = 5
```

### CI/CD Profile

```toml
[tool.singleagent.profiles.ci]
extends = "production"

# Non-interactive mode
interactive = false
auto_confirm = true

# Focus on code quality
agents.code.auto_format = true
agents.code.auto_lint = true
agents.code.strict_type_checking = true

# Faster execution
performance.tool_timeout = 15
context.max_context_tokens = 4000
```

## Configuration Validation

### Schema Validation

The system validates configuration against a schema:

```python
# Validate current configuration
!config validate

# Check specific section
!config validate tools.ruff

# Show validation errors
!config validate --verbose
```

### Configuration Testing

```bash
# Test configuration with dry run
python -m singleagent --config-test --dry-run

# Validate tool configuration
python -m singleagent --validate-tools

# Check performance settings
python -m singleagent --benchmark-config
```

## Advanced Configuration

### Custom Tool Configuration

```toml
[tool.singleagent.custom_tools]

[tool.singleagent.custom_tools.my_linter]
command = "my-custom-linter {file_path}"
enabled = true
timeout = 30
output_format = "json"
error_patterns = ["ERROR:", "CRITICAL:"]
```

### Plugin Configuration

```toml
[tool.singleagent.plugins]
enabled = ["custom_analyzer", "project_templates"]

[tool.singleagent.plugins.custom_analyzer]
module = "my_plugins.analyzer"
config = {threshold = 0.8, mode = "strict"}

[tool.singleagent.plugins.project_templates]
module = "my_plugins.templates"
templates_dir = "~/.singleagent/templates"
```

### Integration Configuration

```toml
[tool.singleagent.integrations]

# Version Control
[tool.singleagent.integrations.git]
enabled = true
auto_stage = false
commit_message_template = "SingleAgent: {summary}"

# IDE Integration
[tool.singleagent.integrations.vscode]
enabled = true
extension_id = "singleagent.vscode"
auto_format_on_save = true

# CI/CD Integration
[tool.singleagent.integrations.github_actions]
enabled = true
workflow_file = ".github/workflows/singleagent.yml"
```

## Configuration Best Practices

### Security

1. **Environment Variables**: Store sensitive data in environment variables
2. **File Permissions**: Secure configuration files (600 permissions)
3. **API Keys**: Use key rotation and access controls
4. **Logging**: Avoid logging sensitive information

### Performance

1. **Caching**: Enable caching for better performance
2. **Resource Limits**: Set appropriate limits for your environment
3. **Background Tasks**: Use background processing for non-critical tasks
4. **Tool Selection**: Enable only necessary tools

### Maintenance

1. **Profile Usage**: Use configuration profiles for different environments
2. **Regular Updates**: Keep configuration in sync with system updates
3. **Documentation**: Document custom configuration changes
4. **Validation**: Regularly validate configuration integrity

### Example Complete Configuration

```toml
[tool.singleagent]
name = "my-awesome-project"
default_agent = "code"
model = "gpt-4"
max_tokens = 8000

[tool.singleagent.agents.code]
enabled = true
tools = ["ruff", "pylint", "pyright"]
auto_format = true

[tool.singleagent.tools.ruff]
enabled = true
auto_fix = true
config_file = "pyproject.toml"

[tool.singleagent.context]
max_context_tokens = 8000
track_all_variables = false
deep_dependency_analysis = true

[tool.singleagent.performance]
max_concurrent_tools = 3
enable_caching = true
cache_directory = "~/.singleagent/cache"

[tool.singleagent.logging]
level = "INFO"
file = "singleagent.log"
```

This configuration system provides flexible and comprehensive control about all aspects or the SingleAgent system while maintaining sensible defaults for common use cases.
