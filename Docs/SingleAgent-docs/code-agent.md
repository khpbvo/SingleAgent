# Code Agent

De Code Agent (SingleAgent) is gespecialiseerd in directe code manipulatie, analyse, en debugging. Het is ontworpen voor ontwikkelaars die gedetailleerde hulp nodig hebben bij programmeer taken.

## Overzicht

De Code Agent biedt een uitgebreide set tools voor:
- **Code Quality Analysis**: Linting, type checking, en style analysis
- **File Operations**: Lezen, schrijven, en manipuleren van bestanden
- **Debugging Support**: Error analysis en context-aware debugging
- **Patch Management**: Diff creation en patch application
- **Command Execution**: Shell command integration

## Activeren

```bash
# Schakel naar Code Agent mode
!code
```

Het systeem start standaard in Code Agent mode.

## Core Capabilities

### 1. Code Quality Analysis

#### Ruff - Modern Python Linting

```python
# Basis gebruik
"Run ruff op alle Python bestanden"

# Specifieke bestanden
"Gebruik ruff om main.py en utils.py te checken"

# Met custom flags
"Run ruff met --fix flag om automatische correcties toe te passen"
```

**Ruff Features:**
- Snelle linting (100x sneller dan flake8)
- Gecombineerde functionaliteit van flake8, isort, pyupgrade
- Automatische fixes voor veel issues
- Configureerbaar via pyproject.toml

#### Pylint - Comprehensive Analysis

```python
# Diepgaande analyse
"Run pylint op de hele codebase voor een uitgebreide analyse"

# Specifieke modules
"Gebruik pylint om The_Agents module te analyseren"
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

# Met specifieke configuratie
"Check types in alle Python bestanden met pyright"
```

**Pyright Features:**
- Fast static type checking
- Integration met VS Code
- Advanced type inference
- Configuration via pyproject.toml

### 2. File Operations

#### Intelligent File Reading

```python
# Basis file reading
"Lees het bestand main.py"
"Wat staat er in requirements.txt?"

# Context-aware reading
"Lees de SingleAgent.py en leg uit hoe de context management werkt"

# Multiple files
"Lees main.py en ArchitectAgent.py en vergelijk hun structuur"
```

**Features:**
- Automatische syntax highlighting
- Context integration
- Large file handling
- Binary file detection

#### File Writing & Modification

De Code Agent kan bestanden maken en wijzigen:

```python
# Bestand aanmaken
"Maak een nieuwe test file voor de SingleAgent class"

# Content modification
"Voeg een docstring toe aan de run methode in SingleAgent.py"

# Configuration files
"Maak een pyproject.toml met ruff configuratie"
```

### 3. Patch Management

#### Diff Creation

```python
# Visual diffs
"Maak een colored diff van de wijzigingen in main.py"

# Compare files
"Vergelijk de oude en nieuwe versie van deze functie"
```

**Diff Features:**
- Color-coded output
- Line-by-line comparison
- Context preservation
- Multiple format support

#### Patch Application

```python
# Apply patches
"Pas deze patch toe op het bestand"

# Verification
"Verifieer of de patch correct is toegepast"
```

### 4. Context-Aware Debugging

#### Error Analysis

```python
# Error help
"Ik krijg een AttributeError in line 42, kun je helpen?"

# Stack trace analysis
"Analyseer deze stack trace en geef suggestions"

# Performance issues
"Deze functie is traag, kun je optimalisatie voorstellen?"
```

#### Code Understanding

```python
# Function explanation
"Leg uit hoe de _extract_entities_from_input methode werkt"

# Flow analysis
"Trace de execution flow van main.py naar SingleAgent"

# Dependency analysis
"Welke modules gebruikt SingleAgent en waarom?"
```

### 5. Command Integration

#### Shell Command Execution

```python
# Git operations
"Voer git status uit"

# Build commands
"Run de tests met pytest"

# File operations
"Maak een backup van de config files"
```

## Tool Reference

### Development Tools

#### `run_ruff`

**Purpose**: Python code linting en formatting

**Parameters:**
- `paths`: List van file/directory paths
- `flags`: Extra command line flags

