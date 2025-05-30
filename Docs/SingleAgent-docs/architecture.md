# Architecture Overview

This page provides a detailed overview or how SingleAgent is designed and how the different components work together.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        SingleAgent System                   │
├─────────────────────────────────────────────────────────────┤
│  main.py - Entry Point & Agent Orchestration               │
├─────────────────────────────────────────────────────────────┤
│                    Agent Layer                              │
│  ┌──────────────────┐           ┌─────────────────────────┐ │
│  │   Code Agent     │           │    Architect Agent      │ │
│  │  (SingleAgent)   │           │   (ArchitectAgent)      │ │
│  │                  │           │                         │ │
│  │ - Code Analysis  │           │ - Structure Analysis    │ │
│  │ - Debugging      │           │ - Design Patterns       │ │
│  │ - Testing        │           │ - Dependency Graphs     │ │
│  │ - File Ops       │           │ - TODO Generation       │ │
│  └──────────────────┘           └─────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                     Tools Layer                             │
│  ┌─────────────────┐            ┌─────────────────────────┐ │
│  │ Code Agent Tools│            │ Architect Agent Tools   │ │
│  │ - ruff         │            │ - AST Analysis          │ │
│  │ - pylint       │            │ - Project Structure     │ │
│  │ - pyright      │            │ - Pattern Detection     │ │
│  │ - file ops     │            │ - Dependency Analysis   │ │
│  │ - patch mgmt   │            │ - TODO Generation       │ │
│  └─────────────────┘            └─────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                   Context Management                        │
│  ┌───────────────────────────────────────────────────────┐ │
│  │              EnhancedContextData                      │ │
│  │ - Chat History        - Entity Tracking              │ │
│  │ - Token Management    - State Management             │ │
│  │ - File Tracking       - Auto Summarization           │ │
│  └───────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                Infrastructure Layer                         │
│  ┌──────────────┐ ┌──────────────┐ ┌─────────────────────┐ │
│  │   OpenAI     │ │    SpaCy     │ │   Prompt Toolkit    │ │
│  │   Agents     │ │   NLP        │ │   CLI Interface     │ │
│  │    SDK       │ │   Models     │ │   & Streaming       │ │
│  └──────────────┘ └──────────────┘ └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Core Componenten

### 1. Entry Point (main.py)

**Verantwoordelijkheden:**
- Agent orchestration and mode switching
- CLI interface management
- Session management
- Command processing (`!code`, `!architect`, etc.)

**Key Features:**
- Dual-agent mode switching
- Persistent session state
- Interactive CLI with prompt_toolkit
- Real-time streaming output

```python
# Agent mode switching
class AgentMode:
    CODE = "code"
    ARCHITECT = "architect"

# Dynamic agent selection
current_agent = code_agent if current_mode == AgentMode.CODE else architect_agent
```

### 2. Agent Layer

#### Code Agent (SingleAgent)

**Primaire Focus:** Directe code manipulatie and analyse

**Capabilities:**
- Code quality analysis (ruff, pylint, pyright)
- File reading/writing operations
- Patch creation and application
- Context-aware debugging assistance
- Command execution

**Tool Set:**
```python
tools=[
    run_ruff,        # Code linting
    run_pylint,      # Comprehensive analysis  
    run_pyright,     # Type checking
    run_command,     # Shell command execution
    read_file,       # File operations
    create_colored_diff, # Diff visualization
    apply_patch,     # Patch management
    change_dir,      # Directory navigation
    os_command,      # OS operations
    get_context,     # Context access
    add_manual_context # Manual context addition
]
```

#### Architect Agent (ArchitectAgent)

**Primaire Focus:** High-level architectuur and design analyse

**Capabilities:**
- Project structure analysis
- AST-based code pattern detection
- Dependency graph generation
- Design pattern identification
- TODO list generation
- Architectural recommendations

**Tool Set:**
```python
tools=[
    analyze_ast,             # Deep code structure analysis
    analyze_project_structure, # Directory tree analysis
    generate_todo_list,      # Task planning
    analyze_dependencies,    # Dependency mapping
    detect_code_patterns,    # Pattern recognition
    read_file,              # File access
    read_directory,         # Directory listing
    write_file,             # Content creation
    run_command            # Command execution
]
```

### 3. Context Management System

#### EnhancedContextData

Het hart of the geheugen systeem of SingleAgent:

**Features:**
- **Entity Tracking**: Automatische detectie and tracking of files, commands, URLs, etc.
- **Chat History**: Volledige conversatie geschiedenis with role-based messages
- **Token Management**: Automatische token counting and context summarization
- **State Management**: Key-value state storage for session data
- **Persistent Storage**: Context is opgeslagen tussen sessies

**Entity Types:**
```python
ENTITY_TYPES = [
    "file",                # Bestanden in conversaties
    "command",             # Uitgevoerde commands  
    "url",                 # URLs and links
    "search_query",        # Zoekopdrachten
    "task",                # Actieve taken
    "programming_language", # Talen in gebruik
    "framework",           # Frameworks
    "api_endpoint",        # API endpoints
    "error_message",       # Error berichten
    "design_pattern",      # Architect: Design patterns
    "architecture_concept" # Architect: Architectuur concepten
]
```

**Token Management:**
```python
# Automatische summarization wanneer token limit is bereikt
if self.token_count > self.max_tokens * 0.8:
    await self.summarize_if_needed(openai_client)
```

### 4. Tool Architecture

#### Function Tool Decorator

Alle tools use the `@function_tool` decorator from the OpenAI Agents SDK:

