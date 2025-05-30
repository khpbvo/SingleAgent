# Troubleshooting

This document provides solutions to common problems and issues you might encounter when using the SingleAgent system.

## Common Issues

### Installation Problems

#### ImportError: No module named 'openai'

**Problem**: Missing or incorrectly installed OpenAI SDK.

**Solution**:
```bash
# Uninstall and reinstall OpenAI SDK
pip uninstall openai
pip install openai>=1.0.0

# Verify installation
python -c "import openai; print(openai.__version__)"
```

#### ModuleNotFoundError: No module named 'singleagent'

**Problem**: SingleAgent not properly installed or not in Python path.

**Solution**:
```bash
# Install in development mode
cd /path/to/SingleAgent
pip install -e .

# Or install from requirements
pip install -r requirements.txt

# Verify installation
python -c "from The_Agents.SingleAgent import SingleAgent"
```

#### Permission Denied Errors

**Problem**: Insufficient permissions to install packages or access files.

**Solutions**:
```bash
# Use virtual environment (recommended)
python -m venv singleagent_env
source singleagent_env/bin/activate  # On Windows: singleagent_env\Scripts\activate
pip install -r requirements.txt

# Or install with user flag
pip install --user -r requirements.txt

# Fix file permissions
chmod +x main.py
chmod -R 755 SingleAgent/
```

### Configuration Issues

#### API Key Not Found

**Problem**: OpenAI API key not configured or accessible.

**Symptoms**:
```
AuthenticationError: No API key provided
```

**Solutions**:
```bash
# Set environment variable (Linux/Mac)
export OPENAI_API_KEY="sk-your-api-key-here"

# Set environment variable (Windows)
set OPENAI_API_KEY=sk-your-api-key-here

# Or create .env file in project root
echo "OPENAI_API_KEY=sk-your-api-key-here" > .env

# Verify API key is set
python -c "import os; print('API Key set:', bool(os.getenv('OPENAI_API_KEY')))"
```

#### Invalid Configuration Format

**Problem**: Syntax errors in `pyproject.toml` configuration.

**Symptoms**:
```
TOMLDecodeError: Invalid TOML syntax
```

**Solution**:
```bash
# Validate TOML syntax
python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))"

# Common fixes:
# 1. Check for missing quotes around strings
# 2. Ensure proper array syntax: ["item1", "item2"]
# 3. Verify boolean values are lowercase: true, false
# 4. Check for trailing commas in tables
```

**Example of correct TOML format**:
```toml
[tool.singleagent]
default_agent = "code"  # String values need quotes
enabled_tools = ["ruff", "pylint"]  # Array syntax
auto_format = true  # Boolean lowercase
```

#### Tool Configuration Errors

**Problem**: Tools not working due to missing dependencies or incorrect configuration.

**Symptoms**:
```
ToolExecutionError: ruff command not found
```

**Solutions**:
```bash
# Install missing tools
pip install ruff pylint pyright

# Verify tool installation
ruff --version
pylint --version
pyright --version

# Check tool configuration in pyproject.toml
[tool.singleagent.tools.ruff]
enabled = true
config_file = "pyproject.toml"  # Ensure this file exists
```

### Runtime Issues

#### Context Window Exceeded

**Problem**: Input exceeds model's context window limit.

**Symptoms**:
```
InvalidRequestError: This model's maximum context length is 8192 tokens
```

**Solutions**:
```python
# Reduce context window in configuration
[tool.singleagent]
max_tokens = 4000  # Reduce from default 8000

# Or use context optimization
[tool.singleagent.context]
priority_threshold = 0.7  # Only keep high-priority context
summarization_ratio = 0.5  # More aggressive summarization
```

#### Agent Switching Not Working

**Problem**: Commands like `!code` or `!architect` don't switch agents.

**Symptoms**:
- No response to switch commands
- Agent stays on current agent

**Solutions**:
```python
# Check if interactive mode is enabled
python main.py --interactive

# Verify command syntax (commands start with !)
!code      # Correct
code       # Incorrect
!architect # Correct
architect  # Incorrect

# Check for typos in command
!code      # Correct
!cod       # Incorrect
```

