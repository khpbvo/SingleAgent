# Code Agent

The Code Agent (SingleAgent) is specialized in direct code manipulation, analysis, and debugging. It is designed for developers who need detailed help with programming tasks.

## Overview

The Code Agent provides an extensive set of tools for:
- **Code Quality Analysis**: Linting, type checking, and style analysis
- **File Operations**: Reading, writing, and manipulating files
- **Debugging Support**: Error analysis and context-aware debugging
- **Patch Management**: Diff creation and patch application
- **Command Execution**: Shell command integration

## Activation

```bash
# Switch to Code Agent mode
!code
```

The system starts in Code Agent mode by default.

## Core Capabilities

### 1. Code Quality Analysis

#### Ruff - Modern Python Linting

```python
# Basic usage
"Run ruff on all Python files"

# Specific files
"Use ruff to check main.py and utils.py"

# With custom flags
"Run ruff with --fix flag to apply automatic corrections"
```

**Ruff Features:**
- Fast linting (100x faster than flake8)
- Combined functionality of flake8, isort, pyupgrade
- Automatic fixes for many issues
- Configurable via pyproject.toml

#### Pylint - Comprehensive Analysis

```python
# Deep analysis
"Run pylint on the entire codebase for a comprehensive analysis"

# Specifieke modules
"Gebruik pylint om The_Agents module te analyze"
```

**Pylint Features:**
- Code quality metrics
- Design pattern violations
- Complexity analysis
- Documentation checking

#### Pyright - Static Type Checking

```python
# Type checking
"Run pyright om type errors te vinden"

# Met specifieke configuration
"Check types in alle Python files with pyright"
```

**Pyright Features:**
- Fast static type checking
- Integration with VS Code
- Advanced type inference
- Configuration via pyproject.toml

### 2. File Operations

#### Intelligent File Reading

```python
# Basis file reading
"Lees the bestand main.py"
"Wat staat er in requirements.txt?"

# Context-aware reading
"Lees the SingleAgent.py and leg from hoe the context management werkt"

# Multiple files
"Lees main.py and ArchitectAgent.py and vergelijk hun structuur"
```

**Features:**
- Automatische syntax highlighting
- Context integration
- Large file handling
- Binary file detection

#### File Writing & Modification

De Code Agent kan files create and wijzigen:

```python
# Bestand aancreate
"Create a nieuwe test file for the SingleAgent class"

# Content modification
"Voeg a docstring toe aan the run methode in SingleAgent.py"

# Configuration files
"Create a pyproject.toml with ruff configuration"
```

### 3. Patch Management

#### Diff Creation

```python
# Visual diffs
"Create a colored diff of the wijzigingen in main.py"

# Compare files
"Vergelijk the oude and nieuwe versie of deze functie"
```

**Diff Features:**
- Color-coded output
- Line-by-line comparison
- Context preservation
- Multiple format support

#### Patch Application

```python
# Apply patches
"Pas deze patch toe on the bestand"

# Verification
"Verifieer or the patch correct is toegepast"
```

### 4. Context-Aware Debugging

#### Error Analysis

```python
# Error help
"Ik krijg a AttributeError in line 42, kun je helpen?"

# Stack trace analysis
"Analyze theze stack trace and geef suggestions"

# Performance issues
"This function is traag, kun je optimalisatie voorstellen?"
```

#### Code Understanding

```python
# Function explanation
"Leg from hoe the _extract_entities_from_input methode werkt"

# Flow analysis
"Trace the execution flow of main.py to SingleAgent"

# Dependency analysis
"Welke modules used SingleAgent and waarom?"
```

### 5. Command Integration

#### Shell Command Execution

```python
# Git operations
"Voer git status uit"

# Build commands
"Run the tests with pytest"

# File operations
"Create a backup of the config files"
```

## Tool Reference

### Development Tools

#### `run_ruff`

**Purpose**: Python code linting and formatting

**Parameters:**
- `paths`: List of file/directory paths
- `flags`: Extra command line flags

**Example Usage:**
```python
# Via natural language
"Run ruff on alle Python files"
"Gebruik ruff --fix om automatische correcties toe te passen"

# Direct tool call equivalent
run_ruff(paths=[".", "tests/"], flags=["--check"])
```

**Common Flags:**
- `--fix`: Automatische correcties
- `--check`: Check-only mode
- `--config`: Custom config file
- `--select`: Specifieke rules selecteren

#### `run_pylint`

**Purpose**: Comprehensive Python code analysis

**Parameters:**
- `paths`: Files or directories om te analyze
- `flags`: Pylint command line options

**Example Usage:**
```python
"Run pylint on the The_Agents module"
"Gebruik pylint with --disable=missing-docstring"
```

**Common Flags:**
- `--disable`: Disable specifieke checks
- `--enable`: Enable specifieke checks
- `--rcfile`: Custom configuration
- `--output-format`: Output format (text, json, etc.)

#### `run_pyright`

**Purpose**: Static type checking

**Parameters:**
- `paths`: Paths om te type checken
- `flags`: Pyright options

**Example Usage:**
```python
"Check types with pyright"
"Run pyright --verbose for gedetailleerde output"
```

### File Operations Tools

#### `read_file`

**Purpose**: Bestand inhoud lezen with context tracking

**Parameters:**
- `file_path`: Path to the bestand
- `start_line`: Start line (optional)
- `end_line`: End line (optional)

**Features:**
- Automatische encoding detection
- Large file handling
- Context integration
- Entity tracking

#### `create_colored_diff`

**Purpose**: Visual diff creation tussen files or content

**Parameters:**
- `original_content`: Original content
- `modified_content`: Modified content
- `original_filename`: Original file name
- `modified_filename`: Modified file name

**Output:**
- Color-coded differences
- Line numbers
- Context lines
- Statistics

