# Architect Agent

The Architect Agent is specialized in high-level software architecture analysis, design pattern detection, and strategic project planning. It is designed for software architects and senior developers who need structural insights.

## Overview

The Architect Agent provides advanced tools for:
- **Project Structure Analysis**: Complete codebase structure analysis  
- **Design Pattern Detection**: Automatic identification or design patterns
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
"Give me an overview or the Tools/ directory structure"

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
"Create a tree view or the project structure"

# Filtered analysis
"Show only Python files in the structure"

# Depth control  
"Analyze project structure up to 3 levels deep"
```

### 2. AST-Based Code Analysis

#### Deep Code Structure Analysis

```python
# Complete AST analysis
"Analyze the AST or SingleAgent.py"

# Specific aspects
"What classes and methods are in ArchitectAgent.py?"

# Dependency extraction
"What imports and dependencies does main.py have?"
```

**AST Analysis Types:**
- **Classes**: Class definitions, inheritance, methods
- **Functions**: Function signatures, parameters, return types
- **Imports**: Module dependencies and import patterns
- **Dependencies**: Internal and external dependencies

#### Method and Class Discovery

```python
# Class analysis
"Give me all classes in the The_Agents module"

# Method signatures
"What are the method signatures or the SingleAgent class?"

# Inheritance hierarchy
"Show the inheritance relationships in the codebase"
```

### 3. Design Pattern Detection

#### Automatic Pattern Recognition

```python
# Pattern scanning
"What design patterns do you see in the codebase?"

# Specific pattern analysis
"Is there a singleton pattern used in the project?"

# Anti-pattern detection
"Are there code anti-patterns that need to be addressed?"
```

**Detected Patterns:**
- **Creational**: Singleton, Factory, Builder
- **Structural**: Adapter, Facade, Decorator
- **Behavioral**: Observer, Strategy, Command
- **Anti-patterns**: God Object, Magic Numbers, Code Duplication

#### Pattern Analysis Example

```python
# Input
"Analyze the design patterns in ArchitectAgent.py"

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
"Create a dependency graph of the entire project"

# Module-specific dependencies
"What dependencies does the Tools module have?"

# Circular dependency detection
"Are there circular dependencies in the codebase?"
```

**Graph Features:**
- Visual dependency mapping
- Cycle detection
- Dependency strength analysis
- External vs internal dependencies

#### Import Analysis

```python
# Import patterns
"Analyze all import statements and their patterns"

# Unused imports
"Are there unused imports that can be cleaned up?"

# Import optimization
"How can the imports be better organized?"
```

### 5. Architectural Planning

#### TODO List Generation

```python
# Complete roadmap
"Create a TODO list for architectural improvements"

# Specific features
"Generate a TODO for adding new agent types"

# Priority-based planning
"Create a prioritized list of architectural improvements"
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
"What are the most important architectural debt items?"

# Scalability analysis
"How can this system scale better?"

# Modularity assessment
"Hoe modulair is the huidige architectuur?"
```

## Tool Reference

### Analysis Tools

#### `analyze_project_structure`

**Purpose**: Complete project directory and file analysis

**Parameters:**
- `directory`: Root directory om te analyze
- `max_depth`: Maximum depth for tree traversal  
- `include_patterns`: File patterns om te includeren (e.g., "*.py")
- `exclude_patterns`: Patterns om from te sluiten (e.g., "__pycache__")

**Example Usage:**
```python
"Analyze the project structure until 4 levels diep"
"Show only Python and Markdown files in the structuur"
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
- `file_path`: Path to Python bestand
- `analysis_type`: Type analyse (classes, functions, imports, dependencies, all)

**Example Usage:**
```python
"Analyze the AST of main.py for alle elementen"
"Give me alleen the classes from SingleAgent.py"
```

**Analysis Types:**
- `classes`: Class definitions and methods
- `functions`: Function definitions and signatures  
- `imports`: Import statements and modules
- `dependencies`: Dependency extraction
- `all`: Complete analysis

#### `detect_code_patterns`

**Purpose**: Design pattern and anti-pattern detectie

**Parameters:**
- `file_path`: Path to Python bestand om te analyze

**Example Usage:**
```python
"Detecteer design patterns in ArchitectAgent.py"
"Zijn er anti-patterns in the Tools module?"
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

**Purpose**: Dependency graph creation and analysis

**Parameters:**
- `directory`: Root directory for dependency analysis
- `include_external`: Include external dependencies
- `max_depth`: Maximum analysis depth

**Example Usage:**
```python
"Create a dependency graph of the Tools directory"
"Analyseer alle dependencies inclusief externe packages"
```

#### `generate_todo_list`

**Purpose**: Structured TODO list generation

**Parameters:**
- `description`: Project beschrijving
- `features`: List of gewenste features
- `directory`: Project directory for context

**Example Usage:**
```python
"Create a TODO lijst for the uitbreiden of agent capabilities"
"Genereer a roadmap for performance optimizations"
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

**Purpose**: Directory content listing with metadata

**Parameters:**
- `path`: Directory path
- `recursive`: Recursive listing
- `include_hidden`: Include hidden files
- `max_depth`: Maximum depth

#### `write_file`

**Purpose**: File creation for documentation and planning

