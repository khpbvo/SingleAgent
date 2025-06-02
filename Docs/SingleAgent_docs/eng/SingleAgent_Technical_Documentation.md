# SingleAgent: Technical Documentation

## Overview

SingleAgent is an advanced implementation of a multi-agent system built on top of the [OpenAI Agents SDK](https://github.com/openai/openai-agents-python). The project demonstrates how to use the SDK's core primitives to build a production-ready agent application with rich context management, tool integration, and dual-agent orchestration.

For background information on the underlying OpenAI Agents SDK, see the [official documentation](../openai_agents_sdk_docs/index.md).

## Architecture

### Core Components

The SingleAgent system is organized around three main components:

1. **The_Agents/**: Agent implementations
2. **Tools/**: Tool definitions and functionalities 
3. **utilities/**: Helper functions and shared utilities

### Agent Hierarchy

```
SingleAgent System
├── SingleAgent (Code Agent)
│   ├── Context Management
│   ├── Entity Recognition
│   └── Code Tools
└── ArchitectAgent (Architecture Agent)
    ├── System Design Tools
    ├── Documentation Tools
    └── Planning Tools
```

## Agent Implementations

### SingleAgent (Code Agent)

**Location**: `The_Agents/SingleAgent.py`

The `SingleAgent` class implements a specialized code assistant that leverages OpenAI Agents SDK principles:

#### Core Functionalities

1. **Enhanced Context Management**: 
   - Tiktoken-based token counting
   - Entity tracking via spaCy NLP
   - Context summarization
   - Persistent storage between sessions

2. **Agent Loop Integration**:
   - Uses the SDK's built-in agent loop as described in [agents.md](../openai_agents_sdk_docs/agents.md)
   - Handles tool calls automatically
   - Loops until the LLM is done

3. **Tools Integration**:
   - Function tools for code operations (see [tools.md](../openai_agents_sdk_docs/tools.md))
   - Custom tools for file operations, command execution
   - Automatic schema generation via Pydantic

#### Code Example

```python
from The_Agents.SingleAgent import SingleAgent
from utilities.tool_usage import handle_stream_events

# Initialize the agent
agent = SingleAgent()

# Execute a query
response = await agent.run_query_streaming(
    "Write a Python function to calculate fibonacci numbers",
    handle_stream_events
)
```

### ArchitectAgent

**Location**: `The_Agents/ArchitectAgent.py`

A specialized agent for system design and architecture tasks, follows the same pattern as SingleAgent but focuses on:
- System design tools
- Documentation generation
- High-level planning

## Tools System

The tools system follows the OpenAI Agents SDK [tools specifications](../openai_agents_sdk_docs/tools.md):

### Tool Categories

#### 1. Shared Tools (`Tools/shared_tools.py`)

Basic functionalities shared between agents:

```python
@function_tool
async def read_file(ctx: RunContextWrapper[Any], params: FileReadParams) -> str:
    """Read the contents of a file."""
    # Implementation follows SDK function tool pattern
```

#### 2. SingleAgent Tools (`Tools/singleagent_tools.py`)

Code-specific tools:

```python
@function_tool
async def write_file(ctx: RunContextWrapper[Any], params: WriteFileParams) -> str:
    """Write content to a file with safety checks."""
    # Uses SDK's automatic schema generation
```

#### 3. Architect Tools (`Tools/architect_tools.py`)

Architecture-specific tools for system design.

### Tool Implementation Pattern

All tools follow the SDK pattern:

1. **Pydantic Models** for parameter validation
2. **@function_tool decorator** for automatic registration
3. **RunContextWrapper** for context access
4. **Automatic schema generation** from function signatures

```python
from agents import function_tool, RunContextWrapper
from pydantic import BaseModel, Field

class ToolParams(BaseModel):
    param1: str = Field(description="Description for param1")
    param2: Optional[int] = Field(default=None, description="Optional parameter")

@function_tool
async def my_tool(ctx: RunContextWrapper[Any], params: ToolParams) -> str:
    """Tool description extracted from docstring."""
    # Tool implementation
    return "result"
```

## Context Management

### Enhanced Context Data

**Location**: `The_Agents/context_data.py`

Implements advanced context management on top of the SDK base:

#### Features

1. **Token Counting**: Use of tiktoken for accurate token tracking
2. **Entity Recognition**: spaCy NLP for entity extraction
3. **Context Summarization**: Automatic context compression
4. **Persistent Storage**: Context storage between sessions

#### Code Example

```python
from The_Agents.context_data import EnhancedContextData

context = EnhancedContextData()
context.add_entry("user", "Implement a REST API", {"entities": ["API", "REST"]})
summary = context.get_context_summary()
```

### SpaCy Integration

**Location**: `The_Agents/spacy_singleton.py`

Singleton pattern for efficient NLP model initialization:

```python
from The_Agents.spacy_singleton import nlp_singleton

# Async initialization
await nlp_singleton.initialize(model_name="en_core_web_lg")

# Use in tools
entities = nlp_singleton.extract_entities(text)
```

## Multi-Agent Orchestration

### Mode Switching

**Location**: `main.py`

The system supports dynamic switching between agents:

```python
# Switch to Code Agent
current_mode = AgentMode.CODE
agent = code_agent

# Switch to Architect Agent  
current_mode = AgentMode.ARCHITECT
agent = architect_agent
```

### Handoffs

While handoffs are a core feature of the SDK (see [handoffs.md](../openai_agents_sdk_docs/handoffs.md)), SingleAgent currently uses mode switching instead of true handoffs. A future improvement would be:

```python
# Potential handoff implementation
from agents import Agent, handoff_to

architect_agent = Agent(
    name="Architect",
    instructions="You are a system architect...",
)

code_agent = Agent(
    name="Coder", 
    instructions="You are a coding assistant...",
    tools=[handoff_to(architect_agent)]
)
```

## Streaming and Event Handling

### Stream Events

**Location**: `utilities/tool_usage.py`

Implements event handling for streaming responses:

```python
async def handle_stream_events(event):
    """Handle streaming events from the agent."""
    if event.type == "text_delta":
        print(event.text, end="", flush=True)
    elif event.type == "tool_call_start":
        print(f"\n[Using tool: {event.tool_name}]")
```

## Configuration and Setup

### Dependencies

The project requires:
- `openai-agents`: Core SDK
- `spacy`: NLP processing
- `tiktoken`: Token counting
- `prompt_toolkit`: Enhanced CLI interface
- `pydantic`: Data validation

### Environment Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_lg

# Set OpenAI API key
export OPENAI_API_KEY=sk-your-key-here
```

## Best Practices & Patterns

### 1. Tool Design

Follow the SDK patterns:
- Use Pydantic models for type safety
- Document tools via docstrings
- Implement async functions for I/O operations

### 2. Context Management

- Track entities for better context awareness
- Use token counting for efficiency
- Implement context compression for long sessions

### 3. Error Handling

```python
try:
    result = await agent.run_query(query)
except Exception as e:
    logger.error(f"Agent error: {e}")
    # Graceful fallback
```

### 4. Logging

Use structured logging for debugging:

```python
import logging
logger = logging.getLogger(__name__)
logger.info(json.dumps({
    "event": "tool_execution",
    "tool": tool_name,
    "params": params
}))
```

## Tracing and Monitoring

The project is prepared for the SDK's built-in tracing capabilities (see [tracing documentation](../openai_agents_sdk_docs/tracing.md)):

```python
# Future tracing integration
from agents import Runner

result = await Runner.run(
    agent=agent,
    messages=messages,
    trace=True  # Enable tracing
)
```

## Testing

### Test Structure

```
tests/
├── test_agents.py        # Agent behavior tests
├── test_tools.py         # Tool functionality tests
└── test_context.py       # Context management tests
```

### Example Test

```python
import pytest
from The_Agents.SingleAgent import SingleAgent

@pytest.mark.asyncio
async def test_agent_code_generation():
    agent = SingleAgent()
    response = await agent.run_query("Write a hello world function")
    assert "def" in response.lower()
```

## Extensions and Enhancements

### Adding New Tools

1. Define Pydantic model for parameters
2. Implement async function with @function_tool decorator
3. Add to agent's tools list

### Adding New Agents

1. Extend base agent pattern
2. Define specific tools set
3. Implement in main.py orchestration

### Guardrails Integration

For future extension with SDK guardrails:

```python
from agents import Agent, Guardrail

input_guardrail = Guardrail(
    name="input_validator",
    # Guardrail implementation
)

agent = Agent(
    name="SafeAgent",
    guardrails=[input_guardrail]
)
```

## Conclusion

SingleAgent demonstrates a robust implementation of OpenAI Agents SDK principles with:

- **Agent Loop**: Automatic tool calling and iteration
- **Function Tools**: Python functions as tools with automatic schema generation  
- **Context Management**: Advanced context tracking and persistence
- **Multi-Agent Orchestration**: Mode switching between specialized agents
- **Streaming**: Real-time response handling

The project shows how the SDK's minimal abstractions can be used to build complex, production-ready agent applications while maintaining the Python-first philosophy.

For further details on the underlying SDK capabilities, consult the [OpenAI Agents SDK documentation](../openai_agents_sdk_docs/).
