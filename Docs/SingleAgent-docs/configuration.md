# Configuration

This guide covers all configuration options and settings for the SingleAgent system.

## Table of Contents

- [Configuration Files](#configuration-files)
- [Environment Variables](#environment-variables)
- [Model Settings](#model-settings)
- [Agent Configuration](#agent-configuration)
- [Tool Configuration](#tool-configuration)
- [Logging Configuration](#logging-configuration)
- [Advanced Settings](#advanced-settings)

## Configuration Files

### pyproject.toml

The main project configuration is defined in `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "singleagent"
version = "0.1.0"
description = "A dual-agent system for code and architecture tasks"
dependencies = [
    "openai",
    "python-dotenv",
    "requests",
    "spacy",
    "networkx",
    "toml"
]
```

### requirements.txt

Runtime dependencies are listed in `requirements.txt`:

```
openai
python-dotenv
requests
spacy
networkx
toml
prompt-toolkit
tiktoken
```

## Environment Variables

Create a `.env` file in your project root with the following variables:

### Required Variables

```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Model Configuration
OPENAI_MODEL=gpt-4  # Default model for agents
ARCHITECT_MODEL=gpt-4  # Model for Architect Agent
CODE_MODEL=gpt-4  # Model for Code Agent
```

### Optional Variables

```bash
# API Configuration
OPENAI_BASE_URL=https://api.openai.com/v1  # Custom API endpoint
OPENAI_ORGANIZATION=your_org_id  # Organization ID

# Performance Settings
MAX_TOKENS=4096  # Maximum tokens per response
TEMPERATURE=0.1  # Model temperature (0.0-1.0)
TIMEOUT=30  # API request timeout in seconds

# Logging Configuration
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
LOG_FILE=logs/main.log  # Log file path

# Tool Configuration
ENABLE_WEB_SEARCH=true  # Enable web search tools
ENABLE_FILE_OPERATIONS=true  # Enable file operation tools
```

## Model Settings

### Model Configuration Class

The system uses a centralized model configuration system defined in `agents/model_settings.py`:

```python
class ModelSettings:
    def __init__(self):
        self.model = os.getenv("OPENAI_MODEL", "gpt-4")
        self.max_tokens = int(os.getenv("MAX_TOKENS", "4096"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.1"))
        self.timeout = int(os.getenv("TIMEOUT", "30"))
```

### Agent-Specific Models

You can configure different models for different agents:

```python
# Code Agent Configuration
code_settings = ModelSettings()
code_settings.model = "gpt-4"
code_settings.temperature = 0.1  # Lower temperature for precise code

# Architect Agent Configuration
architect_settings = ModelSettings()
architect_settings.model = "gpt-4"
architect_settings.temperature = 0.3  # Higher temperature for creativity
```

## Agent Configuration

### SingleAgent Configuration

The main SingleAgent class accepts various configuration options:

```python
from The_Agents.SingleAgent import SingleAgent

agent = SingleAgent(
    model="gpt-4",
    temperature=0.1,
    max_tokens=4096,
    timeout=30,
    enable_logging=True,
    log_level="INFO"
)
```

### ArchitectAgent Configuration

The ArchitectAgent has specialized configuration options:

```python
from The_Agents.ArchitectAgent import ArchitectAgent

architect = ArchitectAgent(
    model="gpt-4",
    temperature=0.3,
    max_design_iterations=5,
    enable_tools=True,
    tools_config={
        "web_search": True,
        "file_analysis": True,
        "diagram_generation": False
    }
)
```

### Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | str | "gpt-4" | OpenAI model to use |
| `temperature` | float | 0.1 | Response creativity (0.0-1.0) |
| `max_tokens` | int | 4096 | Maximum response length |
| `timeout` | int | 30 | API request timeout |
| `enable_logging` | bool | True | Enable detailed logging |
| `log_level` | str | "INFO" | Logging verbosity level |

## Tool Configuration

### Tool Registry

Tools are configured in the `Tools/` directory with specific settings:

```python
# tools_single_agent.py
TOOL_CONFIGS = {
    "file_operations": {
        "enabled": True,
        "max_file_size": "10MB",
        "allowed_extensions": [".py", ".md", ".txt", ".json"]
    },
    "web_search": {
        "enabled": True,
        "max_results": 10,
        "timeout": 15
    },
    "code_analysis": {
        "enabled": True,
        "max_complexity": 100,
        "include_metrics": True
    }
}
```

### Architect Tools Configuration

Specialized tools for the Architect Agent:

```python
# architect_tools.py
ARCHITECT_TOOL_CONFIGS = {
    "system_design": {
        "enabled": True,
        "max_components": 50,
        "include_patterns": True
    },
    "technology_research": {
        "enabled": True,
        "search_depth": "comprehensive",
        "include_comparisons": True
    }
}
```

### Tool Security Settings

```python
SECURITY_SETTINGS = {
    "sandbox_mode": True,  # Run tools in sandbox
    "allowed_paths": ["/workspace", "/project"],  # Restricted file access
    "blocked_commands": ["rm", "del", "format"],  # Dangerous commands
    "require_confirmation": True  # Ask before destructive operations
}
```

## Logging Configuration

### Log Levels

Configure logging verbosity:

- `DEBUG`: Detailed debugging information
- `INFO`: General operational messages
- `WARNING`: Warning messages for potential issues
- `ERROR`: Error messages for failures

### Log File Configuration

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/main.log'),
        logging.StreamHandler()  # Console output
    ]
)
```

### Agent-Specific Logging

Each agent can have its own log file:

```python
# Architect Agent logging
architect_logger = logging.getLogger('ArchitectAgent')
architect_handler = logging.FileHandler('logs/architectagent.log')
architect_logger.addHandler(architect_handler)

# Tool logging
tool_logger = logging.getLogger('ArchitectTools')
tool_handler = logging.FileHandler('logs/architect_tools.log')
tool_logger.addHandler(tool_handler)
```

## Advanced Settings

### Context Management

Configure how agents handle context:

```python
CONTEXT_SETTINGS = {
    "max_context_length": 8192,  # Maximum context tokens
    "context_window": 4096,  # Working context window
    "auto_summarize": True,  # Auto-summarize long contexts
    "preserve_entities": True,  # Keep important entities
    "compression_ratio": 0.3  # Context compression ratio
}
```

### Performance Settings

Optimize system performance:

```python
PERFORMANCE_SETTINGS = {
    "enable_caching": True,  # Cache API responses
    "cache_duration": 3600,  # Cache duration in seconds
    "parallel_requests": 3,  # Max parallel API calls
    "retry_attempts": 3,  # Failed request retries
    "backoff_factor": 2  # Exponential backoff multiplier
}
```

### Memory Management

Configure memory usage:

```python
MEMORY_SETTINGS = {
    "max_memory_mb": 1024,  # Maximum memory usage
    "gc_threshold": 0.8,  # Garbage collection threshold
    "context_cleanup": True,  # Auto-cleanup old contexts
    "tool_result_limit": 100  # Max stored tool results
}
```

## Configuration Validation

### Validating Settings

The system includes configuration validation:

```python
def validate_config():
    """Validate all configuration settings."""
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise ConfigurationError(f"Missing required variables: {missing_vars}")
    
    # Validate model settings
    if not isinstance(float(os.getenv("TEMPERATURE", "0.1")), float):
        raise ConfigurationError("TEMPERATURE must be a float")
    
    # Validate paths
    log_dir = os.path.dirname(os.getenv("LOG_FILE", "logs/main.log"))
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
```

### Configuration Testing

Test your configuration:

```python
from utilities.config_validator import validate_config

try:
    validate_config()
    print("✓ Configuration is valid")
except ConfigurationError as e:
    print(f"✗ Configuration error: {e}")
```

## Best Practices

### Security

1. **Never commit API keys** to version control
2. **Use environment variables** for sensitive data
3. **Restrict file access** with allowed paths
4. **Enable sandbox mode** for tool execution

### Performance

1. **Set appropriate timeouts** to prevent hanging
2. **Use caching** for repeated API calls
3. **Limit context length** to control costs
4. **Monitor memory usage** for long-running sessions

### Maintenance

1. **Regular log rotation** to prevent disk space issues
2. **Monitor API usage** and costs
3. **Update models** as new versions become available
4. **Test configuration** after changes

## Next Steps

- [Context Management](context-management.md) - Learn about context handling
- [Tools Documentation](tools.md) - Explore available tools
- [Troubleshooting](troubleshooting.md) - Solve common issues
- [Examples](examples.md) - See practical configurations

---

For more information, see the [main documentation](index.md) or [installation guide](installation.md).
