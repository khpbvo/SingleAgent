# Context Management

This document explains how the SingleAgent system manages context, including conversation history, entity tracking, and memory optimization.

## Overview

The SingleAgent system implements sophisticated context management to maintain awareness of:
- Conversation history and user interactions
- Code entities (classes, functions, variables)
- Project structure and relationships
- Tool usage patterns and results

## Context Architecture

### Context Components

The context system consists of several interconnected components:

```
┌─────────────────────────────────────────────────────────────┐
│                    Context Manager                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │  Conversation   │  │     Entity      │  │   Project    │ │
│  │    History      │  │    Tracker     │  │   Context    │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │     Token       │  │     Memory      │  │  Knowledge   │ │
│  │   Management    │  │   Prioritizer   │  │     Base     │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Context Layers

1. **Immediate Context**: Current conversation and active files
2. **Session Context**: Recent interactions and working set
3. **Project Context**: Overall project understanding
4. **Historical Context**: Long-term patterns and knowledge

## Entity Tracking

### Code Entity Recognition

The system automatically identifies and tracks various code entities:

#### Classes
```python
class UserManager:
    """Tracked as: Class entity with methods and attributes"""
    def __init__(self):
        self.users = []  # Tracked as: Instance attribute
    
    def add_user(self, user):  # Tracked as: Method with parameters
        self.users.append(user)
```

**Tracked Information:**
- Class name and inheritance hierarchy
- Methods and their signatures
- Instance and class attributes
- Decorators and metadata
- Dependencies and relationships

#### Functions
```python
def calculate_score(data: List[dict]) -> float:
    """Tracked as: Function entity with type hints"""
    return sum(item['score'] for item in data)
```

**Tracked Information:**
- Function name and signature
- Parameters and type hints
- Return type and behavior
- Decorators and wrappers
- Call relationships

#### Variables and Constants
```python
API_BASE_URL = "https://api.example.com"  # Tracked as: Module constant
user_config = load_config()               # Tracked as: Module variable
```

**Tracked Information:**
- Variable names and types
- Scope and lifetime
- Usage patterns
- Value relationships

### Entity Relationships

The system maps relationships between entities:

```python
# Dependency relationship
from models import User, Database
# Usage relationship  
db = Database()
# Inheritance relationship
class AdminUser(User):
    pass
```

**Relationship Types:**
- **Import dependencies**: Module-to-module relationships
- **Inheritance**: Class hierarchy relationships
- **Composition**: Object containment relationships
- **Usage**: Function/method call relationships
- **Data flow**: Variable assignment and transformation

### Entity Context Updates

Entities are updated automatically when:
- Files are modified or created
- New imports are added
- Classes or functions are defined
- Relationships change

## Conversation History Management

### Message Categorization

Messages are categorized for efficient retrieval:

```python
{
    "user_queries": ["How do I add a new feature?", "Fix this bug"],
    "agent_responses": ["I'll help you add the feature...", "Bug fixed"],
    "tool_results": ["Linting completed", "Tests passed"],
    "system_events": ["Agent switched", "File modified"]
}
```

### Conversation Context

The system maintains conversation context through:

#### Thread Awareness
- Tracks conversation threads and topics
- Maintains context across agent switches
- Preserves discussion state

#### Intent Recognition
- Identifies user intentions and goals
- Tracks task progression
- Maintains objective awareness

#### Reference Resolution
- Resolves pronouns and references
- Maintains entity mention tracking
- Preserves context across interactions

## Token Management

### Context Window Optimization

The system automatically manages the context window to stay within token limits:

#### Priority-Based Retention
1. **Current conversation** (highest priority)
2. **Active file content** (high priority)
3. **Recent tool results** (medium priority)
4. **Related entities** (medium priority)
5. **Historical context** (low priority)

#### Intelligent Truncation
```python
def optimize_context(context_items, token_limit):
    """
    Intelligently truncate context while preserving important information
    """
    # 1. Preserve current conversation
    # 2. Summarize historical context
    # 3. Keep essential entity information
    # 4. Compress tool results
    pass