#### `apply_patch`

**Purpose**: Patch toepassing on files

**Parameters:**
- `file_path`: Target file
- `patch_content`: Patch content (unified diff format)

**Features:**
- Dry-run mode
- Backup creation
- Verification
- Rollback capability

### System Tools

#### `run_command`

**Purpose**: Shell command execution with output capture

**Parameters:**
- `command`: Command om from te voeren
- `working_dir`: Working directory (optional)

**Features:**
- Real-time output
- Error handling
- Environment preservation
- Command history tracking

#### `os_command`

**Purpose**: OS-specific command operations

**Parameters:**
- `command`: OS command
- `capture_output`: Whether to capture output

#### `change_dir`

**Purpose**: Working directory wijzigen

**Parameters:**
- `path`: New working directory

## Advanced Features

### 1. Smart Context Integration

De Code Agent tracked automatisch:

```python
# File access patterns
"Recently accessed files: main.py, SingleAgent.py, tools.py"

# Command history  
"Recently run commands: ruff check ., pylint The_Agents/"

# Active tasks
"Current task: debugging entity extraction"
```

### 2. Multi-file Analysis

```python
# Cross-file analysis
"Vergelijk the error handling in alle agent files"

# Dependency tracking
"Welke files importeren of agents module?"

# Pattern detection
"Zoek to inconsistente naming patterns in the codebase"
```

### 3. Intelligent Suggestions

```python
# Code improvements
"This function kan worden gerefactored for betere leesbaarheid"

# Performance optimizations
"Dit loop kan worden geoptimaliseerd with list comprehension"

# Best practices
"Overweeg the gebruik of type hints for deze functie"
```

### 4. Integration with Development Workflow

```python
# Pre-commit checks
"Run alle quality checks voordat ik commit"

# Testing integration
"Create a test for deze nieuwe functie"

# Documentation
"Genereer docstrings for alle publieke methodes"
```

## Configuration

### Model Settings

```python
# Code Agent used deterministic settings
model_settings=ModelSettings(temperature=0.0)
```

**Rationale**: Temperature 0.0 zorgt for consistente, reproduceerbare code analysis.

### Tool Configuration

#### Ruff Configuration (pyproject.toml)

```toml
[tool.ruff]
line-length = 120
select = ["E", "F", "B", "UP", "I", "SIM", "D"]
ignore = ["D203", "D213"]
```

#### Pylint Configuration

```ini
[MASTER]
load-plugins = pylint_pydantic

[MESSAGES CONTROL]
disable = missing-docstring,too-few-public-methods
```

## Best Practices

### 1. Incremental Analysis

```python
# Start breed, ga dan specifiek
"Geef a algemeen overzicht of the code quality" 
→ "Focus on the error handling in SingleAgent.py"
→ "Bekijk specifiek the _extract_entities_from_input methode"
```

### 2. Tool Combinatie

```python
# Combineer tools for complete analyse
"Run ruff for style, pylint for logic, and pyright for types"
```

### 3. Context Behoud

```python
# Gebruik context for follow-up vragen
"Na the vorige analyse, wat are the prioriteiten for fixes?"
```

### 4. Documentation Integration

```python
# Vraag om explanations at code analysis
"Leg from waarom pylint deze warning geeft and hoe the on te lossen"
```

## Performance Tips

### 1. Selective Analysis

```python
# Analyseer specifieke delen for snellere results
"Run ruff alleen on the Tools/ directory"
```

### 2. Cached Results

De Code Agent cached tool results wanneer mogelijk:

```python
# Hergebruik of recente analysis results
"Gebaseerd on the eerdere ruff check..."
```

### 3. Parallel Execution

```python
# Multiple tools can parallel draaien
"Run ruff and pylint tegelijkertijd"
```

## Common Workflows

### 1. Code Review Workflow

```python
1. "Analyseer alle Python files with ruff"
2. "Run pylint for diepere analyse" 
3. "Check types with pyright"
4. "Create a samenvatting of alle gevonden issues"
5. "Prioriteer the fixes on basis of impact"
```

### 2. Debugging Workflow

```python
1. "Lees the bestand waar the error optreedt"
2. "Analyze the error message and stack trace"
3. "Bekijk gerelateerde files and dependencies"
4. "Stel a fix for and maak a patch"
5. "Verifieer the fix with relevante tools"
```

### 3. Refactoring Workflow

```python
1. "Analyze the huidige code structure"
2. "Identificeer refactoring opportunities"
3. "Create a plan for the wijzigingen"
4. "Implementeer incrementele changes"
5. "Verifieer with tests and quality checks"
```

## Troubleshooting

### Common Issues

#### Tool Execution Errors
```python
# Zorg that tools geïnstalleerd are
"Run pip install ruff pylint pyright"

# Check working directory
"Wat is the huidige working directory?"
```

#### File Access Issues
```python
# Check file permissions
"Kan ik dit bestand lezen/schrijven?"

# Verify file paths
"Bestaat dit bestand on the verwachte pad?"
```

#### Context Confusion
```python
# Reset context indien nodig  
"!clear"

# Manual context addition
"!manualctx"
```

For more troubleshooting, zie [Troubleshooting Guide](troubleshooting.md).

## Extensibility

### Adding New Tools

Nieuwe tools can worden toegevoegd via the `@function_tool` decorator:

```python
@function_tool
async def my_custom_tool(wrapper: RunContextWrapper, params: MyParams) -> str:
    # Tool implementation
    return result
```

### Custom Workflows

Implementeer custom workflows through tools te combineren in agent instructions.

### Integration with External Tools

Tools can externe systemen aanroepen for uitgebreide functionaliteit.

De Code Agent vormt a krachtige basis for elke development workflow and kan aangepast worden aan specifieke project behoeften.
