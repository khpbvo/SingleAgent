# Architect Agent

The Architect Agent is specialized in high-level software architecture analysis, design pattern detection, and strategic project planning. It is designed for software architects and senior developers who need structural insights.

## Overview

The Architect Agent provides advanced tools for:
- **Project Structure Analysis**: Complete codebase structure analysis  
- **Design Pattern Detection**: Automatic identification of design patterns
- **Dependency Analysis**: Dependency graphs and cyclic dependencies
- **Architectural Planning**: TODO lists and roadmap generation
- **AST-based Analysis**: In-depth code structure analysis

## Activation

```bash
# Switch to Architect Agent mode
!architect
```

The system then shows:
```
=== Architect Agent Mode ===
```

## Core Capabilities

### 1. Project Structure Analysis

#### Complete Codebase Overview

```python
# High-level project analysis
"Analyze the complete project structure"

# Specific directory
"Give me an overview of the Tools/ directory structure"

# With statistics
"Analyze the project structure and provide statistics per file type"
```

**Output Features:**
- Hierarchical directory tree
- File type statistics
- Size metrics
- Dependency relationships

#### Directory Tree Generation

```python
# Visual tree representation
"Maak een tree view van de project structuur"

# Filtered analysis
"Toon alleen Python bestanden in de structuur"

# Depth control  
"Analyseer project structuur tot 3 levels diep"
```

### 2. AST-Based Code Analysis

#### Deep Code Structure Analysis

```python
# Complete AST analysis
"Analyseer de AST van SingleAgent.py"

# Specific aspects
"Welke classes en methods zitten in ArchitectAgent.py?"

# Dependency extraction
"Welke imports en dependencies heeft main.py?"
```

**AST Analysis Types:**
- **Classes**: Class definitions, inheritance, methods
- **Functions**: Function signatures, parameters, return types
- **Imports**: Module dependencies en import patterns
- **Dependencies**: Internal en external dependencies

#### Method and Class Discovery

```python
# Class analysis
"Geef me alle classes in de The_Agents module"

# Method signatures
"Wat zijn de method signatures van de SingleAgent class?"

# Inheritance hierarchy
"Toon de inheritance relationships in de codebase"
```

### 3. Design Pattern Detection

#### Automatic Pattern Recognition

```python
# Pattern scanning
"Welke design patterns zie je in de codebase?"

# Specific pattern analysis
"Is er een singleton pattern gebruikt in het project?"

# Anti-pattern detection
"Zijn er code anti-patterns die geaddresseerd moeten worden?"
```

**Detected Patterns:**
- **Creational**: Singleton, Factory, Builder
- **Structural**: Adapter, Facade, Decorator
- **Behavioral**: Observer, Strategy, Command
- **Anti-patterns**: God Object, Magic Numbers, Code Duplication

#### Pattern Analysis Example

```python
# Input
"Analyseer design patterns in ArchitectAgent.py"

# Output  
{
  "singleton": {
    "instances": [{"name": "SpacyModelSingleton", "confidence": 0.9}],
    "description": "Single instance throughout the program"
  },
  "facade": {
    "instances": [{"name": "ArchitectAgent", "confidence": 0.7}],
    "description": "Simple interface to complex subsystem"
  }
}
```

### 4. Dependency Analysis

#### Dependency Graph Generation

```python
# Complete dependency graph
"Maak een dependency graph van het hele project"

# Module-specific dependencies
"Welke dependencies heeft de Tools module?"

# Circular dependency detection
"Zijn er circular dependencies in de codebase?"
```

**Graph Features:**
- Visual dependency mapping
- Cycle detection
- Dependency strength analysis
- External vs internal dependencies

#### Import Analysis

```python
# Import patterns
"Analyseer alle import statements en hun patterns"

# Unused imports
"Zijn er unused imports die opgeruimd kunnen worden?"

# Import optimization
"Hoe kunnen de imports beter georganiseerd worden?"
```

### 5. Architectural Planning