```python
@function_tool
async def run_ruff(wrapper: RunContextWrapper[None], params: RuffParams) -> str:
    # Tool implementation
    cmd = ["ruff", "check", *params.paths, *params.flags]
    # ... execution logic
    return output
```

#### Tool Categorieën

**Development Tools:**
- `run_ruff`: Python linting
- `run_pylint`: Comprehensive code analysis
- `run_pyright`: Static type checking

**File Operations:**
- `read_file`: File content reading
- `write_file`: File content writing
- `create_colored_diff`: Visual diff creation
- `apply_patch`: Patch application

**Analysis Tools:**
- `analyze_ast`: AST-based code analysis
- `analyze_project_structure`: Directory structure analysis
- `detect_code_patterns`: Design pattern detection
- `analyze_dependencies`: Dependency graph creation

### 5. Entity Recognition System

#### SpaCy Integration

SingleAgent used spaCy for geavanceerde entity recognition:

```python
# SpaCy singleton for performance
from The_Agents.spacy_singleton import nlp_singleton

# Entity extraction
entities = await entity_recognizer.extract_entities_async(
    user_input, 
    nlp_singleton.nlp
)
```

#### Fallback Recognition

Als spaCy faalt, used the systeem regex-based fallback:

```python
def _extract_entities_fallback(self, user_input: str):
    # File paths
    file_matches = re.findall(r'[\w\-_/.]+\.py', user_input)
    
    # Commands  
    command_matches = re.findall(r'\b(run|execute|check)\s+(\w+)', user_input)
    
    # Tasks
    task_matches = re.search(r'(implement|create|fix|debug)\s+([^\.]+)', user_input)
```

### 6. Streaming Architecture

#### Real-time Output

SingleAgent used async streaming for real-time feedback:

```python
async def _run_streamed(self, user_input: str) -> str:
    response_chunks = []
    
    async for event in Runner.run_stream(
        starting_agent=self.agent,
        input=user_input,
        context=self.context,
    ):
        if isinstance(event, ResponseTextDeltaEvent):
            print(event.delta, end="", flush=True)
            response_chunks.append(event.delta)
    
    return "".join(response_chunks)
```

## Data Flow

### 1. User Input Processing

```
User Input → Entity Extraction → Context Update → Agent Selection → Tool Execution → Response
```

### 2. Context Flow

```
┌─────────────────┐
│   User Input    │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐    ┌──────────────────┐
│ Entity Extract  │────│  Update Context  │
└─────────────────┘    └─────────┬────────┘
                                 │
                                 ▼
┌─────────────────┐    ┌──────────────────┐
│  Agent Execute  │────│   Tool Execution │
└─────────┬───────┘    └──────────────────┘
          │
          ▼
┌─────────────────┐    ┌──────────────────┐
│   Response      │────│   Update History │
└─────────────────┘    └──────────────────┘
```

### 3. Tool Execution Flow

```
Agent Request → Tool Selection → Parameter Validation → Execution → Result Processing → Context Update
```

## Memory Management

### Token Counting

```python
# Automatische token counting with tiktoken
import tiktoken

def count_tokens(self, text: str) -> int:
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))
```

### Context Summarization

Wanneer the context te groot is:

```python
async def summarize_if_needed(self, openai_client) -> bool:
    if self.token_count > self.max_tokens * 0.8:
        # Gebruik OpenAI om context samen te vatten
        summary = await self._create_summary(openai_client)
        self._replace_old_messages_with_summary(summary)
        return True
    return False
```

## Configuration

### Model Settings

```python
# Code Agent configuration
model_settings=ModelSettings(temperature=0.0)  # Deterministic for code

# Architect Agent configuration  
model="gpt-4.1"  # Krachtig model for architectuur analyse
```

### File Persistence

```python
# Context opslag
CONTEXT_FILE_PATH = os.path.join(os.path.expanduser("~"), ".singleagent_context.json")
ARCHITECT_CONTEXT_FILE = os.path.join(os.path.expanduser("~"), ".architectagent_context.json")
```

## Error Handling

### Graceful Degradation

- SpaCy entity extraction → Regex fallback
- OpenAI API errors → Local processing waar mogelijk
- Tool failures → Error reporting with continue execution

### Logging Strategy

```python
# Structured logging
logging.debug(json.dumps({
    "event": "user_input",
    "input": query,
    "mode": current_mode,
    "entities_extracted": len(entities)
}))
```

## Performance Considerations

### Optimization Strategies

1. **Lazy Loading**: SpaCy model is alleen geladen wanneer nodig
2. **Caching**: Entity results worden gecached
3. **Streaming**: Real-time output for betere UX
4. **Selective Tools**: Agents laden alleen relevante tools
5. **Context Pruning**: Automatische context summarization

### Scalability

- **Modular Design**: Nieuwe agents can eenvoudig worden toegevoegd
- **Tool Extensibility**: Tools can onafhankelijk worden ontwikkeld
- **Context Partitioning**: Context kan worden gesegmenteerd for grote projecten

## Design Principles

### 1. Separation or Concerns
- Agents focussen on hun domein (code vs architectuur)
- Tools are single-purpose and composable
- Context management is centralized

### 2. Extensibility
- Nieuwe tools can eenvoudig worden toegevoegd
- Agents can nieuwe capabilities krijgen
- Context types can worden uitgebreid

### 3. User Experience
- Intuitive command structure (`!code`, `!architect`)
- Real-time feedback via streaming
- Rich context awareness

### 4. Reliability
- Graceful error handling
- Fallback mechanisms
- Persistent state management

Deze architectuur maakt SingleAgent a krachtig, uitbreidbaar and gebruiksvriendelijk systeem for software development and analyse taken.