```

### Token Estimation

The system estimates token usage for different content types:

```python
TOKEN_ESTIMATES = {
    "code_line": 15,          # Average tokens per line of code
    "comment_line": 10,       # Average tokens per comment line
    "docstring_line": 12,     # Average tokens per docstring line
    "message_word": 1.3,      # Average tokens per word in messages
}
```

## Memory Prioritization

### Content Importance Scoring

Different types of content receive importance scores:

```python
IMPORTANCE_WEIGHTS = {
    "current_file": 1.0,      # Currently active file
    "modified_file": 0.9,     # Recently modified files
    "imported_module": 0.8,   # Directly imported modules
    "related_class": 0.7,     # Classes with relationships
    "tool_result": 0.6,       # Recent tool execution results
    "conversation": 0.5,      # Historical conversation
}
```

### Adaptive Retention

The system adapts retention based on:
- **Usage frequency**: Frequently accessed content stays longer
- **Recency**: Recently accessed content has higher priority
- **Relevance**: Content related to current tasks is prioritized
- **Importance**: Critical system components are preserved

## Context Persistence

### Session Persistence

Context is persisted across sessions using:

```json
{
    "session_id": "uuid-string",
    "timestamp": "2024-01-01T00:00:00Z",
    "project_context": {
        "project_root": "/path/to/project",
        "main_files": ["main.py", "config.py"],
        "key_entities": ["UserManager", "DatabaseHandler"]
    },
    "conversation_summary": "User working on authentication system...",
    "entity_graph": {
        "nodes": [...],
        "edges": [...]
    }
}
```

### Knowledge Base Updates

Long-term knowledge is updated incrementally:
- **Pattern recognition**: Learned usage patterns
- **Best practices**: Discovered optimization opportunities  
- **Error patterns**: Common problems and solutions
- **Project insights**: Architectural understanding

## Context Retrieval

### Semantic Search

The system uses semantic search to retrieve relevant context:

```python
async def find_relevant_context(query: str, context_type: str):
    """
    Find context relevant to the current query
    """
    # 1. Parse query for entities and intentions
    # 2. Search entity graph for related items
    # 3. Retrieve conversation history matches
    # 4. Rank results by relevance
    # 5. Return top results within token limit
```

### Context Injection

Relevant context is automatically injected into agent prompts:

```python
def build_agent_prompt(user_message, relevant_context):
    """
    Build agent prompt with relevant context
    """
    prompt_parts = [
        "System instructions",
        "Project context summary",
        "Relevant entities and relationships", 
        "Recent conversation history",
        "Current file content",
        "User message"
    ]
    return combine_with_token_management(prompt_parts)
```

## Performance Optimization

### Caching Strategies

#### Entity Cache
- AST parsing results cached
- Entity relationships memoized
- File modification tracking

#### Conversation Cache
- Recent interactions in memory
- Frequently accessed content prioritized
- Compressed historical summaries

### Background Processing

Some context operations run in the background:
- **Entity graph updates**: After file modifications
- **Relationship analysis**: During idle periods
- **Context summarization**: When approaching token limits
- **Knowledge base updates**: Periodic batch processing

## Context Configuration

### Tunable Parameters

Context management can be configured:

```toml
[tool.singleagent.context]
# Token management
max_context_tokens = 8000
priority_threshold = 0.5
summarization_ratio = 0.3

# Entity tracking
track_all_variables = false
deep_dependency_analysis = true
max_entity_depth = 5

# Memory management
session_cache_size = 1000
entity_cache_size = 500
conversation_history_limit = 100
```

### Adaptive Configuration

The system can adapt configuration based on:
- **Project size**: Larger projects need more selective context
- **Usage patterns**: Heavy users get more aggressive caching
- **Performance constraints**: Limited resources require optimization
- **User preferences**: Customizable context depth and focus

## Debugging Context Issues

### Context Inspection

Tools for inspecting context state:

```python
# View current context summary
!context summary

# Inspect entity relationships
!context entities --class UserManager

# Check token usage
!context tokens

# View conversation history
!context history --last 10
```

### Common Context Problems

#### Context Loss
- **Symptom**: Agent forgets recent information
- **Cause**: Token limit exceeded, poor prioritization
- **Solution**: Adjust token limits, improve importance scoring

#### Irrelevant Context
- **Symptom**: Agent mentions unrelated information
- **Cause**: Poor relevance scoring, over-broad retrieval
- **Solution**: Refine semantic search, adjust relevance weights

#### Slow Context Retrieval
- **Symptom**: Long delays before agent responses
- **Cause**: Expensive context operations, cache misses
- **Solution**: Optimize caching, background processing

This context management system ensures that the SingleAgent maintains appropriate awareness of the project state, conversation history, and code relationships while efficiently managing computational resources and token limits.