**Example Usage:**
```python
# Via natural language
"Run ruff op alle Python bestanden"
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
- `paths`: Files of directories om te analyseren
- `flags`: Pylint command line options

**Example Usage:**
```python
"Run pylint op de The_Agents module"
"Gebruik pylint met --disable=missing-docstring"
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
"Check types met pyright"
"Run pyright --verbose voor gedetailleerde output"
```

### File Operations Tools

#### `read_file`

**Purpose**: Bestand inhoud lezen met context tracking

**Parameters:**
- `file_path`: Path naar het bestand
- `start_line`: Start line (optional)
- `end_line`: End line (optional)

**Features:**
- Automatische encoding detection
- Large file handling
- Context integration
- Entity tracking

#### `create_colored_diff`

**Purpose**: Visual diff creation tussen bestanden of content

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

**Purpose**: Patch toepassing op bestanden

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

**Purpose**: Shell command execution met output capture

**Parameters:**
- `command`: Command om uit te voeren
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
"Vergelijk de error handling in alle agent files"

# Dependency tracking
"Welke bestanden importeren van agents module?"

# Pattern detection
"Zoek naar inconsistente naming patterns in de codebase"
```

### 3. Intelligent Suggestions

```python
# Code improvements
"Deze functie kan worden gerefactored voor betere leesbaarheid"

# Performance optimizations
"Dit loop kan worden geoptimaliseerd met list comprehension"

# Best practices
"Overweeg het gebruik van type hints voor deze functie"
```

### 4. Integration met Development Workflow

```python
# Pre-commit checks
"Run alle quality checks voordat ik commit"

# Testing integration
"Maak een test voor deze nieuwe functie"

# Documentation
"Genereer docstrings voor alle publieke methodes"
```

## Configuration

### Model Settings

```python
# Code Agent gebruikt deterministic settings
model_settings=ModelSettings(temperature=0.0)
```

**Rationale**: Temperature 0.0 zorgt voor consistente, reproduceerbare code analysis.

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
"Geef een algemeen overzicht van de code quality" 
→ "Focus op de error handling in SingleAgent.py"
→ "Bekijk specifiek de _extract_entities_from_input methode"
```

### 2. Tool Combinatie

```python
# Combineer tools voor complete analyse
"Run ruff voor style, pylint voor logic, en pyright voor types"
```

### 3. Context Behoud

```python
# Gebruik context voor follow-up vragen
"Na de vorige analyse, wat zijn de prioriteiten voor fixes?"
```

### 4. Documentation Integration

```python
# Vraag om explanations bij code analysis
"Leg uit waarom pylint deze warning geeft en hoe het op te lossen"
```

## Performance Tips

### 1. Selective Analysis

```python
# Analyseer specifieke delen voor snellere results
"Run ruff alleen op de Tools/ directory"
```

### 2. Cached Results

De Code Agent cached tool results wanneer mogelijk:

```python
# Hergebruik van recente analysis results
"Gebaseerd op de eerdere ruff check..."
```

### 3. Parallel Execution

```python
# Multiple tools kunnen parallel draaien
"Run ruff en pylint tegelijkertijd"
```

## Common Workflows

### 1. Code Review Workflow

```python
1. "Analyseer alle Python bestanden met ruff"
2. "Run pylint voor diepere analyse" 
3. "Check types met pyright"
4. "Maak een samenvatting van alle gevonden issues"
5. "Prioriteer de fixes op basis van impact"
```

### 2. Debugging Workflow

```python
1. "Lees het bestand waar de error optreedt"
2. "Analyseer de error message en stack trace"
3. "Bekijk gerelateerde bestanden en dependencies"
4. "Stel een fix voor en maak een patch"
5. "Verifieer de fix met relevante tools"
```

### 3. Refactoring Workflow

```python
1. "Analyseer de huidige code structure"
2. "Identificeer refactoring opportunities"
3. "Maak een plan voor de wijzigingen"
4. "Implementeer incrementele changes"
5. "Verifieer met tests en quality checks"
```

## Troubleshooting

### Common Issues

#### Tool Execution Errors
```python
# Zorg dat tools geïnstalleerd zijn
"Run pip install ruff pylint pyright"

# Check working directory
"Wat is de huidige working directory?"
```

#### File Access Issues
```python
# Check file permissions
"Kan ik dit bestand lezen/schrijven?"

# Verify file paths
"Bestaat dit bestand op het verwachte pad?"
```

#### Context Confusion
```python
# Reset context indien nodig  
"!clear"

# Manual context addition
"!manualctx"
```

Voor meer troubleshooting, zie [Troubleshooting Guide](troubleshooting.md).

## Extensibility

### Adding New Tools

Nieuwe tools kunnen worden toegevoegd via de `@function_tool` decorator:

```python
@function_tool
async def my_custom_tool(wrapper: RunContextWrapper, params: MyParams) -> str:
    # Tool implementation
    return result
```

### Custom Workflows

Implementeer custom workflows door tools te combineren in agent instructions.

### Integration met External Tools

Tools kunnen externe systemen aanroepen voor uitgebreide functionaliteit.

De Code Agent vormt een krachtige basis voor elke development workflow en kan aangepast worden aan specifieke project behoeften.