#### TODO List Generation

```python
# Complete roadmap
"Maak een TODO lijst voor architecturale verbeteringen"

# Specific features
"Genereer een TODO voor het toevoegen van nieuwe agent types"

# Priority-based planning
"Maak een geprioriteerde lijst van architectural improvements"
```

**TODO Features:**
- Priority levels (critical, high, medium, low)
- Category classification (infrastructure, feature, documentation, testing)
- Time estimations
- Dependency tracking
- Subtask breakdown

#### Project Planning

```python
# Strategic planning
"Wat zijn de belangrijkste architectural debt items?"

# Scalability analysis
"Hoe kan dit systeem beter schalen?"

# Modularity assessment
"Hoe modulair is de huidige architectuur?"
```

## Tool Reference

### Analysis Tools

#### `analyze_project_structure`

**Purpose**: Complete project directory en file analysis

**Parameters:**
- `directory`: Root directory om te analyseren
- `max_depth`: Maximum depth voor tree traversal  
- `include_patterns`: File patterns om te includeren (e.g., "*.py")
- `exclude_patterns`: Patterns om uit te sluiten (e.g., "__pycache__")

**Example Usage:**
```python
"Analyseer de project structuur tot 4 levels diep"
"Toon alleen Python en Markdown bestanden in de structuur"
```

**Output:**
```json
{
  "structure": {
    "files": [...],
    "directories": {...}
  },
  "statistics": {
    "file_count": 45,
    "directory_count": 12,
    "file_types": {".py": 32, ".md": 8, ".toml": 1}
  }
}
```

#### `analyze_ast`

**Purpose**: AST-based code structure analysis

**Parameters:**
- `file_path`: Path naar Python bestand
- `analysis_type`: Type analyse (classes, functions, imports, dependencies, all)

**Example Usage:**
```python
"Analyseer de AST van main.py voor alle elementen"
"Geef me alleen de classes uit SingleAgent.py"
```

**Analysis Types:**
- `classes`: Class definitions en methods
- `functions`: Function definitions en signatures  
- `imports`: Import statements en modules
- `dependencies`: Dependency extraction
- `all`: Complete analysis

#### `detect_code_patterns`

**Purpose**: Design pattern en anti-pattern detectie

**Parameters:**
- `file_path`: Path naar Python bestand om te analyseren

**Example Usage:**
```python
"Detecteer design patterns in ArchitectAgent.py"
"Zijn er anti-patterns in de Tools module?"
```

**Detected Patterns:**
```json
{
  "design_patterns": {
    "singleton": {"instances": [...], "confidence": 0.9},
    "factory": {"instances": [...], "confidence": 0.7}
  },
  "anti_patterns": {
    "god_object": {"instances": [...], "confidence": 0.6},
    "magic_numbers": {"instances": [...], "confidence": 0.8}
  }
}
```

#### `analyze_dependencies`

**Purpose**: Dependency graph creation en analysis

**Parameters:**
- `directory`: Root directory voor dependency analysis
- `include_external`: Include external dependencies
- `max_depth`: Maximum analysis depth

**Example Usage:**
```python
"Maak een dependency graph van de Tools directory"
"Analyseer alle dependencies inclusief externe packages"
```

#### `generate_todo_list`

**Purpose**: Structured TODO list generation

**Parameters:**
- `description`: Project beschrijving
- `features`: List van gewenste features
- `directory`: Project directory voor context

**Example Usage:**
```python
"Maak een TODO lijst voor het uitbreiden van agent capabilities"
"Genereer een roadmap voor performance optimizations"
```