**Parameters:**
- `file_path`: Output file path
- `content`: Content om te schrijven
- `mode`: Write mode (write, append)

**Example Usage:**
```python
"Schrijf the TODO lijst to a TODO.md bestand"
"Create a ARCHITECTURE.md with the project structure"
```

#### `read_file`

**Purpose**: Context-aware file reading

Identical aan Code Agent versie maar used for architectural analysis.

### System Tools

#### `run_command`

**Purpose**: Command execution for build/analysis tools

**Example Usage:**
```python
"Run find . -name '*.py' | wc -l om Python files te tellen"
"Voer tree command from for directory visualization"
```

## Advanced Features

### 1. Multi-dimensional Analysis

#### Complexity Analysis

```python
# Cyclomatic complexity
"Analyze the code complexity of alle modules"

# Coupling analysis  
"Hoe tight are the coupling relationships?"

# Cohesion assessment
"Beoordeel the cohesion binnen modules"
```

#### Maintainability Metrics

```python
# Technical debt assessment
"Wat is the technical debt of dit project?"

# Refactoring opportunities
"Welke delen of the code can gerefactored worden?"

# Code quality trends
"Hoe is the code quality about tijd veranderd?"
```

### 2. Architectural Recommendations

#### Design Improvements

```python
# Pattern recommendations
"Welke design patterns zouden dit project verbeteren?"

# Structural improvements
"Hoe kan the modulaire structuur verbeterd worden?"

# Performance architecture
"Welke architecturale wijzigingen zouden performance verbeteren?"
```

#### Best Practices

```python
# SOLID principles
"Hoe goed volgt the code the SOLID principles?"

# Clean architecture
"What are the clean architecture violations?"

# Domain-driven design
"Hoe kan DDD beter toegepast worden?"
```

### 3. Context-Aware Planning

#### Project Evolution

```python
# Growth planning
"Hoe moet the architectuur evolueren for schaalgroei?"

# Technology migration
"Wat is the strategie for the adopteren of nieuwe technologieën?"

# Legacy modernization
"Hoe can legacy onderdelen gemoderniseerd worden?"
```

#### Team Coordination

```python
# Work distribution
"Hoe can architectural tasks verdeeld worden about the team?"

# Risk assessment
"What are the grootste architectural risks?"

# Timeline planning
"Wat is a realistische timeline for deze architectural changes?"
```

## Configuration

### Agent Instructions

De Architect Agent is geconfigureerd with specifieke architectural focus:

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
1. "Analyze the complete project structure"
2. "Identificeer the core architectural patterns"
3. "Create a dependency graph"
4. "Detecteer potential architectural issues"
5. "Genereer a improvement roadmap"
```

### 2. Architecture Review

```python
1. "Evalueer the huidige architectural decisions"
2. "Identificeer design pattern usage"
3. "Assess code organization and modularity"
4. "Detect anti-patterns and technical debt"
5. "Recommend structural improvements"
```

### 3. Refactoring Planning

```python
1. "Analyseer areas die refactoring nodig have"
2. "Prioriteer refactoring efforts"
3. "Plan incremental improvement steps" 
4. "Estimate effort and impact"
5. "Create detailed TODO lists"
```

### 4. Scalability Assessment

```python
1. "Evaluate current architecture for scalability"
2. "Identify bottlenecks and limitations"
3. "Recommend scaling strategies"
4. "Plan infrastructure improvements"
5. "Create migration roadmap"
```

## Best Practices

### 1. Holistic Analysis

```python
# Start with big picture
"Geef a high-level overzicht of the gehele architectuur"

# Drill down systematically
"Focus nu on the agent interaction patterns"

# Cross-cutting concerns
"Hoe is logging and error handling geïmplementeerd?"
```

### 2. Contextual Recommendations

```python
# Consider project constraints
"Gegive the huidige team size, wat are realistische improvements?"

# Technology stack alignment
"Hoe passen the voorgestelde changes at the huidige tech stack?"

# Business requirements  
"Welke architectural changes ondersteunen the business goals?"
```

### 3. Incremental Planning

```python
# Phase recommendations
"Deel the architectural improvements on in phases"

# Risk mitigation
"What are the risks of elke architectural change?"

# Backward compatibility
"Hoe behouden we backward compatibility tijdens refactoring?"
```

## Performance Considerations

### 1. Analysis Optimization

- **Selective Analysis**: Focus on specifieke modules waar nodig
- **Caching**: Cache AST analysis results for hergebruik
- **Parallel Processing**: Analyseer multiple files tegelijkertijd
- **Depth Limiting**: Controleer analysis depth for grote codebases

### 2. Memory Management

```python
# Large project handling
"Analyseer grote projecten in chunks"

# Result streaming
"Stream analysis results for real-time feedback"

# Selective loading
"Load alleen relevante AST data"
```

## Integration with Development Workflow

### 1. CI/CD Integration

```python
# Automated architecture analysis
"Integreer architectural checks in CI pipeline"

# Quality gates
"Definieer architectural quality gates"

# Trend analysis
"Track architectural metrics about time"
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

De Architect Agent biedt a krachtige set tools for software architects om complexe systemen te analyze, verbeteren and strategisch te plannen. Door focus on high-level concerns and structural analysis, complementeert the perfect the detailed code analysis of the Code Agent.