#### Slow Performance

**Problem**: Agent responses are very slow.

**Symptoms**:
- Long delays before responses
- Tool execution timeouts

**Solutions**:
```toml
# Optimize performance settings
[tool.singleagent.performance]
max_concurrent_tools = 2  # Reduce from 3
tool_timeout = 15         # Reduce from 30
enable_caching = true     # Enable caching

# Disable expensive analysis
[tool.singleagent.tools.ast_analysis]
deep_analysis = false     # Disable deep analysis

[tool.singleagent.context]
track_all_variables = false  # Reduce entity tracking
```

### Tool-Specific Issues

#### Ruff Tool Failures

**Problem**: Ruff linting fails or produces unexpected results.

**Common Issues and Solutions**:

```bash
# Issue: Ruff not found
# Solution: Install ruff
pip install ruff

# Issue: Configuration file not found
# Solution: Create or specify config file
[tool.ruff]
line-length = 88
target-version = "py39"

# Issue: Unsupported Python version
# Solution: Update Ruff or Python
pip install --upgrade ruff
```

#### Pylint Tool Problems

**Problem**: Pylint analysis fails or hangs.

**Solutions**:
```bash
# Install missing dependencies
pip install pylint

# Create .pylintrc if missing
pylint --generate-rcfile > .pylintrc

# Disable problematic checkers
[tool.singleagent.tools.pylint]
disable_warnings = ["missing-docstring", "too-few-public-methods"]
```

#### Pyright Type Checking Issues

**Problem**: Pyright fails to analyze code properly.

**Solutions**:
```bash
# Install pyright
npm install -g pyright
# or
pip install pyright

# Create pyrightconfig.json
{
    "typeCheckingMode": "basic",
    "pythonVersion": "3.9"
}

# Disable strict mode if causing issues
[tool.singleagent.tools.pyright]
strict_mode = false
```

### File Operation Issues

#### Permission Denied on File Operations

**Problem**: Cannot read, write, or modify files.

**Solutions**:
```bash
# Check file permissions
ls -la path/to/file

# Fix permissions
chmod 644 path/to/file  # Read/write for owner, read for others
chmod 755 path/to/dir   # Execute permissions for directories

# Ensure SingleAgent has proper permissions
sudo chown -R $USER:$USER /path/to/project
```

#### File Encoding Issues

**Problem**: Files with non-UTF-8 encoding cause errors.

**Symptoms**:
```
UnicodeDecodeError: 'utf-8' codec can't decode byte
```

**Solutions**:
```python
# Convert file to UTF-8
iconv -f iso-8859-1 -t utf-8 file.py > file_utf8.py

# Or specify encoding in Python
with open('file.py', 'r', encoding='latin-1') as f:
    content = f.read()
```

#### Large File Handling

**Problem**: Very large files cause memory issues or timeouts.

**Solutions**:
```toml
# Configure file size limits
[tool.singleagent.tools.file_ops]
max_file_size = "5MB"  # Reduce from default

# Enable streaming for large files
stream_large_files = true
chunk_size = 1024
```

### Agent Behavior Issues

#### Agent Provides Irrelevant Responses

**Problem**: Agent responses don't match the query or context.

**Solutions**:
```python
# Clear context and restart
!context clear
!restart

# Provide more specific instructions
# Instead of: "Fix this file"
# Use: "Run Ruff linter on src/main.py and fix formatting issues"

# Switch to appropriate agent
!code      # For code quality issues
!architect # For structural analysis
```

#### Agent Forgets Previous Context

**Problem**: Agent doesn't remember earlier conversation.

**Solutions**:
```toml
# Increase context retention
[tool.singleagent.context]
max_conversation_history = 200  # Increase from 100
session_cache_size = 2000       # Increase cache

# Check context status
!context summary
!context history --last 10
```

#### Inconsistent Tool Results

**Problem**: Same operation produces different results.

**Solutions**:
```python
# Clear tool cache
!cache clear

# Use consistent configuration
[tool.singleagent.tools.ruff]
config_file = "pyproject.toml"  # Always use same config

# Check for external factors
# - File system changes
# - Environment variables
# - Tool version updates
```