**TODO Structure:**
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Implement caching layer",
      "priority": "high",
      "category": "infrastructure",
      "estimated_time": "2-4 hours",
      "dependencies": [],
      "subtasks": [...]
    }
  ]
}
```

### File Operations Tools

#### `read_directory`

**Purpose**: Directory content listing met metadata

**Parameters:**
- `path`: Directory path
- `recursive`: Recursive listing
- `include_hidden`: Include hidden files
- `max_depth`: Maximum depth

#### `write_file`

**Purpose**: File creation voor documentation en planning

**Parameters:**
- `file_path`: Output file path
- `content`: Content om te schrijven
- `mode`: Write mode (write, append)

**Example Usage:**
```python
"Schrijf de TODO lijst naar een TODO.md bestand"
"Maak een ARCHITECTURE.md met de project structuur"
```

#### `read_file`

**Purpose**: Context-aware file reading

Identical aan Code Agent versie maar gebruikt voor architectural analysis.

### System Tools

#### `run_command`

**Purpose**: Command execution voor build/analysis tools

**Example Usage:**
```python
"Run find . -name '*.py' | wc -l om Python bestanden te tellen"
"Voer tree command uit voor directory visualization"
```

## Advanced Features

### 1. Multi-dimensional Analysis

#### Complexity Analysis

```python
# Cyclomatic complexity
"Analyseer de code complexity van alle modules"

# Coupling analysis  
"Hoe tight zijn de coupling relationships?"

# Cohesion assessment
"Beoordeel de cohesion binnen modules"
```

#### Maintainability Metrics

```python
# Technical debt assessment
"Wat is de technical debt van dit project?"

# Refactoring opportunities
"Welke delen van de code kunnen gerefactored worden?"

# Code quality trends
"Hoe is de code quality over tijd veranderd?"
```

### 2. Architectural Recommendations

#### Design Improvements

```python
# Pattern recommendations
"Welke design patterns zouden dit project verbeteren?"

# Structural improvements
"Hoe kan de modulaire structuur verbeterd worden?"

# Performance architecture
"Welke architecturale wijzigingen zouden performance verbeteren?"
```

#### Best Practices

```python
# SOLID principles
"Hoe goed volgt de code de SOLID principles?"

# Clean architecture
"Wat zijn de clean architecture violations?"

# Domain-driven design
"Hoe kan DDD beter toegepast worden?"
```

### 3. Context-Aware Planning

#### Project Evolution

```python
# Growth planning
"Hoe moet de architectuur evolueren voor schaalgroei?"

# Technology migration
"Wat is de strategie voor het adopteren van nieuwe technologieën?"

# Legacy modernization
"Hoe kunnen legacy onderdelen gemoderniseerd worden?"
```

#### Team Coordination

```python
# Work distribution
"Hoe kunnen architectural tasks verdeeld worden over het team?"

# Risk assessment
"Wat zijn de grootste architectural risks?"

# Timeline planning
"Wat is een realistische timeline voor deze architectural changes?"
```

## Configuration

### Agent Instructions

De Architect Agent is geconfigureerd met specifieke architectural focus:

```python
AGENT_INSTRUCTIONS = """
You are an expert software architect focused on:
1. High-level system design and structure analysis
2. Design pattern identification and recommendations  
3. Architectural debt identification and prioritization
4. Strategic technical planning and roadmapping
5. Code organization and modularity assessment

PRINCIPLES TO FOLLOW:
- Focus on architectural concerns rather than implementation details
- Explain reasoning behind suggestions
- Consider trade-offs between different approaches
- Respect existing architecture when suggesting changes
- Consider maintainability, scalability, and extensibility
"""
```

### Tool Configuration

#### AST Analysis Configuration

```python
# Analysis depth control
MAX_AST_DEPTH = 5

# Pattern detection thresholds
PATTERN_CONFIDENCE_THRESHOLD = 0.7
ANTI_PATTERN_THRESHOLD = 0.6
```

#### Project Structure Analysis

```python
# Default exclude patterns
EXCLUDE_PATTERNS = [
    "__pycache__", "*.pyc", "*.pyo", 
    ".git", ".venv", "venv", 
    "node_modules", ".DS_Store"
]