### Network and API Issues

#### Rate Limiting

**Problem**: OpenAI API rate limits exceeded.

**Symptoms**:
```
RateLimitError: Rate limit reached for requests
```

**Solutions**:
```python
# Add retry logic and delays
[tool.singleagent]
max_retries = 5
retry_delay = 2  # seconds

# Use a different model or reduce usage
model = "gpt-3.5-turbo"  # Instead of gpt-4

# Monitor API usage
!status api
```

#### Network Connectivity Issues

**Problem**: Cannot connect to OpenAI API.

**Solutions**:
```bash
# Test connectivity
curl -I https://api.openai.com/v1/models

# Check proxy settings
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080

# Configure custom endpoint if needed
export OPENAI_BASE_URL="https://custom.openai.endpoint.com/v1"
```

### Development and Debugging

#### Enabling Debug Mode

**For detailed debugging information**:

```bash
# Set debug environment variable
export SINGLEAGENT_DEBUG=true

# Or use command line flag
python main.py --debug

# Enable verbose logging
export SINGLEAGENT_LOG_LEVEL=DEBUG
```

#### Logging Configuration

**To capture detailed logs**:

```toml
[tool.singleagent.logging]
level = "DEBUG"
file = "debug.log"
format = "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"

# Component-specific logging
[tool.singleagent.logging.components]
agents = "DEBUG"
tools = "DEBUG"
context = "DEBUG"
```

#### Performance Profiling

**To identify performance bottlenecks**:

```bash
# Enable profiling
export SINGLEAGENT_PROFILE=true

# Run with profiler
python -m cProfile -o profile.stats main.py

# Analyze profile
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative').print_stats(20)"
```

### Recovery Procedures

#### Reset to Factory Defaults

**Complete reset of configuration**:

```bash
# Remove cache and config
rm -rf ~/.singleagent/cache
rm -rf ~/.singleagent/config

# Reset to default configuration
python main.py --reset-config

# Verify clean state
python main.py --validate-config
```

#### Backup and Restore

**Backup current state**:

```bash
# Backup configuration
cp pyproject.toml pyproject.toml.backup

# Backup cache
tar -czf singleagent_cache_backup.tar.gz ~/.singleagent/cache

# Restore from backup
cp pyproject.toml.backup pyproject.toml
tar -xzf singleagent_cache_backup.tar.gz -C ~/
```

## Diagnostic Commands

### Built-in Diagnostics

```python
# Check system status
!status

# Validate configuration
!config validate

# Test tool connectivity
!tools test

# Check context state
!context summary

# View recent errors
!errors --last 10

# Performance metrics
!metrics
```

### Manual Diagnostics

```bash
# Check Python environment
python --version
pip list | grep -E "(openai|ruff|pylint)"

# Check file permissions
ls -la SingleAgent/
stat main.py

# Test API connectivity
python -c "import openai; client = openai.OpenAI(); print(client.models.list())"

# Validate TOML syntax
python -c "import tomllib; print('TOML valid') if tomllib.load(open('pyproject.toml', 'rb')) else print('TOML invalid')"
```

## Getting Help

### Log Analysis

**When reporting issues, include**:

1. **Error messages** (complete stack traces)
2. **Configuration files** (`pyproject.toml`)
3. **Environment information** (Python version, OS, dependencies)
4. **Steps to reproduce** the issue
5. **Expected vs actual behavior**

### Support Resources

- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Check the full documentation set
- **Examples**: Review example configurations and use cases
- **Community**: Join discussions and ask questions

### Creating Minimal Reproducible Examples

```python
# Minimal test case for reporting issues
import os
from The_Agents.SingleAgent import SingleAgent

# Set minimal environment
os.environ['OPENAI_API_KEY'] = 'sk-test-key'

# Create simple test
agent = SingleAgent()
try:
    response = agent.process_request("test message")
    print("Success:", response)
except Exception as e:
    print("Error:", e)
    import traceback
    traceback.print_exc()
```

This troubleshooting guide covers the most common issues and their solutions. For issues not covered here, enable debug logging and examine the detailed error messages for more specific guidance.