# Include patterns for analysis
INCLUDE_PATTERNS = [
    "*.py", "*.md", "*.txt", "*.json", 
    "*.toml", "*.yaml", "*.yml"
]
```

## Entity Tracking

### Architecture-Specific Entities

De Architect Agent tracked specifieke entities:

```python
# Design patterns
design_patterns = ["singleton", "factory", "observer", "strategy"]

# Architecture concepts  
architecture_concepts = ["module", "component", "service", "dependency"]

# Planning entities
planning_entities = ["task", "milestone", "requirement"]
```

### Context State Management

```python
# Architecture state
architecture_state = {
    "design_patterns": [...],
    "architecture_concepts": [...], 
    "identified_debt": [...],
    "improvement_areas": [...]
}
```

## Common Workflows

### 1. New Project Analysis

```python
1. "Analyseer de complete project structuur"
2. "Identificeer de core architectural patterns"
3. "Maak een dependency graph"
4. "Detecteer potential architectural issues"
5. "Genereer een improvement roadmap"
```

### 2. Architecture Review

```python
1. "Evalueer de huidige architectural decisions"
2. "Identificeer design pattern usage"
3. "Assess code organization en modularity"
4. "Detect anti-patterns en technical debt"
5. "Recommend structural improvements"
```

### 3. Refactoring Planning

```python
1. "Analyseer areas die refactoring nodig hebben"
2. "Prioriteer refactoring efforts"
3. "Plan incremental improvement steps" 
4. "Estimate effort en impact"
5. "Create detailed TODO lists"
```

### 4. Scalability Assessment

```python
1. "Evaluate current architecture voor scalability"
2. "Identify bottlenecks en limitations"
3. "Recommend scaling strategies"
4. "Plan infrastructure improvements"
5. "Create migration roadmap"
```

## Best Practices

### 1. Holistic Analysis

```python
# Start with big picture
"Geef een high-level overzicht van de gehele architectuur"

# Drill down systematically
"Focus nu op de agent interaction patterns"

# Cross-cutting concerns
"Hoe wordt logging en error handling geïmplementeerd?"
```

### 2. Contextual Recommendations

```python
# Consider project constraints
"Gegeven de huidige team size, wat zijn realistische improvements?"

# Technology stack alignment
"Hoe passen de voorgestelde changes bij de huidige tech stack?"

# Business requirements  
"Welke architectural changes ondersteunen de business goals?"
```

### 3. Incremental Planning

```python
# Phase recommendations
"Deel de architectural improvements op in phases"

# Risk mitigation
"Wat zijn de risks van elke architectural change?"

# Backward compatibility
"Hoe behouden we backward compatibility tijdens refactoring?"
```

## Performance Considerations

### 1. Analysis Optimization

- **Selective Analysis**: Focus op specifieke modules waar nodig
- **Caching**: Cache AST analysis results voor hergebruik
- **Parallel Processing**: Analyseer multiple files tegelijkertijd
- **Depth Limiting**: Controleer analysis depth voor grote codebases

### 2. Memory Management

```python
# Large project handling
"Analyseer grote projecten in chunks"

# Result streaming
"Stream analysis results voor real-time feedback"

# Selective loading
"Load alleen relevante AST data"
```

## Integration met Development Workflow

### 1. CI/CD Integration

```python
# Automated architecture analysis
"Integreer architectural checks in CI pipeline"

# Quality gates
"Definieer architectural quality gates"

# Trend analysis
"Track architectural metrics over time"
```

### 2. Documentation Generation

```python
# Auto-generated docs
"Genereer architectural documentation"

# Decision records
"Maak architectural decision records"

# API documentation
"Documenteer architectural interfaces"
```

### 3. Team Coordination

```python
# Architectural reviews
"Facilitate architectural review meetings"

# Knowledge sharing
"Create architectural knowledge base"

# Training materials
"Develop architectural training content"
```

De Architect Agent biedt een krachtige set tools voor software architects om complexe systemen te analyseren, verbeteren en strategisch te plannen. Door focus op high-level concerns en structural analysis, complementeert het perfect de detailed code analysis van de Code Agent.
